# Integração mínima Angular + FastAPI

## Objetivo e estado

O fluxo previsto é carregar a base da API, criar cenários pela API e apresentar os mesmos resultados em indicadores, comparação e gráficos em `/simulador`. A API e o roteiro funcional foram executados localmente. A execução integrada pelo endereço do frontend não pôde ser comprovada nesta máquina porque Node.js/npm e `node_modules` não estão disponíveis; a preparação do workspace e do proxy está concluída.

## Execução local

Use dois terminais a partir da raiz deste projeto.

Backend (Python 3.12.10, porta 8000):

```powershell
cd backend
# Somente se o ambiente ainda não contiver as dependências:
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend (porta 4200):

```powershell
cd frontend\meu-primeiro-app
npm install
npm start
```

Abra `http://localhost:4200/simulador`. O script `start` carrega `proxy.conf.json`, que encaminha somente `/api/base`, `/api/simular` e `/api/health` para `http://localhost:8000`. `/api/chat` não é enviado ao simulador; seu destino real ainda precisa ser configurado.

## Fluxo demonstrável

1. Abrir `/simulador` e aguardar a base.
2. Conferir os indicadores e a linha `Base` nas abas Meta 1 e Meta 2.
3. Na Meta 1, criar um cenário sem alterações.
4. Criar outro cenário com `+100` em Julgados para Out/2026.
5. Comparar os cenários e o gráfico; remover um cenário e confirmar que Base e o cenário restante permanecem.

Meta 2 é apresentada como resultado provisório. A aba do otimizador está desabilitada e identificada como pendente.

## Alterações desta intervenção

- Recuperado `frontend/meu-primeiro-app/angular.json` do arquivo original `TCC-Simulador-CNJ.rar`.
- Tornado explícito o uso do proxy no script `npm start`.
- Restringido o proxy às rotas usadas pelo simulador, sem capturar o chat.
- Criado `backend/requirements.txt` apenas com as seis dependências importadas pela API e versões verificadas no ambiente.
- Criados estes registros de entrega e pendências.

Já existiam no material recebido: API, planilhas, script original, modelos e serviços Angular, integração base/simulação, estado de cenários e telas de indicadores, comparação e gráficos. Essas contribuições foram preservadas; não há histórico Git interno no recorte para atribuir autoria individual.

## Verificações realizadas

- API iniciada com Uvicorn e exercitada por HTTP em `127.0.0.1:8010`, pois a porta 8000 já estava ocupada por outro serviço.
- `GET /api/base`: HTTP 200, JSON e 86 registros; metas finais 109,86 e 161,71.
- `POST /api/simular` vazio: resposta idêntica à base.
- `+100` julgados em 2026-10: valor mensal passou de 15.595,083374 para 15.695,083374 e a Meta 1 do mês retornou 110,91.
- Cenário distinto com `+100` suspensos não herdou os julgados do cenário anterior; novo `GET /api/base` permaneceu idêntico.
- Valor fracionário inválido foi rejeitado com HTTP 422.
- A resposta contém métricas `null`; a apresentação usa travessão/estado não calculável, sem convertê-las em zero.
- Inspeção do estado confirmou que indicadores, comparação e gráficos derivam das respostas guardadas por cenário; Base não oferece ação de remoção.
- JSON de `angular.json`, `package.json` e `proxy.conf.json` validado.
- Planilhas, `backend/robo_cnj_meta2.py` e fórmulas de `backend/main.py` não foram alterados nesta etapa.

Não executados: compilação Angular, navegador e `GET /api/base` por `localhost:4200`. Requisitos ausentes: runtime Node.js/npm e dependências `node_modules`. Após disponibilizá-los, executar `npm install`, `npm run build` e o roteiro acima. A ausência impede afirmar compilação ou demonstração integrada completa neste ambiente.
