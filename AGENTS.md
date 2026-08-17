# AGENTS.md

## Project

Mosaic is a mobile-first, research-driven matchmaking system whose terminal objective is mutually satisfying long-term relationships rather than engagement.

## Current stage

**Science S1 — identifiable individual preference model.** Infrastructure Phases 0–8 are complete.

The first defensible observable is a user's **willingness-to-meet probability over a versioned synthetic candidate feature space**, not a universal latent essence called attraction. The provisional identifiable state is a linear-logistic acceptance surface `alpha=[b,beta]`. Ordinary choice data do not separately identify preference magnitude and response consistency without an independent scale anchor.

Current experimental boundary:

`docs/science/results/s1-fair-best-first-search-benchmark-v14g.md`

PR #12 remains draft. Do not merge S1 on current evidence.

## Scientific boundary

### Pre-v14 results

- v7a–v9a: finite query geometry matters; `kappa=2q/(d+1)` alone is not a sufficient finite-dimensional sample-complexity coordinate.
- v10a/v11a: `eta_F=B^2 kappa a(B)` is a useful synthetic large-d mean-risk coordinate, not an individual stopping guarantee.
- v12a–v12e rejected the Laplace/Gaussian angular-q95 stopping family. **Do not revive it with burn-ins, persistence, projections, scalar corrections, or empirical thresholds without a new theorem.**
- v13 establishes the predictable e-process route. For fixed correctly specified `theta`, predictable query covariates, and a normalized numerator chosen before the current outcome, `E_t(theta)=prod q_t(Y_t)/p_theta(Y_t|x_t)` is a nonnegative martingale; Ville yields an anytime-valid parameter confidence sequence.
- v13f makes the running intersection `C_t^cap` the finite-grid default; rejected parameters must not re-enter.
- v13j's geometrically prespecified cone-cover support `{±30,±60,±90,±120,±150,180}` reached 88.48% strict-target stopping by 240 versus 71.29% for nested all-grid mixture, with 264 cone-cover-only paths and zero mixture-only paths.
- v13k showed survivor-focused acquisition improves early stopping but not the 240 endpoint and worsens observed exclusion/false-stop behavior. Retain historical all-grid current disagreement acquisition as the finite-grid reference.

Do not further hand-tune finite-grid numerator supports or acquisition mixtures on these outcomes.

## v14 continuous confidence geometry

Finite angular grids cannot certify between-grid parameters or handle free nuisance intercept and slope magnitude exactly. The continuous construction is deliberately conservative:

```text
predictable binary evidence
        ↓
alpha_0 = 0.005 common e-process
        ↓
certified nuisance region in (intercept, beta_x, beta_y)
        ↓
alpha_c = 0.045 candidate-specific cone-cover e-process
        ↓
exact rational wedge tan(delta_cert)=1/2
        ↓
grouped sufficient statistics
        ↓
60-digit directed interval bounds
        ↓
certified outside-cone exclusion
```

`atan(1/2) ~= 26.565°`, intentionally narrower than the nominal 27° target. Total alpha is at most 0.05 by union bound.

Numerical one-sidedness is non-negotiable. A local optimizer, sampled angular grid, or value that can underestimate an outside-cone survivor cannot be used for stopping.

### v14a — interval validation

`docs/science/results/s1-continuous-bound-validation-v14a.md`

- zero likelihood-enclosure violations over 864 rotated high-precision checks;
- zero cone-e lower-bound violations;
- branch-and-bound did not close tested certificates despite dense diagnostics;
- raw runtime ~1,523 s.

### v14b — grouped sufficient statistics

`docs/science/results/s1-grouped-continuous-runtime-v14b.md`

Exact grouping preserved inequalities and search outcomes while reducing the benchmark runtime 119.55 s -> 7.59 s = **15.74x** overall. Grouping is accepted.

### v14c — coupled likelihood-ratio bounds

`docs/science/results/s1-coupled-continuous-bound-benchmark-v14c.md`

Jointly bounds `log L_rot(theta)-log L_null(theta)` over each box.

- run `32038675988`, job `95413986202`, exact head `0fa9fb93ebd0cabc5fafb57044cfb045febab4b2`;
- artifact `9291544853`;
- zero violations on 162 high-precision points;
- box lower-bound improvement min 20.736, median 32.666, max 48.182 log units;
- minimum direct-reference slack 25.897 -> 5.161;
- aligned 240/480 still did not certify within 250 nodes/side.

