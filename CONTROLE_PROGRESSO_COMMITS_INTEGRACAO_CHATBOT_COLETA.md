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

## FASE P4 — início da implementação integrada

```text
DATA_HORA: 2026-09-11 -03:00
IDS: INT-COL-P4-001, INT-COL-P4-002, INT-COL-P4-003
STATUS_ANTERIOR: TODO
STATUS_DESTA_ETAPA: IN_PROGRESS
PRECONDICAO: P3 e C03 confirmados como VALIDATED no HEAD 485ee7dca07b2e0eb8fda255080991c60e264561; local-first, persistência exclusiva de sucesso, releitura SQLite, reutilização e rollback permanecem presentes no código e nos testes.
DIAGNOSTICO_INICIAL: o adapter preserva os sete estados, porém a camada pública de análise trata especificamente apenas not_found/missing_number; os demais estados degradados não possuem ainda resposta pública determinística própria no fluxo observado pelo consumidor.
ESCOPO: tradução pública segura, preservação da API e testes observáveis dos cinco estados negativos, rollback/preservação e regressão LOCAL_HIT/COLLECTED; sem P5, frontend, schema, retry, rede ou coleta real.
G4: IN_PROGRESS.
C04: TODO; COMMIT_REAL: —.
```

---

## FASE P4 — implementação integrada concluída

```text
DATA_HORA: 2026-09-11 -03:00
IDS: INT-COL-P4-001, INT-COL-P4-002, INT-COL-P4-003
STATUS_ANTERIOR: IN_PROGRESS
STATUS_FINAL_DESTA_RODADA: IMPLEMENTED; validação reservada ao usuário.
DIAGNOSTICO_CONFIRMADO: Adapter e Agent 2 já preservavam os sete códigos, mas a análise determinística só distinguia not_found/missing_number; os demais estados chegavam à resposta com ausência genérica de dados. A mensagem de not_found também atribuía a ausência à coleta local, apesar de o estado ser exclusivamente remoto.
IMPLEMENTACAO: análise determinística agora traduz invalid_number, not_found, partial, blocked e failed para semânticas públicas distintas e seguras. O campo textual collection_status e o envelope HTTP foram preservados; nenhuma mudança de DTO, frontend, schema ou retry foi introduzida.
PERSISTENCIA_E_SEGURANCA: estados negativos permanecem sem process e sem chamada a persist; exceção técnica é convertida em FAILED no adapter com logging por categoria/classe, sem transportar mensagem bruta. Teste de substituição com falha no chunking confirmou rollback e preservação exata da árvore/chunks anteriores.
TESTES_NOVOS: 17 cenários em test_p4_failure_semantics.py — cinco estados via Agent 2, cinco via orquestrador, cinco via API ASGI, exceção técnica na fronteira e rollback com dado anterior.
TESTES_EXECUTADOS: `.venv\\Scripts\\python.exe -m pytest tests\\test_p4_failure_semantics.py -q -p no:cacheprovider` (17 passed); suíte focada de adapter/progresso/API/P3/P4 (111 passed); suíte completa `tests` (134 passed); coletor offline `entrada-de-dados/tests` (3 passed).
ARQUIVOS_FUNCIONAIS: chatbot_processual_ai/agents/agent3_process_analysis.py.
ARQUIVOS_TESTE: chatbot_processual_ai/tests/test_p4_failure_semantics.py.
DOCUMENTACAO_OPERACIONAL: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
EFEITOS_EXTERNOS: nenhum acesso a rede/TRT18, browser, Playwright, CAPTCHA, banco operacional, deploy, push ou commit; somente SQLite isolado removido pelo teste.
LIMITACAO_AMBIENTAL: uma tentativa inicial teve 16 passed e erro de setup por permissão no tmp global do pytest; a fixture foi tornada isolada como na P3 e a execução seguinte passou com 17 testes.
G4: IN_PROGRESS, aguardando validação do usuário.
C04: TODO; COMMIT_REAL: —.
COMMIT_CRIADO: não.
```

---

## FASE P6 — validação do checkpoint C06

```text
DATA_HORA: 2026-09-11 -03:00
CHECKPOINT_ENCONTRADO: f536ce2ce8f88847c3c49a4d59f5beefd9e1a9fe — test(integration): cover chatbot collector workflow.
REVISAO_DO_COMMIT: quatro arquivos, restritos à matriz automatizada backend/collector e aos dois registros operacionais P6; git diff HEAD^ HEAD --check passou; worktree estava limpo antes deste registro.
TESTES_REEXECUTADOS: suíte focada backend 143 passed em 4.73 s; suíte completa backend 143 passed em 3.74 s; suíte completa collector offline 16 passed em 0.52 s.
VALIDADO: P6-001 (regressão e frontend preservados), P6-002 (contrato produtor offline, cache-only e zero coleta externa) e P6-003 (matriz API/orquestrador/Agent 2/adapter/repository/SQLite, estados, reutilização e rollback).
P6_004: permanece BLOCKED. O commit não contém nem poderia conter evidência do aceite real; nenhum CNJ explicitamente autorizado foi fornecido e a limitação ambiental do Chromium permanece. O pedido genérico de validação não substitui o insumo processual nem comprova a cadeia real.
STATUS_FINAL: P6-001 VALIDATED; P6-002 VALIDATED; P6-003 VALIDATED; P6-004 BLOCKED; G6 BLOCKED; C06 BLOCKED com hash real registrado, ainda não aprovado como fechamento completo da fase.
P7: não iniciada.
COMMIT_DE_VALIDACAO: não criado.
```

---

## FASE P6 — aceite explícito da exceção ambiental e fechamento

```text
DATA_HORA: 2026-09-11 -03:00
DECISAO_DO_USUARIO: aceitar o impedimento do computador institucional, limitado e sem privilégios suficientes, como exceção para o aceite real controlado da P6.
EVIDENCIA_PRESERVADA: P6-001, P6-002 e P6-003 foram validadas por 143 testes backend e 16 testes collector offline; o checkpoint C06 foi auditado. P6-004 não acessou TRT18, não utilizou CNJ real e não produziu evidência de sucesso real.
ACEITE: P6-004 VALIDATED exclusivamente por decisão explícita do usuário, com ressalva ambiental permanente e sem reclassificar o teste não executado como sucesso técnico.
STATUS_FINAL: P6-001, P6-002, P6-003 e P6-004 VALIDATED; G6 e C06 VALIDATED no checkpoint f536ce2ce8f88847c3c49a4d59f5beefd9e1a9fe.
PENDENCIA_RESIDUAL: em ambiente autorizado e com Chromium Playwright disponível, executar futuramente um aceite real controlado com CNJ autorizado e banco isolado.
P7: não iniciada nesta rodada.
COMMIT_DE_ACEITE: não criado.
```

---

## FASE P4 — validação e fechamento do C04

```text
DATA_HORA: 2026-09-11 -03:00
IDS_AVALIADOS: INT-COL-P4-001, INT-COL-P4-002, INT-COL-P4-003
CHECKPOINT_ENCONTRADO: 259b5ed7a10261f72162f47377ffba38f3dcfb3a — fix(chat): preserve collector failure semantics.
ESCOPO_DO_COMMIT: quatro arquivos restritos à P4 — análise determinística, matriz de testes e dois registros operacionais; nenhum frontend, schema, dependência, configuração ou item P5.
DIAGNOSTICO_VALIDADO: somente NOT_FOUND comunica ausência remota no TRT18; INVALID_NUMBER, PARTIAL, BLOCKED e FAILED mantêm semânticas públicas distintas, seguras e sem processo ativo.
PERSISTENCIA_VALIDADA: os cinco estados negativos não alcançam persist; falha durante substituição transacional preserva exatamente árvore e chunks anteriores. LOCAL_HIT continua sem coleta/escrita e COLLECTED continua persistindo e relendo do SQLite.
SEGURANCA_VALIDADA: respostas e progresso não expõem traceback, exceção bruta, path SQLite, Playwright, CAPTCHA, cookie ou token; nenhuma mensagem promete retry automático.
TESTES_REEXECUTADOS_NO_COMMIT: P4 17 passed em 0.60 s; focados 111 passed em 1.64 s; regressão completa do chatbot 134 passed em 2.98 s; coletor offline 3 passed em 0.52 s.
REVISAO: worktree estava limpo antes deste registro; git diff HEAD^ HEAD --check passou; conteúdo e mensagem do checkpoint conferidos; nenhuma coleta real, rede, browser, banco operacional, deploy ou alteração de frontend ocorreu.
STATUS_FINAL: INT-COL-P4-001, INT-COL-P4-002 e INT-COL-P4-003 VALIDATED.
G4: VALIDATED.
C04: VALIDATED no commit 259b5ed7a10261f72162f47377ffba38f3dcfb3a.
P5: não iniciada; INT-COL-P5-001..004 permanecem TODO.
COMMIT_DE_VALIDACAO: não criado.
```

---

## INT-COL-P3-001 — registro detalhado

```text
ID: INT-COL-P3-001
DATA_HORA: 2026-09-09 09:49:34 -03:00
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Sol
MODELO_EXECUTADO: GPT-5 (Codex)
MOTIVO_DIVERGENCIA_MODELO: o ambiente identifica o agente como Codex baseado em GPT-5; GPT-5.6 Sol permaneceu como recomendação registrada.
DIAGNOSTICO_CONFIRMADO: o adapter já era a autoridade única do fluxo validate->lookup->collect e preservava os sete estados, mas não existia uma composição produtiva dos defaults canônicos. O Agent 2 ainda usa o wrapper local legado; conectá-lo neste item causaria lookup redundante ou anteciparia o consumo de CollectorResult reservado para P3-003.
PONTO_DE_COMPOSICAO: create_collector_adapter em chatbot_processual_ai/collector_adapter.py. A fábrica mantém o adapter como fronteira única e não altera Agent 2, API HTTP, frontend, sessão ou progresso.
DEPENDENCIAS_PRODUTIVAS: validate_process_number, find_process_by_number e collect_process são defaults substituíveis; collect_process continua importando tardiamente somente from trt18_collector import obter_processo. persist e reload permanecem parâmetros keyword-only obrigatórios para a composição posterior de P3-002, sem stubs produtivos ou sucesso aparente.
ORDEM_CONTAGEM: inválido=0 lookup/0 coleta; ativo=0 lookup/0 coleta no short-circuit legado; hit=1 lookup/0 coleta; miss válido=1 lookup/1 coleta; erro de lookup=1 lookup/0 coleta; estado remoto não persistível=1 lookup/1 coleta/0 persistência; duas tentativas independentes sem dado local=1 lookup e 1 coleta por tentativa, sem retry oculto. Ordem comprovada: validate->lookup->collect.
TESTES_NOVOS: 4 — composição produtiva em hit; composição produtiva em miss PARCIAL; duas chamadas independentes sem retry; short-circuit de processo ativo antes do lookup.
TESTES_PREEXISTENTES: 58 cenários focados do adapter continuaram verdes; matriz anterior cobre inválido, erro de lookup, os sete estados, invariantes, exceções, mensagens, import leve e bloqueio de socket.
COMANDOS_EXECUTADOS: .venv/Scripts/python.exe -m pytest tests/test_collector_adapter.py -q -p no:cacheprovider; .venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider; .venv/Scripts/python.exe -m pytest ../entrada-de-dados/tests -q -p no:cacheprovider; probe isolado de import leve; python -m trt18_collector.cli --help; git diff --check.
RESULTADOS: 62 testes focados passaram em 0.31 s; 105 testes do chatbot passaram em 2.20 s; 3 testes offline do package passaram em 0.48 s; import leve e CLI passaram. Zero falhas, warnings de teste e skips. git diff --check passou, com apenas avisos informativos de conversão LF/CRLF do Git.
CORRECOES_MINIMAS: adicionada somente a fábrica de composição e sua exportação pública; nenhuma lógica, estado ou tradução do adapter foi duplicada ou alterada.
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/collector_adapter.py; chatbot_processual_ai/tests/test_collector_adapter.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
EFEITOS_EXTERNOS_BLOQUEADOS: os testes novos usam fakes na fronteira do adapter; não houve rede, Playwright, browser, CAPTCHA, OCR, cache/debug real, SQLite real, Ollama, Qdrant ou coleta TRT18. O probe confirmou que importar collector_adapter não carrega trt18_collector, playwright, cv2 ou ddddocr.
REVISAO_DO_DIFF: diff completo restrito aos quatro arquivos autorizados; sem logs/debug temporários, segredos, dados pessoais, mudanças de contrato, dependências, persistência, outputs protegidos ou alterações acidentais. Worktree inicial estava limpo; avisos de diretórios temporários sem permissão eram preexistentes e foram preservados.
RISCOS_LIMITACOES: a fábrica ainda não pode ser instalada no fluxo conversacional até P3-002 fornecer persist/reload reais e P3-003 consumir CollectorResult. A validação ocorreu no venv existente, não em ambiente limpo. Diretórios temporários preexistentes sem permissão seguem intocados.
G3: IN_PROGRESS, pois somente P3-001 foi validado.
C03: TODO; COMMIT_REAL: —.
P3_002_P3_003_P3_004: não iniciados e permanecem TODO.
COMMIT_CRIADO: não.
```

