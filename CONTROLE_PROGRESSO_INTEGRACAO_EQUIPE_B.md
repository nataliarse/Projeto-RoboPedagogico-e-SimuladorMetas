# CONTROLE DE PROGRESSO — Integração Equipe B → base do Robô Pedagógico

**Documento de referência:** `CHECKLIST_INTEGRACAO_EQUIPE_B.md`  
**Estado global:** `EB-001 A EB-018 CONCLUÍDAS; EB-019 ELEGÍVEL`
**Atualizado em:** `2026-10-23 16:45 -03:00`
**Responsável executor:** `Codex (execução supervisionável por registros)`  
**Regra:** este arquivo é o diário de execução. **Não antecipar resultados.**

## 1. Dados de execução (preencher na tarefa EB-001)

| Campo | Valor observado |
|---|---|
| Diretório do repositório | `C:/Users/filipe.duarte/Projeto-bolsa/Projeto-RoboPedagogico-e-SimuladorMetas` |
| Branch de origem integrada | `feat/integracao_robo_metas` (limpa e alinhada a `origin/feat/integracao_robo_metas`) |
| Branch de trabalho para Equipe B | `feat/integracao-equipe-b` |
| SHA de baseline | `8b1a12e39a9618f770916bf94587669c4b827817` |
| Estado inicial de `git status` | `LIMPO` em nova retomada; `integracao_entrada/` está ignorada por `.gitignore` e preservada somente para consulta |
| Caminho exato da fonte em `integracao_entrada/` | `integracao_entrada/TCC-Simulador-CNJ/` |
| Serviço canônico de simulação encontrado em | `simulador_metas_cnj/` |
| Versões efetivas Python / Node / npm | `Python 3.12.10`; Node e npm indisponíveis no PATH |
| Data/hora de início | `2026-10-23 15:53 -03:00` |
| Último item terminado | `EB-018 (CONCLUÍDO)` |
| Próxima tarefa elegível | `EB-019` |

### Regra de status

- `PENDENTE`: não executado.
- `EM ANDAMENTO`: execução iniciada, não validada.
- `CONCLUÍDO`: aceite demonstrado, teste/documentação/commit registrado.
- `BLOQUEADO`: depende de decisão, falta de dependência/ambiente, discrepância de regra ou risco não resolvido.
- `PARCIAL`: houve avanço, mas algum critério de aceite não foi cumprido; **não equivale a concluído**.
- `NÃO APLICÁVEL`: item analisado e tecnicamente dispensável, **com justificativa e evidência**.

## 2. Painel executivo

| Métrica | Valor inicial | Atualizar com evidência |
|---|---|---|
| Itens planejados | **24** | Conforme IDs EB-001 a EB-024 |
| Itens concluídos | **18** | EB-001 a EB-018 |
| Itens parciais | **0** | — |
| Itens em andamento | **0** | — |
| Itens bloqueados | **0** | Nenhum bloqueio matemático ativo; limitações ambientais permanecem |
| Commits de integração | **14** | Antes do commit EB-014; HEAD `db09f15` |
| Testes novos executados | **83 APROVADOS** | Angular 53, proxy 3 e simulador 27 nesta retomada |
| Regressões P0 abertas | **Não avaliado** | Número com evidências |
| Gate Meta 1 | `LIBERADO` | Responsável validou regras/séries da Equipe B como atualização em 23/10/2026 |
| Gate Meta 2 | `LIBERADO` | Responsável validou regras/séries da Equipe B como atualização em 23/10/2026; riscos seguem documentados |
| Gate final | `PENDENTE` | `LIBERADO` / `BLOQUEADO`, justificativa |

**Baseline histórico de referência (22/10/2026, outro checkout/execução):** 157 testes chatbot + 2 subtestes, 26 coletor, 8 simulador, 38 Angular, 3 proxy = **232 testes + 2 subtestes**; build Angular aprovado. **Isto não é resultado do novo código recebido nem validação desta rodada.**

## 3. Quadro por item

