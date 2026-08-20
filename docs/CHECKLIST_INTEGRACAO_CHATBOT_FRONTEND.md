# Checklist de Integração — Chatbot Processual + Frontend Angular

**Branch-alvo informada:** `feat/integra_chatbot_frontend`  
**Data do baseline:** 18/08/2026  
**Escopo:** integrar `frontend/` ao `chatbot_processual_ai/` de forma rastreável, testável e reversível, preservando `simulador-de-metas/` fora do escopo desta integração.  
**Regra operacional:** esta checklist deve ser executada em unidades pequenas. Um item com ID rastreável não autoriza avanço automático para outro item.

---

## 0. Resultado esperado

Ao final desta checklist:

- o Angular consome a API FastAPI real sem mocks de sucesso;
- frontend e backend compartilham um contrato HTTP documentado e tipado;
- cada navegador/sessão possui contexto conversacional isolado;
- a aplicação trata sucesso, falha HTTP e falha controlada do pipeline de forma distinta;
- o histórico do frontend usa o processo realmente identificado pelo backend;
- desenvolvimento local possui fluxo reproduzível em ambiente limpo;
- testes de backend, frontend e integração cobrem o contrato principal;
- documentação do repositório descreve a arquitetura real;
- caches, dependências instaladas e artefatos locais não entram no versionamento;
- a branch só fica pronta para merge quando os gates finais forem atendidos.

---

## 1. Evidências do baseline atual

### Backend

- Existe API FastAPI em `chatbot_processual_ai/api.py`.
- Endpoint de chat real: `POST /api/processos/chat`.
- Entrada atual: `session_id: str | None` + `mensagem: str`.
- Saída atual: `session_id` + `resultado` estruturado.
- `resultado` expõe pelo menos: `tipo`, `intent`, `resposta`, `processo_ativo`, `collection_status`, `failed_stage`, `rag_status` e `fontes`.
- A ausência de `session_id` é normalizada atualmente para o valor fixo `default`.
- Sessões ficam em memória no processo Python (`_SESSIONS`).
- Suite backend executada a partir de `chatbot_processual_ai/`: **29 testes aprovados**.
- A mesma suite executada a partir da raiz do repositório não coleta corretamente por causa dos imports atuais; o diretório de execução deve ser documentado ou posteriormente normalizado.
- Não foi identificada cobertura específica da camada HTTP/FastAPI nos testes existentes.

### Frontend

- Angular `21.2.x`, TypeScript `5.9.x`, RxJS `7.8.x`.
- `ChatService` chama atualmente `POST /api/chat`.
- O corpo enviado atualmente contém apenas `{ mensagem }`.
- O retorno é tipado como `Observable<any>`.
- `ChatComponent` ignora a resposta HTTP e executa `responderMock()` tanto em `next` quanto em `error`.
- O histórico grava atualmente a pergunta do usuário no campo `numero_processo`.
- O estado possui `erro`, mas a interface atual não apresenta esse erro ao usuário.
- O status “Sistema disponível” está estático na interface.
- Timeout HTTP do frontend: 60 s; timeout configurável do Ollama no backend: 60 s por padrão.
- Código de aplicação do frontend passou em `tsc -p tsconfig.app.json --noEmit`.
- Testes TypeScript do frontend **não compilam** no baseline por imports antigos (`Chat`, `LocalStorage`, `State` etc.).
- O teste de `App` ainda espera conteúdo da tela inicial gerada pelo Angular e está semanticamente desatualizado.
- O pacote recebido contém `node_modules/` e `.angular/cache/`; ambos já constam no `.gitignore` interno do frontend, portanto é necessário verificar se estão apenas no arquivo recebido ou se chegaram a ser rastreados pelo Git.
- O build Angular não pôde ser validado no ambiente Linux usado para este diagnóstico porque o `node_modules` recebido contém binário `esbuild` de Windows. Isso reforça que a validação correta deve partir de `npm ci` em ambiente limpo, e não do `node_modules` transportado.

### Governança/documentação

- `AGENTS.md` existe na raiz e já define diagnóstico, escopo, testes, documentação, Git, checklist e critérios de validação.
- `.codex/rules/safety.rules` existe no material recebido.
- O `.gitignore` raiz ignora `.codex/`; se `safety.rules` ainda não estiver rastreado, ele não será incluído automaticamente em commit. Isso precisa ser resolvido deliberadamente.
- `docs/ARCHITECTURE.md` possui conteúdo técnico relevante.
- `docs/design_philosophy.md`, `docs/development.md` e `docs/orchestration.md` estão vazios no baseline recebido.
- O `README.md` raiz contém recomendações históricas (ex.: Streamlit/LangGraph) que não representam integralmente a implementação atual Angular + FastAPI.
- `frontend/README.md` permanece majoritariamente como README padrão gerado pelo Angular CLI.

---

## 2. Convenção de status

