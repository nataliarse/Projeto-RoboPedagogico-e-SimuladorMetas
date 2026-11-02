# Guia local — integração do Simulador de Metas

## Ambientes e portas

Use ambientes Python separados: o chatbot requer Pydantic 2, enquanto o simulador fixa Pydantic 1.10.26. Não instale os dois backends no mesmo ambiente.

```powershell
# Terminal 1 — chatbot, porta 8000
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m uvicorn api:app --reload --port 8000

# Terminal 2 — simulador, porta 8001
cd simulador_metas_cnj
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Terminal 3 — Angular, porta 4200
cd frontend
npm ci
npm start
```

A interface fica em `http://localhost:4200`: chat em `/` e simulador em `/simulador`. O proxy encaminha `/api/processos/*` para 8000 e remove `/api/simulador` antes de encaminhar ao backend da porta 8001.

## Rotas do protótipo

- Meta 1: `GET /api/simulador/base`, `POST /simular`, `/comparar`, `/otimizador` e `/meta1/quanto-falta`.
- Meta 2: `GET /api/simulador/meta2/base` e `POST /api/simulador/meta2/simular`.
- Chat: `POST /api/processos/chat`; reutilize o `session_id` retornado para preservar o contexto.
- Saúde: `/api/processos/health` e `/api/simulador/health` são independentes.

## Validação offline

```powershell
cd simulador_metas_cnj
python -m unittest discover -s tests -v

cd ..\frontend
npm test -- --watch=false
npm run test:proxy
npm run build

# Em seus ambientes isolados próprios:
cd ..\chatbot_processual_ai
python -m pytest tests -q -p no:cacheprovider
cd ..\entrada-de-dados
python -m pytest tests -q -p no:cacheprovider
```

## Limites

Os resultados são estimativas de um protótipo de apoio à decisão, não homologação do CNJ nem garantia institucional. As séries A/ANT incluem projeções estáticas identificadas na UI; `null` significa resultado não calculável e nunca deve ser convertido em zero. Não altere planilhas, fórmulas, parâmetros ou snapshots para ajustar resultados. Testes e smoke locais não validam produção, scraping, PJe, AWS, Ollama ou Qdrant.
