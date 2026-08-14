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

# Phase 0 — Repository Foundation

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

# Phase 1 — Mobile Development Shell

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
- App boots on at least one Android and one iOS-compatible development target before Phase 1 closes.
- Navigation smoke test covers launch → auth → onboarding → home.

## Exit artifact
A deliberately boring mobile shell that is stable enough to receive real features.

---

# Phase 2 — Reproducible Data and Authentication Layer

## Objective
Create a version-controlled local Supabase/PostgreSQL environment before using a hosted database as the source of schema truth.

## Implementation
- Initialize `supabase/` with Supabase CLI.
- Track all schema changes as migrations.
- Add deterministic seed data for development.
- Configure authentication.
- Create the minimum identity/profile schema only:
  - user/account linkage
  - profile lifecycle state
  - timestamps/versioning
- Enable Row Level Security from the beginning.
- Connect Expo client to local/hosted Supabase through environment configuration.

## Security invariants
- Service-role credentials never ship in the mobile bundle.
- Client access uses publishable/anon credentials plus RLS.
- Private user rows are inaccessible to other users unless an explicit policy permits them.
- `.env*` secrets remain ignored; `.env.example` documents required variables.

## Exit criteria
Automated integration test demonstrates:

```text
create authenticated test user
        ↓
create/read own profile
        ↓
attempt cross-user private read
        ↓
request rejected by policy
```

Database can be recreated from migrations + seed data on a clean machine.

---

# Phase 3 — Science Engine Skeleton and API Contract

## Objective
Establish the boundary around Mosaic's scientific algorithms before implementing those algorithms.

## Implementation
- Create `services/engine` using Python + FastAPI.
- Add typed configuration and structured logging.
- Minimum endpoints:
  - `GET /health`
  - `GET /version`
  - `POST /v1/calibration/next`
  - `POST /v1/calibration/response`
  - `POST /v1/matches/rank`
- Calibration and matching endpoints initially return deterministic mock results.
- Define request/response schemas independently from model implementation.
- Generate or maintain TypeScript contracts used by the mobile client.
- Add API versioning from day one.

## Design invariant
The mobile application never imports or reimplements scientific equations. It consumes stable API contracts.

## Exit criteria
A contract test verifies that the TypeScript-facing API schema and FastAPI schema agree.

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
- Python lint/type checks
- Python tests
- API contract test
- migration validation
- secret scanning where practical

## Operational instrumentation
- structured server logs
- request/correlation IDs
- API latency metrics
- error-rate metrics
- database migration/version visibility
- model/policy version in every scientific response

## Initial service-level engineering targets
These are development targets, not user-facing guarantees:
- API health endpoint availability measurable continuously in deployed environments.
- p95 non-generation API response latency target <500 ms for simple endpoints.
- experiment response ingestion idempotent under retry.
- all production schema changes migration-backed.

## Exit criteria
A deliberately induced API failure, database migration failure, and duplicate client request are each detected and handled predictably.

---

# Phase 8 — Internal Alpha Infrastructure Complete

## Objective
Declare the preliminary platform ready for actual Mosaic algorithm development.

## Alpha vertical slice
A test user can:
1. create an account;
2. create a profile;
3. complete hard constraints;
4. complete a mock adaptive questionnaire;
5. complete synthetic preference calibration;
6. receive deterministic/mock candidate rankings;
7. close and reopen the app without losing state.

## Infrastructure completion criteria
- Fresh-clone setup is documented and reproducible.
- Mobile, database, and engine test suites run in CI.
- Historical experiment/model versions are preserved.
- Security boundaries have automated tests.
- Synthetic experiment provenance is auditable.
- No core Mosaic algorithm is duplicated in the client.

Only after this point should we begin replacing deterministic placeholders with the Bayesian preference, psychometric, compatibility, and matching models.

---

# Sequencing Rule

Do not build chat, payments, global matching, notifications, recommendation ML, or longitudinal relationship tracking during this infrastructure program unless a vertical-slice requirement proves the underlying infrastructure first needs them.

The immediate sequence is:

```text
Phase 0
  ↓
Phase 1
  ↓
Phase 2
  ↓
Phase 3
  ↓
Phase 4  ← first hard integration checkpoint
  ↓
Phases 5–7
  ↓
Phase 8 internal alpha
  ↓
algorithm research/implementation
```
