# Controle de Progresso e Commits — Integração Chatbot + Coleta TRT18

> **Artefato operacional temporário da branch de integração.**
> Este arquivo registra execução e evidências, não integra a documentação do
> produto e deve ser removido antes de a entrega chegar à `main`.

**Branch-alvo:** `feat/integra_chatbot_coleta_etl`
**Baseline documental:** 01/09/2026
**Checklist vinculada:** `CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md`
**Estado global inicial:** `NOT_READY`
**Objetivo:** rastrear status, modelo recomendado/executado, evidências, gates e
um único commit por fase.

Este arquivo não substitui o Git. A checklist especifica o que deve acontecer;
este controle registra o que realmente aconteceu.

---

## 1. Regras operacionais

1. Um prompt executa somente um ID explicitamente autorizado.
2. Um item entra em `IN_PROGRESS` apenas quando seu trabalho realmente começa.
3. O item não autoriza avanço automático para outro ID ou fase.
4. `IMPLEMENTED` não equivale a `VALIDATED`.
5. Evidência deve registrar comandos, resultados, arquivos e limitações reais.
6. Falha preexistente ou ambiental não pode ser renomeada como sucesso.
7. O modelo recomendado orienta custo/complexidade; não integra o critério de aceite.
8. Escalação de modelo é permitida, mas deve ser registrada antes de improvisar
   decisão arquitetural.
9. `COMMIT_REAL` de item permanece `—`; commits pertencem somente ao fechamento
   da fase.
10. Cada fase possui exatamente um commit planejado.
11. O commit exige todos os IDs da fase validados, regressão proporcional, diff
    revisado, `git diff --check` e autorização explícita do usuário.
12. `git push`, merge, limpeza destrutiva e remoção fora dos alvos autorizados
    nunca são implícitos.

```text
ID = unidade de execução
ID = unidade de validação
FASE = unidade de checkpoint/commit
```

---

## 2. Política de modelos Codex

### GPT-5.6 Luna

Usar em trabalho mecânico, localizado e com decisão já tomada:

- auditoria simples e objetiva;
- atualização textual delimitada;
- links, paths, referências e metadados;
- atualização deste controle;
- fechamento documental de baixo risco.

### GPT-5.6 Terra

Modelo padrão para implementação e análise técnica delimitada:

- mudanças moderadas em múltiplos arquivos;
- testes focados e regressão;
- adapters e imports com decisão arquitetural já aprovada;
- persistência seguindo padrão existente;
- configuração, dependências e documentação técnica derivada do código.

### GPT-5.6 Sol

Reservar para decisões cujo erro causa cascata ou exige investigação difícil:

- contrato produtor/consumidor;
- semântica de estados e falhas;
- fronteira entre os dois subsistemas;
- fallback local → coleta → persistência;
- regressão complexa ou incompatibilidade inesperada;
- revisão de aceite real e gate final de alto risco.

### Regra de escalação

```text
Luna → Terra → Sol
```

Se o item revelar complexidade material acima da recomendação:

1. interromper a decisão não autorizada;
2. registrar a descoberta e o trabalho seguro já concluído;
3. manter `IN_PROGRESS`, `IMPLEMENTED` ou `BLOCKED` conforme a evidência;
4. recomendar novo modelo/prompt;
5. preencher `MODELO_EXECUTADO` e `MOTIVO_DIVERGENCIA_MODELO`.

Usar um modelo diferente não invalida tecnicamente o item. O que valida é a
evidência do critério de aceite.

---

## 3. Estado inicial observado

| Área | Estado inicial | Evidência disponível | Situação |
|---|---|---|---|
| Nova branch | Ainda não confirmada | Usuário está preparando a branch | `READY` para confirmação |
| Módulo de coleta | Incorporado ao worktree | `entrada-de-dados/` e anexos fornecidos | Estrutura presente; rastreabilidade pendente |
| Fronteira do coletor | Existe | `servico.obter_processo()` | Ainda não consumida pelo chatbot |
| Adapter do chatbot | Local-only | delega ao `process_repository` | Integração remota ausente |
| Lookup conversacional | Local-only | Agent 2 transforma `None` em `not_found` | Falha remota ainda sem semântica |
| Persistência | Disponível | `ingest_processes()` + SQLite + chunks | Ainda não ligada ao coletor |
| Sanitização | Existente | remove documento de partes e IDs internos | Deve ser preservada |
| Estados do coletor | Cinco estados | sucesso, parcial, falha, não encontrado, bloqueado | Tradução ainda não integrada |
| README raiz | Centralização implementada | relato/diff anterior | Validação na nova branch pendente |
| Requirements Python | Centralização implementada | dependências do coletor incorporadas | Bootstrap limpo pendente |
| Docs de ingestão | Iniciados | análise técnica anterior em `docs/` | Alinhamento final depende do código |
| Frontend | Fora do escopo funcional | integração Angular–FastAPI já concluída | Deve permanecer inalterado |
| Artefatos operacionais | Temporários | checklist, controle, AGENTS e safety | Remover da projeção final |

