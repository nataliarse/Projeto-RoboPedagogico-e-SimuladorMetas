# Contexto do Projeto

## Objetivo

Construir um chatbot processual local em Python, com execucao via terminal e API
HTTP, usando Ollama para chamadas LLM quando disponivel. O projeto tambem possui
uma base local SQLite e uma camada inicial de RAG com Qdrant/Ollama para
evolucao futura com documentos reais.

## Fluxo obrigatorio

Toda mensagem do chat processual deve seguir este fluxo:

```text
Usuario
-> Agente 1: interpreta a intencao inicial da mensagem
-> Agente 2: usa contexto da conversa, carrega processo ativo e decide rota
-> Roteador deterministico: classifica structured, rag, hybrid ou fora de escopo
-> Base local/RAG: consulta SQLite e, quando aplicavel, Qdrant
-> Agente 3: analisa pergunta, JSON estruturado, chunks e limites
-> Agente 4: transforma a analise em resposta clara e segura
-> Usuario
```

## Responsabilidade dos agentes

### Agente 1

Entende a mensagem inicial do usuario. Exemplos: saudacao, pedido de consulta,
pergunta sobre processo ja carregado, duvida juridica geral, pergunta fora de
escopo ou mensagem ambigua.

### Agente 2

Recebe a interpretacao do Agente 1 e o estado da conversa. Decide se precisa
buscar dados de um processo, preserva o processo ativo em memoria e aciona a
busca RAG somente quando o roteador indicar necessidade.

### Roteador deterministico

Mantem a decisao de rota em Python. Separa perguntas respondidas por dados
estruturados de perguntas que podem precisar de chunks, teor documental ou
contexto hibrido.

### Agente 3

Recebe a pergunta, a conversa recente, a arvore estruturada do processo ativo e
o `rag_context` quando houver. Produz uma analise estruturada com fatos,
explicacao, limitacoes e foco de resposta. Nunca inventa dados ausentes.

### Agente 4

Transforma a analise do Agente 3 em resposta natural, clara e util. Nunca
menciona agentes, JSON, prompts, Ollama, Qdrant, chunks ou detalhes internos.

## Limites atuais

- Nao ha Playwright real, Selenium, CAPTCHA ou consulta web implementados.
- Nao ha frontend visual implementado.
- O simulador de metas ainda e um contrato/placeholder (`not_integrated`).
- O Qdrant e opcional em runtime; se estiver indisponivel, o chat continua com
  dados estruturados e `rag_status=unavailable`.
- O JSON de exemplo traz metadados de documentos, mas nao o teor integral das
  decisoes. Sem teor textual, o sistema nao afirma o conteudo de sentencas.
- Nao expor CPF ou CNPJ ao usuario.
- Nao fornecer aconselhamento juridico individual, previsao de resultado, prazo
  juridico ou estrategia processual.

## Dados disponiveis

A ingestao inicial usa `data/sample_processes.json` e cria/atualiza a base
SQLite local em `data/processual.sqlite3`. A arvore de processo preservada para
os agentes contem:

- processo
- partes_interessadas
- movimentacoes
- documentos
- pendencias
- coleta

O SQLite tambem guarda chunks canonicos para indexacao vetorial. O arquivo
`.sqlite3` e local e nao deve ser versionado.

## Estado da conversa

O sistema mantem sessao em memoria durante a execucao:

```python
{
    "conversation": [],
    "active_process": None,
    "last_intent": None,
}
```

O historico e podado para evitar crescimento indefinido. A base SQLite persiste
os dados estruturados do processo, mas nao substitui a memoria de sessao.
