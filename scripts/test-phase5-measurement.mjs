import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const anonKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;
const engineUrl = process.env.MOSAIC_TEST_ENGINE_URL ?? 'http://127.0.0.1:8000';

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(anonKey, 'Supabase ANON_KEY is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required for integration verification.');

const password = 'Mosaic-P5-Test-Password-42!';
const email = `phase5-${randomUUID().slice(0, 12)}@mosaic.invalid`;

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

function answerFor(item, ordinal) {
  if (item.kind === 'rating') {
    return { kind: 'rating', value: ((ordinal - 1) % 5) + 1 };
  }
  if (item.kind === 'forced_choice') {
    return {
      kind: 'choice',
      option_id: ordinal % 2 ? item.left.id : item.right.id,
    };
  }
  const option = item.options[(ordinal - 1) % item.options.length];
  return { kind: 'choice', option_id: option.id };
}

const unauthenticated = await engine('/v1/measurement/next', null, {});
assert.equal(unauthenticated.response.status, 401, 'measurement endpoint accepted unauthenticated request');

const user = await signup();
let accessToken = user.token;
let sessionId = null;
const presentationIds = [];
const itemKinds = [];

for (let ordinal = 1; ordinal <= 20; ordinal += 1) {
  const next = await engine('/v1/measurement/next', accessToken, {});
  assert.equal(next.response.status, 200, `next item failed: ${JSON.stringify(next.payload)}`);
  assert.equal(next.payload.status, 'item');
  assert.equal(next.payload.ordinal, ordinal);
  assert.equal(next.payload.completed_item_count, ordinal - 1);
  assert.equal(next.payload.target_item_count, 20);
  assert.equal(next.payload.is_mock, true);
  assert.ok(next.payload.presentation_id);
  assert.ok(next.payload.item_id);
  assert.ok(next.payload.item_version);
  assert.ok(next.payload.instrument_version);
  assert.ok(next.payload.selection_policy_version);

  sessionId ??= next.payload.session_id;
  assert.equal(next.payload.session_id, sessionId, 'server did not resume the same measurement session');
  presentationIds.push(next.payload.presentation_id);
  itemKinds.push(next.payload.item.kind);

  const repeatedNext = await engine('/v1/measurement/next', accessToken, {});
  assert.equal(repeatedNext.response.status, 200);
  assert.equal(
    repeatedNext.payload.presentation_id,
    next.payload.presentation_id,
    'repeated next request created a second unanswered measurement item',
  );

  const responseBody = {
    session_id: sessionId,
    presentation_id: next.payload.presentation_id,
    client_response_id: randomUUID(),
    answer: answerFor(next.payload.item, ordinal),
    client_timestamp: new Date().toISOString(),
  };

  const accepted = await engine('/v1/measurement/response', accessToken, responseBody);
  assert.equal(accepted.response.status, 200, `response failed: ${JSON.stringify(accepted.payload)}`);
  assert.equal(accepted.payload.accepted, true);
  assert.equal(accepted.payload.duplicate, false);
  assert.equal(accepted.payload.completed_item_count, ordinal);
  assert.equal(accepted.payload.session_complete, ordinal === 20);

  const duplicate = await engine('/v1/measurement/response', accessToken, responseBody);
  assert.equal(duplicate.response.status, 200, `idempotent retry failed: ${JSON.stringify(duplicate.payload)}`);
  assert.equal(duplicate.payload.duplicate, true);
  assert.equal(duplicate.payload.completed_item_count, ordinal);

  if (ordinal === 10) {
    accessToken = await signIn();
    const resumed = await engine('/v1/measurement/next', accessToken, {});
    assert.equal(resumed.response.status, 200);
    assert.equal(resumed.payload.session_id, sessionId);
    assert.equal(resumed.payload.completed_item_count, 10);
    assert.equal(resumed.payload.ordinal, 11);
  }
}

assert.deepEqual(
  itemKinds.reduce((counts, kind) => ({ ...counts, [kind]: (counts[kind] ?? 0) + 1 }), {}),
  { hard_constraint: 5, rating: 5, scenario: 5, forced_choice: 5 },
);

const complete = await engine('/v1/measurement/next', accessToken, {});
assert.equal(complete.response.status, 200);
assert.equal(complete.payload.status, 'complete');
assert.equal(complete.payload.session_id, sessionId);
assert.equal(complete.payload.completed_item_count, 20);
assert.equal(complete.payload.presentation_id, null);
assert.equal(complete.payload.item, null);

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
  `${supabaseUrl}/rest/v1/measurement_sessions?select=*&subject_id=eq.${subjectId}`,
  serviceHeaders,
);
assert.equal(sessions.response.status, 200);
assert.equal(sessions.payload.length, 1);
assert.equal(sessions.payload[0].id, sessionId);
assert.equal(sessions.payload[0].status, 'complete');
assert.equal(sessions.payload[0].target_item_count, 20);

