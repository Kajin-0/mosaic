# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current development stage

**Preliminary infrastructure program complete (Phases 0–8).**

The repository now has a reproducible mobile/database/engine/contracts stack, immutable experimental ledgers, replayable synthetic-calibration artifacts, versioned derived-state persistence, operational hardening, destructive recovery validation, and a complete resumable internal-alpha journey.

The next development stage is the real Mosaic inference/model program. Do not reinterpret any existing deterministic questionnaire, synthetic PNG, candidate, score, or ranking fixture as a validated matchmaking, psychometric, attraction, compatibility, or relationship-prediction model.

## Required reading before substantial work

1. `README.md`
2. `docs/ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. ADRs 0004–0008, especially the raw-evidence/derived-state, synthetic-provenance, operational-recovery, and persisted-ranking boundaries.
5. `docs/protocols/phase8-internal-alpha.md` for the complete application replay.
6. `docs/operations/database-recovery.md` before database or migration work that can affect persistent scientific state.

## Architectural invariants

- Mobile client: React Native + Expo + TypeScript.
- Database/auth/storage foundation: Supabase/PostgreSQL unless an ADR explicitly changes this.
- Scientific/application engine: Python + FastAPI.
- The repository is a monorepo unless an ADR explicitly changes that decision.
- Scientific logic is server-authoritative; do not duplicate model equations or decision semantics in the mobile app.
- Raw experimental responses are immutable evidence.
- Derived scores, posteriors, predictions, and ranking outputs are separate versioned persistence classes; they must never overwrite raw evidence.
- A scientifically meaningful output must retain the implementation/model/policy version and enough input/provenance information for audit and reconstruction.
- Database schema changes must be migration-backed. Applied migrations are forward-owned history; repair deployed defects with a new migration rather than rewriting an applied migration.
- Service-role or otherwise privileged credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous. Do not introduce raw auth user IDs, bearer tokens, request bodies, raw science UUIDs, experimental answers, or generated artifact bytes into routine request logs.
- Detached `mosaic-science-state-backup-v2` recovery intentionally excludes `science_subjects.user_id`; identity relinking is a separate privileged operation.
- The 500 ms latency threshold is an internal-alpha CI regression budget for ordinary local non-generation operations, not a production scalability claim.
- Existing deterministic fixtures are infrastructure test inputs. Replacing them with real scientific models requires explicit model versioning, tests, documentation, and validation; passing infrastructure CI is not evidence of scientific validity.

## Authoritative CI gate

`.github/workflows/phase7-operational-hardening.yml` remains the repository-wide read-only pull-request gate. Its name is retained for check/branch-protection continuity even though it now validates the completed Phase 8 application journey as well.

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
- the complete Phase 8 signup → measurement → synthetic calibration → persisted ranking → fresh sign-in → reconstruction journey;
- the authenticated persisted-ranking latency regression budget;
- destructive detached science-state recovery, including versioned derived ranking state, plus post-restore RLS validation; and
- zero dependency/generated-contract drift.

Do not weaken or bypass a gate merely to make CI green. Treat failures as evidence about the implementation, contract, or model until proven otherwise.

## Scientific development method

For each substantive model change:

1. State the scientific quantity being inferred or predicted.
2. Separate population priors from individual evidence.
3. Identify what is raw observation, what is latent state, what is derived output, and what is a downstream decision.
4. State identifiability assumptions and uncertainty explicitly.
5. Version the implementation/model/policy semantics before persisting output.
6. Add synthetic/unit tests for mathematical invariants and live integration tests for persistence/provenance boundaries.
7. Update ADR/protocol documentation when assumptions or stored semantics change.
8. Record failed approaches when they reveal a meaningful scientific or architectural constraint.
9. Never silently change historical evidence or reinterpret a stored model output under new semantics.
10. Require the authoritative read-only gate to pass on the exact intended merge head.

## Handoff requirement

Before handing the project to another agent/developer after substantial work, leave the repository in a state where the next person can determine:

- what scientific or infrastructure question was attempted;
- what is currently working;
- what failed and why;
- the current branch/PR state;
- the next scientific checkpoint;
- the model/version/provenance assumptions currently active; and
- any unresolved identifiability, validation, or architectural assumptions.

Use repository documentation, commits, PR descriptions, issues, and CI records as the durable record rather than relying on chat context.
