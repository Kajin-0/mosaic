# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active S1 question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

The first observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Separate preference magnitude and response consistency are not treated as identified without an independent scale anchor.

Current experimental boundary: `docs/science/results/s1-finite-confidence-geometry-benchmark-v13b.md`.

## S1 scientific history and current boundary

- v7a showed `kappa=2q/(d+1)` does not collapse ranking performance when a fixed 18-candidate Gaussian bank becomes increasingly ill-conditioned.
- v8a/v9a controlled candidate geometry with deterministic and stochastic tight frames and recovered much of the high-dimensional behavior.
- v10a/v11a supported the large-dimensional mean information coordinate
  `eta_F = B^2 kappa a(B)`, `a(B)=E[sigmoid(BZ)(1-sigmoid(BZ))]`, for mean directional ranking error. This remains a mean-risk law, not an individual stopping guarantee.
- v12a–v12e tested Laplace-posterior angular-q95 stopping variants. Raw q95 undercovered; persistence did not fix high-dimensional weak-signal subgroup failures; radial/transverse debiasing restored safety by becoming too conservative; tangent projection restored utility by becoming strongly anti-conservative. **The Laplace-q95 stopping family is closed. Do not revive it with more scalar corrections, burn-ins, persistence constants, covariance projections, or empirical threshold tuning without a new theorem-level justification.**
- v13 introduced a prequential likelihood-ratio e-process. For fixed correctly specified `theta` and any normalized numerator `q_t` chosen predictably before the current outcome,
  `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.
- v13a verified the finite fixed-composite-null machinery. At nominal alpha 5%, the valid construction rejected only `22/4608 = 0.477%` true-null paths by 80 observations. A deliberately invalid numerator that used the current outcome rejected `4608/4608 = 100%`, median observation 6. Fixed-alternative power was `194/512 = 37.9%`, so the harness was safe but conservative.
- v13b implemented the intended operational sequence directly on a finite 24-direction grid: predictable finite-mixture numerator -> anytime confidence set -> adaptive disagreement query -> exact finite directional radius -> stop. Across 6,144 paths, truth was excluded from the confidence sequence at some time on `2.865%` of paths. **Zero false stops occurred while truth remained in the confidence set.** Target 0.25 stopped on 65.90% of paths by 120 observations with 0.130% false-stop rate; target 0.20 stopped on 25.57% with 0.081% false-stop rate; target 0.15 had no stops.

### Current conclusion

The finite-grid **safety mechanism is working**. The problem has moved from posterior calibration to efficiency, resolution, and continuous confidence-set geometry.

The supported operational route is:

```text
predictable normalized prequential numerator
        ↓
anytime-valid parameter confidence sequence C_t
        ↓
certified geometry of all slope directions represented in C_t
        ↓
stop only when the entire confidence set is directionally concentrated enough
```

Do not repeatedly define a data-dependent angular null around the current fitted direction and test it as though fixed. A moving data-dependent null does not automatically inherit the fixed-null e-process theorem.

The next checkpoint is **v13c resolution/efficiency decomposition**. Start by varying **finite angular grid spacing × observation horizon** while freezing the current mixture numerator, nominal alpha, and disagreement query policy. This should determine whether the strict target-0.15 failure is primarily discretization/resolution or insufficient information accumulation. Do not loosen alpha or tune thresholds on v13b.

After finite efficiency is understood, the continuous problem is to conservatively certify that the entire continuous confidence set lies inside a candidate directional cone, including nuisance intercept and slope magnitude. Any numerical method must provide a genuine upper bound on the best outside-cone likelihood; underestimating that supremum is anti-conservative and invalid.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-finite-confidence-geometry-benchmark-v13b.md`
5. `docs/science/results/s1-finite-null-eprocess-benchmark-v13a.md`
6. `docs/science/s1-anytime-likelihood-confidence.md`
7. v12a–v12e stopping result documents for the rejected posterior-q95 family.
8. v7a–v11a result documents for the geometry/sample-complexity/Fisher-law argument.
9. ADR 0009 for the first scientific-state boundary.
10. `docs/ROADMAP.md` and `docs/ARCHITECTURE.md`.
11. ADRs 0004–0008 for evidence, provenance, recovery, and persisted-ranking boundaries.
12. `docs/protocols/phase8-internal-alpha.md`.
13. `docs/operations/database-recovery.md` before persistent-state changes.

## Active S1 scientific invariants