---

## FASE P3 — registro de implementação integrada

```text
DATA_HORA: 2026-09-11 08:25:06 -03:00
IDS: INT-COL-P3-001, INT-COL-P3-002, INT-COL-P3-003, INT-COL-P3-004
STATUS_FINAL_DESTA_RODADA: IMPLEMENTED; validação reservada ao usuário.
PRECONDICAO: C02 confirmado no HEAD c01a5b50bc63413ee7a9734b02abd77dabf1a5d5; package trt18_collector, API leve, CollectorAdapter, CollectorResult, sete AdapterStatus, local-first, imports lazy e seams persist/reload presentes.
IMPLEMENTACAO: composição produtiva do adapter usa ingest_processes([process], source_name="trt18_collector") e find_process_by_number; COLLECTED somente após persistência e releitura válida. Agent 2 consome exclusivamente CollectorResult, ativa somente LOCAL_HIT/COLLECTED e preserva os demais estados discriminados em collection_status.
PROGRESSO: eventos seguros cobrem lookup local, necessidade de aquisição, persistência/reload e resultado; teste impede exposição de CAPTCHA, Playwright, cookie, token, stack trace, HTML bruto e path do SQLite.
REUTILIZACAO: testes com SQLite isolado comprovam processo ativo sem nova fronteira, nova sessão atendida localmente e reinício lógico atendido pelo mesmo banco, sempre sem recoleta.
PERSISTENCIA: teste de round-trip comprova sanitização de documento/id_documento e geração de chunks; teste de falha durante chunking comprova rollback de processo, relações, metadata, chunks e ingestion_run.
TESTES: 94 testes focados passaram em 1.75 s; regressão completa do chatbot 117 testes em 3.09 s; package do coletor 3 testes em 0.46 s; compileall passou.
ARQUIVOS_FUNCIONAIS: chatbot_processual_ai/collector_adapter.py; chatbot_processual_ai/agents/agent2_context_collection.py.
ARQUIVOS_TESTE: chatbot_processual_ai/tests/test_collector_adapter.py; chatbot_processual_ai/tests/test_p3_collector_integration.py.
DOCUMENTACAO: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
EFEITOS_EXTERNOS: nenhum acesso TRT18, rede, browser, Playwright, CAPTCHA, deploy, push ou commit; somente SQLite efêmero isolado e removido pelos testes.
G3: IN_PROGRESS, aguardando validação do usuário.
C03: TODO; COMMIT_REAL: —.
COMMIT_CRIADO: não.
```

---

## FASE P3 — tentativa de validação e auditoria do C03

```text
DATA_HORA: 2026-09-11 08:32:02 -03:00
IDS_AVALIADOS: INT-COL-P3-001, INT-COL-P3-002, INT-COL-P3-003, INT-COL-P3-004
RESULTADO_TECNICO: aprovado; 94 testes focados, 117 testes da regressão do chatbot e 3 testes offline do coletor passaram. Import leve não carregou trt18_collector, Playwright, cv2 ou ddddocr. O diff restrito aos seis arquivos da P3 passou em git diff --check.
CHECKPOINT_ENCONTRADO: 485ee7dca07b2e0eb8fda255080991c60e264561 — feat(chat): acquire and persist missing processes.
IMPEDIMENTO_DE_VALIDACAO: o commit contém 25 arquivos e mistura a P3 com avaliacao/trt18_amostras, frontend/proxy.runtime.json, runtime-logs, PIDs e distribuição local do Node, incluindo node.exe. O git diff HEAD^ HEAD --check falha em runtime-logs/node/node-v24.19.0-win-x64/LICENSE por whitespace. Portanto os critérios obrigatórios de diff focado, ausência de mudanças fora do escopo e git diff --check não foram satisfeitos.
STATUS_DOS_IDS: P3-001 preserva seu registro histórico; P3-002/P3-003/P3-004 permanecem IMPLEMENTED e não foram promovidos a VALIDATED.
G3: IN_PROGRESS.
C03: BLOCKED para saneamento do checkpoint; hash real registrado sem aprovação do conteúdo misto.
P4: não iniciada.
```

---

## FASE P3 — fechamento autorizado na branch de trabalho

```text
DATA_HORA: 2026-09-11 -03:00
DECISAO_DO_USUARIO: a branch atual é uma branch própria de trabalho e versiona também artefatos auxiliares. A presença de checklist, controle de progresso, AGENTS.md, safety.rules, avaliacao e outros auxiliares no histórico desta branch não invalida o checkpoint funcional; esses materiais serão descartados ou removidos antes da integração na main.
ESCOPO_DA_VALIDACAO: o gate de P3 considera o diff funcional restrito aos seis arquivos da fase, que passou em git diff --check, junto aos testes focados e regressões offline. A falha de whitespace no runtime Node auxiliar foi aceita como externa ao produto/P3 e permanece registrada para saneamento antes da main.
EVIDENCIAS: 94 testes focados aprovados; 117 testes da regressão completa do chatbot aprovados; 3 testes offline do coletor aprovados; imports pesados continuaram lazy; round-trip SQLite, sanitização, chunks, rollback, Agent 2, progresso seguro e reutilização em mesma sessão/nova sessão/reinício lógico comprovados.
STATUS_FINAL: INT-COL-P3-001, INT-COL-P3-002, INT-COL-P3-003 e INT-COL-P3-004 VALIDATED.
G3: VALIDATED.
C03: VALIDATED no commit 485ee7dca07b2e0eb8fda255080991c60e264561.
CONDICAO_FUTURA: remover os artefatos auxiliares e revisar o diff global antes de integrar na main; isso não faz parte do fechamento funcional atual da P3.
P4: não iniciada.
```

---

## INT-COL-P2-003 — registro detalhado

```text
ID: INT-COL-P2-003
DATA_HORA: 2026-09-09 -03:00
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5 (Codex)
MOTIVO_DIVERGENCIA_MODELO: o ambiente identifica o agente como Codex baseado em GPT-5; GPT-5.6 Terra permaneceu como recomendação registrada.
MATRIZ_INICIAL: P2-002 já cobria os sete estados, local-first, tradução, mensagens e ciclo de sucesso em 41 testes; faltavam asserts independentes para árvore local exata/sem releitura, todos os efeitos bloqueados em inválido, lookup local incompatível, sanitização dos quatro estados não bem-sucedidos, candidatos SUCESSO inválidos, releitura incompatível/divergente e prova explícita de socket bloqueado.
TESTES_CRIADOS_AJUSTADOS: 17 testes parametrizados/independentes adicionados a chatbot_processual_ai/tests/test_collector_adapter.py; a suíte focada passou de 41 para 58 cenários.
CENARIOS_COBERTOS: INVALID_NUMBER sem dependências; LOCAL_HIT com árvore aprovada e sem coleta/persistência/releitura; miss com ordem validate->lookup->collect->persist->reload; SUCESSO->COLLECTED com árvore relida; NAO_ENCONTRADO->NOT_FOUND, PARCIAL->PARTIAL, BLOQUEADO->BLOCKED e FALHA->FAILED sem persistência; exceções de lookup/coleta/persistência/releitura; status ausente/desconhecido; candidatos não-dict, sem coleta/status/processo/número, divergentes ou estruturalmente incompatíveis; releitura nula, divergente ou incompatível; mensagens/retry/process/diagnostic_id sanitizados.
EFEITOS_EXTERNOS_BLOQUEADOS: todos os cenários do adapter receberam fakes injetados; probe dedicado substituiu socket.socket por falha determinística e ainda completou COLLECTED; não houve import de Playwright, cv2 ou ddddocr, rede, browser, CAPTCHA, coleta TRT18, SQLite real, cache real, subprocesso de browser, Ollama ou Qdrant.
COMANDOS_EXECUTADOS: chatbot_processual_ai/.venv/Scripts/python.exe -m pytest tests/test_collector_adapter.py -q -p no:cacheprovider; mesma suíte completa tests -q -p no:cacheprovider; pytest ../entrada-de-dados/tests/test_package_import.py -q -p no:cacheprovider; python -m trt18_collector.cli --help; probe import api e from trt18_collector import obter_processo; validação JSON estrutural do notebook; git diff --check.
RESULTADOS: 58 testes focados passaram; 101 testes do chatbot passaram; 3 testes do package passaram; CLI, import do backend/package e notebook estrutural passaram; nenhuma falha, skip ou warning de teste. git diff --check passou com apenas avisos CRLF preexistentes do Git.
CORRECOES_MINIMAS: nenhuma correção funcional no adapter/package foi necessária; a cobertura confirmou o contrato P2-002.
ARQUIVOS_MODIFICADOS_NESTE_ITEM: chatbot_processual_ai/tests/test_collector_adapter.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
RISCOS_LIMITACOES: validação ocorreu no venv existente, não em ambiente limpo; persistência/releitura produtivas, Agent 2, SQLite real e fluxo conversacional continuam reservados para P3. Nenhum baseline ou fixture real foi lido ou modificado.
REVISAO_DO_DIFF: diff do teste e dos artefatos operacionais revisado; sem logs temporários, segredos, payloads, dados pessoais ou alterações fora do item. Mudanças preexistentes foram preservadas.
GIT_DIFF_CHECK: pass
G2: tecnicamente apto ao fechamento, condicionado à revisão e autorização do usuário.
C02: READY; COMMIT_REAL: —; nenhum commit criado.
P3: não iniciada.
```

---

## INT-COL-P2-002 — registro detalhado

```text
ID: INT-COL-P2-002
DATA_HORA: 2026-09-09 08:30:18 -03:00
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Sol
MODELO_EXECUTADO: GPT-5 (Codex)
MOTIVO_DIVERGENCIA_MODELO: o ambiente identifica o agente como Codex baseado em GPT-5; GPT-5.6 Sol permaneceu como recomendação registrada.
DIAGNOSTICO_CONFIRMADO: collector_adapter.py continha somente um wrapper de find_process_by_number; Agent 2 e o orquestrador consumiam esse símbolo legado e nenhum fluxo explícito representava aquisição, estados do produtor, persistência/releitura ou falhas sem falso not_found.
CONTRATO_IMPLEMENTADO: CollectorAdapter.lookup_or_acquire_process(process_number) executa validação, lookup local, coleta apenas em miss válido, tradução do produtor e ciclo de persistência/releitura por composição. A função homônima de módulo oferece a mesma operação com dependências keyword-only explícitas; find_process_by_number permanece compatível.
TIPOS_E_SIMBOLOS_PUBLICOS: AdapterStatus com LOCAL_HIT, COLLECTED, NOT_FOUND, PARTIAL, BLOCKED, FAILED e INVALID_NUMBER; CollectorResult dataclass frozen com status, process, public_message, retryable e diagnostic_id opcional; CollectorAdapter; lookup_or_acquire_process; find_process_by_number; validate_process_number; collect_process.
DEPENDENCIAS_INJETAVEIS: validator, lookup, collector, persist e reload são callables explícitos. validate_process_number delega sob demanda ao validador CNJ canônico; collect_process importa sob demanda exclusivamente from trt18_collector import obter_processo. Não há estado global mutável nem composição com banco real.
MATRIZ_TRADUCAO: SUCESSO estruturalmente válido + número correspondente + persistência sem exceção + releitura válida -> COLLECTED; NAO_ENCONTRADO inequívoco -> NOT_FOUND; PARCIAL -> PARTIAL; BLOQUEADO -> BLOCKED; FALHA -> FAILED; status ausente/desconhecido, estrutura inválida/contraditória e exceção -> FAILED.
INVARIANTES: process existe somente em LOCAL_HIT/COLLECTED; hit local impede coleta e escrita; inválido impede lookup/coleta; estados não bem-sucedidos não persistem nem expõem árvore; COLLECTED devolve somente a árvore relida; falha/nulo/divergência na releitura vira FAILED; mensagens são constantes sanitizadas; não há retry automático.
ARQUIVOS_MODIFICADOS: chatbot_processual_ai/collector_adapter.py; chatbot_processual_ai/tests/test_collector_adapter.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
TESTES_EXECUTADOS: chatbot_processual_ai/.venv/Scripts/python.exe -m pytest tests/test_collector_adapter.py -q -p no:cacheprovider; mesma suíte em tests; pytest ../entrada-de-dados/tests/test_package_import.py; py_compile do adapter/teste; probe de import simples sem trt18_collector/playwright/cv2/ddddocr; git diff --check.
RESULTADOS: 41 testes focados passaram; 84 testes do chatbot passaram; 3 testes de import/package passaram; compilação e probe leve passaram. Nenhuma falha ou warning de teste permaneceu.
LIMITACOES: persistência e releitura produtivas não foram compostas; transação/SQLite real e ligação conversacional pertencem a P3. A matriz exaustiva independente de P2-003 não foi antecipada.
RISCOS_RESIDUAIS: a função pública do produtor preserva seus efeitos quando futuramente composta e chamada; nesta validação foi substituída por fake. Política produtiva de diagnóstico_id e atomicidade do ciclo de banco permanece para fases posteriores.
REVISAO_DO_DIFF: revisados contrato, typing, imports tardios, mensagens, logging sanitizado, árvore relida, consumidores legados e diff completo do item; alterações preexistentes de P2-001 foram preservadas e nenhuma alteração fora do escopo do item foi introduzida.
GIT_DIFF_CHECK: pass
EFEITOS_EXTERNOS: ausentes; nenhuma rede, coleta real, browser, CAPTCHA, banco real, frontend, Ollama, Qdrant, instalação, commit ou operação remota foi executada.
AGENT2_E_PERSISTENCIA_REAL: Agent 2, orquestradores e process_repository.py não foram alterados; persist/reload foram exercitados somente com fakes.
DEPENDENCIAS_AFETADAS: G2 permanece IN_PROGRESS; C02 permanece TODO e sem hash real; INT-COL-P2-003 permanece TODO e não iniciado.
COMMIT_DA_FASE: C02
COMMIT_REAL: —
OBSERVACOES: auto-validação autorizada pelos critérios explícitos do prompt; nenhum commit criado.
```

