# Relatório de diagnóstico da integração Angular + FastAPI

## Parecer

**APTO COM RESSALVAS para o escopo da apresentação.** Na execução complementar de 2026-10-02, o ambiente foi preparado, o frontend compilou, os testes passaram e o fluxo integrado foi demonstrado em Chrome headless. Base, cenários, remoção, comparação, gráficos, `null`, erro controlado, Meta 2 provisória e otimizador desabilitado foram verificados. A ressalva visual é que os valores numéricos das barras usam a mesma cor verde do preenchimento e ficam com contraste insuficiente, embora estejam presentes e corretos no DOM. As limitações metodológicas já registradas continuam válidas.

O parecer original desta auditoria foi **INCONCLUSIVO** por ausência de Node/frontend e conflito da porta 8000. Ele permanece documentado abaixo como histórico; a execução complementar resolveu os bloqueios ambientais sem encerrar o serviço preexistente.

## Identificação da auditoria

- Data: 2026-10-02 (America/Sao_Paulo).
- Diretório avaliado: `C:\Users\filipe.duarte\Desktop\TCC-Simulador-CNJ\TCC-Simulador-CNJ`.
- Sistema/shell: Windows, PowerShell.
- Python: 3.12.10.
- Dependências do backend encontradas nas versões do manifesto: FastAPI 0.95.2, pandas 3.0.2, Uvicorn 0.21.1 e openpyxl 3.1.5; NumPy também pôde ser importado.
- Node/npm/ng: indisponíveis no PATH e não encontrados nos caminhos usuais consultados.
- Ambiente virtual: não encontrado na árvore do projeto.
- Git: o projeto não possui repositório Git próprio. O Git resolveu o topo para `C:\Users\filipe.duarte\Desktop`, repositório sem commits (`master`, “No commits yet”), e toda a pasta do projeto aparece como não rastreada. Portanto, não existe commit do projeto nem diff Git confiável para atribuir alterações internas.
- AGENTS.md: nenhum arquivo aplicável encontrado na árvore auditada.

## Árvore efetivamente ativa

O `angular.json` define `sourceRoot: "src"` e o alvo de build usa `src/main.ts`, que importa `src/app/app.ts`. Portanto, a árvore compilada é `frontend/meu-primeiro-app/src/app/`. A pasta `frontend/meu-primeiro-app/simulador-metas/` é uma cópia secundária e não integra o build configurado.

O backend ativo é `backend/main.py`. Ele foi carregado via `uvicorn main:app`; o script legado `backend/robo_cnj_meta2.py` não foi importado nem executado.

As quatro planilhas existem em `backend/dados/`, são legíveis por pandas e têm 86 linhas cada: `casos_novos.xlsx`, `julgados.xlsx`, `dessobrestados.xlsx` e `suspensos.xlsx`. Não foram modificadas.

## Configuração e comandos reais

- Backend previsto pelo projeto, a partir de `backend/`: `python -m uvicorn main:app --host 127.0.0.1 --port 8000` (ou `python main.py`).
- Backend usado na auditoria, a partir de `backend/`: `python -m uvicorn main:app --host 127.0.0.1 --port 8001`. A troca foi necessária porque a porta 8000 estava ocupada; não houve alteração de código ou configuração.
- Frontend previsto, a partir de `frontend/meu-primeiro-app/`: `npm start`, que executa `ng serve --proxy-config proxy.conf.json` na porta padrão 4200.
- Build previsto: `npm run build`.
- Testes previstos: `npm test`.
- Proxy: `/api/base`, `/api/simular` e `/api/health` para `http://localhost:8000`. `/api/chat` não consta no proxy.

Antes da apresentação, a ocupação da porta 8000 precisa ser resolvida de modo controlado ou backend e proxy precisam ser configurados para uma porta livre. O processo preexistente não foi encerrado e não pôde ser identificado por falta de permissão para consultar sua linha de comando.

## Verificações executadas

