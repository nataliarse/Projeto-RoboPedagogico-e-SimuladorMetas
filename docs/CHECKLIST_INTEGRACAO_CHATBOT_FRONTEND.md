# Checklist de Integração — Chatbot Processual + Frontend Angular

**Branch-alvo informada:** `feat/integra_chatbot_frontend`  
**Data do baseline:** 18/08/2026  
**Escopo:** integrar `frontend/` ao `chatbot_processual_ai/` de forma rastreável, testável e reversível, preservando `simulador-de-metas/` fora do escopo desta integração.  
**Regra operacional:** esta checklist deve ser executada em unidades pequenas. Um item com ID rastreável não autoriza avanço automático para outro item.

---

## 0. Resultado esperado

Ao final desta checklist:

- o Angular consome a API FastAPI real sem mocks de sucesso;
- frontend e backend compartilham um contrato HTTP documentado e tipado;
- cada navegador/sessão possui contexto conversacional isolado;
- a aplicação trata sucesso, falha HTTP e falha controlada do pipeline de forma distinta;
- o histórico do frontend usa o processo realmente identificado pelo backend;
- desenvolvimento local possui fluxo reproduzível em ambiente limpo;
- testes de backend, frontend e integração cobrem o contrato principal;
- documentação do repositório descreve a arquitetura real;
- caches, dependências instaladas e artefatos locais não entram no versionamento;
- a branch só fica pronta para merge quando os gates finais forem atendidos.

---

## 1. Evidências do baseline atual

### Backend

- Existe API FastAPI em `chatbot_processual_ai/api.py`.
- Endpoint de chat real: `POST /api/processos/chat`.
- Entrada atual: `session_id: str | None` + `mensagem: str`.
- Saída atual: `session_id` + `resultado` estruturado.
- `resultado` expõe pelo menos: `tipo`, `intent`, `resposta`, `processo_ativo`, `collection_status`, `failed_stage`, `rag_status` e `fontes`.
- A ausência de `session_id` é normalizada atualmente para o valor fixo `default`.
- Sessões ficam em memória no processo Python (`_SESSIONS`).
- Suite backend executada a partir de `chatbot_processual_ai/`: **29 testes aprovados**.
- A mesma suite executada a partir da raiz do repositório não coleta corretamente por causa dos imports atuais; o diretório de execução deve ser documentado ou posteriormente normalizado.
- Não foi identificada cobertura específica da camada HTTP/FastAPI nos testes existentes.

### Frontend

- Angular `21.2.x`, TypeScript `5.9.x`, RxJS `7.8.x`.
- `ChatService` chama atualmente `POST /api/chat`.
- O corpo enviado atualmente contém apenas `{ mensagem }`.
- O retorno é tipado como `Observable<any>`.
- `ChatComponent` ignora a resposta HTTP e executa `responderMock()` tanto em `next` quanto em `error`.
- O histórico grava atualmente a pergunta do usuário no campo `numero_processo`.
- O estado possui `erro`, mas a interface atual não apresenta esse erro ao usuário.
- O status “Sistema disponível” está estático na interface.
- Timeout HTTP do frontend: 60 s; timeout configurável do Ollama no backend: 60 s por padrão.
- Código de aplicação do frontend passou em `tsc -p tsconfig.app.json --noEmit`.
- Testes TypeScript do frontend **não compilam** no baseline por imports antigos (`Chat`, `LocalStorage`, `State` etc.).
- O teste de `App` ainda espera conteúdo da tela inicial gerada pelo Angular e está semanticamente desatualizado.
- O pacote recebido contém `node_modules/` e `.angular/cache/`; ambos já constam no `.gitignore` interno do frontend, portanto é necessário verificar se estão apenas no arquivo recebido ou se chegaram a ser rastreados pelo Git.
- O build Angular não pôde ser validado no ambiente Linux usado para este diagnóstico porque o `node_modules` recebido contém binário `esbuild` de Windows. Isso reforça que a validação correta deve partir de `npm ci` em ambiente limpo, e não do `node_modules` transportado.

### Governança/documentação

- `AGENTS.md` existe na raiz e já define diagnóstico, escopo, testes, documentação, Git, checklist e critérios de validação.
- `.codex/rules/safety.rules` existe no material recebido.
- O `.gitignore` raiz ignora `.codex/`; se `safety.rules` ainda não estiver rastreado, ele não será incluído automaticamente em commit. Isso precisa ser resolvido deliberadamente.
- `docs/ARCHITECTURE.md` possui conteúdo técnico relevante.
- `docs/design_philosophy.md`, `docs/development.md` e `docs/orchestration.md` estão vazios no baseline recebido.
- O `README.md` raiz contém recomendações históricas (ex.: Streamlit/LangGraph) que não representam integralmente a implementação atual Angular + FastAPI.
- `frontend/README.md` permanece majoritariamente como README padrão gerado pelo Angular CLI.

---

## 2. Convenção de status

Use apenas:

- `TODO` — ainda não iniciado;
- `READY` — diagnóstico/precondições permitem iniciar;
- `IN_PROGRESS` — investigação ou implementação iniciada;
- `BLOCKED` — impedimento objetivo;
- `IMPLEMENTED` — código/documentação concluído, validação final ainda pendente;
- `VALIDATED` — critérios de aceite, testes e diff confirmados;
- `REJECTED` — solução implementada foi considerada inadequada;
- `SUPERSEDED` — item substituído formalmente por outro.

**Nenhum item deve ser marcado `VALIDATED` apenas porque o código foi escrito.**

---

# FASE P0 — Baseline, higiene e governança

## INT-P0-001 — Confirmar branch e worktree de integração

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante  
**Objetivo:** garantir que todo o trabalho ocorra na branch isolada correta.

### Ações

- [x] Executar `git branch --show-current`.
- [x] Confirmar `feat/integra_chatbot_frontend`.
- [x] Executar `git status --short`.
- [x] Registrar alterações preexistentes que não pertencem à integração.
- [x] Não limpar, restaurar ou sobrescrever alterações preexistentes automaticamente.

### Critério de aceite

- branch confirmada;
- estado inicial do worktree registrado;
- nenhuma mudança preexistente foi perdida.

---

## INT-P0-002 — Auditar arquivos transportados vs. arquivos rastreados

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante

### Ações

- [x] Verificar se `frontend/node_modules/` está rastreado com `git ls-files frontend/node_modules`.
- [x] Verificar se `frontend/.angular/` está rastreado com `git ls-files frontend/.angular`.
- [x] Verificar `__pycache__`, `.pyc`, bancos locais, `.env` e outros artefatos gerados.
- [x] Se algum artefato estiver rastreado, remover apenas do índice Git de forma não destrutiva para o worktree.
- [x] Confirmar que `frontend/package-lock.json` permanece versionado.
- [x] Confirmar que `.env.example` permanece versionado e `.env` real não.

### Critério de aceite

- dependências instaladas, caches, segredos e artefatos locais não são parte do versionamento;
- lockfiles e exemplos de configuração necessários permanecem rastreados.

---

## INT-P0-003 — Tornar as regras Codex versionáveis de forma intencional

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante para uso confiável do Codex

### Problema observado

O `.gitignore` raiz contém `.codex/`, enquanto o projeto pretende usar `.codex/rules/safety.rules` como política compartilhada.

### Ações

