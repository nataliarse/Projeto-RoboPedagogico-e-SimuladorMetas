# ADR-001 — Arquitetura da aplicação unificada

- Status: **PROPOSTO — AGUARDANDO APROVAÇÃO**
- Data: 2026-10-16
- Checklist: `INT-006`

## Contexto

O repositório possui um Angular executável em `frontend/`, já conectado ao contrato real do chatbot. O snapshot recebido possui a interface completa do simulador e um layout mais adequado, mas não contém `angular.json`; sua árvore `simulador-metas/` interna também é parcial. Os backends FastAPI têm responsabilidades distintas e publicam um `/api/health` conflitante.

## Alternativas consideradas

### A — Usar `frontend/` como workspace canônico e transportar a UI do simulador (recomendada)

- Mantém configuração Angular, testes e chat real já funcionais.
- Transporta para esse workspace o layout e os componentes de simulação recebidos.
- Exige comparação controlada de componentes, estilos e modelos, sem copiar o snapshot indiscriminadamente.
- Menor risco de regressão e menor quantidade de infraestrutura reconstruída.

### B — Reconstruir o workspace Angular ao redor do frontend importado

- Parte diretamente do layout visual recebido.
- Exige recriar `angular.json`, reconciliar configurações e retransportar o chat funcional da raiz.
- Maior risco de perder testes, sessão e tratamento de erro já presentes.

### C — Manter dois frontends

- Reduz transporte inicial.
- Não atende ao requisito de produto único e duplica navegação, build e operação.

## Decisão proposta

Adotar a alternativa A:

1. `frontend/` permanece o único workspace Angular canônico.
2. A identidade visual, shell e funcionalidades de simulador do snapshot serão transportadas incrementalmente para `frontend/src/app/`, preservando primeiro o chat real e seus testes.
3. O backend processual permanece em `chatbot_processual_ai/`, porta local 8000.
4. O backend real do simulador será promovido, por cópia rastreável, para `simulador_metas_cnj/`, porta local 8001; as fórmulas e planilhas não serão alteradas durante o transporte.
5. `integracao_entrada/TCC-Simulador-CNJ/` permanece como snapshot de comparação durante a integração; não será apagado automaticamente.
6. O frontend usará rotas públicas não ambíguas:
   - `/api/processos/*` para o backend processual;
   - `/api/simulador/*` para o backend de metas.
7. Os serviços manterão aliases legados quando necessário, mas a UI não dependerá de `/api/health` genérico. Serão usados `/api/processos/health` e `/api/simulador/health`.
8. No desenvolvimento, um único proxy Angular roteará cada namespace à porta correspondente.
9. Não haverá fusão física dos processos FastAPI nesta etapa.

## Estrutura-alvo

```text
frontend/                 Angular único: chat + simulador
chatbot_processual_ai/    FastAPI processual, porta 8000
simulador_metas_cnj/      FastAPI do simulador, porta 8001
integracao_entrada/       snapshot preservado para comparação
docs/integracao/          ADRs, inventários e evidências
```

## Consequências

- A UI recebida será preservada funcionalmente, não necessariamente como cópia byte a byte no destino final.
- Contratos e healthchecks serão explicitamente namespaced.
- Os dois serviços poderão falhar e ser diagnosticados independentemente.
- O desenvolvimento continuará exigindo três processos, posteriormente reunidos por scripts locais.
- A árvore Angular parcial importada não será tratada como aplicação executável nem removida sem autorização específica.

## Aprovação necessária

O `INT-006` só pode ser promovido a `VALIDATED` após aprovação humana desta decisão. Nenhum código será movido ou copiado para a estrutura-alvo antes dessa aprovação.
