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

Phase 3 merged via PR #5 (`9674b5981b2abdbe42055e7ddb51c2777fb540d9`).

---

# Phase 4 — First End-to-End Vertical Slice — COMPLETE

## Objective
Prove the authenticated mobile → API → persistent-data architecture before adding questionnaires, synthetic images, or matching intelligence.

## Implemented
- Supabase access tokens are validated by the FastAPI engine before calibration access.
- Authentication identity is mapped server-side to a separate pseudonymous `science_subjects.subject_id`.
- The engine, not the mobile client, is authoritative for calibration sessions, authored trials, progress, and evidence ingestion.
- A server-only Supabase credential performs science-table persistence; `anon` and `authenticated` clients have no direct write authority over those tables.
- Versioned `calibration_sessions`, immutable `calibration_trials`, and immutable `calibration_responses` persist the complete experiment history.
- Database triggers reject UPDATE and DELETE on raw trials and responses even through the privileged server role.
- `client_response_id` provides response-ingestion idempotency. Exact retries return a duplicate receipt; conflicting reuse is rejected.
- Repeated `/v1/calibration/next` calls return the same unanswered experiment rather than creating parallel pending trials.
- Client-owned progress counters were removed from the API contract. Persisted server evidence determines the next ordinal.
- The Expo client has a real authenticated calibration route using only generated TypeScript API contracts.
- The Phase 4 instrument is a deterministic 10-trial text-pair protocol with `left`, `right`, `both`, and `neither` responses. It is infrastructure scaffolding, not a validated relationship instrument.
- ADR 0004 records the server-authoritative persistence boundary; `docs/protocols/phase4-calibration-vertical-slice.md` records the replayable test protocol.
- Permanent Phase 4 CI is read-only, installs frozen dependency graphs, rebuilds Supabase from migrations, regenerates API contracts, validates the mobile client, bundles all Expo platforms, starts the real FastAPI process, executes the authenticated ten-trial protocol, and rejects dependency/generated-contract drift.

## Exit criteria — satisfied
A clean GitHub runner proves:

```text
authenticated user
        ↓
server creates pseudonymous science subject + session
        ↓
10 sequential authored trials
        ↓
exact retry remains idempotent
        ↓
re-authenticate after trial 5
        ↓
resume same server-owned session at trial 6
        ↓
complete trial 10
        ↓
reconstruct 10 trials + 10 responses from PostgreSQL
        ↓
direct authenticated-client science write rejected
        ↓
trial/response mutation probes rejected
        ↓
OpenAPI/TypeScript/lock artifacts remain zero-diff
```

On the permanent Phase 4 head, the Phase 1 mobile, Phase 2 Supabase/Auth/RLS, Phase 3 engine/contracts, and Phase 4 vertical-slice workflows all pass together.

Phase 4 merged via PR #6 (`d3e6c5579e88ed1c1f1b33bb3551f2935c228f3f`).

---

# Phase 5 — Onboarding and Measurement Infrastructure — COMPLETE

## Objective
Build the general measurement machinery required by Mosaic without yet claiming psychometric validity.

## Implemented
- A separate generic measurement ledger reuses the pseudonymous science-subject boundary without conflating onboarding measurement with Phase 4 attraction-calibration evidence.
- The deterministic mock instrument contains exactly 20 versioned items: 5 hard constraints, 5 rating/adaptive-question items, 5 scenarios, and 5 forced-choice items.
- `measurement_sessions` stores server-owned instrument state and completion status.
- `measurement_presentations` immutably stores presentation order, item ID/version/kind, selection-policy version, and the exact authored item payload required for replay.
- `measurement_responses` immutably stores typed raw answers, instrument and selection-policy provenance, idempotency UUIDs, and client/server timestamps.
- `measurement_score_runs` is append-only derived state. Every run stores its scoring implementation version, response count, score payload, and SHA-256 evidence fingerprint.
- Evidence fingerprints bind to the exact authored item payload, item/instrument/selection versions, and raw answer used for scoring rather than only high-level item IDs.
- Two deliberately different mock scoring implementations prove that the same immutable evidence can be rescored into different versioned derived outputs without rewriting history.
- Repeated next-item requests return the same unanswered presentation; exact response retries are idempotent and conflicting idempotency-key reuse is rejected.
- The authenticated Expo onboarding route renders all four item families from generated TypeScript contracts and resumes entirely from server state.
- ADR 0005 records the raw-evidence/derived-state separation; `docs/protocols/phase5-measurement-infrastructure.md` records the replayable 20-item protocol.
- Permanent Phase 5 CI is read-only, installs frozen dependency graphs, rebuilds Supabase from migrations, reruns P4, executes the P5 protocol against the real FastAPI process, bundles all Expo targets, and rejects dependency/generated-contract drift.

## Data invariant
Raw measurement evidence and derived scores are different persistence classes. A new scoring implementation creates a new score run over the same immutable evidence; it never updates historical presentations or responses.

## Exit criteria — satisfied
A clean GitHub runner proves:

```text
authenticated user
        ↓
server creates versioned measurement session
        ↓
20 heterogeneous authored items
        ↓
exact retries remain idempotent
        ↓
re-authenticate after item 10
        ↓
resume same server-owned session at item 11
        ↓
complete item 20
        ↓
reconstruct 20 presentations + 20 raw responses
        ↓
score immutable evidence with scoring version 1
        ↓
rescore identical evidence with scoring version 2
        ↓
same evidence fingerprint / different versioned derived output
        ↓
raw response serialization remains unchanged
        ↓
direct authenticated-client science write rejected
        ↓
presentation/response/score-provenance mutation rejected
```

On the permanent Phase 5 code head, the Phase 1 mobile, Phase 2 Supabase/Auth/RLS, Phase 3 engine/contracts, Phase 4 vertical-slice, and Phase 5 measurement workflows all pass together.

Phase 5 merged via PR #7 (`1623f7a13def648aa034ee6d946645179e65468f`).

---

# Phase 6 — Synthetic Calibration Infrastructure — ACTIVE

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