**Conclusão do baseline:** duas bases funcionais e uma persistência compatível
existem, mas o chatbot ainda não aciona `entrada-de-dados`. Estado global:
`NOT_READY`.

---

## 4. Gates macro

| Gate | Fase | Critério para fechar | Estado inicial |
|---|---|---|---|
| G0 | P0 — Baseline estrutural | branch, worktree, artefatos, centralização e testes baseline comprovados | `READY` |
| G1 | P1 — Contratos | produtor, consumidor, estados, importação, ownership e dados decididos | `TODO` |
| G2 | P2 — Fronteira Python | import estável, adapter explícito e testes offline aprovados | `TODO` |
| G3 | P3 — Fallback/persistência | local-first, coleta em miss, ingestão e reuso validados | `TODO` |
| G4 | P4 — Falhas | matriz de estados, API controlada e rollback validados | `TODO` |
| G5 | P5 — Runtime | dependências, config, CAPTCHA canônico e venv limpo aprovados | `TODO` |
| G6 | P6 — Integração | regressões, matriz automatizada e aceite real controlado registrados | `TODO` |
| G7 | P7 — Documentação | README/docs coerentes e auditoria cruzada aprovada | `TODO` |
| G8 | P8 — Fechamento | DoD, diff, segurança e projeção para main aprovados | `TODO` |

---

## 5. Plano de commits por fase

Os commits abaixo são planejados; não constituem autorização para executar
`git commit`.

| Commit lógico | Fase | IDs cobertos | Mensagem sugerida | Estado | Commit real |
|---|---|---|---|---|---|
| C00 | P0 | `INT-COL-P0-001..004` | `chore(integration): establish chatbot collector baseline` | `READY` | — |
| C01 | P1 | `INT-COL-P1-001..004` | `docs(integration): define chatbot collector contracts` | `TODO` | — |
| C02 | P2 | `INT-COL-P2-001..003` | `feat(collector): establish chatbot collection boundary` | `TODO` | — |
| C03 | P3 | `INT-COL-P3-001..004` | `feat(chat): acquire and persist missing processes` | `TODO` | — |
| C04 | P4 | `INT-COL-P4-001..003` | `fix(chat): preserve collector failure semantics` | `TODO` | — |
| C05 | P5 | `INT-COL-P5-001..004` | `chore(runtime): unify collector setup and configuration` | `TODO` | — |
| C06 | P6 | `INT-COL-P6-001..004` | `test(integration): cover chatbot collector workflow` | `TODO` | — |
| C07 | P7 | `INT-COL-P7-001..003` | `docs(project): document chatbot collector integration` | `TODO` | — |
| C08 | P8 | `INT-COL-P8-001..004` | `chore(integration): finalize chatbot collector delivery` | `TODO` | — |

---

## 6. Controle por item e modelo recomendado

### P0 — Baseline estrutural

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P0-001 | `VALIDATED` | GPT-5.6 Luna | GPT-5.6 Luna | branch/base/worktree registrados | C00 |
| INT-COL-P0-002 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | inventário e sanitização confirmados; caches, dados e browsers locais protegidos | C00 |
| INT-COL-P0-003 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | fontes canônicas confirmadas; README auxiliar reconciliado com a estrutura atual | C00 |
| INT-COL-P0-004 | `VALIDATED` | GPT-5.6 Terra | GPT-5.6 Terra | 43 testes; normalização, Pydantic, CNJ e cache offline aprovados; sem acesso externo | C00 |

### P1 — Contratos e arquitetura

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P1-001 | `READY` | GPT-5.6 Terra | — | contrato produtor e side effects mapeados | C01 |
| INT-COL-P1-002 | `TODO` | GPT-5.6 Terra | — | contrato consumidor e round-trip mapeados | C01 |
| INT-COL-P1-003 | `TODO` | GPT-5.6 Sol | — | contrato do adapter e matriz de estados aprovados | C01 |
| INT-COL-P1-004 | `TODO` | GPT-5.6 Sol | — | importação, ownership e política de dados decididos | C01 |

### P2 — Fronteira Python

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P2-001 | `TODO` | GPT-5.6 Terra | — | import estável sem efeito externo | C02 |
| INT-COL-P2-002 | `TODO` | GPT-5.6 Sol | — | adapter implementa contrato sem duplicação | C02 |
| INT-COL-P2-003 | `TODO` | GPT-5.6 Terra | — | matriz offline do adapter aprovada | C02 |

