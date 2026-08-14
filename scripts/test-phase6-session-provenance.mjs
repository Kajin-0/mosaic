import assert from 'node:assert/strict';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required.');

async function request(url, { method = 'GET', body, prefer } = {}) {
  const response = await fetch(url, {
    method,
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
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

const sessions = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_sessions` +
    '?select=id,instrument_version,pair_policy_version,generator_adapter_version,status' +
    '&order=created_at.desc&limit=1',
);
assert.equal(sessions.response.status, 200);
assert.equal(sessions.payload.length, 1, 'Phase 6 replay did not leave a synthetic session to audit.');

const session = sessions.payload[0];
assert.equal(session.status, 'complete');

const forgedInstrument = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_sessions?id=eq.${session.id}`,
  {
    method: 'PATCH',
    body: { instrument_version: 'forged-after-experiment' },
    prefer: 'return=representation',
  },
);
assert.equal(
  forgedInstrument.response.ok,
  false,
  'service role rewrote immutable synthetic session provenance',
);

const forgedDelete = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_sessions?id=eq.${session.id}`,
  {
    method: 'DELETE',
    prefer: 'return=representation',
  },
);
assert.equal(forgedDelete.response.ok, false, 'service role deleted a synthetic calibration session');

const reread = await request(
  `${supabaseUrl}/rest/v1/synthetic_calibration_sessions?id=eq.${session.id}` +
    '&select=id,instrument_version,pair_policy_version,generator_adapter_version,status',
);
assert.equal(reread.response.status, 200);
assert.equal(reread.payload.length, 1);
assert.deepEqual(reread.payload[0], session, 'failed mutation changed synthetic session provenance');

console.log('Mosaic Phase 6 session provenance immutability test passed.');