| Item | Prioridade | Resumo | Estado | Evidência / artefato | Commit |
|---|---|---|---|---|---|
| EB-001 | P0 | Branch, baseline e rollback | CONCLUÍDO | Retomada: base limpa em `8b1a12e`; fonte ignorada em `integracao_entrada/TCC-Simulador-CNJ/`; destinos confirmados; branch `feat/integracao-equipe-b` criada | `c9e814b` |
| EB-002 | P0 | Auditoria de entrada e segredos | CONCLUÍDO | `docs/integracao_equipe_b/INVENTARIO_ENTRADA.md`: 111 arquivos, 6.417.329 bytes, duplicatas, binários, builds, lockfiles e matriz de ação | `6393ea2` |
| EB-003 | P0 | Testes e contratos atuais | CONCLUÍDO | `docs/integracao_equipe_b/BASELINE_ATUAL.md`; simulador 8/8; rotas/proxy documentados; limitações de pytest e Node/npm registradas | `0fb538a` |
| EB-004 | P0 | ADR de arquitetura | CONCLUÍDO | `docs/integracao_equipe_b/ADR-001_PORTABILIDADE.md` | `c0a6cde` |
| EB-005 | P0 | Matriz HTTP e proxy | CONCLUÍDO | `docs/integracao_equipe_b/CONTRATOS_HTTP.md` | `70a2a1b` |
| EB-006 | P0 | Comparação matemática Meta 1 | CONCLUÍDO | `DIVERGENCIAS_NUMERICAS.md` e fixture `meta1_comparison.json`; GATE-M1 bloqueado | `b679b5b` |
| EB-007 | P0 | Auditoria matemática e dados Meta 2 | CONCLUÍDO | `AUDITORIA_META2.md`, fixture `meta2_audit.json`; GATE-M2 bloqueado | `1ecb0c4` |
| EB-008 | P0 | Snapshots numéricos antes | CONCLUÍDO | Fixture/teste adicional em `simulador_metas_cnj/tests`; 9/9 aprovados; baseline global não muta | `ea3e660` |
| EB-009 | P1 | Destino backend e dependências | CONCLUÍDO | `simulador_metas_cnj/services/` e `DESTINO_BACKEND.md`; antigos 9/9 | `96fe9cf` |
| EB-010 | P1 | Endpoint quanto-falta | CONCLUÍDO | Série/regra `susm1` integradas; `/api/meta1/quanto-falta`; snapshots V2; simulador 16/16 | `ffe364b` |
| EB-011 | P1 | API Meta 2 A/ANT | CONCLUÍDO | Serviço isolado e rotas `/api/meta2/base` e `/api/meta2/simular`; 23/23 testes | `061256a` |
| EB-012 | P0 | Não mutação e erros do simulador | CONCLUÍDO | Testes HTTP sequenciais, reload invariável, 422/500 sanitizado e JSON sem NaN; 27/27 | `069e49f` |
| EB-013 | P1 | Clientes HTTP tipados | CONCLUÍDO | Tipos, métodos, timeouts e testes 200/422/500/timeout/malformado; suíte Angular 47/47 após ajuste zoneless do teste | `db09f15` + validação no commit EB-014 |
| EB-014 | P1 | UI quanto-falta | CONCLUÍDO | Aba acessível no simulador, cálculo exclusivo no backend, criação de cenário e testes de UI; Angular 47/47, proxy 3/3, build aprovado | `46a1d82` |
| EB-015 | P1 | UI Meta 2 | CONCLUÍDO | A/ANT independentes, `null` preservado, histórico/projeção rotulados, comparação responsiva; Angular 49/49 e build aprovado | `dc9e300` |
| EB-016 | P1 | Gráficos e cenários | CONCLUÍDO | Gráfico canônico preservado; identificação, valores da API, nulos, acessibilidade e responsividade cobertos; Angular 51/51 | `b78f4e9` |
| EB-017 | P2 | Recentes localStorage | CONCLUÍDO | Histórico por meta, deduplicação, limite 3, restauro, limpeza e fallback sem storage; Angular 53/53 | `626d2cd` |
| EB-018 | P0 | Chatbot preservado | CONCLUÍDO | Sem mock/rota incompatível; `/api/processos/chat`, sessão, navegação e healthchecks preservados; Angular 53/53 e proxy 3/3 | A registrar após commit |
| EB-019 | P0 | Contratos e proxy | PENDENTE | — | — |
| EB-020 | P0 | Smoke integrado offline | PENDENTE | — | — |
| EB-021 | P0 | Revisão segurança/deps | PENDENTE | — | — |
| EB-022 | P0 | Regressão completa + build | PENDENTE | — | — |
| EB-023 | P1 | Guia de execução | PENDENTE | — | — |
| EB-024 | P0 | Relatório final e decisão | PENDENTE | — | — |

## 4. Estado dos gates de decisão

### GATE-M1 — Fórmula e semântica da Meta 1

**Status:** `LIBERADO`
**Evidência necessária:** comparação de séries, denominadores, regras de edição (especialmente `suspensos`/`susm1`), data de corte, arredondamento e testes com cenários determinísticos.  
**Diferenças encontradas:** base usa estoque `suspensos_acum` com piso que impede redução; Equipe B usa incrementos positivos `susm1_acum`; séries e acumulados também divergem; Meta 1 dez/2026 é 109,86 vs 96,47.
**Decisão:** responsável aprovou a atualização da Equipe B em 23/10/2026; regra/série integradas com baseline anterior preservada.
**Funcionalidades afetadas:** endpoint e tela quanto-falta, além de qualquer ajuste na regra da Meta 1.

### GATE-M2 — Metodologia e dados da Meta 2 A/ANT

**Status:** `LIBERADO`
**Evidência necessária:** referência das fórmulas, origem de séries e parâmetros, distinção histórico/projeção, critérios para alterar meses reais, cenários limite e testes de A/ANT.  
**Diferenças encontradas:** A/ANT usam coortes, D, base anterior, projeções e resultado 2025 fixos sem fonte reproduzível; edição de mês real é permitida; ANT é nulo na base e chega a 2200% com denominador 1.
**Decisão:** responsável aprovou a atualização da Equipe B em 23/10/2026; integração autorizada com rotulagem de histórico/projeção e riscos preservados.
**Funcionalidades afetadas:** endpoints e UI pública de Meta 2.

### GATE-FINAL — Não regressão, rastreabilidade e segurança

**Status:** `PENDENTE`  
**Evidência necessária:** chatbot preservado, `/api/processos/chat` funcional, endpoints simulador sem regressão, testes novos, proxy correto, build Angular, riscos registrados, commits e execução exclusivamente local.  
**Decisão:** `NÃO TOMADA`.

## 5. Baseline de testes — nova execução a preencher

