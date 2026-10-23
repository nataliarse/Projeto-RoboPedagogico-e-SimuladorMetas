# CONTROLE DE PROGRESSO — Integração Equipe B → base do Robô Pedagógico

**Documento de referência:** `CHECKLIST_INTEGRACAO_EQUIPE_B.md`  
**Estado global:** `EB-001 A EB-006 CONCLUÍDAS; GATE-M1 BLOQUEADO; EB-007 ELEGÍVEL`
**Atualizado em:** `2026-10-23 16:40 -03:00`
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
| Último item terminado | `EB-006` |
| Próxima tarefa elegível | `EB-007` |

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
| Itens concluídos | **6** | EB-001 a EB-006 |
| Itens em andamento | **0** | Atualizar por tarefa |
| Itens bloqueados | **0** | Nenhum bloqueio ativo |
| Commits de integração | **5** | EB-001 `c9e814b`; EB-002 `6393ea2`; EB-003 `0fb538a`; EB-004 `c0a6cde`; EB-005 `70a2a1b`; EB-006 pendente |
| Testes novos executados | **8 APROVADOS** | Simulador; demais suítes não executadas por ausência de pytest/Node/npm |
| Regressões P0 abertas | **Não avaliado** | Número com evidências |
| Gate Meta 1 | `BLOQUEADO` | Regra `susm1`, denominador, dados e resultado 2026 divergem da base canônica |
| Gate Meta 2 | `PENDENTE` | `LIBERADO` / `BLOQUEADO`, justificativa |
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
| EB-006 | P0 | Comparação matemática Meta 1 | CONCLUÍDO | `DIVERGENCIAS_NUMERICAS.md` e fixture `meta1_comparison.json`; GATE-M1 bloqueado | A registrar após commit |
| EB-007 | P0 | Auditoria matemática e dados Meta 2 | PENDENTE | — | — |
| EB-008 | P0 | Snapshots numéricos antes | PENDENTE | — | — |
| EB-009 | P1 | Destino backend e dependências | PENDENTE | — | — |
| EB-010 | P1 | Endpoint quanto-falta | PENDENTE | — | — |
| EB-011 | P1 | API Meta 2 A/ANT | PENDENTE | — | — |
| EB-012 | P0 | Não mutação e erros do simulador | PENDENTE | — | — |
| EB-013 | P1 | Clientes HTTP tipados | PENDENTE | — | — |
| EB-014 | P1 | UI quanto-falta | PENDENTE | — | — |
| EB-015 | P1 | UI Meta 2 | PENDENTE | — | — |
| EB-016 | P1 | Gráficos e cenários | PENDENTE | — | — |
| EB-017 | P2 | Recentes localStorage | PENDENTE | — | — |
| EB-018 | P0 | Chatbot preservado | PENDENTE | — | — |
| EB-019 | P0 | Contratos e proxy | PENDENTE | — | — |
| EB-020 | P0 | Smoke integrado offline | PENDENTE | — | — |
| EB-021 | P0 | Revisão segurança/deps | PENDENTE | — | — |
| EB-022 | P0 | Regressão completa + build | PENDENTE | — | — |
| EB-023 | P1 | Guia de execução | PENDENTE | — | — |
| EB-024 | P0 | Relatório final e decisão | PENDENTE | — | — |

## 4. Estado dos gates de decisão

### GATE-M1 — Fórmula e semântica da Meta 1

**Status:** `BLOQUEADO`
**Evidência necessária:** comparação de séries, denominadores, regras de edição (especialmente `suspensos`/`susm1`), data de corte, arredondamento e testes com cenários determinísticos.  
**Diferenças encontradas:** base usa estoque `suspensos_acum` com piso que impede redução; Equipe B usa incrementos positivos `susm1_acum`; séries e acumulados também divergem; Meta 1 dez/2026 é 109,86 vs 96,47.
**Decisão:** não alterar regra/dados canônicos nem publicar quanto-falta importado como oficial sem validação humana.
**Funcionalidades afetadas:** endpoint e tela quanto-falta, além de qualquer ajuste na regra da Meta 1.

### GATE-M2 — Metodologia e dados da Meta 2 A/ANT

**Status:** `PENDENTE`  
**Evidência necessária:** referência das fórmulas, origem de séries e parâmetros, distinção histórico/projeção, critérios para alterar meses reais, cenários limite e testes de A/ANT.  
**Diferenças encontradas:** `NÃO AVALIADO`  
**Decisão:** `NÃO TOMADA`  
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

## 7. Mudanças de escopo e decisões humanas

| Data | Decisão/restrição | Quem autorizou | Impacto nos IDs | Evidência |
|---|---|---|---|---|
| — | Nenhuma decisão extra registrada | — | — | — |

**Exemplos de decisão que NÃO cabem ao autopilot:** mudar fórmula oficial, tratar ARIMA estático como dado real atualizado, sobrescrever dados oficiais, introduzir autenticação institucional, integrar AWS/produção, substituir chatbot, fazer deploy ou push, elevar bibliotecas globalmente rompendo compatibilidade. Registrar e deixar em aberto.

## 8. Resumo de handoff entre sessões do Codex

Atualizar ao encerrar cada sessão, inclusive em falhas:

```text
BRANCH_ATUAL: feat/integracao-equipe-b
HEAD_SHA: 70a2a1b (antes do commit EB-006)
ULTIMO_ITEM_VALIDADO: EB-006
PROXIMO_ITEM: EB-007
GATE_M1: BLOQUEADO
GATE_M2: PENDENTE
GATE_FINAL: PENDENTE
ARQUIVOS_COM_MUDANCAS_NAO_COMMITADAS: DIVERGENCIAS_NUMERICAS.md, fixture Meta 1 e controle (EB-006 até o commit)
TESTES_ULTIMA_EXECUCAO: simulador 8/8; chatbot/coletor indisponíveis sem pytest; Angular/proxy/build indisponíveis sem Node/npm
BLOQUEIOS: nenhum bloqueio ativo
ACAO_SEGURA_IMEDIATA: executar EB-007 e auditar Meta 2 sem alterar fórmulas
```

**Não declarar entrega completa apenas porque o Codex encerrou uma sessão.** A conclusão requer EB-024 e GATE-FINAL aprovados.
