# Science S1 v12b — Prospective Stopping-Rule Validation

## Status

Completed fresh-seed prospective synthetic validation.

The prespecified **two-consecutive-crossing** rule replicated the favorable v12a post-hoc aggregate behavior, with aggregate false-stop-given-stop below 5% at all three tested target errors. That is useful evidence that persistence suppresses optional-stopping failures.

However, **the rule is not safe enough to promote as an S1 product stopping rule**. Aggregate pooling hides a large weak-signal/high-dimensional failure. In particular, at `d=12, B=0.55, target=0.25`, two-consecutive crossing false-stopped on `23/89 = 25.8%` of stops.

The 90-query burn-in comparator also failed the prespecified aggregate 5% point-estimate gate at target `0.15` (`5.02%`) and retained the same weak-signal subgroup pathology.

This remains a correctly specified synthetic-model study. It is not human-subject validation, synthetic-to-real attraction transfer, compatibility validation, or relationship-outcome evidence.

## Provenance

- benchmark version: `s1-stopping-validation-benchmark-v12b`
- stopping version: `laplace-angular-sequential-rules-v2`
- executed science head: `eb4773ffc1cb3e112745158d377da77bc5272e16`
- GitHub Actions run: `31884464270`
- benchmark job: `95011628240`
- artifact: `9247044518`
- artifact ZIP SHA-256: `428e6d92267ed0b36de1c6b3411275641d79ce12f3320d5d31380734698d69d9`
- benchmark JSON SHA-256: `53d92bc2917f18c2e1d6ae6426a26baaf464166f0c6a5462507a4f06bdf4d29e`
- benchmark JSON bytes: `16,074,462`
- sequential paths: `1,152`
- posterior refits: `19,584`
- seeds per `(d,B)` condition: `128`
- seeds: `64..191`, disjoint from v12a seeds `0..63`
- complete balanced rounds per path: `17`
- maximum pair queries per path: `153`
- benchmark compute time: approximately `15 min 1 s`

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before benchmark execution.

## Prespecified design

The scientific grid was unchanged from v12a:

\[
d\in\{4,8,12\},\qquad
B\in\{0.55,0.90,1.50\},\qquad
\epsilon_*\in\{0.25,0.20,0.15\}.
\]

The candidate bank, passive balanced round-robin query schedule, Gaussian-prior Laplace fit, and posterior q95 angular statistic were also unchanged.

Three rules were fixed before v12b execution:

1. `single_crossing`: first checkpoint with `U_0.95 <= epsilon*`;
2. `two_consecutive`: first checkpoint completing two consecutive rounds with `U_0.95 <= epsilon*`;
3. `burnin_90`: first checkpoint at or after 90 pair queries with `U_0.95 <= epsilon*`.

The primary safety metric was false-stop-given-stop. The prespecified aggregate point-estimate gate was 5% at every target. Wilson 95% intervals were recorded rather than treating the point estimate as exact.

Synthetic truth was used only to score the operating characteristics after a stopping decision.

## Aggregate result

Across all `1,152` fresh-seed paths:

| Target | Rule | Stop rate | False stop given stop | Wilson 95% | Missed stop at cap | Median pair queries |
|---:|---|---:|---:|---:|---:|---:|
| 0.25 | single crossing | 0.9557 | **0.1035** | 0.0869–0.1229 | 0.0365 | 45 |
| 0.25 | two consecutive | 0.9340 | **0.0465** | 0.0354–0.0607 | 0.0547 | 63 |
| 0.25 | burn-in 90 | 0.9523 | **0.0346** | 0.0253–0.0472 | 0.0391 | 90 |
| 0.20 | single crossing | 0.8021 | **0.0758** | 0.0604–0.0946 | 0.1267 | 72 |
| 0.20 | two consecutive | 0.7561 | **0.0425** | 0.0310–0.0580 | 0.1684 | 81 |
| 0.20 | burn-in 90 | 0.7986 | **0.0370** | 0.0266–0.0512 | 0.1302 | 90 |
| 0.15 | single crossing | 0.5200 | **0.0735** | 0.0552–0.0972 | 0.2691 | 99 |
| 0.15 | two consecutive | 0.4679 | **0.0315** | 0.0198–0.0499 | 0.3194 | 108 |
| 0.15 | burn-in 90 | 0.5191 | **0.0502** | 0.0354–0.0707 | 0.2700 | 99 |

