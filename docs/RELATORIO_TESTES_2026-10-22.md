# Relatório de execução de testes

Data: 22/10/2026  
Ambiente: Windows, Python 3.12.10, pytest 9.1.1, Node.js 24.22.0 e npm 11.19.1.

## Resumo executivo

Todas as suítes oficiais executadas foram aprovadas. Ao todo, passaram 232 testes e 2 subtestes: 191 testes Python, 2 subtestes Python e 41 testes do frontend. O build de produção do Angular também foi concluído com sucesso.

Nenhuma coleta PJe, chamada institucional, acesso a produção ou alteração de baseline foi realizada. As suítes foram executadas localmente com dados sintéticos/sanitizados e dependências isoladas.

| Componente | Comando | Resultado | Duração reportada |
|---|---|---:|---:|
| Chatbot processual | `python -m pytest tests -q -p no:cacheprovider` em `chatbot_processual_ai/` | 157 aprovados e 2 subtestes aprovados | 4,85 s |
| Coletor TRT18 | `python -m pytest tests -q -p no:cacheprovider` em `entrada-de-dados/` | 26 aprovados | 0,62 s |
| Simulador de metas | `python -m unittest discover -s tests -v` em `simulador_metas_cnj/` | 8 aprovados | 0,113 s |
| Frontend Angular | `npm test -- --watch=false` em `frontend/` | 9 arquivos e 38 testes aprovados | 11,38 s |
| Roteamento do proxy | `npm run test:proxy` em `frontend/` | 3 aprovados | 197 ms |
| Build Angular | `npm run build` em `frontend/` | aprovado | 8,623 s |

## Evidências por suíte

### Chatbot processual

```text
...................................................................... [ 44%]
........................................................................ [ 90%]
...............                                                          [100%]
157 passed, 2 subtests passed in 4.85s
```

### Coletor TRT18

```text
..........................                                               [100%]
26 passed in 0.62s
```

### Simulador de metas

Foram validados os contratos HTTP, payloads inválidos, schemas OpenAPI, representação numérica, tratamento de erro interno e snapshots numéricos.

```text
Ran 8 tests in 0.113s

OK
```

### Frontend Angular

```text
Test Files  9 passed (9)
Tests       38 passed (38)
Duration    11.38s
```

### Proxy do frontend

```text
tests 3
pass 3
fail 0
duration_ms 197.2822
```

Os casos confirmaram o encaminhamento do chat e das metas ao backend processual, o encaminhamento das rotas do simulador à porta 8001 e a ausência de colisão entre healthchecks.

### Build de produção

```text
Initial total: 337.53 kB
Estimated transfer size: 89.38 kB
Application bundle generation complete. [8.623 seconds]
```

O build passou, mas manteve um aviso não bloqueante: `src/app/features/chat/chat.css` possui 5,85 kB e excede em 1,85 kB o orçamento de warning de 4 kB. O arquivo permanece abaixo do limite de erro de 8 kB configurado em `angular.json`.

## Preparação e ocorrências ambientais

O checkout não continha os ambientes virtuais Python, `node_modules` ou uma instalação de Node.js disponível no `PATH`. Para executar as suítes sem instalação global:

- foi criado um ambiente virtual Python temporário no workspace, com as dependências declaradas em `chatbot_processual_ai/requirements.txt`, `chatbot_processual_ai/requirements-dev.txt` e o package local `entrada-de-dados`; esse ambiente foi removido após os testes;
- foi usada uma distribuição portátil do Node.js 24.22.0 em `.tools/`, diretório já ignorado pelo Git;
- as dependências do frontend foram instaladas com `npm ci`, respeitando `package-lock.json`.

Tentativas iniciais no ambiente global não representam falhas do código: ele não possuía `pytest`, usava Pydantic 1 enquanto o chatbot exige Pydantic 2 e impedia a criação de subprocessos com `spawn EPERM`. As suítes foram repetidas no ambiente compatível e fora dessa restrição; os resultados válidos são os aprovados acima.

## Alertas e limitações

- `npm ci` informou 4 vulnerabilidades nas dependências resolvidas: 1 de severidade baixa e 3 de severidade alta. Não foi aplicado `npm audit fix`, pois isso alteraria dependências fora do escopo desta execução. Recomenda-se investigar com `npm audit` em uma tarefa própria antes de publicação.
- O warning de orçamento de CSS não impede o build, mas merece acompanhamento se `chat.css` continuar crescendo.
- Não foram executados browser real do coletor, CAPTCHA, Ollama, Qdrant, serviços externos, deploy ou testes contra produção.

## Conclusão

O estado testado do projeto está aprovado nas suítes automatizadas locais e no build de produção do frontend. Não houve falha de teste funcional nesta execução; os únicos pontos pendentes são os alertas de dependências npm e de orçamento de CSS descritos acima.
