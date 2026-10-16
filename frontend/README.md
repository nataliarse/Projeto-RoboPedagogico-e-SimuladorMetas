# Frontend do Chatbot Processual

Aplicação Angular que apresenta o chat processual e consome exclusivamente a
API pública FastAPI por HTTP/JSON. Ela não conhece agentes, SQLite, Ollama,
Qdrant ou outros detalhes internos do backend.

## Preparação e execução

O bootstrap foi validado com Node.js 24.19.0 e npm 11.17.0. O projeto usa
Angular 21.2.x e mantém o grafo reproduzível em `package-lock.json`.

```text
cd frontend
npm ci
npm start
```

A interface fica em `http://localhost:4200`. `npm start` carrega o proxy
versionado em `proxy.conf.json`: `/api/processos/*` e `/api/metas/*` seguem
para o backend processual em `127.0.0.1:8000`; `/api/simulador/*` segue para o
simulador em `127.0.0.1:8001` com reescrita para o prefixo interno `/api`.
Não adicione URLs absolutas aos serviços Angular.

O chat envia `POST /api/processos/chat`; o indicador de disponibilidade ainda
consulta o alias legado `GET /api/health`, encaminhado ao backend processual.
Um health 200 comprova apenas que a fronteira FastAPI responde
ao contrato mínimo, não que banco, agentes, Ollama, Qdrant ou RAG estejam
saudáveis.

## Testes, build e typecheck

```text
npm test -- --watch=false
npm run build
npx tsc -p tsconfig.app.json --noEmit
```

## Sessão, histórico e erros

- `session_id` fica em `sessionStorage`. A primeira chamada pode omiti-lo; o
  backend gera um ID opaco, e as chamadas seguintes da aba o reutilizam.
- O histórico visual fica em `localStorage`, é alimentado por
  `resultado.processo_ativo`, deduplica o processo mais recente e mantém até
  três registros. Histórico não é sessão.
- A interface exibe `resultado.resposta`, inclusive em resposta controlada 2xx.
  `failed_stage` e `rag_status` descrevem falha/degradação sem transformar a
  resposta automaticamente em erro de transporte.
- Timeout, falha HTTP ou indisponibilidade não geram resposta mock, não iniciam
  retry automático e sempre liberam o estado de carregamento.

`sessionStorage` normalmente sobrevive ao refresh da mesma aba. Nova aba tem
contexto próprio, embora uma aba aberta com `opener` possa receber uma cópia
inicial do storage conforme o browser. Reiniciar o backend perde a sessão do
lado servidor, mesmo que o ID permaneça no browser.

## Artefatos locais

Não versione nem transporte `node_modules/`, `.angular/cache/` ou `dist/` entre
máquinas/sistemas operacionais. Reconstrua-os com `npm ci`.

Detalhes: [integração](../docs/integration.md),
[arquitetura](../docs/ARCHITECTURE.md) e
[desenvolvimento](../docs/development.md).
