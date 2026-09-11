# Orquestração

## Fluxo conversacional

```text
entrada → Agent 1 (intenção) → Agent 2 (contexto)
                              → processo ativo?
                              → lookup SQLite
                              → miss válido → CollectorAdapter → collector
                                             → persist → reload SQLite
                              → rota estruturada ou RAG
        → Agent 3 (análise) → Agent 4 (resposta) → DTO público
```

O Angular envia `mensagem` e `session_id` ao FastAPI. A API cria ou recupera a
sessão, chama o orquestrador e devolve `resultado.resposta`, processo ativo,
`collection_status`, `rag_status`, `failed_stage` e progresso público conforme
os DTOs.

## Processo ativo e local-first

Agent 2 reutiliza o processo ativo quando a pergunta se refere ao mesmo
contexto. Para um número novo, o `CollectorAdapter` valida e consulta o SQLite
antes da aquisição externa. Um hit local não coleta nem escreve.

No miss válido, o adapter chama somente a API pública `trt18_collector`. Um
`SUCESSO` consistente é persistido por `ingest_processes` e relido por
`find_process_by_number`; somente então se torna processo ativo. Uma pergunta
seguinte, outra sessão ou um reinício lógico pode recuperar esse registro sem
recoleta. Estados negativos não substituem processo persistido nem gravam uma
árvore parcial.

## Estados e resposta

O adapter preserva `LOCAL_HIT`, `COLLECTED`, `INVALID_NUMBER`, `NOT_FOUND`,
`PARTIAL`, `BLOCKED` e `FAILED`. Agent 2 transporta os estados em minúsculas;
hits locais aparecem como `success` e aquisições persistidas como `collected`.
Cada estado negativo recebe semântica pública segura: ausência confirmada não é
confundida com parcialidade, bloqueio ou falha técnica.

Agent 3 privilegia dados estruturados e chama RAG somente quando a rota exige
conteúdo semântico. Falha de embeddings/Qdrant mantém fatos estruturados e é
indicada por `rag_status`. Exceção capturada pelo orquestrador produz resposta
segura com `failed_stage`; falha HTTP/transporte continua sendo erro técnico.

## Progresso e privacidade

Eventos de progresso informam classificação, lookup, aquisição, persistência,
rota, análise e resposta sem expor exceção bruta, path SQLite, HTML, CAPTCHA,
cookie ou token. O repository sanitiza documento de parte e identificador
interno de documento; as camadas de análise e resposta aplicam novas barreiras.

## Retry manual e degradação

Não há scheduler, fila ou retry automático no chatbot ou frontend. O campo
`retryable` do resultado apenas classifica se uma nova tentativa pode ser útil.
O usuário inicia o retry enviando nova consulta; ela repete o fluxo local-first.
Internamente, uma única aquisição do collector pode tentar o CAPTCHA até o
limite próprio, mas bloqueio e ausência confirmada encerram a chamada.

## Sessão e limitações

`_SESSIONS` guarda conversa, processo ativo e última intenção em memória. O
frontend mantém o ID em `sessionStorage` e histórico visual em `localStorage`.
Reiniciar o backend perde a conversa, mas o SQLite permanece. `session_id` não
é autenticação.

Limitações atuais: portal/CAPTCHA podem impedir aquisição; RAG depende de
Ollama/Qdrant quando requerido; não existe deadline total backend de 120 s; e
o simulador de metas permanece provisório e separado do chat.

Consulte [ARCHITECTURE.md](ARCHITECTURE.md),
[data-ingestion.md](data-ingestion.md) e [integration.md](integration.md).
