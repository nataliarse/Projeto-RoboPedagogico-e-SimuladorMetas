# Checklist de Integração — Chatbot Processual + Coleta TRT18

> **Artefato operacional temporário da branch de integração.**
> Este arquivo orienta o trabalho do Codex, não integra a documentação do produto
> e deve ser removido antes de a entrega chegar à `main`.

**Branch-alvo:** `feat/integra_chatbot_coleta_etl`
**Data do baseline documental:** 01/09/2026
**Escopo:** integrar `chatbot_processual_ai/` a `entrada-de-dados/` por uma
fronteira Python explícita, preservando o frontend e as responsabilidades dos
dois módulos.
**Unidade de execução:** um ID por prompt.
**Unidade de validação:** cada ID individualmente.
**Unidade de commit:** uma fase completa; nunca um commit por ID.

---

## 0. Resultado esperado

Ao final desta checklist, o fluxo deve ser:

```text
usuário solicita um processo
        ↓
chatbot consulta o SQLite
        ↓
processo local? ── sim ──→ fluxo atual do chatbot
        │
        não
        ↓
collector_adapter chama entrada-de-dados
        ↓
coleta TRT18 + CAPTCHA + normalização
        ↓
resultado classificado de forma explícita
        ↓
sucesso válido → ingestão transacional no SQLite
        ↓
chatbot usa exatamente seu fluxo atual
        ↓
nova pergunta/restart reutiliza o dado persistido
```

O resultado global exige:

- consulta local como primeira fonte;
- coleta real somente quando o processo não estiver disponível localmente;
- `collector_adapter` como única fronteira do chatbot com o coletor;
- nenhuma lógica de Playwright, CAPTCHA ou normalização reimplementada no chatbot;
- somente resultado coletado considerado válido sendo persistido;
- `NAO_ENCONTRADO` distinguido de `PARCIAL`, `BLOQUEADO`, `FALHA` e erro técnico;
- falha de coleta sem falso `not_found` e sem quebra não controlada da API;
- persistência no SQLite sobrevivendo ao reinício do backend;
- segunda consulta sem recoleta desnecessária;
- frontend sem alteração funcional;
- dependências, configuração e documentação com fontes de verdade claras;
- testes offline reproduzíveis e pelo menos um aceite real controlado;
- artefatos operacionais da branch ausentes da projeção final para `main`.

---

## 1. Baseline factual disponível

### Chatbot processual

- `chatbot_processual_ai/collector_adapter.py` existe, mas apenas delega a
  `services.process_repository.find_process_by_number()`.
- `Agent 2`, em `agents/agent2_context_collection.py`, consulta o adapter e hoje
  interpreta retorno `None` como `not_found` local.
- `services/process_repository.py` já oferece:
  - lookup por número normalizado;
  - ingestão transacional por `ingest_processes()`;
  - persistência de processo, partes, movimentações, documentos, pendências,
    metadados de coleta e chunks;
  - reconstituição da árvore processual a partir do SQLite.
- A ingestão atual remove `documento` das partes e `id_documento` dos documentos
  antes de persistir, como medida de sanitização existente a ser preservada.
- O fluxo estruturado e o RAG já consomem a árvore processual carregada do
  repositório local.

### Entrada de dados

- `entrada-de-dados/servico.py` expõe `obter_processo(numero, ...)` como
  fronteira pública pretendida.
- O serviço usa cache bruto aproveitável antes de abrir coleta real.
- A coleta real fica encapsulada em `coletor_trt18.py` e usa Playwright,
  CAPTCHA e interceptação das APIs do PJe.
- `normalizador.py` converte o bruto para o modelo Pydantic de `modelos.py`.
- A árvore produzida contém `processo`, `partes_interessadas`,
  `movimentacoes`, `documentos`, `pendencias` e `coleta`.
- `coleta.status_coleta` possui os estados `SUCESSO`, `PARCIAL`, `FALHA`,
  `NAO_ENCONTRADO` e `BLOQUEADO`.
- O diretório usa hífen no nome e seus imports internos foram escritos para
  execução a partir do próprio módulo; a estratégia de importação pelo backend
  precisa ser comprovada, não presumida.

### Baseline estrutural já implementado, ainda sem checkpoint confirmado

- `entrada-de-dados/` foi incorporado ao worktree de integração.
- O README do coletor foi consolidado no `README.md` principal.
- As dependências do coletor foram incorporadas ao
  `chatbot_processual_ai/requirements.txt`.
- Os antigos `entrada-de-dados/README.md` e
  `entrada-de-dados/requirements.txt` foram removidos na consolidação relatada.
- A documentação técnica do fluxo de entrada de dados foi iniciada em `docs/`.
- As alterações ainda precisam ser confrontadas com a nova branch e fechadas
  como baseline reproduzível da Fase P0.