### P3 — Fallback e persistência

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P3-001 | `TODO` | GPT-5.6 Sol | — | local-first e uma coleta somente em miss | C03 |
| INT-COL-P3-002 | `TODO` | GPT-5.6 Terra | — | ingestão/rollback/round-trip aprovados | C03 |
| INT-COL-P3-003 | `TODO` | GPT-5.6 Sol | — | Agent 2 e progresso integrados sem mudar HTTP | C03 |
| INT-COL-P3-004 | `TODO` | GPT-5.6 Terra | — | sessão, nova sessão e restart sem recoleta | C03 |

### P4 — Estados e degradação

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P4-001 | `TODO` | GPT-5.6 Sol | — | matriz de estados traduzida sem falso not_found | C04 |
| INT-COL-P4-002 | `TODO` | GPT-5.6 Sol | — | API segura e banco consistente em falhas | C04 |
| INT-COL-P4-003 | `TODO` | GPT-5.6 Terra | — | testes observáveis dos estados aprovados | C04 |

### P5 — Runtime, configuração e duplicações

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P5-001 | `TODO` | GPT-5.6 Terra | — | manifesto(s) cobrindo imports reais | C05 |
| INT-COL-P5-002 | `TODO` | GPT-5.6 Terra | — | env/paths sem concorrência ou path local | C05 |
| INT-COL-P5-003 | `TODO` | GPT-5.6 Terra | — | CAPTCHA e fontes de verdade canônicos | C05 |
| INT-COL-P5-004 | `TODO` | GPT-5.6 Terra | — | venv limpo, browser, imports, health e testes | C05 |

### P6 — Testes e aceite

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P6-001 | `TODO` | GPT-5.6 Terra | — | regressão backend comparada à baseline | C06 |
| INT-COL-P6-002 | `TODO` | GPT-5.6 Terra | — | regressão offline do coletor | C06 |
| INT-COL-P6-003 | `TODO` | GPT-5.6 Sol | — | matriz integrada automatizada aprovada | C06 |
| INT-COL-P6-004 | `TODO` | GPT-5.6 Sol | — | aceite real ou bloqueio externo honesto | C06 |

### P7 — Documentação do produto

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P7-001 | `TODO` | GPT-5.6 Luna | — | README/setup alinhados ao fluxo final | C07 |
| INT-COL-P7-002 | `TODO` | GPT-5.6 Terra | — | arquitetura/ingestão/dev/orquestração atualizados | C07 |
| INT-COL-P7-003 | `TODO` | GPT-5.6 Terra | — | auditoria cruzada, links e segurança aprovados | C07 |

### P8 — Fechamento e projeção para main

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P8-001 | `TODO` | GPT-5.6 Sol | — | regressão final e diff completo revisados | C08 |
| INT-COL-P8-002 | `TODO` | GPT-5.6 Sol | — | Definition of Done comprovado | C08 |
| INT-COL-P8-003 | `TODO` | GPT-5.6 Terra | — | artefatos operacionais ausentes da projeção | C08 |
| INT-COL-P8-004 | `TODO` | GPT-5.6 Sol | — | READY_FOR_MERGE ou bloqueios objetivos | C08 |

---

## 7. Registro cronológico de execução

Registrar somente eventos reais. Não apagar registros de tentativa, bloqueio,
recuperação ou rejeição; adicionar novo evento.

