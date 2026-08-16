# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active S1 question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

The first observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Separate preference magnitude and response consistency are not treated as identified without an independent scale anchor.

Current experimental boundary: `docs/science/results/s1-cone-cover-benchmark-v13j.md`.

## S1 scientific history and current boundary

- v7a–v9a established that finite query geometry matters and that `kappa=2q/(d+1)` alone is not a sufficient finite-dimensional sample-complexity coordinate.
- v10a/v11a supported the synthetic large-dimensional mean information coordinate `eta_F=B^2 kappa a(B)`, with `a(B)=E[sigmoid(BZ)(1-sigmoid(BZ))]`. This is a mean-risk law, not an individual stopping guarantee.
- v12a–v12e falsified the Laplace-posterior angular-q95 stopping family. **That family is closed. Do not revive it with empirical threshold tuning without a new theorem-level argument.**
- v13 introduced a prequential likelihood-ratio e-process. For fixed correctly specified `theta` and any normalized numerator chosen predictably before the current outcome, `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.
- v13a verified the finite fixed-null machinery: valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an outcome-leaking invalid numerator rejected 100%.
- v13b implemented `predictable numerator -> anytime C_t -> adaptive query -> exact confidence-set directional radius -> stop`. Across 6,144 paths, truth was ever excluded on 2.865%; **zero false stops occurred while truth remained in C_t**.
- v13c showed the strict-target burden is not mainly angular-grid quantization. Refining 15° -> 5° increased the 240-observation stop rate from 2.73% to 7.55%, but all grids remained at zero through 180 and the 5° median stop was 237.
- v13d/v13e showed that under the then-current-time representation, MLE-face/SNML numerators substantially improved efficiency over the all-grid mixture, but the conclusion was representation-dependent.
- v13f corrected the more fundamental set-reentry defect by replacing current-time sets with the running intersection `C_t^cap=intersection_{s<=t} C_s`. On fresh seeds, nesting raised 240-observation stop rates to 70.25% for mixture, 53.97% for MLE-face, and 58.53% for SNML, with zero geometry violations. **Nested/running-intersection sets are now the finite-grid default.**
- v13g tested a theta-specific leave-null-out MLE challenger. It collapsed almost exactly to ordinary MLE-face and materially underperformed the nested all-grid mixture: 54.17% versus 71.81% stopping by 240.
- v13h proved analytically that a leave-one-out all-alternative mixture is only the affine transform `E_j^(-j)=(N E_j^all-1)/(N-1)`. At `N=72`, alpha 0.05, it merely changes the equivalent all-grid threshold from 20 to 19.736 and therefore is not a substantive new mechanism.
- v13i tested an immediate-neighbor mixture at ±5 degrees on fresh seeds `576..703`. It produced **0/1536 certificates by 240 observations**, while the frozen nested all-grid control stopped on 71.74%. The method was safe but essentially powerless because neighboring alternatives were too close to each candidate null. This establishes that prior dilution and null/alternative separation must be optimized jointly.
- v13j used the certification geometry itself to construct an 11-point outside-cone support at offsets `{±30,±60,±90,±120,±150,180}` degrees. On fresh seeds `704..831`, with acquisition still frozen to the historical all-grid controller, cone-cover stopped on **88.48%** by 240 versus **71.29%** for nested all-grid mixture. At 240, 1,095 paths stopped under both, **264 stopped only under cone-cover, and zero stopped only under mixture** (`p≈6.75e-80`). Median stop improved 216 -> 210. Geometry violations were zero. Cone-cover is therefore the leading finite-grid numerator under the current 2-D strict-target protocol.

### Current conclusion

The strongest finite-grid S1 confidence route is now:

```text
predictable normalized candidate-specific cone-cover numerator
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

**Future finite-grid work should use nested confidence sequences by default.** Current-time-only sets remain historical comparators.

**Do not continue hand-tuning numerator supports on v13j data.** v13j's 11-point support is geometrically motivated and prospectively validated. The next checkpoint changes acquisition only while freezing this numerator.

The next exact checkpoint is an acquisition-efficiency comparison:

1. control: historical current-time all-grid-mixture disagreement acquisition + nested cone-cover certification;
2. candidate: disagreement acquisition over the **surviving nested cone-cover set** + the same nested cone-cover certification.

Keep the 5-degree grid, `B=0.9`, target 0.15, alpha 0.05, candidate bank, cone-cover numerator, nested representation, and global finite-grid MLE reporting center unchanged. Use a fresh disjoint seed block. Primary endpoints are paired stop probability at 180 and 240 and stopping-time distribution; zero geometry violations is a hard invariant.

The continuous problem remains unresolved: certify conservatively that the entire continuous confidence set lies inside a candidate directional cone, including nuisance intercept and slope magnitude. Any numerical method must provide a genuine upper bound on the best outside-cone likelihood; underestimating that supremum is anti-conservative and invalid.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-cone-cover-benchmark-v13j.md`
5. `docs/science/results/s1-cone-cover-mixture-design-v13j.md`
6. `docs/science/results/s1-local-neighbor-benchmark-v13i.md`
7. `docs/science/results/s1-leaveout-mixture-equivalence-v13h.md`
8. `docs/science/results/s1-theta-challenger-benchmark-v13g.md`
9. `docs/science/results/s1-nested-confidence-benchmark-v13f.md`
10. v13a–v13e result documents and `docs/science/s1-anytime-likelihood-confidence.md` for the confidence-sequence development chain.
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
- A common numerator across all candidate null parameters is not required. Parameter-specific predictable normalized numerators are allowed.
- Fixed-composite-null likelihood suprema must be genuine upper bounds. Underestimating a null supremum is invalid.
- Prefer `construct confidence sequence -> certify all retained parameters -> stop` over moving data-dependent null tests.
- The preferred finite-grid confidence object is the nested running intersection `C_t^cap`; rejected hypotheses must not be allowed to re-enter.
- An empty nested set is a confidence/model failure state, not a successful certificate.
- Finite-grid false directional stopping is structurally impossible while the true grid parameter remains in the certified set. v13b–v13j have maintained zero geometry violations under the reported finite-grid certificates.
- Numerator mean log loss or support size alone is not an adequate efficiency criterion. v13i shows that a tiny support can be powerless when alternatives have poor KL/separation from the candidate null.
- v13j's supported finite-grid design principle is to balance predictive/prior dilution with geometric coverage and null/alternative separation.
- `oracle_true` is a synthetic diagnostic ceiling only and must never be used operationally.
- v13e's MLE-over-SNML result is scoped to current-time sets; do not carry it into the nested regime.
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
