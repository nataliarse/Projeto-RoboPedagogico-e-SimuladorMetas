# Controle de Progresso e Commits — Resolução de Pendências do Chatbot Processual

**Projeto:** `chatbot_processual_ai`  
**Baseline técnico analisado:** `chatbot_processual_ai(9).zip`  
**Baseline documental:** 17/09/2026  
**Branch confirmada:** `feat/resolucao-pendencias-processual`  
**Checklist vinculada:** `CHECKLIST_RESOLUCAO_PENDENCIAS_CHATBOT.md`  
**Estado global inicial:** `NOT_READY`  
**Objetivo:** fornecer rastreabilidade operacional entre regra de negócio, dados, implementação, validação, arquivos modificados e commits da correção da resolução de pendências.

> Este arquivo **não substitui** `CHECKLIST_RESOLUCAO_PENDENCIAS_CHATBOT.md` e **não substitui** o histórico Git.  
> A checklist define o trabalho; este controle registra **estado, evidência, decisão, bloqueio e commit real** de cada unidade executada.

---

# 1. Regras de atualização

1. Um item entra em `IN_PROGRESS` somente quando o trabalho daquele ID realmente começar.
2. Não avançar automaticamente para outro ID porque o anterior terminou.
3. `IMPLEMENTED` significa que a alteração foi escrita e recebeu validação proporcional, mas ainda pode faltar aceite final/regressão.
4. `VALIDATED` exige:
   - critério de aceite confirmado;
   - evidência objetiva;
   - testes relevantes;
   - revisão do diff;
   - ausência de alteração acidental conhecida.
5. Não preencher `COMMIT_REAL` antes de existir commit.
6. Um commit pode cobrir vários IDs somente quando eles constituírem uma unidade lógica inseparável.
7. Quando um commit cobrir vários IDs, registrar todos explicitamente.
8. Não reescrever hash já registrado; correções posteriores recebem novo registro.
9. Falha preexistente deve permanecer registrada como preexistente.
10. Se faltar regra oficial necessária para um item, marcar `BLOCKED`; não completar a lacuna com conhecimento presumido da LLM.
11. Se faltar dado necessário para aplicar uma regra, marcar `BLOCKED` ou registrar fallback formalmente aprovado; não mascarar ausência com matching textual silencioso.
12. Toda regra codificada deve registrar sua **fonte de negócio**.
13. Mudança na fonte oficial exige reavaliar as regras derivadas e seus testes.
14. `pendencias`, última movimentação e movimento faltante devem permanecer semanticamente separados.
15. Um item que altere conclusão factual PENDENTE/BAIXADO exige teste de negócio correspondente.
16. Mudança de prompt/modelo não valida regra de domínio.
17. `READY_FOR_VALIDATION` só pode ser usado após o gate funcional da checklist.
18. `READY_FOR_MERGE` só deve ser usado quando regressão, documentação, diff e commits também estiverem fechados.

---

# 2. Estado inicial observado

| Área | Estado inicial | Evidência/observação | Pronto? |
|---|---|---|---|
| Branch/worktree real | Não confirmado neste controle | ZIP analisado não representa necessariamente o estado Git local | ⚠️ Confirmar |
| Baseline funcional | Problema reproduzido conceitualmente e por inspeção | perguntas sobre “o que falta” podem retornar última movimentação, `pendencias`, situação ou resposta genérica | ⚠️ Registrar no worktree |
| `situacao` | Campo recebido/persistido | chatbot não possui motor oficial próprio para derivar toda a situação estatística | ⚠️ Revisar fonte |
| Inferência no normalizador | Heurística auxiliar | normalização possui heurística para `PENDENTE/BAIXADO`; não equivale ao mapeamento oficial completo | ❌ Não usar como fonte final |
| `pendencias` | Semântica inadequada para “o que falta” | pode conter sinal auxiliar baseado em última movimentação | ❌ Separar conceitos |
| Última movimentação | Disponível | descreve evento já ocorrido | ✅ Dado histórico |
| Movimento faltante | Não representado explicitamente | não há contrato factual dedicado | ❌ Ausente |
| Regra PENDENTE → saída | Não implementada no runtime do chatbot | depende do mapeamento oficial/operacional | ❌ Bloqueante |
| Fluxograma CNJ | Fonte parcial disponível | contém Situação 88 e eventos/situações de baixa/finalização relevantes | ⚠️ Inventariar |
| Mapeamento citado pela Natália/Leonardo | Ainda não incorporado a este controle | citado como referência central do projeto | ❌ Obter/validar |
| Identificadores das movimentações | Necessidade não fechada | regras podem depender de códigos/situações; confirmar o que o coletor bruto oferece e o que a normalização preserva | ⚠️ Auditar |
| `process_event_extractor.py` | Existe | extrai categorias/eventos de modo determinístico | ⚠️ Reconciliar |
| `meta_rules.py` | Existe, mas provisório | não deve ser promovido automaticamente a motor oficial | ❌ Não suficiente |
| Resolver de consulta | Sem semântica específica de resolução | perguntas distintas podem cair em `generic_process`/rotas diferentes | ❌ Ajustar depois do motor |
| Agent 3 | Comportamento inadequado para resolução | `pending_issues` usa `pendencias`, não calcula transição | ❌ Ajustar |
| Agent 4 | Renderer | só consegue comunicar os fatos que Agent 3 entrega | ⚠️ Ajustar depois |
| LLM | Não é a causa estrutural principal | muitos caminhos de pendência são determinísticos | ✅ Manter secundária |
| Testes de negócio | Insuficientes | existe cobertura de “há pendência?”, não da função “qual movimento falta?” | ❌ Criar |
| Documentação da nova regra | Não existe | deve registrar fonte, contrato e limitações | ❌ Criar/atualizar |

