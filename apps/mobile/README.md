# Mosaic Mobile

Phase 1 mobile shell for Mosaic.

## Stack

- Expo SDK 57
- React Native 0.86
- React 19.2
- Expo Router
- TypeScript

## Commands

From the repository root:

```bash
npm install
npm run mobile:start
npm run mobile:check
```

Or from `apps/mobile`:

```bash
npm run start
npm run typecheck
npm run lint
npm run test
```

## Phase 1 route contract

```text
/ -> /auth -> /onboarding -> /home
```

Authentication, persistence, and matching are intentionally placeholders. Phase 2 replaces the local test-session boundary with Supabase Auth and persisted profile state.
