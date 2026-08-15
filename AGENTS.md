# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active S1 question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

The first observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Separate preference magnitude and response consistency are not treated as identified without an independent scale anchor.

Current experimental boundary: `docs/science/results/s1-nested-confidence-benchmark-v13f.md`.

## S1 scientific history and current boundary

- v7a–v9a established that finite query geometry matters and that `kappa=2q/(d+1)` alone is not a sufficient finite-dimensional sample-complexity coordinate.
- v10a/v11a supported the synthetic large-dimensional mean information coordinate `eta_F=B^2 kappa a(B)`, with `a(B)=E[sigmoid(BZ)(1-sigmoid(BZ))]`. This is a mean-risk law, not an individual stopping guarantee.
- v12a–v12e falsified the Laplace-posterior angular-q95 stopping family. **That family is closed. Do not revive it with empirical threshold tuning without a new theorem-level argument.**
- v13 introduced a prequential likelihood-ratio e-process. For fixed correctly specified `theta` and any normalized numerator chosen predictably before the current outcome, `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.
- v13a verified the finite fixed-null machinery: valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an outcome-leaking invalid numerator rejected 100%.
- v13b implemented `predictable numerator -> anytime C_t -> adaptive query -> exact confidence-set directional radius -> stop`. Across 6,144 paths, truth was ever excluded on 2.865%; **zero false stops occurred while truth remained in C_t**.
- v13c showed the strict-target burden is not mainly angular-grid quantization. Refining 15° -> 5° increased the 240-observation stop rate from 2.73% to 7.55%, but all grids remained at zero through 180 and the 5° median stop was 237.
- v13d held every query/response fixed across numerator variants. Current-time `mixture_all` stopped on 7.81% by 240, MLE-face on 26.30%, SNML on 25.85%, while a synthetic-truth oracle stopped on 96.55% on the same paths. This identified prequential predictive regret as a major efficiency bottleneck under the then-current set representation.
- v13e prospectively replicated the adaptive-numerator effect on fresh seeds `192..319`: mixture control 7.16%, MLE-face 26.89% (+19.73 pp, paired `p≈7.9e-76`), SNML 25.72% (+18.55 pp, `p≈2.5e-72`), zero geometry violations. MLE versus SNML crossed the prespecified ranking threshold (`44` vs `26` discordant stops, `p=0.0414`) but differed by only ~1.17 pp.
- v13f then corrected a more fundamental efficiency mistake: v13b–v13e used the **current-time** set `C_t={theta:E_t(theta)<1/alpha}`, allowing previously rejected parameters to re-enter. The running intersection `C_t^cap=intersection_{s<=t} C_s={theta:max_{s<=t}E_s(theta)<1/alpha}` has the same simultaneous coverage event and remembers all past valid crossings.
- On fresh seeds `320..447`, v13f changed only set representation and held the same global finite-grid MLE center between comparisons. Nesting produced very large gains: mixture `7.23% -> 70.25%`, MLE-face `26.56% -> 53.97%`, SNML `26.17% -> 58.53%` by 240. MLE nested median stop fell to 201 from 219.5. **No current-time stop was lost and geometry violations remained zero.**
- v13f therefore reverses the observed numerator ranking: under the now-preferred nested representation, the original all-grid mixture is the observed leader at 70.25%, ahead of SNML and MLE. v13e's MLE preference is valid only for the inferior current-time-set representation and must not be carried forward unqualified.

### Current conclusion

The strongest finite-grid S1 confidence route is now:

```text
predictable normalized e-process numerator(s)
        ↓
current-time e-process sets
        ↓
running intersection / nested confidence sequence C_t^cap
        ↓
reported finite-grid MLE direction
        ↓
certify every direction retained in C_t^cap lies inside target cone
        ↓
