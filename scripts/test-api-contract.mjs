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
  ['/v1/measurement/next', ['post']],
  ['/v1/measurement/response', ['post']],
  ['/v1/measurement/score', ['post']],
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
  'MeasurementNextRequest',
  'MeasurementNextResponse',
  'MeasurementResponseRequest',
  'MeasurementResponseReceipt',
  'MeasurementScoreRequest',
  'MeasurementScoreResponse',
  'MeasurementScoringVersion',
  'HardConstraintItem',
  'RatingItem',
  'ScenarioItem',
  'ForcedChoiceItem',
  'MatchRankRequest',
  'MatchRankResponse',
]) {
  assert.ok(contract.components.schemas[schemaName], `missing schema ${schemaName}`);
}

const nextRequest = contract.components.schemas.CalibrationNextRequest;
assert.deepEqual(nextRequest.properties ?? {}, {}, 'calibration next request must not accept client-owned progress state');
const measurementNextRequest = contract.components.schemas.MeasurementNextRequest;
assert.deepEqual(
  measurementNextRequest.properties ?? {},
  {},
  'measurement next request must not accept client-owned progress state',
);

assert.ok(contract.components.securitySchemes.HTTPBearer, 'missing bearer security scheme');
for (const path of [
  '/v1/calibration/next',
  '/v1/calibration/response',
  '/v1/measurement/next',
  '/v1/measurement/response',
  '/v1/measurement/score',
]) {
  assert.deepEqual(contract.paths[path].post.security, [{ HTTPBearer: [] }]);
}

const measurementNext = contract.components.schemas.MeasurementNextResponse.properties;
assert.ok(measurementNext.completed_item_count);
assert.ok(measurementNext.target_item_count);
assert.ok(measurementNext.instrument_version);
assert.ok(measurementNext.selection_policy_version);

const score = contract.components.schemas.MeasurementScoreResponse.properties;
assert.ok(score.scoring_version);
assert.ok(score.evidence_fingerprint);
assert.ok(score.scores);

console.log('Mosaic Phase 5 OpenAPI contract surface check passed.');
