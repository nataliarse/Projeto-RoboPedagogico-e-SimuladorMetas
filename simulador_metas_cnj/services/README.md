# Serviços de domínio do simulador

Este diretório é o destino das extensões selecionadas da Equipe B dentro do backend canônico `simulador_metas_cnj/`.

- `meta1_effort.py`: cálculo de esforço mensal usando exclusivamente a regra e a base canônicas. Enquanto o GATE-M1 estiver bloqueado, não haverá rota pública habilitada.
- `meta2_groups.py`: suporte A/ANT isolado da Meta 2 agregada existente. Expõe separadamente a metodologia do Glossário CNJ 2026 v3 e a reprodução histórica não homologada da equipe; datasets declaram proveniência e semântica temporal (`carga_consolidada`, `fluxo_mensal` ou `indefinida`).

Os módulos de domínio não devem importar FastAPI/Pydantic, acessar rede, modificar `BASE_GLOBAL` nem depender do chatbot. `main.py` continua responsável por DTOs e HTTP; os ambientes Python de chatbot e simulador permanecem separados.
