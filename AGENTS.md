# AGENTS.md

## Project

Mosaic is a mobile-first, research-driven matchmaking system whose terminal objective is mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Infrastructure Phases 0–8 are complete.

The first defensible S1 observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a universal latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Ordinary choice data do not separately identify preference magnitude and response consistency without an independent scale anchor.

Current experimental boundary:

`docs/science/results/s1-coupled-continuous-bound-benchmark-v14c.md`

PR #12 remains draft. Do not merge S1 on current evidence.

## Scientific boundary

### Closed results before v13

- v7a–v9a: finite query geometry matters; `kappa=2q/(d+1)` is not a sufficient finite-dimensional sample-complexity coordinate.
- v10a/v11a: the synthetic large-d mean coordinate `eta_F=B^2 kappa a(B)` is useful for mean ranking risk, not individual stopping.
- v12a–v12e: the Laplace/Gaussian posterior angular-q95 stopping family failed finite-sample sequential calibration. **Do not revive it by empirical burn-ins, persistence rules, projections, threshold tuning, or scalar corrections without a new theorem.**

### v13 finite-grid confidence chain

For any fixed correctly specified `theta`, predictable query covariates, and any normalized numerator chosen before the current outcome,

```text
E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)
```

is a nonnegative martingale. Ville therefore gives an anytime-valid parameter confidence sequence.

Important finite-grid results:

- v13a: valid fixed-null rejection 22/4608 = 0.477% at nominal 5%; an outcome-leaking invalid numerator rejected 100%.
- v13b: exact confidence-set geometry produced zero false directional stops while truth remained in the set.
- v13f: replace current-time sets with the running intersection `C_t^cap`; rejected parameters must not re-enter.
- v13i: immediate ±5° alternatives gave 0/1536 certificates by 240; sparse support alone is useless when alternatives are too close to the null.
- v13j: geometrically prespecified cone-cover support `{±30,±60,±90,±120,±150,180}` reached 88.48% strict-target stopping by 240 versus 71.29% for nested all-grid mixture, with 264 cone-cover-only paths and zero mixture-only paths. This is the leading finite-grid numerator.
- v13k: survivor-focused acquisition increased 180-observation stopping from 5.47% to 10.29% but did not improve the 240 endpoint (87.96% vs 88.67%, p=0.538) and worsened observed truth-exclusion/false-stop rates. Retain historical all-grid current disagreement acquisition as the finite-grid reference.

Do not further hand-tune finite-grid numerator supports or acquisition mixtures on these outcomes.

### v14 continuous confidence geometry

Finite angular grids cannot certify between-grid parameters or handle free nuisance intercept and slope magnitude exactly. The current continuous architecture is deliberately conservative:

```text
predictable binary evidence
        ↓
alpha_0 = 0.005 common e-process
        ↓
certified finite nuisance box in (intercept, beta_x, beta_y)
        ↓
alpha_c = 0.045 candidate-specific cone-cover e-process
        ↓
exact rational target wedge tan(delta_cert)=1/2
        ↓
grouped sufficient statistics
        ↓
60-digit directed interval bounds
        ↓
branch-and-bound exclusion of both outside-cone halfspaces
```

`atan(1/2) ~= 26.565°`, intentionally narrower than the nominal 27° target. The total confidence budget is at most 0.05 by union bound.

Numerical one-sidedness is non-negotiable: a local optimizer, sampled angular grid, or numerical value that can underestimate the best outside-cone survivor cannot be used as a stopping certificate.

#### v14a — interval method validation

`docs/science/results/s1-continuous-bound-validation-v14a.md`

- zero likelihood-enclosure violations over 864 rotated high-precision checks;
- zero cone-e lower-bound violations;
- dense diagnostics found no outside-cone survivors in tested scenarios, but branch-and-bound did not prove closure;
- raw runtime about 1,523 s.

Conclusion: arithmetic appeared safe, but bounds were loose and raw-observation evaluation was computationally unacceptable.

#### v14b — grouped sufficient statistics

`docs/science/results/s1-grouped-continuous-runtime-v14b.md`

Exact grouping by feature vector and accept/reject counts preserved directed inequalities and identical tested search outcomes.

- zero tested likelihood/cone bound violations;
- overall runtime comparison 119.55 s -> 7.59 s = **15.74x speedup**;
- 240 observations: 10.46x speedup;
- 480 observations: 20.74x speedup.

Conclusion: grouping is accepted. It removes the dominant repeated-observation runtime cost but does not solve certificate closure.

#### v14c — coupled likelihood-ratio bounds

`docs/science/results/s1-coupled-continuous-bound-benchmark-v14c.md`

Instead of separately bounding rotated-alternative likelihood below and null likelihood above, v14c bounds `log L_rot(theta)-log L_null(theta)` jointly over the same box using directed interval-gradient / mean-value bounds.

Prospective benchmark:

- run `32038675988`, job `95413986202`;
- exact benchmark head `0fa9fb93ebd0cabc5fafb57044cfb045febab4b2`;
- artifact `9291544853`;
- artifact ZIP SHA256 `6913f6d8156519d7475da067cfbd5b2d5ffcf8bcff0e817bb3d53b1046fe275f`.

Results:

- coupled-bound violations: **0/162** direct high-precision points;
- boxwise lower-bound improvement: min 20.736, median 32.666, max 48.182 log units;
- minimum direct-reference slack improved 25.897 -> 5.161 log units;
- nevertheless aligned 240 and 480 scenarios both still failed to certify within 250 nodes/side;
- coupled search was roughly 4–5x slower because of gradient interval work.

Conclusion: dependence loss in v14a/b was real, but it is **not the dominant remaining closure obstruction**. Do not simply spend more nodes or further tighten bounds without diagnosing why boxes remain unresolved.

## Exact next checkpoint — v14d unresolved-box attribution

Replay the frozen aligned 240- and 480-observation scenarios and instrument every branch-and-bound box by termination path:

1. pruned because entirely inside the target halfspace;
2. pruned by the common-confidence likelihood cutoff;
3. pruned by the cone e-process;
4. split/continued;
5. unresolved at the resolution limit;
6. pending when the node budget is exhausted.

For unresolved/pending boxes record:

- parameter intervals and widths;
- split dimension selected by the current largest-width rule;
- halfspace margin;
- common-likelihood margin;
- v14b grouped cone-e margin;
- v14c coupled cone-e margin;
- direct/dense high-precision survivor diagnostics where feasible.

The goal is to distinguish four hypotheses before changing the certificate:

- common nuisance confidence region too broad;
- directional evidence genuinely insufficient;
- local interval bounds still too loose;
- branch order / largest-width splitting wastes the node budget.

**Do not make the primary v14d experiment a larger node budget. Do not lower precision, relax alpha, widen the cone, or replace certified bounds with approximate optimization.**

## S1 scientific invariants

- Controlled target: `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- Provisional state: `alpha_i=[b_i,beta_i]` in a fixed/versioned feature basis.
- Forced pairwise A/B choice removes the intercept and cannot identify absolute pursuit selectivity alone.
- `A only / B only / Both / Neither` is provisionally represented as two binary acceptability observations; conditional independence remains a testable assumption.
- Population information may be used only as versioned priors supported by suitable evidence.
- No universal feature dimension or calibration-question count is established.
- Every e-process numerator must be normalized and predictable before the current response.
- Adaptive query covariates may depend on the past, not the unseen current outcome.
- Prefer `construct confidence sequence -> certify every retained parameter -> stop` over moving data-dependent null tests.
- Empty confidence sets are model/confidence failure states, not successful certificates.
- `oracle_true` is diagnostic only and must never enter operational acquisition or certification.
- E-process validity is conditional on the likelihood containing the truth.
- Synthetic-domain identification does not establish transfer to real profiles, in-person attraction, relationship formation, compatibility, or long-term relationship quality.

## Required misspecification gates before S1 merge

After the continuous correct-specification certificate is computationally usable, test at minimum:

- nonlinear curvature;
- multimodal preference surfaces;
- pair-context/dependence between the two provisional binary observations;
- generator / feature-basis confounding;
- feature measurement error;
- truth outside the assumed logistic family;
- nuisance intercept and slope magnitude behavior;
- higher-dimensional directional geometry.

PR #12 is not merge-ready until these gates are addressed and the authoritative repository CI remains green.

## Architectural invariants

- Mobile: React Native + Expo + TypeScript.
- Database/auth/storage: Supabase/PostgreSQL unless changed by ADR.
- Scientific/application engine: Python + FastAPI.
- Monorepo unless changed by ADR.
- Scientific logic is server-authoritative; do not duplicate model equations or decision semantics in mobile.
- Raw experimental responses are immutable evidence.
- Derived scores, posteriors, confidence sets, predictions, and rankings are separate versioned persistence classes.
- Scientifically meaningful output must retain model/policy/implementation versions and sufficient provenance for reconstruction.
- Database changes are migration-backed; never rewrite deployed migration history.
- Privileged/service-role credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous; do not log raw auth IDs, tokens, request bodies, raw science UUIDs, answers, or generated artifacts.

## Authoritative CI

`.github/workflows/phase7-operational-hardening.yml` is the broad PR gate. Do not weaken it to make CI green.

One-use science workflows should be retired after their results and artifact provenance are recorded.

## Required reading before substantial continuation

1. `docs/science/README.md`
2. `docs/science/results/s1-coupled-continuous-bound-benchmark-v14c.md`
3. `docs/science/results/s1-grouped-continuous-runtime-v14b.md`
4. `docs/science/results/s1-continuous-bound-validation-v14a.md`
5. `docs/science/results/s1-acquisition-benchmark-v13k.md`
6. `docs/science/results/s1-cone-cover-benchmark-v13j.md`
7. `docs/science/s1-anytime-likelihood-confidence.md`
8. v12a–v12e result documents for the rejected posterior-q95 branch.
9. v7a–v11a result documents for the geometry/sample-complexity chain.
10. `docs/science/s1-identifiable-preference-model.md`, ADR 0009, and architecture/roadmap docs when changing interfaces or persistence.

## Handoff requirement

Before handing the project to another agent after substantive work, leave repository evidence of:

- exact question attempted;
- method and frozen assumptions;
- what worked;
- what failed and why;
- workflow/run/job/artifact provenance;
- current branch/PR state;
- next exact checkpoint;
- unresolved identifiability, validity, misspecification, and transfer assumptions.

Use repository documents, commits, CI records, and issues rather than relying on chat context.