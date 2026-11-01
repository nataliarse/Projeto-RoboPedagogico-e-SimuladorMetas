# Auditoria e metodologia da Meta 2 A/ANT

## Referência normativa

A modalidade oficial implementa o **Glossário das Metas Nacionais do Poder Judiciário 2026 — Justiça do Trabalho, versão 3 (março/2026)**, preservado no repositório em `chatbot_processual_ai/data/normas/glossario_metas_2026_jt_v3.txt`.

Fórmulas para TRTs:

- A: `(Σjulgadom2_a / (Σdism2_a − Σsusm2_a − Σdesm2_a)) × (1000 / 9,4)`;
- ANT: `(Σjulgadom2_ant / (Σdism2_ant − Σsusm2_ant − Σdesm2_ant)) × (1000 / 9,9)`.

O glossário esclarece que cargas DataJud sucessivas já são consolidadas. Na entrega auditada, julgados e dessobrestados são fluxos mensais; suspensos é estoque mensal. Por isso, apenas os dois fluxos são acumulados.

## Evidência recebida e recuperação

Os nomes dos seis arquivos recebidos não correspondem ao conteúdo descrito no leia-me:

| Nome recebido | Conteúdo identificado |
|---|---|
| `LEIA_ME (2).txt` | fonte de `historico_projecao_meta2.py` |
| `parametros_meta2_2025 (2).csv` | fonte de `robo_cnj_meta2.py` |
| `requirements (2).txt` | leia-me da entrega |
| `robo_cnj_meta2 (2).py` | lista de dependências |
| `RESULTADO... (2).csv` | parâmetros agregados de 2025 |
| `RESULTADO... (2).xlsx` | ZIP processual com `TRT18.csv` e derivados |

O ZIP renomeado tem SHA-256 `7da8d2d89b7f2df078dbda2df38e68577a53f906d629baf90cbe11b7251065bd`. Ele foi usado somente offline e permanece fora do Git. Nenhuma linha ou identificação processual foi copiada. Os hashes dos fontes e todas as séries agregadas estão na fixture sanitizada `fixtures/meta2_original_series.json`.

A projeção foi reproduzida com os fontes recebidos e `statsmodels 0.15.0`. A entrega não fixa versões; portanto, os inteiros reproduzidos são rastreáveis, mas uma futura execução com outra versão da biblioteca pode selecionar modelo ou arredondamento diferente.

## Comparação integral com a integração anterior

A comparação percorreu os 14 meses observados e os 10 projetados de cada uma das seis séries:

| Grupo/série | Histórico alterado | Projeção alterada | Valores que já coincidiam |
|---|---:|---:|---|
| A julgados | 14/14 | 10/10 | nenhum |
| A suspensos | 14/14 | 9/10 | somente dez/2026 = 190 |
| A dessobrestados | 14/14 | 10/10 | nenhum |
| ANT julgados | 2/14 | 0/10 | 2025 inteiro e toda a projeção |
| ANT suspensos | 14/14 | 9/10 | somente dez/2026 = 28 |
| ANT dessobrestados | 10/14 | 5/10 | jan, fev, nov e dez/2025; mai–set/2026 |

O erro de maior impacto estava em ANT/dessobrestados. A integração anterior registrava dezembro como `24`, tratando o total anual como fluxo mensal e acumulando `44`. A entrega registra janeiro/fevereiro como `[5, 1]` e março–dezembro como `[1, 1, 2, 2, 2, 2, 2, 2, 2, 2]`: `6 + 18 = 24`, com fluxo de dezembro igual a `2`.

Também foram corrigidas omissões/reconstruções relevantes: A observado jan/2025 passa de `1820/95/8` para `4284/150/31`; A observado jan–fev/2026 passa de julgados `[180,137]` para `[127,190]`; ANT suspensos jan–fev/2026 passa de `[1,1]` para `[15,16]`; e ANT dessobrestados jan–fev/2026 passa de `[0,0]` para `[5,1]`.

## Duas modalidades, sem homologação implícita

Os mesmos dados não homologados são apresentados em modalidades separadas:

| Grupo | Reprodução da equipe | Metodologia CNJ 2026 v3 |
|---|---:|---:|
| A | `26907 / (27548 − 190) × (1000/9,4) = 104,63%` | `26907 / (27548 − 190 − 180) × (1000/9,4) = 105,32%` |
| ANT | `22 / (72 − 28 − 24) × 100 = 110,00%` | `22 / (72 − 28 − 24) × (1000/9,9) = 111,11%` |

`104,63%` e `110,00%` reproduzem a metodologia do código entregue. Não são percentuais homologados nem usam integralmente a versão 3. `105,32%` e `111,11%` aplicam as fórmulas da versão 3, mas continuam demonstrativos porque a fonte não veio acompanhada de homologação institucional.

## Condição para homologação futura

Promover os resultados exige registro formal de homologação da fonte agregada, confirmação da versão do ambiente ARIMA ou entrega do output oficial congelado e validação, pela equipe responsável, de que a projeção pode ser usada como dado de acompanhamento institucional.
