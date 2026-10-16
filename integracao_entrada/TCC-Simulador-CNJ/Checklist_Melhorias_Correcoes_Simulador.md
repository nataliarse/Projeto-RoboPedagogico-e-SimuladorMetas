# Checklist de melhorias e correções do simulador

**Referência:** pacote original analisado e último relatório de diagnóstico enviado em 2 de outubro de 2026.
**Finalidade:** registrar o trabalho remanescente após a integração mínima e orientar a divisão de responsabilidades.

O relatório mais recente comprova o funcionamento isolado da API de base/simulação, mas não a execução do Angular. O prompt posterior para ajustar o ambiente foi preparado; não foi apresentado um novo relatório com seus resultados. Portanto, os itens de ambiente e interface abaixo continuam pendentes de confirmação.

A integração emergencial foi delimitada para aproveitar o trabalho existente e preservar as fórmulas recebidas. Essa preservação mantém a necessidade de revisão metodológica e de manutenção pelas áreas responsáveis.

## Como usar

- **P0 — apresentação:** resolver ou confirmar antes de declarar a demonstração pronta.
- **P1 — confiabilidade:** resolver antes de apresentar os indicadores como metodologicamente validados ou habilitar recursos ainda pendentes.
- **P2 — manutenção:** executar após estabilizar a integração.
- **Condicional:** necessário somente se o recurso fizer parte da entrega pretendida.

“Validar” indica ausência de evidência suficiente ou decisão metodológica pendente. Não significa que o item tenha um defeito comprovado. Os responsáveis abaixo são áreas; pessoas e prazos devem ser definidos pela equipe.

## P0 — execução e apresentação

| ID | Ação | Situação/evidência | Área e critério de conclusão |
|---|---|---|---|
| 01 | Disponibilizar Node/npm e restaurar dependências do frontend. | O processo do Codex não encontrou o runtime; node_modules estava ausente. Verificar instalação/PATH antes de reinstalar. | Ambiente/frontend. Scripts do projeto executam usando versão compatível e lockfile preservado; usar a CLI local do projeto. |
| 02 | Alinhar host e porta do backend com o proxy. | A porta 8000 atende outro serviço e devolve 404 para /api/base. A API do simulador foi testada em 8001. | Integração. Uma porta livre atende o simulador e /api/base pelo frontend retorna o JSON correto. Preservar o serviço preexistente. |
| 03 | Executar build, testes pertinentes e fluxo visual completo. | Compilação e interface não foram executadas na auditoria. Isso é uma lacuna de validação. | Frontend. Base, criação de dois cenários, remoção, comparação e navegação demonstrados no navegador. |
| 04 | Confirmar que toda apresentação de resultados usa a resposta da API. | A leitura estática indica correção, mas não houve comparação da tela com os payloads em execução. | Frontend/integração. Indicadores, tabelas e gráficos correspondem à mesma resposta; sem fallback para dados locais. |
| 05 | Conferir carregamento, erros e resultados indisponíveis. | Bloqueio de envio, mensagens e tratamento de null foram identificados estaticamente. | Frontend. Falha controlada não cria cenário, preserva dados/formulário e mostra erro; null não vira zero. |
| 06 | Verificar os gráficos no ambiente da apresentação. | Chart.js vem de CDN; há tratamento previsto para indisponibilidade, ainda não testado. | Frontend. Atualização/criação/remoção de cenários não quebra o gráfico. Se a apresentação exigir gráfico sem internet, disponibilizar a mesma biblioteca localmente; caso contrário, documentar a dependência e conferir a alternativa tabular. |

Se o último prompt já tiver sido executado, atualizar estes itens com evidências da nova execução. Não marcar como concluído apenas porque a alteração foi solicitada.

## P1 — metodologia, regras e dados

