import { access, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const mobileRoot = path.resolve(import.meta.dirname, '..');
const requiredRoutes = ['_layout.tsx', 'index.tsx', 'auth.tsx', 'onboarding.tsx', 'home.tsx'];

for (const route of requiredRoutes) {
  await access(path.join(mobileRoot, 'app', route));
}

const appConfig = JSON.parse(await readFile(path.join(mobileRoot, 'app.json'), 'utf8'));
const packageJson = JSON.parse(await readFile(path.join(mobileRoot, 'package.json'), 'utf8'));

if (packageJson.main !== 'expo-router/entry') {
  throw new Error('Expo Router entry point is not configured.');
}

if (!appConfig.expo?.plugins?.includes('expo-router')) {
  throw new Error('expo-router plugin is not configured in app.json.');
}

if (appConfig.expo?.experiments?.typedRoutes !== true) {
  throw new Error('Typed Expo Router routes must remain enabled.');
}

console.log('Phase 1 mobile scaffold smoke check passed.');
process.exitCode = 0;
