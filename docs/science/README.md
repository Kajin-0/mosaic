# Mosaic Scientific Inference Program

## Status

Active. Preliminary infrastructure Phases 0–8 are complete; scientific model work begins here.

## Governing objective

Mosaic ultimately aims to improve the probability and expected quality of mutually satisfying long-term relationships. No upstream model should be confused with that terminal objective.

```text
controlled observation
        ↓
latent/effective individual state
        ↓
directional candidate prediction
        ↓
dyadic/relationship outcome prediction
```

A model is only allowed to claim the level its evidence validates.

## Scientific workstreams

### S1 — Identifiable individual preference model — ACTIVE

Question: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

Primary document: `s1-identifiable-preference-model.md`.

Current experimental boundary: `results/s1-fair-best-first-search-benchmark-v14g.md`.

### Core S1 conclusions

1. **Mean directional sample complexity:** v11a supports `eta_F=B^2 kappa E[sigma(BZ)(1-sigma(BZ))]` as a synthetic large-dimensional mean-risk coordinate, not an individual stopping guarantee.
2. **Rejected posterior stopping family:** v12a–v12e show Gaussian/Laplace angular-q95 statistics are not trustworthy finite-sample sequential confidence under the tested protocol. This family is closed without a new theorem.
3. **Anytime-valid route:** v13 establishes predictable normalized numerator -> e-process confidence sequence -> geometry of the retained parameter set -> stop.
4. **Nested representation:** v13f establishes the running intersection `C_t^cap` as the preferred finite-grid confidence representation; valid past rejections must not re-enter.
5. **Leading finite-grid numerator:** v13j's geometrically prespecified outside-cone mixture reaches 88.48% strict-target stopping by 240 observations versus 71.29% for nested all-grid mixture on 1,536 fresh paths, with 264 cone-cover-only stops and zero mixture-only stops.
6. **Acquisition boundary:** v13k shows survivor-focused acquisition improves early stopping but not 240-observation completion and increases observed exclusion/false-stop rates. Historical all-grid current disagreement remains the finite-grid reference.
7. **Continuous arithmetic:** v14a–v14c establish a conservative continuous two-slope certificate with free intercept/slope magnitude, exact rational cone geometry, directed 60-digit arithmetic, grouped sufficient statistics, and dependency-aware coupled likelihood-ratio bounds.
8. **Failure attribution:** v14d proves the aligned-240 side-0 path has a genuinely retained outside-cone point, while the 480 frontiers are predominantly numerical/search problems.
9. **Search-policy boundary:** v14e–v14g show both split choice and frontier order matter, but even a fair cached best-first policy fails to certify either 480 side under the same finite bound-evaluation budget. Search-policy tuning is now closed.
10. **Next target:** improve the certified outer representation of the common confidence region without changing its e-process or alpha allocation.

## Anytime-valid confidence basis

For any normalized numerator chosen predictably before the current outcome,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under fixed correctly specified `theta`, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.

The preferred finite-grid representation is

\[
C_t^{\cap}=\bigcap_{s\le t}\{\theta:E_s(\theta)<1/\alpha\}
=\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\}.
\]

Rejected parameters do not re-enter. An empty nested set is a confidence/model failure state, not a successful certificate.

## v13 finite-confidence progression

- **v13a:** valid true-null rejection `22/4608=0.477%` at nominal 5%; an outcome-leaking numerator rejected 100%, confirming predictability is essential.
- **v13b:** exact finite confidence-set geometry produced zero false directional stops while truth remained in the confidence set.
- **v13c:** grid refinement helps strict-target efficiency but does not explain the dominant horizon burden.
- **v13d/v13e:** numerator choice changes efficiency under current-time sets, but the ranking was representation-dependent.
- **v13f:** nesting raised all-grid-mixture strict-target stopping from about 7% to about 70% by 240 and became the required finite-grid representation.
- **v13g:** theta-specific leave-null-out MLE collapsed onto ordinary MLE-face and underperformed nested all-grid mixture.
- **v13h:** leave-one-out all-alternative mixture is analytically only a near-threshold-equivalent affine transform of all-grid mixture.
- **v13i:** immediate ±5° alternatives produced zero certificates by 240; sparse support without meaningful separation is ineffective.
- **v13j:** fixed support `{±30,±60,±90,±120,±150,180}` covers the region outside the nominal 27° cone at 30° spacing. On fresh seeds `704..831`, stop rate was 88.48% by 240 versus 71.29% for all-grid mixture; median stop improved 216 -> 210; geometry violations remained zero.
- **v13k:** with v13j certification frozen, nested-survivor disagreement acquisition increased 180-observation stopping from 5.47% to 10.29% (`p≈3.61e-7`) but yielded 87.96% stopping by 240 versus 88.67% historical (`p=0.538`). It also raised truth exclusion from 3.26% to 3.78% and false-stop rate from 0.46% to 1.30%. The candidate is not promoted.

