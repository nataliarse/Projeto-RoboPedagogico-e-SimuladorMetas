# Robô Pedagógico e Simulador de Metas

Repositório integrado para o desenvolvimento de uma solução de apoio à análise
processual e à simulação de metas. O projeto reúne um backend local em Python,
uma API HTTP, uma interface Angular em evolução e os estudos iniciais do
simulador de metas.

## Estado atual

- O chatbot processual funciona pelo terminal e pela API FastAPI.
- Os dados estruturados são armazenados localmente em SQLite e inicializados a
  partir de uma base de exemplo.
- A busca semântica com Qdrant e embeddings do Ollama é opcional; a consulta
  estruturada continua disponível quando esses serviços não estão acessíveis.
- O backend expõe contratos iniciais para simulação de metas e análise do
  impacto de um processo em uma meta.
- O frontend Angular possui telas e serviços iniciais, mas sua integração com o
  contrato atual da API ainda está em andamento.
- Os modelos e regras oficiais do simulador de metas ainda precisam ser
  implementados e validados.

## Arquitetura resumida

```text
Usuário
  ├── Frontend Angular (em integração)
  ├── Chat no terminal
  └── API FastAPI
          ├── Chat processual
          │     ├── agentes de intenção, contexto, análise e resposta
          │     ├── SQLite (dados estruturados)
          │     └── Ollama + Qdrant (RAG opcional)
          ├── Simulador de metas
          └── Análise de impacto processo × meta
```

A LLM é usada para interpretação e explicação. Fatos, validações e cálculos
devem permanecer em regras determinísticas e contratos estruturados. Consulte
[a documentação de arquitetura](docs/ARCHITECTURE.md) para os fluxos e
responsabilidades detalhados.

## Estrutura do repositório

```text
.
├── chatbot_processual_ai/   # backend Python, API, agentes e testes
├── frontend/                # aplicação Angular
├── simulador-de-metas/      # estudos iniciais do simulador e modelos ARIMA
├── docs/                    # arquitetura, desenvolvimento e planejamento
├── .gitignore               # regras unificadas do repositório
└── README.md                # documentação principal do projeto
```

## Pré-requisitos

- Python compatível com a sintaxe e as dependências de `requirements.txt`;
- Node.js e npm compatíveis com o `package-lock.json` do frontend;
- Ollama, para os recursos que utilizam modelo local;
- Qdrant, opcionalmente, para a busca vetorial.

O SQLite é criado localmente pela aplicação e não exige um servidor separado.

## Backend e chatbot processual

### Instalação

No PowerShell:

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

O arquivo `.env` é local e não deve ser versionado. Ajuste nele os endereços e
modelos do Ollama e do Qdrant quando necessário.

### Execução pelo terminal

```powershell
python main.py
python main.py --chat
```

Use `sair`, `exit` ou `quit` para encerrar o chat. Durante a conversa, `--trace`
alterna a exibição de detalhes seguros de diagnóstico.

### API HTTP

Dentro de `chatbot_processual_ai`, execute:

```powershell
uvicorn api:app --reload
```

Por padrão, a API fica disponível em `http://localhost:8000`. Endpoints atuais:

- `POST /api/processos/chat` — conversa e consulta processual;
- `POST /api/metas/simular` — contrato inicial de simulação de metas;
- `POST /api/metas/impacto-processo` — análise provisória de processo × meta.

### SQLite e RAG opcional

Na primeira consulta, a aplicação cria `data/processual.sqlite3` a partir de
`data/sample_processes.json` caso a base esteja ausente ou vazia. O arquivo do
banco é local e ignorado pelo Git.

O Qdrant funciona somente como índice semântico dos trechos; o SQLite continua
sendo a fonte estruturada. Se Qdrant ou o modelo de embeddings não estiverem
disponíveis, o fluxo utiliza os dados estruturados e registra a limitação em
`rag_status`.

### Diagnósticos e validações locais

```powershell
python main.py --diagnose-runtime
python main.py --check-ollama
python main.py --smoke-ollama
python main.py --test-model-policy
python main.py --test-agent1 "Consulte o processo 0011000-82.1981.5.18.0051"
python main.py --test-agent2 "Consulte o processo 0011000-82.1981.5.18.0051"
python main.py --test-agent2-sequence
python main.py --test-agent3-sequence
python main.py --test-agent4-sequence --trace
```

## Frontend Angular

Em outro terminal:

```powershell
cd frontend
npm install
npm start
```

A interface de desenvolvimento fica em `http://localhost:4200`. Outros comandos:

```powershell
npm test
npm run build
npm run watch
```

O build é gravado em `frontend/dist/`, que é ignorado pelo Git.

> **Atenção:** o serviço atual do frontend ainda usa `POST /api/chat`, enquanto
> o backend expõe `POST /api/processos/chat`. Proxy, adaptação do contrato e
> tratamento da resposta fazem parte da checklist de integração e precisam ser
> concluídos antes de executar o fluxo completo pelo navegador.

## Simulador de metas

O diretório `simulador-de-metas/` registra o escopo inicial para uma interface
de simulação e estudos com modelos ARIMA. A API já oferece contratos para
simulação e impacto processual, mas fórmulas, indicadores, modelos e critérios
oficiais ainda dependem de implementação e validação com os responsáveis pelo
negócio.

Até essa validação, resultados provisórios não devem ser tratados como regra
oficial de metas.

## Testes

Backend, a partir de `chatbot_processual_ai`:

```powershell
python -m unittest discover -s tests -v
```

Frontend, a partir de `frontend`:

```powershell
npm test
```

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Desenvolvimento](docs/development.md)
- [Filosofia de design](docs/design_philosophy.md)
- [Orquestração](docs/orchestration.md)
- [Checklist de integração](docs/CHECKLIST_INTEGRACAO_CHATBOT_FRONTEND.md)

## Segurança e dados locais

- Nunca versione `.env`, chaves, certificados ou credenciais.
- Não versione bancos SQLite, caches, logs, `node_modules` ou builds.
- Use dados sintéticos ou sanitizados em exemplos e testes.
- `chatbot_processual_ai/data/sample_processes.json` é a amostra versionável;
  dados processuais reais devem permanecer fora do repositório.

## Equipe

O projeto reúne as frentes do robô pedagógico e do simulador de metas, com
participação de Letícia, Natália, Simone, Giuliano, Leonardo, Filipe, Mateus e
Nicole.