**Conclusão do baseline:** a funcionalidade está `NOT_READY` porque falta fechar a fonte de verdade da transição, confirmar os dados necessários e implementar um motor determinístico antes de adaptar os Agents.

---

# 3. Bloqueios e dependências abertas

| ID | Dependência/Bloqueio | Estado | Impacta | Como fechar |
|---|---|---|---|---|
| B01 | Mapeamento oficial/operacional completo de pendência/baixa ainda não consolidado | `OPEN` | P1, P3 e tudo depois | obter o mapeamento citado no projeto + validar fluxograma/tabelas aplicáveis |
| B02 | Não está confirmado se todos os códigos/identificadores exigidos pela regra chegam no dado bruto | `OPEN` | P2/P3 | auditar retorno bruto do coletor e normalização |
| B03 | Semântica atual de `pendencias` conflita com “movimento faltante” | `CONFIRMED` | P2/P4/P5 | separar contrato/uso |
| B04 | Regras existentes em `meta_rules.py` são provisórias | `CONFIRMED` | P3 | reconciliar somente após P1 |
| B05 | Resolver não diferencia listagem de pendência e resolução de pendência | `CONFIRMED` | P4 | criar semântica após motor factual existir |
| B06 | Testes atuais não protegem o requisito central | `CONFIRMED` | P6/P7 | criar testes de negócio focados |

> Fechar um bloqueio não implica validar automaticamente os IDs dependentes.

---

# 4. Gates macro

| Gate | Descrição | Estado inicial | Critério para fechar |
|---|---|---:|---|
| G0 | Baseline e governança | `READY` | branch/worktree, baseline e escopo negativo registrados |
| G1 | Fonte de verdade | `READY` | mapeamento oficial inventariado e contrato da regra aprovado |
| G2 | Dados suficientes | `TODO` | dados brutos/normalizados suportam as regras ou limitações estão formalizadas |
| G3 | Motor de domínio | `TODO` | BAIXADO/PENDENTE e movimento faltante resolvidos deterministicamente com evidência |
| G4 | Integração no chatbot | `TODO` | resolver + Agent 3 + papel da LLM alinhados ao motor |
| G5 | Resposta e testes | `TODO` | Agent 4 + cenários BAIXADO/PENDENTE/indeterminado aprovados |
| G6 | Fechamento | `TODO` | regressão, documentação, diff e rastreabilidade aprovados |

---

# 5. Registro de fontes e decisões de domínio

Esta seção é obrigatória porque a funcionalidade depende de regras externas ao raciocínio livre do chatbot.

| Fonte ID | Fonte | Estado | O que ela define | Autoridade/validação | Evidência/observação |
|---|---|---|---|---|---|
| F01 | Fluxograma CNJ — Meta 1/Meta 2 fornecido ao projeto | `AVAILABLE_PARTIAL` | Situação 88, movimentos/situações relacionados a julgamento, baixa e finalização | precisa ser confrontado com escopo real do projeto | fonte disponível, mas não assumir que sozinha cobre todos os casos |
| F02 | Mapeamento feito no início do projeto citado pela professora Natália/Leonardo | `MISSING` | esperado como referência para movimentos que retiram o processo da situação pendente | precisa ser obtido/validado | bloqueio B01 |
| F03 | Heurística de `normalizer.py` | `NON_AUTHORITATIVE` | inferência auxiliar de situação | código atual, não regra oficial completa | não usar como substituto de F01/F02 |
| F04 | `meta_rules.py` | `PROVISIONAL` | regras auxiliares de metas/eventos | código atual marcado/projetado como provisório | revisar após fechar F01/F02 |
| F05 | Dados reais do coletor/PJe | `TO_AUDIT` | eventos/códigos efetivamente disponíveis | fonte factual dos processos | necessário para B02 |

### Regra de uso das fontes

```text
FONTE OFICIAL / HOMOLOGADA
        ↓
regra estruturada
        ↓
dados reais do processo
        ↓
motor determinístico
        ↓
conclusão factual
        ↓
Agents/LLM apenas explicam
```