### Governança temporária

- `AGENTS.md` governa diagnóstico, escopo, testes, checklist, revisão e relato.
- `.codex/rules/safety.rules` governa comandos persistentes ou destrutivos.
- Esta checklist, o controle de progresso, `AGENTS.md` e `safety.rules` são
  ferramentas exclusivas da branch e não pertencem ao produto final.

---

## 2. Escopo positivo

- estabelecer o contrato entre a árvore produzida e a árvore consumida;
- tornar `entrada-de-dados` consumível por uma fronteira Python estável;
- estender o adapter para lookup local, aquisição remota e classificação;
- ingerir no SQLite apenas árvores válidas e sanitizadas;
- traduzir os estados do coletor sem esconder falhas;
- preservar o comportamento atual para processos já locais;
- tornar dependências e configuração reproduzíveis;
- resolver somente duplicações causadas ou bloqueantes para a integração;
- testar caminhos local, remoto, persistido e degradado;
- atualizar a documentação real do produto após o comportamento funcionar.

## 3. Escopo negativo

Não faz parte desta integração, salvo dependência técnica comprovada e registrada:

- alterar o frontend ou seu contrato HTTP;
- redesenhar o chatbot, agentes, RAG, Ollama ou Qdrant;
- reescrever o coletor, CAPTCHA ou normalizador dentro do chatbot;
- migrar SQLite para outro banco;
- introduzir fila, worker distribuído, scheduler ou serviço HTTP separado;
- paralelizar a coleta em lote;
- corrigir heurísticas antigas do coletor sem relação com a integração;
- refatorar duplicações preexistentes que não interfiram no fluxo integrado;
- adicionar autenticação, deploy ou infraestrutura de produção;
- versionar dados processuais reais, caches, screenshots, HTMLs de diagnóstico,
  bancos de runtime, `.env`, browsers, `.venv` ou dependências instaladas;
- transformar planejamento ou documentação em afirmação de comportamento já
  implementado.

---

## 4. Convenção de status

Use apenas:

- `TODO` — ainda não iniciado;
- `READY` — diagnóstico e precondições permitem iniciar;
- `IN_PROGRESS` — investigação ou implementação iniciada;
- `BLOCKED` — impedimento objetivo impede continuar com segurança;
- `IMPLEMENTED` — alteração concluída, mas ainda existe validação pendente;
- `VALIDATED` — critério de aceite, testes e diff foram confirmados;
- `REJECTED` — solução executada foi considerada inadequada;
- `SUPERSEDED` — item foi formalmente substituído por outro ID.

Um item não vira `VALIDATED` apenas porque o código foi escrito. Um item
incidentalmente afetado permanece no status anterior até validação explícita.

---

## 5. Protocolo de fechamento de fase

Cada fase recebe exatamente um checkpoint Git planejado. O fechamento somente
pode ocorrer quando:

1. todos os IDs da fase estiverem `VALIDATED` ou possuírem exceção formalmente
   aceita;
2. testes focados e regressão exigida pela fase tiverem sido executados;
3. o diff acumulado da fase tiver sido revisado;
4. `git diff --check` estiver aprovado;
5. não houver segredo, dado processual real, debug ou alteração fora do escopo;
6. o controle de progresso contiver as evidências de cada ID;
7. o usuário autorizar explicitamente o commit.

O commit de fase deve cobrir todos os IDs daquela fase. Nenhum ID isolado
autoriza `git commit`, `git push` ou avanço automático para a fase seguinte.

---

# FASE P0 — Congelar a baseline estrutural

## INT-COL-P0-001 — Confirmar branch e preservar o worktree

**Status:** `VALIDATED`
**Prioridade:** bloqueante

### Objetivo

Garantir que a integração comece na nova branch e que as alterações já
existentes sejam reconhecidas antes de qualquer edição adicional.

### Ações

- [x] Confirmar a branch com `git branch --show-current`.
- [x] Registrar `git status --short` e a base de comparação com `main`.
- [x] Separar mudanças preexistentes, arquivos não rastreados e artefatos
  operacionais.
- [x] Não restaurar, limpar, mover ou sobrescrever mudanças automaticamente.

### Critério de aceite

- branch correta registrada;
- worktree inicial inventariado;
- nenhuma alteração preexistente perdida ou atribuída silenciosamente à integração.

## INT-COL-P0-002 — Auditar o módulo transportado e os artefatos protegidos

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P0-001`

### Objetivo

Confirmar o conteúdo real de `entrada-de-dados/` e impedir que cache, dados,
binários ou evidências locais entrem no histórico por acidente.

### Ações

- [x] Inventariar arquivos rastreados e não rastreados do módulo.
- [x] Confirmar código-fonte, exemplos sanitizados e planilha de entrada
  intencionalmente autorizada.
- [x] Auditar `data/brutos`, `data/saida`, `data/debug`, screenshots, HTMLs,
  bancos, `__pycache__`, `.ipynb_checkpoints` e browsers instalados.
- [x] Validar os `.gitignore` sem executar limpeza destrutiva.

### Critério de aceite

- somente artefatos intencionais aparecem na projeção da fase;
- dados reais/cache/runtime permanecem fora do Git;
- baselines e exemplos protegidos não foram modificados.

## INT-COL-P0-003 — Validar a consolidação documental e de dependências

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P0-001`

