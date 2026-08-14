# ADR 0002 — Supabase authentication and private profile boundary

## Status
Accepted for Phase 2.

## Decision

1. `auth.users` is the authentication identity source; Mosaic application state is stored separately in `public.profiles`.
2. `public.profiles` is one-to-one with `auth.users` through `profiles.user_id`.
3. Profile rows are private by default. RLS permits authenticated users to select, insert, and update only their own row.
4. Client SQL privileges are narrower than table-wide write access: users may insert identity/lifecycle fields and update lifecycle state, while timestamps and revision metadata remain database-owned.
5. The Expo client uses a publishable key (or the local CLI anon key) plus the user's JWT. Secret/service-role credentials are forbidden from the mobile bundle.
6. Schema truth is migration history in `supabase/migrations/`; hosted-dashboard edits must be captured as migrations before they become part of Mosaic's reproducible state.
7. Supabase CLI is pinned because the project depends on deterministic migration, seed, and local-service behavior.

## Consequences

- A clean clone plus Docker and `npm ci` can reconstruct the Phase 2 database with `supabase db reset`.
- Security is testable without privileged application code: integration tests use ordinary authenticated user JWTs and verify cross-user isolation.
- Future public matchmaking/profile projections must be introduced as explicit schemas/views/policies rather than weakening the private profile table.
