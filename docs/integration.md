# Integração entre o frontend Angular e o backend FastAPI

## Objetivo e escopo positivo

Esta integração existe para conectar duas aplicações existentes por meio de uma
fronteira HTTP estável:

```text
Browser / Angular
        ↓
      HTTP
        ↓
     FastAPI
```

Seu objetivo é permitir que o usuário consuma, pelo frontend existente, as
funcionalidades já existentes e autorizadas do backend. A topologia lógica é
formalizada abaixo; os detalhes do contrato HTTP, da estratégia de sessão, de
erros, limites temporais, CORS, proxy e topologia física de rede permanecem para
os itens específicos da fase P1.

## Topologia e fronteira arquitetural

O frontend Angular e o backend FastAPI são aplicações irmãs e independentes.
Eles não compartilham implementação interna: sua integração ocorre
exclusivamente pela API pública, mediante HTTP e JSON.

```text
┌──────────────────────────────┐
│ Browser                      │
│ Angular                      │
│ componentes / estado / UI    │
└──────────────┬───────────────┘
               │
               │ HTTP + JSON
               │ API pública
               ▼
┌──────────────────────────────┐
│ FastAPI                      │
│ /api/...                     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Backend interno              │
│ orquestradores / agentes     │
│ serviços / persistência      │
│ RAG / Ollama / Qdrant        │
└──────────────────────────────┘
```

A FastAPI é a porta HTTP pública do backend. As rotas existentes sob
`/api/...` comprovam essa fronteira, mas este item não congela endpoints,
payloads ou semânticas de resposta. Em particular, a divergência atual entre o
serviço Angular (`/api/chat`) e a rota processual FastAPI
(`/api/processos/chat`) deve ser resolvida pelo contrato de `INT-P1-002`, não
por esta decisão topológica.

### Direção das dependências

A direção permitida é:

```text
Angular → API pública FastAPI → backend interno
```

O Angular pode depender somente do contrato público HTTP/JSON. Componentes e
serviços Angular não podem depender diretamente de agentes Python, SQLite,
Qdrant, Ollama, RAG interno nem do filesystem do backend. Qualquer contexto
conversacional web e qualquer erro devem atravessar a mesma fronteira pública,
sem exposição de memória, caminhos, exceções ou outros detalhes internos.

O backend pode expor recursos por sua API pública, validar e rotear requisições
na fronteira e acionar os fluxos internos apropriados. Ele não deve exigir
conhecimento de componentes, services, estilos ou estado interno da interface
Angular.

### Responsabilidades e encapsulamento

O frontend é responsável pela interface, interação com o usuário, estado de
apresentação, construção de requests e interpretação de responses conforme a
API pública. A FastAPI e o backend são responsáveis por expor essa API, validar
e rotear requisições na fronteira, executar os fluxos internos e devolver uma
resposta pública estruturada sem revelar detalhes de implementação.

A implementação interna do backend pode evoluir sem exigir alterações no
Angular desde que o contrato público da API permaneça compatível. Componentes,
organização, estilos e estado interno do Angular podem evoluir sem exigir
mudanças internas no backend desde que as requisições continuem respeitando o
contrato público.

DTOs, sessão, semântica detalhada de erros, limites temporais e topologia física
de rede serão definidos, respectivamente, em `INT-P1-002` a `INT-P1-006`.
Nenhuma dessas decisões é estabelecida aqui. O diretório
`simulador-de-metas/` não integra esta topologia Angular–FastAPI do chat
processual, salvo dependência futura comprovada.

## Contrato HTTP v1 — chat processual

Esta é a versão lógica e documental do contrato público já implementado. Ela
não cria um prefixo `/v1`, uma rota nova nem um protocolo alternativo.

### Endpoint e representação

- método e rota: `POST /api/processos/chat`;
- request: objeto JSON enviado com `Content-Type: application/json`;
- response de sucesso: objeto JSON com `Content-Type: application/json`;
- transporte: HTTP síncrono, sem streaming, SSE ou WebSocket.

O endpoint observado não declara `response_model`. A estrutura de sucesso é
montada explicitamente pela função HTTP, e `resultado` é a serialização do
`ProcessualChatResponse` retornado pelo orquestrador.

### Request

| Campo | Tipo JSON | Obrigatório | Pode ser omitido | Aceita `null` | Semântica |
|---|---|---:|---:|---:|---|
| `session_id` | string ou `null` | não | sim | sim | Identificador de transporte usado para selecionar o estado conversacional. O valor não vazio é aparado nas extremidades antes do uso. Omissão, `null`, string vazia e string composta apenas por espaços são normalizados atualmente para `"default"`. Não há validação de formato ou tamanho. |
| `mensagem` | string | sim | não | não | Texto corrente enviado pelo usuário ao fluxo processual. Deve conter ao menos um caractere não-whitespace. Mensagens válidas são repassadas ao orquestrador sem transformação na fronteira HTTP. Não há limite adicional de tamanho no MVP. |

Campos adicionais do objeto são ignorados pelo modelo Pydantic atual. Isso é
comportamento observado, não autorização para o frontend enviá-los. A política
de geração, persistência, expiração e isolamento de `session_id` está definida
na seção correspondente.

#### Validação de `mensagem` e tamanho no MVP

A fronteira Pydantic rejeita com `422` campo ausente, `null`, tipo incompatível,
string vazia e string composta somente por whitespace (`espaço`, `\t`, `\n` ou
`\r`). A verificação usa `strip()` apenas para determinar se existe conteúdo;
ela devolve a string original e não remove espaços de uma mensagem válida.
Requests rejeitadas não alcançam o endpoint, não chamam o orquestrador e não
criam sessão.

Não foi adotado limite máximo adicional para `mensagem` no MVP. Não existe
atualmente requisito de produto, limite da interface ou restrição de
processamento suficientemente sustentada para escolher um valor sem
arbitrariedade. Permanecem aplicáveis os limites normais do servidor e do
transporte. Esta decisão deve ser revista antes de exposição pública em escala,
considerando proteção de recursos e os limites efetivos da infraestrutura.

### Response

Envelope raiz:

| Campo | Tipo JSON | Obrigatório | Aceita `null` | Semântica |
|---|---|---:|---:|---|
| `session_id` | string | sim | não | Identificador efetivamente selecionado após a normalização da request. Sempre é incluído na resposta de sucesso e deve ser tratado como identificador opaco de transporte. Não define seu ciclo de vida. |
| `resultado` | objeto | sim | não | Resultado público do passo de chat. Sempre é incluído quando o endpoint conclui com sucesso HTTP, inclusive quando o pipeline converte uma exceção interna em falha controlada. |