| Data/hora | ID/Fase | Evento | Transição | Modelo | Evidência resumida | Commit real |
|---|---|---|---|---|---|---|
| 01/09/2026 | Planejamento | Checklist e controle refatorados a partir do baseline fornecido | — | GPT-5.6 | um ID por prompt; commit por fase; modelo por item; artefatos temporários | — |
| 01/09/2026 | INT-COL-P0-001 | Branch, base e worktree confirmados e inventariados | `READY` → `VALIDATED` | GPT-5.6 Luna | branch `feat/integra_chatbot_coleta_etl`; base `main`/`origin/main` em `cce4751`; 15 à frente, 0 atrás; alterações preexistentes preservadas | — |
| 01/09/2026 | INT-COL-P0-002 | Auditoria do módulo transportado e artefatos protegidos iniciada | `READY` → `IN_PROGRESS` | GPT-5.6 Terra | escopo limitado a `entrada-de-dados/`; inspeções somente leitura | — |
| 01/09/2026 | INT-COL-P0-002 | Inventário Git e auditoria de ignores concluídos | `IN_PROGRESS` → `IMPLEMENTED` | GPT-5.6 Terra | 17 arquivos não rastreados; nenhum cache/output/debug/runtime materializado ou rastreado; cobertura de browser/binário não comprovada | — |
| 01/09/2026 | INT-COL-P0-003 | Validação da consolidação documental e de dependências iniciada | `IMPLEMENTED` → `IN_PROGRESS` | GPT-5 | escopo limitado às fontes de verdade, imports, manifesto, documentação e histórico local; sem instalação, coleta ou alteração de produto | — |
| 01/09/2026 | INT-COL-P0-003 | Consolidação estrutural comprovada; inconsistência documental auxiliar registrada | `IN_PROGRESS` → `IMPLEMENTED` | GPT-5 | README raiz e manifesto central são fontes atuais; 5 dependências diretas representadas e sem duplicações; `captcha/DCF_CODE/README.md` ainda referencia setup histórico inexistente | — |
| 01/09/2026 | INT-COL-P0-004 | Registro da baseline técnica iniciado | `READY` → `IN_PROGRESS` | GPT-5.6 Terra | estado Git, ambiente, isolamento e validações offline em apuração; sem coleta, navegador ou serviços externos | — |
| 01/09/2026 | INT-COL-P0-004 | Baseline técnica registrada e auto-validada | `IN_PROGRESS` → `VALIDATED` | GPT-5.6 Terra | 43 testes passaram; normalização/Pydantic/CNJ/cache offline passaram; artefatos protegidos preservados; sem rede ou navegador | — |
| 01/09/2026 | INT-COL-P0-002/P0-003 | Fechamento das lacunas residuais da P0 iniciado | `IMPLEMENTED` → `IN_PROGRESS` | GPT-5 | proteção de binários locais e reconciliação da documentação histórica autorizadas; sem coleta ou instalação | — |
| 01/09/2026 | INT-COL-P0-002 | Artefatos protegidos e política de browsers revalidados | `IN_PROGRESS` → `VALIDATED` | GPT-5 | exemplo sanitizado sem identificadores válidos detectáveis; hashes preservados; cinco probes de browser ignorados | — |
| 01/09/2026 | INT-COL-P0-003 | Consolidação documental e de dependências revalidada | `IN_PROGRESS` → `VALIDATED` | GPT-5 | README auxiliar agora aponta para fluxo, manifesto e documentação canônicos existentes | — |
| 01/09/2026 | Fase P0 | Todos os IDs técnicos validados; checkpoint liberado para fechamento específico | `C00 TODO` → `C00 READY` | GPT-5 | INT-COL-P0-001..004 validados; G0 permanece aberto e nenhum commit foi criado | — |

---

## 8. Modelo de registro após cada item

Copiar e preencher no fim desta seção ou no registro detalhado correspondente:

```text
ID: INT-COL-PX-XXX
DATA_HORA:
STATUS_ANTERIOR:
STATUS_FINAL:
MODELO_RECOMENDADO:
MODELO_EXECUTADO:
MOTIVO_DIVERGENCIA_MODELO:
DIAGNOSTICO_CONFIRMADO:
DECISAO_TECNICA:
ARQUIVOS_MODIFICADOS:
RESUMO_DIFF:
TESTES_EXECUTADOS:
RESULTADOS:
DOCUMENTACAO_ATUALIZADA:
REVISAO_DO_DIFF:
GIT_DIFF_CHECK:
SEGREDOS_DADOS_SENSIVEIS:
RISCOS_RESIDUAIS:
DEPENDENCIAS_AFETADAS:
COMMIT_DA_FASE: CXX
COMMIT_REAL: —
OBSERVACOES:
```

`COMMIT_REAL` permanece `—` no registro do item. O hash é preenchido somente no
registro consolidado de fechamento da fase.

---

## 9. Modelo de fechamento de fase

```text
FASE: PX
GATE: GX
IDS_PREVISTOS:
IDS_VALIDATED:
EXCECOES_ACEITAS:
MODELO_DO_FECHAMENTO:
ARQUIVOS_ACUMULADOS:
TESTES_FOCADOS:
REGRESSAO_DA_FASE:
RESULTADOS:
DIFF_REVISADO: sim/não
GIT_DIFF_CHECK: pass/fail/não executado
SEGREDOS_VERIFICADOS: sim/não
DADOS_REAIS_VERIFICADOS: sim/não
ESCOPO_NEGATIVO_PRESERVADO: sim/não
RISCOS_RESIDUAIS:
COMMIT_LOGICO: CXX
COMMIT_SUGERIDO:
COMMIT_REAL: <hash ou —>
AUTORIZACAO_DO_USUARIO: sim/não
GATE_FINAL: VALIDATED/BLOCKED/NOT_READY
PROXIMA_FASE_AUTORIZADA: não
```

Mesmo após o fechamento, a próxima fase só começa com novo prompt/autorização.

---

## 10. Matriz de prontidão atual

