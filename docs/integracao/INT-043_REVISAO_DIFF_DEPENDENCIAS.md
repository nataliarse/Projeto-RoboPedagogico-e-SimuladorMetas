# INT-043 — Revisão de diff, dependências e artefatos

Data: 2026-10-19

Base revisada: `236e033ec74b9773542e1add13343fc4819fc07c`

Branch: `feat/integracao_robo_metas`

## Resultado

- 153 arquivos alterados entre a base e o fechamento da implementação; nenhuma exclusão nesse intervalo.
- O snapshot em `integracao_entrada/` não divergiu desde o commit de importação `38b9108`.
- Nenhum `node_modules/`, `.venv/`, `.tools/`, `dist/`, banco SQLite ou arquivo `.env` real está versionado. Os dois únicos resultados para `.env.*` são exemplos sem credenciais.
- A busca em todos os arquivos versionados não encontrou chave AWS, bloco de chave privada ou atribuição literal suspeita de senha, segredo, chave de API ou token.
- As quatro alterações preexistentes do usuário (`.codex/rules/safety.rules`, `AGENTS.md` e duas exclusões de checklists antigos) permaneceram fora dos commits da integração.

## Dependências e vulnerabilidades

O lockfile do frontend foi regenerado após atualizar, dentro da mesma linha principal 21, os pacotes Angular de runtime para 21.2.25, `@angular/build`/CLI para 21.2.27 e `compiler-cli` para 21.2.25. Isso removeu os avisos de segurança encontrados na primeira auditoria.

| Verificação | Resultado |
|---|---|
| `npm audit --omit=dev` | 0 vulnerabilidades |
| `npm audit` | 0 vulnerabilidades |
| `pip check` — chatbot | nenhuma dependência quebrada |
| `pip check` — simulador | nenhuma dependência quebrada |
| Angular | 9 arquivos, 37 testes aprovados |
| Proxy | 3 testes aprovados |
| Build Angular | aprovado; warning não bloqueante do orçamento CSS já conhecido |
| Chatbot | 157 testes e 2 subtestes aprovados |
| Simulador | 8 testes e 7 subtestes aprovados |

## Licenças diretas

As dependências diretas usam licenças permissivas: Angular/CLI/build, FastAPI, Pydantic, OpenPyXL e ferramentas associadas usam MIT; RxJS e Requests usam Apache-2.0; `tslib` usa 0BSD; NumPy/Pandas usam licenças BSD. Não foi introduzida dependência direta com licença copyleft ou proprietária.

O inventário é uma revisão técnica para entrega e não substitui parecer jurídico. Dependências transitivas continuam fixadas pelo `package-lock.json` e pelos manifests Python.

## Conclusão

O critério do INT-043 foi atendido: não há remoção inadvertida na integração, segredo detectado ou artefato local indevidamente versionado. As dependências instaladas são consistentes e a auditoria npm encerra sem vulnerabilidades conhecidas.