stop
```

Do not repeatedly test a moving data-dependent angular null as though fixed. Construct the parameter confidence sequence first and certify its geometry afterward.

**Future finite-grid work should use the nested confidence sequence by default.** Current-time-only sets remain historical comparators.

The next exact checkpoint is a theorem-preserving **theta-specific predictable challenger numerator** with the query policy frozen. For each candidate null `theta_j`, its own normalized predictable `q_{t,j}` may be generated from the strongest one-step-lagged alternative excluding `theta_j`. The e-process for `theta_j` remains valid because its numerator is normalized and predictable; a common numerator across all null parameters is not required.

Use the nested all-grid mixture as the baseline control, retain MLE/SNML nested as useful comparators, and test the challenger construction on a fresh disjoint seed block. Do **not** change the acquisition policy in the same checkpoint.

The continuous problem remains unresolved: certify conservatively that the entire continuous confidence set lies inside a candidate directional cone, including nuisance intercept and slope magnitude. Any numerical method must provide a genuine upper bound on the best outside-cone likelihood; underestimating that supremum is anti-conservative and invalid.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-nested-confidence-benchmark-v13f.md`
5. `docs/science/results/s1-numerator-validation-benchmark-v13e.md`
6. `docs/science/results/s1-numerator-efficiency-benchmark-v13d.md`
7. `docs/science/results/s1-resolution-horizon-benchmark-v13c.md`
8. `docs/science/results/s1-finite-confidence-geometry-benchmark-v13b.md`
9. `docs/science/results/s1-finite-null-eprocess-benchmark-v13a.md`
10. `docs/science/s1-anytime-likelihood-confidence.md`
11. v12a–v12e result documents for the rejected posterior-q95 family.
12. v7a–v11a result documents for the geometry/sample-complexity/Fisher-law argument.
13. ADR 0009 for the first scientific-state boundary.
14. `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, ADRs 0004–0008, `docs/protocols/phase8-internal-alpha.md`, and `docs/operations/database-recovery.md` when relevant to persistence/operations.

## Active S1 scientific invariants

- Controlled visual target: `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- Provisional identifiable state: `alpha_i=[b_i,beta_i]` in a fixed/versioned feature basis.
- Do not persist separately named `preference_strength` and `choice_consistency` from ordinary choice data without an independent scale anchor.
- Forced pairwise A/B choices remove the intercept and cannot identify absolute pursuit selectivity alone.
- `A only / B only / Both / Neither` is provisionally represented as two binary acceptability observations; conditional independence remains a testable assumption.
- No universal feature dimension or calibration-question count is established.
- `eta_F` and its associated large-dimensional error formula are synthetic mean-risk benchmarks, not stopping guarantees.
- The Laplace-posterior angular-q95 family is rejected by v12a–v12e.
- Every v13 validity numerator must be normalized and **predictable before the current outcome is observed**. v13a shows catastrophic failure when this is violated.
- Adaptive query covariates may depend on the past but not on the current unseen outcome.
- Fixed-parameter e-process validity comes from the martingale/Ville argument; simulation measures implementation and operating characteristics rather than creating the theorem.
- A common numerator across all candidate null parameters is **not** required. Parameter-specific predictable normalized numerators are allowed; each candidate's validity is judged under that candidate parameter.
- Fixed-composite-null likelihood suprema must be genuine upper bounds. Underestimating a null supremum is invalid.
- Prefer `construct confidence sequence -> certify all retained parameters -> stop` over moving data-dependent null tests.
- The preferred finite-grid confidence object is the nested running intersection `C_t^cap`. It has the same simultaneous truth-coverage event as the sequence of current-time sets and prevents rejected hypotheses from re-entering.
- An empty nested set is a confidence/model failure state, not a successful certificate.
- When current and nested radii are compared about the same center, nested radius must never exceed current radius. v13f enforces this as a hard assertion.
- Finite-grid false directional stopping is structurally impossible while the true grid parameter remains in the certified set; v13b–v13f have shown zero geometry violations.
- Numerator **mean** log loss alone is not an adequate efficiency metric. Stopping depends on the pathwise distribution/tails of realized e-values and confidence contraction.
- `oracle_true` is a synthetic diagnostic ceiling only and must never be used operationally.
- v13e's MLE-over-SNML ranking is scoped to current-time confidence sets. Under nesting, v13f's observed ranking is mixture > SNML > MLE; do not conflate these regimes.
- Do not trade away confidence-sequence validity merely to reduce query burden.
- E-process validity remains conditional on likelihood specification. Pair context, nonlinear curvature, interactions, multimodality, and generator/feature error are still required misspecification regimes.
- Synthetic-domain identification does not establish transfer to real profiles, in-person attraction, relationship formation, compatibility, or long-term relationship quality.

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

Before handing the project to another agent/developer after substantial work, leave durable repository evidence of the question attempted, what worked, what failed and why, the current branch/PR state, the next checkpoint, active model/version/provenance assumptions, and unresolved identifiability/validation/transfer/architecture assumptions.

Use repository documentation, commits, PR descriptions, issues, and CI records rather than chat context.