Campos de `resultado`:

| Campo | Tipo JSON | Obrigatório | Aceita `null` | Semântica | Classificação pública | Uso frontend v1 |
|---|---|---:|---:|---|---|---|
| `tipo` | string, valor `"processual_chat"` | sim | não | Discriminador constante produzido pelo orquestrador processual atual. | contrato público auxiliar | condicional; validar se a UI distinguir famílias de resultado |
| `intent` | string ou `null` | sim | sim | Intenção efetiva reconhecida para a mensagem; pode faltar quando ainda não foi identificada, inclusive em falha antecipada. A enumeração completa não é congelada nesta versão. | contrato público auxiliar | informativo; não consumido inicialmente |
| `resposta` | string | sim | não | Texto utilizável que o frontend apresenta ao usuário. Pode ser conteúdo normal ou mensagem segura de uma falha controlada; seu texto literal é dinâmico e não faz parte do contrato. | contrato principal | necessário |
| `processo_ativo` | string ou `null` | sim | sim | Número do processo atualmente associado à conversa, obtido do contexto corrente ou do estado da sessão; é `null` quando não há processo ativo identificável. Não representa a pergunta livre nem autoriza inferir que qualquer texto do usuário seja número processual. | contrato principal | condicional; necessário quando a UI associar histórico ao processo identificado |
| `collection_status` | string ou `null` | sim | sim | Estado observado da tentativa de coleta/seleção do processo. Valores produzidos hoje: `success`, `already_active`, `missing_number`, `not_found` e `not_needed`; pode ser `null` se o pipeline falhar antes de produzir contexto. | contrato público auxiliar | informativo/condicional |
| `failed_stage` | string ou `null` | sim | sim | Nome da etapa em que o orquestrador capturou uma exceção e produziu resposta segura; é `null` no fluxo sem falha controlada. Valores observáveis atualmente são `Agente 1` a `Agente 4`, conforme a etapa alcançada. Não é erro HTTP por si só. | contrato público auxiliar | condicional; política de UX adiada para `INT-P1-004` |
| `rag_status` | string ou `null` | sim | sim | Estado da recuperação semântica: `not_needed`, `success`, `empty`, `unavailable` ou `error`; pode ser `null` quando nenhum contexto RAG foi produzido. `unavailable` ou `error` não implicam automaticamente erro HTTP. | contrato público auxiliar | informativo/condicional |
| `fontes` | array de objetos | sim | não | Fontes deduplicadas associadas aos trechos recuperados; é `[]` quando não há fontes válidas. | contrato público auxiliar com elementos ainda instáveis | não consumido inicialmente |

Os objetos de `fontes` expõem hoje chaves como `tipo`, `titulo`, `data` e
`conteudo`, derivadas de metadata interna do RAG, mas não possuem schema ou
validação de saída próprios. O contrato v1 congela somente o contêiner como
`array<object>`; nomes, obrigatoriedade, nulabilidade e tipos internos desses
objetos são **NÃO DETERMINADOS** e não devem virar acoplamento da UI. IDs de
SQLite/Qdrant, caminhos, objetos Python, configurações, tokens, segredos e
stack traces não fazem parte do contrato.

### Semântica HTTP factual

- **Request aceito:** a função retorna `200 OK` com o envelope documentado. Uma
  falha controlada do pipeline também retorna atualmente `200 OK` e é
  observável por `resultado.failed_stage`, sem invalidar
  `resultado.resposta`.
- **Erro de validação:** JSON ausente ou incompatível com o contrato de entrada
  gera `422 Unprocessable Entity` no formato FastAPI/Pydantic
  `{"detail": [...]}`.
  Por exemplo, omitir `mensagem`, enviá-la como `null`, usar tipo não textual ou
  enviar texto vazio/somente whitespace produz `422`.
- **Erro HTTP explícito:** a função do endpoint não lança `HTTPException` nem
  define outro status explícito. O roteamento do framework ainda produz, por
  exemplo, `405` para método não permitido e `404` para rota inexistente, com
  `{"detail": "..."}`.
- **Falha inesperada:** exceção que escape do orquestrador ou ocorra depois
  dele não possui tratamento específico no endpoint; sob o servidor FastAPI
  resulta em erro interno `500`. A resposta pública não deve incluir stack
  trace, filesystem, segredo ou a mensagem interna da exceção.

A política completa de erro e degradação está definida na seção
“Semântica de erros e degradação” deste documento.

### Healthcheck mínimo da API

`GET /api/health` responde `200 OK` com `{"status":"ok"}` quando a fronteira
FastAPI está acessível e consegue responder uma requisição HTTP simples. Esse
healthcheck da API não é um healthcheck profundo das dependências: ele não
consulta Ollama, Qdrant, RAG, banco, agentes ou orquestradores e não cria nem
altera sessões.

Portanto, o frontend pode futuramente inferir somente “API disponível” a partir
de uma resposta `200`; não pode inferir que o chatbot inteiro ou suas
dependências estejam saudáveis. A rota não reutiliza os campos de estado do
contrato de chat, como `failed_stage`, `rag_status` ou `collection_status`.

### Exemplos representativos

Os textos de `resposta` abaixo são ilustrações semânticas, não fixtures nem
literais garantidos pelo chatbot.

#### A — sucesso

```http
POST /api/processos/chat
Content-Type: application/json

{"session_id":"sessao-opaca","mensagem":"Qual foi a última movimentação?"}
```

```json
{
  "session_id": "sessao-opaca",
  "resultado": {
    "tipo": "processual_chat",
    "intent": "process_question",
    "resposta": "<texto dinâmico utilizável pelo usuário>",
    "processo_ativo": "<número do processo ativo>",
    "collection_status": "not_needed",
    "failed_stage": null,
    "rag_status": "not_needed",
    "fontes": []
  }
}
```

#### B — processo ausente ou não identificado

O backend sustenta `processo_ativo: null` quando não há processo ativo e
`collection_status: "missing_number"` quando uma consulta de processo não traz
número normalizável. A classificação e o texto podem variar conforme a
mensagem; portanto, não são congelados como literais neste exemplo.

```json
{
  "session_id": "default",
  "resultado": {
    "tipo": "processual_chat",
    "intent": "process_lookup",
    "resposta": "<texto dinâmico informando a insuficiência de contexto>",
    "processo_ativo": null,
    "collection_status": "missing_number",
    "failed_stage": null,
    "rag_status": "not_needed",
    "fontes": []
  }
}
```

