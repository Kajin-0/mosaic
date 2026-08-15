# Science S1 v13a — Finite-Null E-Process Verification

## Status

Completed synthetic method-verification benchmark.

v13a is the first checkpoint after the v12a–v12e Laplace-q95 stopping family was rejected. It does **not** attempt a continuous angular confidence certificate. Instead it tests the more basic sequential-validity machinery in a setting where the composite null is finite, fixed in advance, contains the true parameter in every type-I path, and its likelihood supremum can be computed exactly.

The result is strongly favorable for the e-process logic:

- the valid predictable construction rejected only `22 / 4608 = 0.4774%` of true-null paths by the 80-observation cap, well below the nominal 5% anytime bound;
- the deliberately invalid outcome-leaking numerator rejected `4608 / 4608 = 100%` of null paths, with median stopping observation 6;
- the valid construction had `194 / 512 = 37.89%` power against the fixed alternative by 80 observations, with median stopping observation 70 among rejections.

Therefore the harness cleanly distinguishes predictable sequential evidence from an invalid numerator that sees the current outcome. The construction appears conservative and currently has limited finite-horizon power, but unlike the v12 posterior-q95 family its optional-stopping validity is theorem-backed rather than inferred from calibration simulations.

This remains a synthetic method sanity check. It is not a continuous angular stopping rule, human-subject validation, synthetic-to-real attraction transfer, compatibility validation, or relationship-outcome evidence.

## Provenance

- benchmark version: `s1-finite-null-eprocess-benchmark-v13a`
- method version: `prequential-finite-composite-null-v1`
- executed science head: `0b7039375c4b5229b72865fbb982be485a5ed97d`
- GitHub Actions run: `31903019737`
- benchmark job: `95056556021`
- artifact: `9251599696`
- artifact ZIP SHA-256: `adb80a6707262545f22cd873aa5bf34e8cd7b86541d9d64038f79526636816d0`
- benchmark JSON SHA-256: `27ab1b9537345d40f43eb21a922fbec7b68de606b6f7d1c0f035e92333d3f969`
- benchmark JSON bytes: `2,547,324`
- valid-null paths: `4,608`
- leaky-null paths: `4,608`
- alternative paths: `512`
- null seeds per parameter: `512`
- maximum observations per path: `80`
- nominal alpha: `0.05`
- benchmark compute time: approximately 19 seconds after validation

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before the benchmark ran.

## Prespecified finite problem

Feature dimension was two with zero intercept and slope norm

\[
B=\|\beta\|=0.9.
\]

The fixed alternative direction was 0 degrees. The finite composite null contained nine directions:

```text
-135, -90, -60, -45, 45, 60, 90, 135, 180 degrees
```

so the true parameter was exactly one of the enumerated null points on every type-I path.

The candidate bank contained 12 unit-circle feature vectors. Query selection was adaptive but predictable: before seeing the current outcome, choose the candidate maximizing Bernoulli KL divergence between the fixed alternative predictor and the currently highest-likelihood null parameter.

For the valid construction,

\[
Q_t=\prod_s q_s(Y_s)
\]

used the fixed alternative Bernoulli probability as a normalized predictive numerator. The finite-null statistic was

\[
E_t(H_0)=
\frac{Q_t}{\max_{\theta\in H_0}L_t(\theta)}.
\]

Because the null is finite and explicitly enumerated, the denominator is exact rather than numerically approximated.

A path rejected when

\[
\log E_t(H_0)\ge \log(1/0.05).
\]

The invalid control deliberately violated predictability: after observing `Y_t`, it assigned probability 0.99 to the realized outcome. That numerator is normalized only after seeing the outcome and therefore does not satisfy the prequential martingale condition.

## Aggregate result

| Condition | Runs | Rejections | Rejection rate | Median stop among rejections |
|---|---:|---:|---:|---:|
| Valid true-null e-process | 4,608 | 22 | **0.004774** | 68 |
| Outcome-leaking invalid control | 4,608 | 4,608 | **1.000000** | 6 |
| Valid fixed alternative | 512 | 194 | **0.378906** | 70 |

