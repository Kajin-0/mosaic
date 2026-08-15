# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current development stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active scientific question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample candidate ranking?

S1 defines the first observable target as a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional state is an effective linear-logistic acceptance surface. Separate preference magnitude and response-consistency parameters are not treated as identified because ordinary choice likelihoods only reveal their product without an independent scale anchor.

The current experimental checkpoint follows `s1-finite-null-eprocess-benchmark-v13a`.

### Current synthetic boundary

- v7a showed that `kappa = 2q/(d+1)` did not collapse ranking performance when a fixed 18-candidate iid-Gaussian bank became increasingly ill-conditioned.
- v8a replaced that bank with a deterministic centered tight frame and recovered much of the high-dimensional performance.
- v9a repeated the geometry control with a stochastic Gaussian-derived tight frame; high-dimensional recovery largely replicated, but finite response paths could still infer the wrong direction.
- v10a removed adaptive acquisition and fixed `B = ||beta|| = 0.9`. At `d=12`, the Gaussian-logistic Fisher law predicted mean population ordering error well, while upper-tail error remained too large for a stopping guarantee.
- v11a varied `B` and supported the large-dimensional mean information coordinate `eta_F = B^2 kappa a(B)`, where `a(B)=E[sigmoid(BZ)(1-sigmoid(BZ))]`. This remains a mean-risk law, not a stopping rule.
- v12a tested a posterior-observable Laplace q95 angular stopping statistic. Single crossing was anti-conservative: aggregate false-stop-given-stop was about 7–9%, and fixed-checkpoint coverage was severely subnominal for weak-signal/high-dimensional conditions.
- v12b prospectively replicated the benefit of requiring two consecutive q95 crossings but exposed serious subgroup failure; at `d=12, B=0.55, target=0.25`, `23/89 = 25.8%` of two-crossing stops were false.
- v12c full-trace radial debiasing restored aggregate/subgroup safety but became too conservative, failing the strong-signal utility gate.
- v12d transverse-only debiasing improved utility while preserving safety but still failed the strict high-dimensional strong-signal burden gate.
- v12e projected posterior perturbations into tangent space. It recovered the utility gate but destroyed calibration: the primary tangent two-consecutive rule false-stopped on about 10–12% of aggregate stops, with severe high-dimensional weak-signal subgroup failures including `34/90 = 37.8%` at `d=12, B=0.55, target=0.25`.
- v12e therefore triggered the prespecified family-level stop: **do not continue tuning Laplace-posterior angular-q95 rules with scalar corrections, burn-ins, persistence constants, projections, or threshold hacks.**
- v13 introduced a prequential likelihood-ratio e-process. For fixed `theta` and any normalized numerator distribution `q_t` selected predictably before `Y_t`, `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale under correctly specified `theta`, including predictable adaptive query selection. Ville's inequality gives an anytime-valid parameter confidence sequence.
- v13a tested that logic on a fixed finite composite null with exact null likelihood maximization. Under optional stopping and adaptive predictable query selection, the valid construction rejected only `22/4608 = 0.477%` true-null paths by 80 observations at nominal alpha 5%. A deliberately invalid numerator that used the current outcome rejected `4608/4608 = 100%`, median observation 6. Valid fixed-alternative power was `194/512 = 37.9%` by 80 observations, so the method is strongly valid in this harness but currently conservative/inefficient.

### Current scientific conclusion

The **finite-sample sequential-confidence problem has moved away from posterior calibration and into confidence-set geometry**.

The supported route is:

```text
predictable normalized prequential numerator
        ↓
anytime-valid parameter confidence sequence C_t
        ↓
certified geometry of all slope directions represented in C_t
        ↓
stop only when the entire confidence set is directionally concentrated enough
```

Do **not** repeatedly define a data-dependent angular null around the current fitted direction and test it as though the null were fixed. The fixed-composite-null e-process argument does not automatically cover a sequence of adaptively selected hypotheses.

The next checkpoint is v13b: a **finite-grid confidence-set geometry harness**. Maintain the exact finite e-process confidence set over time, compute its exact directional diameter/radius, and verify the intended operational logic `confidence set -> geometric certification -> stop` before introducing continuous optimization.

Do not reinterpret any existing deterministic questionnaire, synthetic PNG, candidate, score, posterior, confidence set, or ranking fixture as a validated matchmaking, psychometric, attraction, compatibility, or relationship-prediction model.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-finite-null-eprocess-benchmark-v13a.md` for the current experimental boundary.
5. `docs/science/s1-anytime-likelihood-confidence.md` for the v13 theorem/operational-confidence construction.
6. `docs/science/results/s1-tangent-stopping-benchmark-v12e.md`, `s1-transverse-stopping-benchmark-v12d.md`, `s1-radial-stopping-benchmark-v12c.md`, `s1-stopping-validation-benchmark-v12b.md`, and `s1-stopping-calibration-benchmark-v12a.md` for the stopping-family failure chain.
7. Read v7a–v11a result documents when reconstructing the geometry/sample-complexity/Fisher-law argument.
8. ADR 0009 for the first scientific-state boundary.
9. `docs/ROADMAP.md` for completed infrastructure history.
10. `docs/ARCHITECTURE.md`
11. ADRs 0004–0008 for raw-evidence/derived-state, synthetic-provenance, operational-recovery, and persisted-ranking boundaries.
12. `docs/protocols/phase8-internal-alpha.md` for the complete application replay.
13. `docs/operations/database-recovery.md` before database or migration work that can affect persistent scientific state.

## Active S1 scientific invariants