#### C — falha controlada

Uma exceção capturada na etapa inicial do orquestrador produz uma resposta HTTP
válida e segura. `Agente 1` é um valor comprovado pelos testes existentes.

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "session_id": "default",
  "resultado": {
    "tipo": "processual_chat",
    "intent": null,
    "resposta": "<mensagem segura de falha controlada>",
    "processo_ativo": null,
    "collection_status": null,
    "failed_stage": "Agente 1",
    "rag_status": null,
    "fontes": []
  }
}
```

#### D — erro HTTP de validação

Request inválida:

```json
{}
```

Resposta observada, abreviada aos campos estáveis necessários para reconhecer
o erro de entrada:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "mensagem"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

### Compatibilidade do contrato v1

São compatíveis a adição de campos opcionais ou metadata que consumidores
antigos possam ignorar e novos valores somente quando o consumidor afetado
estiver preparado para tolerá-los. O frontend deve depender apenas dos campos
públicos necessários ao seu comportamento e ignorar campos adicionais
desconhecidos quando isso não comprometer a semântica do contrato.

São potencialmente breaking: mudar método ou rota; renomear, remover ou mover
campos obrigatórios; alterar tipo ou nulabilidade de forma incompatível; exigir
campo antes opcional; mudar significado semântico; mover
`resultado.resposta`; alterar a estrutura esperada sem versionamento ou
transição; ou ampliar valores quando o consumidor não for tolerante. Ignorar
campos desconhecidos não permite tolerar silenciosamente a ausência ou mudança
de um campo obrigatório.

### Decisões explicitamente adiadas

- `INT-P1-003`: geração e ciclo de vida de sessão, persistência no navegador,
  refresh, abas, expiração, reset, reinício do backend e `_SESSIONS`;
- `INT-P1-004`: política completa de erro/falha e UX correspondente, definida
  abaixo sem alterar este contrato;
- `INT-P1-005`: timeout final;
- `INT-P1-006`: proxy, CORS, origins, URLs e topologia física de rede.

Este contrato não cria DTO TypeScript nem altera schema Python, endpoint,
backend ou frontend.

## Estratégia de sessão web

> **DECISÃO ALVO / COMPORTAMENTO A IMPLEMENTAR em P2 e P3.** O backend e o
> frontend ainda não implementam esta política. O comportamento factual atual
> continua sendo o fallback compartilhado `"default"` descrito no contrato v1.

### Objetivo e problema atual

A sessão correlaciona mensagens de uma mesma conversa sem transformar o
identificador em usuário, histórico ou credencial. Atualmente,
`_normalize_session_id()` converte campo omitido, `null`, string vazia ou apenas
espaços em `DEFAULT_SESSION_ID` (`"default"`). `_get_session_state()` usa esse
valor como chave do dicionário global em memória `_SESSIONS`. Assim, dois
clientes que não enviam ID selecionam a mesma entrada e podem compartilhar
`conversation`, `active_process` e `last_intent` indevidamente.

O estado criado por `create_session_state()` contém esses três campos. O
orquestrador usa `session_state["active_process"]` como fallback ao construir
`resultado.processo_ativo`; portanto, o isolamento da sessão também isola o
processo ativo. Hoje, reenviar o mesmo ID seleciona a mesma entrada de
`_SESSIONS` e preserva esse contexto enquanto o processo backend permanecer
vivo.

### Decisão

- Quando a request não trouxer `session_id` utilizável conforme o contrato v1,
  o backend deve gerar um novo UUID aleatório, criar uma sessão interna e
  devolver o identificador em `response.session_id`. O UUID é escolhido por ser
  opaco, não derivado de dados do usuário e adequado ao transporte JSON; sua
  estrutura não expõe o estado dos agentes.
- O Angular deve guardar somente o ID retornado em `sessionStorage`, em
  responsabilidade distinta do serviço de histórico. Chamadas seguintes da
  mesma conversa devem reenviar o mesmo ID.
- Um ID conhecido pelo backend reutiliza o contexto existente. Um ID válido
  recebido, mas desconhecido por `_SESSIONS`, cria um contexto vazio associado
  ao próprio ID e ele é devolvido sem alteração. Esta opção preserva a
  previsibilidade do identificador fornecido e o contrato P1-002, mas não simula
  continuidade: o contexto anterior, inclusive `active_process`, foi perdido.
- Não haverá reutilização automática de `"default"` para clientes sem sessão.
  Clientes diferentes recebem contextos distintos, salvo se enviarem
  deliberadamente o mesmo identificador.

O campo HTTP permanece `session_id`, string opcional e anulável na request e
string obrigatória na response. Omissão, `null`, vazio e apenas espaços
continuam sendo formas de “sem sessão utilizável”; muda futuramente apenas a
seleção da sessão, sem redefinir a superfície congelada em `INT-P1-002`.

### Ciclo de vida

| Cenário | ID no browser | Estado backend | Resultado alvo |
|---|---|---|---|
| primeira mensagem | ausente | nenhum | backend gera ID opaco e cria nova sessão |
| segunda mensagem na mesma aba | presente | presente | reutiliza o mesmo contexto e preserva `processo_ativo` |
| refresh na mesma aba | presente | presente | `sessionStorage` preserva o ID e o backend reutiliza o contexto |
| refresh após restart do backend | presente | ausente | cria contexto vazio sob o ID recebido; não recupera `processo_ativo` anterior |
| nova aba | independente por padrão | — | inicia nova sessão na primeira mensagem |
| aba ou navegador fechado | descartável | pode permanecer em memória | encerra a continuidade pelo browser, sem remoção backend imediata |
| reset/nova conversa | descartado | pode permanecer em memória | a próxima mensagem sem ID inicia novo contexto |

`sessionStorage` é adequado porque seu escopo acompanha a sessão da aba,
sobrevive a reloads e não torna a conversa uma identidade duradoura. A política
da aplicação é de abas independentes por padrão. Há uma particularidade do
navegador: quando uma página possui `opener`, uma nova aba pode receber uma
cópia inicial do `sessionStorage` da origem; depois da cópia, os storages são
separados, conforme a documentação da
[Web API `sessionStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage).
P3 deve respeitar a independência desejada e avaliar essa condição ao
implementar, sem antecipar workaround neste item.

Fechar a aba ou janela encerra sua área de `sessionStorage`. Não é necessário,
no MVP, avisar o backend nem apagar imediatamente a entrada correspondente. Um
reset conceitual também descarta o ID no browser; não exige deleção sincronizada
da sessão em memória. Esta decisão não cria botão ou fluxo de UI.

