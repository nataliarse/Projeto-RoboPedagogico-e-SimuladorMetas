# INT-009 — Matriz de ambiente reproduzível

| Componente | Runtime suportado | Manifest/lock | Isolamento |
|---|---|---|---|
| Chatbot processual | Python 3.12.x (validado em 3.12.10) | `requirements.txt`, `requirements-dev.txt` | `.venv` própria em `chatbot_processual_ai/` |
| Collector | Python `>=3.10`, executado no ambiente do chatbot | `entrada-de-dados/pyproject.toml` com extra `collect` | Instalado editável na `.venv` do chatbot |
| Simulador CNJ | Python 3.12.x | `simulador_metas_cnj/requirements.txt`, com versões exatas | `.venv` exclusiva em `simulador_metas_cnj/` |
| Frontend único | Node.js 24.19.0; npm 11.x; Angular 21.2.x | `frontend/package-lock.json` v3 | `node_modules` reconstruído por `npm ci` |

Os ambientes Python não podem ser fundidos: chatbot/collector requerem Pydantic 2+, enquanto o simulador preserva Pydantic 1.10.26 e FastAPI 0.95.2. Os comandos completos para PowerShell e as equivalências POSIX estão em `docs/development.md`.

Nenhuma instalação foi realizada durante este item. A validação em máquina limpa deve usar os manifests versionados, sem copiar `.venv` ou `node_modules`, e deve executar os comandos de teste registrados no `INT-004`.
