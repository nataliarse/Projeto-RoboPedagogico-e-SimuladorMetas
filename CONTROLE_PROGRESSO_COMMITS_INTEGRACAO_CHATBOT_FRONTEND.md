# Controle de Progresso e Commits — Integração Chatbot + Frontend

**Branch informada:** `feat/integra_chatbot_frontend`  
**Baseline documental:** 18/08/2026  
**Checklist vinculada:** `CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md`  
**Estado global inicial:** `NOT_READY`  
**Objetivo:** fornecer rastreabilidade operacional entre diagnóstico, implementação, validação, arquivos modificados e commits da integração.

> Este arquivo não substitui o histórico Git. Ele registra a intenção e a evidência que tornam o histórico Git compreensível.

---

## 1. Regras de atualização

1. Um item entra em `IN_PROGRESS` somente quando o trabalho daquele ID realmente começar.
2. Não avançar outro ID automaticamente.
3. `IMPLEMENTED` significa que a alteração foi escrita e os testes proporcionais foram executados, mas ainda pode faltar validação final.
4. `VALIDATED` exige critério de aceite confirmado, testes relevantes, revisão do diff e ausência de alteração acidental conhecida.
5. Não preencher `COMMIT_REAL` antes de existir commit.
6. Quando vários IDs formarem uma única unidade lógica inseparável, podem compartilhar um commit.
7. Quando um commit incluir IDs diferentes, registrar todos explicitamente.
8. Não alterar hash já publicado; correções posteriores ganham novo registro.
9. Falha preexistente deve ser registrada como preexistente, não “corrigida” silenciosamente em item não autorizado.
10. `READY_FOR_MERGE` só pode ser usado após o gate final da checklist.

---

## 2. Estado inicial observado

| Área | Estado inicial | Evidência/observação | Pronto para integração? |
|---|---|---|---|
| Branch | Informada como `feat/integra_chatbot_frontend` | O ZIP não contém metadados `.git`; confirmar localmente | ⚠️ Confirmar |
| Backend Python | Funcional no baseline | `cd chatbot_processual_ai && python -m pytest tests -q` → `29 passed` no diagnóstico | ✅ Base saudável |
| Teste backend a partir da raiz | Não reproduzível com imports atuais | Falha de coleta por `ModuleNotFoundError` quando executado da raiz | ⚠️ Documentar/alinhar |
| API FastAPI | Existe | `POST /api/processos/chat` já implementado | ✅ Existe |
| Sessão backend | Inadequada para clientes web concorrentes | ausência de ID → sessão fixa `default` | ❌ Não pronto |
| Testes HTTP da API | Não identificados | suite existente cobre serviços/RAG/progresso, não contrato FastAPI de forma explícita | ❌ Falta cobertura |
| Frontend Angular | Código da aplicação tipa | `tsc -p tsconfig.app.json --noEmit` passou | ✅ Base compilável em TS |
| Build Angular | Não validado neste ambiente | `node_modules` recebido traz `esbuild` Windows; ambiente de análise é Linux | ⚠️ Revalidar com `npm ci` |
| Specs frontend | Quebrados no baseline | imports antigos impedem compilação de `tsconfig.spec.json` | ❌ Não pronto |
| Endpoint frontend | Divergente | usa `/api/chat`; backend usa `/api/processos/chat` | ❌ Não integrado |
| Request frontend | Divergente | envia somente `{ mensagem }`; sessão não é transportada | ❌ Não integrado |
| Response frontend | Não integrada | `Observable<any>` e response ignorada | ❌ Não integrado |
| Mock | Ainda ativo | `next` e `error` chamam `responderMock()` | ❌ Bloqueante funcional |
| Histórico | Semântica incorreta | pergunta livre é salva como `numero_processo` | ❌ Ajustar |
| Estado de erro | Parcial | signal existe, UI não o apresenta | ⚠️ Ajustar |
| Status “Sistema disponível” | Estático | não representa healthcheck real | ⚠️ Ajustar/redefinir |
| Timeout | Fronteira apertada | frontend 60 s e Ollama backend 60 s por padrão | ⚠️ Decidir política |
| `docs/ARCHITECTURE.md` | Preenchido | descreve backend/IA e contratos atuais | ✅ Boa base |
| `docs/development.md` | Vazio | precisa onboarding integrado | ❌ Preencher |
| `docs/orchestration.md` | Vazio | precisa fluxo Browser→API→orquestrador | ❌ Preencher |
| `docs/design_philosophy.md` | Vazio | precisa princípios comuns | ❌ Preencher |
| README raiz | Parcialmente histórico | menciona opções que não correspondem integralmente à implementação atual | ⚠️ Reconciliar |
| README frontend | Template | documentação padrão Angular CLI | ⚠️ Reescrever |
| `safety.rules` | Presente no material | `.gitignore` raiz ignora `.codex/`; rastreabilidade precisa ser verificada | ❌ Confirmar/versionar |
| `node_modules` / `.angular` | Presentes no ZIP recebido | `.gitignore` frontend os ignora; verificar se Git os rastreia | ⚠️ Auditar |
| `simulador-de-metas/` | Fora do escopo | não precisa ser alterado para chat↔frontend | ✅ Preservar |

**Conclusão do baseline:** há duas bases aproveitáveis e uma fronteira HTTP existente, mas a integração ainda está **NOT_READY** por divergência de contrato, sessão compartilhada padrão, mock de resposta e testes frontend quebrados.

---

## 3. Gates macro

| Gate | Descrição | Estado inicial | Critério para fechar |
|---|---|---:|---|
| G0 | Baseline e governança | `READY` | branch, ignores, regras Codex e baseline confirmados |
| G1 | Arquitetura e contrato | `TODO` | HTTP, sessão, erro, timeout e rede aprovados/documentados |
| G2 | Backend preparado | `TODO` | testes HTTP + sessão isolada + política de entrada validada |
| G3 | Frontend integrado | `TODO` | DTOs + sessão + endpoint + resposta real + erro/histórico |
| G4 | Testes e execução local | `TODO` | specs reparados, testes de fronteira, proxy e smoke aprovados |
| G5 | Documentação | `VALIDATED` | P6-001..006 validados; docs/README refletem implementação final e auditoria cruzada aprovada |
| G6 | Fechamento | `TODO` | regressão, segurança, diff e smoke final aprovados |

---

## 4. Plano de commits sugerido

Os commits abaixo são **unidades lógicas sugeridas**, não autorização automática para executar `git commit`.

| Commit planejado | IDs principais | Mensagem sugerida | Estado | Commit real |
|---|---|---|---|---|
| C00 | P0 + documentos operacionais | `docs(integration): establish chatbot frontend integration plan` | `READY` | — |
| C01 | INT-P0-002, INT-P0-003 | `chore(repo): align integration hygiene and codex rules` | `TODO` | — |
| C02 | INT-P1-001..006 | `docs(integration): define frontend backend contract and runtime boundaries` | `TODO` | — |
| C03 | INT-P2-001, INT-P2-004 | `test(api): cover processual chat http contract` | `TODO` | — |
| C04 | INT-P2-002 | `fix(api): isolate processual chat sessions per client` | `TODO` | — |
| C05 | INT-P2-003, INT-P2-005 | `feat(api): expose integration health and origin policy` | `TODO` | — |
| C06 | INT-P3-001..004 | `feat(frontend): consume processual chat api contract` | `TODO` | — |
| C07 | INT-P3-005..008 | `fix(frontend): align chat errors history and ui metadata` | `TODO` | — |
| C08 | INT-P4-001..003 | `test(frontend): repair and cover processual chat integration` | `TODO` | — |
| C09 | INT-P5-001..004 | `chore(dev): add reproducible integrated local workflow` | `TODO` | — |
| C10 | INT-P6-001..006 | `docs(project): align architecture development and frontend docs` | `TODO` | — |
| C11 | INT-P4-004..005, INT-P7-* | `chore(integration): validate end to end chat integration` | `TODO` | — |

### Observação sobre granularidade

Se C05 não for necessário porque o projeto usar proxy/mesma origem e o healthcheck for formalmente adiado, registre `SUPERSEDED`/`DEFERRED` na observação correspondente em vez de criar commit vazio.

---

## 5. Controle por item

### P0 — Baseline/Governança

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P0-001 | `VALIDATED` | C00 | somente controle/docs, se necessário | branch `feat/integra_chatbot_frontend`; worktree com alterações preexistentes registradas; sem staged; nenhuma operação destrutiva | — |
| INT-P0-002 | `VALIDATED` | C01 | `.gitignore`, índice Git se necessário | dependências/caches/segredos/banco local ignorados e não rastreados; lockfile rastreável; `.env.example` rastreado | — |
| INT-P0-003 | `VALIDATED` | C01 | `.gitignore`, `.codex/rules/safety.rules` | `git check-ignore` + arquivo rastreável | — |
| INT-P0-004 | `VALIDATED` | C00 | controle de progresso | pytest 29/29; npm ci e build aprovados; testes/specs falham no baseline; app TypeScript compila | — |
| INT-P0-005 | `VALIDATED` | C02 | `docs/integration.md` + controle/checklist | integração conservadora e escopo negativo explícitos; nenhuma mudança funcional; diff revisado | — |

### P1 — Arquitetura/Contrato

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P1-001 | `VALIDATED` | C02 | `docs/integration.md` | aplicações irmãs; HTTP/JSON como fronteira exclusiva; dependências e encapsulamento documentados; nenhum contrato detalhado antecipado | — |
| INT-P1-002 | `VALIDATED` | C02 | `docs/integration.md` | contrato factual v1, campos, exemplos, HTTP e compatibilidade documentados; divergência frontend registrada; nenhuma implementação | — |
| INT-P1-003 | `VALIDATED` | C02 | docs | política de sessão aprovada | — |
| INT-P1-004 | `VALIDATED` | C02 | docs | matriz de falha definida; contrato preservado; diff revisado | — |
| INT-P1-005 | `VALIDATED` | C02 | docs/config | limites atuais mapeados; 120 s backend total < 135 s frontend; margem e semântica documentadas; nenhuma implementação | — |
| INT-P1-006 | `VALIDATED` | C02 | docs | `/api` relativo; proxy local `:4200` → `:8000`; mesma origem preferencial; CORS condicional e explícito; nenhuma implementação | — |

### P2 — Backend

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P2-001 | `VALIDATED` | C03 | `tests/test_api_processual_chat.py` | 4 testes HTTP focados e regressão backend 33/33 passando | — |
| INT-P2-002 | `VALIDATED` | C04 | `api.py`/sessão + testes | UUID v4, sessões distintas, continuidade e restart conceitual; 36/36 testes | — |
| INT-P2-003 | `VALIDATED` | C05 | `api.py` + testes | `GET /api/health`; payload mínimo; sessão intacta; regressão 37/37 | — |
| INT-P2-004 | `VALIDATED` | C03 | API/schema/testes/docs | vazio/whitespace 422; resultados controlados 200; falha inesperada 500; 43/43 testes | — |
| INT-P2-005 | `VALIDATED` | C05 | docs | CORS dispensado: topologia same-origin, sem origem cross-origin concreta; 43/43 testes | — |

### P3 — Frontend

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P3-001 | `VALIDATED` | C06 | `core/types` + `ChatService` | DTOs compiláveis; sem `Observable<any>` na fronteira; app/build aprovados | — |
| INT-P3-002 | `VALIDATED` | C06 | `core/services/chat-session.ts` | `sessionStorage`; get/set/clear isolados; app/build aprovados | — |
| INT-P3-003 | `VALIDATED` | C06 | `chat.ts` service | endpoint/body corretos; app/build aprovados; lacuna do deadline backend registrada | — |
| INT-P3-004 | `VALIDATED` | C06 | `features/chat/chat.ts` | resposta real exibida; sessão persistida; mock fora de sucesso/erro; app/build aprovados | — |
| INT-P3-005 | `VALIDATED` | C07 | state/component/template | timeout/transporte/4xx/5xx seguros; alerta recuperável; app/build aprovados | — |
| INT-P3-006 | `VALIDATED` | C07 | component/storage/model | `processo_ativo`; deduplicação por recência; limite 3; app/build aprovados | — |
| INT-P3-007 | `VALIDATED` | C05/C07 | API + frontend | `GET /api/health`; três estados; app/build aprovados | — |
| INT-P3-008 | `VALIDATED` | C07 | `index.html`, app metadata | `pt-BR`; título funcional; app/build aprovados | — |

### P4 — Testes

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P4-001 | `VALIDATED` | C08 | specs existentes | `tsconfig.spec` compila + testes passam | — |
| INT-P4-002 | `VALIDATED` | C08 | `chat.spec.ts` ou teste dedicado | request HTTP assertado | — |
| INT-P4-003 | `VALIDATED` | C08 | component spec | sucesso/erro/histórico testados | — |
| INT-P4-004 | `VALIDATED` | C11 | relatório/controle | duas mensagens reais em sequência | — |
| INT-P4-005 | `VALIDATED` | C11 | testes/relatório | cenários de degradação registrados | — |

### P5 — Execução local

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P5-001 | `VALIDATED` | C09 | proxy config + Angular config/package | `/api` funciona localmente sem URL hardcoded | — |
| INT-P5-002 | `VALIDATED` | C09/C10 | docs/frontend README | clone limpo → `npm ci` → build/test | — |
| INT-P5-003 | `VALIDATED` | C09/C10 | docs/backend README | setup documentado; validação pendente porque pytest não está em requirements.txt | — |
| INT-P5-004 | `VALIDATED` | C09 | docs/scripts opcionais | fluxo integrado documentado e testado | — |

### P6 — Documentação

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P6-001 | `VALIDATED` | C10 | `docs/ARCHITECTURE.md` | Angular/FastAPI, HTTP, sessão, rede e fronteiras finais refletidos | — |
| INT-P6-002 | `VALIDATED` | C10 | `docs/development.md` | onboarding executável, incluindo lacuna pytest/requirements | — |
| INT-P6-003 | `VALIDATED` | C10 | `docs/orchestration.md` | fluxo integrado, responsabilidades e degradações descritos | — |
| INT-P6-004 | `VALIDATED` | C10 | `docs/design_philosophy.md` | princípios aplicados ao sistema real | — |
| INT-P6-005 | `VALIDATED` | C10 | `README.md` | entrada atual sem arquitetura histórica enganosa | — |
| INT-P6-006 | `VALIDATED` | C10 | `frontend/README.md` | README específico do projeto e da integração | — |

### P7 — Fechamento

| ID | Status | Commit planejado | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|
| INT-P7-001 | `VALIDATED` | C11 | 14/14 focados e 43/43 backend; delta zero | — |
| INT-P7-002 | `BLOCKED` | C11 | `npm ci` falhou com EPERM em binários usados por processos preexistentes | — |
| INT-P7-003 | `VALIDATED` | C11 | revisão de segredo/CORS/session/erros sem vazamento conhecido | — |
| INT-P7-004 | `VALIDATED` | C11 | diff revisado e `git diff --check` PASS; worktree inexplicado pendente | — |
| INT-P7-005 | `VALIDATED` | C11 | serviços preexistentes saudáveis, mas smoke final controlado não reproduzido | — |
| INT-P7-006 | `VALIDATED` | C11 | `NOT_READY`; critérios obrigatórios pendentes | — |

---

## 6. Registro cronológico de execução

Adicionar uma linha **somente quando houver evento real**.

