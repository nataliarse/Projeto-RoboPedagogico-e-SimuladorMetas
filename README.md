# Chatbot Juridico Informativo com Ollama

Prova de conceito em Python para validar um fluxo sequencial de chatbot juridico
informativo com agentes simulados, Ollama local e contratos JSON entre etapas.

O projeto nao e um sistema pronto para producao. Ele nao substitui orientacao de
advogado, nao promete resultado juridico, nao inventa leis, nao inventa prazos e
nao afirma decisao que nao esteja nos dados recebidos ou mockados.

## Estrutura

`legal_chatbot_ai/` e a implementacao oficial. Os arquivos da raiz ficam apenas
como suporte de execucao e configuracao.

```text
main.py
requirements.txt
.env.example
legal_chatbot_ai/
|-- main.py
|-- orchestrator.py
|-- config.py
|-- agents/
|-- collection/
|-- llm/
|-- utils/
`-- docs/
```

## Requisitos

- Python 3.10+
- Ollama instalado e rodando localmente
- Um modelo disponivel no Ollama, por exemplo:

```powershell
ollama pull llama3.2:1b
```

## Configuracao

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e ajuste se necessario:

```powershell
Copy-Item .env.example .env
```

Configuracoes suportadas:

```env
OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEMPERATURE=0.2
DEBUG_MODE=true
```

## Execucao

Modo principal pela raiz:

```powershell
python main.py
```

Modo canonico pelo pacote:

```powershell
python -m legal_chatbot_ai.main
```

## Fluxo

```text
Usuario digita mensagem
-> user_input_agent
-> context_agent
-> se REQUEST_COLLECTION:
     utils/process_number.py
     collection/collection_router.py
     collection/mock_process_tree.py
-> legal_reasoning_agent
-> response_agent
-> resposta final
```

Todos os modulos trocam dados por contratos JSON representados como `dict`.
Nesta versao, a coleta de processo e mockada e nao consulta fontes oficiais.
