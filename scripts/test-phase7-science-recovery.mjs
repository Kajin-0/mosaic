import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const supabaseUrl = process.env.API_URL ?? process.env.SUPABASE_URL;
const serviceRoleKey = process.env.SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;

assert.ok(supabaseUrl, 'Supabase API_URL is required.');
assert.ok(serviceRoleKey, 'Supabase SERVICE_ROLE_KEY is required.');

const backupPath = '/tmp/mosaic-science-evidence-backup.json';
const tableDefinitions = [
  { name: 'science_subjects', select: 'subject_id,created_at', key: 'subject_id' },
  { name: 'calibration_sessions', select: '*', key: 'id' },
  { name: 'calibration_trials', select: '*', key: 'id' },
  { name: 'calibration_responses', select: '*', key: 'id' },
  { name: 'measurement_sessions', select: '*', key: 'id' },
  { name: 'measurement_presentations', select: '*', key: 'id' },
  { name: 'measurement_responses', select: '*', key: 'id' },
  { name: 'measurement_score_runs', select: '*', key: 'id' },
  { name: 'synthetic_calibration_sessions', select: '*', key: 'id' },
  { name: 'synthetic_stimulus_specs', select: '*', key: 'id' },
  { name: 'synthetic_assets', select: '*', key: 'id' },
  { name: 'synthetic_qc_events', select: '*', key: 'id' },
  { name: 'synthetic_pairs', select: '*', key: 'id' },
  { name: 'synthetic_calibration_responses', select: '*', key: 'id' },
];

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

async function rest(table, { method = 'GET', select = '*', body } = {}) {
  const query = method === 'GET' ? `?select=${encodeURIComponent(select)}` : '';
  const response = await fetch(`${supabaseUrl}/rest/v1/${table}${query}`, {
    method,
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
      ...(body ? { 'Content-Type': 'application/json', Prefer: 'return=minimal' } : {}),
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

function ordered(rows, key) {
  return [...rows].sort((left, right) => String(left[key]).localeCompare(String(right[key])));
}

async function snapshot() {
  const tables = {};
  for (const definition of tableDefinitions) {
    const result = await rest(definition.name, { select: definition.select });
    assert.equal(
      result.response.status,
      200,
      `backup read failed for ${definition.name}: ${JSON.stringify(result.payload)}`,
    );
    assert.ok(Array.isArray(result.payload));
    tables[definition.name] = ordered(result.payload, definition.key);
  }
  return {
    format: 'mosaic-science-evidence-backup-v1',
    account_linkage: 'detached',
    tables,
  };
}

async function waitForPostgrest() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const result = await rest('science_subjects', {
        select: 'subject_id',
      });
      if (result.response.status === 200) {
        return;
      }
    } catch {
      // The local API can briefly refuse connections while db reset finishes.
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  assert.fail('PostgREST did not become ready after destructive database reset.');
}

async function insertRows(table, rows) {
  const chunkSize = 20;
  for (let start = 0; start < rows.length; start += chunkSize) {
    const chunk = rows.slice(start, start + chunkSize);
    if (chunk.length === 0) {
      continue;
    }
    const result = await rest(table, { method: 'POST', body: chunk });
    assert.ok(
      result.response.status === 201 || result.response.status === 204,
      `restore insert failed for ${table}: ${JSON.stringify(result.payload)}`,
    );
  }
}

const before = await snapshot();
const requiredTables = [
  'calibration_responses',
  'measurement_responses',
  'measurement_score_runs',
  'synthetic_calibration_responses',
];
for (const table of requiredTables) {
  assert.ok(before.tables[table].length > 0, `${table} was empty before the recovery drill`);
}

const beforeCanonical = stableStringify(before);
const beforeFingerprint = sha256(beforeCanonical);
writeFileSync(backupPath, `${beforeCanonical}\n`, { mode: 0o600 });

const reset = spawnSync('npx', ['supabase', 'db', 'reset'], {
  encoding: 'utf8',
  stdio: ['ignore', 'pipe', 'pipe'],
});
if (reset.status !== 0) {
  process.stderr.write(reset.stdout ?? '');
  process.stderr.write(reset.stderr ?? '');
}
assert.equal(reset.status, 0, 'destructive migration-backed database reset failed');
await waitForPostgrest();

const empty = await snapshot();
for (const table of requiredTables) {
  assert.equal(empty.tables[table].length, 0, `${table} unexpectedly survived db reset`);
}

for (const definition of tableDefinitions) {
  await insertRows(definition.name, before.tables[definition.name]);
}

const after = await snapshot();
const afterFingerprint = sha256(stableStringify(after));
assert.equal(
  afterFingerprint,
  beforeFingerprint,
  'restored science evidence does not exactly match the detached backup fingerprint',
);

for (const definition of tableDefinitions) {
  assert.equal(
    after.tables[definition.name].length,
    before.tables[definition.name].length,
    `${definition.name} row count changed across recovery`,
  );
}

console.log(
  JSON.stringify(
    {
      event: 'phase7_science_recovery_gate',
      backup_path: backupPath,
      fingerprint: beforeFingerprint,
      account_linkage: 'detached',
      row_counts: Object.fromEntries(
        tableDefinitions.map(({ name }) => [name, after.tables[name].length]),
      ),
    },
    null,
    2,
  ),
);
