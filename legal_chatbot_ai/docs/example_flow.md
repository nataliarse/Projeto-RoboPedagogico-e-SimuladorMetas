# Fluxo do prototipo

## 1. Objetivo

Este prototipo demonstra uma arquitetura simples de chatbot juridico
informativo com agentes simulados, Ollama local e contratos JSON entre etapas.

O objetivo nao e criar um sistema pronto para producao, mas validar o fluxo
sequencial e a separacao de responsabilidades.

## 2. O que ele faz

- Recebe uma mensagem pelo terminal.
- Organiza a entrada do usuario em JSON.
- Usa Ollama para decidir a proxima acao.
- Valida numero de processo no codigo, sem confiar cegamente no LLM.
- Retorna dados mockados quando a consulta simulada e aplicavel.
- Usa Ollama para organizar raciocinio informativo.
- Usa Ollama para gerar uma resposta final clara.

## 3. O que ele nao faz

- Nao consulta sites reais.
- Nao faz scraping.
- Nao implementa Playwright real.
- Nao acessa base oficial de tribunal.
- Nao usa banco de dados.
- Nao tem frontend.
- Nao tem autenticacao.
- Nao promete resultado juridico.

## 4. Estrutura oficial

```text
main.py
requirements.txt
.env.example
legal_chatbot_ai/
|-- main.py
|-- orchestrator.py
|-- config.py
|-- llm/
|-- agents/
|-- collection/
|-- utils/
`-- docs/
```

- `main.py` da raiz: wrapper para `legal_chatbot_ai.main.main`.
- `legal_chatbot_ai/main.py`: CLI canonica do pacote.
- `legal_chatbot_ai/orchestrator.py`: fluxo central reutilizado pela CLI.
- `legal_chatbot_ai/config.py`: carrega configuracoes do `.env`.
- `legal_chatbot_ai/llm/`: ponto unico de comunicacao com Ollama.
- `legal_chatbot_ai/agents/`: agentes simulados do fluxo.
- `legal_chatbot_ai/collection/`: coleta mockada de processo.
- `legal_chatbot_ai/utils/`: validacao de numero e utilitarios JSON.

## 5. Fluxo sequencial

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

## 6. Responsabilidade dos agentes

- `user_input_agent`: limpa a mensagem e identifica possivel numero de processo.
- `context_agent`: usa Ollama para decidir `NO_COLLECTION`, `REQUEST_COLLECTION` ou `ASK_CLARIFICATION`.
- `legal_reasoning_agent`: organiza fatos, interpretacoes, incertezas e avisos.
- `response_agent`: transforma a analise tecnica em resposta final amigavel.

A validacao real do numero fica em `utils/process_number.py`.

## 7. Comandos oficiais

Instalar dependencias:

```text
pip install -r requirements.txt
```

Rodar pela raiz:

```text
python main.py
```

Rodar pelo pacote:

```text
python -m legal_chatbot_ai.main
```

## 8. Exemplos de entrada

```text
Quero saber o andamento do processo 0000000-00.0000.0.00.0000
```

```text
Tenho uma duvida sobre pensao alimenticia.
```

```text
Pode consultar meu processo?
```

## 9. Exemplos de saida esperada

Consulta com numero valido:

```text
Pelo que aparece nos dados disponiveis, o processo informado esta em andamento e possui movimentacoes simuladas recentes.

Isso nao permite concluir que houve decisao final nem afirmar prazo especifico.

Esta resposta e apenas informativa e nao substitui orientacao juridica profissional ou consulta oficial.
```

Consulta sem numero:

```text
Para consultar um processo, preciso que voce informe o numero do processo.

Esta resposta e apenas informativa.
```

Pergunta geral:

```text
Posso explicar o tema de forma geral com base na sua pergunta, sem consultar dados externos.

Esta resposta e apenas informativa e nao substitui orientacao juridica profissional.
```

## 10. Onde entraria o Playwright

Se a PoC evoluir para coleta real, o ponto natural seria
`legal_chatbot_ai/collection/collection_router.py`.

Nesta versao, esse arquivo apenas chama `mock_process_tree.py`. Nao ha
Playwright real, acesso externo ou scraping.

## 11. Checklist final de demonstracao

Antes de rodar:

- Instalar as dependencias do projeto.
- Criar `.env` a partir do `.env.example`.
- Confirmar que o Ollama esta instalado.
- Confirmar que o Ollama esta rodando.
- Confirmar que o modelo configurado foi baixado.

Durante a demonstracao:

- Testar pergunta juridica geral.
- Testar consulta com numero de processo.
- Testar consulta sem numero.
- Testar numero invalido.
- Mostrar `DEBUG_MODE=true`, se estiver habilitado no `.env`.
- Explicar que os dados sao mockados.
- Explicar que a resposta e informativa e nao oficial.

## 12. Cenarios de teste manual

Cenario 1 - pergunta geral sem coleta:

```text
O que significa juntada de peticao?
```

Esperado:

- `context_agent` retorna `NO_COLLECTION`.
- `collection_router` nao e chamado.
- A resposta explica o termo de forma geral e informativa.

Cenario 2 - consulta com processo:

```text
Quero saber o andamento do processo 0000000 00 0000 0 00 0000
```

Esperado:

- `context_agent` retorna `REQUEST_COLLECTION`.
- `utils/process_number.py` normaliza o numero para `0000000-00.0000.0.00.0000`.
- `collection_router` retorna uma arvore JSON mockada.
- A resposta final informa que o processo esta em andamento com dados simulados.

Cenario 3 - consulta sem numero:

```text
Quero saber o andamento do meu processo
```

Esperado:

- `context_agent` retorna `ASK_CLARIFICATION`.
- `collection_router` nao e chamado.
- A resposta pede o numero do processo.

Cenario 4 - numero invalido:

```text
Consulta o processo 123
```

Esperado:

- `context_agent` pode retornar `REQUEST_COLLECTION`.
- `utils/process_number.py` rejeita o numero por nao conter 20 digitos.
- `collection_router` nao e chamado.
- A resposta pede um numero de processo valido.

Cenario 5 - mensagem vazia:

```text

```

Esperado:

- O sistema nao quebra.
- A resposta orienta o usuario a digitar uma pergunta ou numero de processo.

Observacao: os resultados podem variar porque `context_agent`,
`legal_reasoning_agent` e `response_agent` usam Ollama. O comportamento esperado
acima e o caminho de arquitetura que a PoC deve demonstrar.