| Suite | Comando (na pasta correta) | Resultado real | Quantidade | Ambiente | Log/arquivo |
|---|---|---|---|---|---|
| Chatbot processual | `python -m pytest tests -q -p no:cacheprovider` | NÃO EXECUTADO | — | — | — |
| Coletor | `python -m pytest tests -q -p no:cacheprovider` | NÃO EXECUTADO | — | — | — |
| Simulador | `python -m unittest discover -s tests -v` | NÃO EXECUTADO | — | — | — |
| Angular | `npm test -- --watch=false` | NÃO EXECUTADO | — | — | — |
| Proxy | `npm run test:proxy` | NÃO EXECUTADO | — | — | — |
| Build | `npm run build` | NÃO EXECUTADO | — | — | — |

Em novo ciclo, duplicar esta tabela sob o título **"Pós-integração"** e comparar caso a caso. Comandos podem ser adaptados ao setup real **após documentar o motivo**. Não desconsiderar falhas como se passassem.

## 6. Diário de execução — APPEND ONLY

> Para **cada EB**, acrescentar uma entrada ao final, sem apagar ocorrências anteriores. Ao retomar uma sessão, ler a última entrada e o painel de status. Depois atualizar a linha correspondente na tabela, as métricas e o próximo item elegível. Registrar **commits reais, não estimativas**.

### Modelo de entrada (copiar ao executar)

```markdown
### [AAAA-MM-DD HH:mm] EB-XXX — Título
- **Estado:** EM ANDAMENTO / CONCLUÍDO / PARCIAL / BLOQUEADO / NÃO APLICÁVEL
- **Objetivo:**
- **Arquivos lidos:**
- **Arquivos alterados (destino; não fonte):**
- **Decisão arquitetural / por quê:**
- **Comandos executados:**
  - `comando`: resultado (N passed / falhas / build / NÃO EXECUTADO + motivo)
- **Fixtures / teste de contrato / amostras numéricas:**
- **Git diff --check:** OK / FALHOU / NÃO EXECUTADO
- **Commit:** `<SHA>` / SEM COMMIT (justificativa)
- **Pendências ou riscos:**
- **Próximo item elegível:** EB-YYY / BLOQUEADO por GATE-...
```

### Registros iniciais

_Nenhuma tarefa executada. Ao começar, registrar EB-001 abaixo desta linha._

### [2026-10-23 15:53] EB-001 — Branch, baseline e rollback
- **Estado:** BLOQUEADO
- **Objetivo:** conferir branch, working tree, fonte importada, destinos canônicos e rollback antes de qualquer integração.
- **Arquivos lidos:** `AGENTS.md`, `CHECKLIST_INTEGRACAO_EQUIPE_B.md`, `CONTROLE_PROGRESSO_INTEGRACAO_EQUIPE_B.md` e metadados Git.
- **Arquivos alterados (destino; não fonte):** `CONTROLE_PROGRESSO_INTEGRACAO_EQUIPE_B.md` (somente este registro operacional).
- **Decisão arquitetural / por quê:** nenhuma alteração de código iniciada. A checklist exige interrupção diante de dirty tree alheia e a fonte declarada somente leitura já possui 14 arquivos rastreados modificados, além de novos arquivos. Há também dois documentos rastreados apagados. Preservar tudo sem reset, clean, stash ou commit.
- **Comandos executados:**
  - `git status --short --branch` / `git status --porcelain=v2`: branch `feat/integracao_robo_metas`; árvore suja.
  - `git show -s --format='%H %s' HEAD`: `ce3730fafc7b321602a85f18804bfcdcfe907f74 fix(frontend): corrigir textos e navegação do simulador`.
  - `git remote -v`: origin `https://github.com/nataliarse/Projeto-RoboPedagogico-e-SimuladorMetas.git`.
  - inspeção de caminhos: fonte localizada em `integracao_entrada/TCC-Simulador-CNJ/`; backend candidato canônico em `simulador_metas_cnj/`; destinos `frontend/`, `chatbot_processual_ai/` e `entrada-de-dados/` presentes.
  - `python --version`: Python 3.12.10; `node --version` e `npm --version`: comandos indisponíveis no PATH.
- **Fixtures / teste de contrato / amostras numéricas:** NÃO EXECUTADOS; EB-001 interrompida no preflight, antes de baseline funcional.
- **Git diff --check:** NÃO EXECUTADO sobre mudanças alheias; nenhum código foi alterado por esta execução.
- **Commit:** SEM COMMIT (critério de aceite não satisfeito; não misturar o registro com mudanças preexistentes).
- **Pendências ou riscos:** responsável deve identificar se as modificações/exclusões preexistentes são a entrega intencional e definir como preservá-las numa base verificável. Não é seguro criar branch/commit nem avançar para EB-002 enquanto a proveniência dessas mudanças estiver indefinida.
- **Próximo item elegível:** EB-001 após saneamento/autorização explícita sobre o working tree; nenhum item posterior é elegível porque EB-001 é precondição de isolamento.

