# Science S1 v12e — Tangent-Space Directional Stopping

## Status

Completed prospective fresh-seed synthetic validation.

v12e tested the mechanistic refinement proposed after v12d: remove pure longitudinal posterior perturbations before converting uncertainty into angular ranking error. For fitted slope mean `m`, fitted direction

\[
u=\frac{m}{\|m\|},
\]

and posterior slope perturbation `delta`, v12e projected

\[
\delta_\perp=(I-uu^T)\delta
\]

and evaluated angular uncertainty from the transverse perturbation while retaining the v12d transverse-debiased signal norm.

The construction recovered the strict high-dimensional strong-signal utility that v12c/v12d lacked, but it did so by becoming badly anti-conservative. The primary `tangent_two_consecutive` rule failed both aggregate and adequately sampled subgroup safety gates at every tested target.

Therefore the tangent-space Laplace-q95 construction is **rejected** as the S1 stopping rule.

This result triggers the prespecified boundary from v12d: stop refining the Laplace posterior-q95 family with additional scalar corrections, projections, burn-ins, persistence constants, or tuned thresholds. The next stopping investigation must use a different finite-sample / sequential confidence construction.

This is a correctly specified synthetic-model result only. It is not human-subject validation, synthetic-to-real attraction transfer, compatibility validation, or relationship-outcome evidence.

## Provenance

- benchmark version: `s1-tangent-stopping-benchmark-v12e`
- executed science head: `1661542c3cdc9f27e185cde7d6edfa7ccf6d113f`
- GitHub Actions run: `31895518174`
- benchmark job: `95038132367`
- artifact: `9249864920`
- artifact ZIP SHA-256: `ae0495fd0329e504a7e3ec01a7b63bc4d78fbafea4dd805b9129c336a1a62147`
- benchmark JSON SHA-256: `b5e6768fcf3e2ce9be202c2feb6ee353b88465ee5e4969fc4d0a00a257170965`
- benchmark JSON bytes: `37,531,357`
- sequential paths: `1,152`
- seeds per `(d,B)` condition: `128`
- seeds: fresh and disjoint from v12a–v12d seeds `0..447`
- complete balanced rounds per path: `17`
- maximum pair queries per path: `153`
- benchmark compute time: approximately `15 min 14 s`

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before any v12e evaluation path was simulated.

## Prespecified comparison

The controlled grid, candidate geometry, pair schedule, prior, logistic likelihood, query cap, and safety/utility gates were unchanged from v12c/v12d.

Four rules were compared on identical fresh response paths:

1. `raw_two_consecutive`;
2. `transverse_full_noise_two_consecutive` — v12d control;
3. `tangent_single`;
4. `tangent_two_consecutive` — primary.

The primary rule retained the existing gates:

- aggregate false-stop-given-stop Wilson 95% upper bound <=5% at every target;
- every `(d,B,target)` cell with at least 32 stops must have false-stop-given-stop <=10%;
- for `B=1.5`, stop rate >=90% at targets 0.25 and 0.20 and >=60% at target 0.15.

## Primary gate

```text
aggregate_safe = false
subgroup_safe = false
strong_signal_safe = true
overall_pass = false
```

The tangent construction therefore solved the utility failure only by sacrificing calibrated safety.

## Aggregate results

| Target | Rule | Stop rate | False stop given stop | Wilson 95% upper | Missed stop at cap | Median pair queries |
|---:|---|---:|---:|---:|---:|---:|
| 0.25 | raw two-consecutive | 0.9201 | 0.0604 | 0.0764 | 0.0720 | 63 |
| 0.25 | transverse full-noise two-consecutive | 0.8281 | 0.0241 | 0.0359 | 0.1562 | 72 |
| 0.25 | tangent single | 0.9549 | 0.2536 | 0.2802 | 0.0417 | 27 |
| 0.25 | tangent two-consecutive | **0.9349** | **0.1179** | **0.1386** | 0.0582 | 45 |
| 0.20 | raw two-consecutive | 0.7396 | 0.0575 | 0.0752 | 0.1866 | 81 |
| 0.20 | transverse full-noise two-consecutive | 0.6571 | 0.0343 | 0.0498 | 0.2604 | 90 |
| 0.20 | tangent single | 0.8281 | 0.2044 | 0.2312 | 0.1111 | 54 |
| 0.20 | tangent two-consecutive | **0.7847** | **0.1073** | **0.1292** | 0.1450 | 63 |
| 0.15 | raw two-consecutive | 0.4314 | 0.0523 | 0.0755 | 0.3533 | 99 |
| 0.15 | transverse full-noise two-consecutive | 0.3811 | 0.0342 | 0.0556 | 0.4010 | 108 |
| 0.15 | tangent single | 0.5460 | 0.1590 | 0.1896 | 0.2569 | 81 |
| 0.15 | tangent two-consecutive | **0.4905** | **0.1062** | **0.1343** | 0.3056 | 90 |

The primary tangent rule misses the 5% safety objective by a large margin, not a borderline confidence interval.

## Subgroup failures