### Objetivo

Confirmar a centralização já executada sem confundir presença de dependências
com bootstrap reproduzível.

### Ações

- [x] Confirmar o `README.md` raiz como entrada documental principal.
- [x] Confirmar `chatbot_processual_ai/requirements.txt` como manifesto Python
  consolidado atual.
- [x] Verificar que os antigos README e requirements do coletor não concorrem
  como fontes de verdade.
- [x] Conferir links, caminhos, nomes de diretório e todas as dependências
  declaradas pelo coletor.
- [x] Registrar que instalação limpa e browsers do Playwright serão validados
  na Fase P5.

### Critério de aceite

- não existem fontes de verdade concorrentes para setup e dependências;
- nenhum conteúdo necessário do coletor foi perdido;
- o status não afirma ainda que um `.venv` limpo foi aprovado.

## INT-COL-P0-004 — Registrar baseline técnico reproduzível

**Status:** `VALIDATED`
**Dependências:** `INT-COL-P0-002`, `INT-COL-P0-003`

### Objetivo

Medir o estado anterior à integração funcional para distinguir regressões de
falhas preexistentes ou ambientais.

### Ações

- [x] Executar a suíte atual do chatbot no diretório documentado.
- [x] Executar normalização offline do exemplo sanitizado do coletor.
- [x] Validar número CNJ e cache sem abrir navegador.
- [x] Registrar comandos, versões, resultados, skips e limitações ambientais.
- [x] Registrar hashes ou evidências dos exemplos protegidos quando necessário.

### Critério de aceite

- baseline do chatbot e do coletor registrada com resultados reais;
- nenhuma coleta externa ocorreu sem autorização;
- falhas preexistentes estão separadas de regressões futuras.

### Fechamento P0

**Commit planejado:** `C00`
**Mensagem sugerida:** `chore(integration): establish chatbot collector baseline`

---

# FASE P1 — Congelar contratos e decisões arquiteturais

## INT-COL-P1-001 — Mapear o contrato produtor do coletor

**Status:** `VALIDATED`
**Dependência:** P0 fechada

### Objetivo

Comprovar o que `servico.obter_processo()` retorna, grava e pode lançar.

### Ações

- [x] Mapear parâmetros, defaults, side effects e importações tardias.
- [x] Mapear a árvore Pydantic completa e nulabilidade dos campos.
- [x] Mapear cache aproveitável, coleta real e arquivos produzidos.
- [x] Mapear `ValueError`, `FileNotFoundError`, falhas técnicas e os cinco
  valores de `status_coleta`.
- [x] Identificar estados em que existe um `dict` válido estruturalmente, mas
  que não representa sucesso persistível.

### Critério de aceite

- contrato produtor e seus efeitos colaterais estão documentados com evidência
  de código/teste;
- ausência de dado, processo inexistente e falha técnica não são confundidas.

## INT-COL-P1-002 — Mapear o contrato consumidor do chatbot

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P1-001`

### Objetivo

Comprovar o formato que repositório, chunking, Agent 2, roteador e resposta
esperam receber.

### Ações

- [x] Mapear `find_process_by_number()` e `ingest_processes()`.
- [x] Mapear sanitização, campos persistidos, campos descartados e round-trip.
- [x] Mapear como `None`, exceções e `collection_status` afetam o Agent 2.
- [x] Mapear consumidores estruturados e RAG da árvore carregada.
- [x] Identificar divergências como `data_distribuicao`, `documento` de parte e
  `id_documento`, sem alterar regras ainda.

### Critério de aceite

- contrato consumidor e consumidores indiretos estão comprovados;
- perdas intencionais e incompatibilidades reais estão separadas.

## INT-COL-P1-003 — Definir contrato mínimo do `collector_adapter`

**Status:** `VALIDATED`
**Dependências:** `INT-COL-P1-001`, `INT-COL-P1-002`

### Objetivo

Escolher uma fronteira explícita que preserve os dois módulos e não converta
falha em sucesso aparente.

### Ações

- [x] Definir resultado tipado ou estrutura equivalente para lookup/aquisição.
- [x] Congelar a matriz `LOCAL_HIT`, `COLLECTED`, `NOT_FOUND`, `PARTIAL`,
  `BLOCKED`, `FAILED` e `INVALID_NUMBER`, com nomes finais comprovados no código.
- [x] Definir quais estados podem ser ingeridos e quais nunca podem virar
  `not_found`.
- [x] Definir exceções controladas, mensagens públicas e detalhes apenas internos.
- [x] Preservar uma fronteira testável por injeção/fake, sem rede em testes unitários.

### Critério de aceite

- cada estado possui semântica, persistibilidade e comportamento do chamador;
- `None` não é usado para representar falha técnica;
- o contrato não expõe Playwright/CAPTCHA ao Agent 2.

## INT-COL-P1-004 — Definir importação, ownership e política de dados

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P1-003`

