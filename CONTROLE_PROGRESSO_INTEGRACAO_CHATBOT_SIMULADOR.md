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
| Validated | 31 |
| In progress | 0 |
| Blocked | 0 |
| Failed | 0 |
| Todo | 14 |
| Skip aprovado | 0 |
| Progresso validado | 68,89% |

## Fases

| Fase | Itens | Total | Validados | Situação |
|---|---|---:|---:|---|
| 0 — Segurança e inventário | INT-001–006 | 6 | 6 | VALIDATED |
| 1 — Repositório e execução | INT-007–011 | 5 | 5 | VALIDATED |
| 2 — Contratos e proxy | INT-012–016 | 5 | 5 | VALIDATED |
| 3 — Chat real | INT-017–024 | 8 | 8 | VALIDATED |
| 4 — Simulador no frontend | INT-025–030 | 6 | 6 | VALIDATED |
| 5 — Integração entre motores | INT-031–036 | 6 | 1 | IN_PROGRESS |
| 6 — Qualidade e entrega | INT-037–045 | 9 | 0 | TODO |
| **Total** | | **45** | **31** | **IN_PROGRESS** |

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
| INT-013 | VALIDATED | `feat(integracao): formalizar contratos do simulador no INT-013` | Fixtures válidas/inválidas e 3 testes; quatro respostas validadas contra seus schemas | Requests rejeitam campos e valores fora do contrato; respostas publicadas no OpenAPI |
| INT-014 | VALIDATED | `test(integracao): validar proxy no INT-014` | 3 testes/8 rotas confirmam destinos e rewrites por namespace | Healthchecks processual e simulador chegam a portas distintas |
| INT-015 | VALIDATED | `feat(integracao): tratar falhas HTTP no INT-015` | 21 testes Angular cobrem timeout, rede, 4xx, 5xx e resposta 2xx inválida | Falhas permanecem no canal de erro e mensagens técnicas não são expostas |
| INT-016 | VALIDATED | `docs(integracao): definir timeouts no INT-016` | 21 testes Angular; timeout do chat exercitado com relógio virtual | Orçamentos centralizados por operação; chat reduzido de 135 s para 120 s |
| INT-017 | VALIDATED | `feat(integracao): tipar envio do chat no INT-017` | 22 testes Angular; spy HTTP confirma POST, corpo e sessão opcional | Sessão explícita pode sobrescrever a armazenada sem alterar o contrato público |
| INT-018 | VALIDATED | `refactor(integracao): consolidar modelos do chat no INT-018` | Build Angular aprovado; modelos sem `any` | Payload real, mensagens e erros estruturados centralizados em `chat.model.ts` |
| INT-019 | VALIDATED | `feat(integracao): usar resposta real no INT-019` | 23 testes Angular; sucesso renderiza `resultado.resposta`; falhas não criam mensagem bot | Nenhum `responderMock` ou resposta simulada no código de produção |
| INT-020 | VALIDATED | `test(integracao): validar sessao do chat no INT-020` | 25 testes Angular; duas requests consecutivas reutilizam o ID retornado | `sessionStorage` isola a sessão do navegador e permite limpeza explícita |
| INT-021 | VALIDATED | `feat(integracao): definir ciclo da conversa no INT-021` | 26 testes Angular; nova conversa limpa sessão/mensagens e preserva histórico | Refresh e limites da persistência local documentados |
| INT-022 | VALIDATED | `feat(integracao): controlar envio do chat no INT-022` | 27 testes Angular cobrem loading, duplicidade, cancelamento, rede e nova tentativa | Resposta tardia após cancelamento é ignorada |
| INT-023 | VALIDATED | `fix(integracao): proteger dados do chat no INT-023` | 28 testes Angular; markup permanece texto e resposta não vai ao storage | Revisão de logs documentada; histórico usa resumo genérico |
| INT-024 | VALIDATED | `test(integracao): validar chat offline no INT-024` | 8 testes E2E backend e 28 testes Angular previamente aprovados | Fixture local percorre HTTP→orquestrador→repositório→resposta; coletor externo proibido |
| INT-025 | VALIDATED | `feat(integracao): transportar UI do simulador no INT-025` | Build Angular aprovado; inventário antes/depois de 9 artefatos | Base, cenários, gráficos, tabela, otimizador e shell preservados na rota `/simulador` |
| INT-026 | VALIDATED | `feat(integracao): adaptar API do simulador no INT-026` | Build Angular aprovado; quatro contratos e timeouts tipados | URLs usam `/api/simulador/*`; nenhuma fórmula Python alterada |
| INT-027 | VALIDATED | `test(integracao): cobrir API do simulador no INT-027` | 33 testes Angular; base, simulação, vazio, rede e payload inválido | Falhas não emitem sucesso e são visíveis pelo estado de erro |
| INT-028 | VALIDATED | `test(integracao): cobrir comparar e otimizador no INT-028` | 35 testes Angular; requests/responses dos dois endpoints | Lacuna visual preservada e documentada conforme snapshot mais recente |
| INT-029 | VALIDATED | `feat(integracao): unificar navegacao no INT-029` | 36 testes Angular e build aprovados | Barra responsiva liga chat e simulador no mesmo app |
| INT-030 | VALIDATED | `test(integracao): fixar snapshot numerico no INT-030` | 5 testes do simulador; baseline 86 registros com tolerância 0,01 | Simulação vazia é idêntica à base; fórmulas não duplicadas no teste |
| INT-031 | VALIDATED | `docs(integracao): definir casos de uso no INT-031` | Matriz separa seis categorias e regras/proibições | Processo, diagnóstico individual e cenário agregado têm destinos distintos |
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

