# Desenvolvimento local

## Pré-requisitos

- Python 3.12.10 foi a versão validada; o projeto não fixa uma única versão.
- Node.js 24.19.0 e npm 11.17.0 foram validados com Angular 21.2.x.
- Ollama e Qdrant são condicionais à capacidade: não são usados pelo health nem
  pelo caminho estruturado; RAG completo exige ambos.
- A coleta ao vivo requer um navegador compatível, Playwright/Chromium e
  autorização institucional para consultar o PJe e processar o CAPTCHA.

## Backend

Os imports pressupõem execução dentro de `chatbot_processual_ai/`.

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn api:app --reload
```

Não sobrescreva `.env` existente nem versione seu conteúdo. `.env.example`
documenta SQLite, Ollama e Qdrant sem segredos. A API fica em
`http://localhost:8000`; `GET /api/health` valida apenas a fronteira FastAPI.

Testes, ainda desse diretório:

```text
python -m pytest tests -q
```

Limitação conhecida: `requirements.txt` cobre runtime, mas não declara
`pytest`. Um venv reconstruído somente por esse arquivo sobe a API, porém não
executa a suíte sem que pytest já esteja disponível. Executar a suíte a partir
da raiz também não é equivalente por causa dos imports atuais; não masque isso
com `PYTHONPATH`.

## Frontend

```text
cd frontend
npm ci
npm start
```

Validação:

```text
npm test -- --watch=false
npm run build
npx tsc -p tsconfig.app.json --noEmit
```

Use `npm ci`, não reutilize `node_modules` recebido de outra máquina/SO e não
altere o lockfile no bootstrap normal.

## Entrada de dados do TRT18

As dependências Python foram centralizadas no arquivo do backend. Para preparar
o módulo e instalar o navegador do Playwright:

```powershell
cd chatbot_processual_ai
python -m pip install -r requirements.txt
python -m playwright install chromium
cd ..\entrada-de-dados
```

Consulta somente com cache, sem acesso externo:

```powershell
python app.py 0011000-82.1981.5.18.0051 --so-cache
```

Validação offline com o exemplo sanitizado:

```powershell
python -c "import json; from pathlib import Path; from normalizador import normalizar; bruto=json.loads(Path('exemplos/exemplo_bruto.json').read_text(encoding='utf-8')); print(normalizar(bruto).model_dump_json(indent=2))"
```

Não execute o notebook com `COLETAR_AGORA = True` por padrão: isso inicia a
coleta em lote e pode acionar os limites do portal. Para detalhes de execução,
cache, status e privacidade, consulte [data-ingestion.md](data-ingestion.md).

## Execução integrada e rede

1. Suba o FastAPI em `localhost:8000`.
2. Suba o Angular em `localhost:4200`.
3. Abra `http://localhost:4200`.

O browser chama `/api/...`; o dev server usa `proxy.conf.json` para encaminhar
ao backend. Não codifique `http://localhost:8000` no frontend. CORS é
desnecessário localmente. Produção prefere mesma origem; uma futura separação de
origens exigirá allowlist configurável, não wildcard.

## Git e artefatos

Trabalhe na branch autorizada da tarefa, preserve alterações preexistentes e
mantenha commits focados. Não versione:

- `node_modules/`, `.angular/cache/`, `dist/`;
- `.venv/`, `__pycache__/`, `.pytest_cache/`;
- `.env`, bancos SQLite e outputs/logs de runtime;
- credenciais, dados reais ou artefatos de baseline modificados.

## Troubleshooting

- **`node`/`npm` não encontrado:** instale runtime compatível e confirme o
  `PATH`; não transporte binários ou `node_modules` de outro sistema operacional.
- **pytest não encontrado:** é a lacuna conhecida de dependência de
  desenvolvimento; não afirme que `requirements.txt` sozinho cobre testes.
- **erro de import no pytest:** entre em `chatbot_processual_ai/` antes do
  comando.
- **Angular abre, API falha:** confirme FastAPI em `:8000` e Angular em `:4200`;
  chamadas do browser devem continuar relativas e passar pelo proxy.
- **RAG degradado:** verifique Ollama, modelo de embeddings, Qdrant e `.env`
  somente quando a consulta exigir capacidade semântica.
- **cache da coleta ignorado:** o bruto existe, mas não contém uma resposta com
  `itensProcesso`, `poloAtivo` ou `poloPassivo`; use `--so-cache` para impedir
  acesso ao portal ou autorize conscientemente uma nova coleta.
- **HTTP 403/429 no PJe:** interrompa as consultas e aguarde; não aumente
  tentativas nem reduza intervalos para contornar a limitação.

Veja também [integration.md](integration.md) e os READMEs específicos de
[frontend](../frontend/README.md) e [backend](../chatbot_processual_ai/README.md).