Use apenas:

- `TODO` — ainda não iniciado;
- `READY` — diagnóstico/precondições permitem iniciar;
- `IN_PROGRESS` — investigação ou implementação iniciada;
- `BLOCKED` — impedimento objetivo;
- `IMPLEMENTED` — código/documentação concluído, validação final ainda pendente;
- `VALIDATED` — critérios de aceite, testes e diff confirmados;
- `REJECTED` — solução implementada foi considerada inadequada;
- `SUPERSEDED` — item substituído formalmente por outro.

**Nenhum item deve ser marcado `VALIDATED` apenas porque o código foi escrito.**

---

# FASE P0 — Baseline, higiene e governança

## INT-P0-001 — Confirmar branch e worktree de integração

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante  
**Objetivo:** garantir que todo o trabalho ocorra na branch isolada correta.

### Ações

- [x] Executar `git branch --show-current`.
- [x] Confirmar `feat/integra_chatbot_frontend`.
- [x] Executar `git status --short`.
- [x] Registrar alterações preexistentes que não pertencem à integração.
- [x] Não limpar, restaurar ou sobrescrever alterações preexistentes automaticamente.

### Critério de aceite

- branch confirmada;
- estado inicial do worktree registrado;
- nenhuma mudança preexistente foi perdida.

---

## INT-P0-002 — Auditar arquivos transportados vs. arquivos rastreados

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante

### Ações

- [x] Verificar se `frontend/node_modules/` está rastreado com `git ls-files frontend/node_modules`.
- [x] Verificar se `frontend/.angular/` está rastreado com `git ls-files frontend/.angular`.
- [x] Verificar `__pycache__`, `.pyc`, bancos locais, `.env` e outros artefatos gerados.
- [x] Se algum artefato estiver rastreado, remover apenas do índice Git de forma não destrutiva para o worktree.
- [x] Confirmar que `frontend/package-lock.json` permanece versionado.
- [x] Confirmar que `.env.example` permanece versionado e `.env` real não.

### Critério de aceite

- dependências instaladas, caches, segredos e artefatos locais não são parte do versionamento;
- lockfiles e exemplos de configuração necessários permanecem rastreados.

---

## INT-P0-003 — Tornar as regras Codex versionáveis de forma intencional

**Status inicial:** `VALIDATED`  
**Prioridade:** bloqueante para uso confiável do Codex

### Problema observado

O `.gitignore` raiz contém `.codex/`, enquanto o projeto pretende usar `.codex/rules/safety.rules` como política compartilhada.

### Ações

- [x] Executar `git check-ignore -v .codex/rules/safety.rules`.
- [x] Confirmar se o arquivo já está rastreado com `git ls-files .codex/rules/safety.rules`.
- [x] Definir política: versionar somente regras compartilhadas e continuar ignorando estado local do Codex.
- [x] Ajustar `.gitignore` de forma mínima para permitir `.codex/rules/safety.rules` sem liberar indiscriminadamente todo `.codex/`.
- [x] Validar com `git check-ignore` e `git status`.

### Critério de aceite

- `safety.rules` compartilhado aparece como rastreável;
- arquivos locais/sensíveis do Codex continuam ignorados;
- nenhuma regra de segurança foi silenciosamente removida.

---

## INT-P0-004 — Registrar baseline técnico reproduzível

**Status inicial:** `VALIDATED`

### Ações

- [x] Backend: `cd chatbot_processual_ai && python -m pytest tests -q`.
- [x] Registrar resultado esperado inicial de 29 testes aprovados, salvo mudança legítima no ambiente/projeto.
- [x] Frontend: remover/ignorar `node_modules` transportado para fins de validação.
- [x] Frontend: executar `npm ci` em ambiente compatível.
- [x] Executar `npm run build`.
- [x] Executar `npm test -- --watch=false`.
- [x] Se testes falharem por problemas preexistentes, registrar como baseline; não mascarar.
- [x] Executar `node node_modules/typescript/bin/tsc -p tsconfig.app.json --noEmit` quando útil como validação focada.

### Critério de aceite

- baseline backend e frontend registrado com comandos e resultados reais;
- falhas preexistentes distinguidas de regressões futuras.

### Resultado da execução em 20/08/2026

- Backend: Python 3.12.10 e pip 26.1.2; o comando previsto com `pytest`
  não pôde coletar testes porque o módulo não está instalado. A suíte
  documentada equivalente com `unittest` executou 29 testes, todos aprovados,
  em 1,294 s.
- Frontend: `node`, `npm` e `npx` não estão instalados ou disponíveis no
  `PATH`; por isso `npm ci`, build, testes e validações TypeScript não puderam
  ser executados.
- Classificação: `BLOCKED` por limitação ambiental objetiva. Nenhuma
  dependência foi instalada, nenhum código funcional ou manifesto foi alterado
  e nenhuma falha foi mascarada.

