# Mosaic Scientific Inference Program

## Status

Active. Preliminary infrastructure Phases 0–8 are complete; scientific model work begins here.

## Governing objective

Mosaic ultimately aims to improve the probability and expected quality of mutually satisfying long-term relationships. No single upstream model should be confused with that terminal objective.

The scientific program separates:

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

Current experimental boundary: `results/s1-coupled-continuous-bound-benchmark-v14c.md`.

The controlled S1 program now has eight distinct conclusions that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate `eta_F=B^2 kappa E[sigma(BZ)(1-sigma(BZ))]` for mean ranking error under the correctly specified passive controlled-geometry model;
2. **rejected posterior stopping family:** v12a–v12e show that Gaussian/Laplace angular-q95 statistics do not provide trustworthy finite-sample sequential confidence under the tested protocol;
3. **anytime-valid confidence route:** v13a–v13b establish `predictable normalized numerator -> e-process confidence sequence -> exact confidence-set geometry -> stop` on a finite grid;
4. **nested representation:** v13f establishes the running intersection `C_t^cap=intersection_{s<=t} C_s` as the preferred finite-grid confidence representation because valid past rejections must not be allowed to re-enter;
5. **numerator-design boundary:** v13g–v13i show that neither leave-null-out MLE, near-equivalent leave-one-out all-alternative mixtures, nor extremely local ±5-degree alternatives solve efficiency. Prior dilution and null/alternative separation must be considered jointly;
6. **leading finite-grid numerator:** v13j's geometrically prespecified 11-point outside-cone mixture reaches **88.48%** strict-target stopping by 240 observations versus **71.29%** for the nested all-grid mixture on 1,536 fresh paths, with 264 cone-cover-only stops, zero mixture-only stops, and zero geometry violations;
7. **acquisition boundary:** v13k shows that focusing queries on nested cone-cover survivors doubles the 180-observation stop rate but does **not** improve 240-observation completion and increases observed truth-exclusion/false-stop rates. The historical all-grid current disagreement controller remains the finite-grid default;
8. **continuous numerical boundary:** v14a–v14c establish a conservative continuous 2-D-slope certificate architecture with free intercept and slope magnitude, exact rational cone geometry, directed 60-digit arithmetic, and branch-and-bound. Grouped sufficient statistics give a 15.74x runtime improvement, and dependency-aware likelihood-ratio bounds tighten tested box lower bounds by a median 32.67 log units with zero direct-reference violations, but even aligned strong-signal cases still do not close under the frozen 250-node budget. The next problem is attribution of the unresolved boxes, not another unmotivated bound tweak.

The v12 family is closed. Do not resume Laplace-q95 tuning without a new theorem-level justification.

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

Rejected parameters do not re-enter later. An empty nested set is a confidence/model failure state, not a successful certificate.

### v13 finite-confidence progression

- **v13a:** valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an intentionally outcome-leaking numerator rejected 100%, demonstrating the predictability requirement.
- **v13b:** exact finite confidence-set geometry produced zero false directional stops while truth remained in the confidence set.
- **v13c:** grid refinement helps strict-target efficiency but does not explain the dominant horizon burden.
- **v13d/v13e:** numerator choice materially changes efficiency under current-time sets, but that ranking was representation-dependent.
- **v13f:** nesting increased all-grid-mixture strict-target stopping from about 7% to about 70% by 240 observations and became the required finite-grid representation.
- **v13g:** theta-specific leave-null-out MLE collapsed onto ordinary MLE-face and underperformed nested all-grid mixture.
- **v13h:** leave-one-out all-alternative mixture is analytically only a near-threshold-equivalent affine transform of all-grid mixture.
- **v13i:** immediate ±5-degree alternatives produced zero certificates by 240; sparse support without meaningful separation is ineffective.
- **v13j:** fixed support at offsets `{±30,±60,±90,±120,±150,180}` degrees covers the entire region outside the 27-degree target cone at 30-degree spacing. On fresh seeds `704..831`, stop rate was 88.48% by 240 versus 71.29% for all-grid mixture; median stop improved 216 -> 210; geometry violations remained zero. Cone-cover is the current leading finite-grid numerator.
- **v13k:** with v13j certification frozen, nested-survivor disagreement acquisition increased 180-observation stopping from 5.47% to 10.29% (`p≈3.61e-7`) but yielded 87.96% stopping by 240 versus 88.67% for the historical controller (`p=0.538`). It also raised truth exclusion from 3.26% to 3.78% and false-stop rate from 0.46% to 1.30%; geometry violations remained zero. The candidate is not promoted.

### v14 continuous-confidence progression

