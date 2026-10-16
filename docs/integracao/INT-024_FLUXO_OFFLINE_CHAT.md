# Fluxo integrado offline do chat

O cenário automatizado usa uma base SQLite temporária e uma árvore processual de
fixture. Antes da chamada HTTP, a fixture é ingerida no repositório real. A coleta é
substituída por uma função que falha o teste se for chamada; portanto o cenário não
consulta PJe nem depende de rede.

Fluxo exercitado:

1. `POST /api/processos/chat` recebe a pergunta com número processual;
2. a aplicação ASGI chama o orquestrador;
3. o contexto encontra o processo no repositório local;
4. análise e montagem de resposta produzem o envelope público;
5. o contrato contém `session_id`, processo ativo e `resultado.resposta` não vazio;
6. a suíte Angular injeta esse mesmo formato no cliente HTTP e confirma que
   `resultado.resposta` aparece no DOM.

O reconhecimento de intenção e a recuperação RAG são tornados determinísticos no teste
para impedir dependência de Ollama/Qdrant. Os agentes de contexto, análise e resposta,
o repositório, o endpoint FastAPI e a serialização permanecem reais.