### Isolamento, segurança e privacidade

O `session_id` é somente uma chave opaca de correlação de contexto:

```text
session_id != numero_processo
session_id != histórico
session_id != usuário
session_id != token de autenticação
```

Ele não representa identidade, autenticação ou autorização; não deve conter
nome, CPF, número de processo, conteúdo da conversa, PII, dado sensível nem
estado interno serializado. Possuir um ID significa apenas solicitar a
continuidade do contexto associado. Sem autenticação, não há proteção prometida
contra duas partes que compartilhem deliberadamente um ID conhecido: ambas
selecionarão o mesmo contexto.

O isolamento obrigatório é uma chave distinta por cliente/conversa, mantendo
`processo_ativo` e as mensagens de A separados dos de B. A continuidade
obrigatória é o inverso: duas perguntas que enviem o mesmo ID devem alcançar o
mesmo estado enquanto ele existir no backend.

### Limitações do MVP

`_SESSIONS` é um dicionário local ao processo Python. Não há TTL, limite de
quantidade, limpeza, eviction nem persistência confirmados. Reiniciar o backend
perde todas as sessões; um ID ainda presente no browser não prova que seu
contexto continua disponível. Também não há compartilhamento de estado entre
processos ou instâncias backend.

**DÍVIDA TÉCNICA:** sessões em memória não possuem estratégia de
expiração/limite confirmada. Uma política deve ser definida antes de escala ou
produção relevante para evitar crescimento sem controle, sem escolher agora
TTL, limite, scheduler, Redis ou banco.

### Decisões adiadas

- A semântica de erro, mensagens, UX, `failed_stage` e matriz HTTP está definida
  abaixo; a perda de contexto não deve expor erro interno.
- P2: geração efetiva do UUID, substituição do fallback, isolamento e testes da
  API.
- P3: serviço de sessão, uso efetivo de `sessionStorage`, captura da response e
  reset no frontend.

## Semântica de erros e degradação

### Princípio e comportamento factual

Esta política interpreta a superfície congelada em `INT-P1-002`; não cria
campo, enum, DTO, status HTTP nem endpoint. A classificação começa pela
fronteira HTTP/transporte e, somente quando existe uma resposta `2xx` no
contrato, considera `resultado.failed_stage`, a usabilidade de
`resultado.resposta` e os estados auxiliares.

No comportamento atual de `POST /api/processos/chat`, FastAPI/Pydantic rejeita
body ausente ou inválido, `mensagem` ausente, `null`, vazia, somente whitespace
ou de tipo incompatível com `422`; roteamento pode produzir outros `4xx`, como
`404` e `405`. O endpoint não
lança `HTTPException` nem converte exceção explicitamente. O orquestrador, por
sua vez, captura `Exception` durante os Agentes 1 a 4 e devolve uma falha
controlada com texto fixo seguro e `failed_stage`; o endpoint serializa esse
resultado como `200 OK`. Exceção fora dessa proteção — por exemplo, na camada
HTTP, ao registrar a mensagem ou serializar o retorno — não tem handler
específico e pode escapar como `500`.

O frontend observado ainda chama `/api/chat`, usa `Observable<any>` e encaminha
tanto `next` quanto `error` ao mesmo mock de sucesso. Esse é diagnóstico do
baseline, não a política aprovada: uma falha real nunca deve ser convertida em
resposta mockada de sucesso.

### Categorias e precedência

1. **Sucesso funcional:** houve `2xx`, o envelope do contrato e
   `resultado.resposta` são utilizáveis, `failed_stage` é `null` e nenhuma
   limitação invalida a resposta principal. `collection_status` esperado, como
   `missing_number` ou `not_found`, pode representar uma resposta válida do
   domínio; não deve ser convertido em `4xx` apenas porque o processo não foi
   localizado.
2. **Sucesso com degradação:** houve `2xx`, `failed_stage` é `null` e a resposta
   continua utilizável, mas uma capacidade auxiliar necessária foi limitada.
   O caso comprovado é RAG requerido com `rag_status` `unavailable`; `error`
   possui a mesma semântica não fatal no código, que continua com dados
   estruturados. `empty` informa ausência de trechos úteis e pode limitar a
   resposta sem provar indisponibilidade técnica.
3. **Falha controlada do pipeline:** houve `2xx` e o orquestrador capturou uma
   exceção prevista pela fronteira de segurança, devolvendo `failed_stage` não
   nulo e uma mensagem pública segura em `resultado.resposta`. É uma falha
   funcional, não sucesso comum nem erro HTTP. Os demais estados podem refletir
   apenas o contexto produzido antes da etapa que falhou.
4. **Erro HTTP de entrada/contrato:** houve `4xx`; não existe resposta normal do
   chatbot. O frontend reconhece a request rejeitada sem depender da estrutura
   completa de `detail` do FastAPI/Pydantic e não renderiza esse payload como
   fala do bot.
5. **Erro de transporte:** nenhuma response HTTP funcional foi recebida por
   indisponibilidade, conexão recusada, DNS/rede ou interrupção. Transporte não
   possui `resultado` e nunca deve gerar `failed_stage` sintético no frontend.
6. **Falha técnica inesperada:** houve `5xx`, response incompatível com o
   contrato ou outra exceção técnica não controlada. Não é resposta
   conversacional; o usuário recebe somente mensagem genérica segura e o
   detalhe fica em diagnóstico/log.

Timeout pode tecnicamente aparecer como erro do cliente/transporte, mas tempo,
margem, classificação específica e mensagem permanecem reservados a
`INT-P1-005`.

### Matriz HTTP e pipeline

| Situação | HTTP/transporte | `resultado` | `failed_stage` | `rag_status` / `collection_status` | Resposta exibível | Classificação |
|---|---|---:|---|---|---:|---|
| resposta normal | `2xx` | sim, válido | `null` | estados compatíveis com a resposta | `resultado.resposta` | sucesso funcional |
| processo ausente/não encontrado | `2xx` | sim, válido | `null` | `collection_status=missing_number` ou `not_found`; RAG conforme fluxo | `resultado.resposta` | resposta funcional do domínio, possivelmente limitada |
| RAG auxiliar limitado | `2xx` | sim, válido | `null` | `rag_status=unavailable`, `error` ou `empty`; coleta independente | `resultado.resposta` | sucesso degradado quando a resposta permanece utilizável |
| exceção capturada no pipeline | `2xx` atual | sim | `Agente 1` a `Agente 4` | valor já produzido ou `null`; não prevalece sobre a falha | mensagem segura de `resultado.resposta` | falha controlada |
| request/rota/método inválido | `4xx` | não normal | n/a | n/a | não como resposta do bot | erro HTTP |
| backend inacessível/rede | sem response | não | n/a | n/a | não | transporte |
| exceção não controlada/contrato inválido | `5xx` ou resposta incompatível | não normal | n/a | n/a | nunca o payload bruto | falha técnica inesperada |

