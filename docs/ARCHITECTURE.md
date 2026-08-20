# Arquitetura do sistema

## Objetivo e escopo

Este documento descreve a arquitetura existente do Robô Pedagógico e
Simulador de Metas. Ele diferencia comportamento implementado de integrações
opcionais e funcionalidades planejadas.

O repositório contém três fluxos de negócio:

1. chat e consulta processual;
2. simulação de metas;
3. análise provisória do impacto de um processo em uma meta.

O chat processual é o fluxo mais completo. Os contratos de metas existem no
backend, mas o cálculo oficial do simulador ainda não está integrado. O
frontend Angular está em desenvolvimento e ainda não consome o contrato atual
do endpoint processual.

## Visão de contexto

```text
Terminal Python ──────────────┐
                              ├── Orquestração do backend
Frontend Angular (pendente) ──┤         │
                              │         ├── SQLite local
Cliente HTTP ── FastAPI ──────┘         ├── Ollama local
                                        └── Qdrant opcional
```

Não há autenticação, persistência distribuída de sessão, coleta real via
Playwright, LangGraph ou deploy de produção implementados nesta fase.

## Componentes

### Interface Angular

O diretório `frontend/` contém uma aplicação Angular standalone com componentes
de início e chat, serviços de estado, acesso HTTP e armazenamento local. O
estado visual usa signals. O serviço HTTP ainda envia `POST /api/chat`, enquanto
a API atual oferece `POST /api/processos/chat`; portanto, a integração ponta a
ponta não deve ser considerada concluída.

### Entradas do backend

- `main.py`: comandos de terminal, chat interativo, diagnóstico do runtime e
  validações isoladas dos agentes;
- `api.py`: aplicação FastAPI e adaptação dos payloads HTTP aos contratos
  internos;
- `collector_adapter.py`: fachada de consulta ao repositório processual local.

### Orquestradores

- `processual_chat_orchestrator.py`: executa sequencialmente intenção, contexto,
  análise e resposta, emitindo eventos de progresso e convertendo exceções em
  resposta segura;
- `hybrid_orchestrator.py`: localiza um processo e coordena sua avaliação
  provisória em relação a uma meta.

### Agentes do chat processual

- Agente 1 — intenção: extrai número processual e classifica a mensagem. Regras
  determinísticas têm prioridade; Ollama é fallback para casos ambíguos;
- Agente 2 — contexto: mantém o processo ativo, consulta a base, resolve a
  especificação da pergunta, escolhe a rota e aciona RAG quando necessário;
- Agente 3 — análise: produz fatos, foco e limitações. Prefere análise local
  estruturada e usa modelo somente nos casos previstos, com validação e remoção
  de dados pessoais do contexto;
- Agente 4 — resposta: transforma a análise validada em texto para o usuário e
  filtra detalhes internos ou dados pessoais.

Os agentes são funções e módulos especializados, não processos autônomos. A
ordem e o tratamento de falhas pertencem ao orquestrador.

### Persistência estruturada

`services/process_repository.py` gerencia SQLite e cria o schema local. A base
armazena processo, partes, movimentações, documentos, pendências, metadados de
coleta, chunks e execuções de ingestão.

```text
data/sample_processes.json
        │ seed automático quando a base está vazia
        ▼
data/processual.sqlite3
        ├── árvore processual reconstruída
        └── chunks canônicos para recuperação
```

A ingestão substitui os filhos do processo dentro de uma transação e mantém o
número normalizado como identidade lógica. O arquivo SQLite é artefato local e
não é versionado.

### Recuperação semântica

O RAG é uma capacidade opcional composta por:

- `chunking.py`: gera chunks canônicos e metadados;
- `embedding_service.py`: solicita embeddings ao Ollama;
- `qdrant_vector_store.py`: cria coleção, grava e pesquisa pontos;
- `rag_retriever.py`: sincroniza chunks, pesquisa, aplica reranking local e
  devolve fontes sanitizadas;
- `process_query_resolver.py` e `process_query_router.py`: determinam se a
  pergunta é estruturada, semântica, híbrida, fora de escopo ou depende de um
  processo ausente.

Rotas possíveis:

| Rota | Uso | RAG |
|---|---|---|
| `structured` | campos, partes, situação e movimentações estruturadas | não |
| `rag` | teor, fundamento ou conteúdo documental | sim |
| `hybrid` | combinação de fatos estruturados e conteúdo textual | sim |
| `missing_process` | pergunta exige processo ativo inexistente | não |
| `out_of_scope` | assunto fora do domínio processual | não |

Falha em Qdrant ou embeddings não transforma a consulta estruturada em falha.
O contexto RAG registra `not_needed`, `success`, `empty`, `unavailable` ou
`error`, permitindo resposta degradada e observável.

### Ollama e seleção de modelo

`ollama_client.py` encapsula disponibilidade, geração e erros do Ollama.
`model_selector.py` escolhe entre modelos já instalados com base na política de
configuração e nos recursos detectados por `system_resources.py`. O sistema não
baixa modelos automaticamente. O modo forçado pode ultrapassar a política
conservadora de memória e deve ser usado conscientemente.

