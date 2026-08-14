import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const baseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const clientKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;

assert.ok(baseUrl, 'API_URL or SUPABASE_URL must be exported from `supabase status -o env`.');
assert.ok(clientKey, 'ANON_KEY or SUPABASE_ANON_KEY must be exported from `supabase status -o env`.');

const password = 'Mosaic-P2-Test-Password-42!';
const runId = randomUUID().slice(0, 12);

async function request(path, { method = 'GET', token = clientKey, body, prefer } = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method,
    headers: {
      apikey: clientKey,
      Authorization: `Bearer ${token}`,
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

async function signUp(label) {
  const { response, payload } = await request('/auth/v1/signup', {
    method: 'POST',
    body: {
      email: `${label}-${runId}@mosaic.invalid`,
      password,
    },
  });

  assert.equal(response.status, 200, `signup failed: ${JSON.stringify(payload)}`);
  assert.ok(payload?.access_token, `signup did not return a session: ${JSON.stringify(payload)}`);
  assert.ok(payload?.user?.id, `signup did not return a user: ${JSON.stringify(payload)}`);
  return { token: payload.access_token, userId: payload.user.id };
}

const userA = await signUp('user-a');
const createA = await request('/rest/v1/profiles', {
  method: 'POST',
  token: userA.token,
  prefer: 'return=representation',
  body: { user_id: userA.userId, lifecycle_state: 'onboarding' },
});
assert.equal(createA.response.status, 201, `own profile insert failed: ${JSON.stringify(createA.payload)}`);
assert.equal(createA.payload?.[0]?.user_id, userA.userId);
assert.equal(createA.payload?.[0]?.profile_version, 1);

const readA = await request(`/rest/v1/profiles?select=*&user_id=eq.${userA.userId}`, { token: userA.token });
assert.equal(readA.response.status, 200);
assert.equal(readA.payload?.length, 1);
assert.equal(readA.payload?.[0]?.user_id, userA.userId);

const userB = await signUp('user-b');
const crossRead = await request(`/rest/v1/profiles?select=user_id&user_id=eq.${userA.userId}`, { token: userB.token });
assert.equal(crossRead.response.status, 200);
assert.deepEqual(crossRead.payload, [], 'RLS leaked another user profile row.');

const forbiddenInsert = await request('/rest/v1/profiles', {
  method: 'POST',
  token: userB.token,
  body: { user_id: randomUUID(), lifecycle_state: 'onboarding' },
});
assert.equal(forbiddenInsert.response.ok, false, 'RLS allowed a user to create a profile for another user id.');

const updateA = await request(`/rest/v1/profiles?user_id=eq.${userA.userId}`, {
  method: 'PATCH',
  token: userA.token,
  prefer: 'return=representation',
  body: { lifecycle_state: 'active' },
});
assert.equal(updateA.response.status, 200, `own profile update failed: ${JSON.stringify(updateA.payload)}`);
assert.equal(updateA.payload?.[0]?.lifecycle_state, 'active');
assert.equal(updateA.payload?.[0]?.profile_version, 2, 'profile revision did not increment on update.');
assert.ok(
  new Date(updateA.payload?.[0]?.updated_at).getTime() >= new Date(createA.payload?.[0]?.updated_at).getTime(),
  'updated_at did not advance monotonically.',
);

const crossUpdate = await request(`/rest/v1/profiles?user_id=eq.${userA.userId}`, {
  method: 'PATCH',
  token: userB.token,
  prefer: 'return=representation',
  body: { lifecycle_state: 'paused' },
});
assert.equal(crossUpdate.response.status, 200);
assert.deepEqual(crossUpdate.payload, [], 'RLS allowed another user to update the private profile row.');

const verifyA = await request(`/rest/v1/profiles?select=*&user_id=eq.${userA.userId}`, { token: userA.token });
assert.equal(verifyA.payload?.[0]?.lifecycle_state, 'active');
assert.equal(verifyA.payload?.[0]?.profile_version, 2);

console.log('Supabase Phase 2 auth/profile/RLS integration test passed.');