---

## INT-COL-P2-001 — registro detalhado

```text
ID: INT-COL-P2-001
DATA_HORA: 2026-09-09 07:57:02 -03:00
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5.6
DIAGNOSTICO_CONFIRMADO: o coletor era composto por scripts irmãos em diretório com hífen; imports e notebook dependiam do CWD e o CAPTCHA alterava sys.path durante a coleta.
RECONCILIACAO: Git comprovou C00 `7275f75936988ffb45722f60d68b00ca6ab22e5d` e C01 `f2ba1723e3bd74cbeb8bc136f465ca773cbc29fd`; G0/G1 e C00/C01 foram atualizados somente com esses fatos.
ARQUIVOS_CRIADOS_OU_MOVIDOS: entrada-de-dados/pyproject.toml; entrada-de-dados/trt18_collector/{__init__,service,models,normalizer,collector_trt18,cli}.py; subpackages captcha/DCF_CODE; testes/test_package_import.py.
IMPORTS_E_WRAPPERS: package usa imports relativos; foram removidas as injeções sys.path do fluxo canônico; app.py e os quatro módulos históricos são wrappers finos de compatibilidade.
API_PUBLICA: from trt18_collector import obter_processo; from trt18_collector.service import obter_processo.
PATHS_E_EFEITOS: dados continuam resolvidos a partir da raiz entrada-de-dados por Path(__file__); notebook resolve a raiz pelo package, sem Path.cwd/sys.path. Import simples não carregou playwright, cv2 ou ddddocr, nem executou rede, browser, CAPTCHA, cache, banco, subprocesso ou thread.
INSTALACAO_AUTORIZADA: chatbot_processual_ai/.venv/Scripts/python.exe -m pip install --no-deps -e entrada-de-dados; distribuição trt18-collector 1.1.0 confirmada.
TESTES_EXECUTADOS: pytest entrada-de-dados/tests/test_package_import.py -q -p no:cacheprovider (3 passed); import API e import api no bootstrap oficial; app.py --help; python -m trt18_collector.cli --help; validação JSON do notebook; git diff --check.
RESULTADOS: todos passaram. A primeira tentativa de pytest com tmp_path foi bloqueada por PermissionError no diretório temporário do ambiente; o teste foi ajustado para CWD C:\ existente, sem criar dados, e passou.
DOCUMENTACAO_ATUALIZADA: checklist e controle operacional somente.
REVISAO_DO_DIFF: código canônico existe apenas no package; wrappers não duplicam lógica; nenhuma alteração funcional foi feita no chatbot; C02 permanece TODO, sem hash.
SEGREDOS_DADOS_SENSIVEIS: não expostos; somente fixture sanitizada foi lida.
RISCOS_RESIDUAIS: a instalação foi validada no venv existente, não em ambiente limpo; diretórios temporários de pytest previamente bloqueados pelo ambiente não foram removidos nem usados pela implementação.
OBSERVACOES: G2 permanece IN_PROGRESS porque P2-002/P2-003 não foram iniciadas. Nenhuma coleta externa e nenhum commit foram realizados; P2-002 não foi iniciada.
```

---

## INT-COL-P1-004 — registro detalhado

**ID:** `INT-COL-P1-004`
**Data/hora:** `2026-09-08 14:55:46 -03:00`
**Status anterior:** `TODO`
**Status final:** `VALIDATED`
**Modelo recomendado:** GPT-5.6 Sol
**Modelo executado:** GPT-5.6 Sol
**Divergência de modelo:** não aplicável.

### Problema confirmado e evidências

- **Fato comprovado:** `entrada-de-dados/` contém scripts no topo, `captcha/`, `data/`, `exemplos/` e `pesquisa/pipeline.ipynb`, mas não contém `__init__.py`, `pyproject.toml`, `setup.py`, `setup.cfg`, manifesto ou entry point. O repositório também não possui metadata Python própria fora de ambientes/terceiros.
- **Fato comprovado:** o hífen não é um identificador Python válido em sintaxe `import`/`from`; por isso não existe um `from entrada-de-dados...` convencional. `importlib.import_module("entrada-de-dados")` chegou a materializar um namespace a partir da raiz, mas `entrada-de-dados.servico` falhou em `from normalizador import normalizar` (`servico.py:23`), comprovando que o nome é apenas um bloqueio entre vários e que carregamento dinâmico não corrige os imports internos.
- **Fato comprovado:** `servico.py:23`, `normalizador.py:24-34` e `app.py:27` usam imports absolutos de scripts irmãos; o coletor injeta `captcha/` e `captcha/DCF_CODE` em `sys.path` somente ao carregar dependências (`coletor_trt18.py:38-56`); `captcha/decifra_coleta.py:5-11` repete a injeção; os módulos DCF misturam `DCF_CODE.*` e imports absolutos irmãos. O notebook calcula `RAIZ` a partir de `Path.cwd()`, injeta-a em `sys.path` e importa scripts soltos (`pipeline.ipynb:62-79`).
- **Fato comprovado:** o bootstrap oficial do backend é executado em `chatbot_processual_ai/` com `python -m uvicorn api:app --reload` (`chatbot_processual_ai/README.md:15,78`; `docs/development.md:17-22`). Coletor/CLI oficiais pressupõem `cd entrada-de-dados` e `python app.py ...` (`README.md:45-55`; `docs/development.md:69-81`); o notebook presume `entrada-de-dados/` ou `entrada-de-dados/pesquisa/` (`docs/data-ingestion.md:237-254`). Assim, o backend não enxerga os scripts irmãos sem manipulação externa do path.
- **Fato comprovado:** cache e recursos principais já usam `Path(__file__)`: `servico.py:25-26`, `coletor_trt18.py:34-35,126-127,558-585`, `app.py:29-30` e os módulos DCF. O notebook é a exceção dependente de CWD. O SQLite consumidor usa default relativo `./data/processual.sqlite3` (`config.py:13`), resolvido pela camada atual do chatbot; consolidação configurável continua em P5.
- **Fato comprovado por probes offline:** na raiz e em diretório temporário, `import servico` terminou em `ModuleNotFoundError`; em `entrada-de-dados/`, importou e resolveu o cache por `__file__`, sem carregar `coletor_trt18`, Playwright, OpenCV ou `ddddocr`; o bootstrap `import api` funcionou no CWD oficial do backend. `python entrada-de-dados/app.py --help` na raiz e `python app.py --help` no diretório do coletor passaram. Nenhuma função de coleta foi chamada e nenhum browser, rede, banco ou cache foi aberto/escrito.

### Alternativas comparadas

| Alternativa | Mudanças necessárias | Impacto no coletor | Impacto no chatbot | CLI/notebook | Independência de CWD | Import leve | Testabilidade | Riscos |
|---|---|---|---|---|---:|---:|---:|---|
| Renomear `entrada-de-dados` para nome importável | mover diretório e corrigir todos os paths/docs/imports | Alto e transversal | import direto possível | quebra paths conhecidos até migração total | Parcial sem instalação | possível | boa após refatoração | diff amplo, histórico/path externo quebrado, ainda exige corrigir imports e distribuição |
| Criar package importável dentro da área atual | adicionar `trt18_collector/`, imports relativos e wrappers legados | Moderado, ownership preservado | importa API estável | wrappers mantêm comandos/células durante migração | Sim quando instalado | Sim com fachada mínima | alta por fake da função pública | coexistência temporária e risco de duas fontes se arquivos forem copiados |
| Fachada fina no coletor sobre scripts atuais | package só delega aos scripts soltos | Baixo inicialmente | API limpa | alta compatibilidade | Não sem hack/install que também exponha scripts | parcialmente | moderada | mantém imports frágeis e duplica superfícies; dívida imediata |
| Tornar coletor instalável/editável | metadata + package real + entry point opcional | Moderado | dependência normal do ambiente | CLI por wrapper/`python -m`; notebook importa package | Sim | Sim | alta; ferramentas Python reconhecem o package | exige declarar instalação local no setup consolidado em P5 |
| `importlib`/carregamento por path | loader, specs e manipulação de módulos | Baixo no arquivo original | adapter carrega por caminho | não melhora fluxos existentes | frágil | incerto | baixa | paths, `sys.modules`, imports irmãos, Windows/POSIX e tooling frágeis |
| Wrapper no chatbot | copiar/delegar lógica de import/coleta | coletor permanece isolado | acoplamento e ownership indevidos | não resolve notebook | Não sem path manual | variável | fake possível, integração frágil | duplicação, circularidade e segunda implementação do coletor |

**Decisão aprovada:** combinar as alternativas complementares “package dentro da área atual” e “distribuição instalável/editável”. É a menor solução que remove dependência de CWD/path manual sem renomear a área histórica. O nome de distribuição proposto é `trt18-collector` e o package importável é `trt18_collector`. O código canônico ficará no package; wrappers legados somente encaminharão chamadas e não duplicarão lógica. `importlib`, path absoluto, `PYTHONPATH` e `sys.path` improvisado são rejeitados.

### Estrutura física e contrato de importação congelados para P2

```text
entrada-de-dados/
├── pyproject.toml                         # metadata/build do coletor
├── app.py                                 # wrapper CLI compatível, sem lógica duplicada
├── trt18_collector/
│   ├── __init__.py                        # reexporta somente API leve
│   ├── service.py                         # fachada pública do produtor
│   ├── models.py
│   ├── normalizer.py
│   ├── collector_trt18.py
│   ├── cli.py
│   └── captcha/                           # package interno; DCF continua sob demanda
└── pesquisa/pipeline.ipynb                # passa a importar o package
```

- **API pública aprovada:** `from trt18_collector import obter_processo`; único símbolo obrigatório ao backend. `trt18_collector.service.obter_processo` é o módulo público explícito. Modelos/status podem ser importados de `trt18_collector.models` por testes/ferramentas do coletor, mas não fazem parte da dependência obrigatória do Agent 2. Playwright, CAPTCHA, browser, cache bruto e normalizador interno não são API do chatbot.
- **Imports a ajustar em P2:** scripts irmãos passam a relativos dentro do package (`.normalizer`, `.models`, `.collector_trt18`, `.captcha...`); removem-se as duas injeções `sys.path`; imports de Playwright, OpenCV, `ddddocr` e pipeline CAPTCHA permanecem dentro da chamada de coleta/OCR. Evitar reexports pesados em `__init__.py` e import circular entre `service` e `collector_trt18`.
- **Compatibilidade:** `entrada-de-dados/app.py` continua aceitando os argumentos atuais e delega a `trt18_collector.cli`; a forma preferida instalada poderá ser `python -m trt18_collector.cli`/entry point equivalente. O notebook mantém seu fluxo, mas importa `trt18_collector` sem `sys.path` e resolve entrada/saída por configuração/base do package, não por CWD. Backend oficial importa o package instalado no mesmo ambiente do FastAPI. Windows e POSIX usam os mesmos imports; descoberta opcional de executável de browser permanece detalhe interno e o fallback Playwright é preservado.
- **Testes:** o `collector_adapter` do chatbot recebe/injeta um callable compatível com `obter_processo`; unitários usam fake e não importam o coletor pesado. Testes do package podem importar normalizador/modelos diretamente. A instalação editável é conveniência de desenvolvimento, não requisito em runtime de produção; ambos usam metadata padrão, sem `PYTHONPATH`.
- **Paths:** recursos versionados são resolvidos por `importlib.resources` ou `Path(__file__)` do package; cache, bruto, saída, CAPTCHA temporário e debug recebem paths/configuração explícitos e redirecionáveis. Nenhum default deriva de `Path.cwd()`. Banco consumidor continua propriedade do chatbot e será consolidado em P5.
- **Arquivos prováveis de P2:** adicionar `entrada-de-dados/pyproject.toml` e árvore `trt18_collector/`; mover logicamente os módulos atuais para ela; transformar `app.py` em wrapper; ajustar o notebook; criar testes offline de import/efeitos/contrato. Não executar essas mudanças neste item.

### Matriz de ownership