| Dimensão | Estado | Bloqueio principal |
|---|---|---|
| Branch/worktree | 🟢 Validado | branch e base confirmadas; worktree inventariado |
| Baseline estrutural | 🟢 Validada | checkpoint C00 pronto para fechamento específico; G0 ainda aberto |
| Contrato produtor | 🟡 Código disponível | mapeamento formal pendente |
| Contrato consumidor | 🟡 Código disponível | round-trip e perdas precisam ser congelados |
| Fronteira Python | 🔴 Não integrada | adapter ainda é apenas local |
| Aquisição remota | 🔴 Não integrada | chatbot não chama `obter_processo()` |
| Persistência pós-coleta | 🔴 Não integrada | ingestão existe, mas não está ligada ao fallback |
| Estados/falhas | 🔴 Não integrados | `None` local ainda representa not_found |
| Runtime/configuração | 🟡 Parcial | requirements centralizado sem venv limpo final |
| Testes integrados | 🔴 Ausentes | fluxo local→coleta→SQLite→resposta não coberto |
| Documentação | 🟡 Adiantada | alinhamento final depende da implementação |
| Frontend | 🟢 Fora do escopo | deve permanecer sem alteração funcional |
| Segurança de dados | 🟢 Baseline validada | regressão integrada permanece reservada para P6 |
| Merge | 🔴 `NOT_READY` | G0–G8 não fechados |

---

## 11. Critério de estado global

### `NOT_READY`

Usar enquanto houver bloqueio de contrato, fronteira, persistência, estados,
bootstrap, testes ou projeção final.

### `INTEGRATION_READY`

Pode ser usado quando:

- G0–G6 estão `VALIDATED`;
- fluxo funcional e regressões estão aprovados;
- restam somente documentação/limpeza final não bloqueante e registrada.

### `READY_FOR_MERGE`

Somente quando:

- G0–G8 estão fechados;
- todos os commits de fase autorizados possuem hash real;
- regressão final, aceite, segurança e `git diff --check` foram aprovados;
- documentação real corresponde ao código;
- riscos adiados foram aceitos;
- checklist, controle, `AGENTS.md` e `safety.rules` não aparecem na projeção
  destinada à `main`;
- push/merge continuam dependentes de autorização explícita.

---

## 12. Próximo passo operacional

O próximo prompt deve executar somente:

```text
C00 — Criar e verificar o checkpoint de fechamento da Fase P0
```

O checkpoint exige prompt específico. G0 permanece aberto até a criação e
verificação do commit; não iniciar P1 automaticamente.

### INT-COL-P0-001 — Registro detalhado

```text
ID: INT-COL-P0-001
DATA_HORA: 01/09/2026
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Luna
MODELO_EXECUTADO: GPT-5.6 Luna
MOTIVO_DIVERGENCIA_MODELO: nenhum
DIAGNOSTICO_CONFIRMADO: branch feat/integra_chatbot_coleta_etl; HEAD não está detached; main e origin/main presentes e convergentes; merge-base cce475130a76babb224ff1425f38e775281b45fe; 15 commits à frente e 0 atrás.
DECISAO_TECNICA: usar main como referência local, com origin/main confirmado no mesmo commit-base.
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: atualização operacional do item, branch-alvo, matriz, cronologia e registro detalhado.
TESTES_EXECUTADOS: inspeções Git read-only; git diff --check
RESULTADOS: inspeções concluídas; diff check sem erros introduzidos.
DOCUMENTACAO_ATUALIZADA: checklist e controle operacional.
REVISAO_DO_DIFF: revisados os dois documentos; nenhuma alteração fora do escopo causada por esta execução.
GIT_DIFF_CHECK: pass
SEGREDOS_DADOS_SENSIVEIS: não expostos; apenas caminhos e estados Git mínimos foram registrados.
RISCOS_RESIDUAIS: worktree já estava sujo com alterações rastreadas, não rastreadas e ignoradas; preservado integralmente.
DEPENDENCIAS_AFETADAS: nenhuma funcional; INT-COL-P0-002 não iniciado.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: checklist localizada em docs/; nenhum comando destrutivo ou atualização remota executado.
```

### INT-COL-P0-002 — Registro detalhado