The valid-null rejection rate is about one tenth of the nominal 5% level. That is not evidence that the true type-I bound is 0.48%; Ville's inequality provides an upper bound, not an equality, and the finite composite-null maximum is expected to create conservatism.

The important observation is qualitative and structural: optional stopping plus adaptive predictable query selection did not create the kind of type-I inflation seen in the v12 posterior-q95 family, while intentional use of current-outcome information destroyed validity completely.

## Null-cell result

| True null angle | Valid rejection rate | Leaky rejection rate |
|---:|---:|---:|
| -135° | 0.000000 | 1.000000 |
| -90° | 0.000000 | 1.000000 |
| -60° | 0.001953 | 1.000000 |
| -45° | 0.021484 | 1.000000 |
| 45° | 0.017578 | 1.000000 |
| 60° | 0.001953 | 1.000000 |
| 90° | 0.000000 | 1.000000 |
| 135° | 0.000000 | 1.000000 |
| 180° | 0.000000 | 1.000000 |

The only appreciable valid-null rejection occurs at the two null directions closest to the fixed 0° alternative. Even there the observed rates, 2.15% and 1.76%, remain below 5%.

## What the benchmark actually verifies

Within this finite correctly specified synthetic problem:

1. a normalized predictable prequential numerator is compatible with adaptive query selection and optional stopping without empirical type-I inflation;
2. exact finite-composite-null maximization retains the fixed-parameter e-process protection;
3. a numerator that uses the current outcome fails catastrophically, so the benchmark is capable of detecting the key predictability assumption violation rather than merely producing low rejection rates for every construction;
4. the valid finite-null method is currently conservative;
5. the particular fixed-alternative numerator/query design is not especially powerful at an 80-observation horizon;
6. simulation supports the implementation but does not replace the martingale/Ville argument;
7. none of this establishes continuous angular confidence-set certification.

## Important theorem boundary

The benchmark uses a **fixed prespecified null set**. It does not justify repeatedly selecting a new angular null around the current fitted direction and testing that moving null as if it were fixed.

The safe operational route remains:

1. construct the anytime-valid parameter confidence sequence

   \[
   C_t(\alpha)=\{\theta:E_t(\theta)<1/\alpha\};
   \]

2. at each time, inspect the geometry of the whole confidence set;
3. stop only when a certified calculation proves that every slope direction represented in `C_t` lies inside an acceptable angular region.

This avoids adaptive hypothesis-selection error because the stopping statement is a deterministic property of an already-anytime-valid confidence set.

## Next checkpoint — v13b finite confidence-set geometry

Do not jump directly to continuous nonlinear optimization yet.

The next checkpoint should extend the finite harness from one fixed composite null to the **entire finite e-process confidence set**. On each path and time:

1. maintain e-values for a finite parameter grid;
2. retain all grid parameters satisfying the confidence threshold;
3. compute the exact angular diameter of the retained slope directions;
4. stop when the finite-grid directional diameter is below a target;
5. verify directly that whenever the true grid parameter remains in the confidence set, the resulting reported direction/radius contains truth;
6. compare burden under alternative numerator predictors only after validity is fixed.

This finite-grid geometry step is important because it tests the intended operational logic—`confidence set -> geometric certification -> stop`—without yet introducing uncertainty from a continuous optimizer.

Only after v13b is correct should the project solve the continuous problem of conservatively upper-bounding the maximum logistic likelihood outside a candidate directional cone.

## Nonclaims

v13a does not establish:

- correctness of the linear-logistic likelihood for people;
- a validated visual feature basis;
- a production query count;
- a continuous angular confidence region;
- efficient user burden;
- synthetic-to-real preference transfer;
- attraction, compatibility, or relationship-quality prediction.