- [x] Executar `git check-ignore -v .codex/rules/safety.rules`.
- [x] Confirmar se o arquivo já está rastreado com `git ls-files .codex/rules/safety.rules`.
- [x] Definir política: versionar somente regras compartilhadas e continuar ignorando estado local do Codex.
- [x] Ajustar `.gitignore` de forma mínima para permitir `.codex/rules/safety.rules` sem liberar indiscriminadamente todo `.codex/`.
- [x] Validar com `git check-ignore` e `git status`.

### Critério de aceite

- `safety.rules` compartilhado aparece como rastreável;
- arquivos locais/sensíveis do Codex continuam ignorados;
- nenhuma regra de segurança foi silenciosamente removida.

---

## INT-P0-004 — Registrar baseline técnico reproduzível

**Status inicial:** `VALIDATED`

### Ações

- [x] Backend: `cd chatbot_processual_ai && python -m pytest tests -q`.
- [x] Registrar resultado esperado inicial de 29 testes aprovados, salvo mudança legítima no ambiente/projeto.
- [x] Frontend: remover/ignorar `node_modules` transportado para fins de validação.
- [x] Frontend: executar `npm ci` em ambiente compatível.
- [x] Executar `npm run build`.
- [x] Executar `npm test -- --watch=false`.
- [x] Se testes falharem por problemas preexistentes, registrar como baseline; não mascarar.
- [x] Executar `node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit` quando útil como validação focada.

### Critério de aceite

- baseline backend e frontend registrado com comandos e resultados reais;
- falhas preexistentes distinguidas de regressões futuras.

### Resultado da execução em 20/08/2026

- Backend: Python 3.12.10 e pip 26.1.2; o comando previsto com `pytest`
  não pôde coletar testes porque o módulo não está instalado. A suíte
  documentada equivalente com `unittest` executou 29 testes, todos aprovados,
  em 1,294 s.
- Frontend: `node`, `npm` e `npx` não estão instalados ou disponíveis no
  `PATH`; por isso `npm ci`, build, testes e validações TypeScript não puderam
  ser executados.
- Classificação: `BLOCKED` por limitação ambiental objetiva. Nenhuma
  dependência foi instalada, nenhum código funcional ou manifesto foi alterado
  e nenhuma falha foi mascarada.

### Resultado da recuperação em 20/08/2026

- Ambiente: `.venv` local ignorado com Python 3.12.10, pip 25.0.1 e pytest
  9.1.1; Node 24.19.0 LTS instalado no escopo do usuário, com npm/npx 11.17.0.
- Backend: `python -m pytest tests -q` executou 29 testes; 29 passaram em
  1,77 s, com um aviso ambiental de cache sem impacto na suíte.
- Frontend: `npm ci` instalou 468 pacotes e preservou os hashes de
  `package.json` e `package-lock.json`; a auditoria reportou 28 vulnerabilidades
  no grafo fixado pelo lockfile.
- Build: aprovado em 4,167 s, com aviso preexistente de budget CSS em
  `src/app/features/chat/chat.css`.
- Testes: iniciaram e falharam antes da coleta por quatro erros TS2305 em specs
  desatualizadas; nenhuma spec foi corrigida.
- TypeScript: `tsconfig.app.json` aprovado; `tsconfig.spec.json` falhou nos
  mesmos quatro imports. Aplicação compila; infraestrutura/specs apresentam
  falha preexistente.
- Classificação final: `VALIDATED`; baseline integralmente executado, observado
  e classificado, sem alteração funcional, de manifests ou de integração.

---

## INT-P0-005 — Definir explicitamente o escopo negativo

**Status inicial:** `VALIDATED`

### Não faz parte desta integração, salvo dependência comprovada

- [x] Não implementar novas regras do simulador de metas.
- [x] Não alterar modelos ARIMA.
- [x] Não refatorar agentes do chatbot sem necessidade da fronteira HTTP.
- [x] Não migrar SQLite/Qdrant/Ollama apenas para facilitar o frontend.
- [x] Não renomear em massa o projeto Angular nesta fase.
- [x] Não introduzir autenticação, deploy ou persistência distribuída de sessão sem decisão específica.

### Critério de aceite

- escopo negativo documentado no material de integração e respeitado no diff.

**Evidência:** `docs/integration.md` formaliza a integração conservadora, os
não objetivos por categoria, o tratamento de dívida técnica e a exceção por
dependência comprovada. O diff do item é exclusivamente documental.

---

# FASE P1 — Arquitetura e contrato antes de código

## INT-P1-001 — Formalizar topologia da integração

**Status inicial:** `VALIDATED`
**Dependência:** P0

### Decisão alvo

```text
Browser / Angular
      |
      | HTTP JSON
      v
FastAPI (/api/...)
      |
      v
Orquestradores / agentes / serviços / SQLite / RAG / Ollama
```

### Ações

- [x] Declarar que frontend e backend são aplicações irmãs, não código a ser fundido internamente.
- [x] Declarar que o frontend conhece apenas a API pública.
- [x] Declarar que detalhes de agentes, RAG, SQLite e Ollama não vazam para componentes Angular.
- [x] Registrar em `docs/ARCHITECTURE.md` ou documento de integração específico.

### Critério de aceite

- fronteira de responsabilidade inequívoca para humano e agente de código.

**Evidência:** `docs/integration.md` formaliza HTTP/JSON como única fronteira
Angular–FastAPI, explicita as direções permitidas e proibidas de dependência,
encapsula os componentes internos do backend e mantém decisões contratuais dos
itens `INT-P1-002` a `INT-P1-006` fora deste item. Nenhum código funcional foi
alterado.

---

## INT-P1-002 — Congelar contrato HTTP v1 do chat processual

**Status inicial:** `VALIDATED`
**Dependência:** INT-P1-001

### Contrato base existente

`POST /api/processos/chat`

Request:

```json
{
  "session_id": "string-ou-null",
  "mensagem": "texto do usuário"
}
```

Response:

```json
{
  "session_id": "identificador da sessão",
  "resultado": {
    "tipo": "processual_chat",
    "intent": "string-ou-null",
    "resposta": "texto para o usuário",
    "processo_ativo": "string-ou-null",
    "collection_status": "string-ou-null",
    "failed_stage": "string-ou-null",
    "rag_status": "string-ou-null",
    "fontes": []
  }
}
```

### Ações

- [x] Validar nomes, nulabilidade e semântica de cada campo.
- [x] Decidir quais campos são obrigatórios na API v1.
- [x] Decidir compatibilidade futura sem acoplar o frontend a campos internos desnecessários.
- [x] Documentar exemplos de sucesso, processo ausente, falha controlada e erro HTTP.
- [x] Registrar política de versionamento/breaking change do contrato.

### Critério de aceite

- backend, frontend, testes e documentação usam o mesmo contrato.

**Evidência:** `docs/integration.md` congela o contrato lógico v1 observado em
`chatbot_processual_ai/api.py`, `schemas/processual_contracts.py` e no
orquestrador, incluindo omissão versus `null`, normalização, estrutura completa
da resposta, classificação de campos, semântica HTTP, exemplos e
compatibilidade. A divergência atual do `ChatService` (`/api/chat`, body sem
`session_id` e `Observable<any>`) está explicitamente registrada como estado a
ser alinhado em P3; nenhum backend, frontend, schema ou DTO foi alterado neste
item documental. Regressão backend: 29 testes aprovados; validação dirigida
ASGI confirmou `200`, `422`, `404` e `405` e a forma JSON observada.

---