| Responsabilidade | Dono | Consumidor | Pode ser duplicada? | Observação |
|---|---|---|---:|---|
| validação inicial CNJ | adapter/chatbot | conversa e coletor | Não | uma dependência canônica injetável; coletor pode validar defensivamente, sem regra divergente |
| lookup SQLite e decisão de coletar | chatbot/adapter | Agent 2 | Não | local-first; hit proíbe coleta |
| Playwright, CAPTCHA e APIs PJe | `trt18_collector` | service do produtor | Não | sempre sob demanda |
| cache bruto | `trt18_collector` | serviço/normalizador/notebook | Não | não cruza para o chatbot |
| normalização e contrato produtor | `trt18_collector` | adapter | Não | árvore produzida pode conter campos depois descartados |
| tradução para estados/persistibilidade | `collector_adapter` do chatbot | Agent 2 | Não | fronteira, não segunda coleta |
| sanitização, transação SQLite e reconstrução | chatbot/repositório | adapter e consumidores | Não | `COLLECTED` só após commit e releitura conforme P1-003 |
| sessão, mensagens públicas e RAG | chatbot | API/usuário | Não | coletor não contém regra conversacional |
| logs/diagnóstico da coleta | coletor | operação interna | Não | chatbot recebe só categoria/correlação sanitizada |
| logs/diagnóstico de ingestão/conversa | chatbot | operação interna | Não | sem payload/PII |
| testes com fake | chatbot na fronteira; coletor em seus módulos | suítes offline | Não se duplica lógica | fake implementa o contrato público mínimo |

### Política dos dados na fronteira

| Categoria | Pode cruzar? | Pode persistir? | Pode aparecer em log? | Destino e retenção |
|---|---:|---:|---:|---|
| número processual | Sim | Sim | somente normalizado/mascarado quando necessário | SQLite/chatbot conforme finalidade institucional |
| árvore normalizada | Sim, somente candidato `SUCESSO` | somente sanitizada | Não como payload | sanitiza → transação → árvore reconstruída |
| status da coleta | Sim | Sim como metadado sanitizado | Sim, enum | SQLite/diagnóstico mínimo |
| mensagem pública controlada | adapter→chatbot | sessão se aplicável | Sim | retenção da conversa |
| código/categoria técnica | Sim, canal interno | opcional como diagnóstico | Sim | correlação e retenção operacional mínima |
| exceção interna/stack trace | Não na API/árvore | Não no SQLite de processo | somente classe/categoria sanitizada | coletor ou observabilidade restrita |
| CPF/CNPJ/documento das partes | pode existir na árvore produzida, mas deve ser removido antes da persistência consumidora | Não | Não | não necessário ao chatbot |
| IDs internos de documentos | pode existir na árvore produzida, mas deve ser removido | Não | Não | não necessário ao chatbot |
| payload bruto/HTML | Não | somente cache privado do coletor | Não | retenção definida pelo coletor; nunca Git |
| screenshot/CAPTCHA | Não | somente temporário/debug do coletor | Não | retenção mínima; CAPTCHA temporário removido |
| tokens/cookies/headers | Não | Não | Não | memória operacional; nunca diagnóstico persistente |
| paths locais | Não | Não | Não | configuração interna, sem API pública |
| dados de debug | Não, salvo categoria opaca | somente área restrita do coletor | apenas contagens/códigos sanitizados | retenção curta/configurável |
| tentativa/timestamps/duração | Sim se mínimos | Sim como metadado não sensível | Sim | diagnóstico e auditoria com retenção definida |

**Invariantes aprovadas:** sanitização ocorre antes de `ingest_processes`; documento de parte e `id_documento` continuam descartados conforme P1-002. Payload bruto, HTML, imagens, tokens e dados pessoais desnecessários não entram em logs, API, fixtures ou Git. A árvore produzida pertence ao contrato do coletor; a árvore sanitizada é a única elegível à transação; a árvore reconstruída do SQLite é a única entregue ao chatbot em `COLLECTED`. Cache/debug e sua retenção pertencem ao coletor; dados reais e artefatos de runtime permanecem fora do Git.

### Política de paths e efeitos de import

- **Permitido no import simples:** criar objetos imutáveis leves, enums/tipos, constantes sem segredo e funções/classes; resolver referência de recurso sem ler/escrever; carregar apenas biblioteca padrão/Pydantic estritamente necessária.
- **Proibido no import simples:** rede, Playwright/browser, OCR/modelo CAPTCHA, `cv2`, criação/leitura/escrita de cache/debug, abertura/seed/migração do SQLite, threads/subprocessos, alteração de event-loop, `sys.path`, CWD ou estado global de terceiros.
- **Invariantes:** nenhum path absoluto de desenvolvedor; nenhum `PYTHONPATH`; nenhum default baseado em CWD; recursos por package/`__file__`, dados mutáveis por configuração explícita; cache, banco e debug redirecionáveis a temporários em testes. A configuração concreta, variáveis finais, requirements e instalação limpa pertencem a P5.

### Consequências, riscos e encaminhamentos

- **Consequências positivas:** import estável e reconhecido por tooling em Windows/POSIX; ownership físico coincide com o conceitual; backend depende de uma API mínima; CLI/notebook migram sem duplicação; testes ficam offline e independentes de CWD.
- **Custos aceitos:** reorganização localizada em P2, wrappers transitórios e metadata de distribuição; documentação de comandos/paths deverá ser atualizada quando a implementação existir.
- **Riscos:** mover módulos pode quebrar imports legados ocultos; imports DCF mistos exigem teste; wrapper e package não podem manter duas implementações; entry point/instalação precisam ser reconciliados com o ambiente único; browser paths Windows atuais são internos e não portáveis, embora exista fallback Playwright. Mitigar com testes a partir da raiz, backend, diretório temporário e CLI/notebook.
- **Tarefas concretas de P2:** criar package/metadata; mover a implementação canônica; converter imports a relativos; remover `sys.path`; preservar imports pesados tardios; criar wrapper CLI e adaptar notebook; conectar o adapter apenas à API pública; adicionar probes/testes de CWD, efeitos de import e fake; comprovar bootstrap oficial sem coleta.
- **Pendências de P5:** consolidar requirements e instalação local/empacotada, nomes/defaults das variáveis de cache/banco/debug/browser, instalação limpa e entry point final; decidir retenção concreta; reconciliar duplicação física de CAPTCHA. Nenhuma foi antecipada.

### Evidências e revisão

- **Arquivos/símbolos/bootstraps inspecionados:** `servico.py::obter_processo`; `normalizador.py`; `modelos.py`; `coletor_trt18.py::_carregar_dependencias_de_coleta/_finalizar/_salvar_diagnostico`; `app.py`; `captcha/decifra_coleta.py`; módulos DCF; notebook; `collector_adapter.py`; `config.py`; `process_repository.py`; READMEs e `docs/development.md`, `docs/data-ingestion.md`; registros integrais P1-001..003; bootstrap FastAPI e comandos CLI/notebook.
- **Comandos diagnósticos:** inventário/metadata e `rg` de imports/paths/comandos; imports por Python do venv na raiz, em `entrada-de-dados/` e no diretório temporário; `importlib` do nome com hífen; delta de `sys.modules`; `app.py --help` nos dois CWDs; `import api` no CWD oficial. Todos foram read-only e offline.
- **Ausência de alteração funcional:** confirmada. Somente checklist e este controle foram modificados; não houve alteração de código, package, import, teste, banco, cache, configuração, dependência ou documentação permanente.
- **Classificação:** fatos estão identificados como comprovados; estratégia, ownership, dados e invariantes são decisões aprovadas; portabilidade/browser oculto é risco; detalhes concretos de ambiente/retenção são pendências P5.
- **Gates:** P1-001..004 estão `VALIDATED`; P1 está pronta para revisão manual e fechamento pelo usuário. G1 permanece `IN_PROGRESS` e C01 permanece `TODO`, sem hash/commit real, até essa autorização. P2 não foi iniciada.

---

## INT-COL-P1-003 — registro detalhado

**ID:** `INT-COL-P1-003`
**Data/hora:** `2026-09-08 12:37:31 -03:00`
**Status anterior:** `TODO`
**Status final:** `VALIDATED`
**Modelo recomendado:** GPT-5.6 Sol
**Modelo executado:** GPT-5.6 Sol
**Divergência de modelo:** não aplicável.

### Problema, fatos consolidados e forças

- **Fato comprovado (P1-001):** `obter_processo(numero, *, usar_cache=True, coletar=True, headless=False, status_cnj_planilha=None) -> dict` aceita número textual, remove não dígitos e exige 20 dígitos no serviço; a validação CNJ completa só ocorre no caminho de coleta. O retorno normalizado contém `processo`, listas de partes/movimentações/documentos/pendências e `coleta.status_coleta` em `SUCESSO`, `PARCIAL`, `FALHA`, `NAO_ENCONTRADO` ou `BLOQUEADO`.
- **Fato comprovado (P1-001):** podem escapar `ValueError`, `FileNotFoundError`, erro de JSON/leitura/escrita, importação/dependência, Playwright/navegador fora do bloco capturado, normalização/Pydantic e serialização. Coleta real pode usar rede, navegador, CAPTCHA, retries e gravar bruto/diagnóstico; cache-only apenas lê. Uma árvore estrutural pode existir sem representar sucesso; cache aproveitável ignora `status_coleta`, e status ausente/desconhecido vira `SUCESSO` no normalizador atual.
- **Fato comprovado (P1-002):** `find_process_by_number(str) -> dict | None` faz lookup SQLite, retorna `None` tanto para número inválido quanto para miss e propaga exceções. `ingest_processes(list[dict], source_name=..., connection=...)` sanitiza, faz upsert, recria filhos/chunks, confirma a transação e, em exceção durante a ingestão, executa rollback e relança.
- **Fato comprovado (P1-002):** Agent 2 trata `dict` como `success`, `None` como `not_found` e não captura exceção; o orquestrador converte exceção em falha segura de estágio. No round-trip, `documento` de parte e `id_documento` são removidos, `data_distribuicao` e horário de `data_autuacao` não retornam, e o consumidor usa a árvore relida e os chunks do SQLite.
- **Forças/restrições aprovadas:** lookup local precede coleta; hit local proíbe coleta; apenas estados autorizados podem alterar SQLite; falha, bloqueio, parcial e inexistência não podem colapsar em `None`; detalhes de Playwright/CAPTCHA/exceções não atravessam a fronteira pública; coleta/normalização permanecem fora do chatbot e regras conversacionais fora do coletor; testes unitários devem ser totalmente offline.

### Alternativas avaliadas

| Alternativa | Simplicidade | Clareza semântica e falso `not_found` | Falha/bloqueio/parcial | Impacto no Agent 2 | Testabilidade e acoplamento | Mudança estimada e compatibilidade |
|---|---|---|---|---|---|---|
| Manter `dict | None` | Alta no curto prazo | Baixa; preserva a ambiguidade factual entre inválido, miss e indisponibilidade | Não representa sem convenções frágeis dentro do `dict` ou exceções | Mínimo, mas mantém comportamento incorreto | Fakes simples, porém sem asserção explícita de estados; Agent 2 continua acoplado à nulabilidade | Pouquíssima mudança; compatível com lookup atual, incompatível com os estados do produtor e com o critério de não gerar falso `not_found` |
| Resultado explícito discriminado por estado | Moderada e ainda localizada | Alta; cada desfecho tem nome e invariantes, e `NOT_FOUND` fica reservado | Representa todos sem expor implementação | Agent 2 passa a mapear status e só ativa árvore em sucesso | Fakes determinísticos por dependência; acoplamento ao contrato estável, não ao Playwright/coletor | Pequena mudança concentrada em adapter/chamador e testes; envolve os contratos existentes sem alterá-los conceitualmente |

**Decisão aprovada neste item:** adotar resultado explícito discriminado. O custo de um tipo/estrutura e de um mapeamento no Agent 2 é menor que o risco de transformar falha técnica, bloqueio ou parcial em ausência. Não foi aprovada uma abstração genérica, barramento de eventos ou hierarquia de exceções, pois não há consumidor que justifique essa complexidade.

### Contrato público conceitual

```python
lookup_or_acquire_process(process_number: str) -> CollectorResult

CollectorResult(
    status: AdapterStatus,
    process: dict | None,
    public_message: str,
    retryable: bool,
    diagnostic_id: str | None = None,
)
```

- **Decisão aprovada:** a única entrada pública obrigatória é `process_number`. Não há opção pública de Playwright, CAPTCHA, cache bruto, browser ou path. Dependências e configuração operacional são fornecidas ao adapter por composição/injeção, não pelo Agent 2.
- **Decisão aprovada:** a operação valida/normaliza a entrada, consulta o repositório local, retorna `LOCAL_HIT` imediatamente em hit e somente tenta coleta em miss válido. A validação canônica pode ser delegada a dependência própria; sua localização física fica para P1-004.
- **Decisão aprovada:** `status`, `process`, `public_message` e `retryable` são obrigatórios; `diagnostic_id` opaco é opcional. Exceção, stack trace, path, payload bruto, documento pessoal, token e detalhe de CAPTCHA nunca integram o resultado público.
- **Invariantes aprovadas:** `process` é obrigatório apenas em `LOCAL_HIT` e `COLLECTED`, e ausente nos demais estados; seu número normalizado deve coincidir com a solicitação. `COLLECTED` só existe após coleta `SUCESSO`, ingestão confirmada e releitura SQLite não nula. `None` em `process` nunca define o estado. Estado ausente/desconhecido ou estrutura contraditória vira `FAILED`, não sucesso ou `NOT_FOUND`.
- **Decisão aprovada:** em aquisição bem-sucedida, o consumidor recebe a árvore **relida do SQLite**, não o objeto recém-coletado. Isso prova que persistência, sanitização, perdas conhecidas e formato realmente consumido são os mesmos antes de ativar sessão, consulta estruturada ou RAG.
- **Detalhes internos:** seleção/importação do produtor, parâmetros `usar_cache/coletar/headless/status_cnj_planilha`, retries, browser, CAPTCHA, normalização, paths, bruto, transação e logs técnicos ficam atrás do adapter.

