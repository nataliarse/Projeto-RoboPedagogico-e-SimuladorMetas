# Checklist — Resolução de Pendências no Chatbot Processual

**Projeto:** `chatbot_processual_ai`  
**Baseline analisado:** `chatbot_processual_ai(9).zip`  
**Data do baseline:** 17/09/2026  
**Branch confirmada:** `feat/resolucao-pendencias-processual`  
**Escopo:** fazer o chatbot responder de forma confiável:

```text
se PENDENTE:
→ explicar por que está pendente
→ identificar qual condição/movimentação ainda falta para sair da pendência

se BAIXADO:
→ informar claramente que o processo já está baixado
→ não inventar movimentação faltante
```

**Regra operacional:** executar em unidades pequenas. Um item validado não autoriza avanço automático para outro item dependente sem revisar suas precondições.

---

# 0. Resultado esperado

Ao final desta checklist:

- o sistema diferencia **pendência registrada** de **movimento/condição faltante**;
- o chatbot não usa a última movimentação como resposta para “o que falta?”;
- o estado `BAIXADO` é tratado antes de tentar calcular pendência;
- existe uma fonte de verdade explícita para regras de transição;
- existe um mecanismo determinístico que aplica essas regras aos dados do processo;
- perguntas equivalentes de resolução de pendência seguem o mesmo fluxo;
- Agent 3 recebe fatos já resolvidos, em vez de tentar descobri-los;
- Agent 4 apenas comunica o resultado estruturado;
- LLM não é usada para inventar regra processual ausente;
- testes cobrem os cenários de negócio principais;
- limitações de dados/regra são respondidas de forma explícita, não mascaradas.

---

# 1. Convenção de status

Use apenas:

- `TODO` — ainda não iniciado;
- `READY` — precondições permitem iniciar;
- `IN_PROGRESS` — investigação/implementação iniciada;
- `BLOCKED` — impedimento objetivo;
- `IMPLEMENTED` — implementação concluída, validação ainda pendente;
- `VALIDATED` — critério de aceite + testes + evidências confirmados;
- `REJECTED` — solução considerada inadequada;
- `SUPERSEDED` — item substituído formalmente.

**Nunca marcar `VALIDATED` somente porque o código foi escrito.**

---

# FASE P0 — Baseline e proteção contra regressão

## PEND-P0-001 — Confirmar branch e estado inicial

**Status inicial:** `READY`  
**Status atual:** `VALIDATED`  
**Prioridade:** bloqueante

### Ações

- [x] Executar `git branch --show-current`.
- [x] Executar `git status --short`.
- [x] Registrar alterações preexistentes.
- [x] Não limpar/restaurar mudanças alheias automaticamente.
- [x] Registrar hash do commit-base.

### Critério de aceite

- branch confirmada;
- worktree inicial registrado;
- baseline reversível.

---

## PEND-P0-002 — Registrar baseline dos testes atuais

**Status inicial:** `READY`  
**Status atual:** `VALIDATED`  
**Prioridade:** bloqueante

### Ações

- [x] Executar a suíte atual do backend a partir do diretório correto.
- [x] Registrar testes aprovados/falhos e causas conhecidas.
- [x] Executar especificamente os testes atuais relacionados a `pending_issues`, situação e movimentações.
- [x] Registrar respostas atuais para:
  - `Quais pendências existem?`
  - `O que falta para sair da pendência?`
  - `Por que continua pendente?`
  - `O que precisa acontecer para ser baixado?`
  - `Qual movimentação ainda falta?`
  - `Qual é o próximo movimento necessário?`
- [x] Executar pelo menos um processo `PENDENTE` e um `BAIXADO`.

### Critério de aceite

- comportamento incorreto atual reproduzido e documentado;
- regressões futuras podem ser comparadas com o baseline.

---

## PEND-P0-003 — Congelar escopo negativo

**Status inicial:** `READY`
**Status atual:** `VALIDATED`

### Não faz parte desta etapa, salvo dependência comprovada

- [x] Não trocar 1B/4B/7B/8B ou outro modelo LLM como solução principal.
- [x] Não reescrever RAG inteiro.
- [x] Não refatorar frontend.
- [x] Não alterar o simulador de metas de forma independente.
- [x] Não refatorar agentes não relacionados.
- [x] Não introduzir framework pesado de rules engine sem necessidade.
- [x] Não introduzir dependência nova apenas por conveniência.
- [x] Não inventar regra jurídica/processual ausente nem inferi-la com conhecimento da LLM.
- [x] Não reescrever a arquitetura inteira.
- [x] Não corrigir problemas fora do escopo apenas porque foram encontrados.

