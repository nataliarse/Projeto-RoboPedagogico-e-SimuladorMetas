# Robô Pedagógico e Simulador de Metas

Este repositório reúne o Chatbot Processual, sua interface web, a coleta e
normalização de processos do TRT18 e estudos ainda provisórios do Simulador de
Metas. O chat já integra consulta local, coleta sob demanda e persistência; as
regras oficiais do simulador de metas ainda não estão homologadas.

## Módulos

```text
chatbot_processual_ai/  backend FastAPI, orquestrador, agentes, SQLite e testes
entrada-de-dados/       package trt18_collector, coleta e normalização TRT18
frontend/               interface Angular única: chat e simulador
simulador_metas_cnj/    backend FastAPI real do simulador de Metas 1 e 2
docs/                   documentação técnica do produto
```

## Fluxo integrado

```text
consulta → processo ativo ou lookup SQLite
         → miss válido → CollectorAdapter → trt18_collector
         → normalização → persistência → reload SQLite → chatbot
```

O lookup local precede qualquer coleta. Apenas `LOCAL_HIT` e um resultado
externo válido (`COLLECTED`) entregam processo ao chat; o sucesso externo é
persistido e relido do SQLite antes do consumo. Consultas posteriores, inclusive
em outra sessão ou após reinício lógico, reutilizam a persistência. Número
inválido, ausência, resultado parcial, bloqueio e falha mantêm estados distintos
e produzem degradação pública controlada.

O `collector_adapter.py` é a única fronteira do chatbot com o package
`trt18_collector`. O chatbot não consome diretamente o bruto recém-coletado.

## Preparar o ambiente

O fluxo foi validado com Python 3.12.10; o collector declara Python `>=3.10`.
Execute os comandos Python a partir de `chatbot_processual_ai/`, salvo o passo
indicado do package:

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
```

Em shells POSIX, ative com `source .venv/bin/activate` e copie o ambiente com
`cp .env.example .env`. Não sobrescreva um `.env` existente.

Os manifests oficiais são:

- `chatbot_processual_ai/requirements.txt`: runtime FastAPI;
- `chatbot_processual_ai/requirements-dev.txt`: testes;
- `entrada-de-dados/pyproject.toml`: package e extra de coleta;
- `entrada-de-dados/requirements-notebook.txt`: somente pesquisa/notebook.

O extra `collect` instala o package Python do Playwright e as dependências de
OCR; `python -m playwright install chromium` materializa o browser. Por padrão o
coletor usa esse Chromium. `TRT18_COLLECTOR_BROWSER_EXECUTABLE` permite apontar
opcionalmente para outro executável válido; Chrome ou Edge instalados
manualmente não são requisito.

Use [`.env.example`](chatbot_processual_ai/.env.example) como lista canônica das
variáveis suportadas: configuração Ollama, SQLite, RAG/Qdrant e o override
opcional do browser. Não versione `.env`, credenciais ou paths pessoais.

## Executar

Backend, dentro de `chatbot_processual_ai/` e com o venv ativo:

```text
python -m uvicorn api:app --reload
```

A API fica em `http://localhost:8000`; pela UI, `GET /api/processos/health`
comprova somente a fronteira FastAPI. Em outro terminal:

```text
cd frontend
npm ci
npm start
```

A interface fica em `http://localhost:4200`, com chat em `/` e simulador em
`/simulador`. O proxy usa `/api/processos/*` e `/api/simulador/*`. Ollama e
Qdrant são necessários somente para a capacidade RAG
completa; consultas estruturadas continuam usando SQLite.

## Testar

```text
cd chatbot_processual_ai
python -m pytest tests -q

cd ../entrada-de-dados
python -m pytest tests -q

cd ../frontend
npm test -- --watch=false
npm run build
```

As suítes do backend devem ser iniciadas no diretório do backend devido aos
imports atuais. Os testes do collector são offline e usam dados sanitizados.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Ingestão e coleta TRT18](docs/data-ingestion.md)
- [Desenvolvimento local](docs/development.md)
- [Orquestração](docs/orchestration.md)
- [Contrato Angular–FastAPI](docs/integration.md)
- [Filosofia de design](docs/design_philosophy.md)
- [Frontend](frontend/README.md)
- [Backend](chatbot_processual_ai/README.md)

## Limites e segurança

A sessão do backend permanece em memória, sem autenticação ou persistência
distribuída. O portal pode bloquear automação e o CAPTCHA pode impedir a
aquisição; não há retry automático no chatbot. RAG pode degradar sem apagar
fatos estruturados disponíveis. O conteúdo bruto pode conter dados pessoais e
serve à auditoria da aquisição; o repository sanitiza o contrato persistido.
Não versione caches, bancos de runtime, debug, HTML, screenshots ou dados
processuais reais. Use somente exemplos sintéticos ou sanitizados.