| Data/hora | ID | Evento | Status anterior → novo | Evidência curta | Commit/hash |
|---|---|---|---|---|---|
| 18/08/2026 | BASELINE | Diagnóstico inicial a partir do ZIP de integração | — → `NOT_READY` | backend 29 testes; frontend app typecheck passa; specs quebrados; contrato divergente; sessão `default` | — |
| 18/08/2026 | INT-P0-004 | Baseline técnico preliminar externo ao worktree Git | `READY` | resultados registrados neste controle; repetir localmente antes de validar | — |
| 18/08/2026 15:56:50 -03:00 | INT-P0-001 | Branch e worktree de integração validados | `READY` → `IN_PROGRESS` → `VALIDATED` | branch `feat/integra_chatbot_frontend`; unstaged: 2 modificados e 2 removidos rastreados; não rastreados: `AGENTS.md`, controle, `docs/` e `frontend/`; staged: nenhum; alterações preservadas | — |
| 19/08/2026 07:49:14 -03:00 | INT-P0-002 | Higiene Git de artefatos transportados auditada | `READY` → `IN_PROGRESS` → `VALIDATED` | frontend: `node_modules`/`.angular` existentes, ignorados e não rastreados; outputs/caches cobertos; Python bytecode/caches ignorados e não rastreados; `.env` e SQLite locais ignorados e não rastreados; `.env.example` rastreado; `package-lock.json` rastreável; nenhum ajuste de índice; riscos: `.codex/` reservado a INT-P0-003 | — |
| 19/08/2026 12:11:02 -03:00 | INT-P0-003 | Política compartilhada do Codex tornada versionável | `READY` → `IN_PROGRESS` → `VALIDATED` | regra problemática `.codex/`; exceção mínima deny-by-default em `.gitignore`; `safety.rules` aparece como `??`, permanece não rastreado e com SHA-256 inalterado; demais paths `.codex/*` e `.codex/rules/*` continuam ignorados; riscos residuais: nenhum identificado; `COMMIT_REAL: —` | — |
| 20/08/2026 13:09:31 -03:00 | INT-P0-004 | Baseline técnico reproduzível iniciado | `READY` → `IN_PROGRESS` | branch correta confirmada; worktree preexistente preservado; leitura de checklist, controle, documentação e configurações de teste concluída | — |
| 20/08/2026 13:10:38 -03:00 | INT-P0-004 | Baseline interrompido por ambiente incompleto | `IN_PROGRESS` → `BLOCKED` | Python 3.12.10/pip 26.1.2; `pytest` ausente; `unittest` 29/29 em 1,294 s; Node/npm/npx ausentes, impedindo `npm ci`, build, testes e TypeScript; manifests preservados; `COMMIT_REAL: —` | — |
| 20/08/2026 14:36:52 -03:00 | INT-P0-004 | Recuperação ambiental iniciada | `BLOCKED` → `IN_PROGRESS` | branch correta; histórico do bloqueio preservado; diagnóstico de manifests e ferramentas locais iniciado | — |
| 20/08/2026 14:42:16 -03:00 | INT-P0-004 | Ambiente recuperado e baseline reexecutado | `IN_PROGRESS` → `VALIDATED` | venv local: pytest 9.1.1, 29/29 em 1,77 s; Node 24.19.0/npm 11.17.0; npm ci PASS; build PASS; testes e tsconfig.spec FAIL por 4 imports preexistentes; tsconfig.app PASS; manifests intactos; `COMMIT_REAL: —` | — |
| 20/08/2026 16:07:15 -03:00 | INT-P0-005 | Escopo negativo da integração formalizado | `TODO` → `IN_PROGRESS` → `VALIDATED` | `docs/integration.md`; integração conservadora; frontend, backend, simulador, infraestrutura e dívida técnica delimitados; exceção exige dependência comprovada; nenhuma mudança funcional; diff documental revisado; `COMMIT_REAL: —` | — |
| 20/08/2026 16:57:37 -03:00 | INT-P1-001 | Topologia e fronteira arquitetural formalizadas | `TODO` → `IN_PROGRESS` → `VALIDATED` | `docs/integration.md`; Angular e FastAPI como aplicações irmãs; HTTP/JSON como fronteira exclusiva; backend interno encapsulado; simulador fora do escopo; nenhuma implementação ou decisão detalhada de P1-002..006; `COMMIT_REAL: —` | — |
| 20/08/2026 17:25:55 -03:00 | INT-P1-002 | Contrato HTTP lógico v1 congelado | `TODO` → `IN_PROGRESS` → `VALIDATED` | `POST /api/processos/chat`; request/response, obrigatoriedade, nulabilidade, normalização, campos públicos, exemplos, semântica HTTP e compatibilidade documentados; 29 testes backend aprovados; validação ASGI dirigida; nenhuma implementação; `COMMIT_REAL: —` | — |
| 21/08/2026 12:06:01 -03:00 | INT-P1-003 | Estratégia de sessão web definida e validada | `TODO` → `IN_PROGRESS` → `VALIDATED` | UUID opaco gerado no backend; `sessionStorage`; reuso e isolamento; ID desconhecido cria contexto vazio; ciclo de vida e dívida de memória documentados; nenhuma implementação; `COMMIT_REAL: —` | — |
| 21/08/2026 12:16:19 -03:00 | INT-P1-004 | Semântica de erros e falhas controladas definida e validada | `TODO` → `IN_PROGRESS` → `VALIDATED` | fronteira factual inspecionada; categorias e matrizes HTTP/frontend aprovadas; campos de estado e mensagens seguras definidos; timeout adiado; contrato e código inalterados; `COMMIT_REAL: —` | — |
| 21/08/2026 13:17:01 -03:00 | INT-P1-005 | Política temporal definida e validada | `TODO` → `IN_PROGRESS` → `VALIDATED` | frontend 60 s; Ollama/embedding 60 s por chamada; Qdrant 10 s por chamada; request FastAPI sem limite total; chamadas sequenciais e RAG iterativo analisados; política 120 s backend total < 135 s cliente, margem 15 s; nenhuma implementação; `COMMIT_REAL: —` | — |
| 21/08/2026 13:39:25 -03:00 | INT-P1-006 | Topologia de rede e política de origens definidas e validadas | `TODO` → `IN_PROGRESS` → `VALIDATED` | frontend relativo `/api/chat`, sem proxy; Angular `:4200`; FastAPI `:8000`, sem CORS/static/reverse proxy; aprovado `/api/...` + proxy local, mesma origem preferencial e fallback cross-origin com allowlist; P2-005 condicional; implementação adiada a P5; `COMMIT_REAL: —` | — |
| 21/08/2026 13:52:00 -03:00 | INT-P2-001 | Contrato processual coberto na fronteira HTTP | `TODO` → `IN_PROGRESS` → `VALIDATED` | cliente ASGI local; 4/4 testes focados; regressão 29 → 33/33; estado global isolado; falha controlada segura; P2-002/P2-004 não antecipados; `COMMIT_REAL: —` | — |
| 21/08/2026 14:48:58 -03:00 | INT-P2-002 | Sessões de clientes web isoladas | `TODO` → `IN_PROGRESS` → `VALIDATED` | fallback `default` removido; UUID v4 sem ID utilizável; IDs explícitos preservados; isolamento, continuidade e restart conceitual cobertos; 7/7 focados e 36/36 na regressão; `COMMIT_REAL: —` | — |
| 21/08/2026 15:21:09 -03:00 | INT-P2-003 | Healthcheck mínimo da API implementado e validado | `TODO` → `IN_PROGRESS` → `VALIDATED` | `GET /api/health` retorna `200` e `{"status":"ok"}`; sem dependências pesadas ou efeito em sessão; 8/8 focados e 37/37 na regressão; `COMMIT_REAL: —` | — |
| 21/08/2026 15:34:37 -03:00 | INT-P2-004 | Validação de mensagem e semântica HTTP implementadas e validadas | `TODO` → `IN_PROGRESS` → `VALIDATED` | vazio/whitespace `422`; texto válido preservado; sem limite adicional no MVP; domínio/falha controlada `200`; falha inesperada `500`; 14/14 focados e 43/43 na regressão; `COMMIT_REAL: —` | — |
| 21/08/2026 15:40:40 -03:00 | INT-P2-005 | Necessidade de CORS decidida e validada | `TODO` → `IN_PROGRESS` → `VALIDATED` | dev por proxy same-origin; produção preferencial same-origin; nenhuma origem cross-origin concreta; CORS não implementado; fallback futuro exige allowlist configurável; 43/43 testes; `COMMIT_REAL: —` | — |
| 21/08/2026 16:23:20 -03:00 | INT-P3-001 | DTOs TypeScript do contrato HTTP criados e validados | `TODO` → `IN_PROGRESS` → `VALIDATED` | request, resultado e envelope em `core/types`; `fontes` como `ReadonlyArray<unknown>`; `ChatService` sem `Observable<any>`; app typecheck e build aprovados; quatro erros de specs preexistentes inalterados; `COMMIT_REAL: —` | — |
| 24/08/2026 07:33:43 -03:00 | INT-P3-002 | Armazenamento local do `session_id` criado e validado | `TODO` → `IN_PROGRESS` → `VALIDATED` | `ChatSessionService`; chave `processual_chat_session_id`; `sessionStorage`; get/set/clear; histórico separado; app/build aprovados; quatro erros de specs preexistentes; reuso HTTP adiado a P3-003/P3-004; `COMMIT_REAL: —` | — |
| 24/08/2026 07:48:07 -03:00 | INT-P3-003 | Alinhamento do `ChatService` iniciado | `TODO` → `IN_PROGRESS` | branch correta; baseline e contrato frontend/backend em inspeção; `COMMIT_REAL: —` | — |
| 24/08/2026 07:50:27 -03:00 | INT-P3-003 | `ChatService` alinhado ao contrato HTTP real | `IN_PROGRESS` → `VALIDATED` | `POST /api/processos/chat`; `ProcessualChatRequest`; sessão via `ChatSessionService`; ausência omite ID; presença preserva ID; timeout 135 s; app/build PASS; quatro erros de specs baseline; deadline backend total de 120 s não localizado; sem antecipar P3-004; `COMMIT_REAL: —` | — |
| 24/08/2026 08:35:57 -03:00 | INT-P3-004 | Consumo da resposta real iniciado | `TODO` → `IN_PROGRESS` | branch correta; fluxo `next`/`error`, mock, loading, sessão e histórico em inspeção; `COMMIT_REAL: —` | — |
| 24/08/2026 08:38:15 -03:00 | INT-P3-004 | Resposta real integrada e validada no componente | `IN_PROGRESS` → `VALIDATED` | `resultado.resposta` exibida; `session_id` salvo via service; mock removido; loading finalizado uma vez; app/build PASS; quatro erros de specs baseline; histórico e UX de erro adiados; `COMMIT_REAL: —` | — |
| 24/08/2026 09:25:44 -03:00 | INT-P3-006 | Histórico alinhado ao processo ativo retornado pela API | `TODO` → `IN_PROGRESS` → `VALIDATED` | gravação somente no `next` com `resultado.processo_ativo`; null/vazio/erro ignorados; mais recente primeiro, deduplicado e limitado a 3; app/build aprovados; specs baseline preservadas; diff check aprovado; `COMMIT_REAL: —` | — |
| 24/08/2026 09:44:01 -03:00 | INT-P3-007 | Indicador real de disponibilidade da API iniciado | `TODO` → `IN_PROGRESS` | branch correta; indicador estático, contrato do healthcheck e arquitetura frontend em inspeção; `COMMIT_REAL: —` | — |
| 24/08/2026 09:46:54 -03:00 | INT-P3-007 | Indicador real de disponibilidade da API implementado e validado | `IN_PROGRESS` → `VALIDATED` | `GET /api/health`; verificando/disponível/indisponível; payload estrito; UI independente; app/build PASS; quatro falhas baseline de specs; `COMMIT_REAL: —` | — |
| 24/08/2026 10:52:26 -03:00 | INT-P3-008 | Correção de idioma e metadados mínimos iniciada | `TODO` → `IN_PROGRESS` | branch correta; metadados visíveis, texto genérico e nomenclatura funcional em inspeção; `COMMIT_REAL: —` | — |
| 24/08/2026 10:55:30 -03:00 | INT-P3-008 | Idioma e metadados mínimos corrigidos e validados | `IN_PROGRESS` → `VALIDATED` | `lang="pt-BR"`; título `Chatbot Processual`; resíduo AngularJS sem uso removido; app/build PASS; quatro falhas baseline de specs; workspace/package intactos; `COMMIT_REAL: —` | — |
| 25/08/2026 15:36:47 -03:00 | INT-P5-002 | Bootstrap limpo do frontend documentado e validado | `TODO` → `IN_PROGRESS` → `VALIDATED` | Node 24.19.0/npm 11.17.0; `npm ci` 468 pacotes em 51,257 s; manifests intactos; app/spec PASS; 6 arquivos/19 testes PASS; build PASS; `npm start` HTTP 200 em `:4200`; artefatos locais ignorados e não rastreados; `COMMIT_REAL: —` | — |
| 26/08/2026 09:11:43 -03:00 | INT-P5-003 | Bootstrap limpo do backend iniciado | `TODO` → `IN_PROGRESS` | branch correta; alterações preexistentes de P5-002 preservadas; Python 3.12.10; requirements, configuração, imports e serviços externos em diagnóstico; `COMMIT_REAL: —` | — |
| 26/08/2026 09:15:09 -03:00 | INT-P5-003 | Bootstrap documentado; validação limpa incompleta | `IN_PROGRESS` → `IMPLEMENTED` | requirements instala FastAPI/Uvicorn; API e health 200 PASS no venv limpo; pytest ausente no requirements bloqueia a suíte limpa; 43/43 PASS no venv anterior; execução da raiz falha por imports atuais; nenhum pacote extra instalado; `COMMIT_REAL: —` | — |
| 26/08/2026 10:28:42 -03:00 | INT-P5-004 | Workflow integrado de desenvolvimento iniciado | `TODO` → `IN_PROGRESS` | branch correta; alterações preexistentes de P5 preservadas; comandos e dependências de P5-001..003 em consolidação; divergência documental do status de P5-003 registrada para verificação; `COMMIT_REAL: —` | — |
| 26/08/2026 10:40:13 -03:00 | INT-P5-004 | Workflow integrado documentado e validado | `IN_PROGRESS` → `VALIDATED` | sete passos em `docs/integration.md`; Uvicorn e npm start PASS; health direto/proxy 200 `{"status":"ok"}`; página Angular 200; sem Ollama/Qdrant, script, dependência, Docker, Compose ou código funcional; processos identificados encerrados; listener 8000 permaneceu reportado com PID inexistente após limpeza; `COMMIT_REAL: —` | — |

### Registro detalhado — INT-P0-004

```text
ID: INT-P0-004
STATUS_ANTERIOR: READY
STATUS_FINAL: BLOCKED
DIAGNOSTICO_CONFIRMADO: ambiente não contém pytest nem runtime Node/npm; sem evidência frontend suficiente para validação
AMBIENTE: Python 3.12.10; pip 26.1.2; Node indisponível; npm indisponível
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: registro operacional do baseline e do bloqueio ambiental; nenhum código/configuração funcional alterado
TESTES_EXECUTADOS: python -m pytest tests -q; python -m unittest discover -s tests -v; npm ci; npm run build; npm test -- --watch=false; tsc app/spec
RESULTADOS: pytest não disponível; unittest 29 coletados, 29 aprovados, 0 falhos, 0 skipped/xfailed em 1,294 s; comandos frontend não iniciaram por ausência de Node/npm
FRONTEND_INSTALL: não executado; npm indisponível
FRONTEND_BUILD: não executado; npm indisponível
FRONTEND_TESTS: não executado; npm indisponível
TYPESCRIPT: app/spec não executados; node indisponível
FALHAS_PREEXISTENTES: não revalidadas neste ambiente
LIMITACOES: bloqueio ambiental; não foi possível distinguir falhas de aplicação e specs no frontend
DOCUMENTACAO_ATUALIZADA: checklist, controle por item e registro cronológico
RISCOS_RESIDUAIS: baseline frontend e comando pytest permanecem sem validação neste ambiente
COMMIT_SUGERIDO: docs(integration): record blocked reproducible baseline
COMMIT_REAL: —
OBSERVACOES: package.json, package-lock.json e requirements.txt preservados; sem instalação, correção ou integração
```

### Registro detalhado da recuperação — INT-P0-004

```text
ID: INT-P0-004
STATUS_ANTERIOR: BLOCKED
STATUS_FINAL: VALIDATED
DIAGNOSTICO_CONFIRMADO: impedimentos ambientais removidos; baseline backend e frontend integralmente executado
AMBIENTE: Python 3.12.10; pip 25.0.1 no venv; pytest 9.1.1 local; Node 24.19.0; npm/npx 11.17.0
PREPARACAO: chatbot_processual_ai/.venv ignorado com requirements.txt + pytest local; Node LTS instalado via winget no escopo do usuário
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
ARTEFATOS_LOCAIS: chatbot_processual_ai/.venv; frontend/node_modules; frontend/.angular; frontend/dist; caches Python/Angular ignorados
RESUMO_DIFF: atualização documental do baseline; nenhum código, manifesto, regra ou integração alterado
BACKEND: python -m pytest tests -q -> 29 passed, 0 failed, 0 skipped/xfailed, 1 warning, 1,77 s
FRONTEND_INSTALL: npm ci -> PASS; 468 pacotes; 28 vulnerabilidades reportadas; package.json e package-lock.json intactos
FRONTEND_BUILD: npm run build -> PASS em 4,167 s; aviso de budget CSS (5,29 kB para limite de 4,00 kB)
FRONTEND_TESTS: npm test -- --watch=false -> FAIL antes da coleta; 4 erros TS2305 em specs com imports desatualizados
TYPESCRIPT_APP: PASS
TYPESCRIPT_SPEC: FAIL; mesmos 4 erros TS2305
FALHAS_PREEXISTENTES: specs importam Chat, LocalStorage e State não exportados; budget CSS acima do limite de warning
LIMITACOES: pytest não declarado nos manifests; dependências Python sem pins; npm ci reportou vulnerabilidades e scripts pendentes de allowScripts
DOCUMENTACAO_ATUALIZADA: checklist, controle por item e registro cronológico; entrada BLOCKED anterior preservada
RISCOS_RESIDUAIS: baseline depende de pytest instalado localmente; specs permanecem sem compilar; vulnerabilidades do lockfile não corrigidas neste item
COMMIT_SUGERIDO: docs(integration): record reproducible technical baseline
COMMIT_REAL: —
OBSERVACOES: nenhuma falha mascarada; nenhuma integração exercitada; INT-P0-005 permaneceu inalterado
```

### Registro detalhado — INT-P0-005