### Objetivo

Definir como o backend consumirá o módulo com hífen sem criar dependência de
diretório atual, `PYTHONPATH` manual ou path absoluto de máquina.

### Ações

- [x] Comparar a menor adaptação de package/import com alternativas mais
  invasivas e registrar a decisão.
- [x] Manter `entrada-de-dados` como dono de coleta, CAPTCHA e normalização.
- [x] Manter chatbot como dono de lookup local, persistência consumidora e conversa.
- [x] Preservar sanitização de CPF/CNPJ e IDs internos já aplicada na ingestão.
- [x] Definir limites de log e proibir payload bruto/dado pessoal desnecessário.

### Critério de aceite

- importação escolhida funciona a partir do bootstrap oficial do backend;
- não há `sys.path`/path absoluto improvisado sem justificativa e teste;
- ownership e política de dados estão explícitos.

**Evidência operacional:** decisão implementável, matrizes, probes offline e
invariantes estão registradas no controle de progresso. P1-001..004 estão
`VALIDATED`; a P1 está pronta para revisão manual e fechamento pelo usuário,
sem início da P2 e sem commit C01.

### Fechamento P1

**Commit planejado:** `C01`
**Mensagem sugerida:** `docs(integration): define chatbot collector contracts`

---

# FASE P2 — Implementar a fronteira Python

## INT-COL-P2-001 — Tornar o coletor importável pelo backend

**Status:** `VALIDATED`
**Dependência:** P1 fechada

### Objetivo

Aplicar somente a estratégia de importação aprovada, preservando execução CLI,
notebook e responsabilidades existentes do coletor.

### Ações

- [x] Implementar package/import sem depender da máquina do desenvolvedor.
- [x] Atualizar imports internos estritamente necessários.
- [x] Confirmar import leve: Playwright/CAPTCHA continuam carregados sob demanda.
- [x] Preservar as entradas públicas atuais do coletor quando possível.

### Critério de aceite

- backend importa a fronteira em ambiente limpo e no diretório oficial;
- CLI/cache do coletor continuam utilizáveis;
- nenhuma coleta externa ocorre durante import.

## INT-COL-P2-002 — Implementar o contrato do adapter

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P2-001`

### Objetivo

Transformar `collector_adapter.py` em fronteira única, explícita e isolável.

### Ações

- [x] Preservar lookup local existente.
- [x] Encapsular chamada a `obter_processo()` e tradução do resultado.
- [x] Permitir fake/injeção em testes sem abrir navegador.
- [x] Não persistir nem alterar o Agent 2 antes das fases autorizadas.
- [x] Não duplicar validação CNJ, coleta, CAPTCHA ou normalização.

### Critério de aceite

- adapter representa todos os estados aprovados em P1;
- resultado local continua compatível;
- dependências pesadas e efeitos externos não vazam para import/teste.

## INT-COL-P2-003 — Cobrir a fronteira com testes offline

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P2-002`

### Objetivo

Fixar o contrato do adapter antes de ligá-lo ao fluxo conversacional.

### Ações

- [x] Testar hit local e ausência local.
- [x] Testar sucesso, não encontrado, parcial, bloqueio, falha e exceção do coletor.
- [x] Provar que testes não acessam rede, navegador ou dados reais.
- [x] Executar regressão proporcional do chatbot e validações offline do coletor.

### Critério de aceite

- matriz do adapter coberta e aprovada;
- chamadas externas são substituídas na fronteira correta, não por mocks do próprio resultado final;
- comportamento legado local permanece verde.

### Fechamento P2

**Commit planejado:** `C02`
**Mensagem sugerida:** `feat(collector): establish chatbot collection boundary`

---

# FASE P3 — Integrar fallback local, aquisição e persistência

## INT-COL-P3-001 — Implementar lookup local antes da coleta

**Status:** `VALIDATED`
**Dependência:** P2 fechada

### Objetivo

Manter o SQLite como primeira fonte e acionar aquisição somente em ausência real.

### Ações

- [x] Consultar e normalizar o número como no fluxo atual.
- [x] Retornar imediatamente em hit local.
- [x] Não coletar quando o processo já estiver ativo ou persistido.
- [x] Acionar somente o adapter em miss local válido.

### Critério de aceite

