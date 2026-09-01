# Robô Pedagógico e Simulador de Metas

Repositório com o **Chatbot Processual**, uma interface Angular integrada a uma
API FastAPI, o sistema de coleta e modelagem dos dados processuais do TRT18 e os
estudos do **Simulador de Metas**.

## Estrutura do repositório

```text
frontend/                aplicação Angular do Chatbot Processual
chatbot_processual_ai/   backend FastAPI, orquestração, agentes, serviços e testes
entrada-de-dados/        coleta, normalização e modelagem dos processos do TRT18
simulador-de-metas/      estudos e artefatos próprios do domínio de metas
docs/                    arquitetura, contrato, desenvolvimento e decisões
```

## Coleta e modelagem dos dados processuais — TRT18

Transforma os processos coletados do PJe do TRT18 (1º Grau) em uma **árvore JSON
padronizada e validada**, pronta para o chatbot, desde a leitura da base até a
entrega do JSON final.

### Estrutura

```
entrada-de-dados/
├── app.py                  # PONTO DE ENTRADA — consulta um processo (CLI)
├── servico.py              # integração com o chatbot: obter_processo(numero) → árvore JSON
├── modelos.py              # esquema Pydantic (a árvore JSON)
├── coletor_trt18.py        # raspagem: acesso + CAPTCHA + extração dos dados
├── normalizador.py         # limpeza, padronização e mapeamento bruto → esquema
├── captcha/                # decifrador de CAPTCHA (autoria: Filipe Campos)
├── pesquisa/
│   └── pipeline.ipynb      # etapa de pesquisa do TCC (coleta em lote + análise)
├── data/
│   ├── entrada/            # planilha com os ~100 processos
│   ├── brutos/             # dados brutos por processo (cache da coleta)
│   └── saida/              # processo_<numero>.json  ← árvore JSON entregue
├── exemplos/               # exemplo de bruto para testar sem raspar
```

### Instalação

```bash
cd entrada-de-dados
pip install -r ../chatbot_processual_ai/requirements.txt
python -m playwright install chromium   # apenas na 1ª vez
```

### Consultar um processo (`app.py`)

```bash
python app.py                                   # modo interativo (pergunta o número)
python app.py 0011000-82.1981.5.18.0051         # consulta e mostra o resumo
python app.py 0011000-82.1981.5.18.0051 --json  # imprime só a árvore JSON
```

Opções: `--headless` (não abre a janela do navegador) e `--so-cache` (usa só o que
já foi coletado, sem raspar). Cada consulta grava
`data/saida/processo_<numero>.json`.

> A consulta em lote a partir de planilha vive em
> `entrada-de-dados/pesquisa/pipeline.ipynb`, que documenta a etapa de pesquisa
> do TCC e **não é o
> fluxo de produção**. O `app.py` é focado na consulta sob demanda, um processo
> por vez — que é o fluxo que alimenta o chatbot/LLM.
>
> Se for rodar o notebook, atenção à flag `COLETAR_AGORA`: com `True` ele raspa
> os 100 processos da planilha em sequência, o que **dispara o bloqueio do
> portal** (ver limites abaixo).

#### Validação do número informado

Antes de abrir o navegador, o número passa por checagens offline (instantâneas):

| Checagem | Exemplo de mensagem |
|---|---|
| 20 dígitos | `tem 6 dígitos; o padrão CNJ exige 20` |
| Dígito verificador (Res. CNJ 65/2008) | `dígito verificador não confere (informado 83, esperado 82)` |
| Justiça do Trabalho / TRT18 | `Processo do TRT15, não do TRT18` |

#### Status possíveis da coleta

| Status | Significado |
|---|---|
| `SUCESSO` | Detalhe do processo capturado (com movimentações). |
| `PARCIAL` | Captcha ok, mas o detalhe não chegou no tempo limite. |
| `NAO_ENCONTRADO` | Número válido, sem processo correspondente no TRT18. |
| `BLOQUEADO` | O portal recusou o acesso (HTTP 403/429) — ver limites abaixo. |
| `FALHA` | Captcha não validado ou erro de navegação. |

Só `SUCESSO`/`PARCIAL` geram arquivo de saída — falhas não gravam JSON vazio.

#### ⚠️ Limite de consultas do portal

O PJe **bloqueia temporariamente (HTTP 403)** quem faz muitas consultas em
sequência — observamos isso após algumas dezenas de consultas seguidas. Quando
acontece, a página vem vazia e o captcha nunca aparece. O coletor detecta esse
estado e aborta em ~10s com status `BLOQUEADO`, em vez de insistir.

