# Backend do Simulador de Metas CNJ

Este é o destino operacional do backend de simulação na arquitetura aprovada pelo ADR-001.

## Proveniência

Os arquivos foram copiados de `integracao_entrada/TCC-Simulador-CNJ/backend/` no `INT-007`. O snapshot de origem permanece preservado para comparação. Na cópia inicial:

- `main.py`, `robo_cnj_meta2.py` e `requirements.txt` mantiveram o mesmo SHA-256 da origem;
- as quatro planilhas em `dados/` mantiveram o mesmo SHA-256 da origem;
- nenhuma fórmula ou série de dados foi modificada;
- caches Python gerados localmente não foram transportados.

## Papel na arquitetura

- Serviço FastAPI do simulador.
- Porta local reservada: `8001`.
- Entrada atual: `main:app`.
- As rotas públicas namespaced e os aliases compatíveis serão tratados nos itens de contrato e proxy.

As planilhas em `dados/` são baseline somente leitura. Alterações de fórmulas, regras CNJ ou valores exigem tarefa e homologação próprias.