### Domínio de metas

`schemas/meta_contracts.py` contém contratos independentes para simulação e
impacto processual.

- `meta_simulator_adapter.py` preserva o contrato, mas atualmente retorna
  `status="not_integrated"`, sem resultado ou meta-alvo;
- `process_event_extractor.py` identifica sinais de distribuição, julgamento,
  baixa e arquivamento nos dados disponíveis;
- `meta_rules.py` converte esses sinais em avaliação provisória;
- `meta_explanation_service.py` cria explicações controladas sem afirmar que a
  regra provisória é oficial.

O código atual não implementa fórmulas oficiais, projeções ARIMA ou indicadores
homologados. Os arquivos em `simulador-de-metas/` são anotações de escopo.

## Fluxos de execução

### Chat processual

```text
mensagem + sessão
  → Agente 1: intenção
  → Agente 2: contexto, processo ativo e rota
      → SQLite
      → Ollama/Qdrant, somente se a rota exigir RAG
  → Agente 3: análise validada
  → Agente 4: resposta sanitizada
  → ProcessualChatResponse
```

Cada etapa pode emitir `ProcessProgressEvent`. Uma exceção não tratada dentro
da sequência é capturada pelo orquestrador, que devolve mensagem segura e
identifica `failed_stage`; detalhes técnicos não são enviados como resposta ao
usuário.

### Simulação de metas

```text
MetaSimulationHTTPRequest
  → MetaSimulationRequest
  → simulate_meta
  → MetaSimulationResponse (atualmente not_integrated)
  → explicação controlada
```

### Impacto de processo em meta

```text
ProcessMetaImpactHTTPRequest
  → normalização do número
  → consulta SQLite
  → extração de eventos
  → regras provisórias
  → ProcessMetaImpactResponse
  → explicação controlada
```

## Contratos HTTP

### `POST /api/processos/chat`

Entrada:

```json
{
  "session_id": "opcional",
  "mensagem": "Consulte o processo ..."
}
```

Saída: `session_id` e `resultado`, contendo `tipo`, `intent`, `resposta`,
`processo_ativo`, `collection_status`, `failed_stage`, `rag_status` e `fontes`.

### `POST /api/metas/simular`

Recebe `session_id`, `pergunta_usuario`, `meta_id`, `ano`, `unidade` e
`cenario`. Devolve `resultado` estruturado e `explicacao`. O status atual é
`not_integrated`.

### `POST /api/metas/impacto-processo`

Recebe `session_id`, `pergunta_usuario`, `numero_processo`, `meta_id` e `ano`.
Devolve flags opcionais para novo, julgado e baixado, classificação provisória,
motivo, observações e explicação.

## Estado e concorrência

No terminal, a sessão é um dicionário em memória com conversa, processo ativo e
última intenção. Na API, `_SESSIONS` mantém um dicionário em memória por
`session_id`; quando ausente, usa `default`. Esse desenho é local e
mono-instância: reinícios perdem sessões e múltiplos workers não compartilham
estado. Não há expiração ou limite global de sessões implementado.

## Segurança e privacidade

- `.env`, SQLite local e artefatos de execução são ignorados pelo Git;
- documentos pessoais são removidos do contexto encaminhado ao modelo e da
  resposta visível quando detectados;
- fontes RAG expostas são sanitizadas e não devem revelar IDs internos, caminho
  do banco ou detalhes do Qdrant;
- prompts não são fonte de fatos; saídas de modelo passam por validação;
- dados reais não devem substituir manualmente a amostra versionada.

Essas proteções não substituem autenticação, autorização, criptografia,
auditoria ou avaliação formal de segurança antes de qualquer uso com dados
reais.

## Configuração

As variáveis documentadas em `chatbot_processual_ai/.env.example` controlam
URL, modelo, timeout e temperatura do Ollama; caminho SQLite; habilitação e
parâmetros do Qdrant/RAG. Caminhos relativos são resolvidos pelo backend em
relação ao projeto do chatbot.

## Limitações e evolução planejada

- alinhar o frontend ao endpoint e ao envelope de resposta atuais;
- configurar proxy de desenvolvimento e estratégia de mesma origem/CORS;
- adicionar endpoint de saúde e política de sessões para uso não local;
- implementar coleta real e governança de dados de origem;
- disponibilizar teor documental suficiente para elevar a utilidade do RAG;
- validar fórmulas, eventos e indicadores oficiais das metas;
- implementar o simulador e, se aprovado, os modelos ARIMA;
- definir autenticação, persistência de sessão, observabilidade e implantação;
- ampliar testes de API, integração frontend/backend e regras de metas.

## Decisões que exigem validação de negócio

- fórmula e população oficial de cada meta;
- eventos que contam como novo, julgado ou baixado;
- fonte, periodicidade e qualidade dos dados do simulador;
- significado aceitável de impacto de um processo individual na meta;
- forma de apresentação e advertências dos resultados provisórios.

Veja também [filosofia de design](design_philosophy.md),
[desenvolvimento](development.md) e [orquestração](orchestration.md).