Se não houver fonte suficiente:

```text
não determinar movimento faltante
→ registrar limitação
→ responder de forma conservadora
```

---

# 6. Plano de commits sugerido

Os commits abaixo são **unidades lógicas sugeridas**, não autorização automática para executar `git commit`.

| Commit planejado | IDs principais | Mensagem sugerida | Estado | Commit real |
|---|---|---|---|---|
| C00 | P0 + documentos operacionais | `docs(pending): establish pending-resolution work plan` | `READY` | — |
| C01 | PEND-P1-001, PEND-P1-002 | `docs(domain): formalize pending transition rules` | `TODO` | — |
| C02 | PEND-P2-001, PEND-P2-002 | `refactor(collection): preserve pending-resolution event data` | `TODO` | — |
| C03 | PEND-P2-003 | `fix(domain): separate pending records from missing events` | `TODO` | — |
| C04 | PEND-P3-001..003 | `feat(domain): add deterministic pending resolution` | `TODO` | — |
| C05 | PEND-P3-004 | `refactor(domain): reconcile event extraction and meta rules` | `TODO` | — |
| C06 | PEND-P4-001 | `feat(chat): route pending-resolution queries explicitly` | `TODO` | — |
| C07 | PEND-P4-002, PEND-P4-003 | `feat(chat): consume deterministic pending analysis` | `TODO` | — |
| C08 | PEND-P5-001..003 | `fix(chat): render pending and closed-state answers safely` | `TODO` | — |
| C09 | PEND-P6-001..005 | `test(chat): cover pending-resolution business behavior` | `TODO` | — |
| C10 | PEND-P7-* | `chore(pending): validate and document pending resolution` | `TODO` | — |

### Observação sobre granularidade

Se a auditoria P2 comprovar que **nenhuma alteração de modelo/normalização é necessária**, C02 pode ser marcado `SUPERSEDED`/`NOT_NEEDED` e a decisão deve ser registrada; não criar commit vazio.

Se P3 exigir mudanças pequenas em arquivos já alterados por C03/C05, commits podem ser reorganizados, desde que os IDs cobertos continuem rastreáveis.

---

# 7. Controle por item

## P0 — Baseline e proteção contra regressão

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P0-001 | `VALIDATED` | C00 | checklist/controle; nenhum código obrigatório | branch, hash-base, worktree e alterações preexistentes registrados | — |
| PEND-P0-002 | `VALIDATED` | C00 | testes/controle | suíte atual + respostas baseline PENDENTE/BAIXADO registradas | — |
| PEND-P0-003 | `VALIDATED` | C00 | checklist/controle/docs | escopo negativo confirmado e preservado no diff | — |

## P1 — Fonte de verdade e regra de negócio

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P1-001 | `READY` | C01 | docs/regra/fonte | F01/F02 e fontes complementares inventariadas; regras oficiais vs. provisórias separadas | — |
| PEND-P1-002 | `TODO` | C01 | contrato/regra/docs | estrutura representa E/OU, aplicabilidade, estados, eventos e fonte sem LLM | — |

## P2 — Dados necessários

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P2-001 | `TODO` | C02 | coletor/modelos/docs/controle | matriz dado bruto → normalizado → regra; perdas identificadas | — |
| PEND-P2-002 | `TODO` | C02 | normalizer/modelos/repository/testes, se necessário | identificadores exigidos preservados; compatibilidade/testes aprovados | — |
| PEND-P2-003 | `TODO` | C03 | normalizer/contratos/Agent 3/docs/testes | `pendencias` não alimenta `required_event` por equivalência semântica indevida | — |

## P3 — Motor determinístico

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P3-001 | `TODO` | C04 | DTO/serviço de domínio + testes | contrato diferencia vazio, desconhecido, resolvido e pendente | — |
| PEND-P3-002 | `TODO` | C04 | motor + testes | BAIXADO reconhecido de forma prioritária com evidência | — |
| PEND-P3-003 | `TODO` | C04 | motor + testes | regra + histórico produzem condições satisfeitas/ausentes e evento requerido | — |
| PEND-P3-004 | `TODO` | C05 | `meta_rules.py`, extractor e/ou serviço compartilhado + testes | não existem fontes de verdade conflitantes para baixa | — |

## P4 — Roteamento e Agent 3

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P4-001 | `TODO` | C06 | resolver/router + testes | `pending_list`, `pending_reason` e `pending_resolution` diferenciados | — |
| PEND-P4-002 | `TODO` | C07 | Agent 3/orquestração/DTO + testes | Agent 3 consome resultado do motor e não ecoa `pendencias` como “o que falta” | — |
| PEND-P4-003 | `TODO` | C07 | prompts/config/docs/testes, se necessário | conclusão factual permanece estável independentemente da LLM | — |