The primary rule had 22 cells with at least 32 stops. Multiple adequately sampled cells exceeded the prespecified 10% false-stop-given-stop gate.

Representative failures:

| d | B | Target | Stops / 128 | Stop rate | False stop given stop |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.55 | 0.25 | 124 | 0.9688 | 0.1452 |
| 4 | 0.55 | 0.20 | 104 | 0.8125 | 0.1346 |
| 8 | 0.55 | 0.25 | 95 | 0.7422 | 0.1579 |
| 8 | 0.55 | 0.20 | 37 | 0.2891 | 0.2162 |
| 8 | 0.90 | 0.25 | 128 | 1.0000 | 0.1250 |
| 12 | 0.55 | 0.25 | 90 | 0.7031 | 0.3778 |
| 12 | 0.90 | 0.25 | 128 | 1.0000 | 0.1797 |
| 12 | 0.90 | 0.20 | 112 | 0.8750 | 0.1875 |
| 12 | 1.50 | 0.20 | 128 | 1.0000 | 0.1016 |
| 12 | 1.50 | 0.15 | 109 | 0.8516 | 0.1193 |

The weak-signal/high-dimensional failure is especially severe: at `d=12, B=0.55, target=0.25`, 34 of 90 tangent two-consecutive stops were false.

## Strong-signal utility

Unlike v12c and v12d, the tangent primary rule passed the strong-signal burden/utility requirement. In particular, at the previously limiting `d=12, B=1.5, target=0.15` condition it stopped on

```text
109 / 128 = 85.16%
```

of paths, well above the 60% floor.

That recovery cannot be accepted because 13 of those 109 stops were false (`11.93%`). The desired operating point is therefore not recovered by simply removing longitudinal posterior perturbations.

## Interpretation

v12c and v12d showed that the raw Laplace angular q95 statistic is harmed by radial/noise inflation and that conservative norm debiasing can restore much of the safety. v12e shows the complementary failure: projecting all posterior perturbations into the tangent subspace removes too much finite-sample uncertainty and creates false confidence.

This matters conceptually. The finite-sample ranking uncertainty is not captured by either extreme:

```text
full Gaussian posterior perturbation
```

or

```text
pure first-order tangent perturbation.
```

Longitudinal uncertainty is first-order irrelevant to infinitesimal rotation, but it still couples to direction through finite perturbations, sign changes, curvature of the unit sphere, and uncertainty in the fitted reference direction itself. The Laplace Gaussian approximation also remains only an asymptotic local approximation to the finite-sample logistic likelihood.

The v12a–v12e sequence therefore identifies the family-level defect: **a posterior Gaussian q95 converted into an angular statistic is not a trustworthy finite-sample sequential confidence guarantee under the current S1 protocol.**

## What v12e establishes

Within the tested correctly specified synthetic model:

1. tangent-only perturbations substantially reduce stopping burden and recover strict high-dimensional strong-signal utility;
2. that utility recovery is accompanied by severe anti-conservative false stopping;
3. two-round persistence is insufficient to repair the tangent construction;
4. full-noise transverse-debiased Laplace q95 remains much safer but is too conservative in the strict high-dimensional strong-signal regime;
5. the remaining problem is not another scalar norm correction or a choice between one versus two crossings;
6. the Laplace posterior-q95 family has reached its prespecified stopping boundary and should not be tuned further;
7. the next confidence method must be designed for finite-sample sequential validity rather than calibrated post hoc to a desired query count;
8. no human, real-profile, compatibility, or relationship-outcome claim follows from this result.

## Next checkpoint — leave the Laplace-q95 family

The next S1 stopping investigation should use an **anytime-valid likelihood/e-process confidence construction** under predictable/adaptive query covariates.

For Bernoulli logistic observations with predictable design `x_t`, let

\[
p_\theta(y_t\mid x_t)
\]

be the logistic likelihood and let `q_t(y_t | H_{t-1}, x_t)` be any normalized predictive distribution chosen using only past data and the current predictable design. Then for a fixed candidate parameter `theta`,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s\mid H_{s-1},x_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under `theta`, because each conditional expectation of the one-step likelihood ratio is one. Ville's inequality therefore gives an anytime-valid confidence sequence

\[
C_t(\alpha)=\{\theta:E_t(\theta)<1/\alpha\}
\]

with coverage at least `1-alpha` under arbitrary predictable stopping and adaptive query selection, provided the likelihood/model is correctly specified.

This construction directly targets the defect exposed by v12a–v12e: optional stopping validity is built into the confidence object rather than estimated from a Laplace posterior tail.

A first v13 checkpoint should remain methodological. Before another large benchmark:

1. implement and test a prequential e-process kernel with predictable numerator probabilities;
2. prove/test the martingale one-step normalization identity numerically;
3. define an angular certification problem: stop only when every parameter remaining in the confidence set has ranking direction within the target cone;
4. develop a conservative numerical method for upper-bounding the maximum logistic likelihood outside that cone;
5. only then run a fresh-seed operating-characteristic benchmark.

Do not approximate the new confidence sequence with an unvalidated posterior quantile and do not tune an empirical correction factor on v12a–v12e artifacts.