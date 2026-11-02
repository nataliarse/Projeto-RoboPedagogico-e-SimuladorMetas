# Destino dos novos cálculos

Os novos cálculos pertencem ao serviço existente `simulador_metas_cnj/`, não ao chatbot e não a um terceiro processo.

| Responsabilidade | Destino | Estado do gate |
|---|---|---|
| Esforço mensal da Meta 1 | `simulador_metas_cnj/services/meta1_effort.py` | bloqueado para exposição; deve reutilizar funções/base canônicas |
| Meta 2 A/ANT | `simulador_metas_cnj/services/meta2_groups.py` | bloqueado para exposição; séries importadas não entram até validação |
| DTOs e rotas HTTP | `simulador_metas_cnj/main.py` | somente quando o gate correspondente permitir |
| Testes | `simulador_metas_cnj/tests/` | sempre offline e com fixtures versionadas |

Regras de dependência:

- serviços de domínio recebem dados/valores por argumento e não importam FastAPI;
- `main.py` pode adaptar os serviços ao contrato HTTP;
- módulos não importam `chatbot_processual_ai` nem suas dependências Pydantic 2+;
- nenhuma dependência nova foi adicionada; mantém-se FastAPI 0.95.2/Pydantic 1.10.26 no ambiente exclusivo do simulador;
- endpoints antigos e seus response models permanecem inalterados.
