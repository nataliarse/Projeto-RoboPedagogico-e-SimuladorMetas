# Coleta e estruturação de dados processuais do TRT18

## Objetivo e estado da integração

O módulo `entrada-de-dados/` consulta processos de 1º grau no PJe do TRT18,
preserva a resposta capturada em formato bruto e a converte em uma árvore JSON
validada por Pydantic. Ele oferece dois usos:

- consulta sob demanda pela CLI (`app.py`) ou pela função
  `servico.obter_processo()`;
- pesquisa em lote e análise da amostra pelo notebook
  `pesquisa/pipeline.ipynb`.

`servico.obter_processo()` é a fronteira projetada para o chatbot, mas ainda não
há importação ou chamada desse serviço em `chatbot_processual_ai/`. Portanto, a
coleta está implementada como módulo autônomo e a integração com o fluxo web é
uma capacidade preparada, não uma integração ativa.

## Visão geral do fluxo sob demanda

```text
número CNJ
   │
   ├─ app.py ── validação offline completa para feedback da CLI
   │              (20 dígitos, DV, Justiça do Trabalho e TRT18)
   │
   └─ servico.obter_processo()
          │
          ├─ cache completo? ── sim ── lê data/brutos/<20 dígitos>.json
          │
          └─ não
              ├─ coletar=False ── FileNotFoundError
              └─ coletar=True
                   └─ coletor_trt18.coletar_processo()
                         ├─ valida número CNJ
                         ├─ abre Chromium/Chrome/Edge via Playwright
                         ├─ detecta bloqueio ou processo inexistente
                         ├─ captura e resolve CAPTCHA
                         ├─ intercepta respostas JSON do PJe
                         ├─ captura HTML e texto como fallback
                         └─ grava data/brutos/<20 dígitos>.json
          │
          └─ normalizador.normalizar()
                 ├─ extrai e limpa campos
                 ├─ infere situação e pendências
                 ├─ valida modelos Pydantic
                 └─ devolve dict JSON
                        │
                        └─ app.py grava data/saida/processo_<20 dígitos>.json
```

A CLI valida o número antes de chamar o serviço. Chamado diretamente, o serviço
verifica inicialmente apenas se há 20 dígitos para localizar o cache; a
validação completa ocorre no coletor quando uma coleta ao vivo é necessária.

## Responsabilidades por arquivo

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Interface de linha de comando, modo interativo, mensagens por status, resumo e gravação da saída individual. |
| `servico.py` | Fachada de integração: escolhe cache ou coleta e sempre normaliza o bruto antes de retornar. |
| `coletor_trt18.py` | Validação CNJ, automação do navegador, CAPTCHA, captura das APIs, estados da coleta, cache bruto e lote. |
| `normalizador.py` | Busca tolerante, limpeza, conversão, extração, ordenação, heurísticas e montagem do modelo raiz. |
| `modelos.py` | Contrato Pydantic v2 da árvore entregue ao consumidor. Campos extras são proibidos. |
| `captcha/` | Pipeline OCR local reutilizado para resolver a imagem capturada. |
| `pesquisa/pipeline.ipynb` | Fluxo de pesquisa em lote, análise exploratória, validação e geração de um array JSON. Não é o caminho de produção. |

## Validação do número CNJ

`coletor_trt18.validar_numero_cnj()` remove pontuação e valida, sem rede:

1. exatamente 20 dígitos no padrão `NNNNNNN-DD.AAAA.J.TR.OOOO`;
2. dígito verificador por módulo 97, base 10 (ISO 7064);
3. segmento `J = 5`, correspondente à Justiça do Trabalho;
4. tribunal `TR = 18`.

Um número estruturalmente válido não comprova existência. O coletor conclui
`NAO_ENCONTRADO` somente quando a chamada `dadosbasicos` do PJe é observada com
lista vazia.

## Cache e persistência

Há três classes de artefatos:

| Local | Conteúdo | Consumidor | Política |
|---|---|---|---|
| `data/brutos/<numero>.json` | URL, tempos, status, erros, respostas da API, HTML e texto da página. | Serviço, normalizador e notebook. | Reprocessável; pode existir também para falhas e resultados parciais. |
| `data/saida/processo_<numero>.json` | Uma árvore `Processo` normalizada. | Usuário/consumidor da consulta individual. | A CLI não grava para `FALHA`, `BLOQUEADO` ou `NAO_ENCONTRADO`; grava `SUCESSO` e `PARCIAL`. |
| `data/saida/processos_trt18*.json` | Array de processos normalizados. | Entrega experimental do notebook. | Sufixo `_DEMO` quando usa somente o exemplo local. |

A existência de um bruto não o torna reutilizável. `cache_aproveitavel()` exige
que alguma resposta contenha pelo menos uma das chaves `itensProcesso`,
`poloAtivo` ou `poloPassivo`. Isso invalida coletas antigas ou parciais que
tenham somente dados básicos. Em consequência:

- `servico.obter_processo()` tenta coletar novamente quando o cache é
  incompleto;
