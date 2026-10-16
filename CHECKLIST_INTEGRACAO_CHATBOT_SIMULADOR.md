# CHECKLIST — Integração Chatbot Processual AI + TCC-Simulador-CNJ

**Estado:** PLANEJADO | **Escopo:** unir os dois projetos numa aplicação coerente, preservando comportamentos homologados.

**Fontes analisadas:** `chatbot_processual_ai(10).zip` e `TCC-Simulador-CNJ.zip` (14/10/2026).

**Branch:** `feat/integracao_robo_metas`. **Estratégia:** adicionar o ZIP novo em uma pasta isolada inicialmente; nunca despejar seus arquivos sobre caminhos existentes.

## Princípios inegociáveis

1. Não excluir, substituir, mover ou renomear código legado antes de mapear dependências, testes e obter aprovação explícita. Não apagar checklists antigas: elas estão fora do escopo, mesmo que ausentes da branch.
2. Não executar coleta real, acessar sistemas institucionais, redes externas, alterar bases de produção ou efetuar deploy sem autorização específica. Preferir fixtures/simulações locais.
3. Uma tarefa por execução do Codex; um commit por item concluído, ou por pequeno conjunto explicitamente autorizado; registrar commit, teste e evidência no controle. Se não passar, marcar `BLOCKED` ou `FAILED`, nunca `VALIDATED`.
4. Não adaptar contratos no improviso: registrar formato atual e futuro, compatibilidade e testes de contrato. Nunca interpretar erro de backend como sucesso.
5. Manter o motor de cálculo do simulador novo; `services/meta_simulator_adapter.py` no chatbot retorna `not_integrated` e **não** deve substituir o simulador.
6. Sem alterações em regras processuais/CNJ, fórmulas, dados, modelos de IA ou prompts fora do estritamente necessário à integração; mudanças de negócio precisam de item separado e homologação.
7. Toda alteração exige `git diff --check`, teste direcionado e evidência. Sem declarar "pronto para produção" baseado apenas em mocks.
8. `node_modules`, `.venv`, `.env`, bancos locais, tokens, logs sensíveis e artefatos de build não devem entrar em commits.

## Arquitetura alvo (hipótese a validar na fase 0)

```
Angular único (preferencialmente o do TCC-Simulador-CNJ)
    ├── /api/processos/*  → FastAPI chatbot processual (agentes, coleta, SQLite, RAG)
    └── /api/base|simular|comparar|otimizador → FastAPI simulador (regras e cálculos)
```

O usuário vê **uma** aplicação, mas os dois serviços podem continuar separados internamente. A fusão física em um único processo Python é uma decisão posterior e **não** condição para entregar a integração funcional.

## Evidências concretas do baseline

- Frontend novo: `frontend/meu-primeiro-app/src/app/core/services/chat.ts` chama `POST /api/chat` somente com `{ mensagem }` e timeout de 60 s.
- Frontend novo: `src/app/features/chat/chat.ts` chama `responderMock(pergunta)` tanto em sucesso como erro, desprezando a resposta real.
- Frontend novo: `frontend/meu-primeiro-app/proxy.conf.json` encaminha `/api/base`, `/api/simular`, `/api/health` para `127.0.0.1:8001`, mas não encaminha o chat.
- Backend processual: `chatbot_processual_ai/api.py`: `POST /api/processos/chat`, corpo `{mensagem, session_id?}`, retorno `{session_id, resultado}` e texto em `resultado.resposta`.
- Backend de metas novo: `backend/main.py`: `/api/health`, `/api/base`, `/api/simular`, `/api/comparar`, `/api/otimizador`.
- Ambos os backends têm `/api/health`; é necessário evitar colisão/roteamento ambíguo.
- Backend chatbot mantém sessões em `_SESSIONS` em memória; não pressupor persistência entre reinícios.
- Existem múltiplas árvores Angular dentro do ZIP novo (`frontend/meu-primeiro-app` e `simulador-metas` interno). Escolher uma única aplicação principal **após** inventário, sem descartar funcionalidades do outro projeto.

## Fase 0 — Segurança, inventário e definição [INT-00]