### [2026-10-23 16:12] EB-001 — Retomada, branch, baseline e rollback
- **Estado:** CONCLUÍDO
- **Objetivo:** reconciliar o bloqueio anterior, confirmar uma base integrada limpa, localizar fonte e destinos e criar branch isolada.
- **Arquivos lidos:** `AGENTS.md`, `CHECKLIST_INTEGRACAO_EQUIPE_B.md`, `CONTROLE_PROGRESSO_INTEGRACAO_EQUIPE_B.md`, `.gitignore` (via `git check-ignore`) e estrutura da fonte/destinos.
- **Arquivos alterados (destino; não fonte):** `CONTROLE_PROGRESSO_INTEGRACAO_EQUIPE_B.md`.
- **Decisão arquitetural / por quê:** usar `feat/integracao_robo_metas` em `8b1a12e` como base verificável e criar `feat/integracao-equipe-b`; manter `integracao_entrada/` ignorada e somente leitura. Rollback é a reversão dos commits atômicos da branch, sem reescrever a base.
- **Comandos executados:**
  - `git status --short --branch` / `git status --porcelain=v2`: árvore limpa antes da criação da branch.
  - `git log -5 --oneline --decorate` e `git remote -v`: HEAD/base `8b1a12e39a9618f770916bf94587669c4b827817`, alinhado ao origin esperado.
  - `git check-ignore -v integracao_entrada ...`: fonte coberta por `.gitignore:119:/integracao_entrada/`.
  - `rg --files integracao_entrada`: fonte descoberta em `integracao_entrada/TCC-Simulador-CNJ/`.
  - `Test-Path` dos arquivos e destinos obrigatórios: `backend/main.py`, `backend/meta2_service.py`, app Angular importado, `simulador_metas_cnj/`, `frontend/src/app/`, `chatbot_processual_ai/` e `entrada-de-dados/` presentes.
  - `git switch -c feat/integracao-equipe-b`: branch de trabalho criada.
- **Fixtures / teste de contrato / amostras numéricas:** NÃO APLICÁVEL; item de descoberta sem mudança funcional.
- **Git diff --check:** OK após remoção de whitespace apontado na revisão pré-commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** a fonte contém planilhas/binários e duas árvores Angular; serão auditados na EB-002. Nenhum arquivo da fonte será versionado.
- **Próximo item elegível:** EB-002.

### [2026-10-23 16:15] EB-002 — Auditoria da entrada e segredos
- **Estado:** CONCLUÍDO
- **Objetivo:** inventariar a entrega importada, classificar o uso de cada grupo e verificar duplicatas, artefatos, dados e indicadores de segredo.
- **Arquivos lidos:** todos os caminhos da fonte por metadados/hash; símbolos/rotas de `backend/*.py`; dependências; serviços/componentes Angular; documentos da entrega; metadados de todas as planilhas.
- **Arquivos alterados (destino; não fonte):** `docs/integracao_equipe_b/INVENTARIO_ENTRADA.md` e este controle.
- **Decisão arquitetural / por quê:** portar apenas funcionalidades selecionadas; usar Python/Angular importados como referência; excluir chat mock, aplicação duplicada, configurações globais, builds, bytecode e dados sem proveniência.
- **Comandos executados:**
  - listagem/tamanhos/extensões: 111 arquivos, 6.417.329 bytes.
  - `Get-FileHash -Algorithm SHA256`: oito grupos de duplicatas documentados.
  - `rg -l` para padrões de segredo e inspeção de nomes sensíveis: nenhum candidato encontrado; conteúdo potencialmente sensível não foi impresso.
  - `rg` de símbolos, rotas, URLs, `responderMock`, `localStorage` e Chart: responsabilidades e exclusões confirmadas.
  - `openpyxl.load_workbook(..., read_only=True)`: nove planilhas inspecionadas somente por metadados/headers.
- **Fixtures / teste de contrato / amostras numéricas:** NÃO APLICÁVEL; auditoria estrutural, sem execução de regra matemática.
- **Git diff --check:** OK após remoção de linha em branco excedente apontada na revisão pré-commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** proveniência das planilhas e séries/projeções da Meta 2 será tratada na EB-007; fórmulas não foram validadas nesta tarefa.
- **Próximo item elegível:** EB-003.

### [2026-10-23 16:20] EB-003 — Baseline real e contratos atuais
- **Estado:** CONCLUÍDO
- **Objetivo:** executar as suítes disponíveis e documentar o backend canônico, rotas e proxy antes da integração funcional.
- **Arquivos lidos:** testes dos quatro componentes, `simulador_metas_cnj/main.py`, `chatbot_processual_ai/api.py`, `frontend/proxy.conf.json` e `frontend/package.json`.
- **Arquivos alterados (destino; não fonte):** `docs/integracao_equipe_b/BASELINE_ATUAL.md` e este controle.
- **Decisão arquitetural / por quê:** integrar as novas rotas no `simulador_metas_cnj/`; manter o proxy externo `/api/simulador/*` e as rotas/sessões do chatbot inalteradas.
- **Comandos executados:**
  - chatbot `python -m pytest tests -q -p no:cacheprovider`: NÃO EXECUTADO, `pytest` ausente (exit 1).
  - coletor `python -m pytest tests -q -p no:cacheprovider`: NÃO EXECUTADO, `pytest` ausente (exit 1).
  - simulador `python -m unittest discover -s tests -v`: 8 testes aprovados em 0,698 s.
  - Angular, proxy e build via npm: NÃO EXECUTADOS, Node/npm ausentes no PATH.
  - busca por ambientes locais: nenhum `pyvenv.cfg`/`python.exe` no workspace.
  - `rg` de rotas e leitura do proxy: contratos canônicos registrados no baseline.
- **Fixtures / teste de contrato / amostras numéricas:** snapshots numéricos existentes do simulador passaram; nenhuma fixture foi modificada.
- **Git diff --check:** OK após remoção de whitespace apontado na revisão pré-commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** cobertura integral não é comprovável no ambiente atual; a EB-022 deverá repetir todas as tentativas e manter o gate final honesto.
- **Próximo item elegível:** EB-004.