## INT-P1-003 — Definir estratégia de sessão web

**Status inicial:** `VALIDATED`
**Prioridade:** bloqueante para uso multiusuário

### Problema observado

Quando o cliente não envia `session_id`, o backend usa atualmente `default`; clientes diferentes podem compartilhar estado conversacional no mesmo processo Python.

### Decisão recomendada

- backend gera identificador opaco/UUID quando a requisição não possui sessão válida;
- frontend captura `response.session_id`;
- frontend armazena a sessão em `sessionStorage` para manter contexto durante a aba/sessão do navegador;
- chamadas seguintes reutilizam o mesmo ID;
- sessão em memória do backend permanece explicitamente uma limitação do MVP.

### Ações

- [x] Aprovar estratégia.
- [x] Definir comportamento em refresh, nova aba, fechamento do navegador e backend reiniciado.
- [x] Definir limite/expiração futura para `_SESSIONS` ou registrar dívida técnica.
- [x] Garantir que IDs não carreguem dados pessoais/sensíveis.

### Critério de aceite

- dois clientes sem `session_id` não recebem automaticamente a mesma sessão;
- segunda pergunta do mesmo cliente preserva `processo_ativo`.

**Evidência:** `docs/integration.md` registra a decisão-alvo de UUID opaco
gerado pelo backend na ausência de ID utilizável, reuso do mesmo ID,
`sessionStorage`, ciclo de vida completo, isolamento de `processo_ativo`,
privacidade e limitações de `_SESSIONS`. ID válido desconhecido cria contexto
vazio sob o próprio ID, sem promessa de recuperar estado perdido. A semântica
de abas considera a possível cópia inicial quando existe `opener`. Nenhum
código, teste ou item posterior foi alterado.

---

## INT-P1-004 — Definir semântica de erros e falhas controladas

**Status inicial:** `VALIDATED`

### Ações

- [x] Diferenciar erro de transporte/HTTP de resposta válida com `failed_stage`.
- [x] Definir texto seguro mostrado ao usuário em cada caso.
- [x] Definir quais detalhes ficam apenas em logs/trace.
- [x] Não expor stack trace, path local, configuração, IDs internos do banco ou Qdrant.
- [x] Definir como `collection_status`, `rag_status` e `failed_stage` influenciam UI sem transformar limitação em “sucesso verde”.

### Critério de aceite

- tratamento previsível e documentado no frontend e backend.

**Evidência:** `docs/integration.md` registra o comportamento factual do
endpoint e a precedência entre transporte, `4xx`/`5xx`, falha controlada,
degradação e sucesso. A matriz preserva o contrato P1-002, define o papel de
`failed_stage`, `rag_status`, `collection_status` e `resultado.resposta`, separa
mensagem pública de diagnóstico, proíbe mock como fallback e reserva timeout a
`INT-P1-005`. Nenhum código funcional, schema, sessão, healthcheck ou item
posterior foi alterado.

---

## INT-P1-005 — Definir política de timeout

**Status inicial:** `VALIDATED`

### Ações

- [x] Mapear timeout interno do Ollama e demais operações demoradas.
- [x] Garantir que timeout do frontend seja maior que o limite interno relevante, com margem de transporte/processamento.
- [x] Evitar timeout infinito.
- [x] Definir mensagem de timeout distinta de erro genérico.
- [x] Registrar valores em documentação/configuração, não espalhar números mágicos.

### Critério de aceite

- o frontend não aborta rotineiramente a requisição no mesmo instante em que o backend atinge seu próprio limite.

**Evidência:** `docs/integration.md` registra os limites atuais (`60 s` no
Angular e por chamada Ollama/embedding, `10 s` por chamada Qdrant e ausência de
limite total FastAPI), comprova chamadas sequenciais e o laço de embeddings do
RAG, e aprova um orçamento total backend de `120 s` com timeout cliente de
`135 s`. A margem de `15 s`, a classificação, a mensagem segura, a
recuperabilidade, a sessão e as fontes futuras de configuração estão
definidas. Nenhum timeout ou código funcional foi alterado.

---

## INT-P1-006 — Definir topologia de rede em desenvolvimento e produção

**Status inicial:** `VALIDATED`

### Recomendação

- desenvolvimento: Angular em `localhost:4200` com proxy `/api` para FastAPI em `localhost:8000`;
- produção: preferir mesma origem/reverse proxy quando a infraestrutura permitir;
- se houver origens distintas: CORS explícito por allowlist, nunca `*` por conveniência sem necessidade.

### Ações

- [x] Aprovar topologia local.
- [x] Aprovar origem/URL de produção quando conhecida.
- [x] Definir se será necessário `CORSMiddleware`.
- [x] Não codificar `http://localhost:8000` dentro de componentes.

### Critério de aceite

- URL da API tem uma única estratégia definida e reproduzível por ambiente.

**Evidência:** `docs/integration.md` registra o diagnóstico factual, aprova
`/api/...` relativo com proxy Angular `localhost:4200` → FastAPI
`localhost:8000`, dispensa CORS local nessa topologia e prefere mesma origem em
produção. A origem real permanece não definida; se a infraestrutura exigir
origens distintas, `INT-P2-005` deverá usar allowlist explícita. `INT-P5-001`
implementará o proxy e `INT-P5-004` o workflow. Contrato, sessão, erros e timeout
anteriores foram preservados; nenhum código, proxy, CORS ou item P2 foi alterado.

---

# FASE P2 — Fortalecimento da fronteira backend

## INT-P2-001 — Adicionar testes HTTP do endpoint processual

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Dependência:** contrato P1 validado

### Cobertura mínima

- [x] request válido retorna HTTP esperado;
- [x] estrutura de response respeita contrato;
- [x] `session_id` é retornado;
- [x] `resultado.resposta` é string utilizável;
- [x] `processo_ativo` é retornado após consulta válida;
- [x] segunda pergunta com mesma sessão preserva contexto;
- [x] mensagens inválidas/vazias seguem política definida;
- [x] falha controlada não vaza detalhe sensível.

### Critério de aceite

- contrato principal tem teste automatizado na camada FastAPI.

**Evidência:** `tests/test_api_processual_chat.py` exerce a aplicação ASGI/FastAPI
real com quatro cenários determinísticos: response contratual com processo ativo,
continuidade por `session_id` explícito, payload sem `mensagem` rejeitado com
`422` e falha controlada `200` sem vazamento do marcador técnico sintético. A
política de vazio/espaços não foi antecipada e permanece reservada a
`INT-P2-004`. Teste focado: 4/4; regressão backend: 33/33; `git diff --check`
aprovado.

---

## INT-P2-002 — Isolar sessões de clientes web

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Dependência:** INT-P1-003 + INT-P2-001

### Ações

- [x] Substituir fallback global `default` pela estratégia aprovada.
- [x] Preservar IDs válidos enviados pelo cliente.
- [x] Adicionar testes para duas sessões independentes.
- [x] Adicionar teste de continuidade da mesma sessão.
- [x] Manter alteração localizada na camada de sessão/API.

### Critério de aceite

- contexto de um cliente não é reutilizado por outro cliente sem ID compartilhado explicitamente.

**Evidência:** `api.py` gera UUID v4 para omissão, `null`, vazio ou apenas
espaços, preserva IDs explícitos normalizados e mantém `_SESSIONS` em memória.
Os testes HTTP comprovam IDs e contextos distintos, continuidade do
`processo_ativo`, preservação de ID explícito e contexto vazio sob o mesmo ID
após perda do estado. Teste focado: 7/7; regressão backend: 36/36;
`git diff --check` aprovado.

