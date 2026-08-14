import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const contract = JSON.parse(
  await readFile(new URL('../packages/contracts/openapi.json', import.meta.url), 'utf8'),
);

const expected = new Map([
  ['/health', ['get']],
  ['/version', ['get']],
  ['/v1/calibration/next', ['post']],
  ['/v1/calibration/response', ['post']],
  ['/v1/matches/rank', ['post']],
]);

assert.deepEqual(new Set(Object.keys(contract.paths)), new Set(expected.keys()));

for (const [path, methods] of expected) {
  assert.ok(contract.paths[path], `missing contract path ${path}`);
  for (const method of methods) {
    assert.ok(contract.paths[path][method], `missing ${method.toUpperCase()} ${path}`);
    assert.ok(contract.paths[path][method].operationId, `missing operationId for ${method} ${path}`);
  }
}

for (const schemaName of [
  'CalibrationNextRequest',
  'CalibrationNextResponse',
  'CalibrationResponseRequest',
  'CalibrationResponseReceipt',
  'MatchRankRequest',
  'MatchRankResponse',
]) {
  assert.ok(contract.components.schemas[schemaName], `missing schema ${schemaName}`);
}

console.log('Mosaic Phase 3 OpenAPI contract surface check passed.');