### [2026-10-23 16:25] EB-004 — ADR de portabilidade
- **Estado:** CONCLUÍDO
- **Objetivo:** decidir o destino arquitetural das funcionalidades novas com base nos componentes reais.
- **Arquivos lidos:** `docs/ARCHITECTURE.md`, `docs/development.md`, ADR/matrizes anteriores, requirements dos backends, proxy e estrutura do simulador.
- **Arquivos alterados (destino; não fonte):** `docs/integracao_equipe_b/ADR-001_PORTABILIDADE.md` e este controle.
- **Decisão arquitetural / por quê:** Angular canônico mantido; FastAPI separados; novos cálculos no simulador existente; namespace externo `/api/simulador/*`; chatbot e dados/fórmulas protegidos.
- **Comandos executados:** `rg --files`, leitura de imports/requirements e busca de referências arquiteturais.
- **Fixtures / teste de contrato / amostras numéricas:** NÃO APLICÁVEL; decisão documental, sem alteração funcional.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** gates matemáticos e indisponibilidade parcial do ambiente de testes permanecem explícitos.
- **Próximo item elegível:** EB-005.

### [2026-10-23 16:30] EB-005 — Matriz HTTP e proxy
- **Estado:** CONCLUÍDO
- **Objetivo:** comparar contratos antigos e novos, incluindo método, URLs, body, tipos, nulos, erros, timeout e healthchecks.
- **Arquivos lidos:** modelos/rotas FastAPI canônicos e importados, serviços Angular canônico/importados, proxy e timeouts.
- **Arquivos alterados (destino; não fonte):** `docs/integracao_equipe_b/CONTRATOS_HTTP.md` e este controle.
- **Decisão arquitetural / por quê:** manter namespace externo `/api/simulador`, rotas internas `/api`, response models e erros honestos; não copiar clientes sem timeout nem chat mock.
- **Comandos executados:** leitura segmentada de `main.py`, serviços Angular e proxy; comparação com contratos existentes.
- **Fixtures / teste de contrato / amostras numéricas:** NÃO APLICÁVEL; item documental sem alteração de runtime.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** schemas finais de quanto-falta e Meta 2 dependem das auditorias EB-006/EB-007.
- **Próximo item elegível:** EB-006.

### [2026-10-23 16:40] EB-006 — Comparação matemática da Meta 1
- **Estado:** CONCLUÍDO
- **Objetivo:** comparar fórmulas, dados, acumulados, datas, tipos, arredondamento e casos não calculáveis.
- **Arquivos lidos:** `main.py` canônico/importado, planilhas por carregamento normal e snapshot numérico canônico.
- **Arquivos alterados (destino; não fonte):** `DIVERGENCIAS_NUMERICAS.md`, `fixtures/meta1_comparison.json` e este controle.
- **Decisão arquitetural / por quê:** preservar integralmente a Meta 1 canônica; bloquear a promoção da regra importada devido a divergência material não autorizada.
- **Comandos executados:** execução isolada das duas implementações com quatro casos escalares e base de dezembro/2026.
- **Fixtures / teste de contrato / amostras numéricas:** caso divergente 83,3333 vs 111,1111; zero/nulo → `null` em ambas; base final 109,86 vs 96,47; fixture versionada com tolerância 0,01.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** GATE-M1 requer decisão humana sobre metodologia e proveniência de dados; endpoint/UI não podem ser apresentados como oficiais.
- **Próximo item elegível:** EB-007.

### [2026-10-23 16:50] EB-007 — Auditoria matemática e dados Meta 2
- **Estado:** CONCLUÍDO
- **Objetivo:** auditar fórmulas A/ANT, origem, janela, parâmetros, projeções, constantes e edição de meses reais.
- **Arquivos lidos:** `meta2_service.py`, `robo_cnj_meta2.py`, documentos importados e implementação canônica.
- **Arquivos alterados (destino; não fonte):** `AUDITORIA_META2.md`, `fixtures/meta2_audit.json`, `DIVERGENCIAS_NUMERICAS.md` e este controle.
- **Decisão arquitetural / por quê:** manter A/ANT isolada e oculta; bloquear promoção por ausência de proveniência/metodologia verificável.
- **Comandos executados:** execução offline de base, alteração em mês real/projetado, alterações simultâneas e denominadores não positivos.
- **Fixtures / teste de contrato / amostras numéricas:** A 104,63; ANT `null`; +10 julgados real/projetado → A 104,67; ANT com denominador 1 → 2200,00; denominador não positivo → `null`.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** validação humana obrigatória de coortes, D, séries, ARIMA, resultado 2025, temporalidade e limites.
- **Próximo item elegível:** EB-008.

### [2026-10-23 17:00] EB-008 — Snapshot numérico pré-integração
- **Estado:** CONCLUÍDO
- **Objetivo:** congelar cenários canônicos antes de integrar e provar não mutação da base global.
- **Arquivos lidos:** snapshot/testes existentes e resultados do motor canônico.
- **Arquivos alterados (destino; não fonte):** `simulador_metas_cnj/tests/fixtures/equipe_b_preintegration_snapshot.json`, `test_equipe_b_preintegration_baseline.py` e este controle.
- **Decisão arquitetural / por quê:** adicionar fixture separada sem modificar o snapshot protegido existente; tolerância de 0,01 para metas e igualdade exata da base global.
- **Comandos executados:** cálculo offline de três cenários; `python -m unittest discover -s tests -v`: 9 testes aprovados em 0,099 s.
- **Fixtures / teste de contrato / amostras numéricas:** base 109,86/161,71; +100 julgados out/2026 → 109,92/161,80; +100 suspensos → 109,86/161,71; `BASE_GLOBAL` invariável após cada cenário.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** snapshots A/ANT permanecem documentais e bloqueados pelo GATE-M2; não foram incorporados ao runtime.
- **Próximo item elegível:** EB-009.

