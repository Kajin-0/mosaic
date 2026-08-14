# Mosaic

**Working codename:** Mosaic

Mosaic is an experimental mobile matchmaking system being developed around the objective of identifying mutually promising long-term relationships rather than maximizing swipe or engagement metrics.

## Infrastructure status

The preliminary infrastructure program is complete:

- Phase 0: repository foundation — complete
- Phase 1: Expo/React Native mobile shell — complete
- Phase 2: Supabase/PostgreSQL authentication + private profile/RLS foundation — complete
- Phase 3: FastAPI science-engine skeleton + generated versioned API contracts — complete
- Phase 4: authenticated mobile → engine → PostgreSQL calibration vertical slice — complete
- Phase 5: onboarding and measurement infrastructure — complete
- Phase 6: replayable synthetic calibration infrastructure — complete
- Phase 7: CI, security, observability, and recovery — complete
- Phase 8: complete resumable internal-alpha journey — complete

The permanent read-only pull-request gate reconstructs the database from migrations, verifies authentication/RLS, runs engine and mobile checks, regenerates API contracts, replays Phases 4–6 plus the complete Phase 8 journey, scans repository history for secrets, enforces the local internal-alpha latency budget, executes destructive detached science-state recovery, revalidates RLS after restoration, and rejects dependency/generated-contract drift.

Phase 8 also makes mock ranking authenticated, append-only, versioned derived state. This is an infrastructure guarantee only. The questionnaire, synthetic stimuli, candidate IDs, scores, and rankings remain deterministic fixtures and carry no claim of psychometric, attraction, compatibility, matchmaking, or long-term relationship validity.

The next project stage is development and validation of the real Mosaic inference models behind these established boundaries.

See [`docs/ROADMAP.md`](docs/ROADMAP.md), ADR 0008, and [`docs/protocols/phase8-internal-alpha.md`](docs/protocols/phase8-internal-alpha.md).

## Repository layout

```text
apps/mobile/          Expo / React Native / TypeScript client
services/engine/      Python / FastAPI server-authoritative engine
packages/contracts/   OpenAPI artifact + generated TypeScript API contracts
supabase/             migrations, seed data, local configuration
scripts/              development, replay, security, latency, and recovery utilities
docs/                 architecture, ADRs, protocols, operations, and completed roadmap
```