The continuous route is required because a finite angular grid cannot certify parameters between grid points or handle free nuisance intercept and slope magnitude exactly.

For a two-dimensional slope vector, the accepted direction cone can be conservatively represented using the exact rational wedge `tan(delta_cert)=1/2`, giving `delta_cert=atan(1/2)≈26.565°`, slightly narrower than the nominal 27° target. The outside-cone region is the union of two halfspace violations.

The current confidence budget is split conservatively:

- `alpha_0=0.005` for a common predictable-numerator confidence sequence used to construct a finite nuisance box;
- `alpha_c=0.045` for the candidate-specific cone-cover e-process;
- `alpha_0+alpha_c=0.05` total by union bound.

The numerical invariant is non-negotiable: every pruning decision used for stopping must be one-sided in the safe direction. A local optimum or numerical value that can underestimate the best surviving outside-cone parameter is invalid.

- **v14a — continuous interval validation:** 60-digit directed `Decimal` likelihood enclosures and exact-rational geometry had zero violations over 864 rotated high-precision likelihood checks and zero cone-e lower-bound violations. However, bounded branch-and-bound did not close any tested full certificate despite dense diagnostics showing no outside-cone survivors, and the raw implementation took about 1,523 seconds.
- **v14b — grouped sufficient statistics:** repeated observations over the 12-point candidate bank were grouped exactly by feature vector and outcome counts. Directed integer multiplication preserved the same inequalities and search outcomes while reducing the runtime comparison from 119.55 s to 7.59 s overall, a **15.74x** speedup; 240-observation speedup was 10.46x and 480-observation speedup was 20.74x. This solved the dominant raw-observation runtime cost but not certificate looseness.
- **v14c — coupled likelihood-ratio bounds:** each rotated-alternative versus null log-likelihood ratio was bounded jointly over the same parameter box rather than subtracting independent alternative-lower and null-upper bounds. Across 162 high-precision points there were **zero violations**. The lower bound improved every tested box by 20.74–48.18 log units, median **32.67**, and minimum direct-reference slack fell from 25.90 to 5.16 log units. Nevertheless neither aligned 240- nor 480-observation scenario certified within 250 nodes per side, and the extra interval-gradient work made the tested search roughly 4–5x slower. Dependence loss was real but is not the dominant remaining closure obstruction.

### Current finite-grid conclusion

The finite-grid reference route remains:

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

Do not hand-tune further numerator supports or acquisition mixtures on v13j/v13k outcomes.

### Current continuous conclusion and next checkpoint

The current continuous method stack is:

```text
predictable binary evidence
        ↓
0.5% common e-process -> certified finite nuisance box
        ↓
4.5% candidate-specific cone-cover e-process
        ↓
exact rational outside-cone halfspaces
        ↓
grouped sufficient statistics
        ↓
directed 60-digit interval bounds
        ↓
branch-and-bound outside-cone exclusion
```

v14c shows that another generic attempt to tighten the likelihood box bound is not justified yet. The exact next checkpoint is **v14d unresolved-box attribution**.

For both aligned 240- and 480-observation scenarios, replay the frozen search and count boxes by termination path:

1. target-halfspace geometry prune;
2. common-confidence likelihood prune;
3. cone-e-process prune;
4. split/continued;
5. resolution-limit unresolved;
6. node-limit pending.

For unresolved and pending boxes, record parameter widths, split dimension, common-likelihood margin, v14b grouped cone-e margin, v14c coupled cone-e margin, and dense/high-precision point diagnostics where feasible. The purpose is to distinguish four hypotheses before changing the algorithm:

- the common nuisance confidence region is still too broad;
- directional evidence is genuinely insufficient;
- local interval bounds remain too loose;
- the fixed largest-width DFS splitting policy wastes the node budget.

Do not increase the node budget as the primary experiment. Do not lower precision, relax alpha, widen the cone, or replace the certified bound with an approximate optimizer.

After continuous correct-specification validation, S1 still requires explicit misspecification experiments: nonlinear curvature, multimodal preferences, pair-context dependence, generator/feature-basis error, feature measurement error, and synthetic truth outside the assumed likelihood family.

Synthetic truth may be used for evaluation and explicitly labeled oracle diagnostics only. It must never enter an operational confidence statistic or query decision.

### Later workstreams

These are deliberately not yet treated as solved:

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
6. version the feature basis, likelihood, model, and query policy;
7. preserve raw observations independently from derived outputs;
8. test model misspecification rather than automatically increasing complexity;
9. distinguish synthetic/analytic validation from real-world external validation; and
10. never treat infrastructure success as scientific validation.
