# Mosaic Preliminary Infrastructure Roadmap

## Purpose

Build the smallest reproducible technical foundation that can support Mosaic's mobile client, persistent data, scientific inference engine, and later synthetic calibration work without prematurely implementing the matchmaking algorithm.

The governing rule is **vertical integration before sophistication**: each phase must produce a runnable, testable increment and satisfy explicit exit criteria before the next phase begins.

---

## Target architecture

```text
apps/mobile/                 React Native + Expo + TypeScript
packages/contracts/          Shared API/data contracts for TypeScript clients
services/engine/             Python + FastAPI scientific/application API
supabase/                    Local database config, migrations, seed data
scripts/                     Development/bootstrap utilities
docs/                        Architecture, decisions, protocols
.github/workflows/           CI
```

The repository begins as a monorepo so application code, schemas, contracts, and model interfaces can change atomically while the architecture is still evolving.

---

# Phase 0 — Repository Foundation — COMPLETE

## Objective
Create a clean, documented repository with explicit boundaries before generating framework code.

## Deliverables
- Root README and codename notice.
- Monorepo directory conventions.
- Root workspace configuration for JavaScript/TypeScript packages.
- Repository-wide `.gitignore` and `.editorconfig`.
- Architecture document and ADRs for major decisions.
- `AGENTS.md` describing project invariants and handoff requirements.
- Development branch/PR workflow.

## Exit criteria
- Fresh clone has an unambiguous directory structure and setup path.
- No secrets or generated artifacts are intended to enter Git.
- Mobile, engine, database, and contracts have explicit ownership boundaries.
- Architectural assumptions are documented rather than implicit.

---

# Phase 1 — Mobile Development Shell — COMPLETE

## Objective
Produce the first runnable iOS/Android client with no Mosaic business logic.

## Implementation
- Scaffold `apps/mobile` using the current supported Expo template.
- TypeScript only.
- Expo Router for navigation.
- Establish development, preview, and production environment configuration.
- Add basic application shell:
  - launch screen
  - placeholder authentication route
  - placeholder onboarding route
  - placeholder home route
- Establish design tokens rather than styling individual screens ad hoc.
- Add unit/component test harness.

## Initial quality gates
- Type checking succeeds with zero errors.
- Lint succeeds with zero errors.
- Unit smoke test succeeds.
- App produces valid Android, iOS, and web bundles in CI.
- Navigation smoke test covers launch → auth → onboarding → home.

## Exit artifact
A deliberately boring mobile shell that is stable enough to receive real features.

---

# Phase 2 — Reproducible Data and Authentication Layer — COMPLETE

## Objective
Create a version-controlled local Supabase/PostgreSQL environment before using a hosted database as the source of schema truth.

## Implemented
- Pinned Supabase CLI and committed dependency lockfile.
- Version-controlled `supabase/config.toml`, migrations, and deterministic seed data.
- Email/password Supabase Auth integration in the Expo client.
- One-to-one private `public.profiles` table linked to `auth.users`.
- Profile lifecycle state plus database-owned timestamps and monotonic revision number.
- Owner-only RLS from initial schema creation.
- Column-scoped client write grants.
- Publishable/anon client-key boundary; no service-role credential in mobile configuration.
- Two-user integration test proving own-row access and cross-user isolation.
- Permanent read-only CI using `npm ci`, full local database reset, RLS integration testing, mobile checks, and all-platform Expo export.

## Exit criteria — satisfied
Automated integration test demonstrates:

```text
create authenticated test user
        ↓
create/read/update own profile
        ↓
attempt cross-user private read/update
        ↓
row remains inaccessible and immutable to the other user
```

Database recreation from migrations + seed data passes on a clean GitHub runner.

Phase 2 merged via PR #4 (`40c5af3dbdbe6ea61f7f74f646be7338612adb58`).

---

# Phase 3 — Science Engine Skeleton and API Contract — COMPLETE

## Objective
Establish the boundary around Mosaic's scientific algorithms before implementing those algorithms.

## Implemented
- Python 3.13 `services/engine` project using FastAPI, Pydantic, Pydantic Settings, Uvicorn, uv, Ruff, and pytest.
- Typed environment configuration and structured JSON request logging with request IDs and latency.
- Explicit version metadata for the engine, API contract, mock calibration policy, and mock ranker.
- Endpoints:
  - `GET /health`
  - `GET /version`
  - `POST /v1/calibration/next`
  - `POST /v1/calibration/response`
  - `POST /v1/matches/rank`
- Deterministic mock calibration and ranking behavior, explicitly marked `is_mock`.
- Pydantic request/response models with strict extra-field rejection and stable operation IDs.
- `packages/contracts` workspace generated from FastAPI's OpenAPI document.
- ADR 0003 establishes FastAPI/OpenAPI as the sole wire-contract authority; TypeScript DTOs are generated rather than independently maintained.
- Committed Python `uv.lock`, npm lockfile update, OpenAPI artifact, and generated TypeScript declarations.
- Permanent read-only CI uses frozen Python dependencies, `npm ci`, Python lint/format/tests, OpenAPI regeneration, TypeScript generation/typecheck, contract-surface validation, and a zero-diff generated-contract gate.

