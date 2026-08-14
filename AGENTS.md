# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current development stage

Phase 8 — infrastructure-complete internal alpha. Phases 0–7 established the repository, mobile shell, authenticated data boundary, science engine/contracts, immutable experimental ledgers, replayable synthetic calibration, and operational hardening.

The next objective is to prove one complete resumable internal-alpha journey using the existing deterministic/mock scientific components. Do not reinterpret those placeholders as validated matchmaking, psychometric, attraction, or relationship-prediction models.

## Required reading before substantial work

1. `README.md`
2. `docs/ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. Relevant ADRs and protocol documents, especially ADRs 0004–0007 for evidence, provenance, and operational invariants.
5. `docs/operations/database-recovery.md` before database or migration work that can affect persistent evidence.

## Architectural invariants

- Mobile client: React Native + Expo + TypeScript.
- Database/auth/storage foundation: Supabase/PostgreSQL unless an ADR explicitly changes this.
- Scientific/application engine: Python + FastAPI.
- The repository is initially a monorepo.
- Scientific logic is server-authoritative; do not duplicate it in the mobile app.
- Raw experimental responses are immutable evidence.
- Derived scores/posteriors/predictions are versioned separately from raw evidence.
- Database schema changes must be migration-backed. Applied migrations are forward-owned history; repair deployed defects with a new migration rather than rewriting an applied migration.
- Every scientifically meaningful experiment or prediction must retain provenance sufficient for audit/reconstruction.
- Service-role or otherwise privileged credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous. Do not introduce raw auth user IDs, bearer tokens, request bodies, raw science UUIDs, experimental answers, or generated artifact bytes into routine request logs.
- The detached science-evidence recovery representation intentionally excludes `science_subjects.user_id`; identity relinking is a separate privileged operation.
- The 500 ms Phase 7 latency threshold is an internal-alpha CI regression budget for ordinary non-generation operations, not a production scalability claim.

## Authoritative CI gate

`.github/workflows/phase7-operational-hardening.yml` is the repository-wide pull-request gate. The former Phase 1–6 workflow files were retired after this consolidated gate reproduced their guarantees.

A normal pull request must preserve:

- frozen npm and uv dependency graphs;
- repository-history secret scanning;
- mobile typecheck/lint/tests and all-platform Expo export;
- Python Ruff + mypy + pytest;
- OpenAPI/TypeScript contract regeneration with zero drift;
- migration-backed database reconstruction;
- authentication/RLS isolation;
- live Phase 4, 5, and 6 replay protocols;
- Phase 6 session-provenance immutability;
- Phase 7 latency regression budget;
- destructive detached science-evidence recovery plus post-restore RLS validation; and
- zero dependency/generated-contract drift.

Do not weaken or bypass a gate merely to make CI green. Treat failures as evidence about the implementation or contract until proven otherwise.

## Working method

For each significant change:

1. Identify the roadmap phase and exit criterion the change serves.
2. Prefer the smallest vertical improvement that can be tested.
3. Add or update tests with behavior changes.
4. Update architecture/protocol documentation when assumptions change.
5. Record failed approaches when they reveal a meaningful constraint or design decision.
6. Do not silently change model semantics or stored-data semantics.
7. Require the authoritative read-only gate to pass on the exact intended merge head.

## Handoff requirement

Before handing the project to another agent/developer after substantial work, leave the repository in a state where the next person can determine:

- what was attempted;
- what is currently working;
- what failed and why;
- the current branch/PR state;
- the next roadmap checkpoint;
- any unresolved scientific or infrastructure assumptions.

Use repository documentation, commits, PR descriptions, issues, and CI records as the durable record rather than relying on chat context.