- com `coletar=False`, cache ausente ou incompleto causa `FileNotFoundError`;
- o lote pula somente caches completos;
- um resultado `PARCIAL` pode ser entregue na chamada corrente, mas será
  considerado incompleto numa chamada futura se não contiver as chaves acima.

Os diretórios `data/brutos/`, `data/saida/` e `data/debug/` são ignorados pelo
Git no `.gitignore` do módulo.

## Coleta no PJe

### Inicialização e navegador

As dependências pesadas (`playwright`, OpenCV e `ddddocr`) são importadas sob
demanda. No Windows, o módulo substitui `cv2.imread` e `cv2.imwrite` por versões
compatíveis com caminhos Unicode. O Playwright tenta usar Chrome ou Edge em
caminhos conhecidos e recorre ao Chromium instalado pelo próprio Playwright.

Quando chamado dentro de um event loop, como no Jupyter, a coleta síncrona roda
em uma thread. No Windows, essa thread troca temporariamente a policy do asyncio
por `WindowsProactorEventLoopPolicy`, necessária para iniciar subprocessos.

### Uma tentativa de CAPTCHA

Cada tentativa cria navegador, contexto e página novos. O fluxo é:

1. registrar listeners de requests e responses;
2. abrir a URL do processo, com timeout de 60 segundos;
3. aguardar até 10 segundos pela resposta `dadosbasicos` ou por bloqueio;
4. abortar imediatamente em HTTP 403/429 (`BLOQUEADO`) ou lista vazia
   (`NAO_ENCONTRADO`);
5. esperar o campo `#captchaInput` por até 12 segundos;
6. obter a imagem `data:image/png;base64`, salvá-la temporariamente e chamar o
   OCR;
7. preencher e enviar a resposta;
8. considerar o CAPTCHA aceito quando o campo some em até 5 segundos;
9. aguardar até 45 segundos pelo payload detalhado;
10. capturar respostas JSON, HTML completo e texto do `body`.

São permitidas até cinco tentativas, com dois segundos entre elas. Bloqueio e
processo inexistente não são repetidos. Na última falha por timeout/erro, o
coletor tenta salvar screenshot e HTML em `data/debug/`. Essas gravações de
diagnóstico são best effort e erros nelas são deliberadamente ignorados.

### Captura das respostas

O listener aceita respostas JSON cujas URLs contenham `consultaprocessual` ou
`api`. O payload detalhado normalmente vem de
`/pje-consulta-api/api/processos/{id}?tokenDesafio=...`. A coleta é completa
quando encontra `itensProcesso`, `poloAtivo` ou `poloPassivo`.

Se o CAPTCHA é aceito, mas o detalhe não chega em 45 segundos, o resultado é
`PARCIAL`. O HTML e o texto visível são mantidos como fallback, porém a captura
de APIs é a fonte preferencial.

## Pipeline do CAPTCHA

```text
imagem base64 do portal
  → captcha/img_captured.png
  → remoção de ruído/pixelização e recorte da faixa
  → segmentação em seis posições
  → ddddocr por posição
  → normalização para [a-z0-9]
  → concatenação e envio ao PJe
  → limpeza de arquivos temporários
```

Uma posição cujo OCR não retorne exatamente um caractere vira `?`, o que tende
a fazer a tentativa falhar e iniciar novo navegador. A imagem principal é
excluída depois do OCR quando se usa o caminho padrão.

O código em `captcha/` é descrito pelo próprio módulo como cópia temporária de
outro pipeline do repositório e deve ser reconciliado para evitar duplicação de
código. Seu uso depende de autorização institucional e não autoriza contornar
barreiras de acesso.

## Estados da coleta

| Estado | Condição | Repetição automática | Saída individual pela CLI |
|---|---|---|---|
| `SUCESSO` | CAPTCHA aceito e payload detalhado recebido. | Não necessária. | Gravada. |
| `PARCIAL` | CAPTCHA aceito, mas detalhe não chegou em 45 s. | Não na chamada atual; cache pode ser rejeitado depois. | Gravada com aviso. |
| `NAO_ENCONTRADO` | `dadosbasicos` observado com lista vazia. | Não. | Não gravada. |
| `BLOQUEADO` | Resposta HTTP 403 ou 429 observada. | Não. | Não gravada. |
| `FALHA` | CAPTCHA não validado, timeout ou erro de navegação. | Até cinco tentativas, salvo estado terminal. | Não gravada. |

O bruto é finalizado e, por padrão, salvo para todos os estados. Isso permite
auditar falhas sem transformar uma falha técnica em sucesso.

## Normalização e contrato de saída

O normalizador percorre recursivamente os payloads e procura listas e valores
por nomes candidatos. Para campos escalares, a ordem de candidatos define a
prioridade; isso evita que um campo semanticamente secundário encontrado antes
substitua, por exemplo, a data de autuação.

Fontes preferenciais:

- `itensProcesso` com `documento=false`: movimentações;
- `itensProcesso` com `documento=true`: documentos;
- `poloAtivo` e `poloPassivo`: partes;
- `expedientes` não fechados: pendências concretas;
- listas com nomes alternativos: fallback para mudanças de payload;
- linhas datadas do texto da página: fallback final para movimentações.