### Critério de aceite

- diff futuro permanece focado na resolução de pendência.

---

# FASE P1 — Fonte de verdade e regra de negócio

## PEND-P1-001 — Inventariar o mapeamento oficial existente

**Status inicial:** `READY`  
**Prioridade:** bloqueante  
**Dependência externa:** SIM

### Objetivo

Descobrir exatamente qual fonte define:

```text
PENDENTE
→ quais movimentos/situações mantêm ou caracterizam esse estado
→ quais movimentos/situações encerram esse estado
→ quando o processo passa a BAIXADO
```

### Ações

- [ ] Revisar o fluxograma CNJ fornecido.
- [ ] Obter o mapeamento citado pela professora Natália como feito no início do projeto.
- [ ] Identificar se existem tabelas/códigos TPU, Situações CNJ ou regras complementares.
- [ ] Identificar se regras variam por classe, grau, fase, meta ou período.
- [ ] Marcar regras provisórias vs. regras homologadas.
- [ ] Registrar fonte e versão de cada regra.

### Critério de aceite

- existe um conjunto explícito e auditável de regras;
- nenhuma regra crítica depende apenas de “conhecimento do modelo”.

### Bloqueio

`BLOCKED` se o mapeamento oficial não estiver disponível ou estiver ambíguo.

---

## PEND-P1-002 — Formalizar contrato da regra de transição

**Status inicial:** `TODO`  
**Dependência:** PEND-P1-001

### Decisão alvo

Representar a regra em estrutura verificável, por exemplo:

```text
rule_id
current_state
target_state
applicability
required_events
alternative_events
terminal_events
evidence_source
rule_source
```

### Ações

- [ ] Definir quais campos são obrigatórios.
- [ ] Definir como representar `E` / `OU` entre movimentos.
- [ ] Definir como tratar múltiplas condições simultâneas.
- [ ] Definir como registrar regras condicionais.
- [ ] Definir como referenciar a fonte oficial.
- [ ] Evitar texto livre como única representação da regra.

### Critério de aceite

- uma regra pode ser aplicada por Python sem interpretação da LLM;
- estrutura suporta identificar condições satisfeitas e ausentes.

---

# FASE P2 — Dados necessários para aplicar a regra

## PEND-P2-001 — Auditar o que o coletor realmente entrega

**Status inicial:** `TODO`  
**Dependência:** PEND-P1-002

### Ações

- [ ] Mapear campos brutos das movimentações vindos do PJe/coletor.
- [ ] Confirmar existência ou ausência de:
  - código TPU;
  - código/situação CNJ;
  - descrição;
  - complemento;
  - data;
  - grau;
  - classe processual;
  - fase;
  - outros identificadores exigidos pelas regras.
- [ ] Comparar dado bruto com o objeto normalizado.
- [ ] Registrar campos descartados durante a normalização.

### Critério de aceite

- sabemos exatamente se os dados disponíveis são suficientes para aplicar cada regra.

---

## PEND-P2-002 — Preservar identificadores necessários na normalização

**Status inicial:** `TODO`  
**Dependência:** PEND-P2-001

### Ações

- [ ] Adicionar ao modelo normalizado somente os identificadores necessários.
- [ ] Preservar compatibilidade com dados já persistidos quando possível.
- [ ] Não substituir código oficial por matching textual se o código estiver disponível.
- [ ] Definir fallback explícito quando código oficial não existir na fonte.
- [ ] Atualizar persistência/DTO interno se necessário.

### Critério de aceite

- nenhum dado necessário ao motor de regras é perdido entre coleta e chatbot.

---

## PEND-P2-003 — Corrigir o significado do campo `pendencias`

**Status inicial:** `TODO`  
**Dependência:** PEND-P2-001

### Problema observado

`pendencias` atualmente pode conter algo semelhante a:

```text
"Última movimentação: ..."
```

Isso não equivale a:

```text
"movimentação que ainda falta ocorrer"
```

### Ações

- [ ] Documentar semanticamente o que `pendencias` representa hoje.
- [ ] Separar expedientes/pendências observadas de requisitos de saída da pendência.
- [ ] Impedir que `pendencias` seja tratado como fonte de `required_event`.
- [ ] Se o campo for mantido, preservar seu significado original sem sobrecarregá-lo.

### Critério de aceite

- `pendencias` não é mais usado como sinônimo de “o que falta”.

---

# FASE P3 — Motor determinístico de resolução

## PEND-P3-001 — Criar resultado estruturado de resolução

