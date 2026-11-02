# Snapshot numérico do simulador

O snapshot usa exclusivamente as quatro planilhas versionadas em
`simulador_metas_cnj/dados`. A tolerância aprovada é absoluta de **0,01 ponto
percentual**, alinhada ao arredondamento de duas casas feito pelo backend.

Baseline esperado para 86 registros:

- Meta 1 final: `109,86`;
- Meta 2 final: `161,71`.

Além do baseline, uma simulação com `alteracoes={}` deve produzir registros e métricas
idênticos à base. O teste chama as mesmas funções usadas pelos endpoints, sem duplicar
as fórmulas CNJ na suíte.