- [ ] **INT-001** Confirmar branch de integração, `git status`, commit-base, arquivos não rastreados e plano de rollback. Aceite: relatório antes de qualquer edição.
- [ ] **INT-002** Copiar/descompactar o projeto novo em diretório de quarentena versionável (ex.: `integracao_entrada/TCC-Simulador-CNJ/`), sem sobreposição de nomes. Aceite: diff somente aditivo e inventário de arquivos.
- [ ] **INT-003** Inventariar aplicações Angular, backends Python, módulos comuns, arquivos de configuração e scripts; detectar duplicatas e código morto sem excluir nada. Aceite: mapa arquivo→função→destino.
- [ ] **INT-004** Registrar os comandos de execução e os testes existentes de ambos os projetos; rodar baselines locais somente offline. Aceite: resultados, versões e limitações.
- [ ] **INT-005** Produzir matriz completa de rotas, verbos, schemas, status HTTP, payloads, timeouts e dependências (incluindo `/api/health`). Aceite: tabela revisável.
- [ ] **INT-006** Decidir a árvore Angular canônica, a estratégia de convivência dos dois FastAPI e a estrutura-alvo do repositório. Aceite: ADR curto, aprovado antes de mover código.

## Fase 1 — Preparação de repositório e execução [INT-01]

- [ ] **INT-007** Estabelecer estrutura de diretórios definitiva sem apagar o legado; usar movimentações rastreáveis. Aceite: histórico e imports identificáveis.
- [ ] **INT-008** Consolidar `.gitignore` e arquivos `.env.example` sem segredos reais. Aceite: verificação de arquivos sensíveis.
- [ ] **INT-009** Documentar versões suportadas de Python, Node/npm e dependências e instruções de instalação reproduzíveis. Aceite: ambiente recriável em máquina limpa.
- [ ] **INT-010** Criar comandos de inicialização local individuais para Angular, chatbot e simulador, com portas distintas. Aceite: cada um sobe isoladamente.
- [ ] **INT-011** Estabelecer configuração de URL/portas por ambiente; não embutir endereços institucionais nem credenciais. Aceite: dev funciona por proxy e configuração é explícita.

## Fase 2 — Contratos HTTP e proxy [INT-02]

- [ ] **INT-012** Formalizar schema tipado request/response do chatbot; incluir `session_id`, `resultado.resposta` e erros. Aceite: teste de contrato correspondente ao backend.
- [ ] **INT-013** Formalizar e preservar schemas dos endpoints do simulador (`base`, `simular`, `comparar`, `otimizador`). Aceite: fixtures de exemplos válidos e inválidos.
- [ ] **INT-014** Configurar proxy Angular para rotas de chatbot e simulador, inclusive healthchecks distintos; prevenir colisões. Aceite: chamadas chegam ao destino correto.
- [ ] **INT-015** Garantir tratamento consistente de 4xx/5xx, indisponibilidade, timeouts e respostas inválidas. Aceite: erros visíveis, sem resposta mock fingindo sucesso.
- [ ] **INT-016** Definir orçamentos de timeout coerentes sem simplesmente elevar valores; documentar operações potencialmente longas. Aceite: decisão e teste de timeout.

## Fase 3 — Chat real no Angular [INT-03]

- [ ] **INT-017** Refatorar `core/services/chat.ts` para `POST /api/processos/chat` e request tipada, com opção `session_id`. Aceite: teste HTTP por spy/mock.
- [ ] **INT-018** Tipar `core/models/chat.model.ts` para payload real, erro estruturado e mensagens; sem `any` desnecessário. Aceite: build TypeScript.
- [ ] **INT-019** Remover `responderMock()` do caminho de sucesso e renderizar `resultado.resposta`; conservar fallback honesto apenas para falhas. Aceite: teste de sucesso/falha.
- [ ] **INT-020** Guardar e reenviar `session_id` durante a conversa. Aceite: duas perguntas consecutivas usam a mesma sessão.
- [ ] **INT-021** Definir comportamento de nova conversa, limpeza e restauração após refresh; histórico local não implica sessão persistida no servidor. Aceite: cenários documentados e testados.
- [ ] **INT-022** Implementar estado de carregamento, cancelamento/duplicidade, erros de rede e recuperação. Aceite: nenhum envio silenciosamente perdido ou duplicado.
- [ ] **INT-023** Tratar respostas potencialmente sensíveis com renderização segura; evitar HTML injetável e dados processuais indevidos em logs. Aceite: testes de sanitização e revisão de logs.
- [ ] **INT-024** Exercitar fluxo chat com backend real **local e fixture offline** (sem consultar PJe). Aceite: pergunta→HTTP→agentes→resposta visível.

## Fase 4 — Simulador preservado no frontend único [INT-04]