| Verificação | Resultado | Evidência |
|---|---|---|
| Leitura de instruções aplicáveis | PASSOU | Nenhum `AGENTS.md` encontrado no projeto. |
| Identificação da árvore Angular ativa | PASSOU | `angular.json` → `sourceRoot: src`; `src/main.ts` importa `src/app/app.ts`. |
| Preservação do script legado | PASSOU | `robo_cnj_meta2.py` não foi importado/executado. |
| Disponibilidade e leitura das planilhas | PASSOU | Quatro arquivos presentes e legíveis; 86 linhas em cada. |
| Compilação sintática do backend | PASSOU | `python -m compileall -q backend` retornou sucesso. |
| Inicialização do backend do projeto | PASSOU | Uvicorn iniciou em `127.0.0.1:8001`; processo criado pela auditoria. |
| `GET /api/health` direto | PASSOU | HTTP 200, JSON `{"status":"ok","registros":86}` na porta 8001. |
| `GET /api/base` direto | PASSOU | HTTP 200, `application/json`, 86 registros, `meta1_final=109.86`, `meta2_final=161.71`. |
| Datas e tipos do contrato | PASSOU | Datas em `YYYY-MM`; valores centrais numéricos; 26 registros com resultado indisponível representado por `null`. |
| Meta final do ano configurado | PASSOU | 12 registros de 2026; os finais coincidem com a linha 2026-12, apesar de a base continuar até 2027-02. |
| Cenário vazio | PASSOU | `POST /api/simular` com `{"alteracoes":{}}` devolveu JSON exatamente igual ao Base. |
| Incremento de +100 julgados em 2026-10 | PASSOU | Julgados passaram de 15595.083374 para 15695.083374 somente no registro 2026-10; finais 109.92 e 161.80. |
| Preservação de entradas não alteradas | PASSOU | A única diferença nos quatro campos de entrada foi `2026-10:julgados`. |
| Delta negativo e piso zero | PASSOU | Delta -999999 em julgados de 2026-10 resultou em 0.0. |
| Imutabilidade da base | PASSOU | `GET /api/base` posterior foi exatamente igual ao inicial. |
| Validação: mês inválido | PASSOU | `2026-13` → HTTP 422 com mensagem de formato/mês inválido. |
| Validação: mês ausente | PASSOU | `2099-01` → HTTP 422 com mensagem de mês não disponível. |
| Validação: `null` explícito | PASSOU | HTTP 422, valor nulo não permitido. |
| Validação: incremento fracionário | PASSOU | HTTP 422, inteiro inválido. |
| Validação: booleano | PASSOU | HTTP 422, inteiro inválido. |
| Validação: variável desconhecida | PASSOU | HTTP 422, campo extra não permitido. |
| Rota `/api/chat` no backend do simulador | PASSOU | POST sem conteúdo de usuário real → HTTP 404; não foi redirecionado ao simulador nem houve processamento de chatbot. |
| Otimizador não executado | PASSOU | Nenhuma chamada a `/api/otimizador`; botão ativo está marcado `desabilitada: true`. |
| Build Angular | NÃO EXECUTADO | Node/npm/ng indisponíveis e `node_modules` ausente. Não se instalou runtime ou estrutura nova. |
| Testes unitários Angular | NÃO EXECUTADO | Mesma limitação de runtime/dependências. |
| Frontend em `/simulador` | NÃO EXECUTADO | Nada escutando em `127.0.0.1:4200`; conexão recusada. |
| `GET /api/base` pelo endereço do frontend | NÃO EXECUTADO | Frontend indisponível; portanto não foi possível confirmar JSON em vez de `index.html`. |
| Fluxo visual de cenários, remoção, comparação e gráficos | NÃO EXECUTADO | Sem build/servidor frontend; presença de Playwright/Selenium em Python não substitui uma aplicação servida. |
| Falha controlada de conexão/validação na tela | NÃO EXECUTADO | Não foi possível abrir a interface; nenhum serviço de terceiro foi interrompido. |

## Comparação Base e cenários