**Status inicial:** `TODO`  
**Dependência:** PEND-P1-002 + PEND-P2

### Contrato alvo conceitual

```text
current_state
target_state
already_resolved
applicable_rule
satisfied_conditions
missing_conditions
required_events
evidence
limitations
confidence
```

### Ações

- [ ] Definir DTO interno.
- [ ] Distinguir `unknown` de lista vazia.
- [ ] Permitir múltiplos movimentos alternativos.
- [ ] Permitir resposta “não determinável com os dados disponíveis”.
- [ ] Incluir evidência rastreável para cada condição.

### Critério de aceite

- Agent 3 pode receber uma conclusão factual sem recalcular regra.

---

## PEND-P3-002 — Implementar avaliação de BAIXADO como saída prioritária

**Status inicial:** `TODO`  
**Dependência:** PEND-P3-001

### Regra comportamental

```text
se estado atual já representa BAIXADO:
→ already_resolved = true
→ missing_conditions = []
→ não procurar próximo movimento para atingir BAIXADO
```

### Ações

- [ ] Definir estados considerados terminais conforme regra oficial.
- [ ] Evitar inferência por texto quando código/situação oficial estiver disponível.
- [ ] Registrar evidência usada para concluir BAIXADO.

### Critério de aceite

- processo já baixado nunca recebe movimento faltante inventado.

---

## PEND-P3-003 — Implementar avaliação de PENDENTE

**Status inicial:** `TODO`  
**Dependência:** PEND-P3-001 + PEND-P3-002

### Ações

- [ ] Selecionar regra aplicável.
- [ ] Ler eventos/movimentos já existentes.
- [ ] Marcar condições satisfeitas.
- [ ] Marcar condições ausentes.
- [ ] Determinar evento(s) necessário(s), se possível.
- [ ] Registrar evidência para cada conclusão.
- [ ] Retornar limitação explícita se a regra não puder ser aplicada.

### Critério de aceite

Para caso suportado, o motor produz deterministicamente:

```text
está PENDENTE
já ocorreu X
já ocorreu Y
falta Z
```

sem usar LLM.

---

## PEND-P3-004 — Reconciliar `meta_rules.py` / `process_event_extractor.py`

**Status inicial:** `TODO`  
**Dependência:** PEND-P3-003

### Ações

- [ ] Verificar se lógica existente pode ser reaproveitada.
- [ ] Remover duplicação de regras conflitantes.
- [ ] Não promover regra marcada como provisória sem validação.
- [ ] Definir fronteira entre:
  - extração de eventos;
  - regra estatística;
  - análise de pendência.
- [ ] Garantir uma única fonte de verdade para movimentos de baixa.

### Critério de aceite

- não existem dois mecanismos independentes decidindo baixa com critérios diferentes.

---

# FASE P4 — Roteamento e Agent 3

## PEND-P4-001 — Criar semântica explícita para resolução de pendência

**Status inicial:** `TODO`  
**Dependência:** PEND-P3

### Alvos mínimos

Distinguir:

```text
pending_list
pending_reason
pending_resolution
```

### Ações

- [ ] Atualizar `process_query_resolver`.
- [ ] Mapear frases equivalentes:
  - “o que falta para sair da pendência?”
  - “qual movimentação ainda falta?”
  - “por que continua pendente?”
  - “o que precisa acontecer para ser baixado?”
  - “qual próximo movimento necessário?”
- [ ] Evitar depender apenas da palavra literal `pendencia`.
- [ ] Revisar `process_query_router` para não enviar perguntas equivalentes por caminhos diferentes sem necessidade.

### Critério de aceite

- formulações semanticamente equivalentes chegam ao mesmo `pending_resolution`.

---

## PEND-P4-002 — Fazer Agent 3 consumir o motor de domínio

**Status inicial:** `TODO`  
**Dependência:** PEND-P4-001 + PEND-P3

### Ações

- [ ] Substituir o uso de `process["pendencias"]` como resposta para resolução.
- [ ] Consumir `pending_resolution`.
- [ ] Produzir `facts` com:
  - situação;
  - regra aplicável;
  - condições satisfeitas;
  - condições faltantes;
  - evento necessário;
  - evidências.
- [ ] Preencher `limitations` quando a conclusão não for possível.
- [ ] Não chamar LLM para completar regra ausente.

### Critério de aceite

- Agent 3 representa corretamente “o que falta”, não apenas “o que foi registrado”.

---

## PEND-P4-003 — Definir papel da LLM nesse fluxo

**Status inicial:** `TODO`  
**Dependência:** PEND-P4-002

### Decisão alvo

A LLM pode:

