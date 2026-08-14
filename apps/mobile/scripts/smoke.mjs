import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const routeFiles = ['app/index.tsx', 'app/auth.tsx', 'app/onboarding.tsx', 'app/home.tsx', 'app/calibration.tsx'];

for (const routeFile of routeFiles) {
  const source = await readFile(new URL(`../${routeFile}`, import.meta.url), 'utf8');
  assert.match(source, /export default function/, `${routeFile} must export a route component`);
}

const packageJson = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));
assert.equal(packageJson.main, 'expo-router/entry');
assert.equal(packageJson.dependencies['@supabase/supabase-js'], '2.112.3');
assert.equal(packageJson.dependencies['@react-native-async-storage/async-storage'], '2.2.0');
assert.equal(packageJson.dependencies['@mosaic/contracts'], '0.1.0');
assert.equal(packageJson.dependencies['expo-crypto'], '~57.0.1');

const appJson = JSON.parse(await readFile(new URL('../app.json', import.meta.url), 'utf8'));
assert.ok(appJson.expo.plugins.includes('expo-router'));
assert.equal(appJson.expo.experiments.typedRoutes, true);

const layout = await readFile(new URL('../app/_layout.tsx', import.meta.url), 'utf8');
assert.match(layout, /AuthProvider/, 'root layout must establish the authentication provider boundary');

const authProvider = await readFile(new URL('../src/providers/AuthProvider.tsx', import.meta.url), 'utf8');
assert.match(authProvider, /profiles/, 'auth provider must hydrate the private profile row');

const calibration = await readFile(new URL('../app/calibration.tsx', import.meta.url), 'utf8');
assert.match(calibration, /getNextCalibrationTrial/);
assert.match(calibration, /submitCalibrationResponse/);
assert.match(calibration, /Crypto\.randomUUID/);

const envExample = await readFile(new URL('../.env.example', import.meta.url), 'utf8');
assert.match(envExample, /EXPO_PUBLIC_SUPABASE_URL/);
assert.match(envExample, /EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY/);
assert.match(envExample, /EXPO_PUBLIC_MOSAIC_ENGINE_URL/);
assert.doesNotMatch(envExample, /SERVICE_ROLE|SERVER_KEY|SECRET_KEY/i, 'mobile env example must not contain privileged credentials');

console.log('Mosaic mobile Phase 4 scaffold smoke test passed.');
