import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const anonKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;
const engineUrl = process.env.MOSAIC_TEST_ENGINE_URL ?? 'http://127.0.0.1:8000';

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(anonKey, 'Supabase ANON_KEY is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required for integration verification.');

const password = 'Mosaic-P4-Test-Password-42!';
const email = `phase4-${randomUUID().slice(0, 12)}@mosaic.invalid`;

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

const unauthenticated = await engine('/v1/calibration/next', null, {});
assert.equal(unauthenticated.response.status, 401, 'calibration endpoint accepted an unauthenticated request');

const user = await signup();
let accessToken = user.token;
let sessionId = null;
const experimentIds = [];

for (let ordinal = 1; ordinal <= 10; ordinal += 1) {
  const next = await engine('/v1/calibration/next', accessToken, {});
  assert.equal(next.response.status, 200, `next trial failed: ${JSON.stringify(next.payload)}`);
  assert.equal(next.payload.status, 'trial');
  assert.equal(next.payload.ordinal, ordinal);
  assert.equal(next.payload.completed_trial_count, ordinal - 1);
  assert.equal(next.payload.target_trial_count, 10);
  assert.equal(next.payload.is_mock, true);
  assert.ok(next.payload.experiment_id);

  sessionId ??= next.payload.session_id;
  assert.equal(next.payload.session_id, sessionId, 'server did not resume the same calibration session');
  experimentIds.push(next.payload.experiment_id);

  const repeatedNext = await engine('/v1/calibration/next', accessToken, {});
  assert.equal(repeatedNext.response.status, 200);
  assert.equal(
    repeatedNext.payload.experiment_id,
    next.payload.experiment_id,
    'repeated next request created a second unanswered experiment',
  );

  const responseBody = {
    session_id: sessionId,
    experiment_id: next.payload.experiment_id,
    client_response_id: randomUUID(),
    response: ['left', 'right', 'both', 'neither'][(ordinal - 1) % 4],
    client_timestamp: new Date().toISOString(),
  };

  const accepted = await engine('/v1/calibration/response', accessToken, responseBody);
  assert.equal(accepted.response.status, 200, `response failed: ${JSON.stringify(accepted.payload)}`);
  assert.equal(accepted.payload.accepted, true);
  assert.equal(accepted.payload.duplicate, false);
  assert.equal(accepted.payload.completed_trial_count, ordinal);
  assert.equal(accepted.payload.session_complete, ordinal === 10);

  const duplicate = await engine('/v1/calibration/response', accessToken, responseBody);
  assert.equal(duplicate.response.status, 200, `idempotent retry failed: ${JSON.stringify(duplicate.payload)}`);
  assert.equal(duplicate.payload.duplicate, true);
  assert.equal(duplicate.payload.completed_trial_count, ordinal);

  if (ordinal === 5) {
    accessToken = await signIn();
    const resumed = await engine('/v1/calibration/next', accessToken, {});
    assert.equal(resumed.response.status, 200);
    assert.equal(resumed.payload.session_id, sessionId);
    assert.equal(resumed.payload.completed_trial_count, 5);
    assert.equal(resumed.payload.ordinal, 6);
  }
}

const complete = await engine('/v1/calibration/next', accessToken, {});
assert.equal(complete.response.status, 200);
assert.equal(complete.payload.status, 'complete');
assert.equal(complete.payload.session_id, sessionId);
assert.equal(complete.payload.completed_trial_count, 10);
assert.equal(complete.payload.experiment_id, null);
assert.equal(complete.payload.stimulus, null);

const serviceHeaders = { apiKey: serviceRoleKey, token: serviceRoleKey };
const subjects = await request(
  `${supabaseUrl}/rest/v1/science_subjects?select=subject_id,user_id&user_id=eq.${user.userId}`,
  serviceHeaders,
);
assert.equal(subjects.response.status, 200);
assert.equal(subjects.payload.length, 1);
const subjectId = subjects.payload[0].subject_id;
assert.notEqual(subjectId, user.userId, 'science subject id must not reuse the authentication user id');

const sessions = await request(
  `${supabaseUrl}/rest/v1/calibration_sessions?select=*&subject_id=eq.${subjectId}`,
  serviceHeaders,
);
assert.equal(sessions.response.status, 200);
assert.equal(sessions.payload.length, 1);
assert.equal(sessions.payload[0].id, sessionId);
assert.equal(sessions.payload[0].status, 'complete');

const trials = await request(
  `${supabaseUrl}/rest/v1/calibration_trials?select=*&session_id=eq.${sessionId}&order=ordinal.asc`,
  serviceHeaders,
);
const responses = await request(
  `${supabaseUrl}/rest/v1/calibration_responses?select=*&session_id=eq.${sessionId}&order=server_timestamp.asc`,
  serviceHeaders,
);
assert.equal(trials.response.status, 200);
assert.equal(responses.response.status, 200);
assert.equal(trials.payload.length, 10);
assert.equal(responses.payload.length, 10);
assert.deepEqual(trials.payload.map((trial) => trial.ordinal), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
assert.deepEqual(new Set(trials.payload.map((trial) => trial.id)), new Set(experimentIds));
assert.deepEqual(
  new Set(responses.payload.map((response) => response.experiment_id)),
  new Set(experimentIds),
);
for (const trial of trials.payload) {
  assert.ok(trial.stimulus_id);
  assert.ok(trial.stimulus_version);
  assert.ok(trial.policy_version);
  assert.ok(trial.stimulus?.left?.label);
  assert.ok(trial.stimulus?.right?.label);
}

const directUserWrite = await request(`${supabaseUrl}/rest/v1/calibration_responses`, {
  method: 'POST',
  apiKey: anonKey,
  token: accessToken,
  body: {
    session_id: sessionId,
    experiment_id: randomUUID(),
    subject_id: subjectId,
    client_response_id: randomUUID(),
    response: 'left',
    policy_version: 'forged-client-write',
  },
});
assert.equal(directUserWrite.response.ok, false, 'authenticated client bypassed the engine write boundary');

const immutableResponse = await request(
  `${supabaseUrl}/rest/v1/calibration_responses?id=eq.${responses.payload[0].id}`,
  {
    method: 'PATCH',
    ...serviceHeaders,
    body: { response: 'neither' },
    prefer: 'return=representation',
  },
);
assert.equal(immutableResponse.response.ok, false, 'database allowed mutation of raw calibration evidence');

const immutableTrial = await request(
  `${supabaseUrl}/rest/v1/calibration_trials?id=eq.${trials.payload[0].id}`,
  { method: 'DELETE', ...serviceHeaders },
);
assert.equal(immutableTrial.response.ok, false, 'database allowed deletion of an authored calibration trial');

const verifyResponses = await request(
  `${supabaseUrl}/rest/v1/calibration_responses?select=id&session_id=eq.${sessionId}`,
  serviceHeaders,
);
assert.equal(verifyResponses.payload.length, 10, 'immutability probes changed the stored response history');

console.log('Mosaic Phase 4 authenticated ten-trial vertical slice passed.');