A precedência normativa é: ausência de response identifica transporte; response
`4xx`/`5xx` identifica erro HTTP/técnico; em `2xx` contratual,
`failed_stage != null` identifica falha controlada; sem ele, uma resposta
utilizável com capacidade auxiliar limitada identifica degradação; os demais
casos utilizáveis são sucesso funcional. Um `2xx` sem envelope obrigatório ou
sem `resultado.resposta` utilizável é violação técnica do contrato, não sucesso.

### Semântica dos campos

#### `failed_stage`

É `string | null`, obrigatório e anulável no contrato v1. Os valores produzidos
pelo código são `Agente 1`, `Agente 2`, `Agente 3` e `Agente 4`; o teste atual
confirma diretamente `Agente 1`. Sua presença significa que o orquestrador
capturou exceção na etapa indicada e substituiu o resultado principal por uma
resposta segura. `null` significa somente que essa captura não ocorreu: não
prova que RAG, coleta ou todos os subsistemas estejam saudáveis. É sinal de
classificação para o frontend, nunca texto para exibição direta; nomes de
agentes continuam detalhes internos.

#### `rag_status`

É `string | null`, obrigatório e anulável. Valores confirmados:
`not_needed`, `success`, `empty`, `unavailable` e `error`. `not_needed` indica
que a rota não exigiu RAG; `success`, que trechos foram recuperados; `empty`,
que não houve processo/chunk/resultado útil; `unavailable`, que a capacidade
estava desabilitada ou houve falha conhecida de embedding/Qdrant; e `error`,
que outra exceção foi capturada pelo recuperador. O código retorna contexto
vazio e continua a análise com dados estruturados em todos os três estados de
limitação. Portanto, nenhum valor de `rag_status` é isoladamente fatal nem
autoriza o Angular a conhecer Qdrant, embedding ou Ollama. O frontend pode usar
a condição pública apenas para não apresentar saúde plena quando houver
degradação; inicialmente, o campo é metadata diagnóstica/condicional e a
resposta pública permanece a fonte de conteúdo.

#### `collection_status`

É `string | null`, obrigatório e anulável. Valores confirmados: `success`,
`already_active`, `missing_number`, `not_found` e `not_needed`. Eles indicam,
respectivamente, processo localizado, processo já ativo, número ausente ou
incompleto, processo não encontrado e coleta local desnecessária. O campo muda
durante o Agente 2 e pode ser `null` se a falha controlada ocorrer antes de o
contexto ser produzido. `missing_number` e `not_found` são limitações
funcionais esperadas, não erro HTTP nem falha técnica; o pipeline ainda monta
uma resposta ao usuário. O uso frontend é informativo/condicional e não deve
acoplar a UI ao repositório local.

Os três campos podem coexistir. `failed_stage` prevalece na classificação de
um `2xx` como falha controlada; `rag_status` descreve somente a capacidade de
recuperação; `collection_status` descreve o resultado da coleta. Nenhum status
auxiliar, sozinho, prova disponibilidade global. Uma falha de RAG não torna a
API FastAPI automaticamente indisponível, e uma resposta degradada ou falha
controlada não prova que todos os subsistemas estejam disponíveis.

### Política do frontend e mensagens públicas

| Classe | Renderiza `resultado.resposta` | Estado de erro/limitação | Mock | Detalhe técnico |
|---|---:|---|---:|---:|
| sucesso funcional | sim | não | nunca | não |
| sucesso degradado utilizável | sim | condição pública neutra quando necessária; nunca “saúde total” | nunca | não |
| falha controlada | sim, pois é a mensagem segura prevista | falha recuperável, distinta de sucesso comum | nunca | não |
| `4xx` | não como resposta normal do bot | falha da request | nunca | não |
| transporte | não | serviço não alcançado | nunca | não |
| `5xx`/falha técnica | não | falha recuperável | nunca | não |

Quando o backend entrega uma resposta funcional do contrato, inclusive uma
falha controlada, `resultado.resposta` é o único texto público a renderizar. O
frontend não concatena `failed_stage`, não deriva texto de status interno e não
exibe `detail`, objeto HTTP ou JSON bruto. Classes mínimas de mensagem local,
com copy provisória, são:

- transporte: “Não foi possível conectar ao serviço.”;
- `4xx`: “Não foi possível enviar a solicitação.”;
- `5xx`, contrato inválido ou falha inesperada: “Não foi possível concluir a
  solicitação.”;
- falha controlada: usar `resultado.resposta`;
- timeout: reservado integralmente a `INT-P1-005`.

Essas falhas devem encerrar o estado de carregamento e permitir tentativa
posterior. Retry automático, toast, modal e desenho visual não são definidos
aqui. P3/P4 devem implementar e testar o comportamento; uma falha real nunca
pode acionar mock como fallback de sucesso.

### Diagnóstico, logs e segurança

Informação técnica necessária ao diagnóstico pertence ao backend/log/trace. A
resposta pública pode conter a resposta do chatbot, a mensagem segura da falha
controlada ou a mensagem genérica do frontend. Conforme a política existente,
logs internos podem registrar tipo da exceção, estágio, contexto técnico mínimo
e traceback no ambiente adequado, sujeitos à sanitização e ao controle de
acesso.

Nunca devem chegar ao usuário: stack trace/traceback, `repr` ou mensagem bruta
de exceção, path local, diretório do projeto, hostname interno, variável de
ambiente, segredo/token/chave, query SQL, configuração de Ollama, detalhe de
Qdrant/embedding, estrutura Python, IDs internos desnecessários ou objeto HTTP
bruto. O array `detail` de validação é implementação do framework; P3/P4
precisam conhecer apenas a classe “request rejeitada pelo contrato”.

```text
diagnóstico técnico → logs/trace
mensagem pública segura → API/frontend
```

### Decisões adiadas

- `INT-P1-005`: tempo, margem e política/mensagem específica de timeout;
- P2: testes HTTP, eventual handler seguro e decisão separada sobre healthcheck;
- P3: DTOs, classificação no cliente, loading, estado recuperável, remoção do
  mock dos caminhos reais e apresentação mínima;
