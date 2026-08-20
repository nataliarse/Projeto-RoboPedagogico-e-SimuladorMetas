# Estruturação e Modelagem dos Dados Processuais — TRT18

Transforma os processos coletados do PJe do TRT18 (1º Grau) em uma **árvore JSON
padronizada e validada**, pronta para o chatbot. Cobre as etapas descritas em
`tarefas.md`: da leitura da base até a entrega do JSON final.

## Estrutura

```
robo-orientador-dados/
├── app.py                  # PONTO DE ENTRADA — consulta um processo (CLI)
├── servico.py              # integração com o chatbot: obter_processo(numero) → árvore JSON
├── modelos.py              # esquema Pydantic (a árvore JSON)
├── coletor_trt18.py        # raspagem: acesso + CAPTCHA + extração dos dados
├── normalizador.py         # limpeza, padronização e mapeamento bruto → esquema
├── captcha/                # decifrador de CAPTCHA (autoria: Filipe Campos) — ver captcha/README.md
├── pesquisa/
│   └── pipeline.ipynb      # etapa de pesquisa do TCC (coleta em lote + análise)
├── data/
│   ├── entrada/            # planilha com os ~100 processos
│   ├── brutos/             # dados brutos por processo (cache da coleta)
│   └── saida/              # processo_<numero>.json  ← árvore JSON entregue
├── exemplos/               # exemplo de bruto para testar sem raspar
└── requirements.txt
```

## Instalação

```bash
pip install -r requirements.txt
python -m playwright install chromium   # apenas na 1ª vez
```

## Consultar um processo (`app.py`)

```bash
python app.py                                   # modo interativo (pergunta o número)
python app.py 0011000-82.1981.5.18.0051         # consulta e mostra o resumo
python app.py 0011000-82.1981.5.18.0051 --json  # imprime só a árvore JSON
```

Opções: `--headless` (não abre a janela do navegador) e `--so-cache` (usa só o que
já foi coletado, sem raspar). Cada consulta grava
`data/saida/processo_<numero>.json`.

> A consulta em lote a partir de planilha vive em `pesquisa/pipeline.ipynb`, que
> documenta a etapa de pesquisa do TCC (etapas 1→8 do `tarefas.md`) e **não é o
> fluxo de produção**. O `app.py` é focado na consulta sob demanda, um processo
> por vez — que é o fluxo que alimenta o chatbot/LLM.
>
> Se for rodar o notebook, atenção à flag `COLETAR_AGORA`: com `True` ele raspa
> os 100 processos da planilha em sequência, o que **dispara o bloqueio do
> portal** (ver limites abaixo).

### Validação do número informado

Antes de abrir o navegador, o número passa por checagens offline (instantâneas):

| Checagem | Exemplo de mensagem |
|---|---|
| 20 dígitos | `tem 6 dígitos; o padrão CNJ exige 20` |
| Dígito verificador (Res. CNJ 65/2008) | `dígito verificador não confere (informado 83, esperado 82)` |
| Justiça do Trabalho / TRT18 | `Processo do TRT15, não do TRT18` |

### Status possíveis da coleta

| Status | Significado |
|---|---|
| `SUCESSO` | Detalhe do processo capturado (com movimentações). |
| `PARCIAL` | Captcha ok, mas o detalhe não chegou no tempo limite. |
| `NAO_ENCONTRADO` | Número válido, sem processo correspondente no TRT18. |
| `BLOQUEADO` | O portal recusou o acesso (HTTP 403/429) — ver limites abaixo. |
| `FALHA` | Captcha não validado ou erro de navegação. |

Só `SUCESSO`/`PARCIAL` geram arquivo de saída — falhas não gravam JSON vazio.

### ⚠️ Limite de consultas do portal

O PJe **bloqueia temporariamente (HTTP 403)** quem faz muitas consultas em
sequência — observamos isso após algumas dezenas de consultas seguidas. Quando
acontece, a página vem vazia e o captcha nunca aparece. O coletor detecta esse
estado e aborta em ~10s com status `BLOQUEADO`, em vez de insistir.