- The first controlled visual target is `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- The provisional identifiable state is `alpha_i = [b_i, beta_i]` in a fixed/versioned feature basis.
- Do not persist separately named `preference_strength` and `choice_consistency` from ordinary pairwise/acceptance data unless a later protocol provides an independent scale anchor.
- Forced pairwise A/B choices remove the intercept and therefore cannot identify absolute pursuit selectivity on their own.
- The base S1 four-option response `A only / B only / Both / Neither` is provisionally modeled as two binary acceptability observations; conditional independence is a testable assumption, not a fact.
- Operational selectivity is initially a derived predictive acceptance rate over a versioned reference candidate distribution, not an unqualified intrinsic threshold scalar.
- Population information enters only through explicit versioned priors learned from suitable evidence; direct individual evidence determines operative individual inference.
- No universal feature dimension or fixed calibration-question count is established. Query burden is adaptive and uncertainty must remain explicit when a product cap is reached.
- `kappa = 2q/(d+1)` is not a sufficient finite-dimensional directional sample-complexity coordinate by itself. Query-path information geometry, the `d-1` transverse ranking modes, prior information, and effective slope signal `B = ||beta||` matter.
- For an isotropic Gaussian reference population and nonzero true/fitted slopes, population ordering error is exactly `acos(cos(beta,m))/pi`.
- For passive isotropic Gaussian-logistic sampling, `a(B) = E[sigmoid(BZ)(1-sigmoid(BZ))]` is the transverse Fisher weight and `eta_F = B^2 kappa a(B)` is the current supported large-dimensional mean-information coordinate across the tested `B` range. It is not a production stopping rule.
- The large-dimensional mean-error relation `ordering_error ≈ atan(eta_F^-1/2)/pi` is a synthetic analytical benchmark. Mean risk does not control individual/tail risk.
- The Laplace-posterior angular-q95 family is rejected as a finite-sample sequential confidence guarantee under the tested S1 protocol. v12a–v12e jointly establish this boundary.
- Do not reintroduce raw q95, scalar radial multipliers, arbitrary burn-ins, persistence thresholds, or tangent/full-covariance mixtures without a new theorem-level justification.
- For the v13 e-process, every numerator `q_t` used for validity must be normalized and **predictable before the current outcome is observed**. v13a's leaky control demonstrates catastrophic failure when this is violated.
- Adaptive query features `x_t` may depend on the past, provided they are predictable with respect to the current outcome.
- For a fixed parameter `theta`, the confidence-sequence guarantee follows from the nonnegative martingale and Ville's inequality; simulation is an implementation sanity check, not the source of validity.
- A fixed composite-null e-process can safely use `Q_t / sup_{theta in H0} L_t(theta)` only when the denominator is a genuine upper bound on the null likelihood supremum. **Underestimating the supremum is anti-conservative and invalid.**
- A time-varying data-dependent null is not automatically covered by the fixed-null theorem. Prefer constructing `C_t(alpha)` first and then certifying a geometric property of the entire confidence set.
- The next operational confidence object is directional concentration of `C_t`: exact finite-grid diameter/radius first, then a conservatively certified continuous analogue.
- Exact identity empirical covariance of an admissible query bank does not imply the finite accumulated query path is isotropic and does not guarantee finite-sample active-policy reliability.
- Active queries must include model-diagnostic probes; do not optimize information gain forever under an untested likelihood.
- E-process validity is conditional on the likelihood model containing the truth. Pair context, nonlinear curvature, interactions, multimodality, and generator/feature error remain required misspecification regimes.
- Synthetic-domain identification does not establish transfer to real profile choices, in-person attraction, relationship formation, or long-term relationship quality.

## Architectural invariants

- Mobile client: React Native + Expo + TypeScript.
- Database/auth/storage foundation: Supabase/PostgreSQL unless an ADR explicitly changes this.
- Scientific/application engine: Python + FastAPI.
- The repository is a monorepo unless an ADR explicitly changes that decision.
- Scientific logic is server-authoritative; do not duplicate model equations or decision semantics in the mobile app.
- Raw experimental responses are immutable evidence.
- Derived scores, posteriors, confidence sets, predictions, and ranking outputs are separate versioned persistence classes; they must never overwrite raw evidence.
- A scientifically meaningful output must retain implementation/model/policy version and enough input/provenance information for audit and reconstruction.
- Database schema changes must be migration-backed. Applied migrations are forward-owned history; repair deployed defects with a new migration rather than rewriting an applied migration.
- Service-role or otherwise privileged credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous. Do not introduce raw auth user IDs, bearer tokens, request bodies, raw science UUIDs, experimental answers, or generated artifact bytes into routine request logs.
- Detached `mosaic-science-state-backup-v2` recovery intentionally excludes `science_subjects.user_id`; identity relinking is a separate privileged operation.
- The 500 ms latency threshold is an internal-alpha CI regression budget for ordinary local non-generation operations, not a production scalability claim.
- Existing deterministic fixtures are infrastructure test inputs. Replacing them with real scientific models requires explicit model versioning, tests, documentation, and validation; passing infrastructure CI is not evidence of scientific validity.

## Authoritative CI gate

`.github/workflows/phase7-operational-hardening.yml` remains the repository-wide read-only pull-request gate. Its name is retained for check/branch-protection continuity even though it validates the completed Phase 8 application journey.

A normal pull request must preserve frozen npm/uv dependency graphs, secret scanning, mobile typecheck/lint/tests/export, Python Ruff+mypy+pytest, contract zero-drift, migration reconstruction, authentication/RLS isolation, live replay protocols, persisted-ranking reconstruction/latency, detached science-state recovery, and zero generated-contract drift.

Do not weaken or bypass a gate merely to make CI green. Treat failures as evidence about the implementation, contract, or model until proven otherwise.

## Scientific development method

For each substantive model change:

1. State the scientific quantity being inferred or predicted.
2. Separate population priors from individual evidence.
3. Identify raw observation, latent/effective state, derived output, and downstream decision.
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