### INT-013 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `75dd16e`.
- **Arquivos modificados:** modelos e rotas do simulador, fixtures JSON, testes de contrato e este controle.
- **Resumo técnico:** `base`, `simular`, `comparar` e `otimizador` agora possuem response models explícitos; requests proíbem campos extras, e o otimizador restringe variável, meta e mês aos valores aceitos.
- **Testes:** `python -m unittest discover -s tests -v` → 3 aprovados; respostas reais dos quatro endpoints validadas pelos respectivos modelos; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** fixtures versionadas cobrem exemplos válidos e inválidos, e o OpenAPI referencia os quatro schemas de resposta esperados.
- **Riscos:** os registros mensais continuam flexíveis (`Dict[str, Any]`) porque a base tabular contém colunas heterogêneas; os campos de envelope e métricas são estritos.
- **Commit:** identificado pelo assunto `feat(integracao): formalizar contratos do simulador no INT-013`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-014`.

### INT-014 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `ea99197`.
- **Arquivos modificados:** script npm, teste automatizado do proxy e este controle.
- **Resumo técnico:** teste resolve a regra mais específica do proxy e aplica os mesmos rewrites declarados, cobrindo chatbot, metas integradas e todos os quatro endpoints do simulador.
- **Testes:** `npm run test:proxy` → 3 testes aprovados, cobrindo 8 rotas; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** `/api/processos/health` chega a `127.0.0.1:8000/api/health` e `/api/simulador/health` a `127.0.0.1:8001/api/health`, sem colisão; demais rotas mantêm o backend correto.
- **Riscos:** o teste verifica deterministicamente configuração, precedência e rewrite; disponibilidade dos processos locais permanece responsabilidade dos scripts de inicialização já validados.
- **Commit:** identificado pelo assunto `test(integracao): validar proxy no INT-014`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-015`.

### INT-015 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `9125e4e`.
- **Arquivos modificados:** serviço e componente do chat, testes correspondentes e este controle.
- **Resumo técnico:** o cliente valida em runtime o envelope de sucesso antes de entregá-lo à interface e emite erro específico para payload inválido; a UI classifica timeout, transporte, 4xx, 5xx e resposta inválida em mensagens públicas seguras.
- **Testes:** `npm test -- --watch=false` → 6 arquivos/21 testes aprovados; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** nenhum cenário de falha emite valor de sucesso; loading é finalizado, o erro aparece com `role=alert`, e detalhes técnicos não são renderizados.
- **Riscos:** a validação runtime checa o envelope e os campos discriminantes consumidos pela UI; validação integral de todas as propriedades permanece garantida pelo schema do backend e pela tipagem estática.
- **Commit:** identificado pelo assunto `feat(integracao): tratar falhas HTTP no INT-015`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-016`.

### INT-016 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `fdc3e23`.
- **Arquivos modificados:** configuração central de timeouts, serviço/teste do chat, decisão técnica e este controle.
- **Resumo técnico:** foram definidos limites distintos para health, base, cenário, comparação, otimizador e chat; o chat foi reduzido de 135 s para 120 s e passou a consumir a constante central.
- **Testes:** `npm test -- --watch=false` → 6 arquivos/21 testes aprovados; teste com relógio virtual confirma ausência de timeout antes do limite e cancelamento depois dele; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** operações locais recebem limites curtos e proporcionais; somente coleta/agentes/RAG possuem orçamento longo, documentado sem elevar o valor anterior.
- **Riscos:** os limites do simulador serão aplicados quando seu serviço Angular for transportado na fase 4; timeout do cliente não interrompe necessariamente trabalho já iniciado no backend.
- **Commit:** identificado pelo assunto `docs(integracao): definir timeouts no INT-016`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-017`.