### Resultado da recuperação em 20/08/2026

- Ambiente: `.venv` local ignorado com Python 3.12.10, pip 25.0.1 e pytest
  9.1.1; Node 24.19.0 LTS instalado no escopo do usuário, com npm/npx 11.17.0.
- Backend: `python -m pytest tests -q` executou 29 testes; 29 passaram em
  1,77 s, com um aviso ambiental de cache sem impacto na suíte.
- Frontend: `npm ci` instalou 468 pacotes e preservou os hashes de
  `package.json` e `package-lock.json`; a auditoria reportou 28 vulnerabilidades
  no grafo fixado pelo lockfile.
- Build: aprovado em 4,167 s, com aviso preexistente de budget CSS em
  `src/app/features/chat/chat.css`.
- Testes: iniciaram e falharam antes da coleta por quatro erros TS2305 em specs
  desatualizadas; nenhuma spec foi corrigida.
- TypeScript: `tsconfig.app.json` aprovado; `tsconfig.spec.json` falhou nos
  mesmos quatro imports. Aplicação compila; infraestrutura/specs apresentam
  falha preexistente.
- Classificação final: `VALIDATED`; baseline integralmente executado, observado
  e classificado, sem alteração funcional, de manifests ou de integração.

---

## INT-P0-005 — Definir explicitamente o escopo negativo

**Status inicial:** `VALIDATED`

### Não faz parte desta integração, salvo dependência comprovada

- [x] Não implementar novas regras do simulador de metas.
- [x] Não alterar modelos ARIMA.
- [x] Não refatorar agentes do chatbot sem necessidade da fronteira HTTP.
- [x] Não migrar SQLite/Qdrant/Ollama apenas para facilitar o frontend.
- [x] Não renomear em massa o projeto Angular nesta fase.
- [x] Não introduzir autenticação, deploy ou persistência distribuída de sessão sem decisão específica.

### Critério de aceite

- escopo negativo documentado no material de integração e respeitado no diff.

**Evidência:** `docs/integration.md` formaliza a integração conservadora, os
não objetivos por categoria, o tratamento de dívida técnica e a exceção por
dependência comprovada. O diff do item é exclusivamente documental.

---

# FASE P1 — Arquitetura e contrato antes de código

## INT-P1-001 — Formalizar topologia da integração

**Status inicial:** `TODO`  
**Dependência:** P0

### Decisão alvo

```text
Browser / Angular
      |
      | HTTP JSON
      v
FastAPI (/api/...)
      |
      v
Orquestradores / agentes / serviços / SQLite / RAG / Ollama
```

### Ações

- [ ] Declarar que frontend e backend são aplicações irmãs, não código a ser fundido internamente.
- [ ] Declarar que o frontend conhece apenas a API pública.
- [ ] Declarar que detalhes de agentes, RAG, SQLite e Ollama não vazam para componentes Angular.
- [ ] Registrar em `docs/ARCHITECTURE.md` ou documento de integração específico.

### Critério de aceite

- fronteira de responsabilidade inequívoca para humano e agente de código.

---

## INT-P1-002 — Congelar contrato HTTP v1 do chat processual

**Status inicial:** `TODO`  
**Dependência:** INT-P1-001

### Contrato base existente

`POST /api/processos/chat`

Request:

```json
{
  "session_id": "string-ou-null",
  "mensagem": "texto do usuário"
}
```

Response:

```json
{
  "session_id": "identificador da sessão",
  "resultado": {
    "tipo": "processual_chat",
    "intent": "string-ou-null",
    "resposta": "texto para o usuário",
    "processo_ativo": "string-ou-null",
    "collection_status": "string-ou-null",
    "failed_stage": "string-ou-null",
    "rag_status": "string-ou-null",
    "fontes": []
  }
}
```

### Ações

- [ ] Validar nomes, nulabilidade e semântica de cada campo.
- [ ] Decidir quais campos são obrigatórios na API v1.
- [ ] Decidir compatibilidade futura sem acoplar o frontend a campos internos desnecessários.
- [ ] Documentar exemplos de sucesso, processo ausente, falha controlada e erro HTTP.
- [ ] Registrar política de versionamento/breaking change do contrato.

### Critério de aceite

- backend, frontend, testes e documentação usam o mesmo contrato.

---

## INT-P1-003 — Definir estratégia de sessão web

**Status inicial:** `TODO`  
**Prioridade:** bloqueante para uso multiusuário

### Problema observado

Quando o cliente não envia `session_id`, o backend usa atualmente `default`; clientes diferentes podem compartilhar estado conversacional no mesmo processo Python.

### Decisão recomendada

- backend gera identificador opaco/UUID quando a requisição não possui sessão válida;
- frontend captura `response.session_id`;
- frontend armazena a sessão em `sessionStorage` para manter contexto durante a aba/sessão do navegador;
- chamadas seguintes reutilizam o mesmo ID;
- sessão em memória do backend permanece explicitamente uma limitação do MVP.

