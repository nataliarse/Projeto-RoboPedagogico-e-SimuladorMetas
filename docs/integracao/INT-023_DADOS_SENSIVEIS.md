# Renderização e dados processuais

- Respostas do backend são exibidas somente por interpolação Angular (`{{ }}`), sem
  `innerHTML`, bypass de sanitização ou criação dinâmica de elementos.
- O histórico local guarda número do processo, data da consulta e uma descrição
  genérica. Trechos da resposta, movimentações, partes e documentos não são gravados.
- O frontend não registra request, resposta, número processual ou `session_id` no
  console. O único `console.error` é o erro de bootstrap em `main.ts`.
- O backend registra falhas do coletor apenas por estágio e nome da exceção, sem payload
  processual, mensagem do usuário ou texto da exceção.

O teste usa uma resposta contendo markup executável e um marcador sensível: o conteúdo
permanece texto, nenhum elemento é criado e o marcador não chega ao histórico local.