### INT-017 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `dceeab9`.
- **Arquivos modificados:** serviço/teste HTTP do chat e este controle.
- **Resumo técnico:** `ChatService.enviar` usa request tipada em `POST /api/processos/chat` e aceita opção tipada de `sessionId`; quando omitida, mantém a sessão corrente, e quando nula, omite o campo do payload.
- **Testes:** `npm test -- --watch=false` → 6 arquivos/22 testes aprovados; spy HTTP confirma verbo, URL, mensagem e `session_id` explícito; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** o teste intercepta a chamada real do `HttpClientTestingController` e compara exatamente o corpo enviado.
- **Riscos:** nenhum retry automático foi introduzido; a validação runtime da resposta permanece ativa.
- **Commit:** identificado pelo assunto `feat(integracao): tipar envio do chat no INT-017`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-018`.

### INT-018 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `3b0c4da`.
- **Arquivos modificados:** modelos do chat, reexport de compatibilidade, consumidores TypeScript e este controle.
- **Resumo técnico:** `chat.model.ts` passou a ser a fonte canônica para mensagens, histórico, request/response real, erros 422 e classificação estruturada de falhas; coleções desconhecidas usam `unknown`, sem `any`.
- **Testes:** `npm run build` aprovado; bundle produzido com aviso preexistente de orçamento CSS, sem erro TypeScript; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** build de produção compila os consumidores contra os modelos centrais e busca textual não encontra `any` no modelo.
- **Riscos:** o arquivo antigo de tipos permanece apenas como reexport temporário para compatibilidade e pode ser removido quando não houver consumidores externos.
- **Commit:** identificado pelo assunto `refactor(integracao): consolidar modelos do chat no INT-018`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-019`.

### INT-019 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `31b08d3`.
- **Arquivos modificados:** validação/teste do serviço de chat e este controle.
- **Resumo técnico:** o único caminho de sucesso entrega `resultado.resposta` não vazio do backend; payload ausente ou em branco é falha explícita, sem texto mock ou fallback apresentado como resposta real.
- **Testes:** `npm test -- --watch=false` → 6 arquivos/23 testes aprovados; varredura do código de produção sem `responderMock`; testes do componente cobrem sucesso real e falhas; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** o DOM contém exatamente a resposta do envelope no sucesso; timeout, rede, HTTP e resposta inválida mantêm apenas a pergunta do usuário e mostram alerta honesto.
- **Riscos:** falhas controladas retornadas pelo backend em HTTP 200 continuam visíveis como mensagem segura do próprio backend, identificadas por `failed_stage`.
- **Commit:** identificado pelo assunto `feat(integracao): usar resposta real no INT-019`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-020`.

### INT-020 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `e9c282d`.
- **Arquivos modificados:** testes do cliente HTTP e da sessão do chat, além deste controle.
- **Resumo técnico:** o fluxo guarda o `session_id` devolvido pelo backend em `sessionStorage`; a request seguinte consulta esse valor e o reenvia no envelope tipado.
- **Testes:** `npm test -- --watch=false` → 7 arquivos/25 testes aprovados; sequência de duas perguntas compara os dois corpos HTTP; serviço de sessão cobre guardar, recuperar e limpar; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** a primeira request omite ID e a segunda envia exatamente `session_id: sessao-123` retornado pela primeira.
- **Riscos:** a sessão é intencionalmente limitada à aba/sessão do navegador e não representa persistência durável no servidor.
- **Commit:** identificado pelo assunto `test(integracao): validar sessao do chat no INT-020`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-021`.