### Matriz congelada de estados

| Estado do adapter | Condição/origem e relação com o coletor | Processo disponível? | Pode ingerir? | Retorno ao Agent 2 | Mensagem pública segura | Diagnóstico interno permitido | Recoleta futura? |
|---|---|---:|---:|---|---|---|---:|
| `LOCAL_HIT` | número válido e lookup SQLite retorna árvore; coletor não é chamado | Sim, árvore local | Não | ativa/usa a árvore | “Processo localizado.” | código de etapa, origem local e `diagnostic_id`; sem payload | Não nesta chamada |
| `COLLECTED` | miss local + produtor retorna `SUCESSO` reconhecido, árvore válida e correspondente + ingestão e releitura passam | Sim, somente árvore relida | Sim, obrigatório | ativa/usa a árvore relida | “Processo localizado e atualizado com sucesso.” | etapas, duração, status do produtor e contagens não sensíveis | Não enquanto houver hit local válido |
| `NOT_FOUND` | exclusivamente `NAO_ENCONTRADO` inequívoco para número válido, sem árvore substantiva contraditória | Não | Nunca | não ativa; informa ausência remota comprovada | “Processo não encontrado na fonte consultada.” | status do produtor, etapa e correlação; sem resposta/payload bruto | Sim, por ação/política futura, pois a fonte pode mudar |
| `PARTIAL` | produtor retorna `PARCIAL`, ainda que haja árvore normalizada | Não para o consumidor; parcial fica interno à tentativa | Nunca no schema atual | não ativa e não envia árvore parcial | “A consulta retornou dados incompletos. Tente novamente mais tarde.” | status, etapa, contagens e warnings sanitizados | Sim |
| `BLOCKED` | produtor retorna `BLOQUEADO` (inclui bloqueio externo observado); não equivale a inexistência | Não | Nunca | não ativa | “A consulta externa está temporariamente indisponível. Tente novamente mais tarde.” | categoria de bloqueio, etapa, tentativa e correlação; sem detalhe de CAPTCHA | Sim |
| `FAILED` | produtor retorna `FALHA`; exceção técnica; falha de normalização/ingestão/releitura; status desconhecido; retorno inválido/contraditório | Não | Nunca como resultado; ingestão pode ter sido tentada apenas após candidato `SUCESSO` | não ativa; nunca converte em `not_found` | “Não foi possível consultar o processo agora. Tente novamente mais tarde.” | categoria/etapa, classe de exceção sanitizada, correlação e rollback/commit conhecido | Sim quando transitória; política de retry fica interna |
| `INVALID_NUMBER` | normalização/validação canônica rejeita entrada antes do lookup/coleta | Não | Nunca | solicita correção do número | “Número de processo inválido. Confira os dados informados.” | código de validação e etapa; não registrar entrada bruta desnecessária | Após correção pelo usuário |

### Política de persistibilidade

- **Decisão aprovada:** `LOCAL_HIT` preserva o banco sem escrita; `COLLECTED` é o único estado que exige ingestão e releitura; `NOT_FOUND`, `PARTIAL`, `BLOCKED`, `FAILED` e `INVALID_NUMBER` não persistem árvore nem substituem dado existente.
- **Decisão aprovada sobre `PARTIAL`:** a árvore parcial não possui integridade mínima comprovada além de validação estrutural; o schema guarda `status_coleta`, mas os consumidores atuais não o usam para impedir ativação, RAG ou consulta estruturada. Persistir contaminaria consultas futuras e poderia fazer um parcial virar hit aparente. Portanto não há persistência nem retorno parcial ao Agent 2 neste contrato; uma coleta posterior é preferível ao custo de propagar completude falsa.
- **Fato/limitação:** falha dentro de `ingest_processes` causa rollback. Como a implementação atual faz `commit()` antes de uma releitura pública, falha de releitura posterior deve resultar em `FAILED`, mas não permite prometer rollback; não se fará compensação destrutiva. O registro já confirmado pode permanecer e ser recuperado por lookup futuro. Tornar ingestão+releitura atomicamente controláveis é questão de implementação de P2, sem mudança de schema decidida aqui.
- **Decisão aprovada:** qualquer dado preexistente permanece intacto em falha; o adapter não apaga um hit anterior nem persiste tombstone de ausência/bloqueio/falha.

### Política de falhas e mensagens

| Caso | Estado público | Mensagem ao chatbot | Diagnóstico interno permitido | Banco | Retry |
|---|---|---|---|---|---|
| validação do número | `INVALID_NUMBER` | conferir o número informado | código de validação/etapa | inalterado | após correção |
| inexistência remota inequívoca | `NOT_FOUND` | não encontrado na fonte consultada | status produtor e correlação | inalterado | permitido por política futura |
| bloqueio externo/CAPTCHA | `BLOCKED` | consulta externa temporariamente indisponível | categoria, etapa e tentativas, sem desafio/imagem/HTML | inalterado | sim, controlado |
| falha técnica do coletor | `FAILED` | não foi possível consultar agora | classe/código sanitizado e etapa | inalterado | conforme transitoriedade |
| falha de normalização | `FAILED` | não foi possível consultar agora | categoria de schema/campo, sem payload/valor sensível | inalterado | após correção técnica/nova coleta |
| falha de ingestão | `FAILED` | não foi possível disponibilizar agora | etapa, classe sanitizada e confirmação de rollback | rollback da tentativa | sim |
| falha de releitura | `FAILED` | não foi possível disponibilizar agora | etapa, classe sanitizada e estado conhecido do commit | commit pode permanecer; sem compensação destrutiva | sim, primeiro lookup local |
| retorno estrutural inesperado/contraditório | `FAILED` | não foi possível consultar agora | motivo estrutural sanitizado/status recebido | inalterado, salvo commit anterior já confirmado | após correção/nova tentativa |

**Decisão aprovada:** mensagens públicas são estáveis e não incluem stack trace, path local, payload bruto, documento pessoal, token, OCR, Playwright, navegador, CAPTCHA ou detalhes do portal. Logs internos podem guardar somente código/categoria, etapa, classe de exceção sanitizada, contagens, duração e identificador de correlação; conteúdo sensível permanece proibido.

### Superfície de testabilidade

- **Decisão aprovada:** devem ser substituíveis por fake/injeção: validador/normalizador do número, lookup local, função pública de coleta, ingestão e releitura. Conexão/repositório pode ser injetado quando necessário para verificar transação, sem banco real.
- **Decisão aprovada:** testes de contrato usarão fakes que retornem cada um dos cinco `status_coleta`, hit/miss/exceção de lookup, falha de ingestão, releitura nula/exceção e estrutura inesperada. Devem provar ordem local-first, zero coleta em hit, matriz de persistência, árvore relida em `COLLECTED` e sanitização das mensagens.
- **Consequência positiva:** nenhuma rede, browser, Playwright, CAPTCHA, SQLite real, path absoluto, mutação global ou monkeypatch difícil de restaurar é necessário. Agent 2 depende apenas de `CollectorResult`.
- **Custo aceito:** há novo mapeamento de estados no chamador e mais casos de teste; o status conversacional atual precisará ser reconciliado na implementação, sem transferir regras de conversa ao coletor.

### Riscos e pendências posteriores

- **Risco:** o normalizador atual converte status ausente/desconhecido em `SUCESSO`; P2 deve caracterizar/fechar essa lacuna na borda sem tratar árvore vazia ou contraditória como `COLLECTED`.
- **Risco:** não existe hoje garantia transacional pública cobrindo ingestão e releitura; o contrato não inventa rollback após commit.
- **Inferência:** a checagem mínima segura de candidato `SUCESSO` inclui status reconhecido, árvore estrutural válida e número correspondente, mas não autoriza inferir completude de campos opcionais ausentes.
- **Pendência de P1-004, não decidida aqui:** estratégia física de package/import para `entrada-de-dados`, renomeação/wrapper/package auxiliar, localização definitiva das interfaces, ownership físico dos arquivos, paths/`PYTHONPATH`, configuração ampla e política documental permanente.
- **Pendência de P2/fases posteriores:** implementar tipo/enum/operação, integrar Agent 2, fechar transação/releitura, testes offline, mensagens/API e retries. Nenhum desses trabalhos foi iniciado.

### Evidências e revisão

- **Arquivos/símbolos consultados:** `entrada-de-dados/servico.py::obter_processo`; `normalizador.py::normalizar`; `modelos.py::StatusColeta/Processo`; `chatbot_processual_ai/collector_adapter.py::find_process_by_number`; `services/process_repository.py::find_process_by_number/ingest_processes/_load_process_tree/_sanitized_process_tree`; `agents/agent2_context_collection.py::_handle_process_lookup/_collection_status_message`; registros integrais de P1-001 e P1-002.
- **Arquivos modificados:** `docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md` e `CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md`.
- **Ausência de alteração funcional:** confirmada; nenhum código, teste, schema, banco, fixture, baseline, dependência ou documentação permanente foi modificado.
- **Validações executadas:** revisão integral do diff dos dois artefatos; conferência dos sete estados, invariantes e persistibilidade; `git diff --name-only`; `git status --short --branch`; `git diff --check -- docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md` (`pass`). Testes de código não foram executados porque não houve alteração funcional e P1-003 apenas congela o contrato.
- **Gates/commit:** G1 permanece `IN_PROGRESS`; P1-004 permanece `TODO`; C01 permanece `TODO` e sem hash real; nenhum commit foi criado.

---

## INT-COL-P1-002 — registro detalhado

