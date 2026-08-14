import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const anonKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;
const engineUrl = process.env.MOSAIC_TEST_ENGINE_URL ?? 'http://127.0.0.1:8000';

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(anonKey, 'Supabase ANON_KEY is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required.');

const password = 'Mosaic-P8-Alpha-Password-42!';
const email = `phase8-${randomUUID().slice(0, 12)}@mosaic.invalid`;
const candidateIds = [
  '10000000-0000-4000-8000-000000000001',
  '10000000-0000-4000-8000-000000000002',
  '10000000-0000-4000-8000-000000000003',
  '10000000-0000-4000-8000-000000000004',
  '10000000-0000-4000-8000-000000000005',
];

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
    return { kind: 'choice', option_id: ordinal % 2 ? item.left.id : item.right.id };
  }
  return { kind: 'choice', option_id: item.options[(ordinal - 1) % item.options.length].id };
}

const unauthenticatedRank = await engine('/v1/matches/rank', null, {
  candidate_ids: candidateIds,
  limit: candidateIds.length,
});
assert.equal(unauthenticatedRank.response.status, 401, 'ranking accepted unauthenticated request');

const user = await signup();
let accessToken = user.token;

const profileCreate = await request(`${supabaseUrl}/rest/v1/profiles`, {
  method: 'POST',
  apiKey: anonKey,
  token: accessToken,
  prefer: 'return=representation',
  body: { user_id: user.userId, lifecycle_state: 'onboarding' },
});
assert.equal(profileCreate.response.status, 201, `profile create failed: ${JSON.stringify(profileCreate.payload)}`);
assert.equal(profileCreate.payload?.[0]?.lifecycle_state, 'onboarding');

let measurementSessionId = null;
let hardConstraintCount = 0;
for (let ordinal = 1; ordinal <= 20; ordinal += 1) {
  const next = await engine('/v1/measurement/next', accessToken, {});
  assert.equal(next.response.status, 200, `measurement next failed: ${JSON.stringify(next.payload)}`);
  assert.equal(next.payload.status, 'item');
  assert.equal(next.payload.ordinal, ordinal);
  measurementSessionId ??= next.payload.session_id;
  assert.equal(next.payload.session_id, measurementSessionId);
  if (next.payload.item.kind === 'hard_constraint') hardConstraintCount += 1;

  const accepted = await engine('/v1/measurement/response', accessToken, {
    session_id: next.payload.session_id,
    presentation_id: next.payload.presentation_id,
    client_response_id: randomUUID(),
    answer: answerFor(next.payload.item, ordinal),
    client_timestamp: new Date().toISOString(),
  });
  assert.equal(accepted.response.status, 200, `measurement response failed: ${JSON.stringify(accepted.payload)}`);
  assert.equal(accepted.payload.completed_item_count, ordinal);
}
assert.equal(hardConstraintCount, 5, 'internal alpha did not traverse the five hard-constraint fixtures');

const measurementComplete = await engine('/v1/measurement/next', accessToken, {});
assert.equal(measurementComplete.response.status, 200);
assert.equal(measurementComplete.payload.status, 'complete');
assert.equal(measurementComplete.payload.completed_item_count, 20);

const profileActivate = await request(
  `${supabaseUrl}/rest/v1/profiles?user_id=eq.${user.userId}`,
  {
    method: 'PATCH',
    apiKey: anonKey,
    token: accessToken,
    prefer: 'return=representation',
    body: { lifecycle_state: 'active' },
  },
);
assert.equal(profileActivate.response.status, 200, `profile activation failed: ${JSON.stringify(profileActivate.payload)}`);
assert.equal(profileActivate.payload?.[0]?.lifecycle_state, 'active');

let syntheticSessionId = null;
for (let ordinal = 1; ordinal <= 20; ordinal += 1) {
  const next = await engine('/v1/synthetic-calibration/next', accessToken, {});
  assert.equal(next.response.status, 200, `synthetic next failed: ${JSON.stringify(next.payload)}`);
  assert.equal(next.payload.status, 'pair');
  assert.equal(next.payload.pair.ordinal, ordinal);
  syntheticSessionId ??= next.payload.session_id;
  assert.equal(next.payload.session_id, syntheticSessionId);

  const accepted = await engine('/v1/synthetic-calibration/response', accessToken, {
    session_id: next.payload.session_id,
    pair_id: next.payload.pair.pair_id,
    client_response_id: randomUUID(),
    response: ['left', 'right', 'both', 'neither'][(ordinal - 1) % 4],
    client_timestamp: new Date().toISOString(),
  });
  assert.equal(accepted.response.status, 200, `synthetic response failed: ${JSON.stringify(accepted.payload)}`);
  assert.equal(accepted.payload.completed_trial_count, ordinal);
}

const syntheticComplete = await engine('/v1/synthetic-calibration/next', accessToken, {});
assert.equal(syntheticComplete.response.status, 200);
assert.equal(syntheticComplete.payload.status, 'complete');
assert.equal(syntheticComplete.payload.completed_trial_count, 20);