- P4: cobertura automatizada de sucesso, degradação, falha controlada, `4xx`,
  transporte e `5xx`.

Esta decisão não cria healthcheck, logging, handler, retry, UI, schema ou código
funcional e não redefine a estratégia de sessão de `INT-P1-003`.

## Política de timeout

### Diagnóstico e limites observados

O `ChatService` aplica `timeout(60000)`, isto é, `60 s`, à chamada HTTP do
Angular. No backend, `OLLAMA_TIMEOUT_SECONDS` vale `60 s` por padrão, é
configurável por ambiente e limita separadamente cada geração e cada request
de embedding. O cliente Qdrant usa `10 s` fixos por request. O endpoint FastAPI
e o orquestrador não possuem deadline total explícito.

| Camada | Timeout atual | Papel | Política aprovada | Implementação futura |
|---|---:|---|---|---|
| Ollama: geração/embedding | `60 s` por request | limita uma operação da dependência | manter `60 s`; nunca tratar como máximo total da request | P2/backend, sem ajuste inicial |
| Qdrant | `10 s` por request | limita cada operação vetorial | manter como limite interno; centralizar se for alterado | P2/backend, se necessário |
| FastAPI/request | inexistente | fronteira e pipeline completos | orçamento total de `120 s`, incluindo tratamento e resposta segura | P2/backend |
| Angular HTTP | `60 s` | limite percebido pelo usuário | `135 s` | P3 |
| proxy/infra futuros | n/a | transporte | não encerrar antes do limite aplicável da aplicação | P5/infra |

Não há retry automático geral no fluxo. Há, porém, fallback sequencial
no embedding: se `/api/embed` produz `EmbeddingError`, o serviço tenta
`/api/embeddings`, e cada tentativa pode consumir até `60 s`. Quando RAG é
necessário, o fluxo gera um embedding da consulta, consulta/prepara o Qdrant e
percorre os chunks textuais ainda sincronizados; para cada chunk, gera um novo
embedding e faz um upsert. O número de chunks controla quantas operações
sequenciais ocorrem. Nos caminhos sem resolução local, Agentes 1 e 3 também
podem chamar o Ollama sequencialmente; o Agente 4 pode acrescentar outra chamada
quando `AGENT4_USE_OLLAMA` estiver habilitado.

Logo, o timeout de `60 s` de uma operação **não** representa o máximo total da
request. O pipeline e a leitura SQLite local não possuem hoje deadline de
aplicação explícito. A igualdade atual entre cliente e uma operação Ollama
não oferece margem, e chamadas sequenciais tornam a divergência mais grave.

### Política aprovada e margem

A implementação deve obedecer a esta ordem:

```text
timeout de cada operação interna (atualmente 60 s Ollama / 10 s Qdrant)
    < orçamento total do backend (120 s)
    < timeout da request no frontend (135 s)
```

O orçamento de `120 s` limita a request inteira, inclusive chamadas
sequenciais e laços, em vez de somar cegamente todos os limites potenciais. Ele
preserva o limite interno atual de `60 s`, admite duas janelas desse porte no
pior caminho útil e impede que a quantidade de chunks torne a espera ilimitada.
O backend deve reservar tempo dentro desse orçamento para interromper ou
classificar a operação e emitir uma resposta segura quando tecnicamente
possível; ele não deve iniciar uma nova operação cujo limite ultrapasse o tempo
restante.

O cliente usa `135 s`: a margem de `15 s` cobre transporte, roteamento,
serialização, processamento Python anterior/posterior à dependência e o
encerramento controlado. Essa margem é deliberadamente limitada, mas suficiente
para não disputar o mesmo instante do deadline backend. Timeout infinito é
proibido em qualquer operação externa relevante.

Se um limite interno, a quantidade de tentativas ou o orçamento backend mudar,
o timeout cliente deve ser revisto para preservar a ordem e uma margem
operacional adequada. Proxy, reverse proxy, gateway ou load balancer futuros
também não podem encerrar a conexão antes da política da aplicação; nenhuma
topologia, origem, porta, CORS ou configuração concreta é decidida aqui.

### Classificação e experiência pública

- Se o backend captura o timeout de uma dependência e consegue devolver o
  envelope seguro, ele pode ser falha controlada conforme `INT-P1-004`, com
  `failed_stage` real e `resultado.resposta` segura.
- Se o timeout escapa do fluxo controlado ou o servidor falha ao cumprir seu
  orçamento, trata-se de falha técnica/`5xx`, também conforme `INT-P1-004`.
- Se o Angular esgota `135 s` sem resposta, trata-se de timeout específico do
  cliente, sem resposta funcional e sem inventar `failed_stage`.
- Timeout não é erro genérico e nunca pode acionar `responderMock()`.

A mensagem local aprovada para timeout do cliente é: **“A solicitação demorou
mais que o esperado. Tente novamente.”** Ela não expõe dependência, duração
interna, stack ou conclusão definitiva. Após qualquer timeout, a UI deve sair de
loading e permitir nova tentativa.

### Sessão, nova tentativa e limitações

Timeout não invalida `session_id`, não cria sessão, não limpa contexto e não
altera a política de `INT-P1-003`. Sem cancelamento distribuído, o backend pode
continuar executando depois que o cliente desistiu. Uma tentativa posterior é
uma nova request e pode encontrar estado produzido pela anterior. Esse risco é
registrado, sem decidir idempotência, `AbortController`, token/endpoint de
cancelamento, fila, task ID, WebSocket ou SSE.

Os valores futuros devem ter fonte única e clara: timeout por dependência e
orçamento total na configuração/env existente do backend; timeout cliente em
constante ou configuração central do service Angular. Eles não devem ser
duplicados em componentes nem justificar um gerenciador de timeouts. A mesma
semântica vale em desenvolvimento e produção salvo necessidade comprovada.

### Cenários normativos

1. **Resposta normal:** backend conclui antes de `120 s`; Angular recebe a
   resposta antes de `135 s` e segue o contrato normal.
2. **Timeout interno capturado:** dependência excede seu limite; backend captura
   e, havendo tempo no orçamento total, devolve resposta segura conforme
   `INT-P1-004`.
3. **Timeout do frontend:** `135 s` expiram; Angular encerra a espera, exibe a
   mensagem específica, encerra loading e permite nova tentativa.
4. **Backend continua:** o cliente expirou, mas o servidor pode continuar; a
   sessão é preservada e não se presume cancelamento.