O cache em `data/brutos/` evita reconsultar o que já foi obtido. O lote atual
não aplica pausa explícita entre processos, portanto não deve ser executado em
volume sem revisão operacional. Para uso com chatbot/LLM, prefira sempre o
cache antes de raspar de novo.

### Integração com o chatbot

Conforme a proposta técnica, a coleta foi preparada como uma **ferramenta
interna** para que o chatbot não navegue sozinho. O ponto de entrada planejado
é `servico.obter_processo`:

```python
from servico import obter_processo

# raspa ao vivo (abre navegador + CAPTCHA) ou usa cache de data/brutos:
arvore = obter_processo("0011000-82.1981.5.18.0051")

# só cache, sem abrir navegador (útil em testes / no dev do chatbot):
arvore = obter_processo("0011000-82.1981.5.18.0051", coletar=False)
```

Retorna sempre a árvore JSON já **limpa e validada** (um `dict` pronto para
`json.dumps`), escondendo toda a complexidade de raspagem/CAPTCHA/normalização.
O backend em `chatbot_processual_ai/` ainda não chama esse serviço; a integração
está preparada, mas não está ativa no fluxo web.

### A árvore JSON (esquema)

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

### Como a coleta funciona (endpoints reais do PJe)

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

### Nota de governança (CAPTCHA / ddddocr)

A proposta técnica é explícita: `ddddocr` e o processamento de imagem só devem
ser usados **com autorização institucional** e **não** para burlar mecanismos de
segurança/CAPTCHA ou barreiras de acesso. O módulo `captcha/` é o protótipo que
já existia (fora do escopo desta etapa de estruturação) e está aqui apenas para
permitir a coleta ponta a ponta. Confirme com a professora/TRT as regras de
acesso (frequência de consultas, credenciais, tratamento de dados) antes de
rodar coletas em volume.

## Aplicação web

No fluxo web atual, o browser acessa o Angular, que usa HTTP/JSON relativo sob
`/api`. Em desenvolvimento, o servidor Angular encaminha essas chamadas ao
FastAPI por um proxy versionado. O endpoint principal é
`POST /api/processos/chat`; `GET /api/health` verifica somente a disponibilidade
da fronteira FastAPI.

### Começo rápido

Prepare primeiro o backend e as dependências compartilhadas, em um terminal:

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn api:app --reload
```

Em outro terminal, prepare o frontend:

```powershell
cd frontend
npm ci
npm start
```

A interface fica em `http://localhost:4200` e o FastAPI em
`http://localhost:8000`. Não é necessário codificar o endereço do backend no
frontend nem habilitar CORS para essa topologia local.

Ollama e Qdrant são condicionais: consultas estruturadas usam o SQLite local;
a capacidade semântica completa (RAG) requer embeddings via Ollama e índice no
Qdrant. Consulte o guia de desenvolvimento antes de preparar ou testar o
ambiente. Em particular, `pytest` ainda não é declarado em `requirements.txt`.

## Documentação complementar

- [Arquitetura](docs/ARCHITECTURE.md)
- [Contrato e integração](docs/integration.md)
- [Orquestração](docs/orchestration.md)
- [Desenvolvimento local](docs/development.md)
- [Coleta e estruturação de dados do TRT18](docs/data-ingestion.md)
- [Filosofia de design](docs/design_philosophy.md)
- [Frontend](frontend/README.md)
- [Backend](chatbot_processual_ai/README.md)
- [CAPTCHA](entrada-de-dados/captcha/README.md)

## Estado e limites atuais

- a sessão web é identificada por `session_id`, mantida no `sessionStorage` do
  browser e em `_SESSIONS`, na memória do processo Python;
- reiniciar o backend perde o contexto conversacional; não há persistência
  distribuída, autenticação por `session_id` nem deploy de produção definido;
- o histórico recente da interface usa `localStorage` e não substitui a sessão;
- o frontend aplica timeout de 135 s, mas o orçamento total backend planejado de
  120 s não está implementado;
- o simulador de metas ainda não implementa regras oficiais homologadas; os
  endpoints atuais preservam contratos e resultados provisórios.

Não versione `.env`, credenciais, bancos SQLite de runtime, caches, logs,
`node_modules`, `.venv`, builds ou dados processuais reais. Use dados sintéticos
ou sanitizados em exemplos e testes.
