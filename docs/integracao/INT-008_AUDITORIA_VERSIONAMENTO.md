# INT-008 — Auditoria de ignore e exemplos de ambiente

## Alterações

- A regra genérica `models/` foi restringida a diretórios operacionais de modelos de ML conhecidos.
- Diretórios Angular `src/app/core/models/` passam a ser reconhecidos normalmente como código-fonte.
- Foi criado `simulador_metas_cnj/.env.example` somente com host, porta, reload e diretório local de dados, sem credenciais.
- O `.env.example` existente do chatbot foi preservado como fonte canônica para Ollama, SQLite, Qdrant e collector.

## Verificações

- `git check-ignore -v` não classifica mais os três diretórios de modelos TypeScript como ignorados.
- O índice não contém `node_modules`, ambientes virtuais, builds, caches, bancos locais, logs, chaves ou arquivos `.env` reais.
- A busca textual por padrões comuns de credenciais retornou somente documentação, nomes de variáveis, dependências de lockfiles e fixtures deliberadamente sintéticas de testes.
- `.env.example` continua explicitamente permitido pela raiz; `.env` e variantes reais continuam ignorados.

## Limite

As novas variáveis do simulador documentam o contrato de configuração que será implementado no `INT-011`. Até lá, a execução direta existente ainda possui host/porta fixos no bloco `__main__`; nenhum comportamento foi alterado neste item.
