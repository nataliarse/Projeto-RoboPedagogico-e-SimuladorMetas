# Chatbot Processual AI

## Objetivo atual

Base local para um chatbot processual em Python, com conversa via terminal/API,
estado de sessao em memoria, consulta estruturada em SQLite e base inicial de
RAG local com Qdrant e embeddings via Ollama.

## Estrutura criada

```text
chatbot_processual_ai/
  main.py
  config.py
  model_selector.py
  system_resources.py
  session_state.py
  PROJECT_CONTEXT.md
  README.md
  requirements.txt
  .env.example
  data/
    sample_processes.json
    processual.sqlite3  # gerado localmente e ignorado pelo Git
  agents/
    __init__.py
    agent1_intent.py
    agent2_context_collection.py
    agent3_process_analysis.py
    agent4_response.py
  orchestrators/
    processual_chat_orchestrator.py
    hybrid_orchestrator.py
  prompts/
    __init__.py
  schemas/
    processual_contracts.py
    meta_contracts.py
  services/
    process_repository.py
    process_query_router.py
    rag_retriever.py
    embedding_service.py
    qdrant_vector_store.py
    chunking.py
    meta_*.py
  tests/
    test_rag_base.py
```

## Criar ambiente virtual

```powershell
cd chatbot_processual_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Criar arquivo `.env`

```powershell
Copy-Item .env.example .env
```

## Rodar

```powershell
python main.py
```

## Chat no terminal

```powershell
python main.py --chat
```

Use `sair`, `exit` ou `quit` para encerrar a conversa. Digite `--trace` durante o chat para ligar ou desligar o modo de depuração seguro.

Ao iniciar o chat, o sistema consulta os modelos ja instalados no Ollama e escolhe um modelo local compativel com a RAM disponivel, sem baixar modelos e sem alterar `.env`. Detalhes tecnicos de modelo e recursos aparecem somente no diagnostico ou no modo `--trace`.

## API HTTP

```powershell
uvicorn api:app --reload
```

Endpoints disponiveis:

- `POST /api/processos/chat`
- `POST /api/metas/simular`
- `POST /api/metas/impacto-processo`

O resultado do chat processual inclui os campos principais `intent`,
`resposta`, `processo_ativo`, `collection_status` e `failed_stage`. Tambem
inclui `rag_status` e `fontes`, usados quando a pergunta aciona a camada RAG.

## Base local SQLite + RAG

Por padrao, o projeto usa SQLite em `data/processual.sqlite3` como base
estruturada local. Se o banco nao existir ou estiver vazio, ele e inicializado
automaticamente a partir de `data/sample_processes.json` na primeira consulta.

```env
LOCAL_DB_PATH=./data/processual.sqlite3
RAG_ENABLED=true
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=processual_chunks
OLLAMA_EMBED_MODEL=nomic-embed-text
RAG_TOP_K=5
RAG_MIN_SCORE=0.35
```

O SQLite guarda processos, partes, movimentacoes, documentos, pendencias,
metadados de coleta e chunks canonicos. O Qdrant e usado apenas para busca
vetorial dos chunks. Se Qdrant ou o modelo de embedding do Ollama nao estiverem
disponiveis, o chat continua funcionando com os dados estruturados e informa a
limitacao internamente por `rag_status`.

Com o JSON de exemplo atual, o RAG ainda tem utilidade limitada porque os
documentos trazem metadados, mas nao o teor integral das decisoes.

Status possiveis de RAG no chat:

- `not_needed`: pergunta resolvida por dados estruturados ou fora de RAG.
- `success`: chunks recuperados com sucesso no Qdrant.
- `empty`: nenhum chunk util encontrado.
- `unavailable`: Qdrant/Ollama de embedding indisponivel.
- `error`: falha inesperada controlada na recuperacao.

## Selecao de modelo local

Por padrao, `OLLAMA_MODEL_SELECTION=auto` faz o sistema escolher o melhor modelo instalado que caiba na politica conservadora de RAM disponivel.

```env
OLLAMA_MODEL=llama3.2:1b
OLLAMA_MODEL_SELECTION=auto
```

Para testar um modelo maior manualmente, defina `force`. Nesse modo, o sistema usa `OLLAMA_MODEL` se ele estiver instalado no Ollama, ignorando a politica de RAM e o catalogo oficial.

```env
OLLAMA_MODEL=qwen3:8b
OLLAMA_MODEL_SELECTION=force
```

Use `force` com cuidado: se faltar RAM, o sistema operacional pode ficar lento ou usar disco como memoria.

## Diagnóstico de recursos locais

```powershell
python main.py --diagnose-runtime
```

Esse diagnóstico é voltado a desenvolvimento e exibe RAM, GPU/VRAM quando detectável, modelo configurado e disponibilidade do Ollama. No chat, essas informações aparecem somente quando `--trace` é ativado.

O diagnostico tambem exibe a selecao automatica de modelo recomendada para a execucao atual.

## Teste da politica de modelo

```powershell
python main.py --test-model-policy
```

Esse comando valida cenarios simulados da funcao pura de selecao de modelo. Ele nao chama `ollama pull`, nao baixa modelos e nao altera configuracoes persistentes.

## Testes automatizados

```powershell
python -m unittest discover -s tests -v
```

A suite atual valida:

- criacao e ingestao idempotente no SQLite;
- sanitizacao de CPF/CNPJ e identificadores internos;
- chunking com metadados;
- fallback quando RAG/Qdrant nao esta disponivel;
- mapeamento de retorno vetorial mockado para fontes seguras;
- preservacao do chat estruturado quando a busca semantica falha.

## Validacao do Ollama local

```powershell
python main.py --check-ollama
python main.py --smoke-ollama
```

Use `--check-ollama` para verificar se o servidor local esta acessivel e se o modelo configurado existe. Use `--smoke-ollama` para fazer a mesma verificacao e, em seguida, executar uma geracao minima de texto.

## Teste isolado do Agente 1

```powershell
python main.py --test-agent1 "Consulte o processo 0011000-82.1981.5.18.0051"
```

Esse comando interpreta a intencao inicial da mensagem e exibe um JSON estruturado. Ele ainda nao consulta dados, nao inicia coleta e nao abre uma conversa completa.

O Agente 1 usa uma abordagem hibrida: primeiro aplica regras deterministicas para mensagens claras, como saudacoes, pedidos explicitos de consulta, perguntas sobre processo ativo, duvidas juridicas gerais e pedidos fora de escopo. O Ollama fica como fallback apenas quando essas regras nao classificam a mensagem com seguranca. Mesmo quando o Ollama e usado, a resposta final e validada em Python.

## Teste isolado do Agente 2

```powershell
python main.py --test-agent2 "Consulte o processo 0011000-82.1981.5.18.0051"
python main.py --test-agent2-sequence
```

O Agente 2 usa a saida do Agente 1, controla o processo ativo apenas em memoria,
consulta a base SQLite local por meio do adaptador de processos e aciona a busca
RAG somente quando o roteador deterministico classifica a pergunta como textual
ou hibrida. Ele nao gera resposta final ao usuario.

## Teste isolado do Agente 3

```powershell
python main.py --test-agent3-sequence
```

Esse comando executa Agente 1, Agente 2 e Agente 3 em uma mesma sessao usando uma sequencia fixa de validacao. O Agente 3 produz uma analise estruturada com fatos, explicacao, limitacoes e foco de resposta; ele ainda nao gera a resposta final ao usuario.

## Teste isolado do Agente 4

```powershell
python main.py --test-agent4-sequence
python main.py --test-agent4-sequence --trace
```

O Agente 4 recebe a analise pronta do Agente 3 e cria a mensagem final exibida ao usuario. Ele nao consulta diretamente o processo bruto, nao chama a coleta e nao decide novos fatos.
