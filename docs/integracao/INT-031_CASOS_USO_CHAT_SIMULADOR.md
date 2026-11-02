# Casos de uso autorizados entre chat e simulador

## Fronteiras

| Categoria | Exemplos | Destino autorizado |
|---|---|---|
| Pergunta processual | movimentação, partes, assunto, valor, situação | Agentes processuais e repositório; nunca simulador |
| Consulta de processo | número CNJ informado | Repositório/coletor processual; nunca simulador |
| Impacto do processo em Meta 1/2 | “este processo pesa na Meta 1?” | Regras determinísticas do coletor sobre o processo ativo |
| Cenário agregado CNJ | alteração mensal de julgados, dessobrestados ou suspensos | API real do simulador |
| Comparação de cenários | comparar conjuntos explícitos de alterações | API real do simulador |
| Otimização agregada | ajuste mínimo de variável/mês para meta-alvo | API real do simulador |

## Regras de autorização

1. Menção genérica a “meta” não autoriza criar cenário nem escolher parâmetros.
2. Perguntas processuais não são desviadas para o simulador agregado.
3. Diagnóstico de um processo usa apenas dados do processo e regras oficiais já
   implementadas; não usa projeções agregadas como se fossem fatos processuais.
4. Simulação exige `meta_id`, ano e cenário explícitos. Campos ausentes geram pedido de
   esclarecimento ou erro, nunca números presumidos.
5. Resultados agregados devem identificar premissas e origem; ausência do motor ou dos
   dados produz indisponibilidade transparente.
6. O LLM pode explicar resultados calculados, mas não calcula percentuais, não escolhe
   movimentos e não inventa regras CNJ.

## Casos proibidos

- inferir impacto processual a partir da Meta 1/2 agregada;
- chamar o simulador para perguntas sobre partes ou movimentações;
- retornar `not_integrated` como se fosse cálculo;
- completar cenário, unidade, mês, variável ou meta-alvo sem informação do usuário;
- recomendar registro processual que não corresponda a ato realmente praticado.