- caminho local mantém comportamento e desempenho esperados;
- fake do coletor prova zero chamadas em hit local;
- miss local válido alcança a fronteira remota exatamente uma vez.

## INT-COL-P3-002 — Ingerir somente coleta válida no SQLite

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P3-001`

### Objetivo

Persistir a árvore normalizada aceita usando o repositório existente.

### Ações

- [x] Chamar `ingest_processes()` com origem identificável e sem payload bruto.
- [x] Preservar transação, rollback e sanitização existentes.
- [x] Recarregar a árvore persistida como fonte consumida pelo chatbot.
- [x] Não persistir `PARCIAL`, `BLOQUEADO`, `FALHA` ou `NAO_ENCONTRADO`.

### Critério de aceite

- sucesso aceito gera uma linha processual e chunks coerentes;
- falha de ingestão não deixa persistência parcial;
- árvore retornada ao chatbot corresponde ao round-trip sanitizado do SQLite.

## INT-COL-P3-003 — Integrar o resultado ao Agent 2 e ao progresso

**Status:** `VALIDATED`
**Dependências:** `INT-COL-P3-001`, `INT-COL-P3-002`

### Objetivo

Permitir que o fluxo atual responda com o processo recém-adquirido sem mudar a
fronteira HTTP ou o frontend.

### Ações

- [x] Atualizar apenas a fronteira de contexto/coleta necessária.
- [x] Definir `active_process`, `last_intent` e `collection_status` coerentes.
- [x] Emitir progresso seguro para lookup local, coleta, persistência e resultado.
- [x] Evitar detalhes de CAPTCHA, paths, stack trace ou dados sensíveis na resposta pública.

### Critério de aceite

- processo coletado se torna ativo e percorre análise/resposta atuais;
- processo local continua produzindo os estados anteriores compatíveis;
- contrato FastAPI/Angular permanece inalterado.

## INT-COL-P3-004 — Reutilizar o processo sem recoleta

**Status:** `VALIDATED`
**Dependência:** `INT-COL-P3-003`

### Objetivo

Comprovar que sessão ativa e persistência evitam trabalho externo repetido.

### Ações

- [x] Testar pergunta seguinte na mesma sessão.
- [x] Testar nova sessão consultando o SQLite.
- [x] Testar reinício lógico do backend com o mesmo banco.
- [x] Confirmar que o fake do coletor permanece sem nova chamada.

### Critério de aceite

- segunda pergunta, nova sessão e restart reutilizam o processo persistido;
- coleta ocorre somente quando a fonte local realmente não possui o processo.

### Fechamento P3

**Commit planejado:** `C03`
**Mensagem sugerida:** `feat(chat): acquire and persist missing processes`

---

# FASE P4 — Tratar estados, degradação e falhas

## INT-COL-P4-001 — Traduzir a matriz de estados do coletor

**Status:** `IMPLEMENTED`
**Dependência:** P3 fechada

### Objetivo

Fazer cada resultado externo chegar ao chatbot com semântica verdadeira.

### Ações

- [x] Tratar número inválido/ausente sem abrir navegador.
- [x] Tratar `NAO_ENCONTRADO` como ausência semântica comprovada no TRT18.
- [x] Tratar `PARCIAL` como dado insuficiente, sem persistir como sucesso.
- [x] Tratar `BLOQUEADO` como indisponibilidade/retry posterior.
- [x] Tratar `FALHA` e exceções como falha técnica controlada.

### Critério de aceite

- somente `NAO_ENCONTRADO` segue a semântica remota de não encontrado;
- nenhum outro estado vira `None`/`not_found` silenciosamente;
- mensagens não prometem retry automático inexistente.

## INT-COL-P4-002 — Preservar a API diante de falha externa

**Status:** `IMPLEMENTED`
**Dependência:** `INT-COL-P4-001`

### Objetivo

Impedir que indisponibilidade do portal, CAPTCHA ou persistência quebre a API
ou produza resposta enganosa.

### Ações

- [x] Integrar falhas ao mecanismo controlado já existente no orquestrador.
- [x] Manter resposta pública segura e observabilidade interna suficiente.
- [x] Não capturar exceções amplas sem classificação e contexto.
- [x] Não apagar processo local existente por falha de atualização/aquisição.

### Critério de aceite

- API retorna o contrato público esperado nos cenários controlados;
- nenhum falso sucesso, falso `not_found` ou traceback público;
- banco permanece consistente após falha.

## INT-COL-P4-003 — Fixar regressões dos estados em testes

**Status:** `IMPLEMENTED`
**Dependência:** `INT-COL-P4-002`

### Objetivo

Cobrir a matriz completa no nível em que o usuário do chatbot observa o efeito.

### Ações

- [x] Testar estados via Agent 2/orquestrador e, quando adequado, API ASGI local.
- [x] Testar ausência de persistência em estados não aceitos.
- [x] Testar rollback de ingestão e preservação de dado anterior.
- [x] Executar regressão do backend.

### Critério de aceite

- todos os estados possuem teste de comportamento, não apenas teste do adapter;
- falhas externas não causam regressão no caminho local.

### Fechamento P4

**Commit planejado:** `C04`
**Mensagem sugerida:** `fix(chat): preserve collector failure semantics`

---

# FASE P5 — Unificar runtime, configuração e duplicações da integração

## INT-COL-P5-001 — Fechar o manifesto de dependências Python

**Status inicial:** `TODO`
**Dependência:** P4 fechada

### Objetivo

Transformar o requirements consolidado em fonte reproduzível, não apenas em
uma soma textual dos dois arquivos antigos.

### Ações

- [ ] Auditar dependências diretas reais de chatbot, coletor e CAPTCHA.
- [ ] Remover duplicações por nome sem remover dependência necessária.
- [ ] Separar runtime de notebook/pesquisa/teste somente se a divisão tiver
  benefício comprovado e continuar com fonte de verdade clara.
- [ ] Documentar/automatizar instalação dos browsers exigidos pelo Playwright.
- [ ] Não atualizar versões maiores incidentalmente.

### Critério de aceite

- manifesto(s) possuem ownership e propósito explícitos;
- instalação cobre os imports reais de runtime;
- notebook/pesquisa não força dependências desnecessárias no runtime sem decisão.

## INT-COL-P5-002 — Unificar configuração e paths

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P5-001`

