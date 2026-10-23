# Contratos HTTP — base canônica e extensão da Equipe B

## Regra de roteamento

O navegador usa `/api/simulador/*`. O proxy Angular encaminha para `127.0.0.1:8001` e reescreve `^/api/simulador` como `/api`. Assim, `/api/simulador/meta2/base` chega ao FastAPI como `/api/meta2/base`. O chatbot continua em `/api/processos/*`, porta 8000.

## Contratos existentes e protegidos

| Função | Método e URL externa | URL interna | Corpo | Resposta 200 | Erros/nulos |
|---|---|---|---|---|---|
| Saúde do simulador | `GET /api/simulador/health` | `GET /api/health` | — | `{status, registros}` | falha inesperada 500 |
| Base | `GET /api/simulador/base` | `GET /api/base` | — | `{registros[], meta1_final, meta2_final}` | metas e campos mensais podem ser `null`; nunca converter em zero |
| Simular | `POST /api/simulador/simular` | `POST /api/simular` | `{alteracoes: Record<YYYY-MM, {julgados, dessobrestados, suspensos}>}`; inteiros estritos, extras proibidos | mesmo schema da base | 422 para schema/mês inválido; 500 sanitizado em falha inesperada |
| Comparar | `POST /api/simulador/comparar` | `POST /api/comparar` | `{cenarios: [{nome, alteracoes}]}` | `{cenarios[], meta1_base, meta2_base}` | métricas/diferenças podem ser `null`; 422/500 |
| Otimizador | `POST /api/simulador/otimizador` | `POST /api/otimizador` | `{variavel, mes, meta_alvo, meta}` | `{variavel, mes, meta_alvo, meta_atual, incremento_necessario, meta_resultante, mensagem, ok}` | resultado pode conter `null`; 400 semântico e 422 estrutural |
| Chat real | `POST /api/processos/chat` | igual, porta 8000 | `{mensagem, session_id?}` | resposta processual tipada com `session_id` efetivo | contrato, sessão e erro são protegidos |
| Saúde processual | `GET /api/processos/health` | `GET /api/health`, porta 8000 | — | `{status}` | não testa agentes/Ollama/Qdrant |

## Novos contratos candidatos

### Esforço mensal da Meta 1

- Externa: `POST /api/simulador/meta1/quanto-falta`.
- Interna: `POST /api/meta1/quanto-falta`.
- Corpo: `{meta_alvo: number > 0 e <= 200, mes_inicio?: YYYY-MM, alteracoes?: Record<YYYY-MM, AlteracaoMes>}`.
- Resposta candidata: `{ok, ja_atingida, meta_alvo, meta_atual, meta_resultante, mes_inicio, meses[], n_meses, meses_reais[], incremento_mensal, total_adicional, julgados_previstos_periodo, conta, mensagem}`.
- Nulabilidade: `meta_atual`, `meta_resultante`, `incremento_mensal`, `total_adicional`, `conta.denominador` e `conta.julgados_necessarios` podem ser `null` quando não calculáveis.
- Erros: 400 para mês inicial semanticamente inadequado; 422 para tipos, campos extras, mês de alteração inválido e limites; 500 sem detalhe interno para falha inesperada.

### Meta 2 A/ANT

- Externa: `GET /api/simulador/meta2/base` e `POST /api/simulador/meta2/simular`.
- Interna: `GET /api/meta2/base` e `POST /api/meta2/simular`.
- Corpo de simulação: `{alteracoes_A: Record<YYYY-MM, AlteracaoMes>, alteracoes_ANT: Record<YYYY-MM, AlteracaoMes>}`.
- Resposta candidata: `{resultado_2025, resultado_2026: {A, ANT}, serie_A[], serie_ANT[]}`; cada série informa `tipo` (`real`/`previsao`) e `meta2` anulável.
- Erros: 422 para schema/mês fora da série; 500 sanitizado para falha inesperada.
- Condição de publicação: GATE-M2 liberado e projeções claramente rotuladas. Contrato preparado não equivale a homologação do cálculo.

## Timeout e tratamento do cliente

- O cliente canônico aplica timeouts centralizados: base, cenário, comparação e otimizador têm orçamentos próprios em `HTTP_TIMEOUT_MS`.
- Os clientes importados novos não aplicam timeout e usam namespace incorreto (`/api` ou `/api/meta2`); não serão copiados literalmente.
- Os novos métodos devem reutilizar os orçamentos do simulador ou criar entradas explícitas na mesma configuração, com loading finalizado em sucesso/erro/timeout.
- Resposta ausente ou estruturalmente malformada deve falhar como erro de contrato; não usar fallback fictício.

## Matriz de compatibilidade

| Aspecto | Base canônica | Entrega Equipe B | Decisão |
|---|---|---|---|
| Namespace browser | `/api/simulador` | `/api` e `/api/meta2` | preservar canônico |
| Respostas antigas | response models explícitos | sem response models | manter e adicionar schemas explícitos |
| Campos extras de entrada | proibidos | misto (`CenarioItem` permissivo) | padronizar como proibidos |
| Inteiros de alterações | estritos | estritos | preservar |
| `null` | serializado como `null` | presente nas novas respostas | preservar sem coerção |
| Timeout Angular | centralizado | ausente | usar centralizado |
| Chat | real, com sessão | `/api/chat` mock | não importar |
