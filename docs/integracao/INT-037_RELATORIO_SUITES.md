# Relatório das suítes locais

Data: 2026-10-19. Nenhuma chamada institucional ou coleta PJe foi realizada.

| Suíte | Diretório/comando | Resultado |
|---|---|---|
| Chatbot Python | `chatbot_processual_ai`: `.venv/Scripts/python -m pytest tests -q -p no:cacheprovider` | 155 aprovados |
| Simulador Python | `simulador_metas_cnj`: `.venv/Scripts/python -m unittest discover -s tests -v` | 5 aprovados |
| Angular | `frontend`: `npm test -- --watch=false` | 8 arquivos, 36 testes aprovados |
| Build Angular | `frontend`: `npm run build` | aprovado, bundle inicial 332,05 kB |

Uma tentativa inicial iniciou pytest na raiz e falhou na coleta por os módulos
históricos (`api`, `schemas`, `orchestrators`) serem importados relativamente ao
diretório do chatbot. A repetição no diretório documentado passou integralmente; não era
regressão funcional. O build mantém aviso não bloqueante: `chat.css` tem 5,75 kB contra
orçamento de warning de 4 kB, abaixo do limite de erro de 8 kB.

Nenhuma regressão causada pela integração permaneceu após a execução das quatro gates.