### Aggregate interpretation

The v12a post-hoc persistence signal **replicated prospectively**: two-consecutive crossing remained below the 5% aggregate point gate at all three targets.

The result is nevertheless weaker than a calibrated 5% guarantee. The Wilson upper bound remains above 5% at targets `0.25` and `0.20` for two-consecutive crossing. Only target `0.15` has a two-sided Wilson upper endpoint just below 5%.

The burn-in comparator is not uniformly successful: its target-`0.15` point estimate is already slightly above 5%.

## Dimension dependence of two-consecutive crossing

Pooling signal levels within each dimension:

| d | Target | Stop rate | False stop given stop | Median queries |
|---:|---:|---:|---:|---:|
| 4 | 0.25 | 0.9714 | 0.0188 | 45 |
| 4 | 0.20 | 0.8880 | 0.0323 | 54 |
| 4 | 0.15 | 0.7083 | 0.0257 | 81 |
| 8 | 0.25 | 0.9323 | 0.0391 | 54 |
| 8 | 0.20 | 0.7292 | 0.0357 | 81 |
| 8 | 0.15 | 0.4401 | 0.0296 | 108 |
| 12 | 0.25 | 0.8984 | **0.0841** | 72 |
| 12 | 0.20 | 0.6510 | **0.0640** | 99 |
| 12 | 0.15 | 0.2552 | **0.0510** | 135 |

Persistence substantially reduces the aggregate optional-stopping error, but high dimension remains systematically less safe.

## Signal-strength dependence is stronger

Pooling dimensions within each true synthetic slope norm gives the sharper diagnosis:

| B | Target | Stop rate | False stop given stop | Median queries |
|---:|---:|---:|---:|---:|
| 0.55 | 0.25 | 0.8021 | **0.1234** | 90 |
| 0.55 | 0.20 | 0.3411 | **0.0763** | 117 |
| 0.55 | 0.15 | 0.0625 | **0.0833** | 130.5 |
| 0.90 | 0.25 | 1.0000 | 0.0286 | 63 |
| 0.90 | 0.20 | 0.9297 | 0.0532 | 90 |
| 0.90 | 0.15 | 0.4401 | 0.0473 | 117 |
| 1.50 | 0.25 | 1.0000 | 0.0026 | 45 |
| 1.50 | 0.20 | 0.9974 | 0.0209 | 63 |
| 1.50 | 0.15 | 0.9010 | 0.0202 | 99 |

This is the main v12b result. **Weak directional signal, not optional stopping alone, controls the residual failure.**

A pooled aggregate can therefore look acceptable while the stopping rule remains badly anti-conservative for exactly the users whose individual direction is hardest to identify.

## Worst structured two-consecutive cells

The most important cell is:

`d=12, B=0.55, target=0.25`

- stop rate: `0.6953`;
- stops: `89/128`;
- false stops: `23`;
- false-stop-given-stop: **`0.2584`**;
- Wilson 95% interval: `0.1788–0.3580`;
- median stopping queries: `99`.

This is not a small-denominator accident. The interval excludes 10% and the cell contains 89 stops.

Other materially unsafe cells include:

- `d=12, B=0.90, target=0.20`: `12/111 = 10.8%` false stops;
- `d=8, B=0.55, target=0.20`: `3/34 = 8.8%`;
- `d=4, B=0.55, target=0.20`: `7/85 = 8.2%`;
- `d=8, B=0.55, target=0.25`: `8/102 = 7.8%`.

Cells with one or very few stops can produce unstable percentages and should not be read as population rates, but they still demonstrate that catastrophic isolated false confidence remains possible.

## Fixed-checkpoint coverage confirms the mechanism

