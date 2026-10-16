# Pendências do simulador

Nomes e prazos dependem de alinhamento da equipe. As áreas abaixo indicam domínio de decisão, sem transferir ao apoio de integração a manutenção permanente.

| Problema observado | Evidência | Impacto | Área responsável |
|---|---|---|---|
| Validar denominador e piso da Meta 1 | A implementação usa `max(novos + dessobrestados - suspensos, novos + dessobrestados, 1)`. | Pode alterar percentuais e conclusão de cumprimento. | Negócio/metodologia CNJ, com apoio de dados. |
| Definir metodologia e dados por coorte da Meta 2 | A tela já identifica o resultado como provisório; a API calcula com agregados disponíveis, sem coortes de processos antigos. | Meta 2 não deve ser tratada como resultado metodologicamente validado. | Negócio/metodologia CNJ e dados. |
| Consolidar cópias de regras e separar ETL, cálculo e API | Há regras no backend, código legado/local no frontend e uma cópia em `simulador-metas/`. | Risco de divergência e manutenção duplicada. | Arquitetura/engenharia. |
| Integrar e revisar o otimizador | Existe implementação, mas a tela mantém a aba desabilitada. | Recurso não faz parte do fluxo validado e não pode ser executado pela tela. | Negócio/metodologia e engenharia. |
| Validar rotas fora do fluxo mínimo e padronizar erros | Foram exercitadas apenas `/api/base`, `/api/simular` e `/api/health`; `/api/comparar` e `/api/otimizador` não integram o proxy mínimo. | Comportamento e mensagens dessas rotas não estão cobertos pela entrega. | Backend/QA. |
| Configurar o backend do chat | O frontend chama `/api/chat`; o único proxy recebido apontava `/api` inteiro ao simulador, que não possui essa rota. Não foi encontrada URL real no projeto/histórico disponível. | Chat falha até receber destino e configuração próprios. | Plataforma/ambiente e equipe responsável pelo chat. |
| Completar ambiente frontend | Esta máquina não possui Node.js/npm no `PATH` nem `node_modules`; `angular.json` foi recuperado do arquivo original. | Build, servidor Angular, teste pelo proxy e navegador não puderam ser executados aqui. | Plataforma/ambiente, com validação posterior de frontend/QA. |
| Resolver ocupação da porta 8000 no ambiente de teste | Ao iniciar a API, a porta 8000 já respondia por outro serviço; a validação desta API usou 8010. | Os comandos padrão exigem liberar 8000 ou alinhar outra porta e atualizar o proxy. | Plataforma/ambiente. |

As planilhas, as fórmulas atuais e `backend/robo_cnj_meta2.py` permanecem preservados. Qualquer mudança nesses itens exige validação metodológica fora deste recorte.