### Ações

- [ ] Aprovar estratégia.
- [ ] Definir comportamento em refresh, nova aba, fechamento do navegador e backend reiniciado.
- [ ] Definir limite/expiração futura para `_SESSIONS` ou registrar dívida técnica.
- [ ] Garantir que IDs não carreguem dados pessoais/sensíveis.

### Critério de aceite

- dois clientes sem `session_id` não recebem automaticamente a mesma sessão;
- segunda pergunta do mesmo cliente preserva `processo_ativo`.

---

## INT-P1-004 — Definir semântica de erros e falhas controladas

**Status inicial:** `TODO`

### Ações

- [ ] Diferenciar erro de transporte/HTTP de resposta válida com `failed_stage`.
- [ ] Definir texto seguro mostrado ao usuário em cada caso.
- [ ] Definir quais detalhes ficam apenas em logs/trace.
- [ ] Não expor stack trace, path local, configuração, IDs internos do banco ou Qdrant.
- [ ] Definir como `collection_status`, `rag_status` e `failed_stage` influenciam UI sem transformar limitação em “sucesso verde”.

### Critério de aceite

- tratamento previsível e documentado no frontend e backend.

---

## INT-P1-005 — Definir política de timeout

**Status inicial:** `TODO`

### Ações

- [ ] Mapear timeout interno do Ollama e demais operações demoradas.
- [ ] Garantir que timeout do frontend seja maior que o limite interno relevante, com margem de transporte/processamento.
- [ ] Evitar timeout infinito.
- [ ] Definir mensagem de timeout distinta de erro genérico.
- [ ] Registrar valores em documentação/configuração, não espalhar números mágicos.

### Critério de aceite

- o frontend não aborta rotineiramente a requisição no mesmo instante em que o backend atinge seu próprio limite.

---

## INT-P1-006 — Definir topologia de rede em desenvolvimento e produção

**Status inicial:** `TODO`

### Recomendação

- desenvolvimento: Angular em `localhost:4200` com proxy `/api` para FastAPI em `localhost:8000`;
- produção: preferir mesma origem/reverse proxy quando a infraestrutura permitir;
- se houver origens distintas: CORS explícito por allowlist, nunca `*` por conveniência sem necessidade.

### Ações

- [ ] Aprovar topologia local.
- [ ] Aprovar origem/URL de produção quando conhecida.
- [ ] Definir se será necessário `CORSMiddleware`.
- [ ] Não codificar `http://localhost:8000` dentro de componentes.

### Critério de aceite

- URL da API tem uma única estratégia definida e reproduzível por ambiente.

---

# FASE P2 — Fortalecimento da fronteira backend

## INT-P2-001 — Adicionar testes HTTP do endpoint processual

**Status inicial:** `TODO`  
**Dependência:** contrato P1 validado

### Cobertura mínima

- [ ] request válido retorna HTTP esperado;
- [ ] estrutura de response respeita contrato;
- [ ] `session_id` é retornado;
- [ ] `resultado.resposta` é string utilizável;
- [ ] `processo_ativo` é retornado após consulta válida;
- [ ] segunda pergunta com mesma sessão preserva contexto;
- [ ] mensagens inválidas/vazias seguem política definida;
- [ ] falha controlada não vaza detalhe sensível.

### Critério de aceite

- contrato principal tem teste automatizado na camada FastAPI.

---

## INT-P2-002 — Isolar sessões de clientes web

**Status inicial:** `TODO`  
**Dependência:** INT-P1-003 + INT-P2-001

### Ações

- [ ] Substituir fallback global `default` pela estratégia aprovada.
- [ ] Preservar IDs válidos enviados pelo cliente.
- [ ] Adicionar testes para duas sessões independentes.
- [ ] Adicionar teste de continuidade da mesma sessão.
- [ ] Manter alteração localizada na camada de sessão/API.

### Critério de aceite

- contexto de um cliente não é reutilizado por outro cliente sem ID compartilhado explicitamente.

---

## INT-P2-003 — Definir endpoint de saúde mínimo

**Status inicial:** `TODO`  
**Obrigatoriedade:** recomendado para integração saudável; pode ser adiado formalmente

### Ações

- [ ] Criar `GET /api/health` ou equivalente mínimo.
- [ ] Não transformar healthcheck em diagnóstico pesado de Ollama/Qdrant a cada chamada.
- [ ] Retornar apenas estado técnico seguro necessário para disponibilidade da API.
- [ ] Testar resposta.

### Critério de aceite

- frontend pode distinguir “interface carregou” de “API está acessível”.

---

## INT-P2-004 — Revisar validação de request e códigos HTTP

**Status inicial:** `TODO`

### Ações