### INT-021 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `9016059`.
- **Arquivos modificados:** componente/template/estilo/teste do chat, documentação do ciclo e este controle.
- **Resumo técnico:** a interface ganhou “Nova conversa”, que limpa `session_id`, mensagens, erro e rascunho, preservando deliberadamente o histórico visual de processos.
- **Testes:** `npm test -- --watch=false` → 7 arquivos/26 testes aprovados; cenário verifica limpeza sem escrita/remoção indevida do histórico; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** comportamento de refresh, fechamento da aba, nova conversa e histórico local foi documentado e testado; histórico não é tratado como sessão do servidor.
- **Riscos:** refresh na mesma aba mantém o ID em `sessionStorage`, mas o backend pode ter perdido seu estado; a documentação deixa explícita essa degradação.
- **Commit:** identificado pelo assunto `feat(integracao): definir ciclo da conversa no INT-021`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-022`.

### INT-022 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `335d344`.
- **Arquivos modificados:** componente/template/teste do chat e este controle.
- **Resumo técnico:** a assinatura HTTP ativa pode ser cancelada pela interface; envio concorrente permanece bloqueado, loading sempre finaliza, e nova tentativa limpa o erro anterior sem retry automático.
- **Testes:** `npm test -- --watch=false` → 7 arquivos/27 testes aprovados; cancelamento confirma unsubscribe e ignora resposta tardia; matriz existente cobre timeout, rede, 4xx e 5xx; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** nenhuma segunda request é criada durante loading e nenhuma resposta cancelada vira mensagem ou sessão.
- **Riscos:** cancelar no navegador não garante interromper computação já iniciada no servidor, conforme decisão de timeout.
- **Commit:** identificado pelo assunto `feat(integracao): controlar envio do chat no INT-022`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-023`.

### INT-023 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `4dd7da3`.
- **Arquivos modificados:** componente/teste do chat, revisão de dados sensíveis e este controle.
- **Resumo técnico:** respostas continuam em interpolação Angular segura e deixaram de ser parcialmente copiadas ao `localStorage`; o histórico registra apenas descrição genérica.
- **Testes:** `npm test -- --watch=false` → 7 arquivos/28 testes aprovados; payload com `<img onerror>` permanece texto, não cria elemento e seu marcador não chega ao storage; revisão por `rg` dos pontos de log; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** não há `innerHTML`/bypass no frontend nem logs de payload processual; logger do coletor usa somente estágio e classe da exceção.
- **Riscos:** o número do processo permanece no histórico por ser a função explícita desse recurso; usuários podem limpá-lo pelo serviço existente.
- **Commit:** identificado pelo assunto `fix(integracao): proteger dados do chat no INT-023`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-024`.

### INT-024 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `377a355`.
- **Arquivos modificados:** teste E2E offline, documentação do fluxo e este controle.
- **Resumo técnico:** processo de fixture é ingerido em SQLite temporário e consultado pelo endpoint ASGI real; contexto, análise, resposta, contrato e projeção Angular são exercitados sem consulta externa.
- **Testes:** suíte `test_p6_end_to_end_integration.py` → 8 aprovados; cenário local exige resposta não vazia contendo dado da fixture e falha imediatamente se o coletor for chamado; suíte Angular mais recente → 28 aprovados; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** pergunta → HTTP → orquestrador/agentes → repositório local → `resultado.resposta`; teste Angular correspondente confirma resposta no DOM.
- **Riscos:** intenção e RAG são doubles determinísticos para excluir Ollama/Qdrant; contexto, análise, resposta, repositório e FastAPI permanecem reais.
- **Commit:** identificado pelo assunto `test(integracao): validar chat offline no INT-024`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-025`.