Por isso: há pausa entre consultas no modo lote, e o cache em `data/brutos/`
evita reconsultar o que já foi obtido. Para uso com chatbot/LLM, prefira sempre
o cache antes de raspar de novo.

## Integração com o chatbot

Conforme a proposta técnica, o chatbot chama a coleta como uma **ferramenta
interna** (não navega sozinho). O ponto de entrada é `servico.obter_processo`:

```python
from servico import obter_processo

# raspa ao vivo (abre navegador + CAPTCHA) ou usa cache de data/brutos:
arvore = obter_processo("0011000-82.1981.5.18.0051")

# só cache, sem abrir navegador (útil em testes / no dev do chatbot):
arvore = obter_processo("0011000-82.1981.5.18.0051", coletar=False)
```

Retorna sempre a árvore JSON já **limpa e validada** (um `dict` pronto para
`json.dumps`), escondendo toda a complexidade de raspagem/CAPTCHA/normalização.

## A árvore JSON (esquema)

```json
{
  "processo":            { "numero", "numero_normalizado", "classe_judicial",
                           "assunto", "orgao_julgador", "unidade", "jurisdicao", "grau",
                           "data_autuacao", "data_distribuicao", "valor_causa", "situacao" },
  "partes_interessadas": [ { "polo", "nome", "tipo", "documento", "representantes" } ],
  "movimentacoes":       [ { "ordem", "data", "descricao", "complemento" } ],
  "documentos":          [ { "data", "titulo", "tipo", "id_documento" } ],
  "pendencias":          [ "..." ],
  "coleta":              { "fonte", "coletado_em", "versao_coletor",
                           "tempo_execucao_seg", "status_coleta", "tentativas_captcha",
                           "status_cnj_planilha", "warnings", "erros" }
}
```

Os blocos seguem a `proposta_tecnica_chatbot_governo.pdf` (processo,
partes_interessadas, movimentacoes, documentos, pendencias, coleta).

`situacao` é **PENDENTE / BAIXADO / INDEFINIDO**. O `normalizador` traz uma
heurística simples (olha os últimos movimentos buscando termos como "baixa
definitiva", "trânsito em julgado", "arquivado definitivamente"). O mapeamento
"oficial" contra o fluxograma continua sendo do chatbot — aqui é só um palpite
auxiliar.

## Como a coleta funciona (endpoints reais do PJe)

Após o captcha ser aceito, o PJe Consulta responde o detalhe do processo em:

```
GET /pje-consulta-api/api/processos/{id}?tokenDesafio=...
```

Esse payload traz `itensProcesso` (o histórico — cada item com `titulo`, `data` e
o booleano `documento`), `poloAtivo`/`poloPassivo` (partes, já anonimizadas pelo
próprio PJe), `assuntos`, `expedientes`, `autuadoEm`, `distribuidoEm` e
`valorDaCausa`. O `normalizador.py` mapeia exatamente esses campos, com fallback
genérico por *nomes candidatos* caso o portal mude.

> **Importante:** essa resposta chega **vários segundos depois** de o campo do
> captcha desaparecer. O coletor faz espera ativa até ela aparecer (até 45s) —
> antes disso a página era lida ainda em "Enviando resposta do captcha. Aguarde."
> e o resultado saía sem movimentações, mas marcado como sucesso.
> Brutos coletados antes da versão 1.1.0 são detectados como incompletos
> (`cache_aproveitavel`) e recoletados automaticamente.

## Nota de governança (CAPTCHA / ddddocr)

A proposta técnica é explícita: `ddddocr` e o processamento de imagem só devem
ser usados **com autorização institucional** e **não** para burlar mecanismos de
segurança/CAPTCHA ou barreiras de acesso. O módulo `captcha/` é o protótipo que
já existia (fora do escopo desta etapa de estruturação) e está aqui apenas para
permitir a coleta ponta a ponta. Confirme com a professora/TRT as regras de
acesso (frequência de consultas, credenciais, tratamento de dados) antes de
rodar coletas em volume.