### Objetivo

Eliminar configuração concorrente e dependência da máquina do desenvolvedor.

### Ações

- [ ] Levantar `.env`, constantes e paths dos dois módulos.
- [ ] Centralizar somente variáveis realmente compartilhadas.
- [ ] Preservar configuração específica no módulo proprietário.
- [ ] Atualizar `.env.example` sem segredo.
- [ ] Garantir que cache, debug, SQLite e browser sejam resolvidos por paths do projeto/configuração.

### Critério de aceite

- bootstrap oficial não depende de path absoluto local;
- não existem duas variáveis com o mesmo propósito e precedência ambígua;
- dados/cache continuam fora do Git.

## INT-COL-P5-003 — Resolver duplicações bloqueantes da integração

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P5-002`

### Objetivo

Manter uma implementação canônica de CAPTCHA/configuração sem abrir uma
refatoração geral do repositório.

### Ações

- [ ] Identificar a implementação canônica do CAPTCHA.
- [ ] Remover cópia temporária somente após confirmar consumidores/imports.
- [ ] Atualizar o coletor para a fonte definitiva.
- [ ] Procurar duplicações de README, requirements, config e arquivos criadas
  especificamente pela união das branches.
- [ ] Registrar e adiar duplicações antigas sem impacto na integração.

### Critério de aceite

- nenhuma duplicação da integração possui ownership ambíguo;
- CLI, cache e coleta continuam usando a fonte canônica;
- o diff não contém limpeza oportunista.

## INT-COL-P5-004 — Validar bootstrap Python limpo

**Status inicial:** `TODO`
**Dependências:** `INT-COL-P5-001`, `INT-COL-P5-002`, `INT-COL-P5-003`

### Objetivo

Comprovar instalação, importação e execução a partir das fontes versionadas.

### Ações

- [ ] Criar `.venv` limpo e ignorado.
- [ ] Instalar somente pelos manifests oficiais, com autorização quando exigida.
- [ ] Instalar browsers Playwright pelo procedimento documentado.
- [ ] Importar backend e coletor; executar health e testes offline/focados.
- [ ] Registrar versões, tempo, avisos e falhas ambientais.

### Critério de aceite

- ambiente limpo sobe o backend e importa o coletor;
- testes focados executam sem dependência instalada manualmente fora do manifesto;
- nenhuma coleta real é exigida para validar o bootstrap.

### Fechamento P5

**Commit planejado:** `C05`
**Mensagem sugerida:** `chore(runtime): unify collector setup and configuration`

---

# FASE P6 — Validar a integração de ponta a ponta

## INT-COL-P6-001 — Executar regressão completa do backend

**Status inicial:** `TODO`
**Dependência:** P5 fechada

### Ações

- [ ] Executar testes focados do adapter, repositório, Agent 2 e API.
- [ ] Executar a suíte completa do chatbot no ambiente limpo.
- [ ] Comparar com a baseline P0 e investigar toda falha nova.
- [ ] Confirmar que o frontend não foi alterado funcionalmente.

### Critério de aceite

- zero regressão nova sem explicação;
- caminho local anterior continua aprovado;
- diff funcional do frontend é vazio.

## INT-COL-P6-002 — Executar regressão offline do coletor

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P6-001`

### Ações

