# Orquestração

## Fluxo web integrado

```text
usuário → Angular → FastAPI → orquestrador processual
                                ├─ agentes/serviços
                                ├─ SQLite
                                └─ RAG condicional (Ollama/Qdrant)
       ← resultado.resposta + metadados ←
```

1. O usuário envia texto pela interface.
2. O Angular monta a request com `mensagem` e o `session_id` existente.
3. O FastAPI valida o JSON, resolve ou cria a sessão e chama o orquestrador.
4. O orquestrador executa intenção, contexto/coleta, análise e resposta.
5. A API devolve o ID efetivo e o resultado público, incluindo processo ativo e
   estados auxiliares.
6. O Angular persiste `session_id`, exibe `resultado.resposta` e atualiza o
   histórico somente a partir de `resultado.processo_ativo`.

## Responsabilidades

- **Angular:** interação, estado visual, request/response, sessão no
  `sessionStorage`, histórico no `localStorage`, health e mensagens técnicas.
- **FastAPI:** contrato HTTP, validação, criação/seleção de sessão e delegação.
- **Orquestrador:** ordem das etapas, eventos de progresso e conversão de falha
  interna capturada em resposta pública segura.
- **Agentes e serviços:** intenção, coleta/contexto, análise, redação,
  persistência, regras e recuperação; não são acessados pelo frontend.

## Sessão e processo ativo

Sem ID utilizável, o FastAPI gera UUID e cria estado em `_SESSIONS`. O contexto
contém conversa, processo ativo e última intenção. O ID retornado é persistido
na aba. Um ID desconhecido inicia estado vazio; restart do backend perde todos
os estados. `session_id` não é autenticação.

O agente de contexto seleciona ou reaproveita o processo ativo. Esse processo é
publicado como `resultado.processo_ativo` e pode ser usado pela interface. O
histórico local é separado e não recupera conversa do backend.

## Pipeline processual

1. **Intenção:** regras determinísticas reconhecem padrões verificáveis; Ollama
   pode apoiar casos linguísticos previstos.
2. **Contexto/coleta:** resolve processo, consulta SQLite, determina a rota e
   aciona RAG somente quando a pergunta exige conteúdo semântico.
3. **Análise:** estrutura fatos, foco e limitações, privilegiando dados e regras
   verificáveis.
4. **Resposta:** produz texto público e filtra detalhes internos ou sensíveis.

## Degradação e falha

Falha de embeddings/Qdrant não apaga dados estruturados disponíveis. O estado é
exposto em `rag_status`. Se o orquestrador captura exceção em uma etapa, devolve
HTTP 2xx com resposta segura e `failed_stage`; a UI ainda apresenta
`resultado.resposta`. Falhas de transporte/HTTP são tratadas separadamente e
não geram mock nem retry automático.

## Dependências e fronteiras

Health e consultas estruturadas não exigem Qdrant. A capacidade RAG completa
exige Ollama para embeddings e Qdrant para indexação/busca. O frontend nunca
coordena essas dependências.

O chat processual é o fluxo web integrado. O simulador em
`simulador-de-metas/` permanece uma frente distinta. O orquestrador híbrido do
backend produz avaliação provisória processo × meta, sem incorporar o simulador
ao chat nem homologar regras de negócio.

## Fronteira futura de entrada de dados

`entrada-de-dados/servico.py` oferece `obter_processo(numero)` como fachada para
cache, coleta e normalização. Nenhum componente de `chatbot_processual_ai/` a
invoca atualmente; logo, ela não faz parte das etapas do orquestrador descritas
acima. Uma integração futura deve definir explicitamente timeout, execução do
navegador, autorização para CAPTCHA, tratamento dos cinco estados da coleta,
retenção de dados pessoais e conversão do contrato `Processo` para a fonte
estruturada usada pelo chatbot. Veja [data-ingestion.md](data-ingestion.md).