---

## INT-P2-003 — Definir endpoint de saúde mínimo

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Obrigatoriedade:** recomendado para integração saudável; pode ser adiado formalmente

### Ações

- [x] Criar `GET /api/health` ou equivalente mínimo.
- [x] Não transformar healthcheck em diagnóstico pesado de Ollama/Qdrant a cada chamada.
- [x] Retornar apenas estado técnico seguro necessário para disponibilidade da API.
- [x] Testar resposta.

### Critério de aceite

- frontend pode distinguir “interface carregou” de “API está acessível”.

**Evidência:** `GET /api/health` responde `200` com `{"status":"ok"}` pela
aplicação FastAPI real. A rota não acessa sessões, banco, Ollama, Qdrant,
RAG, agentes ou orquestradores. O teste HTTP confirma o payload e `_SESSIONS`
inalterado. Teste focado: 8/8; regressão backend: 37/37; semântica limitada à
disponibilidade da API documentada em `docs/integration.md`.

---

## INT-P2-004 — Revisar validação de request e códigos HTTP

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Definir comportamento para `mensagem` vazia/só espaços.
- [x] Definir tamanho máximo razoável ou registrar decisão de não limitar no MVP.
- [x] Confirmar semântica de 4xx vs. resposta controlada 200.
- [x] Evitar converter falha técnica inesperada em sucesso silencioso.

### Critério de aceite

- contrato de entrada possui limites e erros compreensíveis.

**Evidência:** o schema Pydantic rejeita `mensagem` ausente, `null`, vazia ou
somente whitespace com `422`, sem chamar o orquestrador ou normalizar conteúdo
válido. Não há limite adicional no MVP por ausência de fundamento objetivo para
um valor; o risco foi documentado. Testes HTTP confirmam resultado funcional
`missing_number` e falha controlada em `200`, além de exceção inesperada em
`500` sem exposição do marcador sintético. Teste focado: 14/14; regressão
backend: 43/43; `git diff --check` aprovado.

---

## INT-P2-005 — CORS somente se a topologia exigir

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Se proxy/mesma origem resolver desenvolvimento e produção, não adicionar CORS por ritual.
- [x] Se necessário, adicionar `CORSMiddleware` com origens explícitas por configuração.
- [x] Não liberar credenciais/origens indiscriminadamente.
- [x] Testar origem permitida e não permitida quando aplicável.

### Critério de aceite

- política de origem coincide com a arquitetura aprovada.

**Evidência:** desenvolvimento aprovado usa `/api/*` relativo com proxy Angular
previsto em `INT-P5-001`, e produção prefere uma origem pública única. Não há
origem cross-origin concreta nem infraestrutura de produção definida; por isso,
nenhum `CORSMiddleware`, wildcard, credencial ou origem fictícia foi adicionado.
Se um deployment futuro separar frontend e API, CORS deverá ser implementado
antes dele com allowlist configurável e superfície mínima. Regressão backend:
43/43; código funcional e itens P3 permaneceram inalterados.

---

# FASE P3 — Adaptação do frontend ao contrato real

## INT-P3-001 — Criar DTOs TypeScript do contrato HTTP

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Criar interface para request do chat.
- [x] Criar interface para envelope HTTP de response.
- [x] Criar interface para `ProcessualChatResponse`.
- [x] Tipar `fontes` com o mínimo público conhecido ou tipo seguro explícito.
- [x] Eliminar `Observable<any>` do `ChatService`.

### Critério de aceite

- TypeScript detecta incompatibilidades básicas do contrato em compilação.

**Evidência:** `core/types/processual-chat.types.ts` representa request, resultado
e envelope do contrato v1 com nulabilidade explícita, discriminador
`'processual_chat'` e `fontes` como `ReadonlyArray<unknown>`, sem congelar sua
estrutura interna. O `ChatService` retorna
`Observable<ProcessualChatHttpResponse>` e tipa o `HttpClient`, preservando
endpoint, body e timeout transitórios. `tsconfig.app` e build aprovados; o
`tsconfig.spec` mantém somente os quatro imports preexistentes reservados a
`INT-P4-001`, sem erro novo do DTO ou service; `git diff --check` aprovado.

---

## INT-P3-002 — Implementar armazenamento do `session_id`

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Dependência:** INT-P1-003 / INT-P2-002

### Ações

- [x] Criar responsabilidade clara para ler/gravar sessão.
- [x] Preferir `sessionStorage` conforme estratégia aprovada.
- [x] Não misturar `session_id` com histórico de processos.
- [x] Primeira chamada pode omitir ID; chamadas seguintes reutilizam o retornado.
- [x] Definir limpeza/reset de conversa.

### Critério de aceite

- duas mensagens consecutivas do mesmo usuário usam a mesma sessão retornada pela API.

**Evidência:** `ChatSessionService`, em `core/services/chat-session.ts`, mantém o
identificador opaco sob a chave específica `processual_chat_session_id` usando
exclusivamente `sessionStorage`. A API `getSessionId`, `setSessionId` e
`clearSession` cobre ausência, persistência e reset local sem tocar no histórico
mantido pelo `LocalStorageService`. Typecheck da aplicação e build aprovados; as
specs mantêm somente os quatro imports preexistentes de `INT-P4-001`. O mecanismo
de persistência está validado; o envio e a captura HTTP permanecem deliberadamente
reservados a `INT-P3-003` e `INT-P3-004`.

---

## INT-P3-003 — Alinhar `ChatService` ao endpoint real

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Alterar `/api/chat` para `/api/processos/chat`.
- [x] Enviar `{ session_id, mensagem }` conforme contrato.
- [x] Retornar observable tipado.
- [x] Aplicar timeout conforme política P1.
- [x] Não adicionar regra de negócio ao service.

### Critério de aceite

- request Angular corresponde exatamente ao contrato FastAPI.

**Evidência:** `ChatService` usa `POST /api/processos/chat`, constrói
`ProcessualChatRequest` com `mensagem` e omite `session_id` somente quando o
`ChatSessionService` retorna `null`; quando presente, o identificador é enviado
sem alteração. O retorno permanece `Observable<ProcessualChatHttpResponse>` e o
timeout cliente está centralizado em `PROCESSUAL_CHAT_TIMEOUT_MS = 135_000`.
Typecheck da aplicação e build aprovados; as specs mantêm apenas os quatro erros
de import baseline. O backend não possui o orçamento total de 120 s previsto em
P1, lacuna cross-phase registrada sem alteração de backend. Component, response,
mock e itens posteriores permaneceram inalterados; `git diff --check` aprovado.

---

## INT-P3-004 — Remover mock do caminho de sucesso

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Em `next`, consumir `response.resultado.resposta`.
- [x] Registrar `response.session_id`.
- [ ] Atualizar `processo_ativo`/histórico quando disponível.
- [x] Em `error`, não chamar `responderMock()`.
- [x] Garantir `carregando=false` em sucesso e erro.
- [x] Evitar duplicação de finalização de estado.

### Critério de aceite

- a mensagem mostrada no chat vem efetivamente do backend no caminho de sucesso.

