# Guia de desenvolvimento

## Objetivo

Este guia descreve como preparar o ambiente, executar os componentes e validar
mudanças no estado atual do repositório. Os comandos usam PowerShell e partem da
raiz do projeto, salvo indicação contrária.

## Estrutura de trabalho

- `chatbot_processual_ai/`: backend Python, FastAPI, agentes e serviços;
- `frontend/`: aplicação Angular e testes Vitest;
- `simulador-de-metas/`: anotações iniciais, ainda sem aplicação executável;
- `docs/`: documentação técnica e checklist de integração.

Consulte `AGENTS.md` antes de alterar código. Mudanças devem preservar arquivos
do usuário, baselines e artefatos protegidos.

## Preparação do backend

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

O `.env` é local e ignorado pelo Git. Não coloque valores reais em exemplos,
testes, documentação ou logs.

Variáveis disponíveis:

| Grupo | Variáveis |
|---|---|
| Ollama | `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_MODEL_SELECTION`, `OLLAMA_TEMPERATURE`, `OLLAMA_TIMEOUT_SECONDS` |
| Persistência | `LOCAL_DB_PATH` |
| RAG | `RAG_ENABLED`, `QDRANT_URL`, `QDRANT_COLLECTION`, `OLLAMA_EMBED_MODEL`, `RAG_TOP_K`, `RAG_MIN_SCORE` |

Use `.env.example` como referência canônica de nomes e valores locais seguros.

## Execução do backend

Dentro de `chatbot_processual_ai`:

```powershell
python main.py
python main.py --chat
uvicorn api:app --reload
```

O primeiro comando inicializa a sessão e a base. O chat mantém estado somente
durante o processo atual. A API usa, por padrão, `http://localhost:8000` e
mantém sessões em memória por `session_id`.

Diagnósticos disponíveis:

```powershell
python main.py --diagnose-runtime
python main.py --check-ollama
python main.py --smoke-ollama
python main.py --test-model-policy
```

Esses comandos não devem ser confundidos com a suíte automatizada. O smoke do
Ollama executa geração real e depende do serviço/modelo local.

## Preparação e execução do frontend

```powershell
cd frontend
npm install
npm start
```

Comandos do projeto:

```powershell
npm test
npm run build
npm run watch
```

O servidor de desenvolvimento usa `http://localhost:4200`. Atualmente não há
proxy Angular versionado, e o serviço de chat ainda aponta para `/api/chat`,
enquanto o backend oferece `/api/processos/chat`. Não considere a integração
local pronta até concluir os itens correspondentes da checklist.

`node_modules/`, `.angular/`, `dist/` e cobertura são artefatos locais e devem
permanecer fora do Git. O `package-lock.json` deve ser versionado.

## Banco local e dados de exemplo

Ao consultar a base vazia, o repositório cria o schema SQLite e importa
`chatbot_processual_ai/data/sample_processes.json`. A ingestão é projetada para
ser repetível sem duplicar o processo.

Regras de desenvolvimento:

- não editar `processual.sqlite3` manualmente para ajustar testes;
- não versionar bancos, WAL ou journals;
- manter a amostra sintética e sanitizada;
- executar testes com caminhos temporários quando houver alteração de
  persistência;
- tratar mudanças no schema como alterações de compatibilidade e documentá-las.

## Ollama e Qdrant

Ollama é necessário apenas nos caminhos que efetivamente usam geração ou
embedding. Qdrant é opcional e utilizado como índice vetorial.

Ao trabalhar nessas integrações:

- não baixar modelos automaticamente pelo código;
- diferenciar indisponibilidade, timeout, HTTP inválido e payload inválido;
- preservar o fallback estruturado;
- evitar que testes unitários dependam de serviços locais reais;
- usar mocks nas fronteiras HTTP, não para reproduzir a própria lógica testada.

## Testes

### Backend

Dentro de `chatbot_processual_ai`:

```powershell
python -m unittest discover -s tests -v
```

A suíte atual concentra cobertura em persistência/RAG, sanitização, fallbacks,
roteamento e eventos de progresso. Para uma correção, execute primeiro o teste
focado e depois a suíte do backend.

Os comandos `--test-agent*` são cenários diagnósticos úteis, mas não substituem
automaticamente testes automatizados:

```powershell
python main.py --test-agent1 "Consulte o processo 0011000-82.1981.5.18.0051"
python main.py --test-agent2-sequence
python main.py --test-agent3-sequence
python main.py --test-agent4-sequence --trace
```

### Frontend

Dentro de `frontend`:

```powershell
npm test
npm run build
```

Os testes usam o builder de testes do Angular com Vitest. O build verifica
compilação, templates e limites configurados no `angular.json`.

### Validação documental e do diff

Antes de concluir qualquer mudança:

```powershell
git diff --check
git status --short
git diff
```

Revise alterações acidentais, arquivos gerados, logs temporários, segredos e
mudanças fora do escopo. Não declare um comando como aprovado se ele não foi
executado.

## Convenções arquiteturais

- normalize texto e números processuais nos serviços compartilhados;
- mantenha entrada HTTP separada dos dataclasses internos;
- deixe sequência e captura de falhas nos orquestradores;
- mantenha cálculo e regra de negócio fora de prompts e componentes;
- exponha ao frontend somente contratos sanitizados;
- use status explícitos para integrações indisponíveis ou incompletas;
- preserve análise determinística quando ela puder responder com segurança.

## Alterando contratos

Ao mudar um campo ou endpoint, revise no mínimo:

1. modelo Pydantic em `api.py`;
2. dataclass em `schemas/`;
3. orquestrador e serviço produtor;
4. serialização HTTP com `asdict`;
5. consumidor frontend;
6. testes e documentação.

Breaking changes devem ser documentadas e, quando o risco justificar, migradas
gradualmente.

## Tratamento de erros e logs

Não use fallbacks para transformar erro técnico em sucesso semântico. O
orquestrador processual oferece uma resposta segura e registra a etapa que
falhou. Integrações devem lançar exceções específicas e os limites externos
devem traduzi-las de maneira controlada.

Eventos de progresso não devem conter mensagens do usuário, documentos
pessoais, prompts completos ou respostas brutas de serviços.

## Fluxo recomendado para mudanças

1. leia documentação, contratos, consumidores e testes relacionados;
2. reproduza ou confirme o comportamento atual;
3. implemente a menor mudança coerente;
4. adicione ou ajuste teste focado;
5. execute testes do módulo e regressão proporcional;
6. atualize documentação afetada;
7. revise o diff completo e execute `git diff --check`;
8. registre limitações e falhas ambientais no relatório final.

Não faça commit, push, deploy, download de modelos ou operação em produção sem
autorização explícita.

## Pontos ainda não disponíveis

- integração funcional completa entre frontend e API;
- endpoint de saúde;
- autenticação e autorização;
- persistência ou expiração de sessões da API;
- coleta real via navegador;
- cálculo oficial do simulador de metas;
- pipeline ARIMA executável;
- configuração de deploy de produção.
