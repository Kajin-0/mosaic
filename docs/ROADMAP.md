# Mosaic Preliminary Infrastructure Roadmap

## Status

**Phases 0–8 complete.**

The preliminary infrastructure program is finished when the Phase 8 release head passes the repository-wide read-only operational gate and merges. The next project stage is scientific/model development behind the infrastructure boundaries established here; deterministic fixtures must not be relabeled as validated Mosaic inference.

## Governing principle

The infrastructure program followed:

```text
vertical integration before sophistication
```

Each phase established one reproducible boundary before the project attempted more complex behavior.

## Target architecture established

```text
apps/mobile/                 React Native + Expo + TypeScript client
packages/contracts/          OpenAPI-derived TypeScript wire contracts
services/engine/             Python + FastAPI server-authoritative engine
supabase/                    PostgreSQL migrations, seed data, local config
scripts/                     replay, security, latency, and recovery tests
docs/                        architecture, ADRs, protocols, operations
.github/workflows/           one repository-wide read-only CI gate
```

---

# Phase 0 — Repository Foundation — COMPLETE

## Purpose
Create explicit repository boundaries and durable handoff documentation before framework implementation.

## Durable result
- Monorepo structure and ownership boundaries established.
- Repository-wide ignore/editor conventions established.
- Architecture, ADR, protocol, and agent-handoff conventions established.
- Secrets and generated build artifacts are not intended to enter Git.

Phase 0 merged via PR #1.

---

# Phase 1 — Mobile Development Shell — COMPLETE

## Purpose
Establish a runnable React Native/Expo/TypeScript application without Mosaic business logic.

## Durable result
- Expo Router mobile shell.
- Environment separation and design tokens.
- Typecheck, lint, smoke-test, and Android/iOS/web export capability.

Phase 1 merged via PR #3.

---

# Phase 2 — Reproducible Data and Authentication — COMPLETE

## Purpose
Make the database/authentication boundary reproducible from version-controlled migrations before hosted state becomes authoritative.

## Durable invariant
An authenticated account can access its own private profile but cannot read or modify another user's profile. The mobile client never contains a service-role credential.

## Validation
A clean runner recreates Supabase/PostgreSQL from migrations and proves two-user RLS isolation.

Phase 2 merged via PR #4 (`40c5af3dbdbe6ea61f7f74f646be7338612adb58`).

---

# Phase 3 — Science Engine and Generated API Contract — COMPLETE

## Purpose
Establish the boundary around scientific/application algorithms before implementing real inference.

## Durable invariants
- Scientific/application logic is server-authoritative in Python/FastAPI.
- FastAPI/OpenAPI is the sole wire-contract authority.
- TypeScript client contracts are generated, not independently reimplemented.
- Model/policy/API versions are explicit.

## Validation
Frozen Python/Node environments pass Ruff, type checks, tests, OpenAPI regeneration, generated TypeScript checks, and zero-drift enforcement.

Phase 3 merged via PR #5 (`9674b5981b2abdbe42055e7ddb51c2777fb540d9`).

---

# Phase 4 — First End-to-End Calibration Slice — COMPLETE

## Purpose
Prove authenticated mobile → engine → persistent science data before adding more measurement machinery.

## Durable invariants
- Account identity maps server-side to a separate pseudonymous science subject.
- Calibration sessions, authored trials, progress, and response ingestion are server-owned.
- Raw trials/responses are immutable evidence.
- Exact retries are idempotent; conflicting reuse fails closed.
- Direct authenticated-client writes to science tables are denied.

## Validation
The live protocol completes and reconstructs a ten-trial deterministic text-pair calibration session across re-authentication.

See ADR 0004 and `docs/protocols/phase4-calibration-vertical-slice.md`.

Phase 4 merged via PR #6 (`d3e6c5579e88ed1c1f1b33bb3551f2935c228f3f`).

---

# Phase 5 — Onboarding and Measurement Infrastructure — COMPLETE

## Purpose
Build reusable measurement infrastructure without claiming psychometric validity.

## Durable invariant
Raw measurement evidence and derived scores are separate persistence classes. A new scoring implementation creates a new versioned score run over unchanged immutable evidence.

## Validation
The live protocol completes 20 heterogeneous fixture items—five hard constraints, five ratings, five scenarios, and five forced choices—then proves immutable evidence can be rescored under different scoring versions without rewriting history.

See ADR 0005 and `docs/protocols/phase5-measurement-infrastructure.md`.

Phase 5 merged via PR #7 (`1623f7a13def648aa034ee6d946645179e65468f`).

---

# Phase 6 — Synthetic Calibration Infrastructure — COMPLETE

## Purpose
Create a replayable experiment substrate for future controlled synthetic-attraction calibration before optimizing inference mathematics.

## Durable invariants
- A synthetic candidate is an experimental artifact, not disposable UI.
- Exact stimulus specification, generated bytes/hash, provider-neutral generation provenance, QC adjudication, pair assignment, and response are reconstructable as distinct immutable records.
- Deterministic JSON-serialized seeds stay within JavaScript's exact-integer range (`2^53 - 1`) so Python/PostgreSQL/JavaScript reproduce canonical identities.
- Completed-session provenance cannot be rewritten or deleted.

## Validation
The live protocol reconstructs 40 specs → 40 PNG assets → 40 QC events → 20 pair assignments → 20 responses and proves canonical hashes, pair order, resume behavior, and mutation rejection.

This establishes experiment reproducibility only; it does not establish realism or attraction validity.

See ADR 0006 and `docs/protocols/phase6-synthetic-calibration-infrastructure.md`.

