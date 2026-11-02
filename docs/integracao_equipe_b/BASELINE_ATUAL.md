# Baseline funcional antes da integração

Execução local em 23/10/2026, na branch `feat/integracao-equipe-b`, antes de qualquer alteração funcional da Equipe B.

## Ambiente

- Python: 3.12.10.
- `pytest`: indisponível no Python global (`No module named pytest`).
- Ambientes virtuais no workspace: nenhum `pyvenv.cfg` ou `python.exe` local encontrado.
- Node.js/npm: indisponíveis no `PATH`.
- Não houve instalação, download, acesso a rede nem uso de serviço institucional.

## Resultados reais

| Suíte | Comando | Resultado |
|---|---|---|
| Chatbot | `python -m pytest tests -q -p no:cacheprovider` em `chatbot_processual_ai/` | NÃO EXECUTADA: módulo `pytest` ausente; exit 1 |
| Coletor | `python -m pytest tests -q -p no:cacheprovider` em `entrada-de-dados/` | NÃO EXECUTADA: módulo `pytest` ausente; exit 1 |
| Simulador | `python -m unittest discover -s tests -v` em `simulador_metas_cnj/` | APROVADA: 8 testes em 0,698 s |
| Angular | `npm test -- --watch=false` em `frontend/` | NÃO EXECUTADA: `npm` indisponível |
| Proxy | `npm run test:proxy` em `frontend/` | NÃO EXECUTADA: `npm` indisponível |
| Build | `npm run build` em `frontend/` | NÃO EXECUTADO: `npm` indisponível |

A referência histórica de 232 testes + 2 subtestes e build aprovado não é contabilizada como resultado desta execução. O baseline comprovado neste ambiente é somente a suíte de 8 testes do simulador; as demais ficam registradas como limitação ambiental, não como aprovação.

## Contratos e roteamento observados

### Simulador canônico (`simulador_metas_cnj/main.py`)

- `GET /api/health`
- `GET /api/base`
- `POST /api/simular`
- `POST /api/comparar`
- `POST /api/otimizador`

### Chatbot canônico (`chatbot_processual_ai/api.py`)

- `GET /api/health`
- `POST /api/processos/chat`
- `POST /api/metas/simular`
- `POST /api/metas/impacto-processo`

### Proxy Angular (`frontend/proxy.conf.json`)

- `/api/processos/health` → `127.0.0.1:8000/api/health`.
- `/api/processos/*` → `127.0.0.1:8000/api/processos/*`.
- `/api/metas/*` → `127.0.0.1:8000/api/metas/*`.
- `/api/simulador/*` → `127.0.0.1:8001/api/*`, removendo o prefixo externo `/api/simulador`.

O destino dos novos endpoints é, portanto, o backend existente `simulador_metas_cnj/`, com rotas internas `/api/meta1/...` e `/api/meta2/...` e URLs externas `/api/simulador/meta1/...` e `/api/simulador/meta2/...`.

## Critério para comparações posteriores

- Toda mudança no backend deve manter os 8 testes atuais aprovados e acrescentar testes focados.
- Chatbot/coletor/Angular/proxy/build devem ser novamente tentados na EB-022; sem runtime/dependências locais, o GATE-FINAL não poderá ser liberado como integralmente comprovado neste ambiente.
- A ausência de ferramenta não autoriza remover testes, alterar lockfiles ou instalar dependências sem a aprovação operacional aplicável.
