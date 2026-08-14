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
  'CalibrationNextStatus',
  'MatchRankRequest',
  'MatchRankResponse',
]) {
  assert.ok(contract.components.schemas[schemaName], `missing schema ${schemaName}`);
}

const nextRequest = contract.components.schemas.CalibrationNextRequest;
assert.deepEqual(nextRequest.properties ?? {}, {}, 'next-trial request must not accept client-owned progress state');
assert.ok(contract.components.securitySchemes.HTTPBearer, 'missing bearer security scheme');
assert.deepEqual(contract.paths['/v1/calibration/next'].post.security, [{ HTTPBearer: [] }]);
assert.deepEqual(contract.paths['/v1/calibration/response'].post.security, [{ HTTPBearer: [] }]);

const nextResponse = contract.components.schemas.CalibrationNextResponse.properties;
assert.ok(nextResponse.completed_trial_count);
assert.ok(nextResponse.target_trial_count);
assert.ok(nextResponse.status);

const receipt = contract.components.schemas.CalibrationResponseReceipt.properties;
assert.ok(receipt.duplicate);
assert.ok(receipt.session_complete);
assert.ok(receipt.server_timestamp);

console.log('Mosaic Phase 4 OpenAPI contract surface check passed.');
