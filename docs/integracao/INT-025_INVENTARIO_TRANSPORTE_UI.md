# Inventário do transporte da UI do simulador

Origem preservada: `integracao_entrada/TCC-Simulador-CNJ/frontend/meu-primeiro-app/src/app`.
Destino canônico: `frontend/src/app`.

| Capacidade | Artefato importado | Situação depois |
|---|---|---|
| Base e estado | `dados.service.ts`, `simulador.service.ts` | Transportados integralmente |
| Contratos HTTP | `simulador.model.ts`, `simulador-api.service.ts` | Transportados; adaptação fica no INT-026 |
| Cenários | `cenarios.component.ts` | Transportado integralmente |
| Gráficos | `graficos.component.ts` | Transportado integralmente |
| Tabela mensal | `tabela.component.ts` | Transportado integralmente |
| Otimizador | `otimizador.component.ts` | Transportado integralmente |
| Composição | `simulador-shell.component.ts` | Transportado e exposto em `/simulador` |

Os nove arquivos foram copiados da versão mais recente recebida sem reescrever fórmulas
ou remover recursos. O chat e sua rota principal permaneceram canônicos. Ajustes de
URLs, modelos e testes são deliberadamente separados nos itens INT-026 a INT-030.