## P5 — Agent 4 e resposta

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P5-001 | `TODO` | C08 | Agent 4/renderer + testes | BAIXADO informado explicitamente; nenhum movimento faltante inventado | — |
| PEND-P5-002 | `TODO` | C08 | Agent 4/renderer + testes | PENDENTE exibe estado, fatos já ocorridos e requisito faltante | — |
| PEND-P5-003 | `TODO` | C08 | Agent 4/renderer + testes | falta de regra/dado gera limitação explícita, não palpite | — |

## P6 — Testes de negócio

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P6-001 | `TODO` | C09 | testes | variações sobre BAIXADO produzem semântica correta | — |
| PEND-P6-002 | `TODO` | C09 | testes/fixtures | regra conhecida identifica requisito faltante exato | — |
| PEND-P6-003 | `TODO` | C09 | testes | formulações equivalentes roteiam corretamente | — |
| PEND-P6-004 | `TODO` | C09 | testes | casos sem regra/dado degradam explicitamente | — |
| PEND-P6-005 | `TODO` | C09 | testes | `generate_text()` pode falhar sem alterar conclusão factual suportada | — |

## P7 — Regressão, documentação e fechamento

| ID | Status | Commit planejado | Arquivos esperados | Evidência para `VALIDATED` | Commit real |
|---|---|---|---|---|---|
| PEND-P7-001 | `TODO` | C10 | testes/controle | suíte focada + regressão completa sem falha nova não explicada | — |
| PEND-P7-002 | `TODO` | C10 | docs/README/arquitetura | regra, fonte, dados, motor, Agents e limitações documentados | — |
| PEND-P7-003 | `TODO` | C10 | controle + diff | diff revisado, `git diff --check`, commits/evidências registrados | — |
| PEND-P7-004 | `TODO` | C10 | checklist/controle | gate funcional integral satisfeito | — |

---

# 8. Registro cronológico de execução

Adicionar uma linha **somente quando houver evento real**.

| Data/hora | ID | Evento | Status anterior → novo | Evidência curta | Commit/hash |
|---|---|---|---|---|---|
| 17/09/2026 | BASELINE | Diagnóstico estrutural da resolução de pendências consolidado | — → `NOT_READY` | ausência de motor de transição; `pendencias` não representa requisito faltante; Agent 3 não calcula saída | — |
| 17/09/2026 | BASELINE | Fluxograma CNJ identificado como fonte parcial relevante | — | Situação 88 e eventos/situações de baixa/finalização precisam ser reconciliados com o mapeamento do projeto | — |
| 17/09/2026 | PLANEJAMENTO | Checklist operacional criada | — | `CHECKLIST_RESOLUCAO_PENDENCIAS_CHATBOT.md` | — |
| 17/09/2026 | PLANEJAMENTO | Controle de progresso criado | — | arquivo auxiliar vinculado à checklist; nenhum código funcional alterado | — |
| 24/09/2026 | PEND-P0-001 | Início da confirmação de branch e estado inicial | `READY` → `IN_PROGRESS` | investigação Git não destrutiva iniciada; worktree preservado | — |
| 24/09/2026 | PEND-P0-002 | Início do baseline técnico e funcional | `READY` → `IN_PROGRESS` | comando oficial identificado e execução local iniciada | — |
| 24/09/2026 | PEND-P0-003 | Início do congelamento do escopo negativo | `READY` → `IN_PROGRESS` | restrições da fase confrontadas com o worktree e a investigação realizada | — |
| 24/09/2026 | PEND-P0-001 | Estado inicial registrado | `IN_PROGRESS` → `VALIDATED` | branch `feat/resolucao-pendencias-processual`; base `230a24e990b4d94217672b5ba6ce4fe61e62be17`; quatro caminhos não rastreados preexistentes | — |
| 24/09/2026 | PEND-P0-002 | Baseline técnico e funcional concluído | `IN_PROGRESS` → `VALIDATED` | suíte completa: 143 passed; 12 cenários funcionais registrados; falha de ordem dos testes isolada e classificada | — |
| 24/09/2026 | PEND-P0-003 | Escopo negativo confirmado | `IN_PROGRESS` → `VALIDATED` | nenhuma alteração funcional, dependência, baseline ou item P1+ introduzido | — |

> Não adicionar transições `READY → IN_PROGRESS` retroativamente.  
> Elas devem ser registradas quando cada item realmente começar no worktree real.

## Evidências da FASE P0 — 24/09/2026

### PEND-P0-001 — Branch e estado inicial