```text
ID: INT-P0-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DIAGNOSTICO_CONFIRMADO: o escopo negativo aparecia parcialmente na checklist e na documentação geral, mas não estava consolidado em uma fonte dedicada à integração
DATA_HORA: 20/08/2026 16:07:15 -03:00
DOCUMENTO_DE_INTEGRACAO: docs/integration.md
PRINCIPIO: preservar comportamento, layout, funcionalidades e arquitetura; alterar somente o necessário para estabelecer, validar, proteger ou documentar Angular ↔ FastAPI
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md; docs/integration.md
RESUMO_DIFF: documentação do objetivo mínimo, teste de inclusão, escopo negativo por categoria, dívida técnica, exceção comprovada e exemplos normativos
TESTES_EXECUTADOS: validação documental por busca dirigida; git status --short; revisão dos documentos alterados; git diff --check
RESULTADOS: critérios de aceite documentados; nenhum código funcional, layout, feature, contrato HTTP detalhado ou item P1 alterado
DOCUMENTACAO_ATUALIZADA: checklist, controle de progresso e documento dedicado de integração
RISCOS_RESIDUAIS: decisões de contrato, sessão, CORS/proxy, DTOs e topologia permanecem para P1
COMMIT_SUGERIDO: docs(integration): define conservative integration scope
COMMIT_REAL: —
OBSERVACOES: checkpoint P0 não criado; fase P0 não declarada fechada
```

### Registro detalhado — INT-P1-001

```text
ID: INT-P1-001
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 20/08/2026 16:57:37 -03:00
DOCUMENTO_ALTERADO: docs/integration.md
TOPOLOGIA_APROVADA: Browser / Angular → HTTP + JSON → FastAPI (/api/...) → orquestradores, agentes, serviços, persistência, RAG, Ollama e Qdrant
FRONTEIRA_DE_DEPENDENCIA: Angular conhece somente a API pública; backend não conhece componentes, services, estilos ou estado interno Angular
EVIDENCIAS_INSPECIONADAS: chatbot_processual_ai/api.py; frontend/src/app/core/services/chat.ts; estrutura superficial de frontend/src/app; estrutura superficial de agents, orchestrators e services; docs/ARCHITECTURE.md
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: decisão arquitetural, diagrama lógico, direções de dependência, responsabilidades mínimas, encapsulamento e exclusão do simulador
AUSENCIA_DE_IMPLEMENTACAO: confirmada; nenhum código funcional alterado
TESTES_EXECUTADOS: validação documental por busca dirigida; git status --short; revisão do diff autorizado; git diff --check
RESULTADOS: critérios de aceite satisfeitos; nenhum detalhe de contrato, sessão, erro, timeout ou rede congelado; nenhum outro item alterado
RISCOS_LIMITACOES: divergência /api/chat versus /api/processos/chat encaminhada a INT-P1-002; sessão a INT-P1-003; erros a INT-P1-004; timeout a INT-P1-005; proxy/CORS e rede a INT-P1-006
COMMIT_SUGERIDO: docs(integration): formalize Angular FastAPI topology
COMMIT_REAL: —
OBSERVACOES: G1 permanece aberto; checkpoint P1 não criado
```

### Registro detalhado — INT-P1-002

```text
ID: INT-P1-002
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 20/08/2026 17:25:55 -03:00
ENDPOINT_OBSERVADO: POST /api/processos/chat; request e response application/json
SCHEMAS_ARQUIVOS_INSPECIONADOS: chatbot_processual_ai/api.py; chatbot_processual_ai/schemas/processual_contracts.py; chatbot_processual_ai/orchestrators/processual_chat_orchestrator.py; chatbot_processual_ai/agents/agent2_context_collection.py; chatbot_processual_ai/services/rag_retriever.py; chatbot_processual_ai/tests/test_rag_base.py; chatbot_processual_ai/tests/test_progress_events.py; frontend/src/app/core/services/chat.ts
CONTRATO_V1_CONGELADO: versão lógica/documental, sem criação de /v1; request session_id + mensagem; response session_id + resultado completo
OBRIGATORIEDADE_NULABILIDADE: session_id da request é opcional e anulável; mensagem é obrigatória e não anulável; envelope de sucesso é obrigatório e não anulável; nulabilidade dos campos de resultado registrada individualmente
CLASSIFICACAO_DOS_CAMPOS: resposta e processo_ativo como contrato principal; tipo, intent, collection_status, failed_stage, rag_status e contêiner fontes como contrato público auxiliar; estrutura interna de fontes não congelada
EXEMPLOS_REGISTRADOS: sucesso; processo ausente/missing_number; falha controlada em Agente 1 com HTTP 200; erro de validação HTTP 422
SEMANTICA_HTTP: 200 para conclusão e falha controlada; 422 para request inválida; nenhum HTTPException explícito no endpoint; 404/405 do framework; falha inesperada sem handler específico resulta em 500
POLITICA_COMPATIBILIDADE: adição ignorável pode ser compatível; rota/método, remoção/renomeação, tipo, nulabilidade, obrigatoriedade ou semântica incompatíveis são breaking
DECISOES_ADIADAS: sessão para INT-P1-003; erro/UX para INT-P1-004; timeout para INT-P1-005; proxy/CORS/rede para INT-P1-006
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: especificação documental do contrato factual e atualização operacional exclusiva de INT-P1-002
TESTES_EXECUTADOS: pytest backend; inspeção dirigida; validação ASGI com orquestrador controlado; revisão do diff autorizado; git diff --check
RESULTADOS: 29 testes aprovados; ASGI confirmou normalização, strings vazias, 200, 422, 404, 405 e JSON; nenhuma mudança funcional
AUSENCIA_DE_IMPLEMENTACAO: confirmada; backend, frontend, schemas e DTOs inalterados
RISCOS: session_id ausente/nulo/vazio converge para default compartilhado; mensagem vazia/espaços é aceita; não há response_model; objetos de fontes não têm schema estável; frontend ainda usa /api/chat, body parcial e Observable<any>; não há testes HTTP dedicados
COMMIT_SUGERIDO: docs(integration): freeze processual chat HTTP v1 contract
COMMIT_REAL: —
OBSERVACOES: G1 permanece aberto; checkpoint P1 não criado; INT-P1-003..006 permanecem TODO
```

### Registro detalhado — INT-P1-003

```text
ID: INT-P1-003
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 12:06:01 -03:00
PROBLEMA_CONFIRMADO: ausência, null, vazio ou espaços em session_id convergem para DEFAULT_SESSION_ID "default"; clientes distintos podem selecionar a mesma entrada de _SESSIONS e compartilhar conversation, active_process e last_intent
DECISAO_GERACAO_REUSO: backend gera UUID aleatório opaco quando não há ID utilizável; ID conhecido reutiliza contexto; ID válido desconhecido cria contexto vazio sob o próprio ID; mesmo ID preserva contexto enquanto a entrada existir
ARMAZENAMENTO_WEB: sessionStorage separado do histórico de processos
REFRESH: mantém o ID e preserva contexto somente se o backend ainda possuir a sessão
NOVA_ABA: independente por padrão; possível cópia inicial de sessionStorage quando há opener foi registrada como limitação a considerar em P3
RESTART_BACKEND: _SESSIONS é perdido; ID remanescente no browser cria contexto vazio, sem falsa promessa de continuidade
RESET_NOVA_CONVERSA: descartar ID no browser; próxima mensagem inicia nova sessão; sem deleção backend sincronizada obrigatória no MVP
ISOLAMENTO_PROCESSO_ATIVO: active_process pertence ao estado indexado por session_id e alimenta resultado.processo_ativo; IDs distintos isolam o contexto, mesmo ID o reutiliza
MEMORIA_MVP: _SESSIONS local ao processo, sem persistência distribuída; entradas podem permanecer após fechar aba ou reset
DIVIDA_EXPIRACAO_LIMITE: não há TTL, limite, limpeza ou eviction confirmados; política adiada para antes de escala/produção relevante
PRIVACIDADE: ID não contém PII, nome, CPF, número de processo, conversa ou estado serializado; não é usuário, histórico, autenticação nem autorização
ARQUIVOS_INSPECIONADOS: AGENTS.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md; docs/integration.md; chatbot_processual_ai/api.py; chatbot_processual_ai/session_state.py; chatbot_processual_ai/orchestrators/processual_chat_orchestrator.py; frontend/src/app/core/services/local-storage.ts; frontend/src/app/features/chat/chat.ts; documentação MDN de sessionStorage e opener
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: decisão documental do ciclo de vida da sessão e atualização operacional exclusiva de INT-P1-003
AUSENCIA_DE_IMPLEMENTACAO: confirmada; backend, frontend, DEFAULT_SESSION_ID, _SESSIONS, schemas, testes, UUID e sessionStorage não foram modificados/implementados
DECISOES_ADIADAS: semântica de erros para INT-P1-004; geração/isolamento/testes para P2; armazenamento/captura/reset frontend para P3
TESTES_EXECUTADOS: não aplicável; item exclusivamente documental, sem implementação funcional
RESULTADOS: estratégia inequívoca e compatível com o contrato P1-002; critérios arquiteturais cobertos; G1 permanece aberto
COMMIT_SUGERIDO: docs(integration): define web session lifecycle
COMMIT_REAL: —
OBSERVACOES: INT-P1-004..006 permanecem TODO; CHECKPOINT_P1: AINDA_NAO
```

### Registro detalhado — INT-P1-004

```text
ID: INT-P1-004
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 12:16:19 -03:00
ENDPOINT_INSPECIONADO: POST /api/processos/chat
COMPORTAMENTO_FACTUAL: 200 com envelope também em exceção capturada pelos Agentes 1..4; 422 para validação; 404/405 pelo framework; exceção fora da proteção pode resultar em 500; transporte não possui response
CATEGORIAS_APROVADAS: sucesso funcional; sucesso degradado; falha controlada; erro HTTP 4xx; erro de transporte; falha técnica inesperada/5xx; timeout reservado
MATRIZ_DE_ERRO: precedência transporte → HTTP → contrato 2xx; em 2xx, failed_stage prevalece como falha controlada, depois degradação auxiliar e sucesso
FAILED_STAGE: string|null obrigatório/anulável; Agente 1..Agente 4; presença indica exceção capturada e resposta segura; null não prova saúde total; nunca exibido diretamente
RAG_STATUS: not_needed|success|empty|unavailable|error; indisponibilidade/erro são degradáveis quando resultado.resposta permanece utilizável; frontend não conhece Qdrant/RAG interno
COLLECTION_STATUS: success|already_active|missing_number|not_found|not_needed; descreve coleta; ausência/não localização é resultado funcional, não 4xx
REGRA_RESPOSTA_PUBLICA: resposta funcional ou falha controlada usa resultado.resposta; 4xx/transporte/5xx usam classe genérica segura; nunca JSON/erro bruto
REGRA_LOGS: tipo da exceção, estágio e contexto técnico mínimo pertencem a log/trace, com sanitização e acesso adequado
PROTECAO_EXPOSICAO: stack, path, hostname, ambiente, segredo, SQL, configuração Ollama, detalhes Qdrant, estrutura Python e IDs internos excluídos da UI
RELACAO_HTTP_TRANSPORTE: 4xx rejeita request; 5xx é falha técnica; sem response é transporte; nenhum deles é resposta conversacional normal nem failed_stage sintético
TIMEOUT: adiado integralmente para INT-P1-005
MOCK: falha real nunca pode ser convertida em mock de sucesso; remoção/integração pertencem a P3
RECUPERABILIDADE: falha deve encerrar loading e permitir tentativa posterior; implementação adiada a P3/P4
ARQUIVOS_INSPECIONADOS: AGENTS.md; checklist; controle; docs/integration.md; api.py; schemas/processual_contracts.py; processual_chat_orchestrator.py; agent2_context_collection.py; rag_retriever.py; ChatService; ChatComponent; StateService; testes de RAG e progress events
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: política documental de erros/degradação e atualização operacional exclusiva de INT-P1-004
AUSENCIA_DE_IMPLEMENTACAO: confirmada; backend, frontend, schemas, sessão, timeout, healthcheck, proxy/CORS e mock inalterados
CONTRATO_P1_002: preservado; nenhum campo, tipo, nulabilidade, status HTTP ou DTO alterado
SESSAO_P1_003: preservada; nenhuma decisão reaberta
TESTES_EXECUTADOS: 3 testes backend focados em falha controlada e RAG; regressão backend completa 29/29; inspeção dirigida; revisão do diff autorizado; git diff --check
RISCOS: frontend baseline ainda mascara sucesso e erro com mock; endpoint não possui handler específico fora do orquestrador; implementação e cobertura HTTP/frontend permanecem para P2/P3/P4
COMMIT_SUGERIDO: docs(integration): define chat error semantics
COMMIT_REAL: —
OBSERVACOES: G1 permanece aberto; INT-P1-005 e INT-P1-006 permanecem TODO; CHECKPOINT_P1: AINDA_NAO
```

### Registro detalhado — INT-P1-005

```text
ID: INT-P1-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 13:17:01 -03:00
ENDPOINT_INSPECIONADO: POST /api/processos/chat
LIMITES_ATUAIS: Angular 60 s; Ollama geração e embedding 60 s por request; Qdrant 10 s por request; FastAPI/request sem timeout total explícito
FLUXO_DEMORADO: orquestrador sequencial Agentes 1→4; caminhos podem fazer gerações Ollama sequenciais; RAG faz embedding da consulta, chamadas Qdrant e, para cada chunk textual, embedding seguido de upsert
RETRIES: nenhum retry automático geral; embedding tenta /api/embed e, em qualquer EmbeddingError, tenta /api/embeddings, cada tentativa com 60 s; sincronização repete por chunk
OPERACOES_SEM_TIMEOUT: request FastAPI e pipeline completo não possuem deadline total; SQLite local não possui timeout de aplicação explícito neste fluxo
DECISAO_APROVADA: manter 60 s como limite por operação Ollama; introduzir em P2 orçamento total backend de 120 s; introduzir em P3 timeout cliente de 135 s
MARGEM: 15 s entre deadline backend e cliente para transporte, serialização, processamento antes/depois das dependências e emissão da resposta controlada
REGRA_NORMATIVA: timeout por dependência < orçamento total backend < timeout cliente; qualquer alteração interna exige rever os limites externos; timeout infinito proibido
MENSAGEM_SEGURA: A solicitação demorou mais que o esperado. Tente novamente.
P1_004: timeout interno capturado pode ser falha controlada contratual; timeout escapado/servidor segue 5xx; timeout cliente é categoria própria sem failed_stage sintético
P1_003: timeout não invalida session_id, não cria sessão e não limpa contexto; backend pode continuar processando após o cliente expirar
RECUPERABILIDADE: loading deve terminar, nova tentativa deve ser permitida e timeout nunca aciona responderMock()
CONFIGURACAO_FUTURA: backend em configuração/env existente; frontend em constante/configuração central do service; sem framework adicional
RISCOS: laço RAG torna o total atual não limitado pelo valor de 60 s; fallback de embedding pode consumir duas tentativas; retry manual pode observar estado produzido pela request anterior; ausência atual de cancelamento distribuído
AUSENCIA_DE_IMPLEMENTACAO: confirmada; nenhum código, env, timeout, retry, proxy, CORS, contrato ou sessão alterado
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
TESTES_EXECUTADOS: inspeção estática dirigida; revisão do diff autorizado; git diff --check
COMMIT_SUGERIDO: docs(integration): define chat timeout policy
COMMIT_REAL: —
OBSERVACOES: G1 permanece aberto; INT-P1-006 permanece TODO; CHECKPOINT_P1: AINDA_NAO
```

### Registro detalhado — INT-P1-006

```text
ID: INT-P1-006
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 13:39:25 -03:00
TOPOLOGIA_OBSERVADA: ChatService usa /api/chat relativo; nenhum proxy/environment de API; Angular documentado em localhost:4200; FastAPI documentado em localhost:8000; api.py sem CORS, frontend estático ou reverse proxy
DECISAO_LOCAL: browser acessa Angular :4200; Angular usa /api/...; proxy de desenvolvimento encaminha /api/* ao FastAPI :8000
PORTAS: Angular 4200; FastAPI 8000
BASE_API: /api como base pública lógica; chat contratual em /api/processos/chat
POLITICA_PROXY: preservar método, path, body JSON, response e status HTTP; implementação em INT-P5-001
DECISAO_CORS: desnecessário em desenvolvimento com proxy e em produção de mesma origem; necessário somente em cross-origin real
PRODUCAO_PREFERENCIAL: origem pública única com frontend em / e /api/* encaminhado ao FastAPI; domínio, hosting e tecnologia não definidos
FALLBACK_CROSS_ORIGIN: base da API por configuração e allowlist explícita; sem wildcard por conveniência; credenciais somente se justificadas
P2_005: condicional; implementar/testar CORS somente se a topologia final exigir origens distintas, ou dispensar/adiar formalmente sob mesma origem
P5_001: responsável pela criação e configuração real do proxy Angular
P5_004: responsável pelo workflow conjunto de desenvolvimento
RELACAO_DECISOES: contrato P1-002, session_id JSON de P1-003, semântica HTTP de P1-004 e política temporal P1-005 preservados
AUSENCIA_DE_IMPLEMENTACAO: confirmada; nenhum proxy, CORS, healthcheck, deploy, código ou configuração funcional alterado
ARQUIVOS_MODIFICADOS: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: decisão documental de topologia/origens e atualização operacional exclusiva de INT-P1-006
TESTES_EXECUTADOS: inspeção estática dirigida; revisão do diff autorizado; git diff --check
RISCOS: infraestrutura e origem de produção desconhecidas; CORS futuro depende da topologia real; configuração e smoke do proxy permanecem para P5
COMMIT_SUGERIDO: docs(integration): define Angular FastAPI network topology
COMMIT_REAL: —
OBSERVACOES: G1 permanece aberto; P1 pronta para auditoria separada de fechamento; P2 não iniciada; CHECKPOINT_P1: AINDA_NAO
```

