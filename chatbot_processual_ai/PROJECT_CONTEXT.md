# Contexto do Projeto

## Objetivo

Construir um chatbot processual local, inicialmente executado no terminal, usando Python e Ollama.

A coleta dos dados e a interface gráfica são responsabilidade de outros membros da equipe. Este projeto cuida somente da camada de IA e da conversa.

## Fluxo obrigatório

Toda mensagem deve seguir este fluxo:

Usuário
→ Agente 1: interpreta a intenção inicial da mensagem
→ Agente 2: usa contexto da conversa e chama a coleta apenas quando necessário
→ Agente 3: analisa a conversa, a pergunta e a árvore JSON do processo
→ Agente 4: transforma a análise em resposta clara para o usuário
→ Usuário

## Responsabilidade dos agentes

### Agente 1
Entende a mensagem inicial do usuário.
Exemplos: saudação, pedido de consulta, pergunta sobre processo já carregado, dúvida jurídica geral, pergunta fora de escopo ou mensagem ambígua.

### Agente 2
Recebe a interpretação do Agente 1 e o estado da conversa.
Decide se precisa buscar dados de um processo.
A decisão real de chamar a coleta deve permanecer no Python, não apenas no LLM.

### Agente 3
Recebe a pergunta, a conversa completa e a árvore JSON do processo ativo.
Produz uma análise estruturada com fatos, interpretação, limites e plano de resposta.
Nunca inventa dados ausentes da coleta.

### Agente 4
Transforma a análise do Agente 3 em resposta natural, clara e útil.
Nunca menciona agentes, JSON, prompts, Ollama ou detalhes internos.

## Limites

- Não realizar scraping, Selenium, Playwright, CAPTCHA ou consulta web.
- Não criar frontend, API HTTP, login, banco de dados ou Docker nesta fase.
- Não expor CPF ou CNPJ ao usuário.
- Não inventar conteúdo de documentos quando a coleta disponibilizar apenas título, tipo e data.
- Não fornecer aconselhamento jurídico individual, previsão de resultado, prazo jurídico ou estratégia processual.
- O modelo LLM deve rodar localmente pelo Ollama.
- A solução inicial deve ser simples e funcional no terminal, mas organizada para evolução futura.

## Dados disponíveis

A coleta fornece uma árvore JSON por processo contendo:

- processo
- partes_interessadas
- movimentacoes
- documentos
- pendencias
- coleta

A coleta pode informar que existe uma sentença, mas não necessariamente entrega o texto da sentença. Nesse caso, o chatbot pode informar que o documento existe, mas não pode afirmar o que foi decidido.

## Estado da conversa

O sistema manterá apenas memória em RAM durante a execução:

```python
{
    "conversation": [],
    "active_process": None,
    "last_intent": None
}
```

Nenhum dado deve ser persistido nesta fase.
