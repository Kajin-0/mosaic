import assert from 'node:assert/strict';
import { createHash, randomUUID } from 'node:crypto';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const anonKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;
const engineUrl = process.env.MOSAIC_TEST_ENGINE_URL ?? 'http://127.0.0.1:8000';

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(anonKey, 'Supabase ANON_KEY is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required for integration verification.');

const password = 'Mosaic-P6-Test-Password-42!';
const email = `phase6-${randomUUID().slice(0, 12)}@mosaic.invalid`;

async function request(url, { method = 'GET', token, apiKey, body, prefer } = {}) {
  const response = await fetch(url, {
    method,
    headers: {
      ...(apiKey ? { apikey: apiKey } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(prefer ? { Prefer: prefer } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }
  return { response, payload };
}

async function signup() {
  const result = await request(`${supabaseUrl}/auth/v1/signup`, {
    method: 'POST',
    apiKey: anonKey,
    token: anonKey,
    body: { email, password },
  });
  assert.equal(result.response.status, 200, `signup failed: ${JSON.stringify(result.payload)}`);
  assert.ok(result.payload?.access_token);
  assert.ok(result.payload?.user?.id);
  return { token: result.payload.access_token, userId: result.payload.user.id };
}

async function signIn() {
  const result = await request(`${supabaseUrl}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    apiKey: anonKey,
    token: anonKey,
    body: { email, password },
  });
  assert.equal(result.response.status, 200, `sign in failed: ${JSON.stringify(result.payload)}`);
  assert.ok(result.payload?.access_token);
  return result.payload.access_token;
}

async function engine(path, token, body) {
  return request(`${engineUrl}${path}`, { method: 'POST', token, body });
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

const unauthenticated = await engine('/v1/synthetic-calibration/next', null, {});
assert.equal(
  unauthenticated.response.status,
  401,
  'synthetic calibration endpoint accepted unauthenticated request',
);

const user = await signup();
let accessToken = user.token;
let sessionId = null;
const presentedPairs = [];

for (let ordinal = 1; ordinal <= 20; ordinal += 1) {
  const next = await engine('/v1/synthetic-calibration/next', accessToken, {});
  assert.equal(next.response.status, 200, `next pair failed: ${JSON.stringify(next.payload)}`);
  assert.equal(next.payload.status, 'pair');
  assert.equal(next.payload.pair.ordinal, ordinal);
  assert.equal(next.payload.completed_trial_count, ordinal - 1);
  assert.equal(next.payload.target_trial_count, 20);
  assert.equal(next.payload.cache_ready, true);
  assert.equal(next.payload.is_mock, true);
  assert.equal(next.payload.response_options.length, 4);
  assert.ok(next.payload.instrument_version);
  assert.ok(next.payload.pair_policy_version);
  assert.ok(next.payload.generator_adapter_version);

  sessionId ??= next.payload.session_id;
  assert.equal(next.payload.session_id, sessionId, 'server did not resume synthetic session');

  for (const side of ['left', 'right']) {
    const asset = next.payload.pair[side];
    assert.ok(asset.asset_id);
    assert.ok(asset.specification_id);
    assert.equal(asset.media_type, 'image/png');
    assert.equal(asset.content_sha256.length, 64);
    assert.ok(asset.asset_uri.startsWith('data:image/png;base64,'));
    assert.equal(asset.provenance.adapter_key, 'deterministic-png');
    assert.equal(asset.provenance.provider, 'mosaic-local-mock');
    const raw = Buffer.from(asset.asset_uri.split(',', 2)[1], 'base64');
    assert.equal(raw.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    assert.equal(sha256(raw), asset.content_sha256);
  }
  assert.notEqual(next.payload.pair.left.asset_id, next.payload.pair.right.asset_id);

  presentedPairs.push({
    id: next.payload.pair.pair_id,
    ordinal,
    left: next.payload.pair.left.asset_id,
    right: next.payload.pair.right.asset_id,
  });

  const repeatedNext = await engine('/v1/synthetic-calibration/next', accessToken, {});
  assert.equal(repeatedNext.response.status, 200);
  assert.equal(
    repeatedNext.payload.pair.pair_id,
    next.payload.pair.pair_id,
    'repeated next request created a second unanswered synthetic pair',
  );

  const responseBody = {
    session_id: sessionId,
    pair_id: next.payload.pair.pair_id,
    client_response_id: randomUUID(),
    response: ['left', 'right', 'both', 'neither'][(ordinal - 1) % 4],
    client_timestamp: new Date().toISOString(),
  };

  const accepted = await engine('/v1/synthetic-calibration/response', accessToken, responseBody);
  assert.equal(accepted.response.status, 200, `response failed: ${JSON.stringify(accepted.payload)}`);
  assert.equal(accepted.payload.accepted, true);
  assert.equal(accepted.payload.duplicate, false);
  assert.equal(accepted.payload.completed_trial_count, ordinal);
  assert.equal(accepted.payload.session_complete, ordinal === 20);

  const duplicate = await engine('/v1/synthetic-calibration/response', accessToken, responseBody);
  assert.equal(duplicate.response.status, 200, `idempotent retry failed: ${JSON.stringify(duplicate.payload)}`);
  assert.equal(duplicate.payload.duplicate, true);
  assert.equal(duplicate.payload.completed_trial_count, ordinal);

  if (ordinal === 10) {
    accessToken = await signIn();
    const resumed = await engine('/v1/synthetic-calibration/next', accessToken, {});
    assert.equal(resumed.response.status, 200);
    assert.equal(resumed.payload.session_id, sessionId);
    assert.equal(resumed.payload.completed_trial_count, 10);
    assert.equal(resumed.payload.pair.ordinal, 11);
  }
}

const complete = await engine('/v1/synthetic-calibration/next', accessToken, {});
assert.equal(complete.response.status, 200);
assert.equal(complete.payload.status, 'complete');
assert.equal(complete.payload.session_id, sessionId);
assert.equal(complete.payload.completed_trial_count, 20);
assert.equal(complete.payload.pair, null);
assert.equal(complete.payload.cache_ready, true);

const serviceHeaders = { apiKey: serviceRoleKey, token: serviceRoleKey };
const subjects = await request(
  `${supabaseUrl}/rest/v1/science_subjects?select=subject_id,user_id&user_id=eq.${user.userId}`,
  serviceHeaders,
);
assert.equal(subjects.response.status, 200);
assert.equal(subjects.payload.length, 1);
const subjectId = subjects.payload[0].subject_id;
assert.notEqual(subjectId, user.userId);

const sessions = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_sessions?select=*&subject_id=eq.${subjectId}`,
  serviceHeaders,
);
assert.equal(sessions.response.status, 200);
assert.equal(sessions.payload.length, 1);
assert.equal(sessions.payload[0].id, sessionId);
assert.equal(sessions.payload[0].status, 'complete');
assert.equal(sessions.payload[0].target_trial_count, 20);

const specs = await request(
  `${supabaseUrl}/rest/v1/synthetic_stimulus_specs?select=*&session_id=eq.${sessionId}&order=stimulus_key.asc`,
  serviceHeaders,
);
const assets = await request(
  `${supabaseUrl}/rest/v1/synthetic_assets?select=*&session_id=eq.${sessionId}&order=created_at.asc`,
  serviceHeaders,
);
const qcEvents = await request(
  `${supabaseUrl}/rest/v1/synthetic_qc_events?select=*&session_id=eq.${sessionId}&order=created_at.asc`,
  serviceHeaders,
);
const pairs = await request(
  `${supabaseUrl}/rest/v1/synthetic_pairs?select=*&session_id=eq.${sessionId}&order=ordinal.asc`,
  serviceHeaders,
);
const responses = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_responses?select=*&session_id=eq.${sessionId}&order=server_timestamp.asc`,
  serviceHeaders,
);

for (const result of [specs, assets, qcEvents, pairs, responses]) {
  assert.equal(result.response.status, 200);
}
assert.equal(specs.payload.length, 40);
assert.equal(assets.payload.length, 40);
assert.equal(qcEvents.payload.length, 40);
assert.equal(pairs.payload.length, 20);
assert.equal(responses.payload.length, 20);

const specById = new Map(specs.payload.map((spec) => [spec.id, spec]));
const assetById = new Map(assets.payload.map((asset) => [asset.id, asset]));
const qcByAsset = new Map(qcEvents.payload.map((event) => [event.asset_id, event]));

for (const spec of specs.payload) {
  assert.equal(spec.specification_sha256.length, 64);
  assert.equal(sha256(stableStringify(spec.specification)), spec.specification_sha256);
  assert.equal(spec.specification.spec_version, spec.spec_version);
  assert.ok(spec.specification.control_vector);
}

for (const asset of assets.payload) {
  assert.ok(specById.has(asset.spec_id));
  assert.equal(asset.media_type, 'image/png');
  assert.equal(asset.content_sha256.length, 64);
  assert.ok(asset.asset_uri.startsWith('data:image/png;base64,'));
  const raw = Buffer.from(asset.asset_uri.split(',', 2)[1], 'base64');
  assert.equal(raw.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
  assert.equal(sha256(raw), asset.content_sha256);
  assert.equal(asset.generation_provenance.adapter_key, 'deterministic-png');
  assert.equal(asset.generation_provenance.provider, 'mosaic-local-mock');
  assert.equal(qcByAsset.get(asset.id)?.decision, 'accepted');
}

assert.deepEqual(
  pairs.payload.map((pair) => ({
    id: pair.id,
    ordinal: pair.ordinal,
    left: pair.left_asset_id,
    right: pair.right_asset_id,
  })),
  presentedPairs,
  'database metadata could not replay the exact presented pair sequence',
);
for (const pair of pairs.payload) {
  assert.ok(assetById.has(pair.left_asset_id));
  assert.ok(assetById.has(pair.right_asset_id));
  assert.notEqual(pair.left_asset_id, pair.right_asset_id);
  assert.ok(pair.pair_policy_version);
}
for (const response of responses.payload) {
  assert.ok(pairs.payload.some((pair) => pair.id === response.pair_id));
  assert.ok(['left', 'right', 'both', 'neither'].includes(response.response));
}

const directUserWrite = await request(`${supabaseUrl}/rest/v1/synthetic_calibration_responses`, {
  method: 'POST',
  apiKey: anonKey,
  token: accessToken,
  body: {
    session_id: sessionId,
    pair_id: randomUUID(),
    subject_id: subjectId,
    client_response_id: randomUUID(),
    response: 'left',
    pair_policy_version: 'forged-client-write',
  },
});
assert.equal(
  directUserWrite.response.ok,
  false,
  'authenticated client bypassed synthetic science write boundary',
);

const mutationProbes = [
  ['synthetic_stimulus_specs', specs.payload[0].id, { stimulus_key: 'forged' }],
  ['synthetic_assets', assets.payload[0].id, { content_sha256: '0'.repeat(64) }],
  ['synthetic_qc_events', qcEvents.payload[0].id, { decision: 'rejected' }],
  ['synthetic_pairs', pairs.payload[0].id, { ordinal: 999 }],
  ['synthetic_calibration_responses', responses.payload[0].id, { response: 'neither' }],
];
for (const [table, id, body] of mutationProbes) {
  const mutation = await request(`${supabaseUrl}/rest/v1/${table}?id=eq.${id}`, {
    method: 'PATCH',
    ...serviceHeaders,
    body,
    prefer: 'return=representation',
  });
  assert.equal(mutation.response.ok, false, `database allowed mutation of ${table}`);
}

console.log('Mosaic Phase 6 replayable synthetic calibration test passed.');
