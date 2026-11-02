# Filosofia de design

## Determinismo antes de LLM

Número processual, roteamento, consulta estruturada, validações e regras
verificáveis devem ser resolvidos por código e dados. A LLM entra onde há ganho
linguístico real, reduzindo variabilidade e mantendo caminhos úteis sem modelo.

## A LLM explica; não inventa regra

O modelo pode interpretar e redigir a partir de fatos validados. Ele não define
fórmulas de metas, estados processuais ou fatos ausentes. Enquanto critérios do
simulador não forem homologados, a resposta deve preservar seu caráter
provisório ou inconclusivo.

## O frontend apresenta o estado real

A interface usa `resultado.resposta`, `processo_ativo`, health e estados de erro
reais. Pergunta do usuário não vira número de histórico; indisponibilidade não
vira resposta mock; health da API não vira promessa de sistema inteiro saudável.

## Falha explícita é melhor que fallback silencioso

Degradação preserva o caminho seguro restante e informa a limitação por estados
como `rag_status` ou `failed_stage`. Fallback não pode transformar erro em
sucesso aparente nem ausência de evidência em afirmação.

## Contratos claros reduzem acoplamento

Angular depende apenas da API HTTP/JSON; FastAPI adapta o contrato público aos
orquestradores; schemas delimitam os dados internos. Mudança de contrato exige
revisão dos consumidores, sem acesso direto do frontend a agentes, banco ou RAG.

## Mudanças pequenas, reversíveis e testáveis

Prefere-se alteração focada, adaptadores nas integrações e testes proporcionais
ao risco. Dados sintéticos e fixtures sanitizadas permitem validar regras sem
alterar baselines ou depender de dados reais.

## Detalhes internos e sensíveis não chegam à UI

Stack traces, paths, objetos HTTP crus, credenciais e identificadores internos
não fazem parte da resposta pública. Dados pessoais só devem alcançar modelos e
interface quando necessários e governados; sanitização é defesa em profundidade,
não autorização de uso.

## Estado e limitações são nomeados

Sessão em memória, dependências condicionais, regras provisórias e decisões de
produção ainda abertas devem ser documentadas como tais. Planejamento não pode
ser descrito como implementação — exemplo atual: 135 s existe no cliente, mas o
deadline total backend de 120 s permanece não implementado.
