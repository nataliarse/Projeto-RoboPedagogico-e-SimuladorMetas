# Arquitetura do sistema

## Visão atual

```text
Browser → Angular → FastAPI → orquestrador processual
                              ├─ Agent 1: intenção
                              ├─ Agent 2: contexto e processo ativo
                              │    └─ CollectorAdapter
                              │         ├─ process_repository → SQLite
                              │         └─ trt18_collector → TRT18/cache bruto
                              ├─ Agent 3: análise estruturada/RAG
                              └─ Agent 4: resposta pública
```

O Angular consome somente os DTOs HTTP/JSON do FastAPI. A API valida a entrada,
resolve a sessão em memória e delega ao orquestrador. O orquestrador coordena os
quatro agentes, progresso e falhas controladas.

## Ownership e fronteiras

- **Chatbot/orquestrador:** decide intenção, contexto conversacional, rota
  estruturada ou RAG e formato público da resposta.
- **Agent 1:** classifica a intenção e extrai o número quando aplicável.
- **Agent 2:** reutiliza o processo ativo e solicita lookup/aquisição pela
  fronteira. Não conhece Playwright, CAPTCHA, cache bruto ou browser.
- **`collector_adapter`:** única fronteira do chatbot com o collector; valida,
  consulta localmente, traduz estados, coleta quando necessário, persiste e
  relê o sucesso.
- **`trt18_collector`:** valida CNJ, adquire/cacheia o bruto, normaliza e devolve
  o modelo público Pydantic.
- **`process_repository`:** sanitiza e persiste a árvore normalizada e seus
  chunks no SQLite; fornece a fonte local consumida pelo chatbot.
- **Agent 3:** analisa fatos estruturados e, quando a rota exige, consulta RAG.
- **Agent 4:** redige e filtra a resposta pública.

## Local-first e persistência

```text
número válido → lookup SQLite
  ├─ encontrado → LOCAL_HIT
  └─ ausente → trt18_collector
       ├─ sucesso válido → transação SQLite → reload → COLLECTED
       └─ estado negativo → sem persistência e sem processo ativo novo
```

O processo retornado após coleta vem do reload do SQLite, não do payload bruto
em memória. A transação preserva o estado anterior se a persistência ou geração
de chunks falhar.

## Contrato de estados

| Estado do adapter | Semântica | Processo entregue | Retry automático |
|---|---|---:|---:|
| `LOCAL_HIT` | encontrado no SQLite | sim | não |
| `COLLECTED` | coletado, persistido e relido | sim | não |
| `INVALID_NUMBER` | número rejeitado pela validação CNJ | não | não |
| `NOT_FOUND` | número válido, ausência confirmada na fonte | não | não |
| `PARTIAL` | aquisição incompleta | não | não |
| `BLOCKED` | portal recusou/limitou a aquisição | não | não |
| `FAILED` | falha técnica ou resultado inconsistente | não | não |

`NOT_FOUND`, `PARTIAL`, `BLOCKED` e `FAILED` não são equivalentes. O atributo
`retryable` informa que uma nova tentativa manual pode fazer sentido, mas não
aciona scheduler, fila ou repetição automática no chatbot.

## Cache bruto e SQLite consumidor

`entrada-de-dados/data/brutos/` contém evidência da aquisição e pode registrar
HTML, respostas e erros, inclusive em resultados incompletos. O SQLite do
backend contém a árvore normalizada e sanitizada consumida pela conversa.
Somente sucesso externo válido cruza a fronteira `persist → reload`.

O bruto pode conter dados pessoais. O repository remove documento de parte e
identificador interno de documento antes da persistência/chunking; Agent 3
repete a sanitização antes do modelo, e Agent 4 aplica controles de saída. Essa
defesa em profundidade não autoriza versionar ou divulgar dados reais.

## Sessão, RAG e outros domínios

`session_id` referencia `_SESSIONS`, em memória do processo Python. Reinício do
backend perde a conversa, mas não o processo no SQLite. Consultas estruturadas
não dependem de Ollama/Qdrant; perguntas semânticas podem usar ambos e expõem
degradação em `rag_status` quando indisponíveis.

`simulador-de-metas/` permanece uma frente separada e provisória; os contratos
atuais não comprovam regras oficiais homologadas.

## Limitações

- sessão sem autenticação, expiração ou persistência distribuída;
- deploy e origem de produção não definidos;
- deadline total backend de 120 s ainda não implementado;
- portal/CAPTCHA podem impedir a coleta e não devem ser contornados;
- conteúdo integral de documentos não é persistido pelo contrato consumidor;
- heurísticas do collector não substituem classificação processual oficial.

Consulte [orchestration.md](orchestration.md),
[data-ingestion.md](data-ingestion.md) e [integration.md](integration.md).
