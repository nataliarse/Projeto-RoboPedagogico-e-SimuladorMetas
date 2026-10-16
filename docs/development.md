# Desenvolvimento local

## Pré-requisitos e manifests

O bootstrap foi validado com Python 3.12.10; `trt18_collector` declara Python
`>=3.10`. Use Python 3.12.x para os dois backends, em ambientes virtuais
separados. O frontend foi validado com Node.js 24.19.0, npm 11.x e Angular
21.2.x; `package.json` declara npm 11.11.1, a validação anterior usou 11.17.0
e o lockfile v3 é a fonte reproduzível do grafo Node.

As fontes canônicas de dependências são:

- `chatbot_processual_ai/requirements.txt`: runtime FastAPI;
- `chatbot_processual_ai/requirements-dev.txt`: pytest;
- `entrada-de-dados/pyproject.toml`: package e extra `collect`;
- `entrada-de-dados/requirements-notebook.txt`: pesquisa, fora do runtime.
- `simulador_metas_cnj/requirements.txt`: runtime isolado do simulador;
- `frontend/package-lock.json`: grafo exato do Angular canônico.

## Backend e collector

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
cd ..\entrada-de-dados
python -m pip install -e ".[collect]"
python -m playwright install chromium
cd ..\chatbot_processual_ai
Copy-Item .env.example .env
python -m uvicorn api:app --reload
```

Em POSIX, use `source .venv/bin/activate` e `cp .env.example .env`. Não
sobrescreva nem versione `.env`. A API fica em `http://localhost:8000`; o health
é `GET /api/health` e não verifica collector, SQLite, Ollama ou Qdrant.

O Chromium instalado pelo Playwright é o browser padrão. O override opcional
`TRT18_COLLECTOR_BROWSER_EXECUTABLE` deve apontar para um executável válido.
Não há requisito de Chrome/Edge instalado manualmente.

## Backend do simulador

O simulador precisa de ambiente separado porque preserva FastAPI 0.95.2 e
Pydantic 1.10.26, enquanto o chatbot exige Pydantic 2 ou superior.

```powershell
cd simulador_metas_cnj
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Em POSIX, use `source .venv/bin/activate` e `cp .env.example .env`. A API fica
em `http://127.0.0.1:8001`. Não reutilize a `.venv` do chatbot e não altere as
planilhas em `dados/` durante preparação ou testes.

## Configuração e paths

`.env.example` documenta as variáveis suportadas de Ollama, SQLite, RAG/Qdrant
e browser. `LOCAL_DB_PATH` relativo é resolvido a partir de
`chatbot_processual_ai/`, não do CWD. O default é
`chatbot_processual_ai/data/processual.sqlite3`.

O collector resolve cache, saída e debug a partir de `entrada-de-dados/`:
`data/brutos/`, `data/saida/` e `data/debug/`. A imagem transitória do CAPTCHA
fica sob `data/debug/captcha/`. Não use path pessoal como configuração
documentada.

## Frontend

```text
cd frontend
npm ci
npm start
```

A UI fica em `http://localhost:4200`; `proxy.conf.json` encaminha `/api/*` para
`http://localhost:8000`. Não codifique URL absoluta no cliente.

## Testes e validação offline

```text
cd chatbot_processual_ai
python -m pytest tests -q

cd ../entrada-de-dados
python -m pytest tests -q

cd ../frontend
npm test -- --watch=false
npm run build
npx tsc -p tsconfig.app.json --noEmit

cd ../simulador_metas_cnj
python -c "import main; print(main.health()); print(len(main.get_base()['registros']))"
```

Execute o pytest do backend dentro de `chatbot_processual_ai/`; os imports
atuais pressupõem esse diretório. As suítes do collector são offline e o modo
cache-only não abre browser nem acessa rede. Não rode o notebook com coleta
habilitada como validação rotineira.

## Dependências condicionais e troubleshooting

SQLite não exige servidor. Consultas estruturadas não exigem Ollama/Qdrant; a
capacidade RAG completa exige ambos e degrada por estado explícito quando
indisponível. A coleta externa exige dependências do extra, Chromium instalado,
rede e autorização institucional.

- Browser ausente: execute o comando oficial de instalação; não contorne
  validação TLS ou políticas institucionais.
- HTTP 403/429: interrompa consultas e aguarde; não aumente tentativas.
- Erro de import no pytest: execute no diretório operacional correto.
- Cache ignorado: o bruto não satisfez o critério estrutural e uma nova coleta
  só deve ocorrer de forma consciente/autorizada.

Não versione `.venv`, `.env`, SQLite de runtime, caches, debug, dados reais,
`node_modules`, `.angular/cache/` ou `dist/`. Em máquina limpa, use sempre
`npm ci`, não copie `node_modules` de outra instalação.

Consulte [data-ingestion.md](data-ingestion.md) e
[orchestration.md](orchestration.md).
