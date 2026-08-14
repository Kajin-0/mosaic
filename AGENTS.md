# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current development stage

Preliminary infrastructure. Do not prematurely implement sophisticated matchmaking, psychometric, Bayesian, or synthetic-generation models until the infrastructure roadmap's vertical integration checkpoints exist.

## Required reading before substantial work

1. `README.md`
2. `docs/ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. Relevant ADRs and protocol documents added later.

## Architectural invariants

- Mobile client: React Native + Expo + TypeScript.
- Database/auth/storage foundation: Supabase/PostgreSQL unless an ADR explicitly changes this.
- Scientific/application engine: Python + FastAPI.
- The repository is initially a monorepo.
- Scientific logic is server-authoritative; do not duplicate it in the mobile app.
- Raw experimental responses are immutable evidence.
- Derived scores/posteriors/predictions are versioned separately from raw evidence.
- Database schema changes must be migration-backed.
- Every scientifically meaningful experiment or prediction must retain provenance sufficient for audit/reconstruction.
- Service-role or otherwise privileged credentials must never enter the mobile bundle or repository.

## Working method

For each significant change:

1. Identify the roadmap phase and exit criterion the change serves.
2. Prefer the smallest vertical improvement that can be tested.
3. Add or update tests with behavior changes.
4. Update architecture/protocol documentation when assumptions change.
5. Record failed approaches when they reveal a meaningful constraint or design decision.
6. Do not silently change model semantics or stored-data semantics.

## Handoff requirement

Before handing the project to another agent/developer after substantial work, leave the repository in a state where the next person can determine:

- what was attempted;
- what is currently working;
- what failed and why;
- the current branch/PR state;
- the next roadmap checkpoint;
- any unresolved scientific or infrastructure assumptions.

Use repository documentation, commits, PR descriptions, and issues as the durable record rather than relying on chat context.