- Controlled visual target: `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- Provisional identifiable state: `alpha_i=[b_i,beta_i]` in a fixed/versioned feature basis.
- Do not persist separately named `preference_strength` and `choice_consistency` from ordinary choice data without an independent scale anchor.
- Forced pairwise A/B choices remove the intercept and cannot identify absolute pursuit selectivity alone.
- The four-option response `A only / B only / Both / Neither` is provisionally represented as two binary acceptability observations; conditional independence is a hypothesis, not a fact.
- Operational selectivity is a derived predictive acceptance rate over a versioned reference distribution, not an intrinsic universal scalar.
- Population information enters only through explicit versioned priors; individual evidence determines operative individual inference.
- No universal feature dimension or calibration-question count is established.
- `kappa=2q/(d+1)` is not a sufficient finite-dimensional sample-complexity coordinate by itself. Query geometry, transverse modes, prior information, and `B=||beta||` matter.
- Under an isotropic Gaussian reference population, population ordering error for nonzero slopes is `acos(cos(beta,m))/pi`.
- `eta_F=B^2 kappa a(B)` and `ordering_error≈atan(eta_F^-1/2)/pi` are synthetic large-dimensional mean-risk relations, not stopping guarantees.
- The Laplace-posterior angular-q95 family is rejected by v12a–v12e.
- Every v13 validity numerator must be normalized and **predictable before the current outcome is observed**. v13a demonstrates catastrophic failure when this is violated.
- Adaptive query covariates may depend on the past but not on the current unseen outcome.
- Fixed-parameter e-process validity comes from the martingale/Ville argument; simulation tests implementation and operating characteristics, not the theorem itself.
- A fixed composite-null statistic using `Q_t/sup_H0 L_t` is safe only when the denominator is a genuine upper bound on the null likelihood supremum. Underestimation is invalid.
- Prefer `construct C_t -> certify geometry of all C_t -> stop` over moving data-dependent null tests.
- In v13b finite geometry, a false directional stop is impossible while the true grid parameter remains in `C_t`; the benchmark verified zero such violations.
- Do not trade away confidence-sequence validity merely to reduce query burden. Improve numerator/query efficiency while retaining predictability and the same nominal coverage semantics.
- E-process validity remains conditional on model specification. Pair context, nonlinear curvature, interactions, multimodality, and generator/feature error remain required misspecification regimes.
- Synthetic-domain identification does not establish transfer to real profile choices, in-person attraction, relationship formation, compatibility, or long-term relationship quality.

## Architectural invariants

- Mobile: React Native + Expo + TypeScript.
- Database/auth/storage: Supabase/PostgreSQL unless changed by ADR.
- Scientific/application engine: Python + FastAPI.
- Monorepo unless changed by ADR.
- Scientific logic is server-authoritative; do not duplicate model equations or decision semantics in the mobile app.
- Raw experimental responses are immutable evidence.
- Derived scores, posteriors, confidence sets, predictions, and rankings are separate versioned persistence classes and must never overwrite raw evidence.
- Scientifically meaningful output must retain model/policy/implementation versions and sufficient provenance for reconstruction.
- Database changes are migration-backed; repair deployed history with new migrations rather than rewriting applied migrations.
- Privileged/service-role credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous; do not log raw auth IDs, tokens, request bodies, raw science UUIDs, experimental answers, or generated artifacts.
- Detached science-state recovery excludes identity relinking by design.
- Existing deterministic fixtures are infrastructure test inputs, not validated scientific models.

## Authoritative CI gate

`.github/workflows/phase7-operational-hardening.yml` remains the repository-wide read-only PR gate. Preserve frozen dependency graphs, secret scanning, mobile checks/export, Python Ruff+mypy+pytest, contract zero-drift, migration reconstruction, auth/RLS isolation, replay protocols, persisted-ranking reconstruction/latency, detached science-state recovery, and generated-contract zero drift.

Do not weaken a gate merely to make CI green.

## Scientific development method

For each substantive model change:

1. State the scientific quantity being inferred or predicted.
2. Separate population priors from individual evidence.
3. Identify raw observation, latent/effective state, derived output, and downstream decision.
4. State identifiability assumptions and uncertainty explicitly.
5. Prefer the smallest identifiable parameterization.
6. Version feature basis, instrument/likelihood, model/implementation, and query-policy semantics.
7. Add analytical/synthetic tests for mathematical invariants and integration tests for persistence/provenance boundaries.
8. Add prespecified misspecification tests before increasing model complexity.
9. Record failed approaches when they reveal a meaningful scientific or architectural constraint.
10. Never silently change historical evidence or reinterpret stored model output under new semantics.
11. Distinguish synthetic-ground-truth validation from human external validation.
12. Require the authoritative read-only gate to pass on the intended merge head.

## Handoff requirement

Before handing the project to another agent/developer after substantial work, leave durable repository evidence of:

- the question attempted;
- what worked;
- what failed and why;
- the current branch/PR state;
- the next checkpoint;
- active model/version/provenance assumptions; and
- unresolved identifiability, validation, transfer, or architectural assumptions.

Use repository documentation, commits, PR descriptions, issues, and CI records rather than chat context.