### Registro detalhado — INT-P2-001

```text
ID: INT-P2-001
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 13:52:00 -03:00
ARQUIVO_TESTE: chatbot_processual_ai/tests/test_api_processual_chat.py
FERRAMENTA_ASGI: cliente ASGI mínimo local sobre a aplicação FastAPI real; httpx não está instalado e nenhuma dependência foi adicionada
ISOLAMENTO: run_processual_chat_step substituído somente nos cenários de contrato/continuidade; falha controlada usa orquestrador real com interpret_user_message substituído; _SESSIONS limpo antes e depois de cada teste
CENARIOS: sucesso HTTP/JSON e envelope público; session_id explícito normalizado e devolvido; resposta utilizável; processo ativo propagado; continuidade do mesmo ID; payload sem mensagem retorna 422; falha controlada retorna 200 e não vaza marcador técnico sintético
BASELINE: 29 passed, 1 warning de cache pytest sem permissão, em 1,64 s
TESTE_FOCADO: 4 passed, 1 warning de cache pytest sem permissão, em 0,47 s
REGRESSAO_FINAL: 33 passed, 1 warning de cache pytest sem permissão, em 1,72 s
CONTAGEM: 29 testes anteriores + 4 novos = 33
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/tests/test_api_processual_chat.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: cobertura HTTP determinística do contrato processual e atualização operacional exclusiva de INT-P2-001
LIMITACOES: vazio/espaços e limites permanecem para INT-P2-004; isolamento entre clientes sem ID, UUID e remoção de default permanecem para INT-P2-002; handler de exceção HTTP inesperada não foi criado
ESCOPO_NEGATIVO: api.py, schemas, orquestradores, agentes, frontend, timeout, healthcheck, CORS, UUID e fallback default inalterados; INT-P2-002..005 permanecem TODO
REVISAO: diff completo revisado; sem debug, segredo real ou alteração funcional; git diff --check aprovado
COMMIT_SUGERIDO: test(api): cover processual chat http contract
COMMIT_REAL: —
CHECKPOINT_P2: AINDA_NAO
```

### Registro detalhado — INT-P2-002

```text
ID: INT-P2-002
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 14:48:58 -03:00
IMPLEMENTACAO: _normalize_session_id gera str(uuid4()) somente quando o ID está omitido, nulo, vazio ou contém apenas espaços
FALLBACK_ANTERIOR: DEFAULT_SESSION_ID = "default", compartilhado entre requests sem ID utilizável
ESTRATEGIA_NOVA: UUID v4 opaco por request sem ID utilizável; ID explícito aparado e preservado; _SESSIONS cria ou reutiliza contexto pela chave efetiva
ARQUIVOS_FUNCIONAIS_MODIFICADOS: chatbot_processual_ai/api.py
TESTES_ADICIONADOS_ALTERADOS: chatbot_processual_ai/tests/test_api_processual_chat.py; duas sessões sem ID e contextos independentes; formas não utilizáveis; ID explícito/continuidade; ID desconhecido após limpeza global
TESTE_DUAS_SESSOES: IDs UUID v4 distintos; objetos de estado distintos; processos ativos A e B preservados separadamente
TESTE_CONTINUIDADE: duas requests com o mesmo ID reutilizam o mesmo objeto de estado e preservam processo_ativo
TESTE_ID_EXPLICITO: ID válido normalizado é devolvido sem substituição por UUID
TESTE_ID_DESCONHECIDO_RESTART: _SESSIONS limpo; ID recebido preservado; novo contexto vazio criado sob o próprio ID; estado anterior não recuperado
BASELINE: 33 passed, 1 warning ambiental de cache pytest sem permissão, em 1,91 s
TESTE_FOCADO: 7 passed, 1 warning ambiental de cache pytest sem permissão, em 0,53 s
REGRESSAO_FINAL: 36 passed, 1 warning ambiental de cache pytest sem permissão, em 1,91 s
CONTAGEM: 33 testes anteriores + 3 novos = 36
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/api.py; chatbot_processual_ai/tests/test_api_processual_chat.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: remoção localizada do fallback compartilhado, geração UUID v4 e cobertura HTTP determinística da política P1-003
LIMITACOES: sessões continuam locais e em memória, sem TTL, limite, eviction ou persistência; restart perde contexto; session_id não autentica; compartilhamento deliberado do mesmo ID permanece possível
ESCOPO_NEGATIVO: frontend, schemas, orquestradores, agentes, persistência, Redis, timeout, healthcheck, CORS e INT-P2-003..005 inalterados
REVISAO: diff completo revisado; sem debug, segredo, PII ou alteração fora do escopo; git diff --check aprovado
COMMIT_SUGERIDO: fix(api): isolate processual chat sessions per client
COMMIT_REAL: —
CHECKPOINT_P2: AINDA_NAO
```

### Registro detalhado — INT-P2-003

```text
ID: INT-P2-003
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 15:21:09 -03:00
ROTA_IMPLEMENTADA: GET /api/health
SEMANTICA: confirma somente que a fronteira FastAPI está acessível e responde HTTP; não representa saúde integral do sistema
PAYLOAD: {"status":"ok"}
ARQUIVOS_FUNCIONAIS_MODIFICADOS: chatbot_processual_ai/api.py
TESTE_CRIADO_ALTERADO: chatbot_processual_ai/tests/test_api_processual_chat.py; aplicação ASGI real; HTTP 200; JSON exato; _SESSIONS preservado
DEPENDENCIAS_PESADAS: handler retorna literal determinístico; não chama Ollama, Qdrant, RAG, banco, agentes, orquestradores ou serviços
BASELINE: 36 passed, 1 warning ambiental de cache pytest sem permissão, em 2,10 s
TESTE_FOCADO: 8 passed, 1 warning ambiental de cache pytest sem permissão, em 0,49 s
REGRESSAO_FINAL: 37 passed, 1 warning ambiental de cache pytest sem permissão, em 1,98 s
CONTAGEM: 36 testes anteriores + 1 novo = 37
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/api.py; chatbot_processual_ai/tests/test_api_processual_chat.py; docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: rota GET mínima, teste HTTP sem efeito em sessão e documentação explícita da semântica limitada
RISCOS: /api/health não detecta indisponibilidade de Ollama, Qdrant, RAG, banco, agentes ou orquestradores por definição
ESCOPO_NEGATIVO: frontend, CORS, proxy, timeout, contrato de chat, P2-004 e P2-005 inalterados; G2 não fechado
REVISAO: diff completo revisado; sem debug, segredo, metadata interna ou alteração fora do escopo; git diff --check aprovado
COMMIT_SUGERIDO: feat(api): add minimal healthcheck
COMMIT_REAL: —
CHECKPOINT_P2: AINDA_NAO
```

### Registro detalhado — INT-P2-004

```text
ID: INT-P2-004
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 15:34:37 -03:00
COMPORTAMENTO_ANTERIOR: mensagem str obrigatória; ausência e null retornavam 422; vazio e whitespace eram aceitos e chegavam ao orquestrador; sem limite máximo; mensagem sem normalização
VALIDACAO_IMPLEMENTADA: field_validator Pydantic na request HTTP exige ao menos um caractere não-whitespace e devolve a string original
POLITICA_VAZIO: HTTP 422 na fronteira, sem execução do endpoint/orquestrador ou criação de sessão
POLITICA_WHITESPACE: HTTP 422 para espaço, tab, LF e CR sem conteúdo textual
MAX_MESSAGE_LENGTH: nenhum limite adicional no MVP; não há requisito objetivo que sustente um número sem arbitrariedade; revisar antes de exposição pública em escala
SEMANTICA_4XX: violação do contrato de entrada ou condição HTTP; não produz resposta conversacional
SEMANTICA_RESULTADO_FUNCIONAL: missing_number/not_found após request válida permanecem HTTP 200 com resposta segura
SEMANTICA_FALHA_CONTROLADA: failed_stage não nulo permanece HTTP 200 com resposta segura
SEMANTICA_FALHA_INESPERADA: exceção não capturada permanece HTTP 500 padrão FastAPI; INTERNAL_TEST_MARKER não aparece no payload
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/api.py; chatbot_processual_ai/tests/test_api_processual_chat.py; docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
TESTES_ADICIONADOS_ALTERADOS: null sem sessão; vazio sem orquestrador/sessão; whitespace; mensagem válida preservada; missing_number 200; falha inesperada 500 segura; helper ASGI permite observar response 500
BASELINE: 37 passed, 1 warning ambiental de cache pytest sem permissão, em 1,88 s
TESTE_FOCADO: 14 passed, 1 warning ambiental de cache pytest sem permissão, em 0,49 s
REGRESSAO_FINAL: 43 passed, 1 warning ambiental de cache pytest sem permissão, em 1,98 s
CONTAGEM: 37 testes anteriores + 6 novos = 43
RESUMO_DIFF: validação mínima no schema HTTP, cobertura das quatro categorias semânticas e documentação da decisão de tamanho
RISCOS: ausência de limite adicional de mensagem; formato detalhado do 422 pertence ao FastAPI/Pydantic; 500 depende do tratamento seguro padrão do FastAPI/Starlette
ESCOPO_NEGATIVO: sessão, healthcheck, timeout, CORS, frontend, P2-005 e G2 inalterados; nenhum handler ou schema de erro novo
REVISAO: diff completo e teste não rastreado revisados; sem debug, segredo real, normalização indevida ou alteração fora do escopo; git diff --check aprovado
COMMIT_SUGERIDO: fix(api): validate processual chat messages
COMMIT_REAL: —
CHECKPOINT_P2: AINDA_NAO
```

### Registro detalhado — INT-P2-005

```text
ID: INT-P2-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 15:40:40 -03:00
TOPOLOGIA_ANALISADA: desenvolvimento Angular :4200 com /api/* relativo e proxy futuro para FastAPI :8000; produção preferencial sob origem pública única
CROSS_ORIGIN_REAL_ATUAL: NÃO
ORIGEM_PRODUCAO_REAL: NÃO DEFINIDA
DECISAO_CORS_ATUAL: NÃO NECESSÁRIO; não implementar enquanto a topologia permanecer same-origin
POLITICA_FUTURA: se um deployment usar origens distintas, implementar antes dele allowlist explícita e configurável, métodos e headers mínimos e credenciais somente mediante requisito separado
CORS_IMPLEMENTADO: NÃO
IMPLEMENTACAO_FUNCIONAL: NENHUMA / NÃO NECESSÁRIA
ARQUIVOS_MODIFICADOS_NO_ITEM: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; docs/integration.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
BASELINE_BACKEND: 43 passed, 0 failed, 0 skipped, 0 warnings, em 1,77 s; cacheprovider desabilitado por restrição ambiental de diretórios de cache
REGRESSAO_FINAL: 43 passed, 0 failed, 0 skipped, 0 warnings, em 1,69 s; cacheprovider desabilitado pela mesma restrição ambiental
RISCOS: origem final de produção permanece indefinida; CORS deverá ser reavaliado antes de qualquer deployment cross-origin; CORS não fornece autenticação, autorização ou proteção do session_id
ESCOPO_NEGATIVO: backend funcional, frontend, proxy, sessão, healthcheck, validação HTTP, timeout, P3, G2 e checkpoint P2 inalterados
REVISAO: diff completo revisado; sem middleware, wildcard, origem fictícia, credenciais, debug, segredo ou alteração fora do escopo; git diff --check aprovado
COMMIT_SUGERIDO: docs(integration): validate same-origin CORS decision
COMMIT_REAL: —
CHECKPOINT_P2: AINDA_NAO
```

---

### Registro detalhado — INT-P3-001

```text
ID: INT-P3-001
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 21/08/2026 16:23:20 -03:00
ARQUIVOS_INSPECIONADOS: AGENTS.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md; docs/integration.md; chatbot_processual_ai/api.py; chatbot_processual_ai/schemas/processual_contracts.py; chatbot_processual_ai/tests/test_api_processual_chat.py; frontend/src/app/core/services/chat.ts; estrutura e consumidores em frontend/src/app
LOCAL_DTO: frontend/src/app/core/types/processual-chat.types.ts; `models/` foi descartado porque a regra global de .gitignore tornaria o arquivo não rastreável
TIPOS_CRIADOS: ProcessualChatRequest; ProcessualChatResponse; ProcessualChatHttpResponse
NULABILIDADE: request.session_id opcional e anulável; mensagem obrigatória; envelope obrigatório e não anulável; intent, processo_ativo, collection_status, failed_stage e rag_status presentes e anuláveis
FONTES: ReadonlyArray<unknown>; contêiner público congelado, estrutura interna deliberadamente não congelada; nenhum any
CHATSERVICE: retorno Observable<ProcessualChatHttpResponse> e post<ProcessualChatHttpResponse>; Observable<any> removido
AMBIENTE: node/npm ausentes do PATH; runtime Node disponível do Playwright v24.14.1 utilizado diretamente; versão npm indisponível nesta sessão
TYPECHECK_APP: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
BUILD: PASS — node node_modules/@angular/cli/bin/ng.js build; warning CSS preexistente de 1,29 kB acima do budget
SPECS: tsconfig.spec FAIL somente nos quatro imports antigos já registrados (Chat, LocalStorage, State e Chat); nenhum erro novo de DTO/service; npm test não executado
NAO_ANTECIPACAO: endpoint /api/chat, body { mensagem }, timeout 60000, componente, mock, sessão, erros, histórico, healthcheck e metadata preservados; backend e specs inalterados; INT-P3-002..008 permanecem TODO
ARQUIVOS_MODIFICADOS: frontend/src/app/core/types/processual-chat.types.ts; frontend/src/app/core/services/chat.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
REVISAO: diff completo autorizado revisado; busca dirigida sem Observable<any>, post<any> ou get<any>; sem debug, segredo, manifestos ou arquivos fora do escopo; git diff --check aprovado
RISCOS: integração HTTP real permanece para INT-P3-003/P3-004; sessão frontend para INT-P3-002; dívida de specs para INT-P4-001; elementos de fontes seguem desconhecidos por contrato
COMMIT_SUGERIDO: feat(frontend): type processual chat HTTP contract
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-002

```text
ID: INT-P3-002
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 07:33:43 -03:00
SERVICE_CRIADO: frontend/src/app/core/services/chat-session.ts; ChatSessionService com providedIn root
CHAVE: processual_chat_session_id
STORAGE: sessionStorage; nenhum novo uso de localStorage para session_id
API_PUBLICA: getSessionId(): string | null; setSessionId(sessionId: string): void; clearSession(): void
SEMANTICA: ausência retorna null; set preserva exatamente o ID opaco; leituras posteriores e refresh da mesma aba preservam o valor; clear remove somente a chave conversacional
RESET: clearSession remove o ID local para que a futura request comece sem session_id; não chama backend nem limpa histórico
SEPARACAO: LocalStorageService e seu histórico chatbot_historico inalterados; StateService inalterado
TYPECHECK_APP_BASELINE: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_APP_FINAL: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
BUILD: PASS — node node_modules/@angular/cli/bin/ng.js build; primeira tentativa no sandbox falhou ambientalmente com spawn EPERM, repetição autorizada fora do sandbox passou; warning CSS preexistente de 1,29 kB acima do budget
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos já registrados (Chat, LocalStorage, State e Chat); nenhum erro novo do service; specs não corrigidas
REUSO_HTTP_REAL: adiado para INT-P3-003/INT-P3-004
NAO_ANTECIPACAO: ChatService, endpoint, body, timeout, componente, response, mock, erros, histórico, healthcheck, metadata, DTO, specs e backend inalterados por este item
ARQUIVOS_MODIFICADOS: frontend/src/app/core/services/chat-session.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RISCOS: session_id não é autenticação; contexto backend permanece em memória e se perde no restart; nova aba com window.opener pode herdar cópia inicial conforme comportamento conhecido do navegador
COMMIT_SUGERIDO: feat(frontend): persist processual chat session id
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-003