**Evidência:** o `ChatComponent` registra imediatamente o `session_id` recebido
por meio do `ChatSessionService`, adiciona a mensagem do bot usando exclusivamente
`response.resultado.resposta` e encerra o loading uma única vez com `finalize`,
tanto no sucesso quanto no erro. O `responderMock` e todas as suas chamadas foram
removidos; erro HTTP não cria mensagem falsa. Respostas contratuais 2xx continuam
no `next` sem classificação por `failed_stage` ou `rag_status`. A atualização de
`processo_ativo`/histórico permanece deliberadamente pendente para `INT-P3-006`,
conforme a fronteira específica deste item. Typecheck da aplicação e build
aprovados; as specs mantêm somente os quatro imports baseline; `git diff --check`
aprovado.

---

## INT-P3-005 — Implementar apresentação de erro real

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Usar `StateService.erro` ou estrutura equivalente.
- [x] Mostrar erro de rede/timeout de forma segura e recuperável.
- [x] Manter resposta controlada do backend como mensagem normal quando o contrato assim definir.
- [x] Não mostrar stack trace ou objeto HTTP bruto.
- [x] Permitir nova tentativa após falha.

### Critério de aceite

- falha não produz resposta mockada falsa e não deixa interface permanentemente em loading.

**Evidência:** `ChatComponent` classifica `TimeoutError`, transporte
(`HttpErrorResponse.status === 0`), HTTP `4xx` e demais falhas técnicas sem
renderizar detalhes do erro. As quatro mensagens públicas seguem literalmente
`docs/integration.md` e são apresentadas por `StateService.erro` em alerta com
`role="alert"`, separado das mensagens do bot. Uma nova tentativa limpa o erro
anterior; o único `finalize` existente encerra o loading em sucesso e falha. Não
há mock, retry automático ou limpeza de sessão. Respostas `2xx`, inclusive
falha controlada e degradação, permanecem no `next` e exibem somente
`resultado.resposta`. Typecheck da aplicação e build aprovados; specs mantêm
somente os quatro imports baseline; `git diff --check` aprovado.

---

## INT-P3-006 — Corrigir histórico de processos consultados

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Problema observado

A pergunta inteira é gravada atualmente como `numero_processo`.

### Ações

- [x] Usar `resultado.processo_ativo` como fonte primária do número.
- [x] Não adicionar histórico quando não houver processo ativo identificável, salvo regra explícita.
- [x] Definir deduplicação/ordenação de consultas se necessário.
- [x] Preservar limite atual de 3 itens ou alterar somente mediante decisão de produto.

### Critério de aceite

- perguntas como “qual foi a última movimentação?” não aparecem como número processual no histórico.

**Evidência:** o `ChatComponent` atualiza o histórico somente no `next` de
uma resposta HTTP contratual e usa exclusivamente
`response.resultado.processo_ativo`, ignorando `null`, vazio e whitespace. O
`LocalStorageService` preserva o modelo existente, remove a entrada anterior do
mesmo processo, insere a consulta renovada no início e mantém no máximo três
itens. Erro e timeout não possuem caminho de gravação; pergunta e `session_id`
não entram no item. Typecheck da aplicação e build aprovados; specs mantêm
somente os quatro imports baseline; `git diff --check` aprovado.

---

## INT-P3-007 — Tornar indicador de disponibilidade verdadeiro

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Dependência:** INT-P2-003 se healthcheck for adotado

### Ações

- [x] Remover interpretação estática de “Sistema disponível”.
- [x] Consultar healthcheck no momento apropriado ou usar estado mais neutro.
- [x] Definir estados: verificando / disponível / indisponível.
- [x] Não bloquear o carregamento inteiro da interface por diagnóstico externo pesado.

### Critério de aceite

- indicador visual corresponde a uma evidência técnica real ou deixa explícito que não é um healthcheck.

**Evidência:** `ApiHealthService` executa uma única chamada tipada a
`GET /api/health` durante a inicialização do `ChatComponent`. O estado local
começa em `verificando`, muda para `disponivel` somente quando o payload possui
`status === 'ok'` e assume `indisponivel` em erro ou payload incompatível. O
cabeçalho preserva o layout e comunica textualmente “Verificando API...”, “API
disponível” ou “API indisponível”, sem bloquear a UI nem reutilizar loading,
erro, sessão ou histórico do chat. Typecheck e build aprovados; specs mantêm
somente os quatro imports baseline; `git diff --check` aprovado.

---

## INT-P3-008 — Corrigir idioma/metadados mínimos da aplicação

**Status inicial:** `TODO`  
**Status atual:** `VALIDATED`
**Prioridade:** alinhamento, não bloqueante para contrato

### Ações

- [x] Alterar `<html lang="en">` para `pt-BR`.
- [x] Substituir título genérico `MeuPrimeiroApp` por nome aprovado ou título provisório do projeto.
- [x] Remover/ajustar `My first Angular JS Project` se não tiver função real.
- [x] Evitar renomear workspace/package inteiro nesta etapa sem necessidade.

### Critério de aceite

- metadados visíveis não contradizem a finalidade real do sistema.

**Evidência:** `src/index.html` declara `lang="pt-BR"` e usa o título funcional
`Chatbot Processual`, nomenclatura já adotada pela checklist de integração e pelo
backend. O `signal` sem consumidores que continha `My first Angular JS Project`
foi removido do componente raiz. O HTML gerado preserva idioma e título;
workspace, package, diretórios, selectors, favicon, manifestos, specs e backend
permanecem inalterados. Typecheck da aplicação e build aprovados; as specs mantêm
somente os quatro imports baseline de `INT-P4-001`; `git diff --check` aprovado.

---

# FASE P4 — Testes do frontend e contrato

## INT-P4-001 — Reparar testes preexistentes do frontend

**Status inicial:** `READY`
**Status atual:** `VALIDATED`

### Falhas observadas

- specs importam classes que não existem mais (`Chat`, `LocalStorage`, `State`);
- spec do componente importa `Chat` em vez de `ChatComponent`;
- `app.spec.ts` espera a tela padrão antiga do Angular.

### Ações

- [x] Atualizar imports/classes sem mascarar comportamento.
- [x] Remover ou reescrever expectativa obsoleta do título conforme interface atual.
- [x] Confirmar compilação de `tsconfig.spec.json`.
- [x] Executar testes reais após `npm ci`.

### Critério de aceite

- testes existentes compilam e representam o código atual.

**Evidência:** as cinco specs desatualizadas agora usam `ChatService`,
`StateService`, `LocalStorageService` e `ChatComponent`; o smoke do componente
possui apenas providers mínimos e um stub restaurável de `scrollIntoView` para o
DOM de teste. `app.spec.ts` verifica a responsabilidade atual do componente raiz
de hospedar o `router-outlet`, sem expectativa do scaffold antigo. Após
`npm ci`, os typechecks da aplicação e das specs passaram, e o runner executou
6 arquivos/7 testes com 7 aprovados. O build passou com o warning CSS
preexistente; manifests permaneceram intactos e `git diff --check` foi aprovado.
Nenhuma cobertura de `INT-P4-002` ou `INT-P4-003` foi antecipada.

---

## INT-P4-002 — Testar `ChatService` como fronteira HTTP

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Cobertura mínima

- [x] método correto `POST`;
- [x] URL `/api/processos/chat`;
- [x] body contém `mensagem` e sessão conforme estado;
- [x] response é interpretada com DTO correto;
- [x] timeout/erro segue política aprovada.

### Critério de aceite

- regressão de endpoint/body é detectada sem depender de E2E.