```text
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
DATA_HORA: 24/09/2026 13:08:51 -03:00

BRANCH: feat/resolucao-pendencias-processual
COMMIT_BASE: 230a24e990b4d94217672b5ba6ce4fe61e62be17
STAGED: nenhum
MODIFICADOS_NAO_STAGED: nenhum arquivo rastreado
UNTRACKED:
- .codex/ (inclui .codex/rules/safety.rules)
- AGENTS.md
- CONTROLE_PROGRESSO_COMMITS_RESOLUCAO_PENDENCIAS_CHATBOT.md
- docs/CHECKLIST_RESOLUCAO_PENDENCIAS_CHATBOT.md

ALTERACOES_PREEXISTENTES: todos os caminhos acima já estavam não rastreados antes desta execução; as edições desta fase ficaram restritas aos dois documentos operacionais já existentes e não rastreados.
COMANDOS: git branch --show-current; git rev-parse HEAD; git status --short; git diff --cached --name-status; git diff --name-status; git ls-files --others --exclude-standard
PRESERVACAO: nenhum reset, clean, restore, checkout, troca de branch, commit ou push executado.
ARQUIVOS_MODIFICADOS_NESTA_FASE: docs/CHECKLIST_RESOLUCAO_PENDENCIAS_CHATBOT.md; CONTROLE_PROGRESSO_COMMITS_RESOLUCAO_PENDENCIAS_CHATBOT.md
COMMIT_REAL: —
```

### PEND-P0-002 — Baseline técnico

Ambiente observado: Windows/PowerShell; Python global 3.12.10; ambiente virtual local `chatbot_processual_ai/.venv`; pytest 9.1.1. O comando oficial documentado é `python -m pytest tests -q`, executado dentro de `chatbot_processual_ai/`.

| Execução | Resultado | Classificação |
|---|---|---|
| `python -m pytest tests -q` com o Python global | não coletou: `No module named pytest` | ambiental; ambiente global sem pytest |
| `.\.venv\Scripts\python.exe -m pytest tests -q` | `143 passed`, `0 failed`, `0 skipped/xfailed`, 1 warning, 4,44 s | baseline completo aprovado |
| `.\.venv\Scripts\python.exe -m pytest tests/test_rag_base.py tests/test_p3_collector_integration.py tests/test_collector_adapter.py -q` | `96 passed`, `1 failed`, 2 warnings, 2,46 s | falha preexistente dependente da ordem: o teste de lazy import encontra `trt18_collector` já carregado pelo arquivo anterior |
| `.\.venv\Scripts\python.exe -m pytest tests/test_rag_base.py -q --disable-warnings` | `23 passed`, 1 warning, 1,57 s | focado: resolver/router, Agent 3, Agent 4, pendências, situação e movimentações |
| `.\.venv\Scripts\python.exe -m pytest tests/test_p3_collector_integration.py -q --disable-warnings` | `12 passed`, 1 warning, 1,14 s | focado: integração de coleta/rota existente |
| `.\.venv\Scripts\python.exe -m pytest tests/test_collector_adapter.py -q --disable-warnings` | `62 passed`, 1 warning, 0,20 s | focado: contrato de movimentações/pendências e lazy import em isolamento |

Aviso ambiental comum: `PytestCacheWarning` por acesso negado ao criar `.pytest_cache`/`pytest-cache-files-*`; não afetou a execução dos testes. A falha combinada não é regressão desta fase: nenhum código funcional foi alterado, a suíte oficial passa e o mesmo teste passa isoladamente e na ordem oficial atual. A remoção dos seis diretórios `chatbot_processual_ai/pytest-cache-files-*` gerados pelo pytest foi tentada após validação individual dos caminhos, mas o Windows também negou acesso; os dois diretórios homônimos já existentes na raiz não foram tocados.

### PEND-P0-002 — Baseline funcional

Dados usados: o processo BAIXADO sanitizado de `data/sample_processes.json`, somente leitura, e uma cópia sintética em memória marcada como PENDENTE, sem a movimentação final e com `pendencias = [{"descricao": "Aguardando baixa definitiva"}]`. Nenhum banco, snapshot, JSON/CSV ou fixture foi alterado. As chamadas de geração foram interceptadas apenas para contar tentativas e impedir acesso externo.

