# Mosaic Supabase

Phase 2 establishes the version-controlled local data/authentication environment.

## Requirements

- Node.js >= 22.13
- Docker-compatible runtime
- repository dependencies installed with `npm ci`

The Supabase CLI is pinned in the root `package.json`; invoke it through npm/npx rather than relying on an unpinned global CLI.

## Local reset

```bash
npm run supabase:start
npm run supabase:reset
npx supabase status -o env
```

`supabase db reset` destroys the local database, reapplies every migration, then applies `seed.sql`. It must remain sufficient to reconstruct the development database from a clean clone.

## Mobile configuration

Copy `apps/mobile/.env.example` to `apps/mobile/.env` and fill in:

- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

For local development, the legacy `ANON_KEY` emitted by `npx supabase status -o env` can be supplied as the client key. Hosted environments should use a current publishable key.

Never place a Supabase secret/service-role key in any `EXPO_PUBLIC_*` variable or mobile source file.
