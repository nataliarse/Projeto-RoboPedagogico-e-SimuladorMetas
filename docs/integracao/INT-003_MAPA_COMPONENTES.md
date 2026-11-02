# INT-003 — Mapa de aplicações e componentes

Este inventário descreve o estado observado. “Candidato” não autoriza remoção; decisões de arquitetura pertencem ao `INT-006`.

## Aplicações executáveis

| Caminho | Função atual | Entrada/configuração | Destino candidato |
|---|---|---|---|
| `chatbot_processual_ai/` | Backend processual, agentes, sessão, persistência e adapter de coleta | `api.py` (`api:app`), `main.py`, `requirements*.txt` | Preservar como serviço processual |
| `entrada-de-dados/` | Package `trt18_collector`, normalização e coleta | `pyproject.toml`; consumido pelo adapter do chatbot | Preservar como dependência do serviço processual |
| `frontend/` | Angular atual do chatbot processual | `angular.json`, `package.json`, `src/main.ts` | Manter como baseline até decisão do Angular canônico |
| `integracao_entrada/TCC-Simulador-CNJ/backend/` | FastAPI e motor de cálculo do simulador | `main.py` (`main:app`), `requirements.txt`, `robo_cnj_meta2.py` | Migrar ou promover como serviço de metas, sem alterar fórmulas |
| `integracao_entrada/TCC-Simulador-CNJ/frontend/meu-primeiro-app/src/` | Fonte Angular com chat, simulador, gráficos e cenários | `src/main.ts`, `app.routes.ts`; o diretório tem `package.json` | Principal candidato visual, condicionado à restauração da configuração Angular |

## Módulos relevantes

| Caminho | Responsabilidade observada | Observação/destino candidato |
|---|---|---|
| `chatbot_processual_ai/agents/` | Extração, contexto, resposta e validação dos fluxos processuais | Preservar |
| `chatbot_processual_ai/orchestrators/` | Orquestração do chat e impacto de processo em metas | Preservar; integração real de metas é fase posterior |
| `chatbot_processual_ai/services/meta_simulator_adapter.py` | Adapter provisório de metas | Não tratar `not_integrated` como cálculo real |
| `chatbot_processual_ai/schemas/` | Contratos internos de processo e metas | Referência para contratos integrados |
| `frontend/src/app/features/chat/` | Chat Angular já conectado a `/api/processos/chat` | Baseline funcional do chat |
| `frontend/src/app/core/` | Modelos e serviços tipados do chat | Fonte de compatibilidade para o frontend unificado |
| `integracao_entrada/.../src/app/features/simulador/` | Shell que compõe cenários e gráficos | Candidato a compor a UI unificada |
| `integracao_entrada/.../src/app/features/{cenarios,graficos,tabela,otimizador}/` | Funcionalidades visuais do simulador | Preservar e testar antes do transporte |
| `integracao_entrada/.../src/app/core/services/simulador-api.service.ts` | Cliente HTTP do simulador | Candidato à integração, após formalização do contrato |
| `integracao_entrada/.../backend/dados/*.xlsx` | Séries agregadas usadas pelo simulador | Baseline somente leitura |

## Configurações e scripts

| Caminho | Papel | Achado |
|---|---|---|
| `frontend/angular.json` | Workspace Angular atual | Único `angular.json` presente no repositório |
| `frontend/package.json` | Scripts `start`, `build` e `test` | Angular 21.2; configuração executável existente |
| `frontend/proxy.conf.json` | Proxy local do frontend atual | Encaminha `/api` ao backend processual em `localhost:8000` |
| `integracao_entrada/.../package.json` | Scripts Angular recebidos | Declara `ng serve/build/test`, mas falta `angular.json` no snapshot |
| `integracao_entrada/.../proxy.conf.json` | Proxy recebido | Encaminha somente `base`, `simular` e `health` ao simulador em `127.0.0.1:8001` |
| `deploy/` | Artefatos de implantação existentes | Fora do escopo até a fase de entrega; sem execução automática |

## Duplicatas exatas confirmadas

- Entre `frontend/` e o Angular importado: `.editorconfig`, `.prettierrc`, `tsconfig.app.json`, `tsconfig.json`, `tsconfig.spec.json`, `favicon.ico`, `app.config.ts` e `app.css`.
- Dentro do snapshot importado: `dados.service.ts` e `tabela.component.ts` são idênticos entre a árvore principal e `simulador-metas/`.
- As duplicatas foram identificadas por SHA-256; nenhuma foi removida.

## Árvores incompletas e candidatos a código inativo

- `integracao_entrada/.../simulador-metas/` possui apenas `src/` e `LEIAME.md`, sem `angular.json`, `package.json` ou `tsconfig`; não é uma aplicação Angular autônoma no estado recebido.
- O próprio `meu-primeiro-app` importado também não contém `angular.json`, embora declare scripts `ng`; não pode ser executado isoladamente sem reconstruir ou reaproveitar uma configuração de workspace.
- `integracao_entrada/.../components/home/` não aparece nas rotas nem em imports de produção; é candidato a scaffold não utilizado.
- `simulador-de-metas/` na raiz contém somente dois textos extensionless de intenção (`estrutura-simulador` e `modelos-arima`), não uma aplicação executável.
- A árvore parcial `simulador-metas/` e os componentes duplicados são candidatos a fonte histórica, mas só poderão ser classificados como mortos depois da escolha canônica e da comparação funcional do `INT-006`/`INT-025`.

## Conclusão

Existem duas aplicações executáveis comprovadas no baseline atual (backend processual e Angular da raiz), um backend de simulador importado e uma fonte Angular importada incompleta como workspace. O mapa preserva todos os candidatos e fornece a base para os baselines (`INT-004`), matriz de rotas (`INT-005`) e ADR (`INT-006`).