- interpretar formulação ambígua;
- resumir;
- explicar fatos já calculados.

A LLM não pode:

- inventar regra;
- inferir movimento obrigatório sem fonte;
- substituir evidência ausente.

### Ações

- [ ] Revisar prompts apenas depois do motor funcionar.
- [ ] Manter fallback determinístico.
- [ ] Garantir que 1B/4B/8B recebam fatos resolvidos.
- [ ] Se houver rewrite, impedir alteração dos fatos essenciais.

### Critério de aceite

- trocar modelo não muda a conclusão factual do fluxo suportado.

---

# FASE P5 — Agent 4 e resposta ao usuário

## PEND-P5-001 — Criar resposta determinística para BAIXADO

**Status inicial:** `TODO`  
**Dependência:** PEND-P4-002

### Resposta esperada

```text
O processo já se encontra na situação BAIXADO.
Não há movimentação pendente necessária para alcançar essa condição.
```

A redação pode variar, mas a semântica não.

### Critério de aceite

- resposta menciona explicitamente `BAIXADO`;
- não lista movimento faltante;
- não confunde `pendencias=[]` com mera ausência de informação.

---

## PEND-P5-002 — Criar resposta para PENDENTE com regra conhecida

**Status inicial:** `TODO`  
**Dependência:** PEND-P4-002

### Estrutura alvo

```text
Situação atual: PENDENTE.

Já ocorreu:
- X
- Y

Ainda falta:
- Z

Por isso o processo permanece pendente.
```

### Ações

- [ ] Mostrar somente fatos/evidências produzidos pelo motor.
- [ ] Diferenciar movimento ocorrido de movimento faltante.
- [ ] Se houver alternativas (`A OU B`), apresentá-las corretamente.
- [ ] Evitar afirmar causalidade além da regra aplicada.

### Critério de aceite

- usuário consegue identificar claramente o motivo e o requisito faltante.

---

## PEND-P5-003 — Criar resposta segura para caso indeterminado

**Status inicial:** `TODO`  
**Dependência:** PEND-P4-002

### Comportamento alvo

Se estiver PENDENTE mas regra/dados forem insuficientes:

```text
O processo está PENDENTE, mas os dados/regras disponíveis não permitem
determinar com segurança qual movimentação falta.
```

### Critério de aceite

- ausência de informação não é mascarada por inferência da LLM;
- resposta não usa última movimentação como substituto.

---

# FASE P6 — Testes de negócio

## PEND-P6-001 — Testar processo BAIXADO

**Status inicial:** `TODO`  
**Dependência:** P5

### Cenários mínimos

- [ ] “O que falta para sair da pendência?”
- [ ] “O que precisa acontecer para ser baixado?”
- [ ] “Qual movimentação ainda falta?”

### Critério de aceite

Todos retornam semanticamente:

```text
já está BAIXADO
→ não há movimento faltante para atingir BAIXADO
```

---

## PEND-P6-002 — Testar PENDENTE com requisito conhecido

**Status inicial:** `TODO`

### Cenários

- [ ] uma condição faltante;
- [ ] múltiplas condições, algumas satisfeitas;
- [ ] alternativas `A OU B`;
- [ ] condição já ocorrida não pode aparecer como faltante.

### Critério de aceite

- resultado corresponde exatamente à regra e ao histórico.

---

## PEND-P6-003 — Testar equivalência semântica das perguntas

**Status inicial:** `TODO`

### Entradas mínimas

- [ ] `Quais pendências existem?`
- [ ] `O que falta para sair da pendência?`
- [ ] `Por que continua pendente?`
- [ ] `O que precisa acontecer para ser baixado?`
- [ ] `Qual movimentação ainda falta?`
- [ ] `Qual é o próximo movimento necessário?`

### Critério de aceite

- `pending_list` permanece separado;
- as demais formulações equivalentes de resolução seguem `pending_resolution`.

---

## PEND-P6-004 — Testar insuficiência de regra/dados

**Status inicial:** `TODO`

### Ações

- [ ] Caso sem regra aplicável.
- [ ] Caso com código/movimento ausente.
- [ ] Caso com dados contraditórios.
- [ ] Caso onde somente descrição textual está disponível.

### Critério de aceite

- sistema responde limitação explícita;
- nenhuma LLM inventa movimento faltante.

---

## PEND-P6-005 — Garantir independência factual da LLM

**Status inicial:** `TODO`

### Ações

- [ ] Patchar `generate_text()` para falhar.
- [ ] Executar cenários determinísticos suportados.
- [ ] Confirmar que conclusão PENDENTE/BAIXADO e movimento faltante continuam corretos.
- [ ] Se Agent 4 usar rewrite, comparar fatos antes/depois.

