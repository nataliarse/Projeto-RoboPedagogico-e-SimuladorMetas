# Backend FastAPI

Este diretório é a raiz operacional do backend. Os imports atuais (`api`,
`agents`, `services` etc.) pressupõem que os comandos abaixo sejam executados
de dentro de `chatbot_processual_ai/`.

O bootstrap foi exercitado com Python 3.12.10. O repositório não fixa uma versão
única de Python; essa é a versão observada na validação, não uma restrição nova.

## Preparar o ambiente

Depois de clonar o repositório:

```text
cd chatbot_processual_ai
python -m venv .venv
```

Ative o ambiente virtual no shell utilizado:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# POSIX
source .venv/bin/activate
```

Instale somente as dependências versionadas e crie a configuração local:

```text
python -m pip install -r requirements.txt
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```sh
# POSIX
cp .env.example .env
```

Não sobrescreva um `.env` existente. O arquivo `.env` é local, ignorado pelo Git
e deve ser ajustado conforme os serviços usados; não coloque segredos no
`.env.example`. Todas as variáveis do exemplo possuem defaults no código:
endereços/modelos/timeouts do Ollama, caminho do SQLite e opções do RAG/Qdrant.
O código também lê a chave opcional `AGENT4_USE_OLLAMA` (desabilitada quando
ausente), que ainda não consta no exemplo; ela não é necessária para importar ou
subir a API.

Não versione nem transporte `.venv` entre máquinas ou sistemas operacionais.
Recrie o ambiente com `python -m venv .venv` e `requirements.txt`.

## Dependências externas por cenário

O SQLite é local e inicializado pela aplicação; não exige servidor separado.

| Cenário | Ollama | Qdrant | Observação |
|---|---|---|---|
| `GET /api/health` | Não usado | Não usado | Verifica somente a fronteira FastAPI. |
| Chat básico | Condicional | Não usado nos fluxos estruturados | Regras locais atendem saudações e várias consultas; mensagens não reconhecidas podem consultar o modelo, com fallback seguro se indisponível. |
| Consulta processual estruturada | Não usado no caminho determinístico | Não usado | Consulta a base SQLite local e campos estruturados. |
| RAG/teor de documentos | Necessário para a capacidade semântica completa | Necessário para a capacidade semântica completa | Ollama gera embeddings e Qdrant indexa/busca vetores. Se o RAG estiver desativado ou indisponível, o fluxo registra degradação em `rag_status` e preserva os dados estruturados. |
| Simulação/impacto de metas | Não usado | Não usado | Os endpoints atuais usam regras e contratos locais; o simulador ainda retorna `not_integrated`. |

Subir a API e obter sucesso no healthcheck não comprova que geração, embeddings,
Qdrant ou RAG estejam disponíveis.

## Executar e verificar

Ainda dentro de `chatbot_processual_ai/`, com o venv ativo:

```text
python -m uvicorn api:app --reload
```

A API fica em `http://localhost:8000`. O healthcheck mínimo é:

```text
GET http://localhost:8000/api/health
```

Resposta esperada: HTTP 200 com `{"status":"ok"}`.

O comando oficial da suíte, executado deste mesmo diretório, é:

```text
python -m pytest tests -q
```

Limitação conhecida: no estado atual, `requirements.txt` não declara `pytest`.
Portanto, um venv estritamente reconstruído por esse arquivo executa a API, mas
não executa a suíte acima (`No module named pytest`). Não instale dependências
avulsas e trate o ambiente como reproduzível; a fonte versionada das dependências
de teste precisa ser deliberadamente corrigida em item próprio.

Executar a suíte a partir da raiz do repositório não é equivalente: os imports
atuais falham na coleta. Não use ajustes de `PYTHONPATH`; entre neste diretório.