## v14 continuous-confidence progression

The continuous route is required because a finite angular grid cannot certify between-grid parameters or handle free nuisance intercept and slope magnitude exactly.

For a two-dimensional slope vector, the accepted direction cone is conservatively represented with exact rational `tan(delta_cert)=1/2`, giving `delta_cert=atan(1/2)≈26.565°`, slightly narrower than the nominal 27° target. The outside-cone region is the union of two halfspace violations.

Confidence budget:

- `alpha_0=0.005` for a common predictable-numerator confidence sequence used to bound nuisance parameters;
- `alpha_c=0.045` for the candidate-specific cone-cover e-process;
- total at most 0.05 by union bound.

The numerical invariant is non-negotiable: every operational pruning decision must be one-sided in the safe direction. A local optimum or numerical value that can underestimate the best surviving outside-cone parameter is invalid.

### v14a — continuous interval validation

`results/s1-continuous-bound-validation-v14a.md`

60-digit directed `Decimal` likelihood enclosures and exact-rational geometry had zero violations over 864 rotated high-precision checks and zero cone-e lower-bound violations. Bounded branch-and-bound did not close tested full certificates and raw runtime was ~1,523 s.

### v14b — grouped sufficient statistics

`results/s1-grouped-continuous-runtime-v14b.md`

Repeated observations over the 12-point bank were grouped exactly by feature vector/outcome counts. Search outcomes were preserved while runtime fell from 119.55 s to 7.59 s overall, a **15.74x** speedup. Grouping is accepted.

### v14c — coupled likelihood-ratio bound

`results/s1-coupled-continuous-bound-benchmark-v14c.md`

Each rotated-alternative versus null log-likelihood ratio is bounded jointly over the same box rather than subtracting independent likelihood bounds.

- zero violations on 162 high-precision points;
- lower-bound improvement 20.74–48.18 log units, median 32.67;
- minimum direct-reference slack 25.90 -> 5.16 log units;
- neither aligned 240 nor 480 case certified within 250 nodes/side.

Dependency loss was real but not the dominant obstruction.

### v14d — unresolved-box attribution

`results/s1-unresolved-box-attribution-v14d.md`

A high-precision direct probe on aligned-240 side 0 is genuinely retained outside the target cone:

```text
theta ~= [0.67584, 1.25355, -0.69181]
halfspace value ~= -0.06503
common direct survival margin ~= +9.8953
cone direct survival margin ~= +4.0638
```

Thus aligned-240 side 0 is **not certifiable under the current confidence construction**. It is a required negative control for every search-only change.

At 480 observations no final frontier probe survived both filters. Common-confidence pruning was the largest prune class. Coupled cone pruning was materially stronger than the older grouped bound.

### v14e — exhaustive preview/best-first

`results/s1-certified-search-allocation-v14e.md`

Same confidence procedure and 250 processed nodes, but every legal split dimension was previewed and the active set processed best-first.

- 240 side0 unresolved `13 -> 7`, 768 previews, 222.62 s;
- 480 side0 `10 -> 3`, 756 previews, 252.41 s;
- 480 side1 `9 -> 5`, 762 previews, 249.95 s;
- zero certificates.

This proves search allocation matters but the policy is computationally unfair/impractical.

### v14f — sensitivity-guided split only

`results/s1-sensitivity-guided-split-benchmark-v14f.md`

Exposes the exact per-axis mean-value penalties already used by v14c and splits the axis with the largest penalty. Tests require exact `Decimal` equality with the production v14c lower bound. DFS order remains unchanged.

- 240 side0 unresolved `13 -> 11`, 44.63 s;
- 480 side0 `10 -> 9`, 46.09 s;
- 480 side1 `9 -> 7`, 54.40 s;
- zero certificates.