- [ ] **INT-025** Escolher/transportar componentes de base, cenários, gráficos, tabelas e otimizador, sem perda funcional. Aceite: inventário comparativo antes/depois.
- [ ] **INT-026** Adaptar serviços Angular do simulador aos endpoints reais sem modificar as fórmulas do backend. Aceite: requests reais e modelos tipados.
- [ ] **INT-027** Testar carregamento de base, simulação e respostas de erro/vazio. Aceite: testes automatizados e demonstração offline.
- [ ] **INT-028** Testar `/api/comparar` e `/api/otimizador` de ponta a ponta, caso sejam acionados pela UI escolhida; se não usados, registrar lacuna explicitamente. Aceite: cobertura ou decisão aprovada.
- [ ] **INT-029** Unificar navegação/layout do Angular para acessar chat e simulador sem alternar aplicativos. Aceite: fluxo navegável e responsivo.
- [ ] **INT-030** Preservar integridade de resultados numéricos: snapshots com tolerância definida e dados de fixture. Aceite: resultados antes/depois equivalentes.

## Fase 5 — Integração entre domínio processual e simulação [INT-05]

- [ ] **INT-031** Definir casos de uso autorizados que requerem o chatbot consultar o simulador. Aceite: especificação separa perguntas processuais de cenários CNJ.
- [ ] **INT-032** Definir contrato interno de chamada ao serviço real do simulador, sem usar `not_integrated` como se fosse cálculo. Aceite: adapter/interface testável.
- [ ] **INT-033** Implementar cliente/adapter com timeout, validação de schema e erros sem inventar números. Aceite: testes unitários com doubles.
- [ ] **INT-034** Integrar orquestração apenas para intenções explicitamente mapeadas. Aceite: perguntas processuais não são desviadas para metas.
- [ ] **INT-035** Garantir rastreabilidade das premissas e resultados numéricos nas explicações, sem regras CNJ inventadas. Aceite: testes de aceitação com cenários conhecidos.
- [ ] **INT-036** Validar recusa/degradação transparente quando motor de metas ou dados faltarem. Aceite: resposta não afirma resultado inexistente.

## Fase 6 — Qualidade, segurança e operação [INT-06]

- [ ] **INT-037** Executar suites existentes de Python e Angular e reparar regressões **causadas pela integração**. Aceite: relatório por suite, comando e resultado.
- [ ] **INT-038** Adicionar testes de contrato entre front e ambos backends, incluindo erros 422/500, sessão e tipos numéricos. Aceite: rodagem automatizada.
- [ ] **INT-039** Executar smoke test local dos três processos e navegação ponta a ponta somente com dados permitidos. Aceite: roteiro e evidências reproduzíveis.
- [ ] **INT-040** Revisar proteção de sessões, CORS/proxy, validações, exposição de dados e logs antes de qualquer publicação. Aceite: riscos classificados e correções obrigatórias identificadas.
- [ ] **INT-041** Adicionar healthchecks diferenciados e mensagens operacionais de indisponibilidade. Aceite: queda isolada de um backend não derruba toda a UI.
- [ ] **INT-042** Preparar scripts/documentação de desenvolvimento e troubleshooting de portas, imports, banco e serviços opcionais. Aceite: outro dev reproduz o ambiente.
- [ ] **INT-043** Executar revisão de diff, dependências, licenças e arquivos não versionáveis. Aceite: nenhuma remoção inadvertida ou segredo versionado.
- [ ] **INT-044** Fazer demonstração final com matriz de evidências e limitações conhecidas. Aceite: chat e simulador navegáveis na mesma UI e teste ponta a ponta aprovado.
- [ ] **INT-045** Preparar PR da branch de integração com plano de rollback e registro de decisões; **não** efetuar merge automático. Aceite: PR revisável.

## Regras de decisão e bloqueio

- Se a árvore Angular canônica não puder ser escolhida sem perda, parar em INT-006 e documentar alternativas.
- Se os contratos reais divergirem desta leitura de ZIP, atualizar matriz/ADR antes de implementar.
- Se o backend não puder funcionar offline, registrar a dependência externa e usar fixtures; não contornar proteções de coleta.
- Se testes falharem no baseline, isolar falha pré-existente de regressão nova.
- Se a integração exigir alteração de regra de negócio, criar item complementar autorizado antes de editar.

## Critério global de conclusão

`DONE` somente se: mesma interface Angular oferece chat real e simulador; endpoints e sessões corretos; nenhum mock de sucesso; fórmulas preservadas; testes automatizados e smoke tests comprovados; documentação reproduzível; diff limpo; PR pronto para revisão humana. Segurança de produção e homologação de regras CNJ são avaliações próprias, não implicitamente aprovadas.