- [ ] Validar CNJ, cache, normalização e modelos com fixtures sanitizadas.
- [ ] Executar CLI/serviço em modo somente cache quando houver fixture completa.
- [ ] Confirmar que exemplos/baselines protegidos não foram sobrescritos.
- [ ] Confirmar ausência de rede nos testes offline.

### Critério de aceite

- contrato produtor permanece válido;
- nenhuma baseline ou dado real foi modificado;
- coleta offline é reproduzível.

## INT-COL-P6-003 — Executar matriz integrada automatizada

**Status inicial:** `TODO`
**Dependências:** `INT-COL-P6-001`, `INT-COL-P6-002`

### Cenários mínimos

- [ ] processo local consultável sem coletor;
- [ ] processo ausente aciona fake de sucesso, normaliza, ingere e responde;
- [ ] segunda pergunta não recoleta;
- [ ] nova sessão/restart reutiliza SQLite;
- [ ] remoto não encontrado recebe tratamento correto;
- [ ] parcial, bloqueio, falha e exceção não viram `not_found`;
- [ ] falha de ingestão faz rollback;
- [ ] API mantém contrato público;
- [ ] frontend permanece fora do fluxo interno.

### Critério de aceite

- todos os cenários passam com evidência de comandos e resultados;
- testes exercitam fronteiras reais internas, não apenas mocks autocontidos.

## INT-COL-P6-004 — Executar aceite real controlado no TRT18

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P6-003`
**Condição:** autorização e ambiente externo disponíveis

### Objetivo

Comprovar uma vez o fluxo completo com processo sanitizável ausente no SQLite.

### Ações

- [ ] Selecionar número autorizado sem registrá-lo na documentação/fixtures.
- [ ] Confirmar previamente que não está no SQLite de teste.
- [ ] Executar chatbot → coleta TRT18 → normalização → ingestão → resposta.
- [ ] Repetir consulta e confirmar ausência de nova coleta.
- [ ] Remover/preservar de forma segura dados locais de teste conforme autorização,
  sem versioná-los.
- [ ] Se portal/CAPTCHA/ambiente bloquear, registrar `BLOCKED`; não simular sucesso.

### Critério de aceite

- fluxo real comprovado sem expor dado processual no Git/log público;
- segunda consulta usa persistência;
- limitação externa, se houver, é declarada honestamente.

### Fechamento P6

**Commit planejado:** `C06`
**Mensagem sugerida:** `test(integration): cover chatbot collector workflow`

---

# FASE P7 — Alinhar a documentação do produto

## INT-COL-P7-001 — Atualizar README e bootstrap principal

**Status inicial:** `TODO`
**Dependência:** P6 fechada

### Ações

- [ ] Descrever `entrada-de-dados/` na estrutura raiz.
- [ ] Documentar fluxo local → coleta → persistência.
- [ ] Documentar setup Python, Playwright/browsers e variáveis necessárias.
- [ ] Manter links para documentação técnica aprofundada.
- [ ] Não recolocar README/requirements concorrentes no coletor.

### Critério de aceite

- README é porta de entrada coerente e executável;
- comportamento planejado não é descrito como implementado sem evidência.

## INT-COL-P7-002 — Atualizar arquitetura, ingestão, desenvolvimento e orquestração

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P7-001`

### Conteúdo mínimo

- [ ] ownership de chatbot, adapter e coletor;
- [ ] contrato e matriz de estados;
- [ ] cache bruto versus SQLite consumidor;
- [ ] sanitização e riscos de dados pessoais;
- [ ] fallback, persistência, retry manual e degradação;
- [ ] setup limpo, Playwright/CAPTCHA e paths;
- [ ] diferença entre consulta individual e notebook/pesquisa;
- [ ] limitações reais ainda existentes.

### Critério de aceite

- `docs/ARCHITECTURE.md`, `docs/data-ingestion.md`,
  `docs/development.md` e `docs/orchestration.md` refletem o código final;
- links locais e nomes de arquivos estão válidos.

## INT-COL-P7-003 — Executar auditoria documental cruzada

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P7-002`

### Ações

- [ ] Comparar afirmações com código, testes e configuração.
- [ ] Remover referências históricas contraditórias.
- [ ] Confirmar fonte única de dependências e setup.
- [ ] Procurar segredo, path local, número processual real e detalhe sensível.
- [ ] Validar links e `git diff --check`.

### Critério de aceite

- documentação não duplica nem contradiz a implementação;
- nenhum dado real/sensível foi incorporado;
- auditoria cruzada está registrada no controle.

### Fechamento P7

**Commit planejado:** `C07`
**Mensagem sugerida:** `docs(project): document chatbot collector integration`

---

# FASE P8 — Fechamento, segurança e projeção para `main`

## INT-COL-P8-001 — Executar regressão e revisão final do diff

**Status inicial:** `TODO`
**Dependência:** P7 fechada

### Ações

- [ ] Reexecutar suítes focadas, regressão backend, offline do coletor e smoke
  integrado automatizado.
- [ ] Revisar `git diff` da branch contra a base correta.
- [ ] Executar `git diff --check`.
- [ ] Remover debug, logs temporários e alterações acidentais.
- [ ] Confirmar ausência de segredo e dado processual real.

### Critério de aceite

- regressões aprovadas ou limitações objetivas formalmente aceitas;
- diff final focado, legível e reversível.

## INT-COL-P8-002 — Validar Definition of Done global

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P8-001`