### INT-025 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `4f4e50a`.
- **Arquivos modificados:** nove artefatos recentes do simulador, rota Angular, inventário comparativo e este controle.
- **Resumo técnico:** modelo, serviços, base/estado, cenários, gráficos, tabela, otimizador e shell foram transportados do snapshot mais recente para o `frontend/` canônico, mantendo o chat existente.
- **Testes:** `npm run build` aprovado; nove pares origem/destino comparados, divergindo somente pela quebra de linha final introduzida pelo transporte; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** inventário antes/depois cobre todas as capacidades pedidas e o compilador inclui a rota `/simulador` no bundle.
- **Riscos:** URLs e contratos importados ainda refletem o snapshot e serão adaptados/testados nos INT-026–028, sem mudança nas fórmulas do backend.
- **Commit:** identificado pelo assunto `feat(integracao): transportar UI do simulador no INT-025`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-026`.

### INT-026 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `47c29d5`.
- **Arquivos modificados:** modelo e cliente HTTP do simulador, além deste controle.
- **Resumo técnico:** base, simulação, comparação e otimizador possuem requests/responses tipadas e usam `/api/simulador/*`, compatível com o rewrite ao backend 8001; cada operação consome seu orçamento de timeout central.
- **Testes:** `npm run build` aprovado; compilação de produção validou todos os consumidores e contratos; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** não restam chamadas do serviço importado para `/api/base`, `/api/simular` ou `/api/otimizador`; todos os quatro endpoints reais estão representados.
- **Riscos:** validação de comportamento HTTP e respostas vazias/erradas pertence ao INT-027; componentes ainda mantêm a experiência importada.
- **Commit:** identificado pelo assunto `feat(integracao): adaptar API do simulador no INT-026`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-027`.

### INT-027 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `80ef5b3`.
- **Arquivos modificados:** cliente/teste HTTP do simulador e este controle.
- **Resumo técnico:** respostas de base são validadas antes do mapeamento; indisponibilidade, erro inesperado e payload 2xx inválido permanecem no canal de erro, enquanto lista vazia válida é preservada sem dados inventados.
- **Testes:** `npm test -- --watch=false` → 8 arquivos/33 testes aprovados; cinco novos cenários cobrem GET base, POST simular, vazio, rede e inválido; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** testes interceptam URL/verbo/corpo reais e verificam loading, mapeamento, erro visível e ausência de falso sucesso.
- **Riscos:** validação runtime detalhada de cada coluna numérica será reforçada no teste de contrato global do INT-038.
- **Commit:** identificado pelo assunto `test(integracao): cobrir API do simulador no INT-027`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-028`.

### INT-028 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `6afaa6e`.
- **Arquivos modificados:** testes do cliente do simulador, decisão de UI e este controle.
- **Resumo técnico:** `/comparar` e `/otimizador` têm chamadas Angular tipadas e cobertas; a UI continua sem acionar comparar e mantém otimizador desabilitado, como no snapshot mais recente.
- **Testes:** `npm test -- --watch=false` → 8 arquivos/35 testes aprovados; spies confirmam URL, POST, corpo e resposta dos dois endpoints; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** há cobertura automatizada do contrato e registro explícito da lacuna visual, sem apresentar funcionalidade pendente como pronta.
- **Riscos:** habilitação visual futura precisa de testes próprios de interação e não deve duplicar cálculos divergentes.
- **Commit:** identificado pelo assunto `test(integracao): cobrir comparar e otimizador no INT-028`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-029`.

### INT-029 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `99f15e0`.
- **Arquivos modificados:** raiz/template/estilo/teste Angular e este controle.
- **Resumo técnico:** o app canônico ganhou navegação persistente com links ativos para chat e simulador; em telas estreitas, a barra reorganiza links em grade sem alternar aplicações.
- **Testes:** `npm test -- --watch=false` → 8 arquivos/36 testes aprovados; `npm run build` aprovado; teste do shell confirma hrefs `/` e `/simulador`; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** ambos os recursos compartilham `App`, Router e bundle, acessíveis pela mesma navegação responsiva.
- **Riscos:** permanece aviso não bloqueante e preexistente de orçamento CSS do chat; o bundle está abaixo do limite total.
- **Commit:** identificado pelo assunto `feat(integracao): unificar navegacao no INT-029`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-030`.

### INT-030 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `f83d02e`.
- **Arquivos modificados:** fixture e teste de snapshot numérico, documentação e este controle.
- **Resumo técnico:** baseline de 86 registros fixa Meta 1 em 109,86 e Meta 2 em 161,71 com tolerância absoluta 0,01; cenário vazio precisa reproduzir integralmente a base.
- **Testes:** `python -m unittest discover -s tests -v` no simulador → 5 aprovados; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** resultados atuais equivalem ao baseline anterior documentado e a simulação neutra não altera registros ou métricas.
- **Riscos:** mudanças intencionais em dados ou regras exigirão revisão explícita da fixture e justificativa, em vez de atualização automática.
- **Commit:** identificado pelo assunto `test(integracao): fixar snapshot numerico no INT-030`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-031`.

### INT-031 — 2026-10-16
- **Estado anterior → novo:** `TODO` → `VALIDATED`.
- **Branch/commit antes:** `feat/integracao_robo_metas` / `f209304`.
- **Arquivos modificados:** especificação de casos de uso e este controle.
- **Resumo técnico:** foram separados consulta/pergunta processual, impacto individual por regras determinísticas e simulação/comparação/otimização agregada no motor real.
- **Testes/evidência:** matriz de seis categorias, seis regras de autorização e cinco casos proibidos revisada contra o roteamento existente; `git diff --check` aprovado antes do commit.
- **Evidência do aceite:** a especificação impede que perguntas processuais sejam desviadas e exige parâmetros explícitos para cenários CNJ.
- **Riscos:** a intenção atual baseada apenas na palavra “meta” é ampla; o INT-034 deverá restringir o roteamento conforme esta matriz.
- **Commit:** identificado pelo assunto `docs(integracao): definir casos de uso no INT-031`; o próprio commit que contém esta entrada é a evidência imutável.
- **Próximo item:** `INT-032`.

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