| Caso | API direta | Interface |
|---|---|---|
| Base | 86 registros; Meta 1 109.86%; Meta 2 161.71% | NÃO EXECUTADO |
| Cenário vazio | Idêntico ao Base, HTTP 200 | NÃO EXECUTADO |
| +100 julgados em 2026-10 | Registro correto +100; Meta 1 109.92%; Meta 2 161.80% | NÃO EXECUTADO |

Os números acima são evidência desta execução e não metas fixas esperadas para versões futuras das planilhas.

## Leitura estática da integração

- A tela ativa chama `SimuladorApiService.carregarBase()` e `SimuladorApiService.simular()`; os cenários visíveis recebem a resposta HTTP e não um resultado local.
- `DadosService`, uma base local estimada e fórmulas TypeScript ainda são construídos no `SimuladorService`, mas o fluxo ativo de Base/criação de cenário não os usa como fallback. Eles permanecem alcançáveis pelo código do otimizador legado, cuja aba ativa está desabilitada e cujo componente não é importado pelo shell.
- Erros HTTP são convertidos em mensagem visível. O Base só é considerado pronto depois da resposta da API, e erro não cria cenário.
- O botão de adicionar cenário é desabilitado enquanto o sinal global `carregando` está ativo; isso cobre bloqueio durante a solicitação no fluxo atual.
- `null` é tipado e formatado como travessão/“Não calculável”, sem conversão visual intencional para zero no Base, comparação e barras.
- A Meta 2 aparece como “resultado provisório”, com aviso explícito sobre validação metodológica e dados por coorte pendentes.
- A aba “Otimizador (pendente)” tem atributo `disabled`.
- Os gráficos dependem de Chart.js carregado por CDN. O código prevê uma mensagem de indisponibilidade se `window.Chart` não existir, mas o carregamento e a atualização real não foram executados.
- `/api/chat` não foi redirecionado ao simulador no backend. Contudo, a rota também não está no proxy Angular; o comportamento no servidor de desenvolvimento não foi executado e o chatbot não funcionará por esse proxy sem configuração/serviço próprio. Isso está fora do fluxo de demonstração auditado.

## Problemas e recomendações

### Bloqueante para o parecer de prontidão — ambiente não permite validar o frontend

- Prioridade: bloqueante para a auditoria/apresentação neste computador.
- Reprodução: `node --version`, `npm --version` e `ng` não são reconhecidos; `http://127.0.0.1:4200/simulador` recusa conexão.
- Esperado: runtime compatível com o lockfile, dependências restauradas sem alterar o lock, build/testes concluídos e servidor Angular acessível.
- Observado: nenhum runtime Node utilizável, nenhum `node_modules` e nenhuma interface servida.
- Evidência/área: `frontend/meu-primeiro-app/package.json`, `package-lock.json`, `angular.json`; execução no ambiente.
- Impacto: impede comprovar todos os critérios visuais e a integração pelo frontend.
- Menor correção: disponibilizar uma versão do Node aceita pelo lock (`^20.19.0`, `^22.12.0` ou `>=24.0.0` para os pacotes Angular), executar `npm ci` no diretório do frontend e então `npm test`, `npm run build` e `npm start`, sem atualizar o lockfile.

### Bloqueante no ambiente padrão — porta 8000 ocupada por outra aplicação

- Prioridade: bloqueante para executar os comandos atuais da demonstração.
- Reprodução: iniciar Uvicorn na porta 8000 gera WinError 10048; `GET :8000/api/health` devolve `{"status":"ok"}` sem `registros`; `GET :8000/api/base` devolve 404.
- Esperado: a API deste projeto escutando na porta para a qual o proxy aponta.
- Observado: serviço preexistente diferente ocupa 8000; seu processo não foi encerrado.
- Evidência/área: execução; `frontend/meu-primeiro-app/proxy.conf.json`; `backend/main.py`.
- Impacto: o frontend receberia 404 em `/api/base` e mostraria erro em vez da simulação.
- Menor correção: antes da apresentação, identificar e encerrar/mover legitimamente o serviço conflitante, ou escolher uma porta livre para este backend e alterar o alvo do proxy de forma coordenada. Revalidar por HTTP através da porta 4200.