### Critério de aceite

- função central continua correta sem modelo generativo.

---

# FASE P7 — Regressão, documentação e gate final

## PEND-P7-001 — Executar regressão completa

**Status inicial:** `TODO`

### Ações

- [ ] Testes focados de pendência.
- [ ] Suite backend completa.
- [ ] Comparar com baseline P0.
- [ ] Investigar toda falha nova.
- [ ] Verificar consultas não relacionadas a pendência.

### Critério de aceite

- nenhuma regressão não explicada.

---

## PEND-P7-002 — Atualizar documentação arquitetural

**Status inicial:** `TODO`

### Conteúdo mínimo

- [ ] significado de `pendencias`;
- [ ] origem de `situacao`;
- [ ] fonte oficial das regras;
- [ ] fluxo de `pending_resolution`;
- [ ] papel do motor determinístico;
- [ ] papel permitido da LLM;
- [ ] comportamento quando regra/dados forem insuficientes.

### Critério de aceite

- novo desenvolvedor consegue entender a função sem inferir pelo código.

---

## PEND-P7-003 — Revisar diff e rastreabilidade

**Status inicial:** `TODO`

### Ações

- [ ] `git diff --check`.
- [ ] Revisar alterações fora do escopo.
- [ ] Remover debug temporário.
- [ ] Confirmar que regras possuem fonte documentada.
- [ ] Registrar commits por unidade lógica.
- [ ] Registrar evidências de validação.

### Critério de aceite

- diff focado, auditável e reversível.

---

## PEND-P7-004 — Gate funcional final

**Status inicial:** `TODO`

A funcionalidade só pode ser declarada pronta quando:

- [ ] `BAIXADO` é reconhecido antes da análise de pendência;
- [ ] `PENDENTE` usa regra explícita;
- [ ] movimento faltante é calculado a partir da regra + histórico;
- [ ] `pendencias` não é usado como sinônimo de requisito faltante;
- [ ] perguntas equivalentes seguem o mesmo fluxo;
- [ ] caso indeterminado não inventa resposta;
- [ ] testes focados aprovados;
- [ ] regressão completa aprovada;
- [ ] documentação atualizada;
- [ ] nenhuma regra oficial está codificada apenas por inferência textual não validada.

**Saída permitida:** `READY_FOR_VALIDATION` ou `NOT_READY` com justificativa objetiva.

---

# 2. Sequência recomendada

```text
P0 Baseline
   ↓
P1 Fonte/regra oficial
   ↓
P2 Dados necessários
   ↓
P3 Motor determinístico
   ↓
P4 Resolver + Agent 3
   ↓
P5 Agent 4 / resposta
   ↓
P6 Testes de negócio
   ↓
P7 Regressão + documentação + gate
```

**Não antecipar P4/P5 antes de P1–P3.**  
Melhorar a resposta antes de existir uma conclusão factual confiável apenas mascara a deficiência estrutural.

---

# 3. Caminho crítico

Os itens realmente bloqueantes são:

```text
PEND-P1-001  Fonte oficial
      ↓
PEND-P1-002  Regra estruturada
      ↓
PEND-P2-001  Dados suficientes?
      ↓
PEND-P2-002  Preservar dados necessários
      ↓
PEND-P3-003  Motor calcula o que falta
      ↓
PEND-P4-002  Agent 3 consome resultado
      ↓
PEND-P5       Resposta
      ↓
PEND-P6       Testes
```

Se `PEND-P1-001` ou `PEND-P2-001` bloquear, **não compensar usando LLM**.

---

# 4. Definition of Done

A tarefa não está concluída quando “o robô respondeu corretamente em um exemplo”.

Está concluída quando:

1. **Regra:** a transição PENDENTE/BAIXADO possui fonte explícita.
2. **Dados:** o sistema preserva os campos necessários para aplicar a regra.
3. **Determinismo:** o movimento faltante é calculado por regra verificável.
4. **Semântica:** listar pendências e resolver pendência são operações distintas.
5. **BAIXADO:** estado terminal é tratado de forma inequívoca.
6. **Limitação:** ausência de regra/dado gera resposta explícita, não invenção.
7. **LLM:** modelo explica/interpreta, mas não cria regra de negócio.
8. **Testes:** cenários PENDENTE, BAIXADO e indeterminado estão cobertos.
9. **Rastreabilidade:** cada regra e conclusão possui evidência/fonte.
10. **Regressão:** demais funções do chatbot continuam operacionais.
