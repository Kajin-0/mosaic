# Mosaic

**Working codename:** Mosaic

Mosaic is an experimental mobile matchmaking system being developed around the objective of identifying mutually promising long-term relationships rather than maximizing swipe or engagement metrics.

## Infrastructure status

- Phase 0: repository foundation — complete
- Phase 1: Expo/React Native mobile shell — complete
- Phase 2: Supabase/PostgreSQL authentication + private profile/RLS foundation — complete
- Phase 3: FastAPI science-engine skeleton + generated versioned API contracts — complete
- Phase 4: authenticated mobile → engine → PostgreSQL calibration vertical slice — complete
- Phase 5: onboarding and measurement infrastructure — complete
- Phase 6: replayable synthetic calibration infrastructure — complete
- Phase 7: CI, security, observability, and recovery — complete
- Phase 8: infrastructure-complete internal alpha — active

Phase 7 consolidated the earlier phase-specific CI into one read-only repository-wide gate. Every pull request now reconstructs the database from migrations, verifies RLS/authentication, runs mobile and engine checks including mypy, regenerates API contracts, replays Phases 4–6, scans for secrets, enforces the internal-alpha latency budget, executes a destructive detached science-evidence recovery drill, and rejects dependency/generated-contract drift.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the phased implementation plan and exit criteria.

## Repository layout

```text
apps/mobile/          Expo / React Native / TypeScript client
services/engine/      Python / FastAPI server-authoritative engine
packages/contracts/   OpenAPI artifact + generated TypeScript API contracts
supabase/             migrations, seed data, local configuration
scripts/              development and integration utilities
docs/                 architecture, ADRs, protocols, operations, and roadmap
```