- [ ] Definir comportamento para `mensagem` vazia/só espaços.
- [ ] Definir tamanho máximo razoável ou registrar decisão de não limitar no MVP.
- [ ] Confirmar semântica de 4xx vs. resposta controlada 200.
- [ ] Evitar converter falha técnica inesperada em sucesso silencioso.

### Critério de aceite

- contrato de entrada possui limites e erros compreensíveis.

---

## INT-P2-005 — CORS somente se a topologia exigir

**Status inicial:** `TODO`

### Ações

- [ ] Se proxy/mesma origem resolver desenvolvimento e produção, não adicionar CORS por ritual.
- [ ] Se necessário, adicionar `CORSMiddleware` com origens explícitas por configuração.
- [ ] Não liberar credenciais/origens indiscriminadamente.
- [ ] Testar origem permitida e não permitida quando aplicável.

### Critério de aceite

- política de origem coincide com a arquitetura aprovada.

---

# FASE P3 — Adaptação do frontend ao contrato real

## INT-P3-001 — Criar DTOs TypeScript do contrato HTTP

**Status inicial:** `TODO`

### Ações

- [ ] Criar interface para request do chat.
- [ ] Criar interface para envelope HTTP de response.
- [ ] Criar interface para `ProcessualChatResponse`.
- [ ] Tipar `fontes` com o mínimo público conhecido ou tipo seguro explícito.
- [ ] Eliminar `Observable<any>` do `ChatService`.

### Critério de aceite

- TypeScript detecta incompatibilidades básicas do contrato em compilação.

---

## INT-P3-002 — Implementar armazenamento do `session_id`

**Status inicial:** `TODO`  
**Dependência:** INT-P1-003 / INT-P2-002

### Ações

- [ ] Criar responsabilidade clara para ler/gravar sessão.
- [ ] Preferir `sessionStorage` conforme estratégia aprovada.
- [ ] Não misturar `session_id` com histórico de processos.
- [ ] Primeira chamada pode omitir ID; chamadas seguintes reutilizam o retornado.
- [ ] Definir limpeza/reset de conversa.

### Critério de aceite

- duas mensagens consecutivas do mesmo usuário usam a mesma sessão retornada pela API.

---

## INT-P3-003 — Alinhar `ChatService` ao endpoint real

**Status inicial:** `TODO`

### Ações

- [ ] Alterar `/api/chat` para `/api/processos/chat`.
- [ ] Enviar `{ session_id, mensagem }` conforme contrato.
- [ ] Retornar observable tipado.
- [ ] Aplicar timeout conforme política P1.
- [ ] Não adicionar regra de negócio ao service.

### Critério de aceite

- request Angular corresponde exatamente ao contrato FastAPI.

---

## INT-P3-004 — Remover mock do caminho de sucesso

**Status inicial:** `TODO`

### Ações

- [ ] Em `next`, consumir `response.resultado.resposta`.
- [ ] Registrar `response.session_id`.
- [ ] Atualizar `processo_ativo`/histórico quando disponível.
- [ ] Em `error`, não chamar `responderMock()`.
- [ ] Garantir `carregando=false` em sucesso e erro.
- [ ] Evitar duplicação de finalização de estado.

### Critério de aceite

- a mensagem mostrada no chat vem efetivamente do backend no caminho de sucesso.

---

## INT-P3-005 — Implementar apresentação de erro real

**Status inicial:** `TODO`

### Ações

- [ ] Usar `StateService.erro` ou estrutura equivalente.
- [ ] Mostrar erro de rede/timeout de forma segura e recuperável.
- [ ] Manter resposta controlada do backend como mensagem normal quando o contrato assim definir.
- [ ] Não mostrar stack trace ou objeto HTTP bruto.
- [ ] Permitir nova tentativa após falha.

### Critério de aceite

- falha não produz resposta mockada falsa e não deixa interface permanentemente em loading.

---

## INT-P3-006 — Corrigir histórico de processos consultados

**Status inicial:** `TODO`

### Problema observado

A pergunta inteira é gravada atualmente como `numero_processo`.

### Ações

- [ ] Usar `resultado.processo_ativo` como fonte primária do número.
- [ ] Não adicionar histórico quando não houver processo ativo identificável, salvo regra explícita.
- [ ] Definir deduplicação/ordenação de consultas se necessário.
- [ ] Preservar limite atual de 3 itens ou alterar somente mediante decisão de produto.

### Critério de aceite

- perguntas como “qual foi a última movimentação?” não aparecem como número processual no histórico.

---

## INT-P3-007 — Tornar indicador de disponibilidade verdadeiro

**Status inicial:** `TODO`  
**Dependência:** INT-P2-003 se healthcheck for adotado

### Ações

- [ ] Remover interpretação estática de “Sistema disponível”.
- [ ] Consultar healthcheck no momento apropriado ou usar estado mais neutro.
- [ ] Definir estados: verificando / disponível / indisponível.
- [ ] Não bloquear o carregamento inteiro da interface por diagnóstico externo pesado.

