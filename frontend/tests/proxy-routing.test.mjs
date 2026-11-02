import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const config = JSON.parse(
  await readFile(new URL('../proxy.conf.json', import.meta.url), 'utf8'),
);

function resolveProxy(path) {
  const context = Object.keys(config)
    .filter((candidate) => path.startsWith(candidate))
    .sort((left, right) => right.length - left.length)[0];
  assert.ok(context, `rota sem proxy: ${path}`);
  const rule = config[context];
  let forwardedPath = path;
  for (const [pattern, replacement] of Object.entries(rule.pathRewrite ?? {})) {
    forwardedPath = forwardedPath.replace(new RegExp(pattern), replacement);
  }
  return `${rule.target}${forwardedPath}`;
}

test('chat e metas integradas chegam ao backend processual', () => {
  assert.equal(
    resolveProxy('/api/processos/chat'),
    'http://127.0.0.1:8000/api/processos/chat',
  );
  assert.equal(
    resolveProxy('/api/metas/simular'),
    'http://127.0.0.1:8000/api/metas/simular',
  );
});

test('rotas antigas e novas do simulador chegam ao backend na porta 8001', () => {
  for (const endpoint of [
    'base', 'simular', 'comparar', 'otimizador',
    'meta1/quanto-falta', 'meta2/base', 'meta2/simular',
  ]) {
    assert.equal(
      resolveProxy(`/api/simulador/${endpoint}`),
      `http://127.0.0.1:8001/api/${endpoint}`,
    );
  }
});

test('healthchecks distintos não colidem', () => {
  assert.equal(
    resolveProxy('/api/processos/health'),
    'http://127.0.0.1:8000/api/health',
  );
  assert.equal(
    resolveProxy('/api/simulador/health'),
    'http://127.0.0.1:8001/api/health',
  );
});