const rankingRequest = { candidate_ids: candidateIds, limit: candidateIds.length };
const ranking = await engine('/v1/matches/rank', accessToken, rankingRequest);
assert.equal(ranking.response.status, 200, `ranking failed: ${JSON.stringify(ranking.payload)}`);
assert.equal(ranking.payload.persisted, true);
assert.equal(ranking.payload.is_mock, true);
assert.equal(ranking.payload.ranked_candidates.length, candidateIds.length);
assert.equal(ranking.payload.request_fingerprint.length, 64);
assert.ok(ranking.payload.run_id);
assert.ok(ranking.payload.model_version);

const repeatedRanking = await engine('/v1/matches/rank', accessToken, {
  candidate_ids: [...candidateIds].reverse(),
  limit: candidateIds.length,
});
assert.equal(repeatedRanking.response.status, 200);
assert.equal(repeatedRanking.payload.run_id, ranking.payload.run_id, 'normalized identical candidate set created a second ranking run');
assert.equal(repeatedRanking.payload.request_fingerprint, ranking.payload.request_fingerprint);
assert.deepEqual(repeatedRanking.payload.ranked_candidates, ranking.payload.ranked_candidates);

// Simulate app closure followed by a fresh authenticated session.
accessToken = await signIn();

const resumedProfile = await request(
  `${supabaseUrl}/rest/v1/profiles?select=*&user_id=eq.${user.userId}`,
  { apiKey: anonKey, token: accessToken },
);
assert.equal(resumedProfile.response.status, 200);
assert.equal(resumedProfile.payload?.[0]?.lifecycle_state, 'active');

const resumedMeasurement = await engine('/v1/measurement/next', accessToken, {});
assert.equal(resumedMeasurement.response.status, 200);
assert.equal(resumedMeasurement.payload.status, 'complete');
assert.equal(resumedMeasurement.payload.session_id, measurementSessionId);
assert.equal(resumedMeasurement.payload.completed_item_count, 20);

const resumedSynthetic = await engine('/v1/synthetic-calibration/next', accessToken, {});
assert.equal(resumedSynthetic.response.status, 200);
assert.equal(resumedSynthetic.payload.status, 'complete');
assert.equal(resumedSynthetic.payload.session_id, syntheticSessionId);
assert.equal(resumedSynthetic.payload.completed_trial_count, 20);

const resumedRanking = await engine('/v1/matches/rank', accessToken, rankingRequest);
assert.equal(resumedRanking.response.status, 200);
assert.equal(resumedRanking.payload.run_id, ranking.payload.run_id);
assert.equal(resumedRanking.payload.request_fingerprint, ranking.payload.request_fingerprint);
assert.deepEqual(resumedRanking.payload.ranked_candidates, ranking.payload.ranked_candidates);

const serviceHeaders = { apiKey: serviceRoleKey, token: serviceRoleKey };
const subjects = await request(
  `${supabaseUrl}/rest/v1/science_subjects?select=subject_id&user_id=eq.${user.userId}`,
  serviceHeaders,
);
assert.equal(subjects.response.status, 200);
assert.equal(subjects.payload.length, 1);
const subjectId = subjects.payload[0].subject_id;

const storedRuns = await request(
  `${supabaseUrl}/rest/v1/match_rank_runs?select=*&subject_id=eq.${subjectId}`,
  serviceHeaders,
);
assert.equal(storedRuns.response.status, 200);
assert.equal(storedRuns.payload.length, 1);
assert.equal(storedRuns.payload[0].id, ranking.payload.run_id);
assert.equal(storedRuns.payload[0].model_version, ranking.payload.model_version);
assert.equal(storedRuns.payload[0].request_fingerprint, ranking.payload.request_fingerprint);
assert.deepEqual(storedRuns.payload[0].ranked_candidates, ranking.payload.ranked_candidates);

const directScienceWrite = await request(`${supabaseUrl}/rest/v1/match_rank_runs`, {
  method: 'POST',
  apiKey: anonKey,
  token: accessToken,
  body: {
    subject_id: subjectId,
    model_version: 'forbidden-client-write',
    request_fingerprint: '0'.repeat(64),
    candidate_ids: candidateIds,
    requested_limit: 5,
    ranked_candidates: [],
  },
});
assert.equal(directScienceWrite.response.ok, false, 'authenticated client wrote a ranking run directly');

const mutation = await request(
  `${supabaseUrl}/rest/v1/match_rank_runs?id=eq.${ranking.payload.run_id}`,
  {
    method: 'PATCH',
    ...serviceHeaders,
    body: { model_version: 'mutated' },
  },
);
assert.equal(mutation.response.ok, false, 'privileged caller mutated immutable ranking history');

console.log('Mosaic Phase 8 complete resumable internal-alpha journey passed.');