```text
ID: INT-P3-003
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 07:50:27 -03:00
ENDPOINT_ANTERIOR: POST /api/chat
ENDPOINT_NOVO: POST /api/processos/chat; URL relativa, sem host ou porta
BODY_ANTERIOR: objeto não tipado { mensagem }
REQUEST_DTO: ProcessualChatRequest; { mensagem } sem sessão; { session_id, mensagem } com sessão
RESPONSE_DTO: Observable<ProcessualChatHttpResponse>; post<ProcessualChatHttpResponse>
SESSION_SOURCE: ChatSessionService.getSessionId(); nenhum acesso direto a sessionStorage no ChatService
SESSION_SEM_ID: campo session_id omitido quando getSessionId() retorna null
SESSION_COM_ID: valor enviado exatamente como retornado pelo ChatSessionService; frontend não gera ou transforma ID
TIMEOUT_ANTERIOR: 60000 ms inline
TIMEOUT_NOVO: 135000 ms; constante local PROCESSUAL_CHAT_TIMEOUT_MS = 135_000
BACKEND_TOTAL_TIMEOUT_120_IMPLEMENTADO: NÃO
EVIDENCIA_TEMPORAL: api.py executa run_processual_chat_step sincronamente sem deadline total; busca backend encontrou apenas timeouts individuais de Ollama/embedding e Qdrant
LACUNA_CROSS_PHASE: política P1 previa orçamento total backend de 120 s, mas implementação não foi localizada após P2; a ordem runtime 120 s backend < 135 s frontend não está garantida
TYPECHECK_APP_BASELINE: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit, usando runtime Node do Playwright por node ausente do PATH
TYPECHECK_APP_FINAL: PASS — mesmo comando e runtime
BUILD: PASS — node node_modules/@angular/cli/bin/ng.js build; tentativa no sandbox falhou ambientalmente com spawn EPERM, repetição autorizada fora do sandbox passou; warning CSS preexistente de 1,29 kB
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos já registrados (Chat, LocalStorage, State e Chat); nenhum erro novo de DTO, ChatService, SessionService ou DI; specs não corrigidas
NAO_ANTECIPACAO: response.session_id não armazenado; response.resultado não consumido; responderMock preservado; sem UX de erro, retry, histórico, healthcheck, metadata, proxy ou correção de specs
ARQUIVOS_MODIFICADOS: frontend/src/app/core/services/chat.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
REVISAO: buscas dirigidas e diff completo revisados; ChatComponent, SessionService, backend, specs e manifestos não modificados pelo item; git diff --check aprovado; sem debug, segredo ou mudança fora do escopo
RISCOS: response.session_id só será persistido no fluxo real em P3-004; proxy depende de P5-001; UX de timeout/erro depende de P3-005; deadline backend total segue ausente; dívida de specs pertence a P4-001
COMMIT_SUGERIDO: feat(frontend): align chat service with processual API
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-004

```text
ID: INT-P3-004
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 08:38:15 -03:00
METODO_COMPONENTE_ENVIO: ChatComponent.enviar()
COMO_MENSAGEM_USUARIO_ENTRA_NO_CHAT: StateService.adicionarMensagem com role user antes da request
COMO_CARREGANDO_E_ATIVADO: StateService.carregando.set(true) antes de ChatService.enviar
NEXT_ANTERIOR: ignorava a response e chamava responderMock(pergunta)
ERROR_ANTERIOR: chamava responderMock(pergunta), produzindo falso sucesso
RESPONDER_MOCK_REFERENCIAS_ANTERIORES: next, error e declaração privada no ChatComponent
HISTORICO_ATUAL: carregado do LocalStorageService; gravação da pergunta pelo mock removida; sem nova persistência neste item
SESSION_SERVICE_ATUAL: ChatSessionService com get/set/clear sobre sessionStorage
USO_NOVO_DA_RESPONSE: next recebe ProcessualChatHttpResponse, persiste session_id e adiciona mensagem do bot
CAMPO_PUBLICO_EXIBIDO: response.resultado.resposta
PERSISTENCIA_SESSION_ID: ChatSessionService.setSessionId(response.session_id); nenhum sessionStorage direto no componente
ESTRATEGIA_LOADING: finalize no componente; uma única finalização para sucesso e erro
DESTINO_RESPONDER_MOCK: método e todas as referências removidos por ficarem sem uso legítimo
PROCESSO_ATIVO_OBSERVADO: disponível no DTO como response.resultado.processo_ativo; não consumido neste item
HISTORICO_ADIADO: SIM — semântica definitiva reservada a INT-P3-006
ERROS_ADIADOS: SIM — apresentação visual e StateService.erro reservados a INT-P3-005
TYPECHECK_APP_INICIAL: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_APP_FINAL: PASS — mesmo comando
BUILD: PASS — node node_modules/@angular/cli/bin/ng.js build; tentativa no sandbox falhou com spawn EPERM, repetição autorizada fora do sandbox passou; warning CSS preexistente de 1,29 kB
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos (Chat, LocalStorage, State e Chat); nenhuma falha nova
CONTINUIDADE_ESTATICA_COMPLETA: SIM — response X → setSessionId(X) → getSessionId() → request futura com X
CONTINUIDADE_E2E_EXECUTADA: NÃO
ARQUIVOS_MODIFICADOS: frontend/src/app/features/chat/chat.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: response real exibida, session_id persistido via responsabilidade existente, mock removido e loading finalizado por finalize
RISCOS: erro HTTP fica temporariamente sem apresentação visual; proxy e smoke integrado ainda indisponíveis; histórico correto permanece pendente
REVISAO: busca dirigida e diff completo revisados; ChatService, SessionService, DTOs, specs, backend e itens posteriores preservados; sem retry, debug, segredo ou fallback falso; git diff --check aprovado
COMMIT_SUGERIDO: feat(frontend): consume real processual chat response
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-005

```text
ID: INT-P3-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 09:11:20 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: worktree com alterações preexistentes de INT-P3-001..004 preservadas; nenhum arquivo staged
CLASSIFICACAO: TimeoutError → timeout; HttpErrorResponse status 0 → transporte; status 400..499 → HTTP 4xx; demais erros, incluindo 5xx, → falha técnica
MENSAGENS_PUBLICAS: timeout “A solicitação demorou mais que o esperado. Tente novamente.”; transporte “Não foi possível conectar ao serviço.”; 4xx “Não foi possível enviar a solicitação.”; técnica “Não foi possível concluir a solicitação.”
FONTE_MENSAGENS: docs/integration.md, Política do frontend e mensagens públicas + Política de timeout
STATE_SERVICE: StateService.erro reutilizado; StateService não modificado; erro limpo antes de nova request legítima
TEMPLATE: alerta mínimo dentro da área de mensagens com role=alert; CSS local mínimo; nenhum redesign
LOADING: finalize único de INT-P3-004 preservado; success e error liberam input/botão
RETRY: nenhum retry/retryWhen; nova tentativa manual permitida
SESSAO: session_id preservado; clearSession não chamado em erro
FALHA_CONTROLADA: responses 2xx permanecem no next e usam response.resultado.resposta; failed_stage/rag_status não são classificados no error handler
SEGURANCA: nenhum error.message, error.error, stack, URL, headers, statusText, body técnico ou objeto HttpErrorResponse renderizado
TYPECHECK_APP_BASELINE: PASS — runtime Node local + node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_APP_FINAL: PASS — mesmo comando
BUILD: PASS — runtime Node local + node_modules/@angular/cli/bin/ng.js build; repetição fora do sandbox após spawn EPERM; warning CSS baseline de 1,42 kB acima do budget
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos (Chat, LocalStorage, State e Chat); nenhuma falha nova
ARQUIVOS_MODIFICADOS: frontend/src/app/features/chat/chat.ts; frontend/src/app/features/chat/chat.html; frontend/src/app/features/chat/chat.css; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
NAO_ANTECIPACAO: ChatService, SessionService, StateService, DTOs, histórico P3-006, healthcheck P3-007, metadata P3-008, specs e backend não modificados
REVISAO: diff completo revisado; buscas dirigidas sem mock, retry ou exposição técnica; git diff --check aprovado
RISCOS: testes frontend completos permanecem para P4; proxy real para P5; smoke integrado para P4/P5/P7; histórico para P3-006; healthcheck visual para P3-007
COMMIT_SUGERIDO: fix(frontend): present recoverable chat request errors
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-006

```text
ID: INT-P3-006
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 09:25:44 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: worktree com alterações preexistentes de INT-P3-001..005 preservadas; nenhum arquivo staged
HISTORICO_ATUAL_EXISTE: SIM; carregado no ngOnInit e exibido no card de últimos processos
LOCAL_DE_PERSISTENCIA: LocalStorageService; localStorage sob a chave chatbot_historico
MODELO_DO_ITEM: ProcessoConsulta com numero_processo, data_consulta e resposta_resumo
PONTO_ANTERIOR_DE_GRAVACAO: responderMock, antes de P3-004, gravava pergunta como numero_processo em sucesso e erro
GRAVACAO_APOS_P3_004: nenhuma; a remoção do mock deixou o histórico sem novos itens
PONTO_NOVO_DE_GRAVACAO: next de ChatComponent.enviar, após response HTTP contratual
FONTE_NUMERO_PROCESSO: response.resultado.processo_ativo; nenhuma regex ou fallback para pergunta
PROCESSO_ATIVO_NULL_OU_VAZIO: não adiciona item; guarda simples com trim
FALHA_CONTROLADA_2XX: atualiza conforme a mesma regra quando processo_ativo é utilizável; failed_stage não decide o histórico
ERRO_HTTP_OU_TIMEOUT: error handler não grava histórico
DEDUP_POLICY: igualdade de numero_processo; remove ocorrência anterior e mantém uma única entrada
ORDER_POLICY: mais recente primeiro; consulta repetida move o processo para o início e renova data/resumo
EXEMPLO_A_B_A: [A] -> [B, A] -> [A, B]
LIMITE_ANTERIOR_E_FINAL: 3; quarto processo novo produz [D, A, B] quando o estado anterior é [A, B, C]
LOCAL_STORAGE_SERVICE_ALTERADO: SIM; somente deduplicação por recência no método salvar
SEPARACAO_STORAGES: histórico continua em localStorage; session_id continua em sessionStorage via ChatSessionService
RESET_SESSAO: clearSession inalterado e não apaga histórico
TYPECHECK_APP_BASELINE: PASS — runtime Node local + node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit; tentativa inicial com node no PATH não iniciou porque o executável não estava resolvível
TYPECHECK_APP_FINAL: PASS — runtime Node local + node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
BUILD: PASS — runtime Node local + node_modules/@angular/cli/bin/ng.js build; repetição fora do sandbox após spawn EPERM; warning CSS baseline de 1,42 kB
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos (Chat, LocalStorage, State e Chat); nenhuma falha nova
ARQUIVOS_MODIFICADOS_NO_ITEM: frontend/src/app/features/chat/chat.ts; frontend/src/app/core/services/local-storage.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
NAO_ANTECIPACAO: ChatService, ChatSessionService, StateService, DTOs, templates, CSS, healthcheck P3-007, metadata P3-008, specs e backend não modificados pelo item
REVISAO: buscas dirigidas e diff completo revisados; pergunta não é atribuída a numero_processo; sem regex, fallback, retry, debug ou segredo; git diff --check aprovado
RISCOS: testes automatizados específicos permanecem para P4-003; smoke integrado permanece posterior; histórico confia no processo_ativo do backend; ausência desse campo deliberadamente não cria entrada
COMMIT_SUGERIDO: fix(frontend): align process history with active process
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-007

