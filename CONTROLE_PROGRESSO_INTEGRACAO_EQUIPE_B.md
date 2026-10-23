# CONTROLE DE PROGRESSO — Integração Equipe B → base do Robô Pedagógico

**Documento de referência:** `CHECKLIST_INTEGRACAO_EQUIPE_B.md`  
**Estado global:** `EB-001 CONCLUÍDA; EB-002 ELEGÍVEL`
**Atualizado em:** `2026-10-23 16:12 -03:00`
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
| Último item terminado | `EB-001` |
| Próxima tarefa elegível | `EB-002` |

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
| Itens concluídos | **1** | EB-001 |
| Itens em andamento | **0** | Atualizar por tarefa |
| Itens bloqueados | **0** | Nenhum bloqueio ativo |
| Commits de integração | **0** | SHAs no histórico abaixo |
| Testes novos executados | **NÃO EXECUTADOS** | Números/versões reais do trabalho atual |
| Regressões P0 abertas | **Não avaliado** | Número com evidências |
| Gate Meta 1 | `PENDENTE` | `LIBERADO` / `BLOQUEADO`, justificativa |
| Gate Meta 2 | `PENDENTE` | `LIBERADO` / `BLOQUEADO`, justificativa |
| Gate final | `PENDENTE` | `LIBERADO` / `BLOQUEADO`, justificativa |

**Baseline histórico de referência (22/10/2026, outro checkout/execução):** 157 testes chatbot + 2 subtestes, 26 coletor, 8 simulador, 38 Angular, 3 proxy = **232 testes + 2 subtestes**; build Angular aprovado. **Isto não é resultado do novo código recebido nem validação desta rodada.**

## 3. Quadro por item

| Item | Prioridade | Resumo | Estado | Evidência / artefato | Commit |
|---|---|---|---|---|---|
| EB-001 | P0 | Branch, baseline e rollback | CONCLUÍDO | Retomada: base limpa em `8b1a12e`; fonte ignorada em `integracao_entrada/TCC-Simulador-CNJ/`; destinos confirmados; branch `feat/integracao-equipe-b` criada | A registrar após commit |
| EB-002 | P0 | Auditoria de entrada e segredos | PENDENTE | — | — |
| EB-003 | P0 | Testes e contratos atuais | PENDENTE | — | — |
| EB-004 | P0 | ADR de arquitetura | PENDENTE | — | — |
| EB-005 | P0 | Matriz HTTP e proxy | PENDENTE | — | — |
| EB-006 | P0 | Comparação matemática Meta 1 | PENDENTE | — | — |
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

**Status:** `PENDENTE`  
**Evidência necessária:** comparação de séries, denominadores, regras de edição (especialmente `suspensos`/`susm1`), data de corte, arredondamento e testes com cenários determinísticos.  
**Diferenças encontradas:** `NÃO AVALIADO`  
**Decisão:** `NÃO TOMADA`  
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

## 7. Mudanças de escopo e decisões humanas

| Data | Decisão/restrição | Quem autorizou | Impacto nos IDs | Evidência |
|---|---|---|---|---|
| — | Nenhuma decisão extra registrada | — | — | — |

**Exemplos de decisão que NÃO cabem ao autopilot:** mudar fórmula oficial, tratar ARIMA estático como dado real atualizado, sobrescrever dados oficiais, introduzir autenticação institucional, integrar AWS/produção, substituir chatbot, fazer deploy ou push, elevar bibliotecas globalmente rompendo compatibilidade. Registrar e deixar em aberto.

## 8. Resumo de handoff entre sessões do Codex

Atualizar ao encerrar cada sessão, inclusive em falhas:

```text
BRANCH_ATUAL: feat/integracao-equipe-b
HEAD_SHA: 8b1a12e39a9618f770916bf94587669c4b827817 (antes do commit EB-001)
ULTIMO_ITEM_VALIDADO: EB-001
PROXIMO_ITEM: EB-002
GATE_M1: PENDENTE
GATE_M2: PENDENTE
GATE_FINAL: PENDENTE
ARQUIVOS_COM_MUDANCAS_NAO_COMMITADAS: CONTROLE_PROGRESSO_INTEGRACAO_EQUIPE_B.md (registro EB-001 até o commit)
TESTES_ULTIMA_EXECUCAO: NÃO EXECUTADOS
BLOQUEIOS: nenhum bloqueio ativo
ACAO_SEGURA_IMEDIATA: executar EB-002, auditando a fonte sem modificá-la
```

**Não declarar entrega completa apenas porque o Codex encerrou uma sessão.** A conclusão requer EB-024 e GATE-FINAL aprovados.