Esta seção é exclusivamente normativa. P2 deve implementar e testar o
orçamento backend e sua classificação; P3 deve centralizar `135 s`, distinguir
timeout e remover mock dos caminhos reais; P4/P5 devem cobrir cenários e
verificar limites de transporte/infraestrutura. Nenhum timeout, retry, contrato,
sessão, proxy ou código funcional foi alterado em `INT-P1-005`.

## Topologia de rede e origens

### Diagnóstico observado

O frontend e o backend continuam aplicações irmãs. O `ChatService` usa hoje a
URL relativa `/api/chat`; ela diverge do path público congelado em P1-002, mas
não contém host ou porta. Não há `proxy.conf.*`, `proxyConfig`, script npm com
proxy nem environment/configuração de base da API versionados. `npm start`
executa `ng serve`, documentado em `http://localhost:4200`.

O backend documenta `uvicorn api:app --reload`, cujo endereço local padrão é
`http://localhost:8000`, e oferece `POST /api/processos/chat`. `api.py` não
configura `CORSMiddleware`, allowlist ou origem, não serve o build Angular e não
monta arquivos estáticos. Também não há reverse proxy ou infraestrutura de
produção definida no repositório.

```text
ORIGEM_PRODUCAO: NÃO DEFINIDA
```

Este diagnóstico não corrige a divergência de path nem implementa rede.

### Desenvolvimento aprovado

```text
Browser http://localhost:4200
    ↓ /api/* (mesma origem observada pelo browser)
Angular dev server localhost:4200
    ↓ proxy de desenvolvimento
FastAPI http://localhost:8000
```

O código Angular deve usar a base lógica relativa `/api`; para o chat, a URL
contratual é `/api/processos/chat`. O proxy local deve encaminhar `/api/*` para
`http://localhost:8000`, preservando método, path, body JSON, response e status
HTTP. Sua configuração real pertence a `INT-P5-001`; o workflow conjunto em
dois terminais pertence a `INT-P5-004`.

Com esse proxy, o browser chama a origem Angular e não realiza diretamente uma
request cross-origin ao FastAPI. Portanto, CORS não é necessário em
desenvolvimento apenas para a integração Angular–FastAPI. A diferença entre as
tecnologias não justifica middleware de CORS.

Fluxo operacional adotado:

```text
Terminal A: FastAPI em localhost:8000
Terminal B: Angular em localhost:4200
Browser: http://localhost:4200
Angular: /api/processos/chat
Proxy Angular: /api/* → http://localhost:8000
```

## Desenvolvimento local integrado

Este fluxo é a rotina diária depois dos bootstraps descritos em
`chatbot_processual_ai/README.md` e `frontend/README.md`. Ele pressupõe que o
`.venv`, o `.env` local e `node_modules/` já estejam preparados; não recrie nem
reinstale esses ambientes a cada início.

1. Inicie somente as dependências externas exigidas pelo cenário. O healthcheck
   e as consultas processuais estruturadas usam apenas o SQLite local; Ollama é
   condicional para geração e Qdrant com Ollama é necessário para a capacidade
   RAG completa.
2. No primeiro terminal, entre em `chatbot_processual_ai`, ative o venv
   (`.\.venv\Scripts\Activate.ps1` no PowerShell ou
   `source .venv/bin/activate` em POSIX) e execute
   `python -m uvicorn api:app --reload`.
3. Confirme `http://localhost:8000/api/health`: deve responder HTTP 200 com
   `{"status":"ok"}`.
4. No segundo terminal, entre em `frontend` e execute `npm start`.
5. Confirme `http://localhost:4200/api/health`: deve responder HTTP 200 com o
   mesmo payload, comprovando o caminho Angular dev server → proxy → FastAPI.
6. Abra `http://localhost:4200` e use o chatbot. O frontend mantém URLs
   relativas `/api/...`; não edite a URL da API e não habilite CORS para esta
   topologia local.
7. Para encerrar, use `Ctrl+C` em cada terminal.

Se a porta 8000 não responder, verifique o backend. Se o health direto funcionar
e o health pela porta 4200 falhar, verifique o dev server e o proxy Angular. A
indisponibilidade de Ollama ou Qdrant afeta somente as capacidades condicionais
descritas no bootstrap do backend.

### Produção preferencial

A preferência arquitetural é uma única origem pública servindo o frontend em
`/` e encaminhando `/api/*` ao FastAPI por reverse proxy, gateway ou
infraestrutura equivalente:

```text
Browser → origem pública única
              ├── /       → frontend
              └── /api/*  → FastAPI
```

O Angular mantém `/api/...`, fica desacoplado do host backend e não exige CORS
nesse arranjo. Domínio, hosting e tecnologia concreta não estão definidos; não
se escolhe Nginx, Apache, Traefik, Cloudflare, Kubernetes ou provedor nesta
fase. Mesma origem tampouco obriga o FastAPI a servir o `dist` Angular ou
autoriza fundir `frontend/` e `chatbot_processual_ai/`.

### Produção com origens distintas

Origens distintas são alternativa suportada somente quando a infraestrutura
real exigir. Nesse caso, a base pública da API deve vir de configuração de
ambiente/rede, sem alteração de componentes, e a chamada será cross-origin.
`INT-P2-005` deverá então implementar e testar CORS com allowlist explícita de
origens permitidas e rejeitadas.

| Ambiente | Origem browser | URL usada pelo Angular | Resolução | CORS |
|---|---|---|---|---|
| desenvolvimento | `http://localhost:4200` | `/api/...` | proxy Angular → FastAPI `:8000` | não necessário pela integração |
| produção mesma origem | origem pública única | `/api/...` | reverse proxy/gateway | não necessário |
| produção origens distintas | frontend e API diferentes | base configurada | chamada cross-origin | allowlist explícita necessária |

### Política CORS

CORS é consequência da política de origem, não autenticação ou autorização. Ele
controla chamadas feitas pelo navegador e não muda a decisão de P1-003 de que
`session_id` não é credencial.

Se a produção exigir origens distintas, as origens devem vir de configuração,
com métodos e headers mínimos. Credenciais só podem ser habilitadas mediante
necessidade real e análise específica. `allow_origins=["*"]` não é solução
padrão para “fazer funcionar” e não deve ser combinado por conveniência com
credenciais. No estado atual, desenvolvimento e produção preferencial usam a
estratégia de mesma origem e não existe origem cross-origin concreta aprovada.
`INT-P2-005` decide, portanto, não implementar CORS enquanto essa topologia
permanecer. Se um deployment futuro separar frontend e API, a necessidade deverá
ser reaberta antes dele e implementada com allowlist configurável, métodos e
headers mínimos e sem credenciais salvo requisito separado. O proxy local
continua pertencendo a `INT-P5-001`.