| ID | Ação | Justificativa e limite | Área e critério de conclusão |
|---|---|---|---|
| 07 | Validar a fórmula efetivamente aplicada à Meta 1, inclusive o piso do denominador. | O piso baseado em novos + dessobrestados neutraliza o abatimento de suspensos em grande parte dos casos; o denominador original igual a zero recebe tratamento específico. Há diferença entre a explicação usual no código e seu comportamento efetivo. | Metodologia + backend. Regra aprovada, fonte/ano de referência e exemplos numéricos independentes; só então corrigir a implementação, se necessário. |
| 08 | Definir a população de processos e obter os dados necessários à Meta 2. | A implementação usa totais gerais; o original declara ausência de dados da coorte de processos antigos. Trocar rótulos não resolve a ausência de dados. | Metodologia/dados + backend. Campos e população correspondem ao indicador pretendido. Até lá, manter saída provisória. |
| 09 | Definir o significado temporal de cada variável. | A Meta 2 combina distribuídos acumulados com suspensos do mês; é preciso confirmar se suspensos representa estoque ou fluxo e se a combinação é apropriada. Esse uso não é automaticamente incorreto. | Metodologia/dados. Dicionário documenta estoque/fluxo, período, unidade, coorte e regra de acumulação de cada série. |
| 10 | Formalizar a semântica de simulação. | O comportamento atual aplica deltas e limita resultados inferiores a zero. Uma solicitação de redução grande pode produzir redução efetiva menor. Também há decisões sobre meses reais, previsões e ano avaliado. | Metodologia + backend/frontend. Definir períodos editáveis, significado dos incrementos, comportamento do piso zero e como informar o ajuste efetivamente aplicado. |
| 11 | Padronizar nulidade, arredondamento, percentuais e classificação de status. | Resultados indisponíveis são diferentes de zero. Metas/status precisam seguir a regra aprovada, inclusive em limites e arredondamentos. | Metodologia + backend/frontend. Exemplos cobrem denominador zero/negativo, resultado nulo e limites de classificação; a tela apenas apresenta o resultado previsto pelo contrato. |
| 12 | Validar a integridade das planilhas antes da consolidação. | O carregamento do pacote original verificava algumas colunas/nulos, mas não constitui uma validação completa da base. | Dados/backend. Conferir colunas, tipos, valores finitos, unicidade dos meses, duplicidades que poderiam multiplicar linhas no merge, cobertura temporal e lacunas entre séries. Não preencher ausência com zero sem regra aprovada. |
| 13 | Documentar origem, versão e identificação de dados reais/previsões. | Existem previsões, datas de corte e rótulos diferentes entre backend e frontend. | Dados/backend/frontend. Cada entrega identifica arquivos/versão, origem das séries, corte real e horizonte. Validar o mapeamento previsao_sas/forecast e a sinalização visível. Definir também o tratamento dos valores fracionários das previsões. |

Nenhuma dessas ações autoriza alterar fórmulas com base apenas em preferência técnica. A decisão metodológica deve ser registrada por quem responde pelo indicador; a implementação e seus testes ficam com o backend.

## P1/P2 — funcionalidades pendentes e contrato

| ID | Ação | Situação e escopo | Área e critério de conclusão |
|---|---|---|---|
| 14 | Revisar o otimizador antes de habilitá-lo. | A interface foi deliberadamente desabilitada; o endpoint não foi auditado. O pacote original contém busca com expansão, bisseção e ajuste final sem limite explícito nesse último laço. | Backend/metodologia. Validar direção, monotonicidade na faixa usada, limites factíveis, metas impossíveis, variáveis sem efeito, resultados nulos e término da busca. Demonstrar que o ajuste encontrado é mínimo segundo a regra definida. |
| 15 | Integrar o otimizador validado ao frontend. | O componente legado usa uma busca local TypeScript. | Condicional, frontend. Após o item 14, consumir a API, representar sinal/zero/nulo corretamente e tratar falha/carregamento. Decidir também se o endpoint deve ficar acessível enquanto o recurso estiver pendente; desabilitar a aba não desabilita a rota. |
| 16 | Definir o papel de /api/comparar e revisar as rotas que forem mantidas. | A comparação visual atual pode usar as simulações já recebidas. A rota de comparação não precisa ser integrada apenas por existir. | Backend/frontend. Manter, documentar e testar somente o contrato suportado para cada recurso; evitar novo caminho de cálculo com comportamento divergente. |
| 17 | Consolidar contratos de entrada/saída e erros. | Base e simulação tiveram validações de entrada aprovadas. A revisão completa das outras rotas e das falhas de carga fica pendente. | Backend + frontend. Modelos documentados, tipos coerentes, null bem definido, erros de cliente distintos de falhas internas e mensagens utilizáveis. Avaliar a tipagem atual antes de substituir modelos já corrigidos. |
| 18 | Configurar o backend próprio do chat, caso ele entre na entrega. | /api/chat não existe no simulador nem está configurado no proxy apresentado. | Condicional, responsável pelo chat/integração. Destino correto configurado e testado; fora desse escopo, documentar a indisponibilidade. |

## P2 — arquitetura e manutenção