### Critério de aceite

- [ ] processo local continua consultável;
- [ ] processo remoto ausente localmente pode ser adquirido;
- [ ] sucesso válido é persistido e reutilizado;
- [ ] falhas não viram falso `not_found` nem quebram a API;
- [ ] frontend não sofreu alteração funcional;
- [ ] adapter é a única fronteira entre os módulos;
- [ ] não existe lógica duplicada de coleta no chatbot;
- [ ] setup limpo e documentação correspondem ao código;
- [ ] commits C00–C07 possuem hashes e evidências registrados.

## INT-COL-P8-003 — Remover artefatos operacionais da projeção final

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P8-002`

### Ações

- [ ] Remover da árvore destinada à `main`:
  - `CHECKLIST_INTEGRACAO_CHATBOT_COLETA.md`;
  - `CONTROLE_PROGRESSO_COMMITS_INTEGRACAO_CHATBOT_COLETA.md`;
  - `AGENTS.md`;
  - `.codex/rules/safety.rules`.
- [ ] Revisar exceções residuais no `.gitignore` criadas apenas para esses arquivos.
- [ ] Não remover `.agents/` ou outro arquivo homônimo sem classificação e
  autorização explícitas.
- [ ] Confirmar pela comparação com `main` que nenhum artefato operacional
  permanece no conteúdo final.

### Critério de aceite

- projeção final contém apenas código, testes, configuração e documentação do produto;
- remoção é restrita aos alvos explicitamente classificados;
- histórico/evidências anteriores permanecem recuperáveis na branch.

## INT-COL-P8-004 — Emitir gate de prontidão para merge

**Status inicial:** `TODO`
**Dependência:** `INT-COL-P8-003`

### Ações

- [ ] Confirmar um commit por fase, sem commits por ID.
- [ ] Confirmar mensagens, hashes, IDs cobertos e testes de cada checkpoint.
- [ ] Registrar riscos adiados e decisão de aceite.
- [ ] Produzir `READY_FOR_MERGE` ou `NOT_READY` com bloqueios objetivos.
- [ ] Não executar push ou merge sem autorização explícita.

### Critério de aceite

- nenhum gate é inferido apenas por código escrito;
- saída final é comprovada por testes, diff, documentação e histórico Git.

### Fechamento P8

**Commit planejado:** `C08`
**Mensagem sugerida:** `chore(integration): finalize chatbot collector delivery`

> Como o controle será removido durante esta fase, o hash de `C08` deve ser
> preservado pelo próprio histórico Git e no relatório final do fechamento.

---

# 6. Sequência obrigatória

```text
P0 Baseline estrutural
        ↓
P1 Contratos e decisões
        ↓
P2 Fronteira Python
        ↓
P3 Fallback e persistência
        ↓
P4 Estados e degradação
        ↓
P5 Runtime e configuração
        ↓
P6 Testes e aceite real
        ↓
P7 Documentação do produto
        ↓
P8 Fechamento e projeção para main
```

Nenhuma fase autoriza avanço automático. Descoberta que aumente materialmente
o escopo deve ser registrada e discutida antes de alterar a checklist.

---

# 7. Definition of Done global

A integração está concluída somente quando:

1. **Contrato:** produtor, consumidor e adapter possuem semântica comprovada.
2. **Aquisição:** lookup local precede coleta real.
3. **Persistência:** sucesso aceito é transacional e sobrevive ao restart.
4. **Estados:** ausência semântica não se confunde com falha externa.
5. **Compatibilidade:** fluxo local, API e frontend permanecem compatíveis.
6. **Segurança:** nenhum segredo, dado real ou detalhe interno indevido foi exposto.
7. **Reprodutibilidade:** ambiente limpo instala, importa e testa o sistema.
8. **Testes:** matriz automatizada e aceite real controlado possuem evidência.
9. **Documentação:** README e `docs/` descrevem a implementação entregue.
10. **Rastreabilidade:** cada ID possui evidência no controle e cada fase possui
    exatamente um checkpoint Git autorizado.
11. **Escopo:** duplicações e refatorações sem relação foram adiadas.
12. **Entrega:** artefatos operacionais temporários não aparecem na projeção final
    destinada à `main`.