### Critério de aceite

- indicador visual corresponde a uma evidência técnica real ou deixa explícito que não é um healthcheck.

---

## INT-P3-008 — Corrigir idioma/metadados mínimos da aplicação

**Status inicial:** `TODO`  
**Prioridade:** alinhamento, não bloqueante para contrato

### Ações

- [ ] Alterar `<html lang="en">` para `pt-BR`.
- [ ] Substituir título genérico `MeuPrimeiroApp` por nome aprovado ou título provisório do projeto.
- [ ] Remover/ajustar `My first Angular JS Project` se não tiver função real.
- [ ] Evitar renomear workspace/package inteiro nesta etapa sem necessidade.

### Critério de aceite

- metadados visíveis não contradizem a finalidade real do sistema.

---

# FASE P4 — Testes do frontend e contrato

## INT-P4-001 — Reparar testes preexistentes do frontend

**Status inicial:** `READY`

### Falhas observadas

- specs importam classes que não existem mais (`Chat`, `LocalStorage`, `State`);
- spec do componente importa `Chat` em vez de `ChatComponent`;
- `app.spec.ts` espera a tela padrão antiga do Angular.

### Ações

- [ ] Atualizar imports/classes sem mascarar comportamento.
- [ ] Remover ou reescrever expectativa obsoleta do título conforme interface atual.
- [ ] Confirmar compilação de `tsconfig.spec.json`.
- [ ] Executar testes reais após `npm ci`.

### Critério de aceite

- testes existentes compilam e representam o código atual.

---

## INT-P4-002 — Testar `ChatService` como fronteira HTTP

**Status inicial:** `TODO`

### Cobertura mínima

- [ ] método correto `POST`;
- [ ] URL `/api/processos/chat`;
- [ ] body contém `mensagem` e sessão conforme estado;
- [ ] response é interpretada com DTO correto;
- [ ] timeout/erro segue política aprovada.

### Critério de aceite

- regressão de endpoint/body é detectada sem depender de E2E.

---

## INT-P4-003 — Testar comportamento do `ChatComponent`

**Status inicial:** `TODO`

### Cobertura mínima

- [ ] envia mensagem do usuário;
- [ ] bloqueia envio duplicado enquanto carrega;
- [ ] renderiza resposta real recebida;
- [ ] finaliza loading no sucesso;
- [ ] finaliza loading no erro;
- [ ] apresenta erro seguro;
- [ ] salva processo ativo correto no histórico;
- [ ] não salva pergunta livre como processo.

### Critério de aceite

- componente possui testes para sucesso e falha sem depender do backend real.

---

## INT-P4-004 — Adicionar smoke test integrado da conversa

**Status inicial:** `TODO`

### Cenário obrigatório

1. subir FastAPI;
2. subir Angular com proxy/configuração aprovada;
3. consultar processo conhecido da fixture/base local;
4. confirmar resposta na interface;
5. enviar segunda pergunta sem repetir o número;
6. confirmar que o processo ativo foi preservado;
7. confirmar histórico correto;
8. confirmar ausência de erro no console/rede relevante.

### Critério de aceite

- fluxo completo navegador → FastAPI → orquestrador → resposta → navegador funciona em duas mensagens encadeadas.

---

## INT-P4-005 — Testar cenários de degradação

**Status inicial:** `TODO`

### Cenários

- [ ] backend indisponível;
- [ ] timeout;
- [ ] processo inexistente/entrada sem contexto suficiente;
- [ ] `rag_status=unavailable` sem derrubar o chat estruturado;
- [ ] falha controlada com `failed_stage`;
- [ ] refresh da página conforme política de sessão;
- [ ] nova sessão/nova aba conforme política aprovada.

### Critério de aceite

- falhas previsíveis não geram estado falso, mock ou travamento permanente.

---

# FASE P5 — Desenvolvimento local e reprodutibilidade

## INT-P5-001 — Configurar proxy de desenvolvimento Angular

**Status inicial:** `TODO`

### Ações

- [ ] Criar configuração de proxy versionada para `/api` → FastAPI local, se estratégia P1 aprovada.
- [ ] Integrar ao comando `npm start` ou documentar comando explícito.
- [ ] Não codificar URL local em componentes.
- [ ] Confirmar que chamadas `/api/...` funcionam via navegador.

### Critério de aceite

- desenvolvedor consegue subir front e back localmente sem editar código-fonte para trocar URL.

---

## INT-P5-002 — Documentar bootstrap limpo do frontend

**Status inicial:** `TODO`

### Ações

- [ ] `cd frontend`.
- [ ] versão recomendada de Node/npm documentada a partir do projeto real.
- [ ] `npm ci` como instalação reproduzível.
- [ ] `npm start`.
- [ ] `npm run build`.
- [ ] comando de testes.
- [ ] explicar que `node_modules` e `.angular/cache` não devem ser transferidos/versionados.