**Evidência:** `core/services/chat.spec.ts` usa `provideHttpClient`,
`provideHttpClientTesting` e `HttpTestingController` com stub determinístico do
`ChatSessionService`. Cinco testes cobrem POST e URL relativa, payload exato com
e sem `session_id`, envelope tipado como `ProcessualChatHttpResponse`, timeout
de 135 s por timers virtuais do Vitest com `TimeoutError` e cancelamento da
request, além da propagação de `HttpErrorResponse` 500 sem fallback. Typechecks
app/spec, spec focada (5/5), suíte completa (11/11), build e
`git diff --check` passaram; somente a spec, checklist e controle foram alterados
por este item, sem mudança de produção, backend, proxy ou manifests.

---

## INT-P4-003 — Testar comportamento do `ChatComponent`

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Cobertura mínima

- [x] envia mensagem do usuário;
- [x] bloqueia envio duplicado enquanto carrega;
- [x] renderiza resposta real recebida;
- [x] finaliza loading no sucesso;
- [x] finaliza loading no erro;
- [x] apresenta erro seguro;
- [x] salva processo ativo correto no histórico;
- [x] não salva pergunta livre como processo.

### Critério de aceite

- componente possui testes para sucesso e falha sem depender do backend real.

**Evidência:** `features/chat/chat.spec.ts` usa `StateService` real e doubles
tipados de `ChatService`, `ChatSessionService`, `LocalStorageService` e
`ApiHealthService`, sem HTTP real. Nove testes cobrem envio e bloqueio durante
Observable pendente, resposta real no estado e DOM, sessão, loading no sucesso e
erro, quatro classes de erro com mensagens públicas seguras, nova tentativa sem
retry automático, histórico derivado de `processo_ativo`, processo ausente e
falha controlada 2xx. Typechecks app/spec, spec focada (9/9), suíte completa
(19/19), build e `git diff --check` passaram; produção, backend, proxy e
manifests permaneceram intactos.

---

## INT-P4-004 — Adicionar smoke test integrado da conversa

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Cenário obrigatório

1. subir FastAPI;
2. subir Angular com proxy/configuração aprovada;
3. consultar processo conhecido da fixture/base local;
4. confirmar resposta na interface;
5. enviar segunda pergunta sem repetir o número;
6. confirmar que o processo ativo foi preservado;
7. confirmar histórico correto;
8. confirmar ausência de erro no console/rede relevante.

### Critério de aceite

- fluxo completo navegador → FastAPI → orquestrador → resposta → navegador funciona em duas mensagens encadeadas.

**Evidência:** em 25/08/2026, FastAPI e Angular reais foram iniciados nas
portas aprovadas; `GET /api/health` direto e pelo proxy retornaram `200`. Um
Microsoft Edge real, automatizado em modo headless pelo Playwright já disponível
no ambiente, consultou a fixture sintética `0011000-82.1981.5.18.0051` e depois
perguntou “Qual foi a última movimentação?” sem repetir o número. Os dois
`POST /api/processos/chat` retornaram `200`, sem `failed_stage` e com
`rag_status=not_needed`; a segunda request reutilizou a sessão criada na primeira
e as duas respostas preservaram o mesmo `session_id` e `processo_ativo`. O
`sessionStorage`, as mensagens exibidas e o histórico foram confirmados em
runtime; o histórico permaneceu com um único item do processo, sem a pergunta
livre. Loading iniciou e encerrou nas duas chamadas. Console, warnings, falhas de
request e erros visuais permaneceram vazios. Regressões: backend 43/43, frontend
19/19, ambos os typechecks e build aprovados; somente o warning CSS preexistente
foi observado. Nenhum mock, dependência nova ou código funcional foi introduzido.

---

## INT-P4-005 — Testar cenários de degradação

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Cenários

- [x] backend indisponível;
- [x] timeout;
- [x] processo inexistente/entrada sem contexto suficiente;
- [x] `rag_status=unavailable` sem derrubar o chat estruturado;
- [x] falha controlada com `failed_stage`;
- [x] refresh da página conforme política de sessão;
- [x] nova sessão/nova aba conforme política aprovada.

### Critério de aceite

- falhas previsíveis não geram estado falso, mock ou travamento permanente.

**Evidência:** Edge real headless com Playwright e os serviços temporários
Angular/FastAPI comprovou backend indisponível e recuperável, contexto ausente,
`rag_status=unavailable`, refresh e nova aba independente sem `opener`. A sessão
foi preservada em erro e reload, um novo ID foi criado na aba independente, e o
histórico compartilhado por `localStorage` permaneceu distinto do estado da
sessão. Os testes existentes de service/component comprovaram o timeout real de
135 s com tempo virtual, copy segura e recuperabilidade; testes FastAPI e do
componente comprovaram `failed_stage` 2xx sem vazamento. Baseline: backend 43/43,
frontend 19/19, ambos os typechecks e build aprovados. Nenhum código de produção,
spec, proxy ou manifest foi alterado; `git diff --check` aprovado.

---

# FASE P5 — Desenvolvimento local e reprodutibilidade

## INT-P5-001 — Configurar proxy de desenvolvimento Angular

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Criar configuração de proxy versionada para `/api` → FastAPI local, se estratégia P1 aprovada.
- [x] Integrar ao comando `npm start` ou documentar comando explícito.
- [x] Não codificar URL local em componentes.
- [x] Confirmar que chamadas `/api/...` funcionam via navegador.

### Critério de aceite

- desenvolvedor consegue subir front e back localmente sem editar código-fonte para trocar URL.

**Evidência:** `frontend/proxy.conf.json` encaminha `/api` para
`http://localhost:8000` sem reescrever o path, e o target `serve` de
`frontend/angular.json` referencia essa configuração; portanto, o `npm start`
existente (`ng serve`) usa o proxy sem argumento manual. Com processos temporários,
`GET http://localhost:8000/api/health` e
`GET http://localhost:4200/api/health` retornaram `200` e `{"status":"ok"}`;
os processos foram encerrados e as portas ficaram livres. URLs relativas dos
services, backend, CORS, produção, manifests e lockfile permaneceram intactos.
JSON/configuração Angular, typechecks app/spec, 19/19 testes, build e
`git diff --check` passaram; o warning CSS preexistente permaneceu.

---

## INT-P5-002 — Documentar bootstrap limpo do frontend

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] `cd frontend`.
- [x] versão recomendada de Node/npm documentada a partir do projeto real.
- [x] `npm ci` como instalação reproduzível.
- [x] `npm start`.
- [x] `npm run build`.
- [x] comando de testes.
- [x] explicar que `node_modules` e `.angular/cache` não devem ser transferidos/versionados.

### Critério de aceite

- novo desenvolvedor consegue reconstruir dependências a partir de `package-lock.json`.

**Evidência:** `frontend/README.md` registra o fluxo `npm ci` → `npm start` →
testes sem watch → build, Node.js 24.x/npm 11.x como recomendação e as versões
observadas Node.js 24.19.0/npm 11.17.0. Após reconstruir 468 pacotes pelo
lockfile, os hashes de `package.json` e `package-lock.json` permaneceram
inalterados; typechecks app/spec, 6 arquivos/19 testes, build e acesso HTTP 200
ao Angular em `localhost:4200` passaram. O proxy `/api` validado em P5-001 foi
preservado. `node_modules` e `.angular/cache` estão ignorados, não rastreados e
documentados como artefatos locais que não devem ser transportados/versionados.

