# Filosofia de design

## Propósito

Este documento registra os princípios usados para evoluir o sistema. Eles não
substituem regras de negócio nem descrevem funcionalidades ainda inexistentes;
servem como critérios para decisões técnicas e revisão de mudanças.

## 1. Verdade estruturada antes de texto gerado

Dados processuais, cálculos e critérios de metas devem vir de fontes e regras
determinísticas. A LLM pode interpretar uma mensagem ou explicar um resultado,
mas não deve criar fatos, fórmulas, indicadores ou regras normativas.

Consequências práticas:

- consultar SQLite e contratos antes de recorrer ao modelo;
- identificar fato, inferência e limitação separadamente;
- validar toda saída estruturada produzida por modelo;
- responder que não há informação suficiente quando a evidência não existe.

## 2. Determinismo primeiro, IA quando agrega valor

O sistema prioriza regras locais para intenção, roteamento, leitura de campos e
respostas previsíveis. Ollama é usado em ambiguidades e tarefas linguísticas nas
quais oferece ganho real. Essa escolha reduz latência, consumo de recursos e
variabilidade, além de manter parte do sistema útil sem o modelo.

## 3. Degradação explícita e segura

Dependências opcionais podem falhar. Qdrant, embeddings ou geração local não
devem ocultar dados estruturados que continuam disponíveis. A degradação deve:

- preservar o caminho seguro restante;
- registrar um status observável;
- informar a limitação sem expor detalhes internos;
- nunca converter ausência de evidência em resposta afirmativa.

Os estados de RAG e o campo `failed_stage` materializam esse princípio.

## 4. Contratos nas fronteiras

Entradas e saídas entre API, orquestradores, serviços e frontend devem ter
formas explícitas. Dataclasses representam os contratos internos atuais, e
modelos Pydantic validam os payloads HTTP de entrada.

Mudanças de contrato exigem revisão de todos os consumidores. Enquanto o
frontend não estiver alinhado ao endpoint e ao envelope reais, a divergência
deve permanecer documentada, e não escondida por suposição.

## 5. Separação de responsabilidades

- interfaces recebem e apresentam dados;
- orquestradores controlam sequência, progresso e falhas;
- agentes executam responsabilidades linguísticas delimitadas;
- repositórios cuidam de persistência;
- serviços executam recuperação, normalização e regras;
- schemas definem contratos;
- prompts orientam modelos, mas não concentram regra de negócio.

Uma camada não deve acessar detalhes internos de outra quando um contrato mais
estável estiver disponível.

## 6. Privacidade por minimização

Somente os dados necessários devem chegar ao modelo ou à interface. CPF, CNPJ,
identificadores internos e detalhes técnicos devem ser removidos quando não são
essenciais para a resposta. Dados reais e credenciais permanecem fora do Git.

Sanitização é defesa em profundidade, não autorização para usar dados sensíveis
sem governança, base legal e controles operacionais adequados.

## 7. Estado local assumido, não disfarçado

O estado atual é em memória e adequado à execução local. Ele não oferece
durabilidade, compartilhamento entre workers, expiração ou escalabilidade
horizontal. Qualquer evolução para produção deve tornar essas propriedades
explícitas e escolher uma estratégia de sessão antes de escalar a API.

## 8. Resultados provisórios devem parecer provisórios

O domínio de metas ainda aguarda critérios oficiais. Nomes de status, motivos e
observações devem impedir que uma heurística seja interpretada como cálculo
homologado. `not_integrated`, `inconclusivo` e as advertências atuais são parte
do contrato de segurança semântica.

## 9. Observabilidade sem vazamento

Eventos de progresso devem ajudar a localizar etapas e tempos sem registrar
conteúdo sensível. O modo normal comunica apenas o necessário; o modo de trace
oferece diagnóstico controlado. Exceções técnicas não devem ser devolvidas
diretamente ao usuário.

## 10. Evolução incremental e testável

Mudanças devem ser pequenas, coerentes com os padrões existentes e cobertas de
forma proporcional ao risco. Prefere-se:

- funções puras para classificação e regras;
- adaptadores nas integrações externas;
- fallbacks testáveis;
- dados sintéticos e fixtures sanitizadas;
- integração gradual em vez de substituição ampla.

## 11. Fonte única para cada responsabilidade

- `README.md`: visão geral, instalação e primeiros comandos;
- `docs/ARCHITECTURE.md`: componentes, limites e estado técnico;
- este documento: princípios de decisão;
- `docs/development.md`: rotina de contribuição e validação;
- `docs/orchestration.md`: sequência dos fluxos;
- checklist de integração: trabalho rastreável, sem ser redefinido por estes
  documentos.

## Critérios para novas decisões

Antes de introduzir uma solução, verifique:

1. qual problema e contrato ela resolve;
2. qual fonte de verdade será usada;
3. como ela falha e qual caminho permanece disponível;
4. quais dados ela recebe e expõe;
5. como será testada sem depender de dados reais;
6. se a mudança representa implementação atual ou apenas intenção futura.
