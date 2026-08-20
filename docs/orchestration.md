# Orquestração dos fluxos

## Objetivo

Este documento detalha como as etapas do backend são coordenadas. A
orquestração atual é síncrona e implementada em Python; não utiliza LangGraph,
fila de mensagens ou motor externo de workflows.

## Princípios

- o orquestrador controla ordem, contexto, progresso e tratamento de falhas;
- cada agente ou serviço recebe dados explícitos e devolve uma estrutura;
- regras determinísticas têm prioridade sobre geração;
- integrações opcionais não anulam resultados estruturados disponíveis;
- respostas públicas não expõem exceções, prompts ou detalhes internos.

## Chat processual

O ponto de entrada comum é
`orchestrators.processual_chat_orchestrator.run_processual_chat_step`.

```text
Entrada: message + session_state + progress_reporter opcional
  │
  ├─ 1. interpret_user_message                 [Agente 1]
  ├─ 2. build_context_and_collect              [Agente 2]
  ├─ 3. analyze_process_context                [Agente 3]
  ├─ 4. create_user_response                   [Agente 4]
  └─ 5. _build_processual_chat_response        [contrato público]
```

### Etapa 1 — intenção

O Agente 1:

1. procura um número processual de 20 dígitos;
2. tenta classificar a mensagem por regras locais;
3. chama Ollama somente quando as regras não bastam;
4. valida o JSON retornado pelo modelo;
5. usa fallback seguro se houver erro esperado de modelo ou parse.

Intenções aceitas: `greeting`, `process_lookup`, `process_question`,
`legal_general_question`, `out_of_scope` e `unclear`.

Saída relevante: intenção, confiança, objetivo do usuário e número processual
quando identificado.

### Etapa 2 — contexto, sessão e recuperação

O Agente 2 recebe a mensagem, a intenção e a sessão. Suas responsabilidades
incluem:

- transportar e ajustar a intenção quando o contexto exige;
- consultar o processo informado por meio do adaptador;
- manter ou substituir `active_process`;
- preservar uma janela limitada da conversa;
- resolver uma especificação estruturada da pergunta;
- selecionar a rota de consulta;
- preparar um contexto RAG quando a rota exigir.

A sessão mínima contém:

```python
{
    "conversation": [],
    "active_process": None,
    "last_intent": None,
}
```

O processo ativo permite perguntas subsequentes sem repetir o número. Perguntas
que exigem processo, mas não possuem processo ativo, seguem a rota
`missing_process`.

### Decisão de rota

`resolve_process_query` representa a necessidade semântica da pergunta;
`route_process_query` decide a estratégia de recuperação.

```text
fora de escopo ───────────────────────────────→ out_of_scope
campo/movimentação estruturada + processo ───→ structured
teor ou fundamento documental + processo ───→ rag
conceito ligado ao caso + processo ──────────→ hybrid
pergunta dependente sem processo ────────────→ missing_process
```

Na rota `structured`, o SQLite fornece os fatos. Nas rotas `rag` e `hybrid`, o
retriever tenta:

1. obter chunks canônicos do processo;
2. gerar embeddings;
3. garantir a coleção e sincronizar pontos no Qdrant;
4. pesquisar por similaridade;
5. aplicar reranking lexical local;
6. produzir chunks e fontes sanitizadas.

Uma falha nessa sequência gera contexto degradado (`unavailable` ou `error`) e
não inventa conteúdo ausente.

### Etapa 3 — análise

O Agente 3 transforma o contexto em uma estrutura com tipo de análise, foco,
fatos e limitações. Ele contém analisadores determinísticos para resumo,
situação, partes, pendências, valor da causa, campos estruturados, sentença,
arquivamento e linhas do tempo.

Quando usa LLM, o agente:

- envia uma versão sanitizada do processo;
- valida a estrutura de saída;
- rejeita conteúdo incompatível ou dados pessoais;
- mantém limitações vindas do RAG;
- prefere fallback local sempre que possível.

### Etapa 4 — resposta

O Agente 4 recebe somente a pergunta e a análise preparada. Ele não consulta o
banco nem decide novos fatos. A resposta final:

- organiza fatos e limitações;
- pode usar geração local nos caminhos previstos;
- remove identificadores e termos internos;
- mascara documentos pessoais;
- possui fallback determinístico quando a geração falha.

### Montagem do contrato

