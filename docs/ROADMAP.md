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
- Phase 2 introduced read-only CI using `npm ci`, full local database reset, RLS integration testing, mobile checks, and all-platform Expo export. These guarantees are now subsumed by the Phase 7 repository-wide gate.

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
- Phase 3 introduced frozen Python dependencies, Python lint/format/tests, OpenAPI regeneration, TypeScript generation/typecheck, contract-surface validation, and zero-diff generated-contract enforcement. These guarantees are now subsumed by the Phase 7 repository-wide gate.

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
- Phase 4 introduced a live authenticated ten-trial CI replay and science-record mutation probes. These guarantees are now subsumed by the Phase 7 repository-wide gate.

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

On the Phase 4 release head, the Phase 1 mobile, Phase 2 Supabase/Auth/RLS, Phase 3 engine/contracts, and Phase 4 vertical-slice workflows passed together.

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
- Phase 5 introduced the persistent heterogeneous measurement replay and immutable rescoring gate. These guarantees are now subsumed by the Phase 7 repository-wide gate.

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

On the Phase 5 release head, the Phase 1 mobile, Phase 2 Supabase/Auth/RLS, Phase 3 engine/contracts, Phase 4 vertical-slice, and Phase 5 measurement workflows passed together.

Phase 5 merged via PR #7 (`1623f7a13def648aa034ee6d946645179e65468f`).

---

# Phase 6 — Synthetic Calibration Infrastructure — COMPLETE

## Objective
Create the experiment platform for controlled synthetic attraction calibration before optimizing its inference mathematics.

## Implemented
- A provider-independent `SyntheticGeneratorAdapter` boundary separates experimental provenance from any particular image-generation vendor.
- The Phase 6 infrastructure fixture is a deterministic Python-standard-library PNG generator (`deterministic-png-1.0.0`) that produces controlled geometric candidate cards without an external image service.
- Every candidate begins as an immutable versioned stimulus specification containing its control vector, seed, prompt template, and canonical SHA-256 identity.
- Every generated artifact retains the exact PNG bytes through its asset URI, PNG SHA-256 identity, media type, and provider-neutral generation provenance: adapter, provider, model, model revision, seed, resolved prompt, and generation parameters.
- Quality control is append-only adjudication rather than artifact mutation. The active mock QC version records an explicit accepted/rejected event for every generated asset.
- The first mock P6 request provisions a complete 20-pair cache: 40 immutable specifications → 40 deterministic PNGs → 40 QC acceptances → 20 immutable pair assignments.
- Pair assignments persist ordinal, exact left/right asset IDs, deterministic randomization seed, and pair-policy version.
- A/B/Both/Neither responses are immutable, idempotently ingested, ordered from server-owned evidence, and bound to the exact persisted pair that the user saw.
- Repeated `/next` requests return the same unanswered pair rather than authoring parallel pending trials.
- Synthetic sessions preserve instrument, pair-policy, generator-adapter, target-count, and lifecycle provenance. Database triggers reject deletion, completed-session rewrites, and any active-session change other than the legitimate `active → complete` transition.
- Deterministic IDs fail closed: an ID collision is accepted only if the previously persisted immutable payload is byte/content equivalent to the newly computed payload.
- JSON-serialized deterministic stimulus and pair seeds are constrained to `0..9,007,199,254,740,991` (`2^53 - 1`) in Pydantic and PostgreSQL so Python, PostgreSQL, and JavaScript can replay canonical specification hashes without numeric precision loss.
- The authenticated Expo route explicitly identifies the displayed people as synthetic calibration candidates, states that they are not real members, and renders the exact persisted PNG artifacts rather than regenerating or transforming them client-side.
- ADR 0006 records the synthetic-artifact, collision, and cross-runtime canonical-provenance invariants; `docs/protocols/phase6-synthetic-calibration-infrastructure.md` records the replay protocol and scientific non-claims.
- Phase 6 introduced the complete synthetic-artifact replay, session-provenance immutability, and zero-drift gate. These guarantees are now subsumed by the Phase 7 repository-wide gate.

## Scientific invariant
A generated candidate is an experimental artifact, not disposable UI content. Historical interpretation requires the exact specification, generated bytes, generation provenance, QC decision, pair assignment, and user response to remain reconstructable as distinct records.

Phase 6 establishes experiment reproducibility only. The deterministic geometric PNG fixtures do not establish realism, attraction validity, psychometric validity, compatibility, long-term relationship prediction, or adaptive-query efficiency.

## Exit criteria — satisfied
A clean GitHub runner proves:

```text
authenticated user
        ↓
server creates versioned P6 session
        ↓
pre-provision complete 20-pair cache
        ↓
40 immutable specs → 40 PNG assets → 40 QC acceptances
        ↓
20 immutable randomized pair assignments
        ↓
exact retry remains idempotent
        ↓
re-authenticate after pair 10
        ↓
resume same server-owned session at pair 11
        ↓
complete pair 20
        ↓
reconstruct 40 specs + 40 assets + 40 QC events + 20 pairs + 20 responses
        ↓
recompute canonical specification SHA-256 identities
        ↓
recompute exact PNG SHA-256 identities
        ↓
stored pair sequence exactly equals API-presented sequence
        ↓
every response resolves to complete immutable experiment metadata
        ↓
direct authenticated-client science write rejected
        ↓
spec/asset/QC/pair/response mutation rejected
        ↓
completed-session provenance rewrite/delete rejected
        ↓
P4/P5 regressions pass
        ↓
OpenAPI/TypeScript/lock artifacts remain zero-diff
```