```text
ID: INT-P3-007
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 09:46:54 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: worktree com alterações preexistentes de INT-P3-001..006 preservadas; nenhum arquivo staged
INDICADOR_ANTERIOR: texto hardcoded “Sistema disponível” e ponto sempre verde no cabeçalho; nenhum estado ou evidência HTTP
ESTADO_IMPLEMENTADO: ApiHealthStatus discriminado em verificando, disponivel e indisponivel; signal local iniciado em verificando
ENDPOINT: GET /api/health; URL relativa, sem host ou porta
TIPO_RESPONSE: ApiHealthResponse com status literal 'ok'; HttpClient.get<ApiHealthResponse>; nenhum any
MOMENTO_VERIFICACAO: uma vez em ngOnInit do ChatComponent, paralelamente ao restante da interface
SUCESSO: somente response.status === 'ok' define disponivel
FALHA: erro HTTP/transporte e payload incompatível definem indisponivel sem detalhes técnicos na UI
SEMANTICA_VISUAL: Verificando API... com ponto neutro; API disponível com ponto verde; API indisponível com ponto vermelho; texto não depende apenas de cor
SEPARACAO: health local e dedicado; ChatService, StateService.erro, carregando, ChatSessionService, LocalStorageService, mensagens e histórico não utilizados pelo healthcheck
REDE: sem localhost, proxy ou CORS; proxy real permanece para P5-001
POLLING_RETRY: ausentes; uma verificação por inicialização; nenhum timeout arbitrário novo
TYPECHECK_APP_INICIAL: primeira tentativa não iniciou porque node não estava no PATH; runtime Node do VS Code localizado
TYPECHECK_APP_FINAL: PASS — runtime Node v22.22.1 + node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
BUILD: PASS — runtime Node local + node_modules/@angular/cli/bin/ng.js build; tentativa no sandbox falhou com spawn EPERM e repetição autorizada fora do sandbox passou
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos (Chat, LocalStorage, State e Chat); nenhuma falha nova de health
ARQUIVOS_CRIADOS: frontend/src/app/core/services/api-health.ts
ARQUIVOS_MODIFICADOS_NO_ITEM: frontend/src/app/features/chat/chat.ts; frontend/src/app/features/chat/chat.html; frontend/src/app/features/chat/chat.css; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
NAO_ANTECIPACAO: backend, ChatService, StateService, SessionService, histórico, specs, manifestos, metadata P3-008, proxy e CORS não modificados pelo item
REVISAO: buscas dirigidas e diff completo revisados; sem polling, retry, diagnóstico profundo, debug, segredo ou falso estado disponível; git diff --check aprovado
RISCOS: healthcheck prova somente resposta contratual da fronteira FastAPI; não prova Ollama, Qdrant, RAG, agentes, banco ou chatbot integral; sem polling, representa a verificação inicial
COMMIT_SUGERIDO: feat(frontend): show API availability from healthcheck
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P3-008

```text
ID: INT-P3-008
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 10:55:30 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: worktree com alterações preexistentes de INT-P3-001..007 preservadas; nenhum arquivo staged
HTML_LANG_ANTERIOR: en
HTML_LANG_NOVO: pt-BR
DOCUMENT_TITLE_ANTERIOR: MeuPrimeiroApp
DOCUMENT_TITLE_NOVO: Chatbot Processual
TITLE_SOURCE: nome funcional existente em docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md e sustentado pelo backend FastAPI
TEXTO_TEMPLATE_GENERICO: My first Angular JS Project; signal sem consumidores em frontend/src/app/app.ts
ACAO_TEMPLATE: propriedade morta e import signal removidos; nenhum texto substituto inventado
WORKSPACE_NAME: meu-primeiro-app; preservado
PACKAGE_NAME: meu-primeiro-app; preservado
CLASSIFICACAO: lang/title = metadados visíveis; My first Angular JS Project = resíduo técnico de template sem função; meu-primeiro-app em package/angular/spec = identificador técnico ou teste histórico fora do escopo
TYPECHECK_APP_INICIAL: PASS — runtime Node v24.14.1 + node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_APP_FINAL: PASS — mesmo comando e runtime
BUILD: PASS — runtime Node local + node_modules/@angular/cli/bin/ng.js build; tentativa no sandbox falhou com spawn EPERM e repetição autorizada fora do sandbox passou; warning CSS preexistente de 1,54 kB acima do budget
HTML_GERADO: dist/meu-primeiro-app/browser/index.html contém lang="pt-BR" e title Chatbot Processual; artefato não versionado nem editado
SPECS_BASELINE: tsconfig.spec FAIL somente nos quatro imports antigos (Chat, LocalStorage, State e Chat); nenhuma falha nova; specs não corrigidas
BUSCA_FINAL: nenhuma ocorrência ativa de lang="en", MeuPrimeiroApp ou My first Angular JS Project no código fonte relevante
ARQUIVOS_MODIFICADOS_NO_ITEM: frontend/src/index.html; frontend/src/app/app.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
ESCOPO_PRESERVADO: package.json, package-lock.json, angular.json, workspace, diretórios, selectors, favicon, manifest/PWA, proxy, DTOs, sessão, ChatService, response real, erros, histórico, healthcheck, specs e backend não modificados pelo item
REVISAO: diff completo revisado; HTML gerado inspecionado; sem branding fictício, debug, segredo ou alteração fora do escopo; git diff --check aprovado
RISCOS: package/workspace e spec legado conservam meu-primeiro-app como identificador interno; favicon Angular não solicitado permanece; testes frontend completos ficam para P4; proxy fica para P5
COMMIT_SUGERIDO: fix(frontend): align application language and metadata
COMMIT_REAL: —
G3_FECHADO: NÃO
CHECKPOINT_P3: AINDA_NAO
```

### Registro detalhado — INT-P4-001

```text
ID: INT-P4-001
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
DATA_HORA: 24/08/2026 12:02:03 -03:00
BRANCH: feat/integra_chatbot_frontend
CHECKPOINT_P3_BASELINE: 5cd265a2334c34dded14cfda9bd668fc75fcaa53 feat(frontend): complete processual chatbot integration
STATUS_INICIAL: worktree limpo; nenhuma alteração nova ou preexistente após o checkpoint P3
NODE: v24.19.0; runtime real do pacote OpenJS.NodeJS.LTS usado por caminho absoluto
NPM: 11.17.0; npm-cli.js executado pelo mesmo runtime e diretório adicionado ao PATH dos subprocessos
BASELINE_TSC_APP: PASS
BASELINE_TSC_SPEC: FAIL — TS2305 em core/services/chat.spec.ts (Chat), core/services/local-storage.spec.ts (LocalStorage), core/services/state.spec.ts (State) e features/chat/chat.spec.ts (Chat)
BASELINE_TEST_RUNNER: primeira tentativa não iniciou por node fora do PATH; com PATH explícito, build do runner falhou no sandbox por spawn EPERM antes da coleta
IMPORTS_CORRIGIDOS: Chat -> ChatService; LocalStorage -> LocalStorageService; State -> StateService; Chat -> ChatComponent
APP_EXPECTATION: h1 “Hello, meu-primeiro-app” do scaffold removido; smoke atual verifica que App hospeda router-outlet
TESTBED_MOCKS: provideHttpClient no smoke do ChatService; ChatService, ChatSessionService, LocalStorageService e ApiHealthService mínimos no ChatComponent; healthcheck retorna Observable de { status: 'ok' }; scrollIntoView stubado e restaurado para jsdom
HTTP_REAL_USADO: NÃO
BACKEND_NECESSARIO: NÃO
NPM_CI: PASS fora do sandbox após spawn EPERM; 468 pacotes; 28 vulnerabilidades reportadas (3 low, 5 moderate, 19 high, 1 critical); npm audit fix não executado
TYPECHECK_APP_FINAL: PASS
TYPECHECK_SPEC_FINAL: PASS
TESTES: npm test -- --watch=false PASS; Vitest coletou 6 arquivos e executou 7 testes; 7 passaram, 0 falharam
BUILD: PASS
WARNINGS: budget CSS preexistente de chat.css excedido em 1,54 kB; npm ci reportou 28 vulnerabilidades e scripts pendentes de allowScripts
MANIFESTS: frontend/package.json e frontend/package-lock.json intactos; nenhuma dependência adicionada
ARQUIVOS_MODIFICADOS: frontend/src/app/app.spec.ts; frontend/src/app/core/services/chat.spec.ts; frontend/src/app/core/services/local-storage.spec.ts; frontend/src/app/core/services/state.spec.ts; frontend/src/app/features/chat/chat.spec.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
RESUMO_DIFF: specs antigas alinhadas às classes reais; expectativa obsoleta do App substituída por responsabilidade atual; providers/mocks mínimos adicionados somente para instanciação determinística
NAO_ANTECIPACAO: sem assertions de contrato HTTP P4-002; sem matriz funcional do componente P4-003; sem backend/navegador/proxy/smoke ou degradações P4-004/P4-005
REVISAO: diff completo revisado; imports antigos, expectativa do scaffold e specs desabilitadas ausentes; produção, backend, proxy e manifests intactos; sem aliases, dependências, debug ou segredos; git diff --check aprovado
RISCOS: cobertura HTTP detalhada permanece P4-002; comportamento completo do ChatComponent permanece P4-003; smoke integrado depende de P5/proxy antes de P4-004; degradações integradas permanecem P4-005
COMMIT_SUGERIDO: test(frontend): repair existing angular specs
COMMIT_REAL: —
CHECKPOINT_P4: AINDA_NAO
```

### Registro detalhado — INT-P4-002

```text
ID: INT-P4-002
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 11:36:10 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: sete arquivos modificados exclusivamente pelo checkpoint P4-001 preservados; nenhum arquivo staged
BASELINE_P4_001: PASS — tsconfig.app e tsconfig.spec aprovados; 6 arquivos/7 testes aprovados antes da nova cobertura
SPEC: frontend/src/app/core/services/chat.spec.ts
HTTP_TESTING: provideHttpClient + provideHttpClientTesting + HttpTestingController; verify após cada teste
SESSION_MOCK: stub mínimo tipado com Pick<ChatSessionService, 'getSessionId'>; null e sessao-123 controlados sem sessionStorage real
SEM_SESSAO: POST /api/processos/chat com body exato { mensagem: 'Olá' }; session_id ausente
COM_SESSAO: POST /api/processos/chat com session_id sessao-123 e mensagem integralmente preservados; nenhum ID gerado
RESPONSE: fixture explicitamente ProcessualChatHttpResponse; envelope completo emitido sem mapeamento
TIMEOUT: 135000 ms; timers virtuais do Vitest; ausência de erro em 134999 ms; TimeoutError após 135001 ms; request cancelada; nenhuma espera real
HTTP_ERROR: flush 500; HttpErrorResponse propagado com status 500; nenhum next, fallback, retry ou mensagem de UI
TYPECHECK_APP: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_SPEC: PASS — node node_modules/typescript/bin/tsc -p tsconfig.spec.json --noEmit
SPEC_FOCADA: PASS — 1 arquivo/5 testes aprovados
SUITE: PASS — 6 arquivos/11 testes aprovados; 11 passed, 0 failed
BUILD: PASS — warning CSS preexistente de chat.css, 1,54 kB acima do budget
MANIFESTS: frontend/package.json e frontend/package-lock.json intactos; nenhuma dependência adicionada
NPM_CI: não executado; node_modules existente, ambiente preservado e lockfile inalterado
ARQUIVOS_MODIFICADOS_NO_ITEM: frontend/src/app/core/services/chat.spec.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
PRODUCAO_BACKEND_PROXY: intactos; nenhum ChatComponent, healthcheck, histórico, navegador ou FastAPI testado
REVISAO: busca dirigida sem endpoint antigo ou any na fronteira; diff completo revisado; git diff --check aprovado; sem debug ou segredo
RISCOS: HttpClient simulado não prova conectividade FastAPI; proxy permanece P5; sessão no componente permanece P4-003/P4-004; deadline backend total de 120 s continua lacuna conhecida; smoke E2E é posterior
COMMIT_SUGERIDO: test(frontend): cover chat service http contract
COMMIT_REAL: —
CHECKPOINT_P4: AINDA_NAO
```

### Registro detalhado — INT-P4-003

```text
ID: INT-P4-003
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 12:07:00 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: sete arquivos modificados exclusivamente por P4-001/P4-002 preservados; nenhum arquivo staged
BASELINE_P4_001: VALIDATED — specs reparadas, typechecks e 7/7 testes aprovados
BASELINE_P4_002: VALIDATED — fronteira HTTP coberta por 5 testes; suíte anterior com 11/11 testes aprovados
TESTS_BEFORE: typechecks app/spec PASS; 6 arquivos/11 testes aprovados, 0 falharam
CHAT_COMPONENT_TESTS_BEFORE: 1 smoke de instanciação
SPEC: frontend/src/app/features/chat/chat.spec.ts
STATE_SERVICE: real e reinicializado pelo TestBed em cada teste
CHAT_SERVICE: double tipado; Subject para sucesso, erro e request pendente; nenhum HttpTestingController
SESSION_SERVICE: double tipado; setSessionId validado com response.session_id
LOCAL_STORAGE_SERVICE: doubles tipados de carregar/salvar; objeto persistido inspecionado por numero_processo
API_HEALTH_SERVICE: check mockado com of({ status: 'ok' }); nenhuma chamada real a /api/health
RESPONSE_FIXTURE: ProcessualChatHttpResponse tipada; resposta, session_id, processo_ativo e failed_stage controláveis; sem any
ENVIO: mensagem integral válida entregue uma vez ao ChatService e adicionada ao estado como user
BLOQUEIO_DUPLICADO: Subject pendente mantém loading true; segunda tentativa não aumenta call count; Subject sempre finalizado
SUCESSO: resultado.resposta vira mensagem bot e aparece no DOM; loading final false
SESSAO: response.session_id entregue uma vez a ChatSessionService.setSessionId
ERROS: TimeoutError, status 0, 422 e 500 cobertos com copies documentais; detalhe bruto ausente; sem bot fake, histórico ou retry
NOVA_TENTATIVA: erro anterior limpo, segunda chamada permitida e loading concluído após sucesso
HISTORICO: response.resultado.processo_ativo entregue como numero_processo; pergunta livre não persistida; null e erro não salvam
FALHA_CONTROLADA: failed_stage Agente 2 em response 2xx preserva resultado.resposta como bot e não preenche erro
SPEC_FOCADA: PASS — 1 arquivo/9 testes aprovados
TYPECHECK_APP: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_SPEC: PASS — node node_modules/typescript/bin/tsc -p tsconfig.spec.json --noEmit
TESTS_AFTER: PASS — 6 arquivos/19 testes aprovados; 19 passed, 0 failed
P4_003_TESTS: 9 passed, 0 failed
P4_002_REGRESSAO: NÃO — suíte completa verde
BUILD: PASS — warning CSS preexistente de chat.css, 1,54 kB acima do budget
MANIFESTS: frontend/package.json e frontend/package-lock.json intactos; nenhuma dependência adicionada
NPM_CI: não executado; node_modules válido e manifests inalterados
NPM_AUDIT_FIX: não executado
ARQUIVOS_MODIFICADOS_NO_ITEM: frontend/src/app/features/chat/chat.spec.ts; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
PRODUCAO_BACKEND_PROXY: intactos; sem endpoint/body, navegador, FastAPI, proxy ou E2E
REVISAO: diff completo revisado; busca dirigida sem responderMock, endpoint, HttpTestingController ou any no component spec; git diff --check aprovado; sem debug ou segredo
RISCOS: doubles não provam integração Angular→FastAPI; endpoint/body pertencem a P4-002; smoke de duas mensagens depende de P5-001; P4-004/P4-005 pendentes; deadline backend total de 120 s permanece dívida conhecida
COMMIT_SUGERIDO: test(frontend): cover chat component behavior
COMMIT_REAL: —
CHECKPOINT_P4: AINDA_NAO
```

### Registro detalhado — INT-P5-001

```text
ID: INT-P5-001
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 13:10:45 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: alterações preexistentes de P4 em checklist, controle e cinco specs preservadas; nenhum proxy existente; serve sem proxyConfig; npm start executava ng serve
PROXY_CONFIG: frontend/proxy.conf.json
PROXY_TARGET: http://localhost:8000
PROXY_PATH: /api preservado; sem pathRewrite
ANGULAR_SERVE: frontend/angular.json associa serve.options.proxyConfig a proxy.conf.json; npm start preservado
CHAT_URL: /api/processos/chat relativa e preservada
HEALTH_URL: /api/health relativa e preservada
FASTAPI_DIRETO: GET http://localhost:8000/api/health → 200 {"status":"ok"}
ANGULAR_PROXY: GET http://localhost:4200/api/health → 200 {"status":"ok"}
PROCESSOS_TEMPORARIOS: FastAPI PID 55564; Angular PID 51332; ambos encerrados; nenhum listener restante em 8000/4200; nenhum processo preexistente alterado
CONFIG_VALIDATION: angular.json e proxy.conf.json válidos; Angular CLI retornou proxy.conf.json para serve.options.proxyConfig
TYPECHECK_APP: PASS
TYPECHECK_SPEC: PASS
TESTES: PASS — 6 arquivos; 19/19 testes aprovados
BUILD: PASS — warning CSS preexistente de chat.css, 1,54 kB acima do budget
MANIFESTS: frontend/package.json e frontend/package-lock.json intactos; nenhuma dependência adicionada; npm install/npm audit fix não executados
CORS: não adicionado
PRODUCAO: não acoplada ao proxy de desenvolvimento
CODIGO_PRODUCAO: ChatService, ApiHealthService e ChatComponent intactos; nenhum localhost adicionado
BACKEND: intacto; apenas iniciado temporariamente pelo comando existente via uvicorn
ARQUIVOS_DO_ITEM: frontend/proxy.conf.json; frontend/angular.json; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
NAO_ANTECIPACAO: INT-P4-004, INT-P4-005 e INT-P5-002..004 inalterados
REVISAO: diff completo revisado; git diff --check aprovado; sem dependência, debug, segredo, CORS, pathRewrite ou alteração incidental de lockfile
RISCOS: warning CSS preexistente; runtime Node fora do PATH exigiu caminho absoluto; primeiras tentativas de coleta HTTP falharam por peculiaridades do PowerShell, sem falha dos serviços e com limpeza confirmada
COMMIT_SUGERIDO: chore(frontend): configure local api proxy
COMMIT_REAL: —
```

---

## Registro consolidado — FASE P7

```text
FASE: P7
DATA_HORA: 31/08/2026 09:40:10 -03:00
BRANCH: feat/integra_chatbot_frontend
HEAD: 87b9bfae312da8c7a4a065a54a6bb6a36ebd4d64
MERGE_TARGET_OR_BASE: main/origin/main
MERGE_BASE: cce475130a76babb224ff1425f38e775281b45fe
METHOD: branches locais/remotas apontam para a mesma base; git merge-base HEAD main e origin/main
WORKTREE_INICIAL: frontend/angular.json modificado; analytics UUID adicionado; origem não atribuída
STAGED_INICIAL: nenhum
UNTRACKED_INICIAL: nenhum listado; avisos de acesso negado em caches pytest ignorados
PRECONDITION_GAP: INT-P5-003 aparece IMPLEMENTED no item detalhado, embora tabelas posteriores o tratem como VALIDATED; G1-G4 permanecem TODO na tabela macro apesar dos itens validados
SUPPLEMENTAL_MANUAL_EVIDENCE: validação manual severa/adicional e avaliação da equipe informadas externamente; sem detalhes adicionais fabricados
RESULTADO: NOT_READY
G6: ABERTO
CHECKPOINT_P7_CRIADO: NÃO
COMMIT_EXECUTADO: NÃO
PUSH_EXECUTADO: NÃO
```

### Commits/checkpoints existentes

| Hash | Mensagem | Fase/IDs atribuíveis | Evidência |
|---|---|---|---|
| `ce728b9` | `chore(integration): establish P0 integration baseline` | P0 | mensagem e diff de governança/baseline |
| `024008a` | `ocs(integration): define Angular FastAPI network topology` | P1 | documentação de topologia/contrato |
| `6f7cddb` | `feat(api): strengthen chatbot HTTP boundary` | P2 | API, testes HTTP e documentação |
| `5cd265a` | `feat(frontend): complete processual chatbot integration` | P3 | DTOs, sessão, services e componente |
| `d007433` | `test(integracao): valida fluxo do chatbot e proxy local` | P4/P5-001 | specs, proxy e evidências de smoke |
| `7d414c4` | `docs(backend): document reproducible bootstrap` | P5-002/P5-003 | READMEs e registros de bootstrap |
| `fe454ee` | `docs(integration): document integrated local workflow` | P5-004 | documentação do workflow integrado |
| `87b9bfa` | `docs(project): align architecture development and frontend docs` | P6 | documentação final reconciliada |

Os commits `f814a06` a `c7bd377` pertencem à linhagem do backend anterior à
fase formal de integração e não foram artificialmente mapeados a IDs P0–P7.

### Registro detalhado — INT-P7-001

```text
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
PYTHON: 3.12.10
PYTEST: 9.1.1
FOCUSED_COMMAND: .venv/Scripts/python.exe -m pytest tests/test_api_processual_chat.py -q
FOCUSED_RESULT: 14 passed; 0 failed; 0 skipped; 1 PytestCacheWarning; 1,23 s
FULL_COMMAND: .venv/Scripts/python.exe -m pytest tests -q
FULL_RESULT: 43 passed; 0 failed; 0 skipped; 1 PytestCacheWarning; 2,61 s
BASELINE_OR_PREVIOUS_TOTAL: 43
FINAL_TOTAL: 43
DELTA: 0
BACKEND_REGRESSION: NÃO
```

### Registro detalhado — INT-P7-002

```text
STATUS_ANTERIOR: TODO
STATUS_FINAL: BLOCKED
NODE: 24.19.0
NPM: 11.17.0
MANIFEST_HASHES: package.json B2E747A3F63E93B70AD5DC63BE0D6D62BB90E7B97AA9807891FA9F3E7DCF1657; package-lock.json 75DBAB39C5ABF49BF0C84B14E73629344D20410873D4150E94984332CA34D030
NPM_CI: FAIL dentro e fora do sandbox; EPERM ao substituir esbuild.exe e node.napi.node
PROCESSOS_PREEXISTENTES: dois node.exe observados; não iniciados nem encerrados pelo gate
MANIFESTS_MODIFICADOS: NÃO
TSC_APP: NÃO EXECUTADO COM INTEGRIDADE; TypeScript ausente após npm ci parcial
TSC_SPEC: NÃO EXECUTADO COM INTEGRIDADE; TypeScript ausente após npm ci parcial
TESTS: NÃO EXECUTADOS
BUILD: NÃO EXECUTADO
FRONTEND_REGRESSION: INCONCLUSIVA
```

### Registro detalhado — INT-P7-003

```text
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
NO_ENV_REAL_TRACKED: SIM
NO_FRONTEND_SECRET: SIM
NO_PUBLIC_INTERNAL_PATH: SIM
CORS_POLICY_CORRECT: SIM; same-origin/proxy, sem middleware CORS
SESSION_ID_SAFE: SIM; UUID opaco quando gerado, sem PII e sem semântica de autenticação
NO_STACK_UI: SIM
RAG_PUBLIC_SURFACE_SAFE: SIM; fontes reduzidas a tipo/título/data/conteúdo
SECURITY_LEAK_KNOWN: NÃO
```

### Registro detalhado — INT-P7-004

```text
STATUS_ANTERIOR: TODO
STATUS_FINAL: IMPLEMENTED
FULL_DIFF_REVIEWED: SIM
GIT_DIFF_CHECK_PASS: SIM
AREAS: GOVERNANCE; DOCS; BACKEND; FRONTEND; TESTS; DEV_CONFIG
SIMULATOR_PRESERVED: SIM
NO_LOCAL_ARTIFACT_TRACKED: SIM
NO_DEBUG_RESIDUAL: SIM, sem ocorrência nova bloqueante em código ativo
SCOPE_CREEP: frontend/angular.json modificado no worktree com analytics UUID; origem não explicada
CRITERIO: pendente por worktree inexplicado
```

### Registro detalhado — INT-P7-005

```text
STATUS_ANTERIOR: TODO
STATUS_FINAL: BLOCKED
HEALTH_DIRECT: PASS; HTTP 200 em localhost:8000/api/health
HEALTH_PROXY: PASS; HTTP 200 em localhost:4200/api/health
FRONTEND_HTTP: PASS; HTTP 200 em localhost:4200
PROCESS_OWNERSHIP: serviços eram preexistentes e não foram iniciados pelo gate
BROWSER_FINAL: NÃO EXECUTADO
VALID_PROCESS: NÃO REPRODUZIDO EM P7
CONTEXTUAL_SECOND_MESSAGE: NÃO REPRODUZIDO EM P7
SECOND_CLIENT_ISOLATED: NÃO REPRODUZIDO EM P7
BACKEND_OFFLINE_RECOVERABLE: NÃO REPRODUZIDO; backend preexistente não foi encerrado
SUPPLEMENTAL_EVIDENCE: P4/P5 e validação manual/equipe preservadas, não usadas como substituto
```

### Gate — INT-P7-006

```text
ALL_BLOCKING_ITEMS_VALIDATED: NÃO
DEFERRED_ITEMS_JUSTIFIED: PARCIAL
BACKEND_TESTS_PASS: SIM
FRONTEND_TESTS_PASS: NÃO CONFIRMADO EM P7
FRONTEND_BUILD_PASS: NÃO CONFIRMADO EM P7
FINAL_SMOKE_PASS: NÃO
DIFF_REVIEWED: SIM
GIT_DIFF_CHECK_PASS: SIM
DOCUMENTATION_UPDATED: SIM, com resultado real P7
NO_SECRET_OR_LOCAL_ARTIFACT: SIM
COMMITS_LOGICAL: SIM
REAL_COMMIT_HASHES_RECORDED: SIM PARA CHECKPOINTS EXISTENTES; NÃO PARA P7, QUE NÃO POSSUI COMMIT
TECHNICAL_MERGE_READINESS: FAIL
FINAL_CHECKPOINT_REQUIRED: SIM
FINAL_GATE: NOT_READY
BLOCKERS: npm ci/regressão frontend; smoke final controlado; worktree inexplicado; precondition gaps documentais; checkpoint P7 ausente
```

### Registro detalhado — INT-P4-004

```text
ID: INT-P4-004
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 13:46:55 -03:00
BRANCH: feat/integra_chatbot_frontend
DEPENDENCIAS: INT-P4-001, INT-P4-002, INT-P4-003 e INT-P5-001 VALIDATED
PROCESSO_SMOKE: 0011000-82.1981.5.18.0051
FONTE_DO_PROCESSO: chatbot_processual_ai/data/sample_processes.json, fixture sintética oficial também referenciada nos testes HTTP
MOTIVO_DE_SER_VALIDO: entrada determinística da base local, com cinco movimentações e última movimentação conhecida
PERGUNTA_1: Consulte o processo 0011000-82.1981.5.18.0051
PERGUNTA_2: Qual foi a última movimentação?
DEPENDENCIAS_EXTERNAS: Ollama não necessário; Qdrant não necessário; SQLite/base local necessária e usada pelo fluxo normal; nenhum serviço adicional iniciado
BACKEND_COMMAND: .venv/Scripts/python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
FRONTEND_COMMAND: runtime Node LTS local + node_modules/@angular/cli/bin/ng.js serve --host 127.0.0.1 --port 4200, usando serve.options.proxyConfig de P5-001
HEALTH_DIRETO: PASS — GET http://127.0.0.1:8000/api/health → 200 {"status":"ok"}
HEALTH_PROXY: PASS — GET http://127.0.0.1:4200/api/health → 200 {"status":"ok"}
BROWSER: Microsoft Edge real em modo headless, automatizado pelo Playwright já instalado; nenhuma dependência adicionada
REQUEST_1: POST http://127.0.0.1:4200/api/processos/chat → 200; request inicial sem session_id
RESPONSE_1: session S1 presente; processo_ativo=0011000-82.1981.5.18.0051; failed_stage=null; rag_status=not_needed; resposta utilizável
UI_1: resposta real exibida e equivalente a resultado.resposta após normalização visual de whitespace; loading observado e encerrado; sem erro visual
SESSION: valor bruto não registrado; response 1 S1 = sessionStorage S1 = request 2 S1 = response 2 S1
REQUEST_2: POST http://127.0.0.1:4200/api/processos/chat → 200; mensagem contextual exata, sem número; session_id=S1
RESPONSE_2: session S1; processo_ativo=0011000-82.1981.5.18.0051; failed_stage=null; rag_status=not_needed; resposta informa Arquivado definitivamente em 05/02/1984
UI_2: resposta real exibida e equivalente a resultado.resposta após normalização visual de whitespace; loading observado e encerrado; sem erro visual
HISTORICO_1: [0011000-82.1981.5.18.0051]
HISTORICO_2: [0011000-82.1981.5.18.0051]; pergunta livre ausente; uma ocorrência do processo; sem duplicata indevida
CONSOLE: zero erros relevantes; zero warnings relevantes
NETWORK: /api/health e dois /api/processos/chat aprovados; zero 404, 5xx, CORS, connection refused ou request cancelada durante o cenário validado
PREFLIGHT_BACKEND: .venv/Scripts/python.exe -m pytest tests -q → 43 passed; um PytestCacheWarning ambiental de acesso negado ao cache
PREFLIGHT_FRONTEND: tsconfig.app PASS; tsconfig.spec PASS; 6 arquivos/19 testes PASS; build PASS; warning CSS preexistente de 1,54 kB acima do budget
TENTATIVAS_PREVIAS: inicialização relativa do Python não subiu FastAPI e gerou ECONNREFUSED antes do cenário; primeira coleta de browser teve conversão de Unicode e foi descartada; execução final acima foi limpa e integral
ARQUIVOS_DO_ITEM: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
CODIGO_PRODUCAO: inalterado
SPECS_BACKEND_PROXY_MANIFESTS: inalterados
PROCESSOS_TEMPORARIOS: FastAPI PID 54588 e Angular PID 54256 iniciados pelo item e encerrados; portas 8000/4200 liberadas; nenhum processo preexistente alterado
NAO_ANTECIPACAO: INT-P4-005 e INT-P5-002 inalterados
RISCOS: smoke prova apenas o cenário escolhido; sessão continua em memória e sem persistência distribuída; P4-005 cobrirá degradações/lifecycle; deadline backend total de 120 s continua dívida conhecida
COMMIT_SUGERIDO: test(integration): record two-message browser smoke
COMMIT_REAL: —
```

### Registro detalhado — INT-P4-005

```text
ID: INT-P4-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 14:29:55 -03:00
BRANCH: feat/integra_chatbot_frontend
DEPENDENCIAS: INT-P4-001, INT-P4-002, INT-P4-003, INT-P4-004 e INT-P5-001 VALIDATED
MATRIZ: BACKEND_UNAVAILABLE | REAL_BROWSER | FastAPI ausente com Angular/proxy ativo | PASS | proxy 500/ECONNREFUSED; copy segura; zero bot; loading finalizado; sessão e histórico preservados; tentativa manual 200 após retorno
MATRIZ: TIMEOUT | AUTOMATED_SERVICE_TEST + AUTOMATED_COMPONENT_TEST | request ultrapassa 135000 ms por timers virtuais e TimeoutError no componente | PASS | request cancelada; copy documental; loading finalizado; sem bot/histórico/retry
MATRIZ: MISSING_CONTEXT_OR_PROCESS | REAL_BROWSER | sessão limpa + "Qual foi a última movimentação?" | PASS | HTTP 200; processo_ativo=null; resposta segura; histórico ausente; novo session_id
MATRIZ: RAG_UNAVAILABLE | REAL_BROWSER + AUTOMATED_BACKEND_TEST | processo ativo + "O que a sentença decidiu?" com RAG desabilitado no fluxo normal | PASS | HTTP 200; rag_status=unavailable; failed_stage=null; resposta exibida; sem erro UI; loading finalizado; sessão preservada
MATRIZ: FAILED_STAGE | AUTOMATED_BACKEND_TEST + AUTOMATED_COMPONENT_TEST | exceção controlada no Agente 1 e fixture 2xx no componente | PASS | HTTP 200; mensagem segura; marcador técnico ausente; response tratada como bot normal; sem erro artificial
MATRIZ: REFRESH | REAL_BROWSER | reload da mesma aba com processo ativo e backend preservado | PASS | sessionStorage antes=depois=response; pergunta contextual reutilizou processo ativo; mensagens visuais anteriores não foram exigidas
MATRIZ: NEW_SESSION_OR_TAB | REAL_BROWSER | nova página independente na mesma origem, sem opener | PASS | session inicial ausente; novo ID diferente; contexto backend não compartilhado; localStorage compartilhado classificado separadamente
BACKEND_UNAVAILABLE_PUBLIC_MESSAGE: Não foi possível concluir a solicitação.
BACKEND_UNAVAILABLE_NETWORK: proxy retornou 500 para /api/health e /api/processos/chat; log confirmou ECONNREFUSED; sem CORS, 404, loop ou exception Angular
BACKEND_RECOVERY: retry manual retornou 200, limpou o erro anterior e reutilizou p4-005-preserved-session sem limpar storage
TIMEOUT_PUBLIC_MESSAGE: A solicitação demorou mais que o esperado. Tente novamente.
TIMEOUT_REAL_135S_WAIT: NÃO; política real validada deterministicamente com timers virtuais
MISSING_CONTEXT: HTTP 200; collection_status=not_needed; processo_ativo=null; resposta solicitou número completo; sem histórico ou falso processo
RAG_UNAVAILABLE: HTTP 200; resultado.resposta utilizável; StateService.erro não acionado; chat estruturado e sessão válidos
FAILED_STAGE: teste HTTP focado confirmou failed_stage=Agente 1 e ausência de segredo/stack/path; spec do componente confirmou resultado.resposta no bot e erro nulo
REFRESH: sessionStorage sobreviveu ao reload; backend in-memory permaneceu ativo; contexto processual foi reutilizado
NEW_TAB: context.new_page independente, window.opener=false; sessionStorage inicial ausente; primeiro request gerou ID diferente; localStorage da origem estava compartilhado
SESSION_STATE: por aba; preservado em erro e refresh; independente na nova aba sem opener
HISTORY_STATE: localStorage compartilhado por origem; inalterado no erro; pergunta sem processo não persistida
CONSOLE_REDE: dois erros esperados de resource 500 no cenário offline (/api/health e /api/processos/chat); zero erros inesperados, CORS, 404, loops ou page errors
PREFLIGHT_BACKEND: .venv/Scripts/python.exe -m pytest tests -q → 43 passed; PytestCacheWarning ambiental de acesso negado ao cache
PREFLIGHT_TSC_APP: PASS
PREFLIGHT_TSC_SPEC: PASS
PREFLIGHT_FRONTEND: npm test -- --watch=false → 6 arquivos/19 testes passed
PREFLIGHT_BUILD: PASS; warning CSS preexistente de chat.css 1,54 kB acima do budget
TESTE_FOCADO_BACKEND: 2 passed — failed_stage HTTP seguro e RAG unavailable por falha de embedding
BROWSER: Microsoft Edge real headless automatizado por Playwright já instalado; nenhuma dependência adicionada
PROCESSOS_TEMPORARIOS: Angular e FastAPI iniciados pelo item e encerrados; portas 4200/8000 liberadas; nenhum processo preexistente alterado
ARQUIVOS_DO_ITEM: docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
SPECS_PRODUCAO_BACKEND_PROXY_MANIFESTS: inalterados
MOCK_FALSE_SUCCESS_LOADING_TECH_DETAILS: nenhum mock, falso sucesso, loading permanente ou detalhe técnico exposto
SESSION_HISTORY_CORRUPTION: não observada
AUTOMATIC_RETRY: não adicionado; recuperação exclusivamente manual
NAO_ANTECIPACAO: INT-P5-002 e demais itens inalterados; nenhum checkpoint criado
RISCOS: _SESSIONS continua em memória do processo Python; refresh não equivale a restart backend; aba com opener pode copiar inicialmente sessionStorage e não foi usada; healthcheck prova somente FastAPI; deadline backend total de 120 s continua dívida conhecida
COMMIT_SUGERIDO: test(integration): validate degradation and session lifecycle
COMMIT_REAL: —
CHECKPOINT_P4: AINDA_NAO
```

### Registro detalhado — INT-P5-002

```text
ID: INT-P5-002
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 25/08/2026 15:36:47 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: worktree limpo; avisos de acesso negado somente em caches pytest fora do escopo; frontend/README.md e frontend/.gitignore inexistentes
CHECKPOINT_P4_BASELINE: d007433 — test(integracao): valida fluxo do chatbot e proxy local; HEAD real no início do item
P5_001: VALIDATED; proxy /api versionado em proxy.conf.json e associado a serve.options.proxyConfig
NODE_OBSERVADO: v24.19.0; runtime Node LTS local já validado, fora do PATH desta sessão
NPM_OBSERVADO: 11.17.0; package.json declara packageManager npm@11.11.1 e não possui engines
POLITICA_VERSAO: Node.js 24.x com npm 11.x recomendado; validado com Node.js 24.19.0/npm 11.17.0; versões locais não declaradas como únicas compatíveis
FUNDAMENTO_VERSAO: Angular 21.2.x do lockfile aceita Node ^20.19.0, ^22.12.0 ou linha 24 compatível; execução real pós-npm ci aprovada com Node 24.19.0/npm 11.17.0
ANGULAR: @angular/core 21.2.6; @angular/cli 21.2.5; @angular/build 21.2.5
TYPESCRIPT: 5.9.3
SCRIPTS: start=ng serve; test=ng test; build=ng build; watch=ng build --watch --configuration development
MANIFESTS_ANTES: package.json SHA-256 B2E747A3F63E93B70AD5DC63BE0D6D62BB90E7B97AA9807891FA9F3E7DCF1657; package-lock.json SHA-256 75DBAB39C5ABF49BF0C84B14E73629344D20410873D4150E94984332CA34D030
NPM_CI: PASS fora do sandbox após spawn EPERM ambiental; 468 pacotes adicionados, 469 auditados em 51,257 s
NPM_CI_WARNINGS: 109 pacotes buscando funding; 4 scripts pendentes de allowScripts (@parcel/watcher, esbuild, lmdb e msgpackr-extract)
AUDIT_REPORT: 28 vulnerabilidades — 3 low, 5 moderate, 19 high e 1 critical; npm audit fix não executado
MANIFESTS_DEPOIS: hashes idênticos aos anteriores; git diff vazio para package.json e package-lock.json
TYPECHECK_APP: PASS — node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit
TYPECHECK_SPEC: PASS — node node_modules/typescript/bin/tsc -p tsconfig.spec.json --noEmit
TESTES: PASS — npm test -- --watch=false; 6 arquivos, 19/19 testes, 0 falhas
BUILD: PASS — npm run build; output dist/meu-primeiro-app; warning CSS preexistente de chat.css 1,54 kB acima do budget
NPM_START: PASS — npm start executou ng serve; listener Angular em localhost:4200; GET / retornou HTTP 200 com 459 bytes
PROCESSOS_TEMPORARIOS: tentativas destacadas com EPIPE foram limpas; execução em primeiro plano criou listener PID 34616, confirmado como ng.js serve e encerrado; porta 4200 livre ao final
PROXY: angular.json preservado com serve.options.proxyConfig=proxy.conf.json; proxy.conf.json preservado com /api → http://localhost:8000
BACKEND_NECESSARIO_PARA_START: NÃO; necessário somente ao efetuar chamadas /api
URL_API: produção usa caminhos relativos /api/health e /api/processos/chat; nenhuma ocorrência de localhost:8000 ou 127.0.0.1:8000 em frontend/src
NODE_MODULES: existe localmente após npm ci; não rastreado; ignorado pela regra node_modules/ do .gitignore raiz
ANGULAR_CACHE: existe localmente após validações; frontend/.angular não rastreado; ignorado pela regra .angular/ do .gitignore raiz
DOCUMENTACAO: frontend/README.md criado com seção operacional curta de pré-requisito, npm ci, npm start, teste sem watch, build, proxy relativo e política de artefatos locais
TRANSPORTE: README proíbe versionar, copiar de outra máquina, enviar por ZIP ou reutilizar node_modules/.angular/cache entre sistemas operacionais
ARQUIVOS_DO_ITEM: frontend/README.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
ESCOPO_PRESERVADO: package.json, package-lock.json, angular.json, proxy.conf.json, código de produção, specs, backend, simulador e docs/development.md intactos
NAO_ANTECIPACAO: INT-P5-003, INT-P5-004, INT-P6-002 e INT-P6-006 inalterados; nenhum setup backend, workflow integrado ou reescrita completa do README
REVISAO: diff completo revisado; artefatos locais não rastreados; sem dependência, caminho absoluto no README, debug, segredo, mudança de URL ou alteração incidental de manifest
RISCOS: versões validadas no ambiente atual não são as únicas compatíveis; instalação pode exigir registry npm; 28 vulnerabilidades permanecem como baseline; runtime do executor fora do PATH; warning CSS preexistente; backend só é necessário em chamadas /api
COMMIT_SUGERIDO: docs(frontend): document reproducible bootstrap
COMMIT_REAL: —
CHECKPOINT_P5: AINDA_NAO
```

### Registro detalhado — INT-P5-003

```text
ID: INT-P5-003
STATUS_ANTERIOR: TODO
STATUS_FINAL: IMPLEMENTED
DATA_HORA: 26/08/2026 09:15:09 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: alterações preexistentes de P5-002 no controle/checklist e frontend/README.md preservadas; caches pytest com acesso negado preexistentes
CHECKPOINT_P4: d007433 — test(integracao): valida fluxo do chatbot e proxy local
P5_001: VALIDATED
P5_002: VALIDATED; evidência local no controle, checklist e frontend/README.md
PYTHON_OBSERVADO: 3.12.10
PYTHON_EXECUTOR: python e py; ambos 3.12.10
POLITICA_PYTHON: versão observada, sem restrição formal criada
REQUIREMENTS: requests, python-dotenv, rich, psutil, fastapi e uvicorn; arquivo intacto
VENV_LIMPO: C:\Users\filipe.duarte\AppData\Local\Temp\int-p5-003-clean-validation; criado exclusivamente para o item
CRIACAO_VENV: python -m venv <TEMP_VENV>; primeira tentativa sofreu PermissionError ambiental no TEMP do sandbox; repetição fora do sandbox PASS
INTERPRETER_VALIDACAO: <TEMP_VENV>\Scripts\python.exe; Python 3.12.10; pip 25.0.1
PIP_INSTALL: <TEMP_VENV_PYTHON> -m pip install -r requirements.txt; PASS; nenhum conflito; aviso apenas de pip 26.2.1 disponível
FASTAPI: 0.141.1; disponível no venv limpo
UVICORN: 0.52.4; disponível no venv limpo
PYTEST: não declarado e indisponível no venv limpo
DEPENDENCIA_EXTRA_INSTALADA: NÃO
REQUIREMENTS_SUFFICIENT: NÃO para executar a suíte oficial; SIM para importar/subir API e healthcheck
MISSING_PACKAGE: pytest
COMMAND_BLOCKED: <TEMP_VENV_PYTHON> -m pytest tests -q → No module named pytest
ENV_EXAMPLE: rastreado; contém defaults locais não secretos para Ollama, SQLite e RAG/Qdrant
ENV_REAL: preexistente, ignorado e não rastreado; não lido nem sobrescrito
ENV_EXAMPLE_GAP: SIM; AGENT4_USE_OLLAMA é chave opcional com default desabilitado e não consta no exemplo; não impede import/start/health
DEPENDENCIAS_EXTERNAS: health sem Ollama/Qdrant; chat básico e consulta estruturada possuem caminhos locais; Ollama é condicional para interpretação/redação; RAG completo usa Ollama embeddings e Qdrant, com degradação registrada; metas atuais são locais
API_IMPORT_REQUIRES_EXTERNAL_SERVICE: NÃO
UVICORN: <TEMP_VENV_PYTHON> -m uvicorn api:app --host 127.0.0.1 --port 8000; PASS; processo temporário encerrado; porta livre ao final
HEALTH: GET http://127.0.0.1:8000/api/health → HTTP 200; {"status":"ok"}; sem Ollama/Qdrant
DIRETORIO_OFICIAL: chatbot_processual_ai
COMANDO_OFICIAL_TESTES: python -m pytest tests -q
TESTE_VENV_LIMPO: FAIL antes da coleta; pytest ausente
REGRESSAO_VENV_ANTERIOR: 43 passed, 1 PytestCacheWarning ambiental, 2,06 s
EXECUCAO_RAIZ: FAIL na coleta; 3 ModuleNotFoundError para api, main e ollama_client; premissa atual confirmada; nenhum PYTHONPATH hack
DOCUMENTACAO: chatbot_processual_ai/README.md criado; bootstrap, env, matriz externa, uvicorn, health, testes e limitação do requirements
ARTEFATOS: .venv/.env/__pycache__/.pytest_cache não rastreados; .env.example rastreado; novos caches com acesso negado não foram adicionados
ARQUIVOS_DO_ITEM: chatbot_processual_ai/README.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
ESCOPO_PRESERVADO: código Python, testes, requirements, .env.example, frontend, simulador e docs de P6 inalterados
RISCO: bootstrap ainda não executa testes somente com dependências versionadas; requisitos sem versões fixadas podem resolver versões diferentes; sessão backend permanece em memória; deadline total de 120 s continua dívida conhecida
COMMIT_SUGERIDO: docs(backend): document reproducible bootstrap
COMMIT_REAL: —
CHECKPOINT_P5: AINDA_NAO
```

### Registro detalhado — INT-P5-004

```text
ID: INT-P5-004
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
DATA_HORA: 26/08/2026 10:40:13 -03:00
BRANCH: feat/integra_chatbot_frontend
STATUS_INICIAL: controle possuía alteração preexistente promovendo P5-003 para VALIDATED; checklist e registro detalhado de P5-003 ainda dizem IMPLEMENTED; divergência preservada e não reaberta
P5_001: VALIDATED
P5_002: VALIDATED
P5_003: VALIDATED conforme premissa do item e tabela de controle; divergência documental residual descrita acima
FRONTEND_INSTALL: cd frontend; npm ci
FRONTEND_START: cd frontend; npm start
FRONTEND_TEST: cd frontend; npm test -- --watch=false
FRONTEND_BUILD: cd frontend; npm run build
BACKEND_VENV: cd chatbot_processual_ai; python -m venv .venv; ativação por .\.venv\Scripts\Activate.ps1 ou source .venv/bin/activate
BACKEND_INSTALL: python -m pip install -r requirements.txt
BACKEND_START: python -m uvicorn api:app --reload
BACKEND_TEST: python -m pytest tests -q; pytest ausente em requirements permanece limitação conhecida de P5-003
HEALTH_DIRETO: GET http://localhost:8000/api/health
HEALTH_PROXY: GET http://localhost:4200/api/health
DEPENDENCIAS_EXTERNAS: SQLite local sem servidor; Ollama condicional para geração; Ollama e Qdrant necessários para RAG completo; nenhuma necessária para health
OLLAMA_STARTED: NÃO
QDRANT_STARTED: NÃO
OTHER_STARTED: NÃO
SCRIPT_INTEGRADO_NECESSARIO: NÃO
SCRIPT_CRIADO: NÃO
MOTIVO_SCRIPT: rotina cabe em dois terminais e sete passos; script adicionaria lifecycle de processos e reduziria transparência para dependências condicionais
DOCUMENTACAO: seção Desenvolvimento local integrado adicionada a docs/integration.md; bootstraps referenciados sem duplicação
ORDEM: dependências condicionais; backend; health direto; frontend; health proxy; browser/chat; Ctrl+C
BACKEND_VALIDACAO: PASS — .venv\Scripts\python.exe -m uvicorn api:app --reload; PIDs 54320/48876
HEALTH_DIRETO_RESULTADO: PASS — HTTP 200; {"status":"ok"}
FRONTEND_VALIDACAO: PASS — npm start; ng serve compilou em 1,661 s; PIDs temporários 61896/65368/22348 e 56836/37704/55808/54632 entre tentativas do harness
HEALTH_PROXY_RESULTADO: PASS — HTTP 200; {"status":"ok"}
BROWSER_URL: http://localhost:4200
PAGINA_RESULTADO: PASS — HTTP 200
CHAT_SMOKE: NÃO repetido; evidência funcional anterior INT-P4-004 preservada
PROCESSOS_ENCERRADOS: todos os PIDs identificados foram finalizados; nenhum processo preexistente foi alterado
LIMPEZA_AMBIENTAL: porta 4200 livre; Windows continuou reportando listener 8000 associado ao PID 48876 já inexistente após Stop-Process/tasklist, registrado sem nova ação destrutiva
REDE: frontend preserva /api relativo; proxy /api para localhost:8000; FastAPI localhost:8000; CORS local desnecessário; nenhuma URL hardcoded adicionada
ARQUIVOS_DO_ITEM: docs/integration.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
CODIGO_FRONTEND_BACKEND: inalterado
SPECS_MANIFESTS_DOCKER_COMPOSE: inalterados; nenhuma dependência adicionada
NAO_ANTECIPACAO: P6-001..006 não iniciados; docs/development.md apenas inspecionado
REVISAO: diff completo revisado; git diff --check aprovado; sem debug, segredo, script, CORS, dependência ou alteração funcional
RISCOS: workflow pressupõe bootstraps P5-002/P5-003; Ollama/Qdrant condicionais; health prova somente FastAPI; sessão em memória; não representa produção; produção prefere mesma origem; documentação ampla pertence a P6; deadline backend total de 120 s continua dívida; divergência documental residual de P5-003
COMMIT_SUGERIDO: docs(integration): document integrated local workflow
COMMIT_REAL: —
CHECKPOINT_P5: AINDA_NAO
```

## 7. Modelo de atualização após cada item

Copiar e preencher:

```text
ID: INT-PX-XXX
STATUS_ANTERIOR:
STATUS_FINAL:
DIAGNOSTICO_CONFIRMADO:
ARQUIVOS_MODIFICADOS:
RESUMO_DIFF:
TESTES_EXECUTADOS:
RESULTADOS:
DOCUMENTACAO_ATUALIZADA:
RISCOS_RESIDUAIS:
COMMIT_SUGERIDO:
COMMIT_REAL:
OBSERVACOES:
```

---

## 8. Modelo de registro de commit

```text
COMMIT_ID_LOGICO: CXX
COMMIT_SUGERIDO: tipo(escopo): descrição
COMMIT_REAL: <hash ou PENDING>
IDS_COBERTOS:
ARQUIVOS_PRINCIPAIS:
TESTES_ANTES_DO_COMMIT:
RESULTADO:
DIFF_REVISADO: sim/não
GIT_DIFF_CHECK: pass/fail/não executado
SEGREDOS_VERIFICADOS: sim/não
RISCO_RESIDUAL:
```

---

## 9. Matriz de prontidão atual

| Dimensão | Estado | Bloqueio principal |
|---|---|---|
| Arquitetura | 🟢 Documentada | Angular/FastAPI, fronteira HTTP, sessão, rede e domínios reconciliados em P6 |
| Contrato HTTP | 🟢 Alinhado | `POST /api/processos/chat` e envelope tipado documentados e implementados |
| Sessão | 🟡 Local | UUID opaco; `_SESSIONS` em memória, sem autenticação ou persistência distribuída |
| Backend | 🟢 Base funcional | testes HTTP e regressão registrados nas fases anteriores |
| Frontend | 🟢 Integrado | resposta real, sessão, histórico, health e erros cobertos |
| Testes integrados | 🟢 Executados | smoke navegador→Angular→FastAPI registrado em P5 |
| Desenvolvimento local | 🟢 Documentado | bootstraps e fluxo conjunto/proxy consolidados; pytest ausente de requirements permanece dívida |
| Documentação | 🟢 Validada | P6-001..006 e auditoria cruzada aprovados |
| Governança Codex | 🟡 Boa base | verificar versionamento de `.codex/rules/safety.rules` |
| Segurança da integração | 🟡 A validar em P7 | sessão local, CORS same-origin e erros documentados; revisão final pertence a P7 |
| Merge | 🔴 `NOT_READY` | G6 e fechamento P7 ainda abertos |

---

## 10. Critério de mudança do estado global

### `NOT_READY`

Use enquanto houver qualquer bloqueio estrutural de contrato, sessão, build/teste ou smoke integrado.

### `INTEGRATION_READY`

Pode ser usado quando:

- contrato está validado;
- backend e frontend estão integrados;
- testes de ambos passam;
- smoke principal passa;
- ainda resta somente documentação/limpeza não bloqueante explicitamente registrada.

### `READY_FOR_MERGE`

Somente quando:

- checklist bloqueante está `VALIDATED`;
- regressões passaram;
- segurança foi revisada;
- documentação final está coerente;
- diff foi revisado e `git diff --check` passou;
- commits reais estão registrados neste controle;
- riscos adiados foram explicitamente aceitos.

---

## 11. Registro histórico do próximo passo a partir do baseline

O bloco abaixo registra a recomendação original do baseline e não representa o
estado operacional atual depois de P0–P6.

**Não iniciar alterando `ChatService` ainda.**

Ordem imediata recomendada:

1. `INT-P0-001` — confirmar branch/worktree local;
2. `INT-P0-002` — auditar o que está realmente rastreado;
3. `INT-P0-003` — garantir que a política Codex compartilhada possa ser versionada;
4. `INT-P0-004` — repetir baseline no ambiente local limpo;
5. `INT-P1-001` a `INT-P1-006` — fechar arquitetura/contrato/sessão/erro/timeout/rede;
6. somente então começar mudanças de backend/frontend.

Isso mantém a integração reversível e impede que decisões arquiteturais sejam tomadas incidentalmente por um patch de código.

---

## Registro consolidado — FASE P6

```text
FASE: P6
DOCUMENTOS_AUDITADOS: README.md; frontend/README.md; chatbot_processual_ai/README.md; docs/ARCHITECTURE.md; docs/integration.md; docs/development.md; docs/orchestration.md; docs/design_philosophy.md; checklist e controle; código/config/testes relevantes de frontend e backend
DOCUMENTOS_ALTERADOS: README.md; frontend/README.md; docs/ARCHITECTURE.md; docs/integration.md; docs/development.md; docs/orchestration.md; docs/design_philosophy.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_FRONTEND.md
CROSS_DOC_AUDIT: PASS — endpoint, sessão, histórico, health, proxy, CORS, erros, RAG, dependências, timeout, testes e fronteira do simulador coerentes
RESULTADO: INT-P6-001..006 VALIDATED
G5_READY: SIM
G5: VALIDATED
CHECKPOINT_P6_READY: SIM
CHECKPOINT_P6_CRIADO: NÃO
P7_STARTED: NÃO
COMMIT_REAL: —
```

### Evidência por item

```text
ID: INT-P6-001
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: docs/ARCHITECTURE.md
CONTEUDO_COBERTO: Angular/FastAPI; HTTP; chat/health; sessão; processo ativo; proxy/same-origin; encapsulamento; chat/metas/híbrido; limitações
FONTES_FACTUAIS: api.py; contratos; serviços Angular; angular.json; proxy.conf.json; orquestradores; testes; P5
CONTRADICOES_REMOVIDAS: frontend pendente; /api/chat; arquitetura sem Angular
LIMITACOES_PRESERVADAS: _SESSIONS em memória; health mínimo; deadline backend ausente; produção indefinida
VALIDACAO: critério individual e auditoria cruzada PASS
COMMIT_REAL: —

