# Auditoria da Meta 2 A/ANT

## Conclusão

O código é determinístico e distingue `real` de `previsao`. Em 23/10/2026, o responsável validou as regras e séries como atualização da Equipe B e autorizou sua integração, liberando o GATE-M2. As limitações de proveniência e sensibilidade abaixo continuam obrigatoriamente documentadas e devem aparecer na UI como natureza histórica/projetada.

## Fórmulas implementadas

- Grupo A: `(julgados_base_antes_2026 + julgados_acum_2026) / (D - suspensos_do_mês) * (1000 / 9,4)`, com `D=27.548`.
- Grupo ANT: `julgados_acum_2026 / (D - suspensos_do_mês - dessobrestados_acum_2026) * 100`, com `D=72`.
- Denominador menor ou igual a zero produz `null`.
- Valores alterados são truncados no piso zero; o resultado é arredondado a duas casas.

A Meta 2 canônica atual é outra métrica agregada: usa julgados e distribuídos gerais do ano e suspensos do mês. Ela própria contém alerta de que faltam dados da coorte. A implementação A/ANT não pode substituí-la nem ser misturada a ela.

## Séries e janela

- Histórico declarado: jan/2025 a fev/2026, embutido em `HISTORICO_REAL`.
- Projeção declarada: mar/2026 a dez/2026, embutida em `PROJECAO_ARIMA`.
- A possui `julgados_base_antes_2026=25.863`; ANT usa zero.
- `RESULTADO_2025` é uma constante independente da série calculada: A `106,22`, ANT `100,00`.
- Não há arquivo de modelo, seed, versão, intervalo de confiança, código que gere essas previsões a partir das planilhas nem hash de fonte externa associado às constantes.
- O comentário “extraídos do robo_cnj_meta2.py” não é proveniência suficiente; o script canônico/importado de mesmo nome declara que a fórmula de processos antigos está fora do cálculo.

## Comportamento observado

- Base 2026: A `104,63`; ANT `null` porque o denominador final é `72 - 28 - 44 = 0`.
- Alterar `+10` julgados em jan/2026 (registro marcado `real`) muda A para `104,67`.
- Alterar `+10` julgados em mar/2026 (projeção) também muda A para `104,67`.
- Portanto, a API permite editar meses reais e projetados sem distinção de autorização; isso precisa ser decidido antes de exposição.
- Uma alteração ANT de `-1` dessobrestado em mar/2026 reduz o acumulado final a 43, torna o denominador 1 e produz `2200,00%`. É matematicamente coerente com a fórmula, mas evidencia extrema sensibilidade e necessidade de limites/metodologia.
- Forçar suspensos de dezembro acima de D produz `null` nos dois grupos, sem `NaN` JSON.

## Riscos metodológicos

1. Ausência de evidência para `D`, coortes e `julgados_base_antes_2026`.
2. `RESULTADO_2025` fixo não é recalculado nem reconciliado com `HISTORICO_REAL`.
3. Projeção ARIMA fixa não comprova atualidade, treinamento ou reprodutibilidade.
4. Edição de meses reais pode transformar histórico em cenário sem sinalização suficiente.
5. ANT frequentemente possui denominador zero ou muito pequeno, gerando `null` ou percentuais extremos.
6. Campos `suspensos` parecem estoque mensal, enquanto `dessobrestados` é acumulado; a semântica temporal precisa de validação.

## Decisão de integração

Os contratos e componentes podem ser preparados isoladamente, mas o acesso público à Meta 2 deve permanecer oculto/indisponível. Nenhum valor será rotulado como oficial ou atualizado. A liberação requer responsável metodológico confirmar fórmulas, coortes, séries, parâmetros, regras de edição de meses reais e limites aceitáveis.

Fixture reproduzível: `docs/integracao_equipe_b/fixtures/meta2_audit.json`.