Dependence loss was real but not the dominant closure obstruction.

### v14d — unresolved-box attribution

`docs/science/results/s1-unresolved-box-attribution-v14d.md`

- run `32039824342`, job `95417036144`, exact head `34ba694b0beff3fc94634d3cb29710803d13a0b6`;
- artifact `9291792563`.

Critical invariant: aligned-240 side 0 contains a **directly verified outside-cone point surviving both confidence filters**:

```text
theta ~= [0.67584, 1.25355, -0.69181]
halfspace value ~= -0.06503
common direct survival margin ~= +9.8953
cone direct survival margin ~= +4.0638
```

Therefore aligned-240 side 0 cannot legitimately certify under the current confidence construction. Every search-only change must preserve this negative control.

At 480 no final frontier probe survived both filters. Common-confidence pruning remained the largest prune class. Coupled cone prunes across the four searches were `1,20,14,21`; the old grouped bound produced zero.

### v14e — exhaustive child-preview search

`docs/science/results/s1-certified-search-allocation-v14e.md`

Same confidence procedure and 250 processed-node budget; all legal children were previewed and a best-first frontier was used.

- 240 side0: unresolved `13 -> 7`, 768 previews, 222.62 s;
- 480 side0: `10 -> 3`, 756 previews, 252.41 s;
- 480 side1: `9 -> 5`, 762 previews, 249.95 s;
- zero certificates.

Search allocation matters, but exhaustive previews are too expensive and unfair as a work comparison.

### v14f — sensitivity-guided split only

`docs/science/results/s1-sensitivity-guided-split-benchmark-v14f.md`

Uses the exact per-axis mean-value penalties already inside the v14c bound; diagnostic and production lower bounds are required to be bit-for-bit `Decimal` equal. DFS order unchanged.

- run `32041812151`, job `95422341619`, exact head `c47ba897345c175cba96580a1a5552ad385b877e`;
- artifact `9292130909`;
- 240 side0: unresolved `13 -> 11`, 44.63 s, negative control preserved;
- 480 side0: `10 -> 9`, 46.09 s;
- 480 side1: `9 -> 7`, 54.40 s.

Split-axis information is real and cheap, but insufficient.

### v14g — fair cached best-first frontier order

`docs/science/results/s1-fair-best-first-search-benchmark-v14g.md`

Holds the v14f split rule fixed and changes only frontier order. Every generated child is evaluated exactly once, cached, and charged against the same finite work budget. No free previews.

- run `32042363933`, job `95423839819`;
- exact head `cc2d71a2d34328a31bd9d03d2c29d5d139159c78`;
- artifact `9292214551`;
- ZIP SHA256 `fd0e83adc84d116d47a6b196cb59e739b4f45497f4dd9f259d2842c2466d60a5`;
- JSON SHA256 `b7164e537e242c6e04d1e43711696a855d5352cf047a82ec2bae58aa7dd49acd`.

Under the nominal 250-evaluation budget, v14g uses 249 because each split requires both children:

- 240 side0: unresolved `11 -> 2`, 44.93 s, **not certified**;
- 480 side0: `9 -> 5`, 51.14 s, not certified;
- 480 side1: `7 -> 4`, 51.15 s, not certified.

This is strong fair-work evidence that frontier order matters, but **zero 480 cases certify**. The search-policy branch is now closed for the current certificate architecture. Do not continue hand-tuning frontier scores, split rules, or primary work budgets on these scenarios.

## Exact next checkpoint — v14h common-confidence region tightening

v14d–v14g point upstream to the common confidence-region representation.

The current 0.5% common confidence sequence is converted first into one broad axis-aligned nuisance box. That box is only an outer approximation to the true convex logistic log-likelihood superlevel set, and the directional search spends substantial work rediscovering the curved common constraint box by box.

v14h should keep the **same common e-process, `alpha_0=0.005`, `alpha_c=0.045`, cone, numerator, directional e-process, and directed arithmetic**, but improve only the outer representation of the common confidence region.

Preferred route: certified coordinate-wise tightening.

1. Preserve the common log-likelihood cutoff exactly.
2. For intercept, `beta_x`, and `beta_y`, compute rigorous lower/upper coordinate bounds containing every parameter satisfying the common-confidence likelihood constraint.
3. Use one-sided certified optimization/bounds, not an ordinary local optimizer.
4. Validate that high-precision retained points are never excluded.
5. Measure width/volume reduction independently.
6. Replay the frozen directional certificate from the tighter outer box under the same work budget.
7. Aligned-240 side 0 must remain uncertified because its direct retained outside-cone point is known.

