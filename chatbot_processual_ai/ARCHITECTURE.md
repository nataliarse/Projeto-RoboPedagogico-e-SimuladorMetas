# Arquitetura do Backend/IA

## Objetivo

Este documento descreve a arquitetura proposta para separar tres fluxos do
backend/IA:

1. chat processual;
2. simulador de metas;
3. analise hibrida de processo + impacto na meta.

A separacao deve preservar o fluxo atual do terminal e manter a evolucao do
projeto em modulos pequenos, contratos claros e funcoes testaveis. A fase atual
ja inclui SQLite local e uma base inicial de RAG com Qdrant/Ollama, mas ainda
nao implementa Playwright real, LangGraph ou interface visual.

## Fluxos

### 1. Chat processual

O chat processual e o fluxo atual de conversa sobre processos. Ele recebe uma
mensagem do usuario, interpreta a intencao, decide se precisa carregar ou usar
um processo ativo e devolve uma resposta clara com base nos dados processuais
disponiveis.

Responsabilidades principais:

- manter o estado da conversa apenas em memoria;
- usar o processo ativo quando a pergunta depender de contexto anterior;
- consultar a base local/adaptador somente quando necessario;
- nunca inventar dados ausentes da arvore do processo;
- manter o comportamento do terminal preservado.

### Base local e RAG

O backend usa SQLite como base estruturada local para processos, partes,
movimentacoes, documentos, pendencias, metadados de coleta e chunks canonicos.
A ingestao inicial vem do JSON local de exemplo e e idempotente por numero de
processo.

O Qdrant e usado como indice vetorial opcional para chunks. O roteador
deterministico decide quando uma pergunta deve usar apenas dados estruturados,
quando deve buscar chunks, ou quando deve combinar os dois. Se Qdrant ou o
modelo de embedding local nao estiverem disponiveis, o chat preserva o fluxo
estruturado e explicita a limitacao na resposta estruturada.

Fluxo atual da base local:

```text
data/sample_processes.json
  -> seed automatico
  -> SQLite local em data/processual.sqlite3
  -> arvore JSON reconstruida para os agentes
  -> chunks canonicos
  -> embeddings via Ollama, quando RAG for acionado
  -> Qdrant, quando disponivel
```

O SQLite e a fonte estruturada local. O Qdrant nao substitui o SQLite; ele e
apenas um indice semantico para trechos textuais.

### 2. Simulador de metas

O simulador de metas recebe um cenario estruturado e devolve um resultado
estruturado sobre a meta solicitada. Ele deve ser tratado como componente de
calculo, nao como uma resposta livre da LLM.

Responsabilidades principais:

- receber identificador da meta, ano, unidade e cenario;
- calcular ou integrar o resultado da simulacao quando a regra estiver definida;
- devolver indicadores, resultado, meta de referencia e observacoes;
- deixar explicito quando a simulacao ainda nao estiver integrada ou validada.

### 3. Processo + impacto na meta

O fluxo hibrido avalia um processo individual em relacao a uma meta. Ele deve
usar os dados ja coletados do processo para identificar eventos relevantes e
produzir uma leitura provisoria de impacto.

Responsabilidades principais:

- localizar o processo pelo numero informado;
- extrair eventos processuais dos campos disponiveis;
- classificar sinais como novo, julgado ou baixado apenas quando houver criterio
  validado;
- indicar quando os dados forem insuficientes ou quando a regra oficial ainda
  nao estiver definida;
- explicar o resultado sem transformar a leitura provisoria em regra oficial.

## Responsabilidades entre calculo, regras e LLM

O backend deve manter uma separacao rigida entre calculo, validacao e
explicacao:

- o simulador calcula;
- as regras deterministicas validam eventos, criterios e consistencia dos dados;
- a LLM explica respostas estruturadas em linguagem natural;
- a LLM nao deve inventar dados processuais, indicadores, formulas oficiais ou
  criterios oficiais da Meta 1;
- quando a regra oficial nao estiver validada, a resposta deve declarar a
  limitacao em vez de preencher lacunas com suposicoes.

Na pratica, a LLM deve receber resultados ja estruturados por contratos do
backend. Ela pode melhorar clareza, tom e organizacao da resposta, mas nao deve
decidir fatos, calcular indicadores ou criar regra normativa.

## Contratos

### ProcessualChatRequest

Entrada do fluxo de chat processual.

Campos:

- `session_id: str | None`: identificador opcional da sessao;
- `mensagem: str`: mensagem enviada pelo usuario.

### ProcessualChatResponse

Saida do fluxo de chat processual.

Campos:

- `tipo: str`: tipo da resposta;
- `intent: str | None`: intencao identificada;
- `resposta: str`: resposta final ao usuario;
- `processo_ativo: str | None`: numero do processo ativo, quando houver;
- `collection_status: str | None`: status da coleta/contexto;
- `failed_stage: str | None`: etapa que falhou, quando houver erro controlado.
- `rag_status: str | None`: status da busca semantica quando houver decisao RAG;
- `fontes: list[dict]`: fontes seguras derivadas dos chunks recuperados.

### MetaSimulationRequest

Entrada do simulador de metas.

Campos:

- `meta_id: str`: identificador da meta;
- `ano: int`: ano de referencia;
- `unidade: str | None`: unidade, vara, tribunal ou recorte equivalente;
- `cenario: dict`: dados estruturados do cenario de simulacao.

### MetaSimulationResponse

Saida do simulador de metas.

Campos:

- `tipo: str`: tipo da resposta;
- `meta_id: str`: identificador da meta;
- `ano: int`: ano de referencia;
- `status: str`: status da simulacao;
- `resultado: float | None`: resultado calculado, quando disponivel;
- `meta_alvo: float | None`: alvo de referencia, quando definido;
- `indicadores: dict`: indicadores usados ou retornados pelo simulador;
- `observacoes: list[str]`: limitacoes, avisos e informacoes de validacao.

### ProcessMetaImpactRequest

Entrada do fluxo hibrido de processo + impacto na meta.

Campos:

- `numero_processo: str`: numero do processo a ser avaliado;
- `meta_id: str`: identificador da meta;
- `ano: int`: ano de referencia.

### ProcessMetaImpactResponse

Saida do fluxo hibrido de processo + impacto na meta.

Campos:

- `tipo: str`: tipo da resposta;
- `numero_processo: str`: numero do processo avaliado;
- `meta_id: str`: identificador da meta;
- `ano: int`: ano de referencia;
- `conta_como_novo: bool | None`: indica se ha sinal validado de processo novo;
- `conta_como_julgado: bool | None`: indica se ha sinal validado de julgamento;
- `conta_como_baixado: bool | None`: indica se ha sinal validado de baixa;
- `impacto: str`: classificacao provisoria do impacto;
- `motivo: str`: motivo estruturado da classificacao;
- `observacoes: list[str]`: limitacoes, avisos e pendencias de validacao.

## Endpoints HTTP

### POST /api/processos/chat

Executa o fluxo de chat processual.

Entrada HTTP:

- `session_id: str | None`;
- `mensagem: str`.

Saida HTTP:

- `session_id`;
- `resultado` com os campos de `ProcessualChatResponse`.

Observacoes:

- `rag_status=not_needed` indica que a pergunta foi resolvida sem busca vetorial.
- `rag_status=unavailable` indica que Qdrant ou embedding local nao estavam
  disponiveis, mas o fluxo estruturado continuou.
- `fontes` nao deve expor IDs internos, caminhos de banco, Qdrant ou nomes de
  chunks.

### POST /api/metas/simular

Executa o fluxo de simulacao de metas.

Entrada HTTP:

- `session_id: str | None`;
- `pergunta_usuario: str | None`;
- `meta_id: str`;
- `ano: int`;
- `unidade: str | None`;
- `cenario: dict`.

Saida HTTP:

- `session_id`;
- `resultado` com os campos de `MetaSimulationResponse`;
- `explicacao` gerada pela camada de explicacao.

### POST /api/metas/impacto-processo

Executa o fluxo hibrido de processo + impacto na meta.

Entrada HTTP:

- `session_id: str | None`;
- `pergunta_usuario: str | None`;
- `numero_processo: str`;
- `meta_id: str`;
- `ano: int`.

Saida HTTP:

- `session_id`;
- `resultado` com os campos de `ProcessMetaImpactResponse`;
- `explicacao` gerada pela camada de explicacao.

## Pontos a validar com professores

- formula oficial da Meta 1;
- quais eventos contam como novo;
- quais eventos contam como julgado;
- quais eventos contam como baixado;
- se a interface sera tela separada ou chat unico;
- se o simulador recebera CSV, banco, API ou outro formato;
- se processo individual deve mesmo ser avaliado em relacao a meta.

## Pendencias arquiteturais

- Playwright/coleta real para alimentar a base com processos atuais.
- Extracao de teor integral de documentos para tornar o RAG semanticamente util.
- Frontend visual para chat, processo ativo, fontes e status de coleta/RAG.
- Reranker opcional depois que houver corpus textual maior.
- Aplicar na API a mesma politica de selecao/safe mode usada no chat terminal.
