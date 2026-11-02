# ADR-001 — Portabilidade seletiva da entrega da Equipe B

- Status: aceito para a integração incremental.
- Data: 23/10/2026.
- Escopo: EB-004 e decisões estruturais das EB-005 a EB-024.

## Contexto

O checkout já possui três componentes canônicos e integrados: `frontend/` (Angular único), `chatbot_processual_ai/` (FastAPI processual, porta 8000) e `simulador_metas_cnj/` (FastAPI de metas, porta 8001). O proxy separa `/api/processos/*` de `/api/simulador/*`; este último remove o prefixo externo e entrega `/api/*` ao simulador.

A entrega em `integracao_entrada/TCC-Simulador-CNJ/` traz funções novas, mas também outro app Angular, chat mock, configurações globais, builds, dados sem proveniência suficiente e dependências Python incompatíveis com o chatbot: FastAPI 0.95.2/Pydantic 1.10.26 contra Pydantic 2+.

## Decisão

1. `frontend/` permanece o único workspace Angular. Componentes e tipos novos serão reimplementados/adaptados nele, sem substituir rotas, proxy, shell ou chat existentes.
2. `simulador_metas_cnj/` permanece o único backend de simulação e recebe, quando os gates matemáticos permitirem, os novos cálculos e endpoints.
3. Os processos Python permanecem separados: chatbot em 8000 e simulador em 8001, com ambientes virtuais próprios.
4. URLs do navegador usam `/api/simulador/*`; as novas rotas internas do simulador usam `/api/meta1/*` e `/api/meta2/*` por causa do rewrite já estabelecido.
5. `POST /api/processos/chat`, `session_id`, tratamento de erro e healthcheck processual são contratos protegidos.
6. A Meta 1 atual não será alterada até comparação numérica. O endpoint quanto-falta será uma extensão isolada.
7. Meta 2 A/ANT será separada das métricas atuais e identificará histórico versus projeção. Constantes e séries importadas não serão apresentadas como dados atuais oficiais.
8. Planilhas, fórmulas, ARIMA e snapshots existentes são somente leitura. Divergências irão para `DIVERGENCIAS_NUMERICAS.md`.
9. A fonte importada continuará ignorada pelo Git e não será modificada.

## Alternativas consideradas

### Substituir frontend e backend pelos importados

Rejeitada: quebraria contratos atuais, introduziria chat fictício, duplicaria aplicação e misturaria configurações/dependências.

### Incorporar o simulador ao processo do chatbot

Rejeitada: as versões de Pydantic/FastAPI são incompatíveis e os domínios têm ciclos de falha e dados distintos.

### Criar um terceiro serviço só para as novidades

Rejeitada por enquanto: o backend canônico do simulador já existe e oferece a fronteira adequada. Um novo serviço exigiria ADR adicional e custo operacional sem benefício demonstrado.

## Consequências e riscos

- O proxy e as portas existentes são preservados; não há colisão de healthcheck.
- Os clientes Angular precisam usar o namespace externo e não copiar `/api/meta2` literalmente.
- Testes do simulador devem provar que a base global não sofre mutação entre requests.
- GATE-M1 e GATE-M2 podem manter recursos ocultos mesmo que contratos/UI estejam preparados.
- Sem Node/npm e pytest disponíveis no ambiente atual, a validação integral fica condicionada à repetição das suítes na EB-022; isso não autoriza reduzir cobertura.
