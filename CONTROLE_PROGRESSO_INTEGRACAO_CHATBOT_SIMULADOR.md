# CONTROLE DE PROGRESSO — Integração Chatbot + Simulador

**Data inicial:** 2026-10-14

**Branch:** `feat/integracao_robo_metas`

**Commit base:** `236e033ec74b9773542e1add13343fc4819fc07c`

**Checklist oficial desta integração:** `CHECKLIST_INTEGRACAO_CHATBOT_SIMULADOR.md`

**Escopo:** somente integração dos dois snapshots. Checklists temporariamente retiradas **não** fazem parte desta execução e não devem ser recriadas, apagadas ou tratadas como autorização de alteração.

## Estados permitidos

- `TODO`: não iniciado.
- `IN_PROGRESS`: execução em andamento, sem aceite.
- `BLOCKED`: depende de decisão, permissão, ambiente ou informação ausente.
- `FAILED`: implementado/tentado, mas critérios de aceite ou teste falharam.
- `VALIDATED`: requisito satisfeito, testes/evidências registrados e commit identificado.
- `SKIPPED_APPROVED`: deliberadamente não aplicável, com justificativa e aprovação registrada.

**Regra:** marcar `VALIDATED` só após verificação objetiva. Não deduzir conclusão de outro item ou de commits sem testes. Nunca marcar retroativamente sem evidência.

## Painel

| Indicador | Inicial |
|---|---:|
| Total de itens | 45 |
| Validated | 12 |
| In progress | 0 |
| Blocked | 0 |
| Failed | 0 |
| Todo | 33 |
| Skip aprovado | 0 |
| Progresso validado | 26,67% |

## Fases

| Fase | Itens | Total | Validados | Situação |
|---|---|---:|---:|---|
| 0 — Segurança e inventário | INT-001–006 | 6 | 6 | VALIDATED |
| 1 — Repositório e execução | INT-007–011 | 5 | 5 | VALIDATED |
| 2 — Contratos e proxy | INT-012–016 | 5 | 1 | IN_PROGRESS |
| 3 — Chat real | INT-017–024 | 8 | 0 | TODO |
| 4 — Simulador no frontend | INT-025–030 | 6 | 0 | TODO |
| 5 — Integração entre motores | INT-031–036 | 6 | 0 | TODO |
| 6 — Qualidade e entrega | INT-037–045 | 9 | 0 | TODO |
| **Total** | | **45** | **12** | **IN_PROGRESS** |

## Registro item a item

