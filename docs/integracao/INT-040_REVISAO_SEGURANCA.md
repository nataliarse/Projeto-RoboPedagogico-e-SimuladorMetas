# Revisão pré-publicação de segurança e privacidade

| Área | Risco | Classe | Tratamento |
|---|---|---|---|
| Sessões | crescimento ilimitado em memória | Alto | limite de 1.000, remoção da mais antiga |
| Entrada do chat | payload/ID excessivos | Médio | mensagem 4.000 e ID 128 caracteres; 422 |
| CORS simulador | métodos/headers curingas e credenciais | Alto | origens locais configuráveis, GET/POST, Content-Type, sem credenciais |
| Proxy | exposição acidental fora do host | Médio | defaults em `127.0.0.1`; publicação exige reverse proxy revisado |
| Dados processuais | resposta pode conter informação sensível | Alto | interpolação segura; resposta não vai ao storage/log; acesso/autorização ainda exigidos em produção |
| Logs | vazamento de payload/exceção | Médio | frontend não loga payload; coletor registra apenas estágio e classe |
| Planilhas | dados agregados versionados | Baixo | somente fixtures permitidas; hashes e snapshots cobertos |

## Pendências obrigatórias antes de produção

1. Autenticação/autorização institucional e política de perfis não fazem parte deste MVP.
2. Sessões em memória não são adequadas a múltiplas réplicas; usar armazenamento com TTL.
3. Definir retenção e base legal para histórico/processos reais.
4. Terminar homologação das regras CNJ e teste de segurança do reverse proxy.
5. Configurar origens CORS exatas do ambiente; nunca usar `*` com credenciais.

Essas pendências não impedem desenvolvimento ou demonstração offline, mas impedem tratar
a integração como pronta para produção.