### Importante — duplicação local ainda existe no serviço ativo

- Classificação: constatação estática; não causou divergência no fluxo HTTP testado.
- Reprodução: inspecionar o construtor e os métodos `montarBase`, `calcularMetas`, `simularCenario` e `encontrarAjusteMinimo` em `simulador.service.ts`.
- Esperado no escopo: o fluxo ativo não substituir a resposta da API por `DadosService`/fórmulas TypeScript.
- Observado: Base e cenários usam a API, mas a base/fórmulas locais continuam instanciadas e ligadas ao método local do otimizador.
- Impacto: risco futuro de reativar cálculo divergente por engano; não é bloqueante enquanto a aba permanecer desabilitada.
- Menor correção: após a apresentação, remover ou isolar o caminho local quando houver autorização para refatorar. Não foi modificado nesta auditoria.

### Posterior — `/api/chat` não está coberto pelo proxy Angular

- Classificação: leitura estática; fora do fluxo do simulador e não executado no frontend.
- Reprodução: comparar `ChatService` (`POST /api/chat`) com `proxy.conf.json`, que só lista base/simular/health.
- Esperado: chat apontar para seu backend próprio, se fizer parte de outra demonstração; em qualquer caso, não redirecionar ao simulador.
- Observado: a API do simulador responde 404, e o proxy não declara `/api/chat`.
- Impacto: possível falha do chat, mas não falseia os cálculos do simulador.
- Menor correção: definir explicitamente o backend do chat ou documentá-lo como indisponível; não mapear a rota ao simulador.

## Limitações metodológicas herdadas e previstas

- Meta 1: permanece o piso do denominador em `backend/main.py`, função `calcular_meta1`: após calcular `novos + dessobrestados - suspensos`, aplica-se como piso `novos + dessobrestados`. Para suspensos não negativos, isso neutraliza sua subtração. A mesma regra existe no código TypeScript legado. É pendência metodológica; a auditoria não alterou nem certificou a fórmula como oficial do CNJ.
- Meta 2: o backend define “distribuídos” como casos novos e usa julgados gerais, sem dados específicos da coorte de processos antigos. Além disso, no cálculo mensal usa suspensos do mês contra distribuídos acumulados. O resultado deve continuar tratado como provisório, como a interface já sinaliza. Não há base para certificar conformidade oficial.
- Otimizador: endpoint e componentes legados existem, mas a execução foi deliberadamente excluída; a aba apresentada ao usuário está desabilitada, conforme o escopo.
- Gráfico: depende de recurso externo (CDN) e pode exibir “Gráfico indisponível” sem rede. Não foi possível testar o comportamento visual neste ambiente.

## Pendências por área

- Ambiente: instalar/disponibilizar Node compatível; restaurar dependências com `npm ci`; resolver a porta 8000.
- Frontend: executar build/testes e todos os cenários visuais; conferir payloads de rede contra indicadores; confirmar erro controlado; confirmar o proxy retornando JSON.
- Backend: contrato principal testado e aprovado; manter validações estritas. A rota de otimizador não foi avaliada por escopo.
- Dados/metodologia: validar formalmente o piso da Meta 1 e obter dados de coorte apropriados à Meta 2 antes de qualquer alegação de conformidade CNJ.
- Git/rastreabilidade: colocar o projeto em um repositório próprio ou registrar um commit/artefato identificável antes da entrega, para permitir auditoria reprodutível.

## Conclusão

Há evidência robusta de que o backend atual lê as planilhas, calcula o ano configurado, simula incrementos e rejeita entradas malformadas sem HTTP 500 nem mutação da base. Há também evidência estática de que Meta 2 está rotulada como provisória e o otimizador está bloqueado na interface.