Logistic log-likelihood is concave, so the common retained superlevel set is convex. Coordinate extrema are convex optimization problems, but operational bounds still require rigorous solver/duality/interval error control in the safe outer direction.

Do **not** reallocate alpha post hoc, lower precision, widen the cone, use a local optimum as a certificate, or return to search-policy tuning.

## S1 scientific invariants

- Controlled target: `P(willing to meet | synthetic candidate, instrument, evidence, model, basis)`.
- Provisional state: `alpha_i=[b_i,beta_i]` in a fixed/versioned feature basis.
- Forced pairwise A/B choice removes the intercept and cannot identify absolute pursuit selectivity alone.
- `A only / B only / Both / Neither` is provisionally represented as two binary acceptability observations; conditional independence remains testable.
- No universal feature dimension or calibration-question count is established.
- Every e-process numerator must be normalized and predictable before the current response.
- Adaptive query covariates may depend on the past, not the unseen current outcome.
- Prefer `construct confidence sequence -> certify every retained parameter -> stop` over moving data-dependent null tests.
- Empty confidence sets are model/confidence failure states, not successful certificates.
- `oracle_true` is diagnostic only and must never enter operational acquisition or certification.
- E-process validity is conditional on the likelihood containing the truth.
- Synthetic-domain identification does not establish transfer to real profiles, in-person attraction, relationship formation, compatibility, or long-term relationship quality.

## Required misspecification gates before S1 merge

After the continuous correct-specification certificate is computationally usable, test at minimum nonlinear curvature, multimodality, pair-context dependence, generator/feature confounding, feature measurement error, truth outside the logistic family, nuisance behavior, and higher-dimensional geometry.

PR #12 is not merge-ready until these gates are addressed and the authoritative repository CI remains green.

## Architectural invariants

- Mobile: React Native + Expo + TypeScript.
- Database/auth/storage: Supabase/PostgreSQL unless changed by ADR.
- Scientific/application engine: Python + FastAPI.
- Monorepo unless changed by ADR.
- Scientific logic is server-authoritative.
- Raw experimental responses are immutable evidence.
- Derived states/predictions/rankings are separate versioned persistence classes.
- Scientific output retains model/policy/implementation versions and reconstruction provenance.
- Database changes are migration-backed; never rewrite deployed history.
- Privileged/service-role credentials must never enter the mobile bundle or repository.
- Science-service observability is pseudonymous; do not log raw IDs, tokens, request bodies, answers, or generated artifacts.

## Authoritative CI

`.github/workflows/phase7-operational-hardening.yml` is the broad PR gate. Do not weaken it to make CI green.

One-use science workflows must be retired after results and artifact provenance are recorded.

## Required reading before continuation

1. `docs/science/README.md`
2. `docs/science/results/s1-fair-best-first-search-benchmark-v14g.md`
3. `docs/science/results/s1-sensitivity-guided-split-benchmark-v14f.md`
4. `docs/science/results/s1-certified-search-allocation-v14e.md`
5. `docs/science/results/s1-unresolved-box-attribution-v14d.md`
6. `docs/science/results/s1-coupled-continuous-bound-benchmark-v14c.md`
7. `docs/science/results/s1-grouped-continuous-runtime-v14b.md`
8. `docs/science/results/s1-continuous-bound-validation-v14a.md`
9. `docs/science/results/s1-acquisition-benchmark-v13k.md`
10. `docs/science/results/s1-cone-cover-benchmark-v13j.md`
11. `docs/science/s1-anytime-likelihood-confidence.md`
12. v12a–v12e for the rejected posterior-q95 branch.
13. v7a–v11a for the geometry/sample-complexity chain.
14. `docs/science/s1-identifiable-preference-model.md`, ADR 0009, and architecture/roadmap docs when changing interfaces or persistence.

## Handoff requirement

Before handing the project to another agent after substantive work, leave repository evidence of the exact question, frozen method/assumptions, what worked, what failed and why, workflow/run/job/artifact provenance, current branch/PR state, next exact checkpoint, and unresolved identifiability/validity/misspecification/transfer assumptions.

Use repository documents, commits, CI records, and issues rather than relying on chat context.