# Ingestão e coleta de dados processuais do TRT18

## Produto e consumidores

O package `trt18_collector`, em `entrada-de-dados/`, realiza a aquisição e a
normalização externa. Ele atende a consulta individual usada pelo chatbot e a
CLI, enquanto `pesquisa/pipeline.ipynb` mantém o fluxo separado de pesquisa em
lote. O notebook não é requisito do backend e a consulta individual não
substitui a finalidade exploratória do notebook.

```text
número CNJ → validação → cache aproveitável?
           → aquisição Playwright, quando necessária e autorizada
           → bruto auditável → normalização → modelos Pydantic → dict público
```

A API pública leve é `trt18_collector.obter_processo()`. Dependências pesadas
de browser/OCR são carregadas somente quando há coleta real.

## Responsabilidades

| Componente | Responsabilidade |
|---|---|
| `trt18_collector.service` | escolhe cache/coleta, normaliza e serializa o modelo público |
| `trt18_collector.collector_trt18` | valida CNJ, opera aquisição, estados e cache bruto |
| `trt18_collector.normalizer` | converte o bruto para a árvore canônica |
| `trt18_collector.models` | modelos Pydantic com campos extras proibidos |
| `CollectorAdapter` | traduz o contrato produtor para o chatbot |
| `process_repository.ingest_processes` | persiste no SQLite consumidor; não pertence ao collector |

O fluxo integrado é:

```text
CollectorAdapter → obter_processo → árvore normalizada
                 → ingest_processes → SQLite → reload → chatbot
```

O collector não grava diretamente no SQLite do chatbot.

## Validação e estados do produtor

A validação canônica remove pontuação, exige 20 dígitos, verifica DV módulo 97,
segmento da Justiça do Trabalho e TRT18 antes da aquisição. O cache é
aproveitável somente se contiver payload estrutural esperado.

| Estado produtor | Tradução no adapter | Significado |
|---|---|---|
| `SUCESSO` | `COLLECTED` | árvore válida apta ao ciclo persist/reload |
| `PARCIAL` | `PARTIAL` | CAPTCHA aceito, mas detalhe incompleto |
| `NAO_ENCONTRADO` | `NOT_FOUND` | ausência confirmada para número válido |
| `BLOQUEADO` | `BLOCKED` | resposta 403/429 observada |
| `FALHA` | `FAILED` | CAPTCHA, timeout, navegação ou resultado inválido |

Nenhum estado negativo é persistido pelo adapter. `NOT_FOUND` não significa
falha técnica; `PARTIAL`, `BLOCKED` e `FAILED` tampouco significam ausência.

## Cache, dados e paths

Os paths pertencem ao módulo `entrada-de-dados/`, independentemente do CWD:

- `data/brutos/<numero>.json`: captura auditável e cache do produtor;
- `data/saida/`: saídas da CLI e da pesquisa;
- `data/debug/`: screenshots, HTML e imagem transitória de CAPTCHA em falha;
- `exemplos/exemplo_bruto.json`: fixture sanitizada para uso offline.

O raw pode conter respostas, HTML, erros e dados pessoais, inclusive para
estados sem sucesso. O SQLite consumidor, configurado pelo backend, recebe
somente sucesso normalizado e sanitizado. Não versione bruto, saída, debug ou
dados reais.

## Playwright e CAPTCHA

Instale o extra oficial e o browser:

```text
cd entrada-de-dados
python -m pip install -e ".[collect]"
python -m playwright install chromium
```

O Chromium do Playwright é o padrão. A variável opcional
`TRT18_COLLECTOR_BROWSER_EXECUTABLE` aceita outro executável válido. A coleta
pode realizar até cinco tentativas internas de CAPTCHA, com intervalo entre
tentativas; bloqueio e ausência confirmada são terminais. Isso não é retry
automático do chatbot.

O portal, sua estrutura, o CAPTCHA e a rede podem impedir a aquisição. Use a
automação somente com autorização institucional, respeite 403/429 e não altere
limites para contornar barreiras. O projeto não documenta técnica de evasão.

## Consulta individual e pesquisa

A CLI individual (`entrada-de-dados/app.py`) usa a fachada do package e pode
operar apenas com cache por `--so-cache`. O notebook instala dependências
separadas de `requirements-notebook.txt`, lê uma amostra e produz saída de
pesquisa em lote. Não execute coleta em lote como parte do bootstrap do backend.

## Normalização, privacidade e limitações

A árvore contém processo, partes, movimentações, metadados de documentos,
pendências e coleta. A situação processual é heurística, não classificação
oficial. O repository remove documento de parte e `id_documento`; Agent 3
sanitiza novamente antes de um modelo e Agent 4 protege a saída.

Limitações confirmadas:

- mudanças no portal podem quebrar seletores ou payloads;
- o bruto pode registrar falhas e dados que não chegam ao SQLite;
- o lote não aplica pausa explícita entre processos;
- não há política automatizada de retenção dos artefatos;
- o conteúdo integral de peças não integra o contrato persistido do chatbot.

Consulte [ARCHITECTURE.md](ARCHITECTURE.md),
[development.md](development.md) e [orchestration.md](orchestration.md).