ID: INT-P6-002
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: docs/development.md
CONTEUDO_COBERTO: pré-requisitos; bootstrap; start; test/build/typecheck; env; rede; Git; ignores; troubleshooting
FONTES_FACTUAIS: package.json; angular.json; proxy.conf.json; requirements.txt; .env.example; READMEs P5; controle de validações
CONTRADICOES_REMOVIDAS: frontend /api/chat; proxy pendente; bootstrap que ocultava lacuna de pytest
LIMITACOES_PRESERVADAS: pytest ausente de requirements; imports exigem diretório backend; dependências condicionais
VALIDACAO: comandos conferidos contra manifests/configuração e auditoria cruzada PASS
COMMIT_REAL: —

ID: INT-P6-003
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: docs/orchestration.md
CONTEUDO_COBERTO: Browser→API→orquestrador→agentes/services→response; sessão; processo ativo; falhas; RAG; fronteiras
FONTES_FACTUAIS: ChatComponent; ChatService; api.py; processual_chat_orchestrator.py; session_state.py; services
CONTRADICOES_REMOVIDAS: fluxo sem frontend integrado e referências a decisões ainda futuras
LIMITACOES_PRESERVADAS: RAG condicional; sessão volátil; metas provisórias
VALIDACAO: critério individual e auditoria cruzada PASS
COMMIT_REAL: —

