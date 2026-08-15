# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current development stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active scientific question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample candidate ranking?

S1 currently defines the observable target as a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional state is an effective linear-logistic acceptance surface. Separate preference magnitude and response-consistency parameters are not treated as identified because ordinary choice likelihoods only reveal their product without an independent scale anchor.

The current experimental checkpoint follows `s1-fixed-signal-sample-complexity-benchmark-v10a`. V7a showed that `kappa = 2q/(d+1)` did not collapse ranking performance when a fixed 18-candidate iid-Gaussian bank became increasingly ill-conditioned. V8a replaced that bank with a deterministic centered DCT tight frame and recovered much of the high-dimensional performance. V9a repeated the geometry control with a stochastic Gaussian-derived tight frame: high-dimensional recovery largely replicated, but finite-sample adaptive response paths could still infer the wrong direction despite exact full-bank covariance conditioning. V10a then removed adaptive acquisition and normalized every synthetic truth to the same effective slope norm `B = ||beta|| = 0.9`, using 32 seeds per `(d,kappa)` cell and 640 runs total. For the isotropic Gaussian reference population, wrong-order probability is exactly `acos(cos(beta,m))/pi`. At `d=12`, the prespecified Gaussian-logistic Fisher law predicted mean ordering error across the tested budgets with about `0.006` mean absolute cell error, but finite-dimensional transverse modes and finite query-path geometry remain important. Critically, mean performance is not a stopping guarantee: at `d=12,kappa=12`, mean ordering error is about `0.198` while the 90th percentile is about `0.270`. V10a tested only `B=0.9`, so the proposed signal coordinate `eta_F = B^2 kappa a(B)` has **not** yet been validated across signal levels. The next scientific checkpoint is a prespecified fixed-`B` phase diagram that varies `B` itself under passive controlled geometry before any product stopping rule or new greedy acquisition policy is introduced. See `docs/science/results/s1-fixed-signal-sample-complexity-benchmark-v10a.md`.

Do not reinterpret any existing deterministic questionnaire, synthetic PNG, candidate, score, or ranking fixture as a validated matchmaking, psychometric, attraction, compatibility, or relationship-prediction model.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-fixed-signal-sample-complexity-benchmark-v10a.md` for the current experimental boundary; read v7a–v9a first when reconstructing the geometry/sample-complexity argument.
5. ADR 0009 for the first scientific-state boundary.
6. `docs/ROADMAP.md` for completed infrastructure history.
7. `docs/ARCHITECTURE.md`
8. ADRs 0004–0008 for raw-evidence/derived-state, synthetic-provenance, operational-recovery, and persisted-ranking boundaries.
9. `docs/protocols/phase8-internal-alpha.md` for the complete application replay.
10. `docs/operations/database-recovery.md` before database or migration work that can affect persistent scientific state.

## Active S1 scientific invariants

- The first controlled visual target is `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- The provisional identifiable state is `alpha_i = [b_i, beta_i]` in a fixed/versioned feature basis.
- Do not persist separately named `preference_strength` and `choice_consistency` from ordinary pairwise/acceptance data unless a later protocol provides an independent scale anchor.
- Forced pairwise A/B choices remove the intercept and therefore cannot identify absolute pursuit selectivity on their own.
- The base S1 four-option response `A only / B only / Both / Neither` is provisionally modeled as two binary acceptability observations; conditional independence is a testable assumption, not a fact.
- Operational selectivity is initially a derived posterior-predictive acceptance rate over a versioned reference candidate distribution, not an unqualified intrinsic threshold scalar.
- Population information enters only through explicit versioned priors learned from suitable evidence; direct individual evidence determines the operative posterior.
- No universal feature dimension or fixed calibration-question count is established. Query burden is adaptive and uncertainty must remain explicit when a product cap is reached.
- `kappa = 2q/(d+1)` is not a sufficient finite-dimensional directional sample-complexity coordinate by itself. Query-path information geometry, the `d-1` transverse ranking modes, prior information, and effective slope signal `B = ||beta||` matter.
- For an isotropic Gaussian reference population and nonzero true/fitted slopes, population ordering error is exactly `acos(cos(beta,m))/pi`.
- For passive isotropic Gaussian-logistic sampling, `a(B) = E[sigmoid(BZ)(1-sigmoid(BZ))]` is the transverse Fisher weight and `eta_F = B^2 kappa a(B)` is the current large-dimensional theoretical information coordinate. V10a supports its mean-error behavior at `B=0.9,d=12`; scaling across `B` remains unvalidated.
- The large-dimensional mean-error relation `ordering_error ≈ atan(eta_F^-1/2)/pi` is a synthetic analytical benchmark, not a production stopping rule. Tail/false-stop operating characteristics remain unresolved.
- Exact identity empirical covariance of the admissible query bank does not imply the finite accumulated query path is isotropic and does not guarantee finite-sample active-policy reliability.
- Active queries must include model-diagnostic probes; do not optimize information gain forever under an untested likelihood.
- Synthetic-domain identification does not establish transfer to real profile choices, in-person attraction, relationship formation, or long-term relationship quality.

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

`.github/workflows/phase7-operational-hardening.yml` remains the repository-wide read-only pull-request gate. Its name is retained for check/branch-protection continuity even though it validates the completed Phase 8 application journey.

A normal pull request must preserve:

- frozen npm and uv dependency graphs;
- repository-history secret scanning;
- mobile typecheck/lint/tests and all-platform Expo export;
- Python Ruff + mypy + pytest;
- OpenAPI/TypeScript contract regeneration with zero drift;
- migration-backed database reconstruction;
- authentication/RLS isolation;
- live Phase 4, 5 and 6 replay protocols;
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
3. Identify what is raw observation, what is latent/effective state, what is derived output, and what is a downstream decision.
4. State identifiability assumptions and uncertainty explicitly.
5. Prefer the smallest identifiable parameterization; do not assign separate psychological labels to observationally confounded quantities.
6. Version feature basis, instrument/likelihood, implementation/model, and query-policy semantics before persisting output.
7. Add analytical/synthetic tests for mathematical invariants and live integration tests for persistence/provenance boundaries.
8. Add prespecified misspecification tests before increasing model complexity.
9. Record failed approaches when they reveal a meaningful scientific or architectural constraint.
10. Never silently change historical evidence or reinterpret a stored model output under new semantics.
11. Distinguish synthetic-ground-truth validation from human external validation.
12. Require the authoritative read-only gate to pass on the exact intended merge head.

## Handoff requirement

Before handing the project to another agent/developer after substantial work, leave the repository in a state where the next person can determine:

- what scientific or infrastructure question was attempted;
- what is currently working;
- what failed and why;
- the current branch/PR state;
- the next scientific checkpoint;
- the model/version/provenance assumptions currently active; and
- any unresolved identifiability, validation, transfer, or architectural assumptions.

Use repository documentation, commits, PR descriptions, issues, and CI records as the durable record rather than relying on chat context.