| ID | Estado | Commit | Teste/evidência | Observação |
|---|---|---|---|---|
| INT-001 | VALIDATED | `chore(integracao): validar INT-001` | Branch, raiz, origin, commit-base, status e rollback conferidos | Branch local sem upstream; alterações preexistentes preservadas fora do staging |
| INT-002 | VALIDATED | `chore(integracao): importar snapshot no INT-002` | 69 arquivos/665.467 bytes inventariados; importação somente aditiva; varredura de segredos sem achados | Três modelos TypeScript adicionados explicitamente por conflito conhecido com `.gitignore` |
| INT-003 | VALIDATED | `docs(integracao): mapear componentes no INT-003` | Mapa aplicação→função→destino, duplicatas SHA-256 e candidatos inativos documentados | Nenhum arquivo removido; decisões reservadas ao INT-006 |
| INT-004 | VALIDATED | `test(integracao): registrar baselines no INT-004` | Versões, comandos e resultados offline documentados; smoke do simulador aprovado | Pytest e Node/npm ausentes; Angular importado sem angular.json |
| INT-005 | VALIDATED | `docs(integracao): mapear contratos no INT-005` | Matriz de 9 rotas com verbos, schemas, status, timeouts e dependências | Colisão de health e lacunas de proxy confirmadas |
| INT-006 | VALIDATED | `docs(integracao): validar arquitetura híbrida no INT-006` | ADR-001 aprovado com `frontend/` canônico e UI importada como referência mais recente | Contratos/sessão/testes atuais serão combinados com a experiência visual importada |
| INT-007 | VALIDATED | `chore(integracao): estabelecer estrutura no INT-007` | Backend promovido para `simulador_metas_cnj/`; hashes e smoke conferidos | Quarentena e legado preservados; transporte do frontend permanece incremental |
| INT-008 | VALIDATED | `chore(integracao): consolidar ignores no INT-008` | Modelos TypeScript visíveis; índice e exemplos de ambiente auditados | Variáveis do simulador serão consumidas no INT-011 |
| INT-009 | VALIDATED | `docs(integracao): documentar ambiente no INT-009` | Python/Node/npm/Angular, manifests e comandos reproduzíveis documentados | Backends exigem ambientes Python separados |
| INT-010 | VALIDATED | `chore(integracao): adicionar inicialização no INT-010` | Scripts PowerShell analisados sintaticamente; portas 8000/8001/4200 distintas | Execução integral depende dos ambientes documentados no INT-009 |
| INT-011 | VALIDATED | `feat(integracao): configurar ambientes no INT-011` | Proxy dividido por namespace; scripts parametrizados; simulador usa configuração de ambiente | Alias `/api/health` mantido temporariamente para compatibilidade |
| INT-012 | VALIDATED | `feat(integracao): tipar contrato do chat no INT-012` | 15 testes de API e contrato; 19 testes Angular; OpenAPI declara request, resposta e erro 422 | Bloqueio ambiental removido com ambientes locais isolados e Node portátil ignorado pelo Git |
| INT-013 | TODO | — | — | — |
| INT-014 | TODO | — | — | — |
| INT-015 | TODO | — | — | — |
| INT-016 | TODO | — | — | — |
| INT-017 | TODO | — | — | — |
| INT-018 | TODO | — | — | — |
| INT-019 | TODO | — | — | — |
| INT-020 | TODO | — | — | — |
| INT-021 | TODO | — | — | — |
| INT-022 | TODO | — | — | — |
| INT-023 | TODO | — | — | — |
| INT-024 | TODO | — | — | — |
| INT-025 | TODO | — | — | — |
| INT-026 | TODO | — | — | — |
| INT-027 | TODO | — | — | — |
| INT-028 | TODO | — | — | — |
| INT-029 | TODO | — | — | — |
| INT-030 | TODO | — | — | — |
| INT-031 | TODO | — | — | — |
| INT-032 | TODO | — | — | — |
| INT-033 | TODO | — | — | — |
| INT-034 | TODO | — | — | — |
| INT-035 | TODO | — | — | — |
| INT-036 | TODO | — | — | — |
| INT-037 | TODO | — | — | — |
| INT-038 | TODO | — | — | — |
| INT-039 | TODO | — | — | — |
| INT-040 | TODO | — | — | — |
| INT-041 | TODO | — | — | — |
| INT-042 | TODO | — | — | — |
| INT-043 | TODO | — | — | — |
| INT-044 | TODO | — | — | — |
| INT-045 | TODO | — | — | — |

## Diário de execução (acrescentar entradas, não apagar histórico)

### Entrada inicial — 2026-10-14
- **Atividade:** planejamento da integração com base nos ZIPs recebidos.
- **Estado do repositório real:** ainda não verificado; nenhuma mudança de código executada por este plano.
- **Decisões pendentes:** nome/commit da branch, pasta da importação, Angular canônico, organização dos serviços.
- **Próximo item:** `INT-001`.

### INT-001 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `236e033ec74b9773542e1add13343fc4819fc07c`.
- **Arquivos modificados:** checklist e controle oficiais da integração.
- **Resumo técnico:** raiz Git e `origin` confirmados; branch local confirmada sem upstream; commit-base registrado; 68 arquivos não rastreados identificados; mudanças preexistentes separadas e preservadas fora do staging.
- **Comandos e resultados:** `git rev-parse HEAD`, `git branch -vv`, `git remote -v`, `git status --porcelain=v2 --branch`, `git diff --check`; verificações concluídas sem alterar código funcional.
- **Evidência do aceite:** relatório de preflight registrado antes de qualquer edição de código; rollback disponível pela preservação do commit-base e por commits locais atômicos, sem reescrita de histórico.
- **Riscos:** `.codex/rules/safety.rules`, `AGENTS.md` e duas exclusões antigas permanecem como mudanças preexistentes não incluídas; a pasta importada permanece não rastreada para tratamento em `INT-002`.
- **Commit:** identificado pelo assunto `chore(integracao): validar INT-001`; o próprio commit que contém esta entrada é a evidência imutável, evitando referência circular ao seu SHA.
- **Próximo item:** `INT-002`.

