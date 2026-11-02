# PR — Integrar chatbot processual e simulador de metas CNJ

## Metadados

- Branch de origem: `feat/integracao_robo_metas`
- Branch de destino sugerida: definida pelo mantenedor no momento da abertura
- Base da integração: `236e033ec74b9773542e1add13343fc4819fc07c`
- Escopo do diff: 156 arquivos, 23.501 adições e 1.237 remoções
- Estado: pacote local pronto para revisão; nenhum push, PR remoto, merge ou deploy foi executado

## Resumo

Esta mudança integra o chatbot processual e o simulador CNJ em uma única aplicação Angular. O `frontend/` existente permanece canônico e recebe os elementos relevantes da UI mais recente importada. Os dois backends FastAPI continuam separados nas portas 8000 e 8001 e são acessados por namespaces de proxy distintos.

Principais entregas:

- chat real com contrato tipado, sessão, loading, cancelamento e falhas honestas;
- simulador com base, cenários, tabela, gráficos e acesso aos quatro contratos preservados;
- navegação única entre chat e simulador;
- gateway opcional do chatbot para intenções explícitas de metas, com rastreabilidade e degradação transparente;
- healthchecks independentes, validações de fronteira e CORS restrito;
- scripts reproduzíveis de inicialização, contratos e smoke local;
- snapshots numéricos, documentação operacional e revisão de segurança/dependências.

## Decisões registradas

- A arquitetura híbrida está registrada em `docs/integracao/ADR-001_ARQUITETURA_APLICACAO_UNIFICADA.md`.
- `frontend/` é a árvore Angular canônica; `integracao_entrada/` preserva o snapshot importado sem drift.
- Os backends não foram fundidos: falha de um serviço não deve derrubar o outro.
- Chamadas institucionais e coleta PJe não fazem parte dos testes; fixtures locais são obrigatórias.
- O simulador só é consultado pelo chatbot para intenções explicitamente mapeadas e nunca inventa resultados.

## Evidências para revisão

| Gate | Resultado |
|---|---|
| Chatbot | 157 testes + 2 subtestes aprovados |
| Simulador | 8 testes + 7 subtestes aprovados |
| Angular | 9 arquivos / 37 testes aprovados |
| Proxy | 3 testes aprovados |
| Build | aprovado |
| Contratos integrados | 23+2, 6 e 29 testes aprovados |
| Smoke dos três processos | healths, chat, 86 registros e rotas `/`/`/simulador` aprovados |
| Dependências | `npm audit` com 0 vulnerabilidades; `pip check` íntegro |
| Diff/segredos | nenhuma exclusão da integração ou assinatura de segredo detectada |

Comandos principais:

```powershell
powershell -File scripts/Test-IntegrationContracts.ps1
powershell -File scripts/Test-LocalSmoke.ps1
```

## Pontos de atenção

- O build emite warning não bloqueante porque `chat.css` excede o orçamento informativo em 1,75 kB.
- Ollama, Qdrant e PJe são opcionais e ficam desabilitados nas gates offline.
- Autenticação, autorização, rate limiting distribuído, retenção e sessões compartilhadas são requisitos anteriores à produção.
- Resultados e regras CNJ exigem homologação funcional; a demonstração automatizada não substitui revisão visual manual.

## Plano de rollback

Antes do merge, basta não aprovar/mesclar a PR; a branch principal permanece inalterada. Depois de eventual merge, o método preferencial é reverter o commit de merge pela plataforma, preservando histórico. Se houver necessidade de rollback seletivo, reverter primeiro o frontend/proxy e depois gateway/backends em commits separados, executar novamente as duas gates e confirmar as portas 8000/8001/4200 livres.

Dados e migrações não exigem rollback: a integração não publica banco, não executa migração destrutiva e mantém o snapshot original em `integracao_entrada/`.

## Checklist do revisor

- [ ] Confirmar branch de destino e políticas de CI.
- [ ] Revisar ADR e separação dos dois backends.
- [ ] Executar gate de contratos e smoke local.
- [ ] Validar manualmente chat e simulador em viewport desktop e móvel.
- [ ] Homologar regras/resultados CNJ com responsável de domínio.
- [ ] Confirmar requisitos de segurança antes de qualquer publicação.
- [ ] Aprovar o plano de rollback.

Não efetuar merge automático.