| Estado | Pergunta | Intenção / rota | Foco do Agent 3 | Resposta final observada | LLM / RAG | Fontes efetivamente usadas |
|---|---|---|---|---|---|---|
| BAIXADO | Quais pendências existem? | `process_question` / `structured` | `pending_issues` | “Nos dados consultados, não há pendências registradas.” + ressalva de que isso não prova inexistência externa | nenhuma / `not_needed` | `pendencias` vazio |
| BAIXADO | O que falta para sair da pendência? | `process_question` / `structured` | `pending_issues` | mesma resposta de ausência de pendências, sem dizer que já está BAIXADO | nenhuma / `not_needed` | `pendencias` vazio |
| BAIXADO | Por que continua pendente? | `process_question` / `hybrid` | `pending_issues` | mesma resposta de ausência de pendências, sem confrontar a premissa com BAIXADO | nenhuma / `unavailable` | `pendencias` vazio; tentativa de RAG sem conteúdo usado |
| BAIXADO | O que precisa acontecer para ser baixado? | `unclear` / `structured` | `current_status` | “o processo consta como BAIXADO” e última movimentação “Arquivado definitivamente”, em 05/02/1984 | Agent 1 tentou geração; Agents 3/4 não / `not_needed` | situação + última movimentação |
| BAIXADO | Qual movimentação ainda falta? | `process_question` / `structured` | `generic_process_question` | informa BAIXADO e a última movimentação; pede que o usuário especifique o tema | Agent 3 tentou geração; Agents 1/4 não / `not_needed` | situação + última movimentação |
| BAIXADO | Qual é o próximo movimento necessário? | `unclear` / `structured` | `generic_process_question` | informa BAIXADO e a última movimentação; pede que o usuário especifique o tema | Agent 1 tentou geração; Agents 3/4 não / `not_needed` | situação + última movimentação |
| PENDENTE | Quais pendências existem? | `process_question` / `structured` | `pending_issues` | lista literalmente `{"descricao": "Aguardando baixa definitiva"}` | nenhuma / `not_needed` | `pendencias` |
| PENDENTE | O que falta para sair da pendência? | `process_question` / `structured` | `pending_issues` | lista literalmente o conteúdo de `pendencias`; não calcula condição/movimentação faltante | nenhuma / `not_needed` | `pendencias` |
| PENDENTE | Por que continua pendente? | `process_question` / `hybrid` | `pending_issues` | lista literalmente o conteúdo de `pendencias`; não explica causalidade processual | nenhuma / `empty` | `pendencias`; RAG sem resultado usado |
| PENDENTE | O que precisa acontecer para ser baixado? | `unclear` / `structured` | `current_status` | informa PENDENTE e a última movimentação “Trânsito em julgado”, em 10/10/1983 | Agent 1 tentou geração; Agents 3/4 não / `not_needed` | situação + última movimentação |
| PENDENTE | Qual movimentação ainda falta? | `process_question` / `structured` | `generic_process_question` | informa PENDENTE e a última movimentação; pede que o usuário especifique o tema | Agent 3 tentou geração; Agents 1/4 não / `not_needed` | situação + última movimentação |
| PENDENTE | Qual é o próximo movimento necessário? | `unclear` / `structured` | `generic_process_question` | informa PENDENTE e a última movimentação; pede que o usuário especifique o tema | Agent 1 tentou geração; Agents 3/4 não / `not_needed` | situação + última movimentação |

Conclusão factual do baseline: nenhuma das 12 respostas calcula uma movimentação realmente faltante. As perguntas de lista/motivo reutilizam `pendencias`; outras formulações caem em situação/última movimentação ou em foco genérico. O resolver produz `target=generic_process` em todas as seis formulações. Há uma chamada de LLM tentada somente nos casos indicados, mas as respostas observadas permanecem no fallback determinístico; Agent 4 não chamou LLM. RAG só foi solicitado em “Por que continua pendente?” e não forneceu conteúdo à resposta.

### PEND-P0-003 — Escopo negativo congelado

Esta frente não autoriza, salvo dependência técnica comprovadamente indispensável: trocar 1B/4B/7B/8B como solução principal; reescrever o RAG; refatorar o frontend; alterar o simulador de metas de forma independente; refatorar agentes não relacionados; adicionar rules engine pesado; adicionar dependência por conveniência; inventar regra jurídica/processual; inferir regra ausente com LLM; reescrever a arquitetura; ou corrigir problemas fora do escopo apenas porque foram encontrados.

Nenhuma dependência indispensável desse tipo foi descoberta na P0. O problema de ordem de testes e o aviso de cache foram somente registrados. Nenhuma correção foi aplicada.

### Checkpoint da fase

```text
FASE: P0
IDS_DA_FASE: PEND-P0-001, PEND-P0-002, PEND-P0-003
STATUS_DOS_IDS: VALIDATED, VALIDATED, VALIDATED
BLOQUEIOS_ABERTOS: nenhum para a conclusão da P0
RISCOS_RESIDUAIS: falha preexistente dependente da ordem em seleção combinada; cache do pytest sem permissão (os diretórios temporários gerados não puderam ser removidos por acesso negado); baseline PENDENTE sintético por ausência de caso PENDENTE no sample local
TESTES_FOCADOS: 23 + 12 + 62 passed quando executados por arquivo
REGRESSAO: 143 passed; 0 failed; 0 skipped/xfailed
FONTES_DE_REGRA_CONFIRMADAS: não aplicável à P0; nenhuma regra foi criada ou alterada
DADOS_CONFIRMADOS: sample BAIXADO sanitizado + cópia PENDENTE sintética em memória
DIFF_REVISADO: sim
CHECKPOINT_READY: SIM
CHECKPOINT_CRIADO: SIM
COMMIT_REAL: —
PROXIMA_FASE_AUTORIZADA: NÃO
JUSTIFICATIVA: execução explicitamente limitada à FASE P0; P1 depende de novo prompt após revisão humana
```

---

# 9. Modelo de atualização após cada item

Copiar e preencher:

```text
ID: PEND-PX-XXX
STATUS_ANTERIOR:
STATUS_FINAL:
DATA_HORA:

OBJETIVO_DO_ITEM:
DIAGNOSTICO_CONFIRMADO:

FONTE_DE_REGRA_USADA:
VERSAO_REFERENCIA_DA_FONTE:
REGRA_DE_NEGOCIO_AFETADA:

DADOS_INSPECIONADOS:
DADOS_NECESSARIOS:
DADOS_AUSENTES:
FALLBACK_APROVADO:

ARQUIVOS_INSPECIONADOS:
ARQUIVOS_MODIFICADOS:
RESUMO_DIFF:

TESTES_EXECUTADOS:
RESULTADOS:
REGRESSAO_EXECUTADA:

LLM_ENVOLVIDA: sim/não
PAPEL_DA_LLM:
CONCLUSAO_FACTUAL_DEPENDE_DA_LLM: sim/não

DOCUMENTACAO_ATUALIZADA:
RISCOS_RESIDUAIS:
BLOQUEIOS_ABERTOS:

COMMIT_SUGERIDO:
COMMIT_REAL:

CHECKPOINT_DA_FASE:
OBSERVACOES:
```

### Regra especial para itens de domínio

Para P1/P3, sempre preencher:

```text
FONTE_DE_REGRA_USADA:
O_QUE_A_FONTE_PROVA:
O_QUE_A_FONTE_NAO_PROVA:
REGRA_IMPLEMENTADA:
CASOS_NAO_COBERTOS:
```

Isso evita transformar interpretação informal em regra oficial sem rastreabilidade.

---

# 10. Modelo de registro de commit

```text
COMMIT_ID_LOGICO: CXX
COMMIT_SUGERIDO: tipo(escopo): descrição
COMMIT_REAL: <hash ou PENDING>

IDS_COBERTOS:
ARQUIVOS_PRINCIPAIS:

FONTE_DE_REGRA_RELACIONADA:
ALTERA_CONCLUSAO_PENDENTE_BAIXADO: sim/não
ALTERA_DADO_NORMALIZADO: sim/não
ALTERA_ROTEAMENTO: sim/não
ALTERA_AGENT3: sim/não
ALTERA_AGENT4: sim/não

TESTES_ANTES_DO_COMMIT:
RESULTADO:
REGRESSAO:
DIFF_REVISADO: sim/não
GIT_DIFF_CHECK: pass/fail/não executado
SEGREDOS_VERIFICADOS: sim/não

RISCO_RESIDUAL:
OBSERVACOES:
```

---

# 11. Modelo de checkpoint de fase

Usar somente quando **todos os itens obrigatórios da fase** tiverem sido revisados.

```text
FASE: PX
IDS_DA_FASE:
STATUS_DOS_IDS:

BLOQUEIOS_ABERTOS:
RISCOS_RESIDUAIS:

TESTES_FOCADOS:
REGRESSAO:

FONTES_DE_REGRA_CONFIRMADAS:
DADOS_CONFIRMADOS:

DIFF_REVISADO:
CHECKPOINT_READY: SIM/NÃO
CHECKPOINT_CRIADO: SIM/NÃO
COMMIT_REAL:

PROXIMA_FASE_AUTORIZADA: SIM/NÃO
JUSTIFICATIVA:
```

---

# 12. Matriz de responsabilidade factual

Esta matriz ajuda a impedir que uma camada assuma responsabilidade que pertence a outra.

| Informação | Fonte/camada responsável | LLM pode decidir? | Estado atual |
|---|---|---:|---|
| Movimentos já ocorridos | coletor/repository | Não | disponível |
| Situação coletada | coletor/normalização | Não | disponível, revisar autoridade |
| Regra que define saída da pendência | fonte oficial + motor de domínio | Não | ausente no runtime |
| Condições já satisfeitas | motor determinístico | Não | a implementar |
| Condições faltantes | motor determinístico | Não | a implementar |
| Movimento/evento requerido | motor determinístico com regra oficial | Não | a implementar |
| Limitação por dado ausente | motor/serviço | Não | a implementar |
| Classificar formulação do usuário | resolver; LLM como fallback | Sim, com validação | parcial |
| Explicação em linguagem natural | Agent 4 / LLM opcional | Sim | existente |
| Alterar conclusão factual | nenhuma LLM | **Não** | deve permanecer proibido |

---

# 13. Matriz de prontidão atual