### [2026-10-23 17:10] EB-009 — Destino backend e dependências
- **Estado:** CONCLUÍDO
- **Objetivo:** definir o módulo de destino no simulador existente e preservar isolamento de dependências/contratos.
- **Arquivos lidos:** estrutura, requirements e `main.py` dos backends; ADR e gates.
- **Arquivos alterados (destino; não fonte):** `simulador_metas_cnj/services/__init__.py`, `services/README.md`, `DESTINO_BACKEND.md` e este controle.
- **Decisão arquitetural / por quê:** serviços de domínio internos, sem FastAPI/Pydantic/rede, adaptados por `main.py`; nenhum terceiro serviço ou dependência nova.
- **Comandos executados:** `python -m unittest discover -s tests -v`: 9 testes aprovados (executar após criação dos módulos e antes do commit).
- **Fixtures / teste de contrato / amostras numéricas:** endpoints/snapshots antigos permanecem cobertos; nenhuma fórmula mudou.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** GATE-M1/M2 impedem ativação pública; EB-010/011 só podem preparar implementação isolada.
- **Próximo item elegível:** EB-010, limitado a preparação interna não exposta.

### [2026-10-23 17:15] EB-010 — Endpoint quanto-falta
- **Estado:** BLOQUEADO
- **Objetivo:** portar e ativar o endpoint de esforço mensal com testes de limites e coerência.
- **Arquivos lidos:** critério da EB-010, `DIVERGENCIAS_NUMERICAS.md`, fixture Meta 1, ADR e destino backend.
- **Arquivos alterados (destino; não fonte):** somente este checkpoint no controle.
- **Decisão arquitetural / por quê:** não implementar uma rota pública nem escolher silenciosamente entre a regra `susm1` importada e a regra canônica. O critério de aceite condiciona ativação ao GATE-M1, que está objetivamente bloqueado.
- **Comandos executados:** revisão dos resultados reproduzíveis da EB-006 e estado do gate; nenhuma fórmula executada novamente.
- **Fixtures / teste de contrato / amostras numéricas:** `meta1_comparison.json` demonstra a divergência; nenhum teste foi removido ou falsamente marcado como aprovado.
- **Git diff --check:** a executar antes do commit de checkpoint.
- **Commit:** checkpoint documental a registrar; nenhum commit funcional da EB-010.
- **Pendências ou riscos:** responsável metodológico deve escolher/validar regra, série e semântica de suspensões. Até lá, endpoint e UI quanto-falta permanecem ausentes.
- **Próximo item elegível:** NENHUM. EB-011 também depende do GATE-M2 bloqueado; EB-012 e fases seguintes dependem dos backends novos, e os testes obrigatórios de frontend estão indisponíveis sem Node/npm.

### [2026-10-23 17:45] EB-010 — Retomada e endpoint quanto-falta
- **Estado:** CONCLUÍDO
- **Objetivo:** integrar a atualização validada da Meta 1 e disponibilizar o cálculo de esforço mensal.
- **Arquivos lidos:** implementação importada, regras/séries auditadas, backend e testes canônicos.
- **Arquivos alterados (destino; não fonte):** `simulador_metas_cnj/main.py`, planilha validada em `dados/`, fixtures/testes V2, auditorias e este controle.
- **Decisão arquitetural / por quê:** atualizar a base canônica para a série única validada, usar `susm1`, preservar snapshots históricos em arquivos separados e expor a rota interna `/api/meta1/quanto-falta` (externa `/api/simulador/meta1/quanto-falta`).
- **Comandos executados:** hash SHA-256 origem/destino idêntico; `python -m unittest discover -s tests -v`: 16 testes aprovados em 2,040 s.
- **Fixtures / teste de contrato / amostras numéricas:** base atualizada 84 registros, Meta 1 96,47; alvo 100% exige +387/mês de mar a dez e resulta 100,01; alvo 90% já atingido; limites e não mutação cobertos.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** Meta 2 agregada antiga passa a refletir a nova série (169,68); EB-011 integrará A/ANT separadamente. Frontend ainda não testável sem Node/npm.
- **Próximo item elegível:** EB-011.

### [2026-10-23 18:10] EB-011 — API Meta 2 A/ANT
- **Estado:** CONCLUÍDO
- **Objetivo:** integrar suporte isolado aos grupos A/ANT sem alterar novamente a Meta 1.
- **Arquivos lidos:** serviço importado validado, auditoria/fixture Meta 2 e contratos canônicos.
- **Arquivos alterados (destino; não fonte):** `services/meta2_groups.py`, `main.py`, `tests/test_meta2_groups.py` e este controle.
- **Decisão arquitetural / por quê:** manter constantes/séries em serviço de domínio puro e usar `main.py` somente para validação/HTTP; rotas externas seguem `/api/simulador/meta2/*` pelo proxy.
- **Comandos executados:** `python -m unittest discover -s tests -v`: 23 testes aprovados em 2,122 s.
- **Fixtures / teste de contrato / amostras numéricas:** A base 104,63; ANT `null`; cenários vazios, reais, projetados, simultâneos, inválidos, denominadores não positivos e requests sequenciais cobertos.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** percentuais extremos de ANT permanecem possíveis e devem ser exibidos com a natureza projetada/experimental documentada.
- **Próximo item elegível:** EB-012.