Não há evidência executada da compilação Angular, do proxy, da tela, dos cenários independentes, da remoção, dos gráficos ou do tratamento visual de falhas. Somada ao conflito real na porta configurada, essa lacuna impede declarar o fluxo completo apto. Depois de corrigir o ambiente, toda a seção visual e o acesso `/api/base` via `localhost:4200` devem ser repetidos antes da apresentação.

---

## Execução complementar — preparação e validação visual

### Ambiente preparado

- Data: 2026-10-02.
- Node.js: 22.22.0, distribuição oficial ZIP x64, extraída em `.tools/node-v22.22.0-win-x64`; não houve instalação global nem alteração permanente do PATH.
- npm: 10.9.4, fornecido pela distribuição local do Node.
- Dependências: `npm ci --no-audit --no-fund`, usando o `package-lock.json` existente e cache em `.tools/npm-cache`. `npm ls --depth=0` terminou sem dependências ausentes.
- Angular: CLI 21.2.22; pacotes resolvidos conforme o lockfile. O lockfile não foi regenerado deliberadamente.
- Navegador: Google Chrome local em modo headless, dirigido pelo Playwright já instalado.
- Backend do simulador: `127.0.0.1:8001`.
- Frontend: `127.0.0.1:4200`.
- O serviço preexistente da porta 8000 foi preservado.

Fonte da versão do runtime: a distribuição Node.js 22.22.0 foi escolhida porque satisfaz a faixa `^22.12.0` exigida pelos pacotes Angular registrados no lockfile.

### Alterações mínimas realizadas

- `frontend/meu-primeiro-app/proxy.conf.json`: apenas os alvos de `/api/base`, `/api/simular` e `/api/health` passaram de `localhost:8000` para `127.0.0.1:8001`. `/api/chat` continuou separado e sem redirecionamento para o simulador.
- `frontend/meu-primeiro-app/README.md`: adicionados os comandos coordenados da API e do frontend.
- Cinco specs tiveram somente nomes de classes desatualizados corrigidos: `AppComponent`, `ChatService`, `LocalStorageService`, `StateService` e `ChatComponent`. O spec do componente de chat também fornece `HttpClient`, e simula `scrollIntoView`, ausente no jsdom.
- `.tools/ui_audit.py`: automação de auditoria visual reproduzível.
- `evidencias-auditoria/simulador-graficos.png` e `evidencias-auditoria/simulador-falha-controlada.png`: capturas pequenas da execução.
- Nenhuma fórmula, planilha, componente de produção, lockfile ou rota do backend foi alterada. O ajuste incidental de analytics feito pelo primeiro `ng serve` foi removido de `angular.json`.

### Comandos da execução complementar

No backend:

```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

No frontend, com o diretório da distribuição local do Node no PATH da sessão:

```powershell
cd frontend\meu-primeiro-app
npm ci --no-audit --no-fund
npm run build
npm test -- --watch=false
npm start -- --host 127.0.0.1 --port 4200
```

Abrir `http://127.0.0.1:4200/simulador`.

### Build e testes

| Verificação | Resultado | Evidência |
|---|---|---|
| `npm ci` | PASSOU | Árvore completa; `npm ls --depth=0` sem `UNMET DEPENDENCY`. |
| Build de produção | PASSOU | Bundle inicial 331,22 kB; saída em `dist/meu-primeiro-app`. |
| Orçamento de CSS | PASSOU COM AVISO | `chat.css` tem 5,34 kB, 1,34 kB acima do limite de aviso; não excede o limite de erro e está fora do simulador. |
| Testes Angular/Vitest | PASSOU | 6 arquivos, 7 testes, execução única. |
| Servidor Angular | PASSOU | Bundle de desenvolvimento servido em `127.0.0.1:4200`. |

As primeiras tentativas de build/teste dentro do sandbox falharam com `spawn EPERM`; repetidas com permissão para o processo auxiliar do esbuild, chegaram ao compilador. A suíte então revelou specs com imports gerados obsoletos; após a correção localizada descrita acima, passou integralmente.

### Validação HTTP e visual executada

