# Chatbot Processual AI

## Objetivo atual

Base inicial para um chatbot processual local em Python, preparado para evoluir para uma camada de IA e conversa usando Ollama. Nesta fase, o projeto apenas inicializa a estrutura e o estado de sessao.

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
  agents/
    __init__.py
  prompts/
    __init__.py
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

O Agente 2 usa a saida do Agente 1, controla o processo ativo apenas em memoria e le somente o JSON local de exemplo em `data/sample_processes.json`. Ele nao gera resposta final ao usuario e nao chama Ollama.

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