```text
ID: INT-COL-P0-002
DATA_HORA: 01/09/2026
STATUS_ANTERIOR: READY
STATUS_FINAL: IMPLEMENTED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5.6 Terra
MOTIVO_DIVERGENCIA_MODELO: nenhum
DIAGNOSTICO_CONFIRMADO: `entrada-de-dados/` possui 17 arquivos físicos, todos não rastreados; não há arquivos staged, modificados, removidos ou renomeados no módulo, nem artefatos operacionais rastreados. A árvore contém 11 Python, 2 Markdown, 1 notebook, 1 JSON de exemplo e 1 planilha em `data/entrada/`.
DECISAO_TECNICA: preservar integralmente o módulo e seus artefatos; classificar código, READMEs, notebook, exemplo e planilha como conteúdo intencional não rastreado da baseline, sem abrir dados potencialmente sensíveis. Manter o item em IMPLEMENTED porque não há regra específica comprovada para diretórios de browsers/binários e a sanitização do exemplo não foi inspecionada.
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: atualização operacional do item, ações comprovadas, cronologia e registro da auditoria; nenhum arquivo do módulo, baseline ou ignore foi alterado.
TESTES_EXECUTADOS: git status --short --branch; git status --porcelain=v1 -- entrada-de-dados; git diff --name-status -- entrada-de-dados; git diff --cached --name-status -- entrada-de-dados; git ls-files; git ls-files --others --exclude-standard; git ls-files --others --ignored --exclude-standard; inventário de metadados da árvore; git check-ignore -v com probes somente leitura.
RESULTADOS: regras internas cobrem dados brutos/saída/debug, logs de dados, imagens de CAPTCHA, cache Python e Jupyter; regras da raiz cobrem .env, bancos, temporários, outputs e artifacts. Não há caches, outputs, diagnósticos, bancos, .env, screenshots, HTMLs, logs, __pycache__, checkpoints ou browsers instalados fisicamente no módulo. Probes para browser/chrome.exe e playwright-browsers/chrome.exe não retornaram regra de ignore.
DOCUMENTACAO_ATUALIZADA: checklist e controle operacional.
REVISAO_DO_DIFF: revisados os dois documentos e o escopo de `entrada-de-dados/`; somente alterações operacionais deste ID foram introduzidas.
GIT_DIFF_CHECK: pass (sem erros de whitespace; `git diff --no-index` retornou somente o código 1 esperado para comparação de arquivos não rastreados)
SEGREDOS_DADOS_SENSIVEIS: não expostos; auditoria limitou-se a caminhos, estados Git, extensões e contagens. Sanitização do JSON de exemplo não comprovada sem abrir o conteúdo.
RISCOS_RESIDUAIS: eventual browser/binário instalado sob diretório próprio no módulo não é coberto pelos probes de ignore; requer item/autorização específica para remediação. Exemplo e planilha permanecem protegidos e não alterados, mas a sanitização do exemplo não foi revalidada nesta auditoria.
DEPENDENCIAS_AFETADAS: nenhuma funcional; INT-COL-P0-003 não iniciado.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: categorias: código-fonte intencional (11 Python); documentação/manifesto intencional (2 Markdown e notebook de pesquisa); baseline autorizada (JSON de exemplo e planilha de entrada, sanitização do JSON não comprovada); cache/output/runtime ignorado (probes cobertos, sem arquivos físicos); não há artefato indevidamente rastreado conhecido. Nenhum comando destrutivo, coleta, instalação ou commit executado.
```

### INT-COL-P0-003 — Registro detalhado

```text
ID: INT-COL-P0-003
DATA_HORA: 01/09/2026
STATUS_ANTERIOR: IMPLEMENTED
STATUS_FINAL: IMPLEMENTED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5
MOTIVO_DIVERGENCIA_MODELO: o ambiente identificou o agente como GPT-5; GPT-5.6 Terra permaneceu como recomendação do item.
DIAGNOSTICO_CONFIRMADO: `README.md` é a entrada documental principal e `chatbot_processual_ai/requirements.txt` é o manifesto Python consolidado atual. `entrada-de-dados/README.md` e `entrada-de-dados/requirements.txt` estão ausentes; não há outro README ou manifesto concorrente. READMEs de frontend, backend e CAPTCHA foram classificados como específicos de subsistema. O README de `entrada-de-dados/captcha/DCF_CODE/` é auxiliar/histórico, mas contém instruções obsoletas para `requirements.txt`, `main.py` e `raspagem_dados.py` inexistentes nesse diretório.
DECISAO_TECNICA: manter a centralização como materialmente implementada, sem auto-validar o item enquanto a documentação auxiliar contradiz a estrutura atual. A correção pertence à atualização documental final em P7; não há perda de conteúdo essencial, fonte concorrente material ou dependência direta ausente que bloqueie a P0.
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: atualização operacional exclusiva do ID, com ações comprovadas, status IMPLEMENTED, cronologia e registro detalhado; nenhum arquivo de produto, baseline, manifesto ou código foi alterado.
TESTES_EXECUTADOS: inventário de READMEs e manifests; `rg` de imports Python em `entrada-de-dados/` e CAPTCHA; comparação dos imports externos com `chatbot_processual_ai/requirements.txt`; normalização de nomes e detecção de duplicações; validação de 21 links Markdown locais; verificações de existência dos arquivos removidos; `git diff`, `git diff --cached`, `git diff --diff-filter=D`, `git log --all --full-history`; `git diff --check`.
RESULTADOS: 5 dependências diretas do fluxo principal identificadas (`pydantic`, `playwright`, `ddddocr`, `opencv-python` para `cv2`, `numpy`), todas presentes no manifesto. Há 15 entradas no manifesto e nenhuma duplicação por nome normalizado. Os 21 links Markdown locais verificados existem. O histórico Git local não contém versão recuperável dos dois arquivos removidos; a cobertura essencial foi comparada com o código e a documentação atuais. A única inconsistência é o README auxiliar/histórico de `captcha/DCF_CODE/` com comandos e paths obsoletos.
DOCUMENTACAO_ATUALIZADA: somente checklist e controle operacional; README, `docs/`, requirements e documentação do CAPTCHA foram apenas auditados, sem edição.
REVISAO_DO_DIFF: revisado o diff operacional; somente os dois artefatos autorizados deste ID foram modificados nesta execução, sem alteração funcional.
GIT_DIFF_CHECK: pass
SEGREDOS_DADOS_SENSIVEIS: não expostos; não foram abertos caches, planilhas, exemplos, bancos, payloads processuais ou arquivos `.env`.
RISCOS_RESIDUAIS: `entrada-de-dados/captcha/DCF_CODE/README.md` pode induzir setup por paths inexistentes e deve ser reconciliado em P7. Bootstrap Python limpo, browsers Playwright e separação final de dependências runtime/teste/notebook continuam não validados e reservados para P5/P7.
DEPENDENCIAS_AFETADAS: nenhuma alteração funcional; P5 deve fechar manifesto, validar bootstrap limpo e instalar browsers Playwright quando autorizado; P7 deve corrigir a documentação auxiliar histórica.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: G0 permanece aberto; não foram instaladas dependências, criado `.venv`, instalado browser Playwright, executada coleta real ou iniciado INT-COL-P0-004.
```