```text
ID: INT-COL-P1-002
DATA_HORA: 2026-09-08 12:11:19 -03:00
STATUS_ANTERIOR: TODO
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5.6 Terra
MOTIVO_DIVERGENCIA_MODELO: não aplicável.
DIAGNOSTICO_CONFIRMADO:
  O adapter atual (collector_adapter.py:4-5) só delega ao lookup SQLite; não há aquisição remota. find_process_by_number(process_number: str) -> dict | None (services/process_repository.py:23-33) chama ensure_database_seeded(), normaliza removendo não-dígitos e exige 20 dígitos; inválido retorna None, hit retorna árvore dict e miss retorna None. Não captura exceções SQLite/leitura/seed. A conexão é aberta por _connect() (145-152), com foreign_keys=ON, e fechada em finally. ensure_database_seeded() cria schema e, somente se processes estiver vazia e data/sample_processes.json existir, faz seed automático (36-45).
CONTRATO_DE_INGESTAO:
  ingest_processes(processes: list[dict], *, source_name: str, connection: sqlite3.Connection | None=None) -> dict[str,int] (48-85) cria/usa conexão, schema e ingestion_run; ignora item não-dict ou sem número normalizável; substitui processo pelo número normalizado, recria filhos/chunks, conta processos/chunks, finaliza run e commit. Qualquer exceção faz rollback e é relançada; conexão própria fecha em finally. Reingestão do mesmo número é upsert e substitui filhos/chunks, não cria duplicata. Efeitos SQLite: schema/migration, ingestion_runs, processes, parties, movements, documents, pending_items, collection_metadata e rag_chunks; não há outro arquivo escrito exceto criação do diretório/banco no caminho LOCAL_DB_PATH.
MATRIZ_ROUND_TRIP:
  processo.numero/numero_normalizado: preservado; processes.numero/TEXT e PK; strings após leitura; Agent2/orquestrador/RAG usam número normalizado.
  processo.classe_judicial, assunto, orgao_julgador, unidade, jurisdicao, grau, situacao: preservados como TEXT; None permanece NULL; leitura devolve str|None; estruturado usa classe/assunto/orgao/situacao e chunking usa os campos rotulados suportados.
  processo.data_autuacao: transformado para date-only por _date_only; TEXT; leitura str|None; consumidor estruturado/chunk data. Horário é perdido.
  processo.data_distribuicao: não suportado/incompatibilidade real; não há coluna nem retorno reconstruído. Permanece apenas no processes.raw_json sanitizado, que não é usado para a leitura; nenhum consumidor atual localizado.
  processo.valor_causa: preservado como REAL quando bindável; leitura float|None; resolver/chunking/Agent3 usam como campo estruturado.
  partes_interessadas[].polo,nome,tipo,representantes: preservados, com representantes serializados JSON e ordem por party_index; consumidores Agent3/estruturado usam partes e nomes. documento: descartado intencionalmente por _sanitized_process_tree (684-698), ausente da tabela/raw_json/retorno.
  movimentacoes[].ordem,data,descricao,complemento,referencia: preservados como INTEGER/TEXT/raw_json sanitizado; None/'' tornam NULL em campos textuais; leitura ordena por movement_index de entrada, não por ordem; chunking/RAG/Agent3 usam descrição, complemento, referência e data.
  documentos[].titulo,data,tipo,conteudo|texto|teor: título/data/tipo e primeiro conteúdo não vazio preservados; documents.conteudo e raw_json sanitizado; leitura devolve conteudo somente se truthy. id_documento é descartado intencionalmente (684-704). Conteúdo permite chunk full_text e recuperação RAG.
  pendencias: preservado como JSON por índice, inclusive lista vazia; leitura mantém list; Agent3/rota estruturada usam lista quando presente.
  coleta e status_coleta: preservados como metadata_json, com tipos/strings do produtor sem validação adicional; leitura dict ou {} se ausência; não determina lookup local. collection_status do chatbot é outra enumeração local.
  payload JSON bruto: incompatibilidade real; processes.raw_json, movements.raw_json e documents.raw_json persistem apenas árvores/objetos já sanitizados, não o bruto do coletor; raw_json não é usado para reconstrução.
SANITIZACAO_VERSUS_INCOMPATIBILIDADE:
  Sanitização deliberada comprovada: documento de parte e id_documento são removidos antes de processes.raw_json e antes dos raws de documentos; Agent3 repete essa remoção antes de modelo (agent3_process_analysis.py:1427-1440) e rejeita resposta que contenha documento de parte (1549-1574). Não são bugs comprovados. Incompatibilidades: data_distribuicao e horário de data_autuacao não sobrevivem; não há persistência de payload bruto. Conteúdo documental, metadata de coleta, listas vazias e ordem de entrada foram comprovados na caracterização.
CONSUMIDORES:
  Agent2 (agent2_context_collection.py:80-211) exige árvore dict com processo.numero_normalizado para ativação; lookup inválido=>missing_number, processo já ativo referenciado=>not_needed, hit=>success e grava active_process/last_intent, None=>not_found sem alterar active_process. Exceção do repositório não é capturada.
  Resolver/roteador (process_query_resolver.py:66-246; process_query_router.py:24-127) consultam valor_causa, assunto, classe_judicial, orgao_julgador, data_autuacao e situacao; só requerem bool(active_process), e ausência leva a missing_process ou valor/campo indisponível no Agent3.
  Chunking (chunking.py:59-136) gera chunks de FIELD_LABELS, movimentações e documentos; ignora campos/listas inválidos ou vazios. RAG (rag_retriever.py:39-220, 374-414) lê rag_chunks por número, exige texto não vazio e propaga source_type/source_id/title/date/content_kind; sem chunks retorna contexto empty.
  Agent3 usa árvore, partes, movimentações, documentos, pendências e coleta (agent3_process_analysis.py:76-104, 264-286, 1320-1344); distingue somente collection_status missing_number/not_found para limitar análise. Orquestrador (processual_chat_orchestrator.py:18-190) captura qualquer exceção por estágio e devolve resposta segura com failed_stage; API (api.py:60-70) devolve session_id e resultado dataclass, incluindo processo_ativo, collection_status, failed_stage, rag_status e fontes.
NONE_EXCECOES_E_STATUS:
  collection_status local possível: not_needed, missing_number, already_active, success e not_found. Não há mapeamento dos status produtores SUCESSO/PARCIAL/FALHA/NAO_ENCONTRADO/BLOQUEADO; status_coleta permanece em coleta, mas não altera controle local. Logo o consumidor não distingue indisponibilidade local, falha técnica, dado parcial ou bloqueio: None é sempre not_found e exceção só vira failed_stage/resposta segura no orquestrador. Esta é limitação factual para P1-003, não decisão antecipada.
TESTES_EXECUTADOS:
  Caracterização offline via chatbot_processual_ai/.venv/Scripts/python.exe: SQLite tempfile com processo sintético sanitizado; 12 verificações passaram (ingestão, lookup interno pós-round-trip, duplicata/upsert, miss, rollback controlado, campos descartados, conteúdo/coleta/lista/ordem e chunks), 9 chunks gerados. Segundo script em memória com mocks apenas na fronteira Agent2/RAG confirmou cinco cenários: número inválido, processo ativo, hit, None/miss e exceção propagada. Sem rede, PJe, browser, CAPTCHA, cache real, seed real ou alteração do DB do projeto; tempfile foi removido ao final.
ARQUIVOS_INSPECIONADOS:
  collector_adapter.py; services/process_repository.py, chunking.py, process_query_resolver.py, process_query_router.py, rag_retriever.py, text_normalization.py; agents/agent2_context_collection.py e agent3_process_analysis.py; orchestrators/processual_chat_orchestrator.py; schemas/processual_contracts.py; config.py; api.py; testes test_rag_base.py, test_api_processual_chat.py e test_progress_events.py; contrato produtor detalhado de INT-COL-P1-001.
DOCUMENTACAO_ATUALIZADA: somente docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md e este controle operacional.
REVISAO_E_LIMITACOES:
  Nenhum código funcional, schema, banco persistente, fixture, dependência ou baseline foi alterado. Caracterização usa chamada interna _load_process_tree para isolar banco temporário; lookup público/seed foi comprovado por código, não executado contra o DB configurado para evitar efeito persistente. P1-003 não foi iniciado; sem contrato final de adapter ou decisão de estados.
DEPENDENCIAS_AFETADAS: G1 permanece IN_PROGRESS; INT-COL-P1-003/P1-004 permanecem TODO; C01 permanece TODO e sem hash real.
COMMIT_DA_FASE: C01
COMMIT_REAL: —
OBSERVACOES: nenhum commit, push, merge, rebase ou mudança de branch foi executado; nenhum dado pessoal, identificador interno, token ou payload real foi registrado.
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
| G0 | P0 — Baseline estrutural | branch, worktree, artefatos, centralização e testes baseline comprovados | `VALIDATED` |
| G1 | P1 — Contratos | produtor, consumidor, estados, importação, ownership e dados decididos | `VALIDATED` |
| G2 | P2 — Fronteira Python | import estável, adapter explícito e testes offline aprovados | `VALIDATED` |
| G3 | P3 — Fallback/persistência | local-first, coleta em miss, ingestão e reuso validados | `VALIDATED` |
| G4 | P4 — Falhas | matriz de estados, API controlada e rollback validados | `VALIDATED` |
| G5 | P5 — Runtime | dependências, config, CAPTCHA canônico e venv limpo aprovados | `VALIDATED` |
| G6 | P6 — Integração | regressões, matriz automatizada e exceção ambiental do aceite real registrada | `VALIDATED` |
| G7 | P7 — Documentação | README/docs coerentes e auditoria cruzada aprovada | `TODO` |
| G8 | P8 — Fechamento | DoD, diff, segurança e projeção para main aprovados | `TODO` |

---

## 5. Plano de commits por fase

Os commits abaixo são planejados; não constituem autorização para executar
`git commit`.

| Commit lógico | Fase | IDs cobertos | Mensagem sugerida | Estado | Commit real |
|---|---|---|---|---|---|
| C00 | P0 | `INT-COL-P0-001..004` | `chore(integration): establish chatbot collector baseline` | `VALIDATED` | `7275f75936988ffb45722f60d68b00ca6ab22e5d` |
| C01 | P1 | `INT-COL-P1-001..004` | `docs(integration): define chatbot collector contracts` | `VALIDATED` | `f2ba1723e3bd74cbeb8bc136f465ca773cbc29fd` |
| C02 | P2 | `INT-COL-P2-001..003` | `feat(collector): establish chatbot collection boundary` | `VALIDATED` | `c01a5b50bc63413ee7a9734b02abd77dabf1a5d5` |
| C03 | P3 | `INT-COL-P3-001..004` | `feat(chat): acquire and persist missing processes` | `VALIDATED` | `485ee7dca07b2e0eb8fda255080991c60e264561` |
| C04 | P4 | `INT-COL-P4-001..003` | `fix(chat): preserve collector failure semantics` | `VALIDATED` | `259b5ed7a10261f72162f47377ffba38f3dcfb3a` |
| C05 | P5 | `INT-COL-P5-001..004` | `chore(runtime): unify collector setup and configuration` | `VALIDATED` | `34e660a677e5d283d55e4f8323815c62ca0496d7` |
| C06 | P6 | `INT-COL-P6-001..004` | `test(integration): cover chatbot collector workflow` | `VALIDATED` | `f536ce2ce8f88847c3c49a4d59f5beefd9e1a9fe` |
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
| INT-COL-P1-001 | `VALIDATED` | GPT-5.6 Terra | GPT-5.6 Terra | assinatura, cache, árvore, estados, exceções e efeitos comprovados offline/código | C01 |
| INT-COL-P1-002 | `VALIDATED` | GPT-5.6 Terra | GPT-5.6 Terra | lookup, ingestão, sanitização, round-trip, consumidores e falhas comprovados offline/código | C01 |
| INT-COL-P1-003 | `VALIDATED` | GPT-5.6 Sol | GPT-5.6 Sol | resultado discriminado, matriz, persistência, erros e testabilidade aprovados | C01 |
| INT-COL-P1-004 | `VALIDATED` | GPT-5.6 Sol | GPT-5.6 Sol | package instalável, API leve, ownership, dados, paths e efeitos aprovados | C01 |

### P2 — Fronteira Python

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P2-001 | `VALIDATED` | GPT-5.6 Terra | GPT-5.6 | import estável sem efeito externo, metadata e compatibilidade offline comprovadas | C02 |
| INT-COL-P2-002 | `VALIDATED` | GPT-5.6 Sol | GPT-5 (Codex) | contrato local-first, sete estados, fakes e imports leves comprovados | C02 |
| INT-COL-P2-003 | `VALIDATED` | GPT-5.6 Terra | GPT-5 (Codex) | matriz offline do adapter aprovada; 58 testes focados e regressão offline verdes | C02 |

### P3 — Fallback e persistência

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P3-001 | `VALIDATED` | GPT-5.6 Sol | GPT-5 (Codex) | local-first e uma coleta somente em miss | C03 |
| INT-COL-P3-002 | `VALIDATED` | GPT-5.6 Terra | GPT-5 (Codex) | ingestão/rollback/round-trip aprovados | C03 |
| INT-COL-P3-003 | `VALIDATED` | GPT-5.6 Sol | GPT-5 (Codex) | Agent 2 e progresso integrados sem mudar HTTP | C03 |
| INT-COL-P3-004 | `VALIDATED` | GPT-5.6 Terra | GPT-5 (Codex) | sessão, nova sessão e restart sem recoleta | C03 |

### P4 — Estados e degradação

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P4-001 | `VALIDATED` | GPT-5.6 Sol | GPT-5 (Codex) | matriz de estados traduzida sem falso not_found | C04 |
| INT-COL-P4-002 | `VALIDATED` | GPT-5.6 Sol | GPT-5 (Codex) | API segura e banco consistente em falhas | C04 |
| INT-COL-P4-003 | `VALIDATED` | GPT-5.6 Terra | GPT-5 (Codex) | testes observáveis dos estados aprovados | C04 |

### P5 — Runtime, configuração e duplicações

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P5-001 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | manifests separados por ownership e imports reais | C05 |
| INT-COL-P5-002 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | env/paths determinísticos e sem paths locais obrigatórios | C05 |
| INT-COL-P5-003 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | CAPTCHA e browser com fonte canônica explícita | C05 |
| INT-COL-P5-004 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | exceção ambiental corporativa aceita pelo usuário; demais evidências P5 aprovadas | C05 |

### P6 — Testes e aceite

| ID | Status | Modelo recomendado | Modelo executado | Evidência esperada | Commit da fase |
|---|---|---|---|---|---|
| INT-COL-P6-001 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | 143 testes backend; zero regressões | C06 |
| INT-COL-P6-002 | `VALIDATED` | GPT-5.6 Terra | GPT-5 | 16 testes offline com bloqueio objetivo da fronteira externa | C06 |
| INT-COL-P6-003 | `VALIDATED` | GPT-5.6 Sol | GPT-5 | 8 cenários API/Agent 2/adapter/repository/SQLite, repetidos | C06 |
| INT-COL-P6-004 | `VALIDATED` | GPT-5.6 Sol | GPT-5 | exceção ambiental aceita explicitamente; fluxo TRT18 não executado | C06 |

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
| 08/09/2026 | INT-COL-P1-001 | Mapeamento factual do contrato produtor iniciado | `READY` → `IN_PROGRESS` | GPT-5.6 Terra | checkpoint C00 `7275f75` confirmado; inspeção limitada ao produtor e caracterização offline sem rede, navegador ou CAPTCHA | — |
| 08/09/2026 | INT-COL-P1-001 | Contrato produtor mapeado e auto-validado | `IN_PROGRESS` → `VALIDATED` | GPT-5.6 Terra | assinatura/cache/schema/status/exceções/efeitos registrados; caracterização em memória e fixture sanitizada; sem coleta real | — |
| 08/09/2026 | INT-COL-P1-002 | Mapeamento do contrato consumidor iniciado | `TODO` → `IN_PROGRESS` | GPT-5.6 Terra | inspeção exclusiva de repositório, Agent 2, roteamento, RAG, orquestrador e API; sem alteração funcional | — |
| 08/09/2026 | INT-COL-P1-002 | Contrato consumidor mapeado e auto-validado | `IN_PROGRESS` → `VALIDATED` | GPT-5.6 Terra | SQLite temporário confirmou round-trip, sanitização, duplicata, miss, rollback e chunks; fluxo Agent 2 caracterizado em memória | — |
| 08/09/2026 | INT-COL-P1-003 | Definição do contrato mínimo do adapter iniciada | `TODO` → `IN_PROGRESS` | GPT-5.6 Sol | análise baseada nos contratos validados de P1-001/P1-002; sem alteração funcional e sem antecipar P1-004 | — |
| 08/09/2026 | INT-COL-P1-003 | Contrato mínimo e matriz de estados auto-validados | `IN_PROGRESS` → `VALIDATED` | GPT-5.6 Sol | resultado discriminado, retorno por releitura SQLite, persistibilidade, mensagens seguras e fakes offline definidos; P1-004 não iniciado | — |
| 09/09/2026 | Fases P0/P1 | Checkpoints reais reconciliados por leitura do Git | `G0/G1` → `VALIDATED`; `C00/C01` → `VALIDATED` | GPT-5.6 | `7275f75936988ffb45722f60d68b00ca6ab22e5d` e `f2ba1723e3bd74cbeb8bc136f465ca773cbc29fd` conferidos no histórico e no conteúdo commitado | C00/C01 |
| 09/09/2026 | INT-COL-P2-001 | Package do coletor iniciado | `TODO` → `IN_PROGRESS` | GPT-5.6 | inventário de consumidores concluído; migração para `trt18_collector` iniciada; P2-002 não iniciada | — |
| 09/09/2026 | INT-COL-P2-001 | Package instalado e fronteira validada | `IN_PROGRESS` → `VALIDATED` | GPT-5.6 | 3 testes focados, bootstrap FastAPI, CLI, metadata e notebook aprovados; sem coleta; P2-002 não iniciada | — |
| 09/09/2026 | INT-COL-P2-002 | Contrato do adapter iniciado | `TODO` → `IN_PROGRESS` | GPT-5 (Codex) | fronteira e consumidores mapeados; somente o item autorizado foi marcado | — |
| 09/09/2026 | INT-COL-P2-002 | Contrato local-first auto-validado | `IN_PROGRESS` → `VALIDATED` | GPT-5 (Codex) | 41 testes focados, 84 do chatbot e 3 do package aprovados; sem efeitos externos ou ligação com Agent 2/SQLite real | — |
| 09/09/2026 | INT-COL-P2-003 | Cobertura offline da fronteira iniciada | `TODO` → `IN_PROGRESS` | GPT-5.6 | auditoria dos contratos P1/P2 e da suíte existente; somente o item autorizado foi marcado | — |
| 09/09/2026 | INT-COL-P2-003 | Matriz offline auto-validada | `IN_PROGRESS` → `VALIDATED` | GPT-5 (Codex) | 58 testes focados, 101 do chatbot, 3 do package, CLI/import/notebook e bloqueio de socket aprovados; sem efeitos externos | — |
| 09/09/2026 | Fase P2 | G2 tecnicamente apto; checkpoint aguarda autorização | `G2 IN_PROGRESS` → `VALIDATED`; `C02 TODO` → `READY` | GPT-5 (Codex) | INT-COL-P2-001..003 validados, regressão e diff check aprovados; nenhum commit criado | — |
| 09/09/2026 | Fase P2 | Fechamento real reconciliado por leitura do Git | `C02 READY` → `VALIDATED` | GPT-5 (Codex) | commit c01a5b50bc63413ee7a9734b02abd77dabf1a5d5 conferido no HEAD e no conteúdo | C02 |
| 09/09/2026 | INT-COL-P3-001 | Composição local-first iniciada | `TODO` → `IN_PROGRESS`; `G3 TODO` → `IN_PROGRESS` | GPT-5 (Codex) | defaults produtivos e seams explícitos definidos sem ligar Agent 2 ou persistência | — |
| 09/09/2026 | INT-COL-P3-001 | Composição local-first auto-validada | `IN_PROGRESS` → `VALIDATED` | GPT-5 (Codex) | 62 testes focados, 105 do chatbot, 3 do package, import leve, CLI e diff check aprovados; P3-002 não iniciado | — |
| 11/09/2026 | Fase P3 | Integração de persistência, Agent 2 e reutilização iniciada | `P3-002/P3-003/P3-004 TODO` → `IN_PROGRESS` | GPT-5 (Codex) | precondição técnica da P2 e checkpoint C02 confirmados; execução conjunta dos quatro IDs autorizada, preservando o histórico já validado de P3-001 | — |
| 11/09/2026 | Fase P3 | Implementação integrada concluída; validação reservada ao usuário | `P3-002/P3-003/P3-004 IN_PROGRESS` → `IMPLEMENTED` | GPT-5 (Codex) | 94 testes focados, 117 do chatbot e 3 do coletor aprovados; round-trip, rollback, progresso seguro e três cenários de reutilização comprovados offline | — |
| 11/09/2026 | Fase P3/C03 | Validação técnica aprovada, mas checkpoint reprovado por escopo misto | `C03 TODO` → `BLOCKED`; `G3 IN_PROGRESS` preservado | GPT-5 (Codex) | commit 485ee7d contém 25 arquivos, incluindo avaliação, proxy, PIDs e runtime Node; diff global falha em whitespace; itens não promovidos a VALIDATED | C03 |
| 11/09/2026 | Fase P3/C03 | Fechamento autorizado para a branch própria de trabalho | `P3-002/P3-003/P3-004 IMPLEMENTED` → `VALIDATED`; `G3/C03` → `VALIDATED` | GPT-5 (Codex) | usuário aceitou artefatos auxiliares versionados nesta branch; gate funcional restrito da P3 e todas as regressões passaram; limpeza global permanece obrigatória antes da main | C03 |
| 11/09/2026 | Fase P4 | Tratamento de estados, degradação e falhas iniciado | `P4-001/P4-002/P4-003 TODO` → `IN_PROGRESS`; `G4 TODO` → `IN_PROGRESS` | GPT-5 (Codex) | P3/C03 confirmados; achatamento na mensagem pública diagnosticado | — |
| 11/09/2026 | Fase P4 | Implementação integrada concluída; validação reservada ao usuário | `P4-001/P4-002/P4-003 IN_PROGRESS` → `IMPLEMENTED` | GPT-5 (Codex) | 17 testes P4, 111 focados, 134 do chatbot e 3 do coletor aprovados; API, segurança, não persistência e rollback com dado anterior comprovados | — |
| 11/09/2026 | Fase P4/C04 | Validação e fechamento autorizados pelo usuário | `P4-001/P4-002/P4-003 IMPLEMENTED` → `VALIDATED`; `G4/C04` → `VALIDATED` | GPT-5 (Codex) | checkpoint 259b5ed conferido; 17 P4, 111 focados, 134 do chatbot e 3 do coletor reexecutados com sucesso; P5 não iniciada | C04 |

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

---

## INT-COL-P1-001 — registro detalhado

```text
ID: INT-COL-P1-001
DATA_HORA: 2026-09-08 11:30:11 -03:00
STATUS_ANTERIOR: READY
STATUS_FINAL: VALIDATED
MODELO_RECOMENDADO: GPT-5.6 Terra
MODELO_EXECUTADO: GPT-5.6 Terra
MOTIVO_DIVERGENCIA_MODELO: não aplicável.
DIAGNOSTICO_CONFIRMADO:
  FATO COMPROVADO PELO CÓDIGO: obter_processo(numero: str, *, usar_cache: bool=True, coletar: bool=True, headless: bool=False, status_cnj_planilha: Optional[str]=None) -> dict importa coletor_trt18 sob demanda; normaliza somente para dígitos e exige comprimento 20; então busca data/brutos/<20-dígitos>.json.
  FATO COMPROVADO POR EXECUÇÃO OFFLINE: introspecção confirmou a assinatura, retorno declarado dict, os cinco enums e Processo requerido apenas em processo/coleta. Entrada "abc" lançou ValueError; cache ausente/incompleto e cache desabilitado com coletar=False lançaram FileNotFoundError; JSON inválido propagou JSONDecodeError.