| Verificação | Resultado | Evidência atual |
|---|---|---|
| `/simulador` abre | PASSOU | HTTP 200 e tela renderizada no Chrome headless. |
| `/api/base` pelo frontend | PASSOU | HTTP 200, `application/json`, 86 registros; não retornou `index.html`. |
| Indicadores Base versus API | PASSOU | API 109.86% / 161.71%; tela 109,86% / 161,71%. |
| Cenário sem alteração | PASSOU | Payload exatamente igual ao Base; linha visível com o mesmo resultado. |
| +100 julgados em 2026-10 | PASSOU | Payload mostrou delta 100.0 no registro; resultado final exibido igual ao HTTP. |
| Dois cenários independentes | PASSOU | Ambos ficaram simultaneamente visíveis com respostas próprias. |
| Remoção de cenário | PASSOU | Cenário vazio removido; Base e “Mais 100 julgados” preservados. |
| Comparação tabular | PASSOU | Resultados finais conferidos com os payloads. |
| Gráfico de linhas | PASSOU | Chart.js carregado; canvas, Base e cenário visíveis; nenhuma mensagem de indisponibilidade. |
| Gráfico de barras | PASSOU COM RESSALVA | DOM contém Base 109.86% e cenário 109.92%, coerentes com a API; texto verde sobre barra verde tem contraste insuficiente. |
| `null` | PASSOU | Resposta de Base interceptada localmente com `meta1_final: null`; KPI mostrou travessão e linha mostrou “Não calculável”, não zero. Depois o interceptador foi removido e a base real restaurada. |
| Meta 2 provisória | PASSOU | Título e aviso de validação/coorte visíveis. |
| Otimizador desabilitado | PASSOU | Botão “Otimizador (pendente)” com estado disabled. |
| Bloqueio durante requisição | PASSOU | Botão ficou desabilitado durante atraso controlado de 1 segundo. |
| Erro controlado | PASSOU | Somente o POST do navegador foi abortado; mensagem de conexão visível, nome preservado e nenhum cenário fictício criado. |
| Restauração após falha | PASSOU | Interceptação retirada; o mesmo formulário produziu HTTP 200 e criou o cenário. |

O único erro de console capturado foi `net::ERR_FAILED`, esperado e restrito à requisição intencionalmente abortada. Nenhum serviço foi parado para provocar a falha.

### Problema visual não bloqueante confirmado

- Prioridade: importante, não bloqueante.
- Reprodução: abrir a aba Gráficos após carregar Base e criar um cenário; observar os números no fim das barras.
- Esperado: valor final legível sobre ou ao lado da barra.
- Observado: `.barra-val` e `.barra-fill` usam a mesma cor `rgb(31, 110, 58)` para resultados acima de 100%; os números existem no DOM, mas ficam praticamente invisíveis sobre o preenchimento verde.
- Evidência: `graficos.component.ts`, funções/template de barras, e `evidencias-auditoria/simulador-graficos.png`.
- Impacto: reduz a legibilidade do gráfico de barras na apresentação, mas a comparação tabular e o gráfico de linhas permanecem corretos e legíveis.
- Menor correção recomendada: aplicar cor de texto com contraste quando o valor estiver sobre a área preenchida, ou posicionar o rótulo fora da barra. Não foi alterado porque não bloqueia o fluxo e a solicitação prioriza mudanças mínimas.

### Parecer atualizado

**APTO COM RESSALVAS.** O fluxo essencial foi efetivamente demonstrado: aplicação aberta, Base carregado via proxy correto, cenários criados e comparados, incremento refletido no registro certo, remoção preservando os demais, gráficos atualizados, ausência mantida como ausência e falha tratada sem fallback ou cenário fictício. Meta 2 permanece claramente provisória e o otimizador permanece indisponível.

A apresentação não tem bloqueio funcional comprovado após a preparação. As ressalvas são o contraste dos rótulos no gráfico de barras, o aviso de orçamento do CSS do chat, a dependência da CDN para Chart.js e as limitações metodológicas herdadas já detalhadas neste relatório.