---

## INT-P5-003 — Documentar bootstrap limpo do backend

**Status inicial:** `TODO`
**Status atual:** `IMPLEMENTED`

### Ações

- [x] `cd chatbot_processual_ai`.
- [x] criar/ativar venv.
- [x] instalar `requirements.txt`.
- [x] copiar `.env.example` para `.env` local.
- [x] documentar Ollama/Qdrant opcionais/necessários por cenário.
- [x] `uvicorn api:app --reload`.
- [x] comando oficial de testes a partir do diretório correto.

### Critério de aceite

- instrução reproduz exatamente a premissa dos imports atuais.

**Evidência:** `chatbot_processual_ai/README.md` documenta o diretório
operacional, Python 3.12.10 observado, reconstrução e ativação do venv,
`requirements.txt`, configuração local, matriz factual de Ollama/Qdrant,
Uvicorn, healthcheck e testes. Em venv limpo, a instalação declarada concluiu,
FastAPI iniciou e `GET /api/health` retornou HTTP 200 com `{"status":"ok"}`.
A suíte existente passou com 43/43 no venv anterior, a partir do diretório
correto, e falhou na coleta a partir da raiz, preservando a premissa dos imports.
O item permanece `IMPLEMENTED`, não `VALIDATED`: `requirements.txt` não declara
`pytest`, e o venv limpo falhou no comando oficial com `No module named pytest`.
Nenhum pacote extra foi instalado para mascarar a lacuna.

---

## INT-P5-004 — Definir comando/workflow integrado de desenvolvimento

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] Documentar ordem para subir dependências externas, backend e frontend.
- [x] Se útil, criar script não destrutivo para desenvolvimento local; não é obrigatório.
- [x] Evitar adicionar Docker/Compose apenas por estética se não houver necessidade real nesta fase.

### Critério de aceite

- fluxo de execução completo cabe em uma seção curta e verificável da documentação.

**Evidência:** `docs/integration.md` consolida a rotina posterior ao bootstrap em
sete passos: dependências condicionais, FastAPI, health direto, Angular, health
pelo proxy, browser/chat e encerramento. O workflow real iniciou o backend com
`python -m uvicorn api:app --reload` e o frontend com `npm start`; os dois
healthchecks retornaram `200` com `{"status":"ok"}` e a página Angular retornou
`200`. Ollama e Qdrant não foram iniciados para esse smoke. Nenhum script,
dependência, container, manifest ou código de produção foi alterado.

---

# FASE P6 — Documentação como fonte de contexto

## INT-P6-001 — Atualizar `docs/ARCHITECTURE.md`

**Status inicial:** `TODO`

**Status atual:** `VALIDATED`

### Ações

- [x] adicionar frontend Angular à visão arquitetural;
- [x] registrar fronteira HTTP;
- [x] registrar sessão web;
- [x] registrar estratégia de rede/proxy;
- [x] preservar separação entre chat processual, simulador e fluxo híbrido;
- [x] atualizar pendência “Frontend visual” porque o frontend agora existe.

### Critério de aceite

- arquitetura documentada corresponde ao repositório depois da integração.

**Evidência:** `docs/ARCHITECTURE.md` foi reconciliado com Angular, FastAPI,
`POST /api/processos/chat`, health mínimo, sessão UUID em memória, proxy local,
produção preferencialmente same-origin, RAG condicional e fronteiras de metas.

---

## INT-P6-002 — Preencher `docs/development.md`

**Status inicial:** `READY`

**Status atual:** `VALIDATED`

### Conteúdo mínimo

- [x] requisitos locais;
- [x] instalação limpa frontend/backend;
- [x] comandos de execução;
- [x] comandos de testes/build/typecheck;
- [x] proxy/CORS;
- [x] variáveis de ambiente;
- [x] convenção de branches/commits relevante;
- [x] itens que não devem ser versionados;
- [x] troubleshooting mínimo.

### Critério de aceite

- documento é suficiente para onboarding técnico básico.

**Evidência:** `docs/development.md` consolida o workflow validado em P5 e
preserva explicitamente a lacuna de `pytest` em `requirements.txt`.

---

## INT-P6-003 — Preencher `docs/orchestration.md`

**Status inicial:** `READY`

**Status atual:** `VALIDATED`

### Conteúdo mínimo

- [x] fluxo Browser → API → orquestrador → agentes → resposta;
- [x] responsabilidades de cada camada;
- [x] fluxo de sessão/processo ativo;
- [x] comportamento em falha controlada;
- [x] papel do RAG sem acoplar frontend;
- [x] fronteiras entre chat processual, metas e híbrido.

### Critério de aceite

- agente/humano entende o fluxo sem inferir a partir de dezenas de arquivos.

**Evidência:** `docs/orchestration.md` descreve sequência, responsabilidades,
sessão, processo ativo, falha controlada, RAG e fronteiras de domínio.

---

## INT-P6-004 — Preencher `docs/design_philosophy.md`

**Status inicial:** `READY`

**Status atual:** `VALIDATED`

### Conteúdo mínimo

- [x] determinismo antes de LLM onde houver regra verificável;
- [x] LLM explica, não inventa regra de negócio;
- [x] frontend apresenta estado real, não sucesso aparente;
- [x] falha explícita > fallback silencioso;
- [x] contratos claros > acoplamento entre camadas;
- [x] mudanças pequenas, reversíveis e testáveis;
- [x] dados sensíveis e detalhes internos não vazam para UI.

### Critério de aceite

- decisões de projeto recorrentes têm princípios explícitos.

**Evidência:** `docs/design_philosophy.md` relaciona cada princípio obrigatório
com contratos, estado, degradação, privacidade e limitações reais do projeto.

---

## INT-P6-005 — Reconciliar README raiz com a implementação atual

**Status inicial:** `TODO`

**Status atual:** `VALIDATED`

### Ações

- [x] substituir recomendações históricas que pareçam arquitetura vigente quando já não são;
- [x] apresentar estrutura atual do repositório;
- [x] apontar `docs/` como fonte técnica aprofundada;
- [x] explicar brevemente frontend Angular + backend FastAPI;
- [x] não prometer Playwright/LangGraph/Streamlit como já implementados.

### Critério de aceite

- README não induz humano ou agente a uma arquitetura diferente da real.

**Evidência:** `README.md` agora é uma porta de entrada curta para a topologia
Angular–FastAPI atual, separa metas e aponta às fontes detalhadas.

---

## INT-P6-006 — Atualizar README do frontend

**Status inicial:** `TODO`

**Status atual:** `VALIDATED`

### Ações

- [x] remover caráter puramente template do Angular CLI;
- [x] explicar finalidade do frontend;
- [x] documentar API/proxy;
- [x] documentar instalação, build e testes;
- [x] registrar política de sessão relevante ao frontend.

### Critério de aceite

- README do frontend serve ao projeto, não apenas ao template Angular.

**Evidência:** `frontend/README.md` documenta finalidade, endpoint/proxy,
bootstrap, validações, sessão, histórico, health e erros específicos do projeto.

---

# FASE P7 — Regressão, segurança e fechamento

## INT-P7-001 — Executar regressão backend

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] executar testes focados da API/sessão;
- [x] executar suite completa existente;
- [x] comparar com baseline;
- [x] investigar qualquer falha nova.

### Critério de aceite

- nenhuma regressão backend não explicada.