### Critério de aceite

- novo desenvolvedor consegue reconstruir dependências a partir de `package-lock.json`.

---

## INT-P5-003 — Documentar bootstrap limpo do backend

**Status inicial:** `TODO`

### Ações

- [ ] `cd chatbot_processual_ai`.
- [ ] criar/ativar venv.
- [ ] instalar `requirements.txt`.
- [ ] copiar `.env.example` para `.env` local.
- [ ] documentar Ollama/Qdrant opcionais/necessários por cenário.
- [ ] `uvicorn api:app --reload`.
- [ ] comando oficial de testes a partir do diretório correto.

### Critério de aceite

- instrução reproduz exatamente a premissa dos imports atuais.

---

## INT-P5-004 — Definir comando/workflow integrado de desenvolvimento

**Status inicial:** `TODO`

### Ações

- [ ] Documentar ordem para subir dependências externas, backend e frontend.
- [ ] Se útil, criar script não destrutivo para desenvolvimento local; não é obrigatório.
- [ ] Evitar adicionar Docker/Compose apenas por estética se não houver necessidade real nesta fase.

### Critério de aceite

- fluxo de execução completo cabe em uma seção curta e verificável da documentação.

---

# FASE P6 — Documentação como fonte de contexto

## INT-P6-001 — Atualizar `docs/ARCHITECTURE.md`

**Status inicial:** `TODO`

### Ações

- [ ] adicionar frontend Angular à visão arquitetural;
- [ ] registrar fronteira HTTP;
- [ ] registrar sessão web;
- [ ] registrar estratégia de rede/proxy;
- [ ] preservar separação entre chat processual, simulador e fluxo híbrido;
- [ ] atualizar pendência “Frontend visual” porque o frontend agora existe.

### Critério de aceite

- arquitetura documentada corresponde ao repositório depois da integração.

---

## INT-P6-002 — Preencher `docs/development.md`

**Status inicial:** `READY`

### Conteúdo mínimo

- [ ] requisitos locais;
- [ ] instalação limpa frontend/backend;
- [ ] comandos de execução;
- [ ] comandos de testes/build/typecheck;
- [ ] proxy/CORS;
- [ ] variáveis de ambiente;
- [ ] convenção de branches/commits relevante;
- [ ] itens que não devem ser versionados;
- [ ] troubleshooting mínimo.

### Critério de aceite

- documento é suficiente para onboarding técnico básico.

---

## INT-P6-003 — Preencher `docs/orchestration.md`

**Status inicial:** `READY`

### Conteúdo mínimo

- [ ] fluxo Browser → API → orquestrador → agentes → resposta;
- [ ] responsabilidades de cada camada;
- [ ] fluxo de sessão/processo ativo;
- [ ] comportamento em falha controlada;
- [ ] papel do RAG sem acoplar frontend;
- [ ] fronteiras entre chat processual, metas e híbrido.

### Critério de aceite

- agente/humano entende o fluxo sem inferir a partir de dezenas de arquivos.

---

## INT-P6-004 — Preencher `docs/design_philosophy.md`

**Status inicial:** `READY`

### Conteúdo mínimo

- [ ] determinismo antes de LLM onde houver regra verificável;
- [ ] LLM explica, não inventa regra de negócio;
- [ ] frontend apresenta estado real, não sucesso aparente;
- [ ] falha explícita > fallback silencioso;
- [ ] contratos claros > acoplamento entre camadas;
- [ ] mudanças pequenas, reversíveis e testáveis;
- [ ] dados sensíveis e detalhes internos não vazam para UI.

### Critério de aceite

- decisões de projeto recorrentes têm princípios explícitos.

---

## INT-P6-005 — Reconciliar README raiz com a implementação atual

**Status inicial:** `TODO`

### Ações

- [ ] substituir recomendações históricas que pareçam arquitetura vigente quando já não são;
- [ ] apresentar estrutura atual do repositório;
- [ ] apontar `docs/` como fonte técnica aprofundada;
- [ ] explicar brevemente frontend Angular + backend FastAPI;
- [ ] não prometer Playwright/LangGraph/Streamlit como já implementados.

### Critério de aceite

- README não induz humano ou agente a uma arquitetura diferente da real.

---

## INT-P6-006 — Atualizar README do frontend

**Status inicial:** `TODO`

### Ações

- [ ] remover caráter puramente template do Angular CLI;
- [ ] explicar finalidade do frontend;
- [ ] documentar API/proxy;
- [ ] documentar instalação, build e testes;
- [ ] registrar política de sessão relevante ao frontend.

### Critério de aceite

- README do frontend serve ao projeto, não apenas ao template Angular.

---

# FASE P7 — Regressão, segurança e fechamento

