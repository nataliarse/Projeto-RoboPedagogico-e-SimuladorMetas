# Orçamentos de timeout HTTP

Os limites do frontend ficam centralizados em `core/config/http-timeouts.ts`. Eles são
orçamentos por classe de operação, não tentativas de ocultar lentidão aumentando um
valor global.

| Operação | Limite | Motivo |
|---|---:|---|
| Healthcheck | 5 s | Deve apenas confirmar disponibilidade local. |
| Carregar base do simulador | 15 s | Leitura e cálculo local, sem coleta externa. |
| Simular cenário | 20 s | Cálculo local de um cenário. |
| Comparar cenários | 30 s | Custo cresce com a quantidade de cenários. |
| Otimizador | 45 s | Executa busca iterativa e múltiplos recálculos. |
| Chat processual | 120 s | Pode incluir coleta PJe, agentes e RAG; é a única operação potencialmente externa e longa. |

O chat usava 135 s; o limite foi reduzido e nomeado. Ao expirar, RxJS cancela a
requisição e a interface informa timeout, sem retry automático e sem resposta mock.
Os limites do simulador serão consumidos pelo serviço transportado na fase 4; esta
decisão impede que cada tela invente um valor próprio.

Timeout não substitui observabilidade no servidor nem garante cancelamento do trabalho
já iniciado no backend. Alterações futuras devem ser justificadas por medição local e
manter testes com relógio virtual.