const presentations = await request(
  `${supabaseUrl}/rest/v1/measurement_presentations?select=*&session_id=eq.${sessionId}&order=ordinal.asc`,
  serviceHeaders,
);
const responsesBeforeScore = await request(
  `${supabaseUrl}/rest/v1/measurement_responses?select=*&session_id=eq.${sessionId}&order=server_timestamp.asc`,
  serviceHeaders,
);
assert.equal(presentations.response.status, 200);
assert.equal(responsesBeforeScore.response.status, 200);
assert.equal(presentations.payload.length, 20);
assert.equal(responsesBeforeScore.payload.length, 20);
assert.deepEqual(
  new Set(presentations.payload.map((presentation) => presentation.id)),
  new Set(presentationIds),
);
for (const presentation of presentations.payload) {
  assert.ok(presentation.item_id);
  assert.ok(presentation.item_version);
  assert.ok(presentation.selection_policy_version);
  assert.ok(presentation.item?.kind);
  assert.ok(presentation.item?.prompt);
}
for (const response of responsesBeforeScore.payload) {
  assert.ok(response.instrument_version);
  assert.ok(response.selection_policy_version);
  assert.ok(response.answer?.kind);
}

const rawSnapshot = JSON.stringify(responsesBeforeScore.payload);
const scoreV1 = await engine('/v1/measurement/score', accessToken, {
  session_id: sessionId,
  scoring_version: 'mock-measurement-p5-score-1.0.0',
});
const scoreV2 = await engine('/v1/measurement/score', accessToken, {
  session_id: sessionId,
  scoring_version: 'mock-measurement-p5-score-2.0.0',
});
assert.equal(scoreV1.response.status, 200, `score v1 failed: ${JSON.stringify(scoreV1.payload)}`);
assert.equal(scoreV2.response.status, 200, `score v2 failed: ${JSON.stringify(scoreV2.payload)}`);
assert.equal(scoreV1.payload.response_count, 20);
assert.equal(scoreV2.payload.response_count, 20);
assert.equal(scoreV1.payload.evidence_fingerprint, scoreV2.payload.evidence_fingerprint);
assert.notEqual(scoreV1.payload.score_run_id, scoreV2.payload.score_run_id);
assert.notDeepEqual(scoreV1.payload.scores, scoreV2.payload.scores);

const scoreV1Repeat = await engine('/v1/measurement/score', accessToken, {
  session_id: sessionId,
  scoring_version: 'mock-measurement-p5-score-1.0.0',
});
assert.equal(scoreV1Repeat.response.status, 200);
assert.equal(scoreV1Repeat.payload.score_run_id, scoreV1.payload.score_run_id);

const responsesAfterScore = await request(
  `${supabaseUrl}/rest/v1/measurement_responses?select=*&session_id=eq.${sessionId}&order=server_timestamp.asc`,
  serviceHeaders,
);
assert.equal(JSON.stringify(responsesAfterScore.payload), rawSnapshot, 'rescoring mutated raw evidence');

const scoreRuns = await request(
  `${supabaseUrl}/rest/v1/measurement_score_runs?select=*&session_id=eq.${sessionId}&order=created_at.asc`,
  serviceHeaders,
);
assert.equal(scoreRuns.response.status, 200);
assert.equal(scoreRuns.payload.length, 2);
assert.deepEqual(
  new Set(scoreRuns.payload.map((run) => run.scoring_version)),
  new Set(['mock-measurement-p5-score-1.0.0', 'mock-measurement-p5-score-2.0.0']),
);

const directUserWrite = await request(`${supabaseUrl}/rest/v1/measurement_responses`, {
  method: 'POST',
  apiKey: anonKey,
  token: accessToken,
  body: {
    session_id: sessionId,
    presentation_id: randomUUID(),
    subject_id: subjectId,
    client_response_id: randomUUID(),
    answer: { kind: 'rating', value: 5 },
    instrument_version: 'forged-client-write',
    selection_policy_version: 'forged-client-write',
  },
});
assert.equal(directUserWrite.response.ok, false, 'authenticated client bypassed measurement write boundary');

const immutableResponse = await request(
  `${supabaseUrl}/rest/v1/measurement_responses?id=eq.${responsesBeforeScore.payload[0].id}`,
  {
    method: 'PATCH',
    ...serviceHeaders,
    body: { answer: { kind: 'rating', value: 1 } },
    prefer: 'return=representation',
  },
);
assert.equal(immutableResponse.response.ok, false, 'database allowed mutation of raw measurement evidence');

const immutablePresentation = await request(
  `${supabaseUrl}/rest/v1/measurement_presentations?id=eq.${presentations.payload[0].id}`,
  { method: 'DELETE', ...serviceHeaders },
);
assert.equal(immutablePresentation.response.ok, false, 'database allowed deletion of authored measurement item');

const immutableScore = await request(
  `${supabaseUrl}/rest/v1/measurement_score_runs?id=eq.${scoreRuns.payload[0].id}`,
  {
    method: 'PATCH',
    ...serviceHeaders,
    body: { scores: { forged: 1 } },
    prefer: 'return=representation',
  },
);
assert.equal(immutableScore.response.ok, false, 'database allowed mutation of derived score provenance');

console.log('Mosaic Phase 5 resumable measurement and immutable-rescoring test passed.');