O orquestrador retorna `ProcessualChatStepResult`, que preserva dados internos
das etapas para diagnóstico e contém `ProcessualChatResponse` como saída
pública. A resposta pública inclui:

- `tipo`;
- `intent` efetiva;
- `resposta`;
- `processo_ativo`;
- `collection_status`;
- `failed_stage`;
- `rag_status`;
- `fontes`.

## Progresso e falhas

Cada etapa principal emite eventos `started` e `finished`. Caminhos internos
podem emitir eventos adicionais, como uso de regra local, consulta ao modelo,
fallback, rota RAG e sincronização vetorial.

`ProcessProgressEvent` possui código, nível, mensagem, detalhes e tempo
decorrido opcional. O callback é opcional; sua ausência não muda o resultado do
fluxo.

Se uma exceção escapar de uma etapa principal, o orquestrador:

1. registra evento `<etapa>.failed`;
2. identifica a etapa como Agente 1, 2, 3 ou 4;
3. devolve uma mensagem genérica segura;
4. preserva os dados válidos produzidos antes da falha;
5. preenche `failed_stage`.

O orquestrador não deve silenciar erros internos nos serviços quando eles
precisam de classificação específica. Cada integração traduz seus erros na
fronteira adequada.

## Adaptação para terminal e API

### Terminal

`main.py --chat` cria uma única sessão em memória e chama o mesmo orquestrador a
cada mensagem. Um reporter apresenta eventos com o prefixo `Fluxo:`. O modo
`--trace` inclui detalhes permitidos para diagnóstico.

### API

`POST /api/processos/chat` obtém ou cria uma sessão em `_SESSIONS`, executa o
orquestrador, registra a resposta do assistente na conversa e serializa a
dataclass com `asdict`.

A API não fornece reporter de progresso ao orquestrador; por isso a resposta é
síncrona e não transmite eventos ao cliente. Não há streaming implementado.

## Orquestração de metas

### Simulação

`POST /api/metas/simular`:

```text
payload Pydantic
  → MetaSimulationRequest
  → simulate_meta
  → MetaSimulationResponse
  → explain_meta_simulation
  → envelope HTTP
```

O adaptador ainda não chama motor de cálculo: retorna `not_integrated`. A
explicação deve conservar essa limitação.

### Processo × meta

`POST /api/metas/impacto-processo`:

```text
payload Pydantic
  → run_process_meta_impact
      → normaliza número
      → find_process_by_number
      → extract_process_events
      → evaluate_process_meta_impact
  → explain_process_meta_impact
  → envelope HTTP
```

Se o processo não for encontrado, o fluxo retorna flags `None` e impacto
`processo_nao_encontrado`. Quando há processo, as flags e a classificação são
heurísticas provisórias; nenhuma fórmula oficial é aplicada.

## Invariantes

Alterações futuras devem preservar, salvo decisão arquitetural explícita:

1. Agente 4 não cria nem consulta fatos;
2. Qdrant não substitui a fonte estruturada SQLite;
3. ausência de RAG não apaga fatos estruturados;
4. saída de modelo é validada antes de virar contrato ou resposta;
5. documento pessoal não deve chegar ao modelo ou ao usuário sem necessidade;
6. cálculo de meta não pertence à LLM;
7. falhas públicas não expõem detalhes técnicos;
8. estado de sessão é passado explicitamente ao fluxo processual.

## Pontos de extensão

- um coletor real pode ser ligado atrás do adaptador, preservando o contrato de
  processo;
- outro armazenamento de sessão pode substituir `_SESSIONS` antes de múltiplos
  workers;
- o simulador oficial pode ser conectado por `meta_simulator_adapter.py` após
  validação dos contratos;
- progresso da API pode evoluir para SSE ou WebSocket sem alterar as etapas
  internas, desde que o callback continue desacoplado;
- novos roteadores ou rerankers devem preservar status de degradação e fontes
  sanitizadas.

## Cenários mínimos de validação

Ao alterar orquestração, cubra pelo menos:

- intenção determinística e fallback do Ollama;
- consulta inicial e pergunta subsequente com processo ativo;
- processo inexistente;
- rota estruturada sem chamada vetorial;
- rota RAG com sucesso, vazio e indisponibilidade;
- falha em cada etapa principal e `failed_stage` correto;
- remoção de dados pessoais;
- independência entre sessões da API;
- retorno `not_integrated` do simulador enquanto não houver implementação;
- impacto inconclusivo quando faltarem dados processuais.