### INT-002 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `7fd8d7cf8adecf5f282dc74bb887106efff66e26`.
- **Arquivos modificados:** 69 arquivos sob `integracao_entrada/TCC-Simulador-CNJ/`, `.gitattributes`, inventário `docs/integracao/INT-002_INVENTARIO_IMPORTACAO.md` e este controle.
- **Resumo técnico:** snapshot preservado em quarentena, sem sobreposição; 66 arquivos normalmente versionáveis e três modelos TypeScript forçados por uma regra genérica `models/` do `.gitignore`.
- **Comandos e resultados:** inventário recursivo, `git ls-files --others`, `git check-ignore -v`, inspeção de links, nomes e padrões de segredo e conteúdo textual das planilhas; 69 arquivos, 665.467 bytes, nenhum link e nenhum indício de segredo.
- **Evidência do aceite:** diff do item exclusivamente aditivo e inventário em `docs/integracao/INT-002_INVENTARIO_IMPORTACAO.md`.
- **Riscos:** a regra genérica de ignore será corrigida no `INT-008`; cinco caminhos de quarentena possuem exceção de whitespace para preservar o snapshot; as planilhas são preservadas como baseline somente leitura.
- **Commit:** identificado pelo assunto `chore(integracao): importar snapshot no INT-002`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-003`.

### INT-003 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `38b9108e6452ae79e1886d3fb88b598f996eab09`.
- **Arquivos modificados:** `docs/integracao/INT-003_MAPA_COMPONENTES.md` e este controle.
- **Resumo técnico:** aplicações, backends, módulos, configurações e scripts foram mapeados; duplicatas exatas foram comparadas por SHA-256; árvores incompletas e candidatos inativos foram registrados sem exclusão.
- **Comandos e resultados:** inventário recursivo, busca de manifests/entradas/imports, leitura de rotas e scripts e agrupamento de hashes; foi confirmado que somente `frontend/` possui `angular.json`.
- **Evidência do aceite:** mapa arquivo/grupo → função → destino candidato em `docs/integracao/INT-003_MAPA_COMPONENTES.md`.
- **Riscos:** o frontend importado não é executável isoladamente no estado recebido por ausência de `angular.json`; a árvore Angular canônica permanece decisão do `INT-006`.
- **Commit:** identificado pelo assunto `docs(integracao): mapear componentes no INT-003`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-004`.

### INT-004 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `70ae343`.
- **Arquivos modificados:** `docs/integracao/INT-004_BASELINES_LOCAIS.md` e este controle.
- **Resumo técnico:** comandos e testes de ambos os projetos foram identificados e tentados offline; versões e limitações ambientais foram separadas de falhas funcionais.
- **Comandos e resultados:** Python 3.12.10; backend do simulador importado e smoke de `health/base/simular/comparar/otimizador` aprovados; chatbot/collector limitados por `pytest`, package e versão global de Pydantic; frontends limitados pela ausência de Node/npm e o importado também pela ausência de `angular.json`.
- **Evidência do aceite:** relatório reproduzível em `docs/integracao/INT-004_BASELINES_LOCAIS.md`.
- **Riscos:** não há baseline Angular executada neste host; nenhuma falha foi atribuída à integração sem ambiente compatível.
- **Commit:** identificado pelo assunto `test(integracao): registrar baselines no INT-004`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-005`.

### INT-005 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `7221dbc`.
- **Arquivos modificados:** `docs/integracao/INT-005_MATRIZ_ROTAS_CONTRATOS.md` e este controle.
- **Resumo técnico:** nove rotas FastAPI e os clientes/proxies Angular foram mapeados por verbo, entrada, saída, status, timeout e dependências.
- **Comandos e resultados:** leitura dos decoradores/modelos/serviços, busca de timeouts e geração local da OpenAPI do simulador; 200/400/422/500 e contratos efetivos documentados.
- **Evidência do aceite:** matriz revisável em `docs/integracao/INT-005_MATRIZ_ROTAS_CONTRATOS.md`.
- **Riscos:** os dois healthchecks colidem; `/api/chat` não existe; `comparar`/`otimizador` não estão integralmente ligados ao proxy/UI; respostas FastAPI do simulador ainda não têm modelos declarados.
- **Commit:** identificado pelo assunto `docs(integracao): mapear contratos no INT-005`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-006`.

