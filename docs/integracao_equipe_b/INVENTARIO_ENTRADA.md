# Inventário da entrega da Equipe B

## Escopo e método

Fonte auditada, sem modificações: `integracao_entrada/TCC-Simulador-CNJ/`.

Inventário realizado em 23/10/2026 com listagem recursiva, tamanho, extensão, SHA-256 para detecção de duplicatas, inspeção de símbolos/rotas, metadados das planilhas em modo somente leitura e busca por nomes/conteúdo indicativos de segredo. A busca por segredo foi limitada a padrões conhecidos e não substitui revisão de proveniência.

## Resumo físico

- 111 arquivos, total de 6.417.329 bytes.
- Código-fonte principal: 40 TypeScript, 3 Python, 7 CSS e 6 HTML.
- Dados/binários: 9 planilhas XLSX, 4 PNG e 2 ICO.
- Artefatos gerados: `backend/__pycache__/` e `frontend/meu-primeiro-app/dist/`, incluindo 2 JavaScript, 12 source maps e 2 bytecodes Python.
- Lockfiles/configuração: `package-lock.json`, `package.json`, `angular.json`, `proxy.conf.json`, arquivos TypeScript e configurações `.vscode/`.
- Duas árvores Angular coexistem: o app em `frontend/meu-primeiro-app/src/app/` e uma cópia anterior em `frontend/meu-primeiro-app/simulador-metas/src/app/`.

## Matriz fonte → função → ação

| Fonte | Função observada | Ação |
|---|---|---|
| `backend/main.py` | FastAPI com base/simulação/comparação, quanto-falta e Meta 2 | `referência` e porte seletivo após gates; nunca sobrescrever o serviço canônico |
| `backend/meta2_service.py` | Séries, projeção fixa e fórmulas A/ANT | `referência`; auditar premissas na EB-007 antes de habilitar |
| `backend/robo_cnj_meta2.py` | ETL, fórmulas, cenários, otimizador, gráficos e exportação | `referência`; não executar contra fontes externas nem portar em bloco |
| `backend/requirements.txt` | FastAPI 0.95.2/Pydantic 1.10.26 e stack de dados | `não importar`; comparar compatibilidade e manter isolamento do chatbot |
| `backend/dados/dados simulador meta1.xlsx` | Série de 85 linhas e 5 colunas para Meta 1 | `referência/fixture candidata`; proveniência e conteúdo exigem auditoria numérica |
| `backend/dados/{casos_novos,dessobrestados,julgados,suspensos}.xlsx` | Séries e forecasts candidatos | `referência`; não versionar nem apresentar como dados atuais sem proveniência |
| `backend/dados/antigos/*.xlsx` | Cópias byte a byte dos quatro arquivos homônimos | `não importar`; duplicatas preservadas somente na fonte |
| `frontend/meu-primeiro-app/src/app/features/quanto-falta/` | Calculadora de esforço mensal | `portar` seletivamente após GATE-M1 |
| `frontend/meu-primeiro-app/src/app/features/meta2/` | UI A/ANT | `portar` seletivamente, oculta enquanto GATE-M2 estiver bloqueado/pendente |
| `frontend/meu-primeiro-app/src/app/features/grafico-cenarios/` | Comparação gráfica | `portar` sem duplicar fórmulas no navegador |
| `frontend/meu-primeiro-app/src/app/core/services/cenarios-recentes.service.ts` | Até três cenários por meta em `localStorage` | `portar` seletivamente com testes e dados não sensíveis |
| `frontend/meu-primeiro-app/src/app/core/services/meta2-api.service.ts` | Cliente de `/api/meta2` | `referência`; adaptar ao namespace canônico `/api/simulador/*` |
| `frontend/meu-primeiro-app/src/app/features/chat/` e `core/services/chat.ts` | Chat mock, endpoint `/api/chat` e `responderMock()` em sucesso/erro | `não importar` |
| `frontend/meu-primeiro-app/simulador-metas/` | Cópia Angular anterior/parcial | `não importar`; usar apenas para comparação histórica |
| `frontend/meu-primeiro-app/dist/` | Build compilado e source maps | `não importar` |
| `frontend/meu-primeiro-app/package*.json`, `angular.json`, `proxy.conf.json` | Manifestos e configuração do app importado | `referência`; não substituir configuração canônica |
| `.vscode/`, `__pycache__/`, `*.pyc` | Configuração local e artefatos gerados | `não importar` |
| `evidencias-auditoria/*.png` | Capturas da entrega | `referência`; não usar como substituto de teste |
| Documentos Markdown da fonte | Alegações, pendências e histórico sem Git verificável | `referência`; validar toda alegação no checkout canônico |

## Duplicatas confirmadas por SHA-256

- Os quatro XLSX em `backend/dados/antigos/` são idênticos aos homônimos do diretório pai.
- Favicon e logotipo do `dist/` são idênticos aos de `public/`.
- `dados.service.ts` e `tabela.component.ts` possuem cópias idênticas nas duas árvores Angular.

## Dados e riscos

- As planilhas não têm nomes de arquivos indicativos de dados pessoais, mas a proveniência não está documentada de modo suficiente; ficam fora dos commits até decisão específica.
- Algumas planilhas informam `max_row=1048576`, provável formatação até o limite do Excel, portanto esse valor não comprova um milhão de registros úteis.
- `meta2_service.py` contém `PROJECAO_ARIMA` e `RESULTADO_2025` fixos; devem ser rotulados como projeção/constante e auditados.
- A fonte declara Meta 2 provisória e registra dúvida sobre o denominador/piso da Meta 1.
- O frontend usa Chart.js via objeto global/CDN; a integração canônica não deve depender de rede externa sem decisão explícita.

## Segredos e exclusões

- Nenhum arquivo `.env`, PEM, chave privada ou nome contendo credencial/segredo/token/senha foi encontrado.
- A busca textual, por nome de arquivo apenas no resultado, não encontrou padrões de chave de API, senha atribuída, token atribuído, chave privada ou credencial AWS nos arquivos textuais.
- `integracao_entrada/` está integralmente ignorada pela regra `/integracao_entrada/` do `.gitignore` do projeto-base.
- Nada da fonte deve ser staged; somente código reimplementado, testes e documentação do destino poderão entrar em commits posteriores.
