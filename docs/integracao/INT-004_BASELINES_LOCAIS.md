# INT-004 — Baselines locais e comandos de execução

Data da execução: 2026-10-16. Todas as verificações foram locais e offline; nenhuma dependência foi instalada.

## Ambiente observado

| Ferramenta | Resultado |
|---|---|
| Python | 3.12.10 |
| pip | 26.1.2 |
| Node.js/npm | Indisponíveis no `PATH` |
| `pytest` | Não instalado no Python global |
| `.venv` do chatbot | Ausente |
| `node_modules` | Ausente nos dois frontends |

## Chatbot processual

- Execução documentada: em `chatbot_processual_ai/`, `python -m uvicorn api:app --reload`.
- Teste oficial: em `chatbot_processual_ai/`, `python -m pytest tests -q`.
- Resultado do teste oficial: não iniciou, pois `pytest` não está instalado.
- Import de `api`: falhou porque o ambiente global possui Pydantic 1.10.26 e o backend utiliza `field_validator`, disponível no Pydantic 2 declarado em `requirements.txt`.
- Fallback diagnóstico `python -m unittest discover -s tests -v`: 34 testes executados; 27 passaram, 2 falharam e 5 deram erro. Os erros decorreram de `pytest` ausente e incompatibilidade de Pydantic; as duas falhas de RAG ocorreram porque o package `trt18_collector` não está instalado no ambiente global.
- Interpretação: baseline ambiental incompleto, sem evidência de regressão causada pela integração.

## Coletor `entrada-de-dados`

- Instalação documentada: `python -m pip install -e ".[collect]"` dentro de `entrada-de-dados/`.
- Teste oficial: `python -m pytest tests -q`.
- Resultado: não iniciou porque `pytest` não está instalado.
- Fallback `unittest`: a descoberta encontrou teste dependente de `pytest` e encerrou com erro de importação.
- Nenhuma coleta, navegador ou endpoint institucional foi acionado.

## Frontend Angular atual

- Execução documentada: em `frontend/`, `npm start`.
- Testes/build documentados: `npm test -- --watch=false` e `npm run build`.
- Resultado: não executados porque Node.js/npm e `node_modules` estão ausentes. Não foi feita instalação pela rede.
- Existem 6 arquivos `*.spec.ts` no frontend atual.

## Backend do simulador importado

- Dependências declaradas: FastAPI 0.95.2, Pydantic 1.10.26, NumPy 2.4.1, Pandas 3.0.2, OpenPyXL 3.1.5 e Uvicorn 0.21.1.
- As mesmas versões estão disponíveis no Python global.
- Execução: em `integracao_entrada/TCC-Simulador-CNJ/backend/`, `python -m uvicorn main:app --reload --port 8001`.
- Não há testes Python automatizados no snapshot.
- Parsing estático: os 2 arquivos Python foram analisados com `ast.parse` sem erro.
- Import: `main.app` carregou com o título `Simulador Metas CNJ`.
- Smoke direto e offline:
  - `health`: 86 registros;
  - `base`: 86 registros, Meta 1 final 109,86 e Meta 2 final 161,71;
  - `simular` sem alterações: mesmos 86 registros e resultados da base;
  - `comparar` sem cenários: resposta vazia consistente e baselines preservadas;
  - `otimizador` padrão: resposta estruturada com os campos esperados.

## Frontend Angular importado

- Scripts declarados: `npm start`, `npm run build` e `npm test`.
- Existem 6 arquivos `*.spec.ts`.
- Resultado: não executável no estado recebido porque falta `angular.json`; adicionalmente Node.js/npm e `node_modules` estão ausentes.

## Conclusão

O backend do simulador possui baseline offline executável neste ambiente. As demais suítes foram corretamente descobertas, mas estão limitadas por ferramentas/dependências locais ausentes. Esses limites devem ser resolvidos de forma reproduzível em `INT-009`; não justificam alterações improvisadas de código ou instalação externa nesta fase.