DECISAO_TECNICA: nenhuma decisão de adapter, consumidor, persistência, importação ou política de dados foi tomada; foi documentado apenas o contrato existente.
CONTRATO_FATUAL:
  ASSINATURA E FLUXO:
    numero é posicional ou por palavra-chave; todos os demais parâmetros são keyword-only. usar_cache só habilita a tentativa de leitura; coletar habilita coletor.coletar_processo; headless e status_cnj_planilha só são transportados para o coletor. A chamada real é coletor.coletar_processo(numero, headless=headless, salvar=True, status_cnj_planilha=status_cnj_planilha). Todo bruto aceito passa por normalizador.normalizar(bruto), Processo.model_dump_json() e json.loads(), retornando dict.
    FLUXO: entrada -> re.sub(\D,"",str(numero)) -> tamanho 20? -> [usar_cache e arquivo existe?] -> json.loads -> cache_aproveitavel? -> normalizar/retornar; caso contrário, coletar=False? FileNotFoundError : coleta real -> normalizar/retornar.
  VALIDAÇÃO:
    FATO: a fronteira servico.py remove não dígitos e só valida comprimento; aceita 20 dígitos mesmo sem DV, segmento ou TRT18 válidos no caminho de cache. A coleta real chama normalizar_numero_processo/validar_numero_cnj, que verifica comprimento, DV módulo 97, segmento 5 e tribunal 18, podendo lançar ValueError antes de navegador/rede. A CLI documentada valida integralmente antes do serviço. Portanto cache e coleta não aplicam as mesmas validações.
  CACHE:
    FATO: path é entrada-de-dados/data/brutos/<numero_normalizado>.json; a leitura só ocorre com usar_cache=True e exists(). JSON inválido não é capturado. cache_aproveitavel ignora status_coleta e só exige alguma respostas_api[].payload dict que contenha itensProcesso, poloAtivo ou poloPassivo. Ausente, JSON inválido, incompleto e usar_cache=False não produzem bruto reaproveitado; com coletar=False, ausente/incompleto/desabilitado levantam FileNotFoundError; com coletar=True acionam recoleta. Um cache com status não-SUCESSO mas payload completo é reaproveitado.
  ÁRVORE RETORNADA (Pydantic extra=forbid em todos os modelos):
    processo: numero:str obrigatório; numero_normalizado:str obrigatório; classe_judicial, assunto, orgao_julgador, unidade, jurisdicao: str|None=None; grau:str|None="1º Grau"; data_autuacao,data_distribuicao: date|None=None; valor_causa:float|None=None; situacao: PENDENTE|BAIXADO|INDEFINIDO=INDEFINIDO.
    partes_interessadas:list[Parte]=[]; Parte: polo ATIVO|PASSIVO|OUTROS=OUTROS, nome:str obrigatório, tipo/documento:str|None=None, representantes:list[str]=[]. documento é potencialmente sensível.
    movimentacoes:list[Movimentacao]=[]; Movimentacao: ordem:int e descricao:str obrigatórios; data:datetime|None=None; complemento/referencia:str|None=None.
    documentos:list[Documento]=[]; Documento: titulo:str obrigatório; data:datetime|None=None; tipo/id_documento:str|None=None. id_documento é metadado potencialmente sensível/interno.
    pendencias:list[str]=[]. coleta: fonte:str com URL TRT18 default; coletado_em:datetime default_factory now; versao_coletor:str|None; tempo_execucao_seg:float|None; status_coleta enum; tentativas_captcha:int|None; status_cnj_planilha:str|None; warnings:list[str]=[]; erros:list[str]=[]. Datas/enum são serializados em JSON por model_dump_json; valor da causa é convertido para float pelo normalizador.
  ESTADOS:
    SUCESSO: coletor atribui após CAPTCHA aceito e payload completo; encerra tentativas e normaliza/retorna normalmente.
    PARCIAL: CAPTCHA aceito sem payload completo no limite; adiciona warning, encerra a chamada normalmente, pode gerar árvore com listas vazias e será cache incompleto se não tiver chaves completas.
    FALHA: valor inicial do bruto; após cinco falhas sem erro recebe erro de CAPTCHA; tentativa final de timeout/Exception acrescenta erro e diagnóstico best effort; normaliza/retorna se o coletor conseguir finalizar.
    NAO_ENCONTRADO: dadosbasicos observado com lista vazia; adiciona erro, interrompe repetição, finaliza/normaliza/retorna.
    BLOQUEADO: resposta 403/429 em URL monitorada; adiciona erro, interrompe repetição, finaliza/normaliza/retorna.
    FATO POR EXECUÇÃO OFFLINE: normalizador propaga os cinco valores reconhecidos. Status ausente ou desconhecido usa fallback SUCESSO, pois status_map.get(bruto.get("status_coleta", "SUCESSO"), StatusColeta.SUCESSO).
  EXCEÇÕES NA FRONTEIRA:
    ValueError: servico para comprimento diferente de 20; coletor para comprimento/DV/segmento/TRT18 ou imagem CAPTCHA inválida; escapam salvo se ocorrerem dentro de _executar_tentativa, onde Exception é convertida em bruto.erros apenas na última tentativa.
    FileNotFoundError: cache ausente/incompleto com coletar=False; escapa. JSONDecodeError e erros de leitura de cache: não capturados no serviço, escapam. ImportError/erro de cv2, OCR ou Playwright em _carregar_dependencias_de_coleta: ocorrem antes do bloco de tentativas, escapam. Pydantic/normalização e serialização: não capturados, escapam. Erros de mkdir/write do bruto em _finalizar: não capturados, escapam.
    Playwright timeout e Exception dentro de _executar_tentativa: capturados, convertidos em erros no bruto só na última tentativa; screenshot/HTML de diagnóstico são best effort e silenciam falhas. Listener de resposta também silencia Exception. Rede/navegador/timeout podem ainda escapar se ocorrerem fora desse try (por exemplo dependências, sync_playwright, lançamento do browser, fechamento, finalização).
  EFEITOS COLATERAIS:
    Importação de servico carrega json/re/pathlib/normalizador; coletor só é importado na chamada, mas seu import ainda não carrega Playwright/OCR. Cache-only lê JSON; não escreve, não abre browser e não acessa rede. Coleta real altera sys.path para captcha, importa cv2/numpy/OCR/Playwright, pode ajustar cv2 globalmente, abre Chrome/Edge/Chromium, acessa URL TRT18 e APIs, aguarda/retry (até 5; 2s; timeouts 60s/12s/45s), e pode criar thread no event loop/Jupyter, alterando temporariamente a policy asyncio no Windows. Sempre chama coletor com salvar=True e pode criar/gravar data/brutos/<numero>.json; pode gravar captcha/img_captured.png; na falha final pode criar data/debug e gravar PNG/HTML; a coleta em lote imprime, mas obter_processo não contém print. Normalização e serialização são em memória.
  DIVERGÊNCIA DOCUMENTAÇÃO/CÓDIGO: docs/data-ingestion.md afirma corretamente a validação mínima direta do serviço e a validação completa só na coleta. A docstring do serviço diz que o resultado é sempre validado, mas não cobre exceções de leitura/importação/coleta/normalização que podem impedir qualquer retorno.
