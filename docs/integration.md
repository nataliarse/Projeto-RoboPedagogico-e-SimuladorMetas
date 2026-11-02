# Integração Angular–FastAPI

Este documento é a fonte detalhada do contrato público e da fronteira web do
Chatbot Processual. A implementação atual é síncrona, via HTTP/JSON, sem
streaming, SSE ou WebSocket.

## Topologia

```text
Browser → Angular → /api/* → FastAPI → orquestradores/serviços/dados
```

Angular e FastAPI são aplicações irmãs. O frontend conhece apenas os contratos
públicos; detalhes de agentes, SQLite, RAG, Ollama e Qdrant ficam encapsulados.

## Chat processual

`POST /api/processos/chat`

Request conceitual:

```json
{
  "session_id": "id-opaco-opcional",
  "mensagem": "Consulte o processo de exemplo"
}
```

`session_id` pode ser omitido ou `null`. String vazia ou somente whitespace
também é tratada como ausência. Nesses casos, o backend gera um UUID. `mensagem`
é obrigatória e precisa conter texto; payload inválido é rejeitado pela
validação FastAPI/Pydantic, normalmente com HTTP 422.

Response 2xx:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "resultado": {
    "tipo": "processual_chat",
    "intent": "process_question",
    "resposta": "Resposta pública sintética.",
    "processo_ativo": "0000000-00.0000.0.00.0000",
    "collection_status": "success",
    "failed_stage": null,
    "rag_status": "not_needed",
    "fontes": []
  }
}
```

`resultado.resposta` é a mensagem pública exibida pela UI.
`resultado.processo_ativo`, e não a pergunta livre, alimenta o histórico.
Os objetos internos de `fontes` não têm schema público estável e não devem
virar acoplamento do frontend.

## Sessão e histórico

1. O Angular lê o ID de `sessionStorage` e o omite quando ausente.
2. O FastAPI normaliza o valor; se não for utilizável, gera UUID.
3. `_SESSIONS` seleciona ou cria um contexto com conversa, processo ativo e
   última intenção.
4. O backend devolve o ID efetivo e o Angular o persiste.
5. Chamadas seguintes da aba reutilizam o ID.

Refresh normalmente mantém o `sessionStorage`. Uma nova aba normalmente começa
sem o ID, mas browsers podem copiar o estado inicial de uma aba com `opener`.
Reiniciar o backend esvazia `_SESSIONS`; reenviar um ID então cria contexto
novo. O ID é opaco e não é autenticação, autorização nem identidade pessoal.

O histórico usa `localStorage`, deduplica por número de processo mantendo o
mais recente e limita a lista a três. Ele é uma conveniência visual, não restaura
o contexto conversacional do backend.

## Resposta, degradação e erro

- **Sucesso:** HTTP 2xx, sem `failed_stage`, com resultado normal.
- **Resposta degradada:** HTTP 2xx e `rag_status` como `unavailable`, `error` ou
  outro estado limitante; dados estruturados ainda podem sustentar a resposta.
- **Falha controlada:** o orquestrador captura uma exceção, devolve mensagem
  segura em `resultado.resposta` e identifica a etapa em `failed_stage`.
- **Falha HTTP/transporte:** validação 4xx, rota/framework, 5xx não capturado,
  indisponibilidade, conexão ou timeout; chega ao Angular como erro técnico.

Resposta degradada ou controlada não vira automaticamente `HttpErrorResponse`.
O frontend não cria mock, não expõe stack/path/objeto HTTP cru, não executa retry
automático e encerra o loading. O timeout do cliente é 135 s. O deadline total
backend planejado de 120 s ainda não existe na implementação atual.

## Health e rede

`GET /api/health` responde `{"status":"ok"}` e prova somente a acessibilidade
da fronteira FastAPI. Não consulta banco, agentes, Ollama, Qdrant ou RAG.

No desenvolvimento:

```text
Browser → http://localhost:4200/api/*
Angular dev proxy → http://localhost:8000/api/*
```

O frontend usa URLs relativas. CORS não é necessário nessa topologia. Produção
deve preferir mesma origem via reverse proxy/gateway; a infraestrutura ainda
não está definida. Se origens distintas forem inevitáveis, CORS deverá ser
implementado com allowlist explícita e configurável, nunca `*` por conveniência.

## Dependências por cenário

| Cenário | Ollama | Qdrant | Resultado |
|---|---|---|---|
| Health | não usado | não usado | apenas FastAPI |
| Consulta estruturada | não usado no caminho determinístico | não usado | SQLite local |
| RAG/documentos | necessário para embeddings/geração aplicável | necessário para índice vetorial | capacidade semântica completa |
| RAG indisponível | pode degradar | pode degradar | status explícito; fatos estruturados preservados quando existentes |
| Metas/impacto atual | não usado | não usado | contratos e regras provisórias |

## Outros endpoints e fronteiras

`POST /api/metas/simular` e `POST /api/metas/impacto-processo` pertencem ao
domínio provisório de metas. Eles não transformam `simulador-de-metas/` em parte
interna do frontend do Chatbot Processual nem comprovam fórmulas oficiais.
