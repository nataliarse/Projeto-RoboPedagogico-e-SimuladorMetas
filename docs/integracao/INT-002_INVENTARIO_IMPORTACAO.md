# INT-002 — Inventário da importação em quarentena

## Origem e destino

- Snapshot recebido: `TCC-Simulador-CNJ`.
- Destino isolado: `integracao_entrada/TCC-Simulador-CNJ/`.
- Estratégia: inclusão exclusivamente aditiva, sem sobreposição com caminhos existentes.

## Inventário físico

- 69 arquivos, totalizando 665.467 bytes.
- 35 arquivos TypeScript, 6 JSON, 6 Markdown, 5 CSS, 5 HTML, 4 XLSX, 2 Python e 6 arquivos de configuração/imagem/texto.
- Nenhum link simbólico ou ponto de junção.
- Nenhum `node_modules`, ambiente virtual, `.env`, chave privada ou arquivo com nome indicativo de credencial.
- A busca textual por padrões comuns de segredo não encontrou ocorrência, desconsiderando lockfile e binários.
- As quatro planilhas contêm séries temporais agregadas de casos novos, julgados, suspensos e dessobrestados; a inspeção dos textos internos não encontrou identificadores processuais ou pessoais.

## Estrutura importada

| Caminho | Conteúdo |
|---|---|
| `backend/` | FastAPI do simulador, motor de cálculo, requisitos e quatro planilhas de dados agregados |
| `frontend/meu-primeiro-app/` | Aplicação Angular principal recebida, configuração, testes e recursos visuais |
| `frontend/meu-primeiro-app/simulador-metas/` | Segunda árvore-fonte Angular parcial recebida no snapshot |
| `Checklist_Melhorias_Correcoes_Simulador.md` | Checklist histórica do simulador |
| `INTEGRACAO_MINIMA.md` | Instruções mínimas de execução do snapshot |
| `PENDENCIAS_SIMULADOR.md` | Pendências conhecidas do snapshot |
| `RELATORIO_DIAGNOSTICO_INTEGRACAO.md` | Diagnóstico anterior do simulador |

## Exceção de versionamento identificada

A regra genérica `models/` do `.gitignore` da raiz ignora três arquivos TypeScript legítimos sob `src/app/core/models/`. Eles fazem parte do snapshot e serão adicionados explicitamente neste commit para preservar a importação integral. A correção estrutural da regra pertence ao `INT-008`.

Cinco arquivos do snapshot contêm whitespace legado. Para não modificar os bytes recebidos, `.gitattributes` desativa somente `blank-at-eol` e `blank-at-eof` nesses caminhos exatos enquanto estiverem na quarentena. A exceção não alcança o código atual nem futuros destinos definitivos.

## Evidência do aceite

Antes do staging, `git status` mostrou somente `?? integracao_entrada/TCC-Simulador-CNJ/` para este caminho. Assim, todo o conteúdo deste item é aditivo. Os arquivos existentes e as mudanças preexistentes fora da quarentena não foram alterados nem incluídos.
