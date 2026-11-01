# Divergências numéricas

## Meta 1 — GATE-M1 liberado por validação humana

A implementação canônica e a entrega da Equipe B não são matematicamente equivalentes. Nenhuma fórmula ou série foi alterada.

### Regra de suspensão

- Canônica: usa `suspensos_acum`, isto é, soma mensal do estoque de suspensos. Calcula `novos_acum + dessobrestados_acum - suspensos_acum`, mas aplica como piso `max(novos_acum + dessobrestados_acum, 1)`. Na prática observada, a subtração não reduz o denominador abaixo do total sem suspensos.
- Equipe B: deriva `susm1 = max(0, estoque_mês - estoque_mês_anterior)`, acumula apenas aumentos do estoque e usa `novos_acum + dessobrestados_acum - susm1_acum`, retornando `null` quando o denominador é menor ou igual a zero.

Caso determinístico `(novos=100, julgados=100, dessobrestados=20, suspensão=30)`:

- canônica: `100 / max(100 + 20 - 30, 100 + 20, 1) * 100 = 83,3333...`;
- Equipe B: `100 / (100 + 20 - 30) * 100 = 111,1111...`.

### Dados e janela

- Canônica: quatro planilhas, 86 registros, de 2020-01 a 2027-02; tipos reais/forecast vêm de cada série e corte de julgados.
- Equipe B: planilha única de Meta 1, 84 registros, de 2020-01 a 2026-12; todas as variáveis recebem tipo pelo mesmo corte.
- Dezembro/2026 canônico: Meta 1 `109,86`.
- Dezembro/2026 Equipe B: Meta 1 `96,47`.

Os acumulados de novos, julgados e dessobrestados também divergem, portanto não é possível atribuir a diferença final somente ao denominador.

### Nulos, zero e arredondamento

- Ambas retornam valor não calculável (`NaN` serializado como `null`) para denominador zero no caso simples e para julgados nulos.
- A canônica testa denominador zero antes de aplicar o piso; a Equipe B rejeita denominador menor ou igual a zero.
- Ambas calculam em precisão de ponto flutuante e arredondam a série de Meta 1 para duas casas em `calcular_metas`.

### Decisão

Em 23/10/2026, o responsável confirmou que as regras e séries da Equipe B constituem atualização autorizada e aprovou sua integração. O GATE-M1 foi liberado; a referência histórica anterior permanece preservada nas fixtures pré-integração.

Fixture reproduzível: `docs/integracao_equipe_b/fixtures/meta1_comparison.json`.

## Meta 2

O cálculo A/ANT permanece independente da Meta 2 agregada anterior. A auditoria da entrega 06 recuperou a semântica e as séries agregadas originais sem versionar o ZIP processual. A aplicação agora separa a reprodução não homologada da equipe (`A=104,63%`, `ANT=110,00%`) da aplicação demonstrativa das fórmulas CNJ 2026 v3 aos mesmos dados (`A=105,32%`, `ANT=111,11%`). Valores, hashes, diferenças mensais e limitações estão em `AUDITORIA_META2.md`.
