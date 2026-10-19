# Smoke local dos três processos

Comando reproduzível: `powershell -File scripts/Test-LocalSmoke.ps1`.

O script inicia processos ocultos e temporários em `127.0.0.1`:

- chatbot FastAPI: 8000;
- simulador FastAPI: 8001;
- Angular dev server/proxy: 4200.

Ollama aponta deliberadamente para uma porta local fechada, o RAG é desabilitado e
nenhuma coleta PJe é iniciada. Todas as chamadas passam pelo frontend:

| Verificação | Evidência de 2026-10-19 |
|---|---|
| `/api/processos/health` | `status=ok` |
| `/api/simulador/health` | `status=ok`, 86 registros |
| `POST /api/processos/chat` | sessão e resposta não vazias |
| `/api/simulador/base` | 86 registros, Meta 1 `109,86` |
| `/` | HTTP 200 e shell Angular |
| `/simulador` | HTTP 200 e shell Angular |

O bloco `finally` encerra somente os PIDs criados pelo próprio roteiro. Após a execução,
as portas 8000, 8001 e 4200 foram verificadas sem listeners remanescentes.