### INT-COL-P0-004 — Registro detalhado

```text
ID: INT-COL-P0-004
DATA_HORA: 01/09/2026 16:21 -03:00
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5.6 Terra
MOTIVO_DIVERGENCIA_MODELO: nenhum
DIAGNOSTICO_CONFIRMADO: o comando oficial é `python -m pytest tests -q`, executado em `chatbot_processual_ai/` com `.venv\\Scripts\\python.exe` (Python 3.12.10, pip 25.0.1, pytest 9.1.1). A suíte usa patches para Ollama/Qdrant e SQLite temporário exclusivo; a coleta só carrega Playwright sob demanda e não foi chamada.
DECISAO_TECNICA: registrar a baseline sem alterar código, testes, fixtures, dependências ou dados. Usar apenas o exemplo sanitizado em memória e funções puras para normalização, CNJ e cache.
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: status, ações comprovadas, cronologia, matriz de prontidão e registro desta baseline; nenhum arquivo funcional ou protegido foi alterado intencionalmente.
TESTES_EXECUTADOS: `chatbot_processual_ai\\.venv\\Scripts\\python.exe -m pytest tests -q`; normalização em memória de `exemplos/exemplo_bruto.json` seguida de `Processo.model_validate`; `validar_numero_cnj` para número autorizado e inválido sintético; `cache_aproveitavel` para estruturas sintéticas completa e incompleta; status Git e SHA-256 do exemplo e da planilha antes/depois.
RESULTADOS: 43 passed em 2.28 s, 1 PytestCacheWarning ambiental (WinError 5 ao criar `.pytest_cache`); normalização, estrutura Pydantic, número formatado, CNJ e rejeição sintética passaram; cache completo foi aproveitável e incompleto rejeitado; contagens técnicas: 2 partes, 5 movimentações, 2 documentos, 0 pendências. Não houve coleta, rede, navegador, CAPTCHA, Ollama, Qdrant ou acesso ao TRT18. Os hashes finais do exemplo e planilha foram registrados; `git status --short` permaneceu igual fora das atualizações operacionais autorizadas.
DOCUMENTACAO_ATUALIZADA: somente checklist e controle operacional.
REVISAO_DO_DIFF: revisados os dois documentos e o estado Git anterior/posterior; alterações rastreadas e não rastreadas preexistentes foram preservadas. O diretório temporário de cache que o pytest não conseguiu criar foi classificado como efeito ambiental, sem limpeza manual.
GIT_DIFF_CHECK: pass; apenas warnings de CRLF preexistentes e aviso de permissão no diretório temporário do pytest.
SEGREDOS_DADOS_SENSIVEIS: não expostos; não foram impressos payload, número processual, nomes, documentos, planilha, banco ou `.env`.
RISCOS_RESIDUAIS: a baseline usa `.venv` existente, não um ambiente limpo; pytest não é declarado em `requirements.txt`; browser Playwright, coleta real, CAPTCHA, Ollama, Qdrant e integração funcional permanecem fora do escopo. INT-COL-P0-002 e INT-COL-P0-003 continuam IMPLEMENTED.
DEPENDENCIAS_AFETADAS: nenhuma funcional; C00 permanece TODO até a validação dos itens P0 pendentes.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: nenhum commit criado; G0 permanece aberto e P1 não foi iniciada.
```

