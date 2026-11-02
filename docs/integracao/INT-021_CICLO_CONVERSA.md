# Ciclo de conversa e persistência local

- **Nova conversa:** remove mensagens e erro da memória da tela, descarta o
  `session_id` do `sessionStorage` e limpa eventual rascunho. A próxima pergunta cria
  uma nova sessão no backend.
- **Refresh na mesma aba:** mensagens em memória são descartadas. O `session_id` pode
  permanecer no `sessionStorage` durante a sessão da aba, permitindo continuidade,
  mas o backend pode ter reiniciado e criar um contexto vazio para o mesmo ID.
- **Fechar a sessão do navegador:** o `session_id` não é persistido em `localStorage`.
- **Histórico de processos:** os três processos recentes ficam em `localStorage` apenas
  como conveniência visual. Esse histórico não restaura mensagens, contexto de agentes
  nem prova que uma sessão correspondente ainda exista no servidor.

A ação “Nova conversa” preserva deliberadamente o histórico visual de processos; sua
limpeza é uma responsabilidade separada do histórico, não da sessão conversacional.