### [2026-10-23 18:20] EB-012 — Isolamento de estado e erros HTTP
- **Estado:** CONCLUÍDO
- **Objetivo:** provar isolamento entre requests, invariância da base e erros/JSON honestos.
- **Arquivos lidos:** handlers FastAPI, helper ASGI e testes de contrato existentes.
- **Arquivos alterados (destino; não fonte):** `tests/test_state_isolation.py` e este controle.
- **Decisão arquitetural / por quê:** testar pela fronteira ASGI real, sem servidor/rede, incluindo dois cenários sequenciais e reload.
- **Comandos executados:** `python -m unittest discover -s tests -v`: 27 testes aprovados em 2,186 s.
- **Fixtures / teste de contrato / amostras numéricas:** base Meta 2 idêntica antes/depois; 422 estruturado; falha inesperada 500 sem detalhe privado; `json.dumps(..., allow_nan=False)` aprovado nas rotas novas/antigas.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** nenhuma regressão Python observada; suíte Angular ainda depende de Node/npm.
- **Próximo item elegível:** EB-013.

### [2026-10-23 18:35] EB-013 — Clientes Angular tipados
- **Estado:** PARCIAL
- **Objetivo:** criar clientes tipados para quanto-falta e Meta 2 sob `/api/simulador/*` com loading, erro, timeout, nulos e validação de payload.
- **Arquivos lidos:** modelos, serviço, timeouts e testes Angular canônicos.
- **Arquivos alterados (destino; não fonte):** `simulador.model.ts`, `http-timeouts.ts`, `simulador-api.service.ts`, spec correspondente e este controle.
- **Decisão arquitetural / por quê:** ampliar o serviço existente e reutilizar tratamento central; nenhum segundo cliente/global state.
- **Comandos executados:** leitura/revisão estática; `node --version` e `npm --version`: comandos indisponíveis.
- **Fixtures / teste de contrato / amostras numéricas:** specs escritas para 200, 422, 500, timeout e resposta malformada; NÃO EXECUTADAS por ausência do runtime.
- **Git diff --check:** a executar antes do commit deste item.
- **Commit:** a registrar após commit atômico de implementação parcial.
- **Pendências ou riscos:** TypeScript/build ainda não comprovados; EB-019/022 deverão executar a suíte quando Node/npm estiver disponível.
- **Próximo item elegível:** EB-014, com mesma limitação ambiental para validação.

### [2026-10-23 16:45] EB-014 — UI quanto-falta
- **Estado:** CONCLUÍDO
- **Objetivo:** integrar a calculadora de esforço mensal da Meta 1 à navegação do simulador canônico.
- **Arquivos lidos:** componente importado, shell do simulador, serviços/modelos canônicos, testes e configuração Angular.
- **Arquivos alterados (destino; não fonte):** `features/quanto-falta/quanto-falta.component.ts`, spec correspondente, shell, tipo da aba, spec do cliente HTTP e este controle.
- **Decisão arquitetural / por quê:** adicionar aba interna ao shell existente; delegar todo cálculo ao endpoint da EB-010; reutilizar cenários e API canônicos, sem copiar roteamento, proxy ou estado global importados.
- **Comandos executados:**
  - suíte Angular com Node local: primeira tentativa compilou, mas revelou `fakeAsync` incompatível com o setup zoneless; após troca por timers Vitest, 10 arquivos e 47 testes aprovados.
  - build Angular: aprovado; warning preexistente de orçamento do CSS do chat (5,85 kB para limite de 4,00 kB).
  - proxy Node: 3 testes aprovados.
  - `python -m unittest discover -s tests -v`: 27 testes do simulador aprovados em 2,122 s.
- **Fixtures / teste de contrato / amostras numéricas:** fluxo testa primeiro mês projetado, alvo inválido, falha HTTP e criação de cenário com +387 julgamentos em dois meses; cálculo não é reimplementado no navegador.
- **Git diff --check:** OK; somente avisos esperados de normalização LF/CRLF.
- **Commit:** `46a1d82`.
- **Pendências ou riscos:** warning de orçamento CSS do chat não foi introduzido pela tarefa; não foi alterado por estar fora do escopo.
- **Próximo item elegível:** EB-015.

### [2026-10-23 16:47] EB-015 — UI Meta 2 A/ANT
- **Estado:** CONCLUÍDO
- **Objetivo:** integrar a simulação Meta 2-A/ANT com distinção clara entre histórico e projeção.
- **Arquivos lidos:** componente e serviço importados, cliente/modelos canônicos e serviço de domínio Meta 2.
- **Arquivos alterados (destino; não fonte):** `features/meta2/meta2.component.ts`, spec correspondente, shell do simulador e este controle.
- **Decisão arquitetural / por quê:** usar exclusivamente `SimuladorApiService`; manter formulários A/ANT independentes e comparação local de respostas completas, sem copiar serviço, roteamento, gráfico ou persistência importados.
- **Comandos executados:** suíte Angular: 11 arquivos e 49 testes aprovados; build Angular aprovado com warning CSS preexistente; simulador Python 27/27 em 2,010 s.
- **Fixtures / teste de contrato / amostras numéricas:** A 104,63%; ANT `null` exibido como “—”; teste envia +10 julgados em A e +2 suspensos em ANT sem cruzar estados; linhas reais e previstas aparecem como Histórico/Projeção.
- **Git diff --check:** a executar antes do commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** as projeções permanecem estáticas e explicitamente rotuladas como protótipo; gráfico comparativo pertence à EB-016.
- **Próximo item elegível:** EB-016.