### INT-COL-P0-002 — Registro de revalidação

```text
ID: INT-COL-P0-002
DATA_HORA: 01/09/2026 16:27 -03:00
STATUS_ANTERIOR: IMPLEMENTED
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5
MOTIVO_DIVERGENCIA_MODELO: o ambiente atual identifica o agente como GPT-5; GPT-5.6 Terra permaneceu como recomendação registrada.
DIAGNOSTICO_CONFIRMADO: a auditoria anterior já cobria dados, caches e runtimes, mas não havia regra específica para browsers materializados dentro do módulo nem comprovação estrutural da sanitização do exemplo.
DECISAO_TECNICA: adicionar ignores explícitos para cinco diretórios usuais de browsers locais e validar o exemplo autorizado somente por métricas e detectores locais, sem imprimir valores.
ARQUIVOS_MODIFICADOS: entrada-de-dados/.gitignore; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: proteção explícita de browsers locais e promoção operacional do item após reauditoria; nenhum baseline, exemplo ou dado foi alterado.
TESTES_EXECUTADOS: cinco probes com `git check-ignore -v`; análise estrutural offline do JSON para CPF/CNPJ válidos, e-mail, telefone e marcador sintético; SHA-256 do exemplo e da planilha; inventário Git; suíte oficial do chatbot.
RESULTADOS: todos os probes de browser foram ignorados; JSON válido com 41 strings analisadas, zero CPF/CNPJ válido, e-mail ou telefone detectável e um marcador sintético; hashes protegidos coincidem com a baseline registrada; 43 testes passaram e houve 1 warning ambiental de cache do pytest.
DOCUMENTACAO_ATUALIZADA: checklist e controle operacional; `.gitignore` do módulo atualizado como política de proteção.
REVISAO_DO_DIFF: alteração limitada às regras de browser e aos registros autorizados; artefatos preexistentes preservados.
GIT_DIFF_CHECK: pass
SEGREDOS_DADOS_SENSIVEIS: não expostos; somente contagens, flags e hashes foram registrados.
RISCOS_RESIDUAIS: a análise estrutural reduz o risco de identificadores comuns, mas não é prova jurídica de anonimização; regressão de dados permanece prevista em P6.
DEPENDENCIAS_AFETADAS: C00 liberado para READY após a validação conjunta de P0-003.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: nenhuma limpeza, instalação, coleta ou commit foi executado.
```

### INT-COL-P0-003 — Registro de revalidação

```text
ID: INT-COL-P0-003
DATA_HORA: 01/09/2026 16:27 -03:00
STATUS_ANTERIOR: IMPLEMENTED
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5
MOTIVO_DIVERGENCIA_MODELO: o ambiente atual identifica o agente como GPT-5; GPT-5.6 Terra permaneceu como recomendação registrada.
DIAGNOSTICO_CONFIRMADO: `captcha/DCF_CODE/README.md` era a única documentação auxiliar contraditória, pois descrevia ponto de entrada, manifesto e arquivos inexistentes.
DECISAO_TECNICA: tornar o README estritamente descritivo do subcomponente e encaminhar setup, dependências e operação às fontes canônicas existentes, sem antecipar a validação de ambiente limpo da P5.
ARQUIVOS_MODIFICADOS: entrada-de-dados/captcha/DCF_CODE/README.md; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md
RESUMO_DIFF: remoção das instruções históricas inválidas e registro das fontes atuais de fluxo, manifesto, desenvolvimento e ingestão.
TESTES_EXECUTADOS: verificação de existência de oito arquivos/fontes referenciados; rechecagem da centralização documentada; suíte oficial do chatbot; revisão do diff e `git diff --check`.
RESULTADOS: todos os caminhos referenciados existem; o README auxiliar não declara setup ou manifesto concorrente; nenhum código funcional foi alterado; 43 testes passaram com 1 warning ambiental já classificado.
DOCUMENTACAO_ATUALIZADA: README auxiliar do pipeline OCR, checklist e controle operacional.
REVISAO_DO_DIFF: conteúdo histórico obsoleto removido; responsabilidades dos cinco componentes existentes preservadas; nenhuma instrução de coleta foi adicionada.
GIT_DIFF_CHECK: pass
SEGREDOS_DADOS_SENSIVEIS: não expostos.
RISCOS_RESIDUAIS: bootstrap limpo, instalação de browser e reconciliação arquitetural definitiva do CAPTCHA continuam reservados para P5/P7.
DEPENDENCIAS_AFETADAS: INT-COL-P0-001..004 agora VALIDATED; C00 READY; G0 ainda aberto.
COMMIT_DA_FASE: C00
COMMIT_REAL: —
OBSERVACOES: Fase P1 não iniciada; o checkpoint depende de prompt específico.
```
