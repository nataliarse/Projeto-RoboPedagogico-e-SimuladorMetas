# Auditoria e metodologia da Meta 2 A/ANT

## Referência normativa

A regra implementada para ANT/TRTs segue o **Glossário das Metas Nacionais do Poder Judiciário 2026 — Justiça do Trabalho, versão 1**, publicado pelo CNJ em janeiro de 2026:

`https://www.cnj.jus.br/wp-content/uploads/2026/01/glossario-metas-nacionais-do-poder-judiciario-2026-justica-do-trabalho-versao-1.pdf`

Fórmula oficial:

`Cumprimento antigos TRTs = (Σjulgadom2_ant / (Σdism2_ant − Σsusm2_ant − Σdesm2_ant)) × (1000 / 9,9)`

O glossário também informa que as variáveis de cada carga DataJud já são consolidadas. Cargas mensais sucessivas não devem ser somadas novamente. Fluxos mensais só podem ser acumulados quando o dataset os declarar expressamente.

## Separação entre regra e dados

`services/meta2_groups.py` separa:

- fórmula oficial de 2026;
- valores brutos das séries preservadas;
- proveniência e homologação;
- semântica temporal por variável;
- classificação do resultado apresentado.

Semânticas aceitas:

- `carga_consolidada`: utiliza o valor da carga correspondente;
- `fluxo_mensal`: acumula os eventos do ano;
- `indefinida`: impede o cálculo, sem heurística ou conversão silenciosa.

Denominador não positivo, entrada não finita ou semântica indefinida produz `null`. Não existe piso, substituição por zero ou fallback para outro indicador.

## Estado das séries embutidas

As séries recebidas da Equipe B continuam preservadas para comparação histórica, mas não possuem extrato de origem, versão do modelo ARIMA, hash de fonte ou homologação verificável.

- Grupo A: mantém o cálculo demonstrativo anterior, incluindo o resultado final `104,63%`, e é rotulado como `Simulação com dados não homologados`.
- Grupo ANT: a semântica das constantes está marcada como `indefinida`; o resultado permanece `null` e é rotulado como `Indicador pendente de validação`.
- `D=72`, julgados `22`, suspensos `28` e dessobrestados de dezembro `24` não foram alterados.
- Os acumulados históricos continuam disponíveis para comparação, mas não alimentam ANT enquanto a semântica da fonte estiver indefinida.
- A Meta 2 agregada anterior permanece independente.

## Origem do valor reportado de 110%

O valor é reproduzível com a regra histórica:

`22 / (72 − 28 − 24) × 100 = 110,00%`

Esse cenário explica a origem do número, mas não define a regra oficial de 2026. Com as mesmas entradas e o fator oficial:

`22 / (72 − 28 − 24) × (1000 / 9,9) = 111,11%`

Nenhum dos dois valores é apresentado como oficial porque as entradas não estão homologadas e o significado temporal de `24` não foi comprovado.

## Contrato de validação

Cada resultado A/ANT informa:

- `homologado`;
- `status_validacao`: `homologado`, `demonstrativo` ou `pendente_validacao`;
- `mensagem_validacao`;
- `proveniencia`;
- `semantica_temporal` de julgados, suspensos e dessobrestados.

Os campos anteriores do contrato foram preservados. Os novos campos são aditivos.

## Condição para homologação futura

Um resultado só pode ser classificado como homologado quando houver, conjuntamente:

1. fonte identificada e versionada;
2. declaração explícita da semântica temporal das três variáveis;
3. aprovação/homologação registrada da fonte;
4. coorte ANT compatível com processos distribuídos até 31/12/2021;
5. cálculo com o fator `1000/9,9` e denominador válido.

Testes e snapshots confirmam comportamento de software, mas não substituem homologação dos dados.
