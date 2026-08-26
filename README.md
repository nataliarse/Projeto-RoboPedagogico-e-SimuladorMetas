# Robô Pedagógico e Simulador de Metas

Repositório com duas frentes relacionadas: o **Chatbot Processual**, já acessível
por uma interface Angular integrada a uma API FastAPI, e o **Simulador de
Metas**, cujo domínio ainda contém contratos e estudos provisórios. Eles
compartilham o repositório, mas não devem ser confundidos como uma única
aplicação concluída.

## Estrutura

```text
frontend/                aplicação Angular do Chatbot Processual
chatbot_processual_ai/   backend FastAPI, orquestração, agentes, serviços e testes
simulador-de-metas/      estudos e artefatos próprios do domínio de metas
docs/                    arquitetura, contrato, desenvolvimento e decisões
```

No fluxo web atual, o browser acessa o Angular, que usa HTTP/JSON relativo sob
`/api`. Em desenvolvimento, o servidor Angular encaminha essas chamadas ao
FastAPI por um proxy versionado. O endpoint principal é
`POST /api/processos/chat`; `GET /api/health` verifica somente a disponibilidade
da fronteira FastAPI.

## Começo rápido

Prepare primeiro o backend, em um terminal:

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn api:app --reload
```

Em outro terminal, prepare o frontend:

```powershell
cd frontend
npm ci
npm start
```

A interface fica em `http://localhost:4200` e o FastAPI em
`http://localhost:8000`. Não é necessário codificar o endereço do backend no
frontend nem habilitar CORS para essa topologia local.

Ollama e Qdrant são condicionais: consultas estruturadas usam o SQLite local;
a capacidade semântica completa (RAG) requer embeddings via Ollama e índice no
Qdrant. Consulte o guia de desenvolvimento antes de preparar ou testar o
ambiente. Em particular, `pytest` ainda não é declarado em `requirements.txt`.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Contrato e integração](docs/integration.md)
- [Orquestração](docs/orchestration.md)
- [Desenvolvimento local](docs/development.md)
- [Filosofia de design](docs/design_philosophy.md)
- [Frontend](frontend/README.md)
- [Backend](chatbot_processual_ai/README.md)

## Estado e limites atuais

- a sessão web é identificada por `session_id`, mantida no `sessionStorage` do
  browser e em `_SESSIONS`, na memória do processo Python;
- reiniciar o backend perde o contexto conversacional; não há persistência
  distribuída, autenticação por `session_id` nem deploy de produção definido;
- o histórico recente da interface usa `localStorage` e não substitui a sessão;
- o frontend aplica timeout de 135 s, mas o orçamento total backend planejado de
  120 s não está implementado;
- o simulador de metas ainda não implementa regras oficiais homologadas; os
  endpoints atuais preservam contratos e resultados provisórios.

Não versione `.env`, credenciais, bancos SQLite de runtime, caches, logs,
`node_modules`, `.venv`, builds ou dados processuais reais. Use dados sintéticos
ou sanitizados em exemplos e testes.