The posterior q95 problem is still present without optional stopping.

Selected v12b fixed-checkpoint coverage `P(epsilon_true <= U_0.95)` by `(d,B)` is:

| d | B | q=9 | q=90 | q=153 |
|---:|---:|---:|---:|---:|
| 4 | 0.55 | 0.8281 | 0.9297 | 0.9297 |
| 4 | 0.90 | 0.9219 | 0.9531 | 0.9297 |
| 4 | 1.50 | 0.9922 | 0.9531 | 0.9375 |
| 8 | 0.55 | 0.5781 | 0.8594 | 0.9219 |
| 8 | 0.90 | 0.7656 | 0.9141 | 0.9453 |
| 8 | 1.50 | 0.8672 | 0.9609 | 0.9688 |
| 12 | 0.55 | **0.4297** | **0.7031** | **0.8203** |
| 12 | 0.90 | 0.6953 | 0.8594 | 0.8984 |
| 12 | 1.50 | 0.9375 | 0.9609 | 0.9531 |

At `d=12, B=0.55`, even the final 153-query q95 bound covers the true directional error only about 82% of the time. No amount of first-crossing bookkeeping can turn that posterior quantity into a valid 95% confidence bound.

This explains why persistence helps but cannot solve the weak-signal regime by itself.

## What v12b establishes

Within the tested correctly specified synthetic model:

1. The v12a observation that two consecutive q95 crossings reduce aggregate false stopping **replicates on fresh seeds**.
2. The original single-crossing rule is decisively unsafe, with 7.3–10.4% false-stop-given-stop in aggregate.
3. Two-consecutive crossing passes the prespecified aggregate 5% point gate, but not a uniform or subgroup safety requirement.
4. The 90-query burn-in does not pass the aggregate point gate at every target and offers a materially worse burden profile.
5. Residual stopping failure is concentrated in weak-signal and high-dimensional conditions.
6. The q95 Laplace angular bound remains substantially anti-conservative at fixed checkpoints in those regimes; optional stopping is therefore only one component of the defect.
7. Aggregate pooling is scientifically inadequate for deciding whether an individual calibration stopping rule is safe.
8. None of these results validate the synthetic feature basis, human attraction measurement, transfer to real profiles, dyadic compatibility, or long-term relationship outcomes.

## Post-hoc diagnostic boundary

The v12b paths may be used to generate **hypotheses**, but any rule chosen after looking at this artifact must be validated on a new disjoint seed set.

A simple post-hoc tightening of the angular threshold can almost eliminate v12b false stops, but that is calibration on the evaluation set and is not evidence of prospective safety. It should not be promoted directly.

The mechanistically stronger next question is whether the posterior can distinguish a genuine directional signal from high-dimensional radial noise. v12a already showed severe norm inflation, and v12b shows that weak true `B` drives the residual false stops.

## Next checkpoint

Do **not** promote two-consecutive crossing as the S1 stopping rule yet.

The next stopping experiment should address radial/signal uncertainty explicitly rather than adding another arbitrary query-count delay.

A preferred v12c direction is:

1. retain two-consecutive q95 as the replicated control;
2. compute posterior-observable radial uncertainty from the slope marginal covariance;
3. test a theory-motivated debiased radial signal statistic, e.g.

   \[
   \widehat B_{db}^2=\max\left(\|m\|^2-\operatorname{tr}(\Sigma_\beta),0\right),
   \]

   which removes the first-order noise contribution to squared fitted norm;
4. use that statistic to prevent an inflated noise vector from masquerading as a well-identified preference direction;
5. preserve the same controlled passive geometry and `(d,B,target)` grid;
6. use another seed set disjoint from both v12a and v12b;
7. require aggregate safety **and** report cell-level operating characteristics, especially `B=0.55,d=12`;
8. treat a product query cap as unresolved uncertainty rather than forced calibration success.

A higher posterior angular quantile can be included as a conservative comparator, but the scientific target is the demonstrated radial-noise mechanism rather than blind threshold tuning.