The exact Phase 6 merge-candidate head `4056784052b09ec7cf85191dbcd0c0d3f6f3cbeb` passed the Phase 1 mobile, Phase 2 Supabase/Auth/RLS, Phase 3 engine/contracts, Phase 4 vertical-slice, Phase 5 measurement, and Phase 6 synthetic-calibration workflows together.

Phase 6 merged via PR #8 (`23071c7ffa876e2cb9bb1945cc45f518fb694cec`).

---

# Phase 7 — CI, Security, Observability, and Recovery — COMPLETE

## Objective
Make failures visible and recovery executable before real users or scientific experiments depend on the system.

## Implemented
- Replaced the six phase-specific workflows with one repository-wide `Phase 7 Operational Hardening` pull-request gate. The replacement was first proven while all P1–P6 workflows still existed, then the old workflows were retired and the consolidated read-only gate passed again by itself.
- CI now runs from frozen npm and uv lockfiles and covers mobile typecheck/lint/tests, Python Ruff, a real mypy static typecheck, pytest, OpenAPI regeneration, generated TypeScript contracts, database migration rebuild, RLS/authentication, all-platform Expo export, P4/P5/P6 live replays, synthetic-session provenance immutability, latency, destructive recovery, and zero drift.
- Added full-history Gitleaks scanning to every pull request. The Phase 7 release candidate scanned the complete Phase 7 change history with no leaks found.
- Added a stable one-way `subject_ref` for science-service observability instead of logging raw account IDs or raw science UUIDs.
- Structured request events include request ID, method/path/status, latency, engine/API/contract versions, and route-relevant policy/model version. Unsafe/unbounded externally supplied request IDs are replaced server-side.
- Unexpected exceptions now emit a versioned `request_failed` event with status 500, latency, request ID, and exception class before propagation.
- Added a pinned mypy gate. Its first diagnostic caught one genuine P6 type-contract weakness: a QC decision persisted as `Literal["accepted", "rejected"]` was locally inferred as generic `str`. The implementation now preserves the literal type at source rather than suppressing the check.
- Added ADR 0007 defining operational controls as part of scientific reproducibility, including pseudonymous observability, latency semantics, recovery boundaries, forward-owned migrations, and secret-incident handling.
- Added `docs/protocols/phase7-operational-hardening.md` and `docs/operations/database-recovery.md` so CI tests and recovery claims have durable operational meaning.

## Latency result

The internal-alpha local runner measures 20 warm-request samples for each of five non-generation operations. On the workflow-retirement validation head:

| Operation | p50 | p95 | max |
|---|---:|---:|---:|
| health | 1.021 ms | 1.593 ms | 1.771 ms |
| version | 0.990 ms | 1.278 ms | 1.647 ms |
| mock ranking | 1.281 ms | 1.783 ms | 3.968 ms |
| cached/pending calibration next | 110.187 ms | 130.837 ms | 134.352 ms |
| cached/pending measurement next | 109.353 ms | 133.259 ms | 134.750 ms |

Across all 100 measured requests:

```text
overall p95 = 130.390 ms < 500 ms target
```

This is an internal CI regression budget, not a hosted-production throughput, concurrency, Internet-latency, or image-generation claim.

## Recovery result

After P4–P6 populated the science database, the Phase 7 gate:

1. canonically snapshotted the detached pseudonymous science graph;
2. computed SHA-256 fingerprint `41c152320e8e713a6585b6f3ff321ec929469204d7aa52e6ac834395098bdd8c`;
3. destructively rebuilt PostgreSQL from migrations and seed data;
4. proved the critical science evidence tables were empty;
5. restored subjects with account linkage intentionally detached plus all P4–P6 evidence in foreign-key order;
6. reproduced the exact same SHA-256 fingerprint and row counts; and
7. reran the two-user RLS test successfully after restoration.

The restored graph contained:

```text
science_subjects                     4
calibration_sessions                 2
calibration_trials                  11
calibration_responses               10
measurement_sessions                 2
measurement_presentations           21
measurement_responses               20
measurement_score_runs               2
synthetic_calibration_sessions       1
synthetic_stimulus_specs            40
synthetic_assets                    40
synthetic_qc_events                 40
synthetic_pairs                     20
synthetic_calibration_responses     20
```

`science_subjects.user_id` is intentionally not part of this detached evidence representation. Full account/platform restoration and scientific-evidence restoration are separate recovery classes.

## Exit criteria — satisfied

The consolidated read-only workflow proves on one clean runner:

```text
frozen dependency graphs
        ↓
full PR-history secret scan
        ↓
Ruff + mypy + pytest
        ↓
OpenAPI/TypeScript regeneration with zero drift
        ↓
mobile checks + Android/iOS/web export
        ↓
full migration-backed database reconstruction
        ↓
two-user auth/RLS isolation
        ↓
P4 replay → P5 replay → P6 replay
        ↓
P6 completed-session provenance immutability
        ↓
100-request p95 latency budget
        ↓
destructive database reset
        ↓
exact detached science-evidence restoration
        ↓
identical SHA-256 recovery fingerprint
        ↓
RLS passes again after recovery
        ↓
no dependency/generated-contract drift
```

The consolidated read-only gate passed after all six phase-specific workflows were removed, proving the repository no longer depends on duplicated phase CI definitions.

---

# Phase 8 — Infrastructure-Complete Internal Alpha — ACTIVE

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