ID: INT-P6-004
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: docs/design_philosophy.md
CONTEUDO_COBERTO: determinismo; papel da LLM; estado real; falha explícita; contratos; mudanças focadas; proteção de detalhes
FONTES_FACTUAIS: orquestrador; agentes; contratos; UI integrada; regras de metas; AGENTS.md
CONTRADICOES_REMOVIDAS: princípios que tratavam a integração atual como pendente
LIMITACOES_PRESERVADAS: resultados provisórios e planejamento não descrito como implementação
VALIDACAO: princípios ligados ao repositório e auditoria cruzada PASS
COMMIT_REAL: —

ID: INT-P6-005
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: README.md
CONTEUDO_COBERTO: finalidade; estrutura; Angular/FastAPI; começo rápido; docs; fronteiras e limites
FONTES_FACTUAIS: documentação reconciliada; código/configuração; validações P5
CONTRADICOES_REMOVIDAS: frontend em integração; /api/chat; componentes históricos como arquitetura vigente
LIMITACOES_PRESERVADAS: metas não homologadas; sessão local; deadline; produção; pytest
VALIDACAO: porta de entrada atual e auditoria de termos PASS
COMMIT_REAL: —

ID: INT-P6-006
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
ARQUIVO_PRINCIPAL: frontend/README.md
CONTEUDO_COBERTO: finalidade; API/proxy; npm ci/start/test/build/typecheck; sessão; histórico; health; erros
FONTES_FACTUAIS: package.json; angular.json; proxy.conf.json; ChatService; ChatSessionService; ApiHealthService; ChatComponent; LocalStorageService
CONTRADICOES_REMOVIDAS: README de bootstrap genérico e ausência de comportamento integrado
LIMITACOES_PRESERVADAS: health mínimo; storage por aba; restart backend; proxy dev-only
VALIDACAO: README específico e auditoria cruzada PASS
COMMIT_REAL: —
```