Split-axis information is real but insufficient.

### v14g — fair cached best-first frontier order

`results/s1-fair-best-first-search-benchmark-v14g.md`

Holds v14f splitting fixed. Every generated child is evaluated once, cached, and charged against the same finite bound-evaluation budget; there are no free previews.

- run `32042363933`, job `95423839819`, exact head `cc2d71a2d34328a31bd9d03d2c29d5d139159c78`;
- artifact `9292214551`;
- 240 side0: unresolved `11 -> 2` at 249 evaluations, 44.93 s, negative control preserved;
- 480 side0: `9 -> 5`, 51.14 s;
- 480 side1: `7 -> 4`, 51.15 s;
- zero certificates.

This is strong fair-work evidence that frontier order matters, but it does not close either 480 case. **Search-policy tuning is now closed for this certificate architecture.**

## Current finite-grid reference

```text
historical all-grid current disagreement acquisition
        ↓
candidate-specific cone-cover e-process
        ↓
nested confidence sequence
        ↓
global finite-grid MLE reporting direction
        ↓
exact radius over every retained direction
        ↓
strict directional certificate
```

Do not hand-tune numerator supports or acquisition mixtures on v13j/v13k outcomes.

## Current continuous stack and next checkpoint

```text
predictable binary evidence
        ↓
0.5% common e-process
        ↓
certified outer common-confidence region
        ↓
4.5% candidate-specific cone-cover e-process
        ↓
exact rational outside-cone halfspaces
        ↓
grouped sufficient statistics
        ↓
directed 60-digit coupled bounds
        ↓
certified outside-cone exclusion
```

The next checkpoint is **v14h certified common-confidence region tightening**.

The current implementation converts the common confidence sequence into one broad axis-aligned nuisance box. This is only an outer approximation to the true convex logistic log-likelihood superlevel set. v14d–v14g show that the directional search then spends substantial certified work rediscovering that common constraint locally.

v14h should change only the outer representation of the common confidence region:

1. preserve the common likelihood cutoff and `alpha_0=0.005` exactly;
2. for intercept, `beta_x`, and `beta_y`, derive rigorous lower/upper coordinate extrema containing every common-CS point;
3. use certified outer bounds, not ordinary numerical optimizer output;
4. validate no direct high-precision retained point is excluded;
5. measure nuisance-box width/volume reduction;
6. replay the frozen directional certificate from the tightened box under the same work budget;
7. preserve the aligned-240 side-0 negative-control failure;
8. do not change alpha allocation, cone, numerator, directional e-process, or arithmetic precision in the same checkpoint.

Logistic log-likelihood is concave, so its superlevel set is convex. Coordinate extrema can be framed as convex optimization problems, but operational bounds require rigorous solver/duality/interval error control in the safe outer direction.

Do not return to search-policy tuning, increase the primary budget as the experiment, lower precision, widen the cone, reallocate alpha post hoc, or use a local optimum as a certificate.

## Remaining S1 gates

After continuous correct-specification certification is computationally usable, S1 still requires deliberate misspecification tests including nonlinear curvature, multimodality, pair-context dependence, generator/feature-basis error, feature measurement error, truth outside the logistic family, nuisance behavior, and higher-dimensional geometry.

Synthetic truth may be used only for evaluation and explicitly labeled oracle diagnostics. It must never enter an operational confidence statistic or query decision.

### Later workstreams

These are deliberately not treated as solved:

- transfer from synthetic candidates to real profile decisions;
- contextual/profile preference inference;
- visual × contextual interactions;
- relationship-relevant self/partner psychometrics;
- directional attraction `A → B` and `B → A`;
- dyadic compatibility and risk;
- relationship formation and longitudinal quality `Q_AB(t)`;
- population-level allocation/global matching.

## Scientific discipline

For every model:

1. define the observable quantity first;
2. state the latent/effective parameterization;
3. prove or state identifiability assumptions;
4. distinguish population prior from individual evidence;
5. retain uncertainty;
6. version feature basis, likelihood, model, and query policy;
7. preserve raw observations independently from derived outputs;
8. test model misspecification rather than automatically increasing complexity;
9. distinguish synthetic/analytic validation from real-world external validation; and
10. never treat infrastructure success as scientific validation.
