import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { randomUUID } from 'node:crypto';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const anonKey = process.env.ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
const engineUrl = process.env.MOSAIC_TEST_ENGINE_URL ?? 'http://127.0.0.1:8000';

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(anonKey, 'Supabase ANON_KEY is required.');

const thresholdMs = 500;
const samplesPerOperation = 20;
const password = 'Mosaic-P7-Latency-Password-42!';
const email = `phase7-latency-${randomUUID().slice(0, 12)}@mosaic.invalid`;

async function request(url, { method = 'GET', token, apiKey, body, requestId } = {}) {
  const started = performance.now();
  const response = await fetch(url, {
    method,
    headers: {
      ...(apiKey ? { apikey: apiKey } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(requestId ? { 'x-request-id': requestId } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const durationMs = performance.now() - started;
  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }
  return { response, payload, durationMs };
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
  return result.payload.access_token;
}

function percentile(values, probability) {
  assert.ok(values.length > 0);
  const ordered = [...values].sort((left, right) => left - right);
  const index = Math.max(0, Math.ceil(probability * ordered.length) - 1);
  return ordered[index];
}

async function sample(label, operation) {
  for (let warmup = 0; warmup < 2; warmup += 1) {
    const result = await operation(`warmup-${label}-${warmup}`);
    assert.equal(result.response.status, 200, `${label} warmup failed: ${JSON.stringify(result.payload)}`);
  }

  const values = [];
  for (let index = 0; index < samplesPerOperation; index += 1) {
    const result = await operation(`sample-${label}-${index}`);
    assert.equal(result.response.status, 200, `${label} failed: ${JSON.stringify(result.payload)}`);
    assert.equal(result.response.headers.get('x-request-id'), `sample-${label}-${index}`);
    values.push(result.durationMs);
  }
  return values;
}

const token = await signup();
const rankPayload = {
  candidate_ids: [
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
    'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
  ],
  limit: 3,
};

const operations = {
  health: (requestId) => request(`${engineUrl}/health`, { requestId }),
  version: (requestId) => request(`${engineUrl}/version`, { requestId }),
  ranking: (requestId) =>
    request(`${engineUrl}/v1/matches/rank`, {
      method: 'POST',
      body: rankPayload,
      requestId,
    }),
  calibration_next_cached: (requestId) =>
    request(`${engineUrl}/v1/calibration/next`, {
      method: 'POST',
      token,
      body: {},
      requestId,
    }),
  measurement_next_cached: (requestId) =>
    request(`${engineUrl}/v1/measurement/next`, {
      method: 'POST',
      token,
      body: {},
      requestId,
    }),
};

const summary = {};
const allSamples = [];
for (const [label, operation] of Object.entries(operations)) {
  const values = await sample(label, operation);
  allSamples.push(...values);
  const p95 = percentile(values, 0.95);
  summary[label] = {
    count: values.length,
    p50_ms: Number(percentile(values, 0.5).toFixed(3)),
    p95_ms: Number(p95.toFixed(3)),
    max_ms: Number(Math.max(...values).toFixed(3)),
  };
  assert.ok(
    p95 < thresholdMs,
    `${label} p95 ${p95.toFixed(3)} ms exceeded ${thresholdMs} ms internal-alpha target`,
  );
}

const overallP95 = percentile(allSamples, 0.95);
summary.overall = {
  count: allSamples.length,
  p95_ms: Number(overallP95.toFixed(3)),
  target_ms: thresholdMs,
};
assert.ok(overallP95 < thresholdMs);

console.log(JSON.stringify({ event: 'phase7_latency_gate', summary }, null, 2));
