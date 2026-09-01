# Arquitetura do sistema

## Contexto

O repositório reúne o Chatbot Processual e o domínio ainda provisório do
Simulador de Metas. No chat web, frontend Angular e backend FastAPI são
aplicações irmãs: comunicam-se somente pela API pública HTTP/JSON.

```text
Browser
  └─ Angular (UI, estado, sessionStorage/localStorage)
       └─ /api/* HTTP/JSON
            └─ FastAPI (validação e rotas públicas)
                 ├─ orquestrador processual
                 │    ├─ agentes e serviços determinísticos
                 │    ├─ SQLite
                 │    └─ RAG: Ollama + Qdrant, quando exigido
                 └─ contratos/fluxo provisório de metas
```

O Angular não acessa agentes, banco, filesystem, RAG, Ollama ou Qdrant. A
fronteira detalhada está em [integration.md](integration.md), e a sequência
interna em [orchestration.md](orchestration.md).

O módulo autônomo `entrada-de-dados/` adiciona uma fronteira de aquisição e
normalização dos processos do TRT18:

```text
PJe TRT18 → Playwright/CAPTCHA → bruto auditável → normalização Pydantic → árvore JSON
```

Sua fachada planejada é `servico.obter_processo()`, mas o backend FastAPI ainda
não a chama. O SQLite continua sendo a fonte estruturada do fluxo web atual. O
fluxo, os caches e o contrato do novo módulo estão detalhados em
[data-ingestion.md](data-ingestion.md).

## Fronteira web

O chat usa `POST /api/processos/chat`; o health mínimo usa `GET /api/health`.
Em desenvolvimento, o Angular roda em `localhost:4200` e seu proxy encaminha
`/api/*` ao FastAPI em `localhost:8000`. Por ser same-origin do ponto de vista
do browser, essa topologia não requer CORS. Para produção, prefere-se mesma
origem por reverse proxy/gateway; host e deploy ainda não estão definidos. Se
uma topologia futura separar origens, deverá usar allowlist CORS configurável.

## Estado e processo ativo

Na primeira chamada sem ID utilizável, o backend gera um UUID opaco. O Angular
persiste o `session_id` em `sessionStorage`; o FastAPI associa o ID a `_SESSIONS`,
um dicionário em memória do processo Python. Refresh da mesma aba normalmente
reutiliza o ID. Nova aba normalmente possui storage próprio, ressalvada a cópia
inicial que alguns browsers fazem quando há `opener`.

`session_id` não autentica o usuário. Um ID desconhecido cria contexto vazio, e
reiniciar o backend perde todas as sessões. Não há expiração, persistência
distribuída ou compartilhamento entre workers.

O processo conversacional vigente sai como `resultado.processo_ativo`. O
histórico visual do Angular usa esse campo, guarda até três consultas recentes
em `localStorage` e não constitui estado de sessão.

## Backend processual

A FastAPI valida a entrada e delega ao orquestrador. Este coordena intenção,
contexto/coleta, análise e resposta. SQLite é a fonte estruturada local. Rotas
semânticas usam embeddings via Ollama e índice Qdrant; falha nessas dependências
pode degradar RAG sem eliminar fatos estruturados disponíveis.

Uma exceção capturada no pipeline produz resposta pública segura com
`failed_stage`. Estados como `rag_status=unavailable` ou `error` podem coexistir
com HTTP 2xx e uma `resultado.resposta` válida. Erros HTTP/transporte são outra
classe e a UI não os converte em sucesso fictício.

## Saúde e limites temporais

`GET /api/health` comprova somente que a fronteira FastAPI responde ao contrato
mínimo; não testa agentes, banco, Ollama, Qdrant nem RAG. O cliente Angular
possui timeout de 135 s. O orçamento total backend de 120 s é uma política
planejada, mas não foi implementado e não deve ser tratado como garantia.

## Fronteiras de domínio

- **Chatbot Processual:** fluxo Angular–FastAPI integrado, com consulta
  estruturada e RAG condicional.
- **Entrada de dados TRT18:** coletor e normalizador autônomos, com fronteira de
  serviço pronta, ainda não conectados ao orquestrador/FastAPI.
- **Simulador de Metas:** `simulador-de-metas/` contém estudos próprios; os
  contratos backend atuais ainda retornam estado provisório/não integrado e não
  representam regras oficiais homologadas.
- **Fluxo híbrido processo × meta:** existe um orquestrador backend provisório
  para avaliar sinais processuais contra contratos de meta; isso não incorpora
  o simulador ao frontend do chat nem torna seus critérios oficiais.

## Limitações arquiteturais conhecidas

- sessão somente em memória e sem autenticação;
- deploy/origem de produção indefinidos;
- proxy Angular é apenas de desenvolvimento;
- deadline total backend de 120 s não implementado;
- dependências externas são condicionais à capacidade escolhida;
- coleta TRT18 ainda não integrada ao backend e dependente de portal/CAPTCHA;
- artefatos brutos podem conter dados pessoais e exigem retenção controlada;
- regras oficiais do simulador de metas não integradas.
