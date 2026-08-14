# Mosaic

**Working codename:** Mosaic

Mosaic is an experimental mobile matchmaking system being developed around the objective of identifying mutually promising long-term relationships rather than maximizing swipe or engagement metrics.

## Infrastructure status

- Phase 0: repository foundation — complete
- Phase 1: Expo/React Native mobile shell — complete
- Phase 2: Supabase/PostgreSQL authentication + private profile/RLS foundation — complete
- Phase 3: FastAPI science-engine skeleton + versioned contracts — next

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the phased implementation plan and exit criteria.

## Repository layout

```text
apps/mobile/          Expo / React Native / TypeScript client
services/engine/      Python / FastAPI science engine (Phase 3)
packages/contracts/   shared API/data contracts (Phase 3)
supabase/             migrations, seed data, local configuration
scripts/              development and integration utilities
docs/                 architecture, ADRs, and roadmap
```