### URL pública, contratos e segurança

Nenhum componente deve conter `localhost`, IP, domínio ou porta da API. A
estratégia lógica única é `/api`; uma eventual origem distinta será resolvida
por configuração mínima, sem abstrações antecipadas como resolvedores ou
gerenciadores de topologia. URL pública não é segredo, mas frontend nunca deve
receber secrets, chaves privadas, senhas, tokens backend, credenciais de
Ollama/Qdrant ou paths internos.

A rede não altera `POST /api/processos/chat`, payload ou response de P1-002. O
proxy transporta `session_id` no JSON de P1-003, sem cookie, header customizado
ou sticky session. Ele preserva `4xx`/`5xx` e não converte falha em sucesso;
erro de CORS é transporte/acesso, não `failed_stage`. Proxy/gateway futuro não
deve expirar antes da política temporal de P1-005; nenhum novo valor é escolhido
sem infraestrutura real.

Healthcheck permanece reservado a `INT-P2-003`; se futuramente existir sob
`/api`, seguirá a mesma resolução. Esta decisão não cria proxy, CORS,
healthcheck, configuração, deploy ou código funcional.

## Princípio de integração conservadora

Esta integração existe para conectar duas aplicações existentes através de uma
fronteira HTTP estável. Ela não constitui autorização para refatoração ampla,
redesign, modernização, expansão de produto ou conclusão de funcionalidades
independentes.

Devem ser preservados ao máximo o comportamento, o layout, as funcionalidades e
a arquitetura existentes. Uma alteração só entra no escopo quando pelo menos
uma das respostas abaixo for positiva:

1. É necessária para Angular e FastAPI funcionarem corretamente?
2. É necessária para evitar erro, regressão, risco de segurança ou comportamento
   incorreto diretamente causado pela integração?
3. É necessária para testar ou documentar de forma confiável a própria
   integração?

Se a resposta for não para todas as perguntas, a alteração está **fora do
escopo**.

## Escopo e não objetivos

As restrições abaixo admitem somente a exceção por dependência comprovada
definida neste documento.

### Frontend

Não fazem parte desta integração:

- alterar layout, redesenhar componentes ou modificar a identidade visual;
- reorganizar CSS por estética, criar animações ou corrigir warnings puramente
  estéticos, como o budget CSS, apenas porque foram encontrados;
- adicionar loading sofisticado apenas por UX, toast, modal ou feedback visual
  que não seja necessário à integração;
- mudar a navegação existente, criar telas ou adicionar funcionalidades;
- completar features ou TODOs preexistentes sem relação direta com a
  integração;
- remodelar o histórico apenas por preferência;
- renomear em massa componentes, arquivos ou o projeto Angular;
- reorganizar services ou components apenas por preferência arquitetural;
- trocar bibliotecas ou frameworks, ou atualizar o Angular sem necessidade
  comprovada.

### Backend

Não fazem parte desta integração:

- refatorar agentes do chatbot ou modificar seu comportamento interno apenas
  por qualidade percebida, sem necessidade da fronteira HTTP;
- reorganizar orquestradores, mudar regras de negócio ou alterar a lógica
  processual existente sem necessidade da integração;
- trocar ou migrar SQLite, Qdrant ou Ollama;
- mudar o modelo de IA apenas para facilitar o frontend;
- reestruturar o RAG ou otimizar um pipeline que já satisfaz o contrato;
- alterar semanticamente respostas sem necessidade do contrato;
- introduzir nova persistência apenas por robustez futura.

### Simulador de metas

Não fazem parte desta integração:

- implementar novas regras do simulador;
- concluir funcionalidades parcialmente desenvolvidas;
- alterar modelos ARIMA ou revisar previsões por oportunidade;
- mudar a lógica de metas sem requisito específico;
- refatorar o simulador como efeito colateral da integração do chat.

O diretório `simulador-de-metas/` só deve ser alterado diante de uma dependência
concreta e demonstrável da integração.

### Infraestrutura e produto

Não devem ser introduzidos automaticamente nesta integração:

- autenticação, autorização ou sistema de usuários;
- deploy ou um novo CI/CD;
- containerização apenas por conveniência;
- infraestrutura ou persistência distribuída de sessão;
- Redis apenas por robustez futura ou qualquer novo banco;
- cloud;
- observabilidade ampla, telemetria, analytics ou monitoramento externo;
- redesign da arquitetura de produção.

Esses assuntos podem ser avaliados futuramente, mediante decisão específica,
mas não pertencem automaticamente à integração atual.

## Dívida técnica encontrada

> Descobrir um problema não constitui autorização para corrigi-lo.

Warnings, TODOs, código antigo, nomes ruins, testes preexistentes quebrados,
dependências desatualizadas, vulnerabilidades npm, refatorações desejáveis e
features parcialmente prontas devem seguir este fluxo:

1. registrar o achado quando relevante;
2. classificar seu impacto sobre a integração;
3. corrigir somente se necessário para concluir a integração com segurança;
4. caso contrário, preservar o comportamento e manter o achado fora do escopo.

Dívida preexistente não deve ser classificada como regressão causada pela
integração.

## Exceção por dependência comprovada

O escopo negativo não impede uma alteração indispensável ao funcionamento da
fronteira HTTP, à segurança da integração, ao isolamento correto de sessão, à
compatibilidade Angular/FastAPI, ao tratamento correto de request e response, à
prevenção de regressão introduzida pela integração, aos testes da integração ou
à sua execução reproduzível.

Toda exceção deve:

1. registrar o motivo;
2. apontar a dependência concreta;
3. aplicar a menor alteração coerente;
4. não expandir o escopo além da necessidade comprovada.

## Exemplos normativos

- O frontend ignora `resultado.resposta` e sempre mostra um mock: deve ser
  alterado, pois impede o uso real do backend.
- Clientes web sem `session_id` compartilham a sessão `default`: pode exigir
  alteração, pois afeta diretamente a correção da integração multiusuário.
- O CSS possui warning de budget: registrar se relevante; não corrigir apenas
  por oportunidade.
- Uma feature frontend está 80% pronta: não completar somente porque o arquivo
  será tocado.
- Um agente Python poderia ser arquiteturalmente mais elegante: não refatorar
  se a API já funciona corretamente.