**Evidência P7:** Python 3.12.10/pytest 9.1.1 no venv existente. A spec
`tests/test_api_processual_chat.py` passou com 14/14 e a suíte oficial
`python -m pytest tests -q`, executada dentro de `chatbot_processual_ai/`,
passou com 43/43 em 2,61 s. A contagem coincide com a baseline final registrada;
permaneceu somente o `PytestCacheWarning` ambiental já conhecido.

---

## INT-P7-002 — Executar regressão frontend

**Status inicial:** `TODO`
**Status atual:** `BLOCKED`

### Ações

- [ ] ambiente reconstruído com `npm ci`;
- [ ] typecheck aplicação;
- [ ] typecheck/testes specs;
- [ ] `npm test -- --watch=false`;
- [ ] `npm run build`;
- [ ] revisar warnings relevantes.

### Critério de aceite

- build e testes acordados passam em ambiente limpo.

**Evidência P7:** Node 24.19.0/npm 11.17.0 foram localizados no runtime LTS já
instalado, mas `npm ci` falhou dentro e fora do sandbox com `EPERM` ao tentar
substituir binários nativos em `node_modules`. Dois processos Node preexistentes
estavam ativos e não foram encerrados pelo gate. A tentativa parcial removeu o
TypeScript instalado, portanto app/spec, runner e build não puderam ser
reexecutados com integridade. `package.json` e `package-lock.json` conservaram
os hashes registrados e não foram modificados.

---

## INT-P7-003 — Revisar segurança da fronteira

**Status inicial:** `TODO`
**Status atual:** `VALIDATED`

### Ações

- [x] nenhum `.env` real no diff;
- [x] nenhum token/credencial no frontend;
- [x] nenhum path local/ID interno exposto em response pública;
- [x] CORS restrito se usado;
- [x] `session_id` não contém dado sensível;
- [x] erros não exibem stack traces;
- [x] fontes RAG permanecem sanitizadas conforme contrato.

### Critério de aceite

- revisão de segurança concluída sem vazamento conhecido.

**Evidência P7:** buscas dirigidas no conteúdo rastreado e inspeção de API,
sessão, orquestrador, RAG e frontend não localizaram segredo real ou credencial
embutida. `.env` não é rastreado; `.env.example` contém somente nomes/defaults
de configuração. A topologia same-origin usa proxy e não habilita CORS. IDs
novos são UUIDs opacos, não autenticação. Exceções são convertidas em resposta
segura e testadas contra token, traceback e paths; fontes públicas contêm apenas
tipo, título, data e tipo de conteúdo.

---

## INT-P7-004 — Revisar diff e higiene final

**Status inicial:** `TODO`
**Status atual:** `IMPLEMENTED`

### Ações

- [ ] `git diff --check`;
- [ ] revisar diff completo;
- [ ] procurar debug/log temporário;
- [ ] procurar alteração fora do escopo;
- [ ] confirmar que `node_modules`, `.angular`, `__pycache__`, bancos e `.env` não entraram;
- [ ] confirmar docs coerentes com implementação;
- [ ] confirmar que arquivos do simulador não mudaram sem necessidade.

### Critério de aceite

- diff é focado, legível e reversível.

**Evidência P7:** merge-base factual `cce4751` (`main`/`origin/main`), diff da
branch e histórico foram revisados; `git diff --check` passou, nenhum arquivo de
`simulador-de-metas/` mudou e nenhum artefato local foi rastreado. A validação
final ficou pendente porque o worktree já continha uma mudança não explicada em
`frontend/angular.json`, adicionando um identificador de analytics do Angular.
O gate não a removeu nem a atribuiu silenciosamente.

---

## INT-P7-005 — Smoke integrado final

**Status inicial:** `TODO`
**Status atual:** `BLOCKED`

### Cenário mínimo de aceite

- [ ] backend sobe do zero;
- [ ] frontend sobe do zero;
- [ ] UI detecta/representa disponibilidade conforme decisão;
- [ ] consulta processo válido;
- [ ] exibe resposta real;
- [ ] exibe processo correto no histórico;
- [ ] pergunta contextual seguinte funciona sem repetir número;
- [ ] sessão de segundo cliente é isolada;
- [ ] backend indisponível produz erro recuperável;
- [ ] nenhum erro crítico no console/rede.

### Critério de aceite

- integração é funcional do ponto de vista do usuário e da arquitetura.

**Evidência P7:** serviços preexistentes responderam `200` no health direto e
via proxy, e a página Angular respondeu `200`, mas não foram iniciados por este
gate. O `npm ci` bloqueado impediu reconstruir/subir o frontend do estado atual;
o backend preexistente também não podia ser controladamente desligado para o
cenário offline. As evidências manuais e os smokes P4/P5 permanecem apenas
suplementares e não substituem a reprodução final exigida.

---

## INT-P7-006 — Gate de prontidão para merge

**Status inicial:** `TODO`
**Status atual:** `BLOCKED`

A branch só pode ser declarada **READY_FOR_MERGE** quando:

- [ ] todos os itens bloqueantes estão `VALIDATED`;
- [ ] itens adiados possuem justificativa e risco residual registrados;
- [ ] testes backend aprovados;
- [ ] testes frontend aprovados;
- [ ] build frontend aprovado;
- [ ] smoke integrado aprovado;
- [ ] diff revisado;
- [ ] `git diff --check` limpo;
- [ ] documentação atualizada;
- [ ] nenhum segredo/artefato local incluído;
- [ ] commits representam unidades lógicas compreensíveis;
- [ ] controle de progresso contém hashes reais dos commits efetuados.

**Saída permitida:** `READY_FOR_MERGE` ou `NOT_READY` com justificativa objetiva.

**Resultado P7:** `NOT_READY`. Bloqueiam o gate: regressão frontend não
reproduzida após `npm ci`; smoke final não reproduzido; alteração não explicada
no worktree; inconsistências documentais preexistentes (`INT-P5-003` detalhado
como `IMPLEMENTED` e G1–G4 ainda `TODO` no controle macro); e ausência do
checkpoint final P7, que este prompt não autoriza criar.

---

# 3. Sequência recomendada

```text
P0 Baseline/Governança
        ↓
P1 Contrato/Decisões
        ↓
P2 Fronteira Backend
        ↓
P3 Adaptação Frontend
        ↓
P4 Testes de contrato/componente
        ↓
P5 Execução local reproduzível
        ↓
P6 Documentação alinhada
        ↓
P7 Regressão + Smoke + Merge Gate
```

Não antecipar P3 “porque é só trocar a URL”: sessão, contrato, erro e topologia devem estar decididos antes.

---

# 4. Definition of Done global

A integração não é considerada concluída quando “a tela respondeu uma vez”. Ela é concluída quando:

1. **Contrato:** request/response estão documentados e tipados.
2. **Isolamento:** sessões não vazam entre clientes.
3. **Comportamento:** frontend usa a resposta real e trata falhas corretamente.
4. **Reprodutibilidade:** projeto é reconstruível sem copiar `node_modules`.
5. **Testes:** backend, frontend e fluxo integrado possuem evidência.
6. **Documentação:** arquitetura e desenvolvimento descrevem o estado atual.
7. **Segurança:** nenhum segredo/detalhe interno indevido foi exposto.
8. **Rastreabilidade:** cada unidade lógica possui status, evidência e commit associado.
9. **Reversibilidade:** commits e diff permitem entender/reverter a integração sem desmontar o backend original.
