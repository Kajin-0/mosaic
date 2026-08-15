# AGENTS.md

## Project

Mosaic is the working codename for a mobile-first, research-driven matchmaking system optimized for mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Preliminary infrastructure Phases 0–8 are complete.

The active S1 question is: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

The first observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a domain-general latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Separate preference magnitude and response consistency are not treated as identified without an independent scale anchor.

Current experimental boundary: `docs/science/results/s1-numerator-efficiency-benchmark-v13d.md`.

## S1 scientific history and current boundary

- v7a–v9a established that finite query geometry matters and that `kappa=2q/(d+1)` alone is not a sufficient finite-dimensional sample-complexity coordinate.
- v10a/v11a supported the synthetic large-dimensional mean information coordinate `eta_F=B^2 kappa a(B)`, with `a(B)=E[sigmoid(BZ)(1-sigmoid(BZ))]`. This is a mean-risk law, not an individual stopping guarantee.
- v12a–v12e falsified the Laplace-posterior angular-q95 stopping family. Raw q95 undercovered; persistence failed weak/high-dimensional subgroups; radial/transverse corrections restored safety by becoming too conservative; tangent projection restored utility by becoming anti-conservative. **That family is closed. Do not revive it with empirical threshold tuning without a new theorem-level argument.**
- v13 introduced a prequential likelihood-ratio e-process. For fixed correctly specified `theta` and any normalized numerator `q_t` chosen predictably before the current outcome, `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.
- v13a verified the finite fixed-null machinery: valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an outcome-leaking invalid numerator rejected `4608/4608=100%`; fixed-alternative power was 37.9% by 80 observations.
- v13b implemented the intended finite operational sequence `predictable numerator -> anytime C_t -> adaptive query -> exact confidence-set directional radius -> stop`. Across 6,144 paths, truth was ever excluded on 2.865%; **zero false stops occurred while truth remained in C_t**. The strict target 0.15 had no stops by 120 observations.
- v13c separated grid resolution from horizon at target 0.15. Refining 15° -> 5° increased the 240-observation stop rate from 2.73% to 7.55%, but every grid had zero stops through 180 and the 5° median stop was 237. **Discretization matters, but evidence accumulation is the dominant burden.**
- v13d then held every query and response fixed across numerator variants on a 5° grid. The existing all-grid mixture stopped on 7.81% by 240; lagged MLE-face stopped on 26.30%; SNML on 25.85%; confidence-restricted mixture on 8.07%. A synthetic-truth oracle numerator stopped on 76.43% by 180 and 96.55% by 240 on exactly the same query paths. **The current query sequence is informative enough; prequential predictive regret is now the dominant identified efficiency bottleneck.**
- v13d does **not** establish MLE > SNML. MLE had 404 stops versus SNML 397; paired discordant counts were 45 versus 38 (`p≈0.51`). Treat them as co-leading exploratory candidates requiring fresh-seed validation.

### Current conclusion

The finite-grid safety mechanism is working and the present strict-target burden is mechanistically localized.

```text
predictable normalized numerator
        ↓
anytime-valid parameter confidence sequence C_t
        ↓
certified geometry of all directions represented in C_t
        ↓
stop only when the entire confidence set is concentrated enough
```

Do not repeatedly test a moving data-dependent angular null as though fixed. Construct `C_t` first and certify geometry afterward.

The immediate checkpoint is a **fresh-seed prospective numerator validation** with the v13d design frozen: `mixture_all` control, `mle_face` and `snml` candidates, 5° grid, `B=0.9`, target 0.15, alpha 0.05, the same candidate bank and disagreement-query controller, and a 240-observation cap. Primary endpoint is stop rate by 240; burden is median stopping observation; safety diagnostics are truth-exclusion and false-stop rates. Any false directional stop while truth is still in `C_t` is a critical implementation failure.

After that replication, attack the remaining oracle gap with a theorem-preserving **predictable challenger/test-specific numerator** or other regret-reduction construction before changing query policy. Query-policy optimization should remain an isolated later experiment.

The continuous problem remains unresolved: certify conservatively that the entire continuous confidence set lies inside a candidate directional cone, including nuisance intercept and slope magnitude. Any numerical method must provide a genuine upper bound on the best outside-cone likelihood; underestimating that supremum is anti-conservative and invalid.

## Required reading before substantial work

1. `README.md`
2. `docs/science/README.md`
3. `docs/science/s1-identifiable-preference-model.md`
4. `docs/science/results/s1-numerator-efficiency-benchmark-v13d.md`
5. `docs/science/results/s1-resolution-horizon-benchmark-v13c.md`
6. `docs/science/results/s1-finite-confidence-geometry-benchmark-v13b.md`
7. `docs/science/results/s1-finite-null-eprocess-benchmark-v13a.md`
8. `docs/science/s1-anytime-likelihood-confidence.md`
9. v12a–v12e result documents for the rejected posterior-q95 family.
10. v7a–v11a result documents for the geometry/sample-complexity/Fisher-law argument.
11. ADR 0009 for the first scientific-state boundary.
12. `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, ADRs 0004–0008, `docs/protocols/phase8-internal-alpha.md`, and `docs/operations/database-recovery.md` when relevant to persistence/operations.

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
- Fixed-composite-null likelihood suprema must be genuine upper bounds. Underestimating a null supremum is invalid.
- Prefer `construct C_t -> certify all of C_t -> stop` over moving data-dependent null tests.
- Finite-grid false stopping is structurally impossible while the true grid parameter remains in `C_t`; v13b–v13d have not shown a counterexample.
- Numerator **mean** log loss alone is not an adequate efficiency metric. v13d shows stopping depends on the pathwise distribution/tails of realized `log Q` and confidence contraction.
- `oracle_true` is a synthetic diagnostic ceiling only and must never be used operationally.
- Do not declare MLE-face or SNML selected from v13d without fresh-seed prospective replication.
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