| ID | Ação | Evidência e finalidade | Área e critério de conclusão |
|---|---|---|---|
| 19 | Consolidar uma implementação das regras de negócio em Python. | O pacote original mantém funções semelhantes no monólito e em main.py. | Backend. Um núcleo reutilizável alimenta os consumidores necessários, com compatibilidade do contrato e resultados verificada. Fazer depois de definir o comportamento esperado. |
| 20 | Retirar dados estimados, ETL e fórmulas TypeScript do serviço ativo. | O relatório confirma que ainda são construídos, embora não alimentem os cenários apresentados. | Frontend. SimuladorService gerencia estado/apresentação e consumo de resultados; cálculo legado não pode ser reativado por engano. Preservar o histórico no versionamento. |
| 21 | Separar carga de dados, cálculo, API e exemplos/exportações. | O original executa leitura no topo; a API recebida também carrega dados ao importar. | Backend. Importar o módulo de cálculo não lê planilhas, desenha gráficos ou exporta arquivos; inicialização dos dados é explícita e falhas de carga são diagnosticáveis. Sem exigir uma arquitetura complexa. |
| 22 | Centralizar configurações que precisam variar. | Ano, corte real, horizonte, portas e caminhos aparecem como valores fixos no pacote original. | Backend/frontend. Configuração explícita para dados e execução; ano/meses da interface coerentes com a base e com o contrato. Não introduzir novos parâmetros de negócio sem definição. |
| 23 | Eliminar a ambiguidade entre as duas árvores Angular. | O relatório confirma que simulador-metas/ não participa do build. | Frontend. Uma árvore ativa; a cópia secundária é arquivada ou removida após verificar se contém trabalho exclusivo. |
| 24 | Padronizar ambiente e empacotamento. | Ambiente Python isolado não foi encontrado na auditoria. O pacote inicial ainda carregava artefatos gerados. | Ambiente/mantenedores. Manifestos e lockfiles suficientes para reprodução, ambiente Python isolado e pacote contendo fontes/configurações/dados necessários, sem dependências instaladas e caches. Atualizar instruções de execução conforme o ambiente real. |

## P1/P2 — verificação, documentação e responsabilidade

| ID | Ação | Escopo proporcional | Área e critério de conclusão |
|---|---|---|---|
| 25 | Preservar os testes úteis já executados e criar regressões focadas. | O sucesso da API foi registrado; isso deve ser reproduzível depois de alterações. | Backend/frontend. Cobrir cenário vazio, deltas, base imutável, entradas inválidas, ano final, null e exibição da resposta HTTP. Para fórmulas, usar resultados de referência independentes aprovados pela metodologia, sem apenas copiar o algoritmo testado. |
| 26 | Documentar execução, contrato e limitações. | Há uma entrega provisória e componentes com status diferente. | Cada área documenta sua parte. README com comandos/portas, arquivos necessários, request/response, erros e recursos disponíveis; checklist distingue implementado, executado, pendente e desabilitado. |
| 27 | Colocar o projeto sob versionamento próprio e identificar as entregas. | O Git resolveu o topo para Desktop, sem commits do projeto; não há diff confiável para atribuir todas as mudanças. | Mantenedores. Repositório do projeto, .gitignore adequado e uma versão identificável do estado recebido e de cada intervenção. Não incluir o Desktop inteiro no versionamento. |
| 28 | Definir responsáveis e limites de manutenção. | A integração exigiu trabalho adicional sobre uma interface de backend em construção. | Coordenação/equipe. Metodologia e dados respondem pela validade do indicador; backend pelo cálculo/contrato; frontend pelo consumo/apresentação; ambiente pela execução. Registrar contribuições verificáveis e responsáveis por cada pendência, sem inferir autoria individual pelo arquivo. |

## O que já foi atendido segundo o último relatório

| Item | Evidência disponível |
|---|---|
| Leitura das quatro planilhas e resposta consolidada da API | Execução relatada, 86 registros. |
| GET /api/base e POST /api/simular no backend correto | Testados na porta 8001. |
| Cenário sem alterações e incremento no mês correto | Testados; resultados correspondentes às entradas. |
| Base não modificada pelas simulações | Comparação antes/depois aprovada. |
| Validação de mês inválido/ausente, null, fração, booleano e campo desconhecido | HTTP 422 nos casos relatados. |
| Escolha da meta final do ano configurado | Confirmada para dezembro de 2026, mesmo com série até fevereiro de 2027. |
| Cenários Angular alimentados pelas respostas da API | Confirmado apenas por leitura estática; execução da tela pendente. |
| Meta 2 identificada como provisória e otimizador bloqueado na interface | Confirmado apenas por leitura estática; execução da tela pendente. |
| Tratamento visual previsto de erros e null | Identificado estaticamente; validação no navegador pendente. |

Não reapresentar as validações de entrada já aprovadas como se ainda precisassem ser implementadas. O que falta nelas é manutenção e regressão, além da confirmação do comportamento visual correspondente.

## Ordem de trabalho proposta

1. Concluir os itens 01–06 e obter um novo parecer sobre a apresentação.
2. Alinhar metodologia e dados dos itens 07–13 antes de certificar resultados.
3. Planejar funcionalidades pendentes segundo o escopo real, especialmente os itens 14–18.
4. Executar a consolidação e limpeza dos itens 19–24 de forma incremental.
5. Manter testes, documentação e responsabilidades dos itens 25–28 acompanhando essas mudanças.

A checklist não transforma todas as pendências em requisito para a reunião nem em responsabilidade de quem prestou o apoio emergencial. Ela registra o trabalho necessário para evoluir da demonstração para uma entrega confiável e mantida.

