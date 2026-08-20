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
| G5 | Documentação | `TODO` | docs/README refletem implementação final |
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
| INT-P1-001 | `TODO` | C02 | `docs/ARCHITECTURE.md` ou doc de integração | fronteira Angular↔FastAPI documentada | — |
| INT-P1-002 | `TODO` | C02 | docs + schemas/DTOs posteriormente | exemplos request/response aprovados | — |
| INT-P1-003 | `TODO` | C02 | docs | política de sessão aprovada | — |
| INT-P1-004 | `TODO` | C02 | docs | matriz de falha definida | — |
| INT-P1-005 | `TODO` | C02 | docs/config | timeout documentado | — |
| INT-P1-006 | `TODO` | C02 | docs | proxy/CORS/topologia definidos | — |

### P2 — Backend

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P2-001 | `TODO` | C03 | testes API | testes HTTP passando | — |
| INT-P2-002 | `TODO` | C04 | `api.py`/sessão + testes | sessões distintas + contexto preservado | — |
| INT-P2-003 | `TODO` | C05 | `api.py` + testes | healthcheck seguro passando ou adiamento registrado | — |
| INT-P2-004 | `TODO` | C03 | API/schema/testes | validação e status HTTP cobertos | — |
| INT-P2-005 | `TODO` | C05 | API/config/docs | origem validada ou item dispensado com justificativa | — |

### P3 — Frontend

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P3-001 | `TODO` | C06 | models/DTOs | sem `Observable<any>` na fronteira | — |
| INT-P3-002 | `TODO` | C06 | service de sessão/storage | ID retorna e é reutilizado | — |
| INT-P3-003 | `TODO` | C06 | `chat.ts` service | endpoint/body corretos | — |
| INT-P3-004 | `TODO` | C06 | `features/chat/chat.ts` | resposta real exibida; mock fora do sucesso | — |
| INT-P3-005 | `TODO` | C07 | state/component/template | erro real visível e recuperável | — |
| INT-P3-006 | `TODO` | C07 | component/storage/model | histórico usa `processo_ativo` | — |
| INT-P3-007 | `TODO` | C05/C07 | API + frontend | indicador baseado em evidência ou texto neutro | — |
| INT-P3-008 | `TODO` | C07 | `index.html`, app metadata | idioma/título coerentes | — |

### P4 — Testes

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P4-001 | `READY` | C08 | specs existentes | `tsconfig.spec` compila + testes passam | — |
| INT-P4-002 | `TODO` | C08 | `chat.spec.ts` ou teste dedicado | request HTTP assertado | — |
| INT-P4-003 | `TODO` | C08 | component spec | sucesso/erro/histórico testados | — |
| INT-P4-004 | `TODO` | C11 | relatório/controle | duas mensagens reais em sequência | — |
| INT-P4-005 | `TODO` | C11 | testes/relatório | cenários de degradação registrados | — |

### P5 — Execução local

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P5-001 | `TODO` | C09 | proxy config + Angular config/package | `/api` funciona localmente sem URL hardcoded | — |
| INT-P5-002 | `TODO` | C09/C10 | docs/frontend README | clone limpo → `npm ci` → build/test | — |
| INT-P5-003 | `TODO` | C09/C10 | docs/backend README | setup backend reproduzível | — |
| INT-P5-004 | `TODO` | C09 | docs/scripts opcionais | fluxo integrado documentado e testado | — |

### P6 — Documentação

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| INT-P6-001 | `TODO` | C10 | `docs/ARCHITECTURE.md` | arquitetura final refletida | — |
| INT-P6-002 | `READY` | C10 | `docs/development.md` | onboarding executável | — |
| INT-P6-003 | `READY` | C10 | `docs/orchestration.md` | fluxo integrado descrito | — |
| INT-P6-004 | `READY` | C10 | `docs/design_philosophy.md` | princípios comuns descritos | — |
| INT-P6-005 | `TODO` | C10 | `README.md` | README sem arquitetura histórica enganosa | — |
| INT-P6-006 | `TODO` | C10 | `frontend/README.md` | README específico do projeto | — |

### P7 — Fechamento

| ID | Status | Commit planejado | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|
| INT-P7-001 | `TODO` | C11 | suite backend e comparação com baseline | — |
| INT-P7-002 | `TODO` | C11 | `npm ci`, tests, build, typecheck | — |
| INT-P7-003 | `TODO` | C11 | revisão de segredo/CORS/session/erros | — |
| INT-P7-004 | `TODO` | C11 | diff completo + `git diff --check` | — |
| INT-P7-005 | `TODO` | C11 | smoke navegador + sessão + falha | — |
| INT-P7-006 | `TODO` | C11 | gate completo = `READY_FOR_MERGE` | — |

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

---

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
| Arquitetura | 🟡 Parcial | frontend ainda não incorporado formalmente aos docs |
| Contrato HTTP | 🔴 Não alinhado | `/api/chat` vs `/api/processos/chat`; body/response divergentes |
| Sessão | 🔴 Não segura para múltiplos clientes | fallback `default` compartilhado |
| Backend | 🟢 Base funcional | falta cobertura HTTP específica |
| Frontend | 🟡 Base funcional | ainda usa mock e specs estão desatualizados |
| Testes integrados | 🔴 Ausentes | nenhum smoke navegador→API registrado |
| Desenvolvimento local | 🟡 Parcial | falta fluxo conjunto/proxy; pacote recebido traz `node_modules` de Windows |
| Documentação | 🟡 Em construção | 3 docs centrais vazios + READMEs desalinhados |
| Governança Codex | 🟡 Boa base | verificar versionamento de `.codex/rules/safety.rules` |
| Segurança da integração | 🟡 A validar | sessão, CORS/origem e erros ainda não fechados |
| Merge | 🔴 `NOT_READY` | gates G0–G6 abertos |

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

## 11. Próximo passo recomendado a partir do baseline

**Não iniciar alterando `ChatService` ainda.**

Ordem imediata recomendada:

1. `INT-P0-001` — confirmar branch/worktree local;
2. `INT-P0-002` — auditar o que está realmente rastreado;
3. `INT-P0-003` — garantir que a política Codex compartilhada possa ser versionada;
4. `INT-P0-004` — repetir baseline no ambiente local limpo;
5. `INT-P1-001` a `INT-P1-006` — fechar arquitetura/contrato/sessão/erro/timeout/rede;
6. somente então começar mudanças de backend/frontend.

Isso mantém a integração reversível e impede que decisões arquiteturais sejam tomadas incidentalmente por um patch de código.