## Design invariant
The mobile application never imports or reimplements scientific equations. It consumes stable generated API contracts. Scientific implementations can later replace deterministic mocks behind that boundary or intentionally revise the contract with an explicit reviewable diff.

## Exit criteria — satisfied
A clean GitHub runner verifies:

```text
locked Python + Node environments
        ↓
FastAPI lint / format / tests
        ↓
OpenAPI regenerated from application
        ↓
TypeScript contract regenerated from OpenAPI
        ↓
TypeScript contract typechecks
        ↓
contract surface test passes
        ↓
generated artifacts have zero diff
```

Authentication/authorization of engine requests and persistence remain deliberately deferred to Phase 4.

Phase 3 implemented in PR #5.

---

# Phase 4 — First End-to-End Vertical Slice

## Objective
Prove the architecture works before adding questionnaires, image generation, or matching intelligence.

## Flow

```text
mobile app
   ↓ authenticated request
science API
   ↓
PostgreSQL/Supabase
   ↓
science API returns deterministic next action
   ↓
mobile renders result
   ↓
user response is persisted
```

## Minimal feature
Use a synthetic text-only calibration item initially. Example:

```text
A / B / Both / Neither
```

No AI image generation yet.

## Required event fields
Every experiment/response must retain:
- immutable experiment ID
- user pseudonymous ID
- stimulus/version ID
- model/policy version
- response
- server timestamp
- client timestamp where useful
- presentation order
- experiment metadata required to reproduce the decision

## Exit criteria
- One authenticated user can complete 10 sequential mock calibration trials.
- Restarting the app does not lose state.
- Duplicate submission is idempotent.
- A complete event history can reconstruct the session.
- No scientific model is needed for the test to pass.

This is the first major infrastructure milestone.

---

# Phase 5 — Onboarding and Measurement Infrastructure

## Objective
Build the general measurement machinery required by Mosaic without yet claiming psychometric validity.

## Implementation
- Hard-constraint forms.
- Generic adaptive-question renderer.
- Scenario renderer.
- Forced-choice renderer.
- Response schema with instrument/version provenance.
- Server-side session state.
- Deterministic baseline question-selection policy.
- Resume interrupted onboarding.

## Data principle
Never store only a derived score. Preserve the raw response, exact instrument version, scoring/model version, and resulting posterior/derived state separately.

## Exit criteria
- A versioned mock 20-item instrument can be completed, interrupted, resumed, and rescored.
- Changing the scoring implementation does not mutate historical raw data.

---

# Phase 6 — Synthetic Calibration Infrastructure

## Objective
Create the experiment platform for controlled synthetic attraction calibration before optimizing its inference mathematics.

## Components
- Synthetic-stimulus specification schema.
- Generator adapter interface independent of any specific AI provider.
- Asset storage and immutable stimulus IDs.
- Pair construction and randomization.
- A/B/Both/Neither response interface.
- Generation provenance and prompt/model metadata.
- Quality-control/rejection state for unusable stimuli.
- Pre-generation/cache mechanism so generation latency is outside the user's interaction loop where possible.

## Scientific invariant
A generated stimulus is an experimental artifact. Its generation specification and provenance must be immutable enough to reproduce or audit the trial.

## Initial performance targets
- Cached next comparison displayed in <300 ms at the client after response acknowledgement under normal network conditions.
- Zero missing stimulus/version references in accepted responses.
- 100% of recorded responses trace to immutable experiment metadata.

## Exit criteria
A user can complete a 20-trial synthetic calibration session and the entire experiment can be replayed from stored metadata.

---

# Phase 7 — CI, Security, Observability, and Recovery

## Objective
Make failures visible before real users or scientific experiments depend on the system.

## CI gates
For every pull request:
- TypeScript typecheck
- JavaScript/TypeScript lint
- mobile tests
- Python lint/typecheck/tests
- API contract tests
- database migration tests
- RLS/security tests
- secret scanning

## Operational requirements
- structured request IDs
- pseudonymous user identifiers in science-service logs
- API version
- model/policy version
- latency/error instrumentation
- database backup/recovery procedure
- migration rollback/forward-fix policy

## Initial API latency target
For ordinary non-generation API operations:

```text
p95 < 500 ms
```

under the internal-alpha load profile.

---

# Phase 8 — Infrastructure-Complete Internal Alpha

## Objective
Demonstrate the entire preliminary platform without requiring production-quality matching science.

## Internal-alpha path

```text
create account
      ↓
create profile
      ↓
set hard constraints
      ↓
complete mock questionnaire
      ↓
complete synthetic calibration
      ↓
receive mock candidate ranking
      ↓
close app
      ↓
return later
      ↓
state remains reconstructable
```

## Completion criteria
- Development setup is reproducible from documentation.
- Mobile, database, engine, and contracts pass CI.
- RLS/security boundary is tested.
- Migrations recreate the database.
- Core experimental records are immutable/versioned.
- No model output is stored without its model/policy version.
- No mobile release contains server credentials.
- The first complete internal-alpha user journey is reproducible.

At that point the infrastructure program is complete and the project can move from deterministic placeholders to the real Mosaic inference models.