### INT-006 — 2026-10-16 — checkpoint de decisão
- **Estado anterior → novo:** `TODO` → `BLOCKED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `c12cf1d`.
- **Arquivos modificados:** `docs/integracao/ADR-001_ARQUITETURA_APLICACAO_UNIFICADA.md` e este controle.
- **Resumo técnico:** três alternativas foram comparadas. A proposta mantém `frontend/` como Angular canônico, promove o backend do simulador para `simulador_metas_cnj/`, conserva dois FastAPI e separa rotas em `/api/processos/*` e `/api/simulador/*`.
- **Evidência:** ADR-001 fundamentado pelos inventários `INT-003` e `INT-005`.
- **Bloqueio:** o critério de aceite exige aprovação antes de mover código; nenhuma movimentação foi iniciada.
- **Commit:** identificado pelo assunto `docs(integracao): propor arquitetura no INT-006`.
- **Próximo passo:** obter aprovação humana do ADR-001; somente então validar `INT-006` e iniciar `INT-007`.

### INT-006 — 2026-10-16 — desbloqueio
- **Estado anterior → novo:** `BLOCKED` → `VALIDATED`.
- **Direcionamento aprovado:** solução híbrida; `frontend/` é o workspace canônico, enquanto a interface e as funcionalidades visuais importadas representam a versão mais recente a preservar.
- **Critério de composição:** transportar a UI recente e manter do frontend atual o contrato processual real, sessão, erros/timeouts, tipos e testes.
- **Arquivos modificados:** ADR-001 e este controle.
- **Evidência do aceite:** aprovação humana registrada na conversa e incorporada ao ADR.
- **Commit:** identificado pelo assunto `docs(integracao): validar arquitetura híbrida no INT-006`.
- **Próximo item:** `INT-007`.

### INT-007 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `3839bd3b5db895c78a7ae2b3136aab011e1ef468`.
- **Arquivos modificados:** nova árvore `simulador_metas_cnj/`, `.gitattributes` e este controle.
- **Resumo técnico:** backend e dados do simulador foram copiados para o destino operacional aprovado; a origem em quarentena e todas as árvores legadas permaneceram intactas.
- **Comandos e resultados:** comparação SHA-256 confirmou igualdade dos sete arquivos de origem; cache Python gerado localmente foi excluído do destino; parsing/import/smoke offline foram repetidos no novo caminho.
- **Evidência do aceite:** `simulador_metas_cnj/README.md` registra proveniência, função e destino; movimentação rastreável e somente aditiva.
- **Riscos:** whitespace legado de `robo_cnj_meta2.py` permanece preservado e possui exceção de atributo restrita ao arquivo; a UI ainda não foi transportada, conforme fases específicas.
- **Commit:** identificado pelo assunto `chore(integracao): estabelecer estrutura no INT-007`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-008`.

### INT-008 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `5f40c62`.
- **Arquivos modificados:** `.gitignore`, `simulador_metas_cnj/.env.example`, `docs/integracao/INT-008_AUDITORIA_VERSIONAMENTO.md` e este controle.
- **Resumo técnico:** ignore de modelos foi limitado a artefatos de ML; modelos TypeScript deixaram de ser ocultados; configuração exemplo do simulador foi adicionada sem segredos.
- **Comandos e resultados:** inspeção de todos os `.gitignore`/`.env.example`, `git check-ignore`, busca de tipos proibidos no índice e varredura textual; nenhum segredo ou artefato proibido identificado.
- **Evidência do aceite:** auditoria em `docs/integracao/INT-008_AUDITORIA_VERSIONAMENTO.md`.
- **Riscos:** as variáveis propostas ainda não são consumidas pelo código; implementação pertence ao `INT-011`.
- **Commit:** identificado pelo assunto `chore(integracao): consolidar ignores no INT-008`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-009`.

### INT-009 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `b07bb4d`.
- **Arquivos modificados:** `docs/development.md`, `simulador_metas_cnj/README.md`, matriz de ambiente e este controle.
- **Resumo técnico:** versões suportadas, manifests, isolamento e comandos de instalação/execução/teste foram consolidados para chatbot, collector, simulador e Angular.
- **Evidência do aceite:** `docs/integracao/INT-009_MATRIZ_AMBIENTE.md` e instruções completas em `docs/development.md`.
- **Limitações:** a reprodução não foi executada neste host por ausência de Node/npm e pytest; nenhuma dependência foi baixada. O lockfile Node e os pins do simulador são exatos; o chatbot preserva os limites declarados nos manifests existentes.
- **Commit:** identificado pelo assunto `docs(integracao): documentar ambiente no INT-009`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-010`.

### INT-010 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `7536315`.
- **Arquivos modificados:** três scripts em `scripts/`, `docs/development.md` e este controle.
- **Resumo técnico:** comandos individuais em primeiro plano foram criados para chatbot (8000), simulador (8001) e frontend (4200), com validação de `.venv`, npm e `node_modules`.
- **Testes:** parsing sintático dos três scripts PowerShell sem erros; argumentos, diretórios operacionais e portas revisados. Processos não foram iniciados por ausência dos ambientes locais completos.
- **Evidência do aceite:** seção “Inicialização individual” de `docs/development.md` e scripts versionados.
- **Commit:** identificado pelo assunto `chore(integracao): adicionar inicialização no INT-010`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-011`.

### INT-011 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `1429a6d`.
- **Arquivos modificados:** proxy Angular, três scripts de inicialização, `simulador_metas_cnj/main.py`, documentação e este controle.
- **Resumo técnico:** URLs permanecem relativas no Angular; proxy separa processo e simulador; host/porta são configuráveis; o simulador resolve diretório de dados por ambiente e usa 8001 como default.
- **Testes:** JSON do proxy parseado; scripts PowerShell analisados; simulador importado/smoke com configuração default e customizada; `git diff --check` aprovado.
- **Evidência do aceite:** desenvolvimento usa `/api/processos/*` → 8000 e `/api/simulador/*` → 8001, sem endereços institucionais ou credenciais.
- **Riscos:** o health do frontend ainda usa alias `/api/health` por compatibilidade; migração ao namespace explícito pertence ao `INT-041`.
- **Commit:** identificado pelo assunto `feat(integracao): configurar ambientes no INT-011`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-012`.

### INT-012 — 2026-10-16 — checkpoint ambiental
- **Estado anterior → novo:** `TODO` → `BLOCKED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `f48447f`.
- **Diagnóstico:** o Python global possui Pydantic 1.10.26 e não possui pytest; o backend processual exige Pydantic 2 (`field_validator`). Não há `.venv`, wheel ou pacote aplicável no cache local.
- **Verificações:** `python -m pytest` falha por módulo ausente; import de `api` falha pela versão de Pydantic; `pip cache` não oferece os pacotes necessários; apenas um Python 3.12 está instalado.
- **Bloqueio:** o critério exige teste de contrato correspondente ao backend. Sem dependências e sem autorização de rede, não é possível validar uma alteração de API com segurança.
- **Mudanças funcionais:** nenhuma; contratos e código permaneceram intactos.
- **Commit:** identificado pelo assunto `chore(integracao): registrar bloqueio do INT-012`.
- **Desbloqueio necessário:** autorização explícita para criar `.venv` e baixar as dependências versionadas do chatbot. A instalação de Node/npm também será necessária antes dos itens Angular.

### INT-012 — 2026-10-16 — desbloqueio e validação
- **Estado anterior → novo:** `BLOCKED` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `d02c3ce`.
- **Arquivos modificados:** contrato HTTP do chatbot, tipos compartilhados do Angular, teste de contrato, `.gitignore` e este controle.
- **Resumo técnico:** a rota `POST /api/processos/chat` agora publica modelos Pydantic explícitos para request e response; `tipo` é discriminado, `session_id` e `resultado.resposta` são obrigatórios, e o erro de validação 422 permanece formalizado pelo OpenAPI. O frontend possui tipos correspondentes para sucesso e erro estruturado.
- **Ambiente local:** dependências instaladas em `.venv` isoladas; Node 24.19.0/npm 11.17.0 portátil validado por SHA-256 e mantido em `.tools/`, ignorado pelo Git.
- **Testes:** `python -m pytest tests/test_api_processual_chat.py -q` → 15 aprovados; suíte Python completa com cache desativado → 144 aprovados; `npm test -- --watch=false` → 6 arquivos/19 testes aprovados; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** OpenAPI referencia `ProcessualChatHTTPRequest`, `ProcessualChatHTTPResponse` e `HTTPValidationError`; resposta serializada e tipagem Angular cobrem os campos obrigatórios e os erros.
- **Riscos:** `npm audit` reportou vulnerabilidades transitivas; não foi aplicado `npm audit fix` porque alteraria o lockfile fora do item. O aviso de cache do pytest é restrição local e não afetou os testes.
- **Commit:** identificado pelo assunto `feat(integracao): tipar contrato do chat no INT-012`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-013`.

### Modelo para cada execução

```text
Data/hora:
Item:
Estado anterior → novo:
Branch/commit antes:
Arquivos modificados:
Resumo técnico:
Comandos e resultados dos testes:
Evidência do critério de aceite:
Riscos/regressões identificados:
Commit SHA (se validado):
Próximo item/desbloqueios:
```

## Protocolo operacional para Codex

1. Ler `AGENTS.md`, regras de segurança do repositório, checklist e este controle, além dos arquivos pertinentes ao item.
2. Conferir branch e `git status`; não tocar em mudanças preexistentes sem identificar proprietário e pedir autorização.
3. Selecionar **somente um** item `TODO` com pré-requisitos concluídos. Para itens de decisão, documentar e solicitar aprovação antes de executar alterações dependentes.
4. Informar plano e caminhos; aplicar alteração mínima e reversível; não fazer exclusões não autorizadas.
5. Rodar os testes do item, `git diff --check` e verificação de regressões apropriada. Não disparar chamadas externas institucionais.
6. Se aprovado, criar commit específico (se a política de repositório permitir), marcar `VALIDATED`, registrar hash e evidência. Se falhar, registrar `FAILED` ou `BLOCKED` e não afirmar conclusão.
7. Atualizar este painel, a tabela e diário **na mesma execução**, sem reescrever histórico.
8. Parar e comunicar bloqueios ou necessidade de homologação; nunca avançar autonomamente para alterações destrutivas.

## Prompt-base reutilizável

> Leia as regras locais, `CHECKLIST_INTEGRACAO_CHATBOT_SIMULADOR.md` e `CONTROLE_PROGRESSO_INTEGRACAO_CHATBOT_SIMULADOR.md`. Execute **somente** o item `INT-XXX`, conferindo pré-requisitos, branch e worktree. Preserve integralmente os dois projetos e não execute coleta externa. Mostre diff, execute testes relevantes e `git diff --check`. Registre evidências, status e commit no controle. Em dúvida, bloqueie sem improvisar. Não execute outro item automaticamente.

## Regras de contabilização

- Total = 45 itens fixos (novos itens exigem atualização de ambos os arquivos, explicação e revisão de totais).
- Percentual validado = `VALIDATED / total × 100`; `SKIPPED_APPROVED` não conta como trabalho validado.
- Se um item validado regredir, reabrir como `FAILED` com justificativa e corrigir o painel.
- A aprovação do PR, integração final e publicação são etapas distintas. Este controle não autoriza deploy nem merge.