## INT-P7-001 — Executar regressão backend

**Status inicial:** `TODO`

### Ações

- [ ] executar testes focados da API/sessão;
- [ ] executar suite completa existente;
- [ ] comparar com baseline;
- [ ] investigar qualquer falha nova.

### Critério de aceite

- nenhuma regressão backend não explicada.

---

## INT-P7-002 — Executar regressão frontend

**Status inicial:** `TODO`

### Ações

- [ ] ambiente reconstruído com `npm ci`;
- [ ] typecheck aplicação;
- [ ] typecheck/testes specs;
- [ ] `npm test -- --watch=false`;
- [ ] `npm run build`;
- [ ] revisar warnings relevantes.

### Critério de aceite

- build e testes acordados passam em ambiente limpo.

---

## INT-P7-003 — Revisar segurança da fronteira

**Status inicial:** `TODO`

### Ações

- [ ] nenhum `.env` real no diff;
- [ ] nenhum token/credencial no frontend;
- [ ] nenhum path local/ID interno exposto em response pública;
- [ ] CORS restrito se usado;
- [ ] `session_id` não contém dado sensível;
- [ ] erros não exibem stack traces;
- [ ] fontes RAG permanecem sanitizadas conforme contrato.

### Critério de aceite

- revisão de segurança concluída sem vazamento conhecido.

---

## INT-P7-004 — Revisar diff e higiene final

**Status inicial:** `TODO`

### Ações

- [ ] `git diff --check`;
- [ ] revisar diff completo;
- [ ] procurar debug/log temporário;
- [ ] procurar alteração fora do escopo;
- [ ] confirmar que `node_modules`, `.angular`, `__pycache__`, bancos e `.env` não entraram;
- [ ] confirmar docs coerentes com implementação;
- [ ] confirmar que arquivos do simulador não mudaram sem necessidade.

### Critério de aceite

- diff é focado, legível e reversível.

---

## INT-P7-005 — Smoke integrado final

**Status inicial:** `TODO`

### Cenário mínimo de aceite

- [ ] backend sobe do zero;
- [ ] frontend sobe do zero;
- [ ] UI detecta/representa disponibilidade conforme decisão;
- [ ] consulta processo válido;
- [ ] exibe resposta real;
- [ ] exibe processo correto no histórico;
- [ ] pergunta contextual seguinte funciona sem repetir número;
- [ ] sessão de segundo cliente é isolada;
- [ ] backend indisponível produz erro recuperável;
- [ ] nenhum erro crítico no console/rede.

### Critério de aceite

- integração é funcional do ponto de vista do usuário e da arquitetura.

---

## INT-P7-006 — Gate de prontidão para merge

**Status inicial:** `TODO`

A branch só pode ser declarada **READY_FOR_MERGE** quando:

- [ ] todos os itens bloqueantes estão `VALIDATED`;
- [ ] itens adiados possuem justificativa e risco residual registrados;
- [ ] testes backend aprovados;
- [ ] testes frontend aprovados;
- [ ] build frontend aprovado;
- [ ] smoke integrado aprovado;
- [ ] diff revisado;
- [ ] `git diff --check` limpo;
- [ ] documentação atualizada;
- [ ] nenhum segredo/artefato local incluído;
- [ ] commits representam unidades lógicas compreensíveis;
- [ ] controle de progresso contém hashes reais dos commits efetuados.

**Saída permitida:** `READY_FOR_MERGE` ou `NOT_READY` com justificativa objetiva.

---

# 3. Sequência recomendada

```text
P0 Baseline/Governança
        ↓
P1 Contrato/Decisões
        ↓
P2 Fronteira Backend
        ↓
P3 Adaptação Frontend
        ↓
P4 Testes de contrato/componente
        ↓
P5 Execução local reproduzível
        ↓
P6 Documentação alinhada
        ↓
P7 Regressão + Smoke + Merge Gate
```

Não antecipar P3 “porque é só trocar a URL”: sessão, contrato, erro e topologia devem estar decididos antes.

---

# 4. Definition of Done global

A integração não é considerada concluída quando “a tela respondeu uma vez”. Ela é concluída quando:

1. **Contrato:** request/response estão documentados e tipados.
2. **Isolamento:** sessões não vazam entre clientes.
3. **Comportamento:** frontend usa a resposta real e trata falhas corretamente.
4. **Reprodutibilidade:** projeto é reconstruível sem copiar `node_modules`.
5. **Testes:** backend, frontend e fluxo integrado possuem evidência.
6. **Documentação:** arquitetura e desenvolvimento descrevem o estado atual.
7. **Segurança:** nenhum segredo/detalhe interno indevido foi exposto.
8. **Rastreabilidade:** cada unidade lógica possui status, evidência e commit associado.
9. **Reversibilidade:** commits e diff permitem entender/reverter a integração sem desmontar o backend original.