Movimentações são ordenadas por data crescente, preservando a ordem capturada
como desempate, e renumeradas a partir de 1. Partes são deduplicadas por polo e
nome em minúsculas. Datas brasileiras e ISO são convertidas; valores monetários
brasileiros são transformados em `float`.

O contrato raiz contém:

- `processo`: número, classe, assunto, órgão, unidade, jurisdição, datas, valor
  e situação;
- `partes_interessadas`: polo, nome, tipo, documento e representantes;
- `movimentacoes`: ordem, data, descrição, complemento e referência;
- `documentos`: data, título, tipo e identificador;
- `pendencias`: expedientes abertos e sinal auxiliar da última movimentação;
- `coleta`: fonte, instante, versão, duração, status, tentativas, warnings e
  erros.

Todos os modelos usam `extra="forbid"`. A serialização de retorno passa por
`Processo.model_dump_json()` e volta a `dict`, garantindo formatos JSON para
datas e enums.

### Situação e pendências são heurísticas

`inferir_situacao()` percorre as movimentações da mais recente para a mais
antiga e decide pelo primeiro sinal relevante:

- termos de baixa, trânsito em julgado ou arquivamento definitivo → `BAIXADO`;
- termos de desarquivamento, reativação, suspensão ou retomada → `PENDENTE`;
- com movimentos, mas sem termo conclusivo → `PENDENTE`;
- sem movimentos → `INDEFINIDO`.

Essa classificação não substitui códigos TPU, Datamart, fluxograma homologado
ou regra oficial. Se o processo não estiver baixado, a descrição da última
movimentação também é incluída como pendência auxiliar.

## Fluxo de pesquisa em lote

O notebook lê as duas primeiras colunas da planilha em `data/entrada/`, cria a
lista de números e status CNJ, e controla a coleta pela variável
`COLETAR_AGORA`:

- `True`: chama `coletar_lote(..., pular_existentes=True)`;
- `False`: carrega os brutos existentes;
- sem brutos: usa `exemplos/exemplo_bruto.json` e ativa modo demonstração.

Depois ele mede cobertura, analisa campos, normaliza cada bruto isolando falhas
e grava um array em `processos_trt18.json` ou `processos_trt18_DEMO.json`.

O notebook deve ser iniciado em `entrada-de-dados/` ou em
`entrada-de-dados/pesquisa/`; a resolução atual de `RAIZ` não funciona a partir
da raiz geral do repositório. Há ainda uma mensagem no modo demonstração que
manda definir `COLETAR_AGORA = False` para gerar a coleta, embora a condição no
código seja `True`; trate o código como fonte de verdade.

`PAUSA_ENTRE_PROCESSOS_S` está declarada no coletor, mas não é aplicada por
`_coletar_lote()`. Assim, atualmente há pausa entre tentativas do mesmo CAPTCHA,
mas não há pausa explícita entre processos do lote.

## Segurança, privacidade e operação responsável

Os brutos podem conter nomes, CPF/CNPJ, representantes, movimentações, HTML e
outros dados pessoais. Screenshots de diagnóstico também podem expor dados. Por
isso:

- não versione nem compartilhe `data/brutos/`, `data/saida/` ou `data/debug/`;
- use o exemplo sintético/sanitizado para desenvolvimento e testes;
- não inclua payloads reais em logs, issues, fixtures ou documentação;
- confirme autorização, finalidade, frequência e retenção com a instituição;
- respeite 403/429 e não aumente tentativas para contornar bloqueio;
- prefira cache completo para reduzir acessos repetidos ao portal.

## Limitações e pontos de integração pendentes

- a fachada ainda não está conectada ao backend FastAPI/orquestrador;
- não há testes automatizados no módulo recebido;
- o cache direto no serviço não executa a validação completa do CNJ antes da
  leitura, embora a coleta ao vivo e a CLI a executem;
- o reconhecimento de payload completo aceita qualquer uma das três chaves,
  não necessariamente histórico e polos simultaneamente;
- heurísticas de situação e pendências não são regras oficiais;
- a coleta depende da estrutura, seletores e APIs externas do PJe;
- a lista de navegadores locais é específica do Windows; outros ambientes
  dependem do Chromium do Playwright;
- o pipeline OCR local está duplicado segundo seu README;
- o lote não aplica a constante de pausa entre processos;
- dados brutos e saídas não possuem política automatizada de retenção.

## Validação offline recomendada

Sem acessar o PJe, é possível validar a transformação usando o exemplo local:

```powershell
cd entrada-de-dados
python -c "import json; from pathlib import Path; from normalizador import normalizar; bruto=json.loads(Path('exemplos/exemplo_bruto.json').read_text(encoding='utf-8')); print(normalizar(bruto).model_dump_json(indent=2))"
```

A coleta real exige, além das dependências Python:

```powershell
python -m playwright install chromium
```

Consulte também [architecture.md](ARCHITECTURE.md),
[development.md](development.md), [orchestration.md](orchestration.md) e a
[nota específica do CAPTCHA](../entrada-de-dados/captcha/README.md).