### [2026-10-23 16:48] EB-016 — Gráficos e cenários
- **Estado:** CONCLUÍDO
- **Objetivo:** validar e aprimorar a comparação gráfica sem substituir o componente canônico.
- **Arquivos lidos:** gráfico/cenários canônicos e gráfico SVG importado.
- **Arquivos alterados (destino; não fonte):** `graficos.component.ts`, spec correspondente e este controle.
- **Decisão arquitetural / por quê:** preservar o gráfico canônico já integrado e seu fallback; adicionar semântica acessível e testes que provam identificação dos cenários e uso dos valores retornados pela API, sem duplicar fórmulas.
- **Comandos executados:** suíte Angular: 12 arquivos e 51 testes aprovados.
- **Fixtures / teste de contrato / amostras numéricas:** Base 96,47%, cenário 100,01% e `null` cobertos; barras limitadas e fallback textual preservado.
- **Git diff --check:** a executar antes do commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** renderização Chart.js mantém fallback quando o script não está disponível; nenhuma dependência foi adicionada.
- **Próximo item elegível:** EB-017.

### [2026-10-23 16:49] EB-017 — Cenários recentes
- **Estado:** CONCLUÍDO
- **Objetivo:** guardar até três cenários recentes por meta sem dados processuais pessoais.
- **Arquivos lidos:** abstração localStorage canônica, serviço importado e componentes de cenários.
- **Arquivos alterados (destino; não fonte):** `cenarios-recentes.service.ts`, spec, componentes Meta 1/Meta 2 e este controle.
- **Decisão arquitetural / por quê:** serviço isolado com chaves por meta; persistir somente nome, grupo e incrementos, sempre recalculando resultados pela API ao simular.
- **Comandos executados:** suíte Angular: 13 arquivos e 53 testes aprovados.
- **Fixtures / teste de contrato / amostras numéricas:** deduplicação por alterações/grupo, limite 3, remoção de zeros, restauro, limpeza e exceção de storage cobertos.
- **Git diff --check:** a executar antes do commit.
- **Commit:** a registrar após commit atômico.
- **Pendências ou riscos:** localStorage é opcional; falha de gravação não impede simulação.
- **Próximo item elegível:** EB-018.

### [2026-10-23 16:50] EB-018 — Preservação do chatbot
- **Estado:** CONCLUÍDO
- **Objetivo:** comprovar preservação do Angular canônico e chatbot real.
- **Arquivos lidos:** cliente/componentes/testes do chat, sessão, rotas, proxy e healthchecks.
- **Arquivos alterados (destino; não fonte):** somente este controle.
- **Decisão arquitetural / por quê:** nenhuma alteração no chatbot; manter endpoint e sessão existentes.
- **Comandos executados:** `rg` confirmou ausência de `responderMock` e `/api/chat`; suíte Angular 53/53 e proxy 3/3 aprovados; pytest chatbot NÃO EXECUTADO (módulo ausente).
- **Fixtures / teste de contrato / amostras numéricas:** testes Angular cobrem POST `/api/processos/chat`, `session_id`, erro e navegação.
- **Git diff --check:** OK.
- **Commit:** a registrar após commit documental.
- **Pendências ou riscos:** suíte Python do chatbot permanece pendente por ausência do pytest.
- **Próximo item elegível:** EB-019.

## 7. Mudanças de escopo e decisões humanas

| Data | Decisão/restrição | Quem autorizou | Impacto nos IDs | Evidência |
|---|---|---|---|---|
| 2026-10-23 | Regras e séries M1/M2 da Equipe B validadas como atualização e autorizadas para integração | Responsável do projeto (usuário) | EB-010 em diante; GATE-M1/M2 liberados | Confirmação explícita nesta sessão |

**Exemplos de decisão que NÃO cabem ao autopilot:** mudar fórmula oficial, tratar ARIMA estático como dado real atualizado, sobrescrever dados oficiais, introduzir autenticação institucional, integrar AWS/produção, substituir chatbot, fazer deploy ou push, elevar bibliotecas globalmente rompendo compatibilidade. Registrar e deixar em aberto.

## 8. Resumo de handoff entre sessões do Codex

Atualizar ao encerrar cada sessão, inclusive em falhas:

```text
BRANCH_ATUAL: feat/integracao-equipe-b
HEAD_SHA: 626d2cd (antes do commit EB-018)
ULTIMO_ITEM_VALIDADO: EB-018
PROXIMO_ITEM: EB-019
GATE_M1: LIBERADO
GATE_M2: LIBERADO
GATE_FINAL: PENDENTE
ARQUIVOS_COM_MUDANCAS_NAO_COMMITADAS: checkpoint documental EB-018
TESTES_ULTIMA_EXECUCAO: Angular 53/53; simulador 27/27; build aprovado com warning CSS preexistente
BLOQUEIOS: pytest ainda precisa ser verificado para chatbot/coletor; gates matemáticos liberados
ACAO_SEGURA_IMEDIATA: executar EB-019
```

**Não declarar entrega completa apenas porque o Codex encerrou uma sessão.** A conclusão requer EB-024 e GATE-FINAL aprovados.