Phase 6 merged via PR #8 (`23071c7ffa876e2cb9bb1945cc45f518fb694cec`).

---

# Phase 7 — CI, Security, Observability, and Recovery — COMPLETE

## Purpose
Make regressions, security failures, latency changes, and unrecoverable state review-blocking before real experiments depend on the platform.

## Durable invariants
- One repository-wide pull-request workflow is authoritative and read-only.
- Frozen dependency graphs, history secret scanning, Ruff, mypy, pytest, generated-contract checks, mobile validation, migration reconstruction, RLS, Expo export, live phase replays, latency, recovery, and zero drift run together.
- Routine science telemetry uses stable one-way `subject_ref` values rather than raw account/science identifiers.
- Request events retain engine/API/contract plus route-relevant model/policy versions.
- Unexpected exceptions emit structured failure telemetry before propagation.
- Applied migrations are forward-owned history.
- Full hosted-platform recovery and detached scientific-state recovery are separate recovery classes.

## Original Phase 7 latency record

On the workflow-retirement validation head, the 100-request local non-generation p95 was:

```text
130.390 ms < 500 ms target
```

This is a local CI regression budget, not a production scalability claim.

## Original Phase 7 recovery record

The P4–P6 detached evidence graph was destructively rebuilt/restored with exact fingerprint:

```text
41c152320e8e713a6585b6f3ff321ec929469204d7aa52e6ac834395098bdd8c
```

Phase 8 later extends this recovery representation from evidence-only state to `mosaic-science-state-backup-v2`, which also includes versioned derived ranking outputs.

See ADR 0007, `docs/protocols/phase7-operational-hardening.md`, and `docs/operations/database-recovery.md`.

Phase 7 merged via PR #9 (`1e88393e38151ad7e428ffc824655bc1d00f3d83`).

---

# Phase 8 — Infrastructure-Complete Internal Alpha — COMPLETE

## Purpose
Prove the entire preliminary platform as one resumable application without requiring production-quality matchmaking science.

## Implemented
- `/v1/matches/rank` is now authenticated and server-persisted rather than stateless.
- `match_rank_runs` stores append-only versioned derived output tied to the pseudonymous science subject.
- Ranking provenance includes model version, normalized candidate input, requested limit, canonical SHA-256 request fingerprint, exact ranked output, run ID, and creation time.
- Semantically identical candidate-set requests reuse the same historical run rather than manufacturing duplicate history.
- The mobile app exposes a five-candidate deterministic internal-alpha ranking screen using generated TypeScript contracts.
- Ranking rows participate in detached `mosaic-science-state-backup-v2` recovery.
- The authoritative read-only CI gate now runs the complete P8 journey after P4–P6 and before latency/recovery.

## Internal-alpha path

```text
create account
      ↓
create onboarding profile
      ↓
complete 20-item measurement fixture
      ↓
prove five hard-constraint fixtures were traversed
      ↓
activate profile
      ↓
complete 20-pair synthetic calibration
      ↓
receive and persist five-candidate mock ranking
      ↓
discard original authenticated session
      ↓
sign in again
      ↓
recover active profile
      ↓
recover same completed measurement session
      ↓
recover same completed synthetic session
      ↓
recover same ranking run / fingerprint / output
```

## First complete integrated validation

GitHub Actions run `31836243873` proved the complete journey on the real FastAPI + local Supabase/PostgreSQL stack while P4, P5, P6, P6 provenance immutability, security, contracts, mobile builds, latency, destructive recovery, post-restore RLS, and zero drift also passed.

The authenticated persisted ranking path measured:

```text
ranking p50    97.640 ms
ranking p95   114.124 ms
ranking max   114.623 ms
```

Across all 100 measured operations:

```text
overall p95 = 160.251 ms < 500 ms target
```

The same run destructively recovered two `match_rank_runs` together with the existing experimental graph. The final release head uses the explicit `mosaic-science-state-backup-v2` format and must reproduce its own exact SHA-256 fingerprint before merge.

## Completion criteria — satisfied

The release gate proves:

- development state is reconstructable from committed configuration/documentation;
- mobile, database, engine, and generated contracts pass together;
- RLS/security boundaries remain intact;
- migrations recreate the database;
- raw experimental records remain immutable/versioned;
- derived scores/rankings retain their model/scoring version and provenance;
- mobile contains no privileged database credential;
- the full internal-alpha journey survives a fresh authenticated session;
- ranking state is independently reconstructable and immutable;
- the expanded detached science-state graph survives destructive rebuild/restore; and
- all prior P4–P7 guarantees remain green.

See ADR 0008 and `docs/protocols/phase8-internal-alpha.md`.

## Scientific non-claims

Phase 8 completes **infrastructure**, not Mosaic's matchmaking science. The current questionnaire answers, synthetic PNG candidates, candidate IDs, and ranking scores are deterministic fixtures.

No Phase 8 result establishes:

- attraction inference;
- psychometric validity;
- compatibility prediction;
- reciprocal selection probability;
- relationship-formation probability;
- long-term relationship quality prediction;
- optimal active-query design; or
- production scalability.

---

# Infrastructure program boundary

The preliminary infrastructure program ends here.

The next work should replace deterministic placeholders with explicitly versioned, testable Mosaic inference models while preserving the boundaries above. In particular, future scientific work must continue to distinguish:

```text
raw observation / experimental evidence
            ≠
versioned derived score or posterior
            ≠
matchmaking decision / recommendation
            ≠
validated long-term relationship outcome
```

A new scientific model is not considered validated merely because it fits behind the now-complete infrastructure.