| Dimensão | Estado | Bloqueio principal |
|---|---|---|
| Baseline operacional | 🟡 A confirmar no Git real | branch/worktree e execução local ainda precisam ser registrados |
| Fonte de regra | 🔴 Incompleta | obter/consolidar mapeamento citado pela equipe |
| Contrato de regra | 🔴 Ausente | depende de P1-001 |
| Dados do coletor | 🟡 Parcialmente conhecidos | confirmar códigos/identificadores necessários |
| Normalização | 🟡 Funcional, insuficiente para a nova função | pode perder semântica necessária; auditar |
| Campo `pendencias` | 🔴 Semântica incompatível | não representa movimento faltante |
| Motor de resolução | 🔴 Ausente | depende de fonte + dados |
| Roteamento | 🔴 Insuficiente | não distingue resolução de pendência |
| Agent 3 | 🔴 Insuficiente | usa `pendencias` em vez de conclusão do motor |
| Agent 4 | 🟡 Aproveitável | depende de receber fatos corretos |
| LLM | 🟢 Não bloqueante | não deve ser fonte da regra |
| Testes de negócio | 🔴 Ausentes | requisito central não está protegido |
| Documentação final | 🔴 Pendente | só fechar após implementação |
| Estado global | 🔴 `NOT_READY` | G1/G2/G3 abertos |

---

# 14. Critério de mudança do estado global

## `NOT_READY`

Usar enquanto qualquer um destes pontos estiver aberto:

- fonte oficial incompleta;
- dados necessários desconhecidos;
- motor determinístico inexistente;
- conclusão factual depender de hipótese/LLM.

## `DOMAIN_READY`

Pode ser usado quando:

- P1 está `VALIDATED`;
- P2 confirmou os dados necessários;
- regras possuem fonte rastreável;
- sabemos exatamente o que o motor deverá calcular.

**Não significa que o chatbot já está corrigido.**

## `IMPLEMENTATION_READY`

Pode ser usado quando:

- motor determinístico está validado;
- PENDENTE/BAIXADO e requisito faltante possuem resultado estruturado;
- integração com Agents ainda pode estar em andamento.

## `READY_FOR_VALIDATION`

Somente quando:

- P3, P4, P5 e P6 estão validados;
- cenários centrais funcionam;
- nenhuma LLM inventa regra;
- resta apenas fechamento/regressão/documentação.

## `READY_FOR_MERGE`

Somente quando:

- P7 está validado;
- regressão completa passou;
- documentação está coerente;
- diff foi revisado;
- `git diff --check` passou;
- commits reais estão registrados;
- riscos adiados estão explicitamente aceitos.

---

# 15. Critério de fechamento dos bloqueios atuais

## B01 — Fonte oficial

Fechar somente quando:

- mapeamento citado pela equipe estiver disponível ou sua ausência tiver sido formalmente resolvida;
- fluxograma/tabelas aplicáveis estiverem identificados;
- houver consenso de quais regras o software deve executar;
- fonte e versão estiverem registradas.

## B02 — Dados suficientes

Fechar somente quando:

- cada campo exigido pelas regras tiver origem identificada;
- soubermos se o coletor o recebe;
- soubermos se a normalização o preserva;
- ausência tiver política explícita.

## B03 — `pendencias`

Fechar somente quando:

- seu significado estiver documentado;
- não for mais usado para representar movimento faltante;
- testes impedirem regressão.

## B04 — Regras provisórias

Fechar somente quando:

- `meta_rules.py` e `process_event_extractor.py` tiverem fronteiras claras;
- nenhuma regra provisória competir com a fonte oficial.

## B05 — Resolver

Fechar somente depois de G3:

- semântica de `pending_resolution` estiver definida;
- frases equivalentes seguirem o mesmo caminho.

## B06 — Testes

Fechar somente quando P6 estiver `VALIDATED`.

---

# 16. Próximo passo operacional

**Não iniciar pelo Agent 3.**

Ordem imediata:

1. `PEND-P0-001` — confirmar branch, hash-base e worktree real;
2. `PEND-P0-002` — registrar baseline executável e respostas atuais;
3. `PEND-P0-003` — congelar escopo;
4. `PEND-P1-001` — reunir/validar todas as fontes do mapeamento;
5. somente depois iniciar `PEND-P1-002`.

Fluxo de decisão:

```text
Temos regra oficial suficiente?
        |
     não ─────→ BLOCKED
        |
       sim
        v
Os dados coletados permitem aplicar a regra?
        |
     não ─────→ P2: corrigir contrato/coleta/normalização
        |
       sim
        v
Construir e validar motor determinístico
        |
        v
Somente então alterar resolver / Agent 3 / Agent 4
```

---

# 17. Definition of Done deste controle

Este arquivo está cumprindo seu papel quando, para qualquer alteração relevante, é possível responder rapidamente:

1. **Qual ID da checklist autorizou a mudança?**
2. **Qual problema concreto aquele ID resolveu?**
3. **Qual fonte de regra sustentou a conclusão?**
4. **Quais dados foram usados?**
5. **Quais arquivos mudaram?**
6. **Quais testes provaram o comportamento?**
7. **Existe risco ou limitação residual?**
8. **Qual commit real contém a alteração?**
9. **A conclusão factual depende de LLM?** — para a regra central, a resposta deve ser `não`.
10. **Qual é o próximo item autorizado?**

Se uma dessas respostas não puder ser encontrada, o item ainda não possui rastreabilidade operacional suficiente.
