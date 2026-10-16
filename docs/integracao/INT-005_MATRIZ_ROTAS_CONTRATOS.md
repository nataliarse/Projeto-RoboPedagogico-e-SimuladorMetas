# INT-005 — Matriz de rotas e contratos HTTP

## Serviço processual — porta atual 8000

| Método e rota | Request | Resposta 200 | Erros/status | Dependências e observações |
|---|---|---|---|---|
| `GET /api/health` | Sem corpo | `{status: string}` | Falha não tratada: 500 | Verifica somente a fronteira FastAPI; colide nominalmente com o health do simulador |
| `POST /api/processos/chat` | `{mensagem: string não vazia, session_id?: string|null}` | `{session_id, resultado}`; `resultado` contém `tipo`, `intent`, `resposta`, `processo_ativo`, `collection_status`, `failed_stage`, `rag_status`, `fontes` | Schema inválido: 422; falha não tratada: 500; falhas esperadas de coleta/RAG podem ser representadas semanticamente dentro de uma resposta 200 | Sessão em `_SESSIONS`, somente memória; pode usar SQLite, collector, Ollama e Qdrant conforme a pergunta |
| `POST /api/metas/simular` | `{session_id?, pergunta_usuario?, meta_id, ano, unidade?, cenario?: object}` | `{session_id, resultado: MetaSimulationResponse, explicacao}` | Schema inválido: 422; falha não tratada: 500 | Adapter atual pode responder `not_integrated`; não é o motor real do simulador |
| `POST /api/metas/impacto-processo` | `{session_id?, pergunta_usuario?, numero_processo, meta_id, ano}` | `{session_id, resultado: ProcessMetaImpactResponse, explicacao}` | Schema inválido: 422; falha não tratada: 500 | Orquestração híbrida existente; não substituir regras do simulador importado |

### Contrato do resultado do chat

```text
tipo: "processual_chat"
intent: string|null
resposta: string
processo_ativo: string|null
collection_status: string|null
failed_stage: string|null
rag_status: string|null
fontes: array
```

O frontend atual aplica timeout de 135 segundos e persiste/reenvia `session_id`. O proxy atual encaminha todo `/api` para `http://localhost:8000`.

## Serviço do simulador — porta alvo 8001

| Método e rota | Request | Resposta 200 | Erros/status | Dependências e observações |
|---|---|---|---|---|
| `GET /api/health` | Sem corpo | `{status: "ok", registros: number}` | Falha de inicialização/dados: processo não sobe; falha não tratada: 500 | Carrega as quatro planilhas na inicialização; colide nominalmente com o health processual |
| `GET /api/base` | Sem corpo | `{registros: RegistroApi[], meta1_final: number|null, meta2_final: number|null}` | Falha não tratada: 500 | Calcula sobre `BASE_GLOBAL` carregada das planilhas |
| `POST /api/simular` | `{alteracoes?: Record<YYYY-MM, {julgados?: int, dessobrestados?: int, suspensos?: int}>}` | Mesmo envelope de `/api/base` | Campo extra, tipo/mês inválido ou fora da base: 422; falha não tratada: 500 | Inteiros são estritos; campos extras do request principal e de alteração são proibidos |
| `POST /api/comparar` | `{cenarios: [{nome: string, alteracoes?: Record<YYYY-MM, AlteracaoMes>}]}` | `{cenarios: [{nome, meta1_final, meta2_final, dif_meta1, dif_meta2, mensal}], meta1_base, meta2_base}` | Schema/mês inválido: 422; falha não tratada: 500 | `CenarioItem` não proíbe explicitamente campos extras no snapshot |
| `POST /api/otimizador` | `{variavel?: string, mes?: string, meta_alvo?: number, meta?: string}` | `{variavel, mes, meta_alvo, meta_atual, incremento_necessario, meta_resultante, mensagem, ok}` | Variável ou meta rejeitada explicitamente: 400; schema inválido: 422; mês pode produzir resposta de domínio ou falha interna conforme motor | Defaults: `julgados`, `2026-06`, `100.0`, `meta1` |

`RegistroApi` contém `data`, `ano`, `mes`, valores mensais, tipos de dado, acumulados e `meta1/meta2`. O frontend converte `previsao_sas` para `forecast` e remove `ano/mes` do modelo de apresentação.

O cliente Angular importado não define timeout para `base`, `simular` ou `otimizador`. Também não possui método HTTP para `/api/comparar`. Seu proxy atual encaminha apenas `/api/base`, `/api/simular` e `/api/health` para `127.0.0.1:8001`; `/api/comparar` e `/api/otimizador` não estão cobertos.

## Chat do frontend importado

| Chamada | Contrato atual | Divergência |
|---|---|---|
| `POST /api/chat` | Envia somente `{mensagem}`; resposta não tipada (`any`); timeout de 60 segundos | A rota não existe em nenhum backend; o contrato real exige consumo de `resultado.resposta` e suporte a `session_id`; o proxy não encaminha a chamada |

Além disso, o componente importado ignora a resposta tanto no sucesso quanto no erro e apresenta uma mensagem mock.

## Colisões e decisão requerida

1. Ambos os serviços publicam `GET /api/health`; um proxy único baseado apenas no prefixo `/api` é ambíguo.
2. O frontend importado usa `/api/chat`, enquanto o backend real usa `/api/processos/chat`.
3. O backend processual também possui `/api/metas/*`, mas esse adapter provisório não corresponde às rotas nem ao motor real do simulador.
4. O destino recomendado para o próximo ADR é preservar `/api/processos/*` no backend processual e rotear explicitamente as rotas reais do simulador, com healthchecks distintos.

## Timeouts conhecidos

| Camada | Valor |
|---|---:|
| Chat Angular atual | 135 s |
| Chat Angular importado | 60 s |
| Ollama no backend processual | 60 s por padrão, configurável |
| Qdrant no backend processual | 10 s |
| Serviços Angular do simulador | Sem timeout explícito |
| FastAPI/Uvicorn | Sem timeout de aplicação explícito nestes módulos |

## Validação

A matriz foi confrontada com decoradores FastAPI, modelos Pydantic/dataclasses, clientes Angular, proxies e OpenAPI gerada localmente para o simulador. A OpenAPI confirma 200 e 422 automáticos, mas os endpoints não declaram modelos de resposta; por isso os schemas de saída acima derivam do código e devem ser formalizados nos itens `INT-012` e `INT-013`.
