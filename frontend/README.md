# Frontend Angular

## Bootstrap local

O frontend usa Angular 21.2.x. Use uma versão do Node.js compatível com essa
versão do Angular e deixe `node` e `npm` disponíveis no `PATH`. Para este
repositório, recomenda-se Node.js 24.x com npm 11.x; o bootstrap foi validado
com Node.js 24.19.0 e npm 11.17.0. O `package.json` declara npm 11.11.1 como
gerenciador do projeto, sem exigir que essa seja a única versão 11 compatível.

A partir da raiz do repositório:

```text
cd frontend
npm ci
npm start
```

`npm ci` reconstrói as dependências exatamente a partir de `package-lock.json`.
Não use `npm install` no fluxo normal de bootstrap, pois ele pode recalcular o
grafo e alterar o lockfile.

O servidor de desenvolvimento fica disponível em `http://localhost:4200/`.
As chamadas da aplicação usam URLs relativas sob `/api`; o proxy de
desenvolvimento já está versionado, portanto não é necessário editar o código
para trocar a URL da API. O backend só precisa estar disponível quando uma
funcionalidade que chama `/api` for utilizada.

## Testes e build

Depois de `npm ci`, execute:

```text
npm test -- --watch=false
npm run build
```

## Dependências e caches locais

`node_modules/` e `.angular/cache/` são artefatos locais reconstruíveis e não
devem ser versionados, copiados de outra máquina, enviados em ZIP nem
reutilizados entre sistemas operacionais. Não transfira esses diretórios: em
cada ambiente de destino, execute `npm ci` para reconstruí-los a partir do
lockfile versionado.