ARQUIVOS_MODIFICADOS: docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
RESUMO_DIFF: somente status, evidências e contrato factual operacional de P1-001; nenhum código, teste, fixture, cache, produto ou dependência alterado.
TESTES_EXECUTADOS: introspecção inspect.signature e schema Pydantic no chatbot_processual_ai/.venv (Pydantic 2.13.4); caracterização em memória de ValueError, FileNotFoundError, JSONDecodeError, cache incompleto, cache aproveitável FALHA, usar_cache=False e fallback de status; normalização da fixture sanitizada exemplos/exemplo_bruto.json.
RESULTADOS: todos os cenários offline executáveis passaram conforme o comportamento acima; fixture retornou Processo com SUCESSO e seis raízes esperadas. Nenhuma rede, coleta real, browser, CAPTCHA ou escrita no repositório foi acionada.
DOCUMENTACAO_ATUALIZADA: somente os dois artefatos operacionais autorizados; documentação do produto foi consultada e não alterada.
REVISAO_DO_DIFF: revisão focada confirmou apenas os dois arquivos autorizados, P0/G0/P1-002/C01 preservados e ausência de alteração funcional.
GIT_DIFF_CHECK: pass (git diff --check, após o preenchimento final).
SEGREDOS_DADOS_SENSIVEIS: nenhum dado real, cache real ou segredo lido/exposto; somente nomes/tipos e fixture sanitizada.
RISCOS_RESIDUAIS:
  RISCO IDENTIFICADO: cache aproveitável não considera status_coleta; uma árvore estruturalmente válida pode representar FALHA, PARCIAL, NAO_ENCONTRADO ou BLOQUEADO e conter listas vazias.
  RISCO IDENTIFICADO: status ausente/desconhecido é convertido em SUCESSO pelo normalizador.
  RISCO IDENTIFICADO: JSON inválido e múltiplas falhas técnicas podem escapar da fronteira pública; a promessa de retorno "sempre" validado é condicional.
  QUESTÃO ABERTA PARA P1-003/P1-004: semântica/persistibilidade de cada estado, tradução de exceções, contrato final do adapter, importação estável e política de dados permanecem sem decisão.
  INFERÊNCIA TÉCNICA: a coleta é uma fronteira de alto custo e efeito externo; consumidores devem distinguir retorno estrutural de coleta bem-sucedida.
DEPENDENCIAS_AFETADAS: G1 permanece IN_PROGRESS; INT-COL-P1-002 permanece TODO e não iniciado; C01 permanece TODO.
COMMIT_DA_FASE: C01
COMMIT_REAL: —
OBSERVACOES: Git read-only confirmou HEAD/C00 em 7275f75936988ffb45722f60d68b00ca6ab22e5d ("feat: P0 - Baseline estrutural") na branch esperada. O controle ainda mostra Commit real de C00 como —, portanto o hash não está registrado nele; divergência operacional preservada e encaminhada, sem reescrever P0.
```

---

## FASE P5 — implementação concluída; validação reservada ao usuário

```text
DATA_HORA: 2026-09-11 -03:00
IDS: INT-COL-P5-001, INT-COL-P5-002, INT-COL-P5-003, INT-COL-P5-004
STATUS_ANTERIOR: TODO
STATUS_FINAL_DESTA_RODADA: IMPLEMENTED; não promover a VALIDATED.
PRECONDICAO: P4/G4/C04 validados no HEAD 259b5ed7a10261f72162f47377ffba38f3dcfb3a.
IMPLEMENTACAO: requirements.txt agora pertence ao runtime FastAPI; requirements-dev.txt possui pytest; pyproject.toml do collector declara pydantic e o extra .[collect] (playwright, ddddocr, opencv-python, numpy). O SQLite relativo é resolvido a partir do módulo do backend. O Chromium Playwright é o padrão; TRT18_COLLECTOR_BROWSER_EXECUTABLE é override opcional. CAPTCHA transitório vai para data/debug/captcha e paths Chrome/Edge fixos foram removidos.
OWNERSHIP: notebook/pesquisa (pandas, openpyxl, jupyter, ipykernel) permanece fora do runtime integrado e não foi instalado.
EVIDENCIAS: venv novo .venv-p5-approved com Python 3.12.10, pip 25.0.1, Windows 11 64-bit; manifests oficiais instalaram runtime, pytest e trt18-collector[collect]; imports backend/adapter/collector leves e imports pesados passaram; health local retornou status ok; 112 testes focados, 135 do backend e 5 do collector passaram offline.
LIMITACAO_AMBIENTAL: python -m playwright install chromium foi tentado pelo fluxo oficial e falhou por SELF_SIGNED_CERT_IN_CHAIN. Nenhum bypass TLS, Chrome/Edge local, navegação, TRT18 ou coleta real foi usado.
G5: IN_PROGRESS; C05: IN_PROGRESS; COMMIT_REAL: —; COMMIT_CRIADO: não.
```

---

## FASE P5 — validação do checkpoint C05

```text
DATA_HORA: 2026-09-11 -03:00
CHECKPOINT_ENCONTRADO: 34e660a677e5d283d55e4f8323815c62ca0496d7 — chore(runtime): unify collector setup and configuration.
REVISAO_DO_COMMIT: 13 arquivos, escopo restrito a manifests, configuração/paths, ownership CAPTCHA, testes de paths e registros operacionais; git diff HEAD^ HEAD --check passou.
VALIDADO: P5-001 (ownership e imports declarados), P5-002 (SQLite/CWD, cache/debug, env e browser override) e P5-003 (fonte canônica e ausência de path local obrigatório).
TESTES_REEXECUTADOS: imports leves + health local; 135 passed no backend; 5 passed no collector; imports playwright/cv2/numpy/ddddocr passaram. Nenhuma rede TRT18, browser launch, CAPTCHA ou coleta real foi executada.
BLOQUEIO_CONFIRMADO: python -m playwright install --list não encontrou browser materializado; a instalação oficial de Chromium falha com SELF_SIGNED_CERT_IN_CHAIN. Não há evidência para validar browser/launch local sem contornar a cadeia TLS.
STATUS_FINAL: P5-001/P5-002/P5-003 VALIDATED; P5-004 BLOCKED; G5 e C05 BLOCKED.
COMMIT_DE_VALIDACAO: não criado.
```

---

## FASE P5 — aceite de exceção ambiental pelo usuário

```text
DATA_HORA: 2026-09-11 -03:00
DECISAO_DO_USUARIO: aceitar temporariamente a ausência de Chromium Playwright como limitação do computador corporativo, sem acesso para corrigir a cadeia TLS.
EVIDENCIA_PRESERVADA: o comando oficial foi tentado, Playwright/lista de browsers confirmou que não há browser materializado, e a falha foi SELF_SIGNED_CERT_IN_CHAIN; nenhuma configuração de segurança foi contornada.
ACEITE: P5-004 VALIDATED por decisão explícita do usuário, com ressalva ambiental documentada.
STATUS_FINAL: P5-001, P5-002, P5-003 e P5-004 VALIDATED; G5 e C05 VALIDATED no checkpoint 34e660a677e5d283d55e4f8323815c62ca0496d7.
PENDENCIA_RESIDUAL: em ambiente sem interceptação TLS, executar python -m playwright install chromium e validar launch local about:blank antes de usar coleta real.
COMMIT_DE_ACEITE: não criado.
```

---

## FASE P6 — regressões e matriz automatizada concluídas; aceite real bloqueado

```text
DATA_HORA: 2026-09-11 -03:00
IDS: INT-COL-P6-001, INT-COL-P6-002, INT-COL-P6-003, INT-COL-P6-004
PRECONDICAO: P3, P4 e P5 confirmadas no código, testes e registros; HEAD 34e660a677e5d283d55e4f8323815c62ca0496d7; ambiente oficial .venv-p5-approved com Python 3.12.10.
WORKTREE_INICIAL: alterações preexistentes somente em docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md e CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md, provenientes dos registros P5; preservadas.
P6_001: IMPLEMENTED. Testes focados e suíte completa passaram: 135 passed antes dos testes P6 e 143 passed após a inclusão da matriz. Baseline P0 era 43 passed; fechamentos P3/P4/P5 registravam 117/134/135 passed. O aumento é explicado por 8 testes P6, sem regressão de lookup local, consultas estruturadas, sessão, API, sanitização, repository ou RAG/degradação.
FRONTEND: nenhum arquivo frontend foi alterado na P6 ou desde C05. Desde C00 existe somente frontend/proxy.runtime.json, adicionado historicamente em C03 como configuração auxiliar de proxy local para porta 8001; nenhum fonte Angular foi alterado pela integração P6.
P6_002: IMPLEMENTED. 16 passed em 0.47 s no collector. Matriz cobre CNJ válido, formato, DV, segmento e tribunal inválidos; cache completo, ausente, JSON inválido e incompleto; normalização aninhada, opcionais, partes, movimentos e documentos; construção, rejeição e serialização Pydantic; serviço público cache-only. Socket e coletor externo são proibidos objetivamente no teste cache-only. Fixtures e baselines versionadas permaneceram sem diff.
P6_003: IMPLEMENTED. 8 passed em 1.01 s, repetidos com o mesmo resultado. API ASGI, orquestrador, Agent 2, CollectorAdapter, repository e SQLite isolado são reais; somente interpretação/RAG não determinísticos e fronteira externa TRT18 são substituídos. Comprovados LOCAL_HIT sem coleta; MISS com uma coleta, persistência, reload e processo ativo; segunda pergunta, nova sessão e restart sem recoleta; NOT_FOUND/PARTIAL/BLOCKED/FAILED distintos; exceção segura; rollback sem persistência parcial e com preservação de dado anterior; envelope HTTP restrito aos DTOs públicos.
P6_004: BLOCKED. Nenhum número processual foi explicitamente autorizado ou configurado para esta execução. A limitação P5 de Chromium Playwright não materializado também permanece. TRT18 não foi acessado; nenhum dado real foi lido, persistido ou exposto.
TESTES_EXECUTADOS: focados backend 135 passed em 3.54 s; backend completo inicial 135 passed em 3.45 s; collector P6 focado 16 passed em 0.59 s; matriz P6 8 passed em 1.01 s; repetição matriz P6 8 passed em 1.01 s; backend completo final 143 passed em 5.32 s; collector completo final 16 passed em 0.47 s.
CORRECOES_PRODUCAO: nenhuma. As falhas intermediárias eram exclusivamente dos testes novos (montagem de CNJ sintético, tmp global sem permissão e bloqueio amplo de socket interferindo no loop ASGI); corrigidas sem alterar código funcional.
ARQUIVOS_P6: chatbot_processual_ai/tests/test_p6_end_to_end_integration.py; entrada-de-dados/tests/test_offline_collector_contract.py; docs/CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md; CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md.
SEGURANCA: nenhuma rede TRT18, browser, CAPTCHA, dado processual real, banco operacional, cache real, HTML, screenshot, raw JSON, segredo, commit ou push. Bancos e caches sintéticos efêmeros foram removidos pelos fixtures.
GIT_DIFF_CHECK: pass; somente avisos informativos LF/CRLF nos dois documentos operacionais.
STATUS_FINAL: P6-001 IMPLEMENTED; P6-002 IMPLEMENTED; P6-003 IMPLEMENTED; P6-004 BLOCKED; G6 BLOCKED; C06 BLOCKED e sem hash.
COMMIT_CRIADO: não.
```
