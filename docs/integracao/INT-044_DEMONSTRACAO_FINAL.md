# INT-044 — Demonstração final

Data: 2026-10-19

Branch: `feat/integracao_robo_metas`

## Matriz de evidências

| Jornada | Evidência executada | Resultado |
|---|---|---|
| Abrir a aplicação | `GET /` pelo servidor Angular | HTTP 200; shell único carregado |
| Navegar ao simulador | `GET /simulador` pelo mesmo frontend | HTTP 200; rota navegável |
| Consultar saúde do chatbot | `GET /api/processos/health` pelo proxy | `status=ok` |
| Consultar saúde do simulador | `GET /api/simulador/health` pelo proxy | `status=ok`; 86 registros |
| Conversar com o chatbot | `POST /api/processos/chat` offline | sessão e resposta não vazias |
| Consultar base de metas | `GET /api/simulador/base` | 86 registros; Meta 1 = `109,86` |
| Validar contratos | `scripts/Test-IntegrationContracts.ps1` | chatbot 23+2 subtestes, simulador 6 e Angular 29 aprovados |
| Validar ponta a ponta | `scripts/Test-LocalSmoke.ps1` | três processos, proxy, chat, base e duas rotas aprovados |

Os dois comandos foram executados em sequência. A primeira tentativa da gate encontrou `spawn EPERM` ao criar o subprocesso do esbuild no sandbox; a repetição autorizada com os mesmos arquivos foi aprovada integralmente. Isso caracteriza restrição do executor, não falha funcional.

## Limitações conhecidas

- A demonstração é HTTP/DOM automatizada e não substitui homologação visual manual em navegadores e tamanhos de tela variados.
- Ollama, Qdrant e coleta PJe ficam deliberadamente desabilitados; o roteiro não acessa sistemas institucionais.
- O build mantém um warning não bloqueante: `chat.css` excede o orçamento informativo de 4 kB em 1,75 kB.
- O MVP não possui autenticação, autorização, rate limiting distribuído nem persistência compartilhada de sessões.
- Regras e resultados CNJ precisam de homologação funcional antes de uso em produção.
- Healthchecks comprovam disponibilidade dos dois backends, não prontidão de integrações opcionais.

## Conclusão

O chat e o simulador estão navegáveis na mesma UI Angular, com namespaces e healthchecks independentes. A gate de contratos e o teste ponta a ponta local foram aprovados, atendendo ao critério do INT-044.
