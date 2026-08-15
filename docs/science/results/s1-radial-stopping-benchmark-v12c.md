# Science S1 v12c — Radial-Debiased Directional Stopping

## Status

Completed prospective fresh-seed synthetic validation.

The theory-motivated radial correction

\[
\widehat B_{db}^2=\max\left(\|m\|^2-\operatorname{tr}(\Sigma_\beta),0\right)
\]

substantially repaired the false-confidence failure identified in v12a/v12b. The primary rule — two consecutive crossings using posterior angular uncertainty evaluated at `B_db` — passed the prespecified aggregate confidence-bound safety gate and the adequately sampled subgroup safety gate.

It nevertheless **failed the overall prespecified gate** because it was too conservative for the strict high-dimensional strong-signal condition. At `d=12, B=1.5, target=0.15`, only `42/128 = 32.8%` of paths stopped, below the prespecified 60% utility floor.

Therefore the v12c primary rule is **not promoted as the S1 stopping rule**.

This is a correctly specified synthetic-model result only. It is not human-subject validation, synthetic-to-real attraction transfer, compatibility validation, or relationship-outcome evidence.

## Provenance

- benchmark version: `s1-radial-stopping-benchmark-v12c`
- stopping version: `laplace-radial-debiased-angular-v3`
- executed science head: `dc5267ed0bd9fde98aa5bda078b7eb7a0309b345`
- GitHub Actions run: `31893065756`
- benchmark job: `95032121782`
- artifact: `9249253132`
- artifact ZIP SHA-256: `ba217f96cffa08015109cbb063c425752a9d8733f7080c566b933757faf70a95`
- benchmark JSON SHA-256: `9e8f614a46733b9b88cf5c1663a1b1d703512e136c4f7bf53f683847e1dbd450`
- benchmark JSON bytes: `27,957,712`
- sequential paths: `1,152`
- seeds per `(d,B)` condition: `128`
- seeds: `192..319`, disjoint from v12a/v12b seeds `0..191`
- complete balanced rounds per path: `17`
- maximum pair queries per path: `153`
- benchmark compute time: approximately `16 min 28 s`

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before any v12c evaluation seed was simulated.

## Scientific design

The controlled grid remained unchanged:

\[
d\in\{4,8,12\},\qquad
B\in\{0.55,0.90,1.50\},\qquad
\epsilon_*\in\{0.25,0.20,0.15\}.
\]

The passive centered/orthogonalized candidate geometry, balanced round-robin pair schedule, Gaussian prior, Laplace logistic posterior, q95 angular statistic, and 18-candidate/153-pair-query cap were held fixed.

The v12c mechanism was motivated by the v12a/v12b observation that fitted slope norm is inflated by posterior noise, especially for weak signal and high dimension. Under an approximately Gaussian estimator,

\[
E\|m\|^2\approx\|\beta\|^2+\operatorname{tr}(V).
\]

v12c therefore subtracts the Laplace slope-covariance trace from squared fitted norm before evaluating angular posterior noise. This is a diagnostic approximation, not a claim of exact finite-sample unbiasedness.

Three rules were prespecified:

1. `raw_two_consecutive` — v12b replicated control;
2. `radial_debiased_single` — one corrected q95 crossing;
3. `radial_debiased_two_consecutive` — corrected q95 plus two-round persistence.

The third rule was primary.

## Prespecified primary gates

The primary rule had to satisfy all three:

1. **aggregate safety:** Wilson 95% upper bound for false-stop-given-stop ≤5% at every target;
2. **subgroup safety:** every `(d,B,target)` cell with at least 32 stops must have false-stop-given-stop ≤10%;
3. **strong-signal utility:** for `B=1.5`, stop rate ≥90% at targets 0.25 and 0.20, and ≥60% at target 0.15.

This prevents a vacuous rule from appearing safe simply by refusing to stop.

## Aggregate results

| Target | Rule | Stop rate | False stop given stop | Wilson 95% upper | Missed stop at cap | Median pair queries |
|---:|---|---:|---:|---:|---:|---:|
| 0.25 | raw two-consecutive | 0.9253 | 0.0647 | 0.0811 | 0.0616 | 63 |
| 0.25 | radial single | 0.8464 | 0.0318 | 0.0448 | 0.1337 | 63 |
| 0.25 | radial two-consecutive | **0.8021** | **0.0195** | **0.0306** | 0.1771 | 72 |
| 0.20 | raw two-consecutive | 0.7457 | 0.0489 | 0.0654 | 0.1858 | 81 |
| 0.20 | radial single | 0.6849 | 0.0406 | 0.0567 | 0.2439 | 81 |
| 0.20 | radial two-consecutive | **0.6363** | **0.0205** | **0.0335** | 0.2908 | 90 |
| 0.15 | raw two-consecutive | 0.4453 | 0.0448 | 0.0664 | 0.3455 | 108 |
| 0.15 | radial single | 0.4253 | 0.0367 | 0.0573 | 0.3628 | 99 |
| 0.15 | radial two-consecutive | **0.3733** | **0.0256** | **0.0452** | 0.4141 | 108 |

The primary corrected/persistent rule therefore passes the aggregate confidence-bound safety requirement at all three targets.

## Primary gate result

```text
aggregate_safe = true
subgroup_safe = true
strong_signal_safe = false
overall_pass = false
```

Nineteen cells had at least 32 primary-rule stops; every one met the ≤10% subgroup point-error requirement.

The failure is utility, not safety.

## Cell-level primary result

### d = 4

| B | Target | Stops / 128 | Stop rate | False stop given stop |
|---:|---:|---:|---:|---:|
| 0.55 | 0.25 | 97 | 0.7578 | 0.0206 |
| 0.55 | 0.20 | 51 | 0.3984 | 0.0196 |
| 0.55 | 0.15 | 10 | 0.0781 | 0.1000 |
| 0.90 | 0.25 | 128 | 1.0000 | 0.0078 |
| 0.90 | 0.20 | 128 | 1.0000 | 0.0000 |
| 0.90 | 0.15 | 104 | 0.8125 | 0.0192 |
| 1.50 | 0.25 | 128 | 1.0000 | 0.0078 |
| 1.50 | 0.20 | 128 | 1.0000 | 0.0000 |
| 1.50 | 0.15 | 128 | 1.0000 | 0.0078 |

### d = 8

| B | Target | Stops / 128 | Stop rate | False stop given stop |
|---:|---:|---:|---:|---:|
| 0.55 | 0.25 | 51 | 0.3984 | 0.0392 |
| 0.55 | 0.20 | 13 | 0.1016 | 0.1538 |
| 0.55 | 0.15 | 0 | 0.0000 | — |
| 0.90 | 0.25 | 124 | 0.9688 | 0.0323 |
| 0.90 | 0.20 | 103 | 0.8047 | 0.0485 |
| 0.90 | 0.15 | 20 | 0.1562 | 0.2000 |
| 1.50 | 0.25 | 128 | 1.0000 | 0.0000 |
| 1.50 | 0.20 | 128 | 1.0000 | 0.0156 |
| 1.50 | 0.15 | 125 | 0.9766 | 0.0160 |

Cells with fewer than 32 stops were not part of the prespecified subgroup gate; their percentages remain useful diagnostics but are too noisy to interpret as precise population rates.

### d = 12

| B | Target | Stops / 128 | Stop rate | False stop given stop |
|---:|---:|---:|---:|---:|
| 0.55 | 0.25 | 25 | 0.1953 | 0.1600 |
| 0.55 | 0.20 | 1 | 0.0078 | 0.0000 |
| 0.55 | 0.15 | 0 | 0.0000 | — |
| 0.90 | 0.25 | 116 | 0.9062 | 0.0259 |
| 0.90 | 0.20 | 58 | 0.4531 | 0.0690 |
| 0.90 | 0.15 | 1 | 0.0078 | 0.0000 |
| 1.50 | 0.25 | 127 | 0.9922 | 0.0079 |
| 1.50 | 0.20 | 123 | 0.9609 | 0.0081 |
| 1.50 | 0.15 | **42** | **0.3281** | **0.0238** |

The final row is the prespecified utility failure. The rule is safe when it stops, but it refuses to declare sufficiently many clearly learnable strong-signal users calibrated at the strict target.

## Fixed-checkpoint coverage

The radial correction directly repairs the mechanism exposed by v12b.

Selected q95 coverage `P(epsilon_true <= U_0.95)`:

| d | B | q | Raw q95 coverage | Radial-debiased q95 coverage | Mean B_db / ||m|| |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.55 | 9 | 0.7969 | 0.9062 | 0.3552 |
| 4 | 0.55 | 90 | 0.9219 | 0.9688 | 0.8087 |
| 4 | 0.55 | 153 | 0.9609 | 0.9766 | 0.8982 |
| 8 | 0.55 | 9 | 0.6406 | 0.8438 | 0.3728 |
| 8 | 0.55 | 90 | 0.7969 | 0.9375 | 0.7063 |
| 8 | 0.55 | 153 | 0.8594 | 0.9531 | 0.8270 |
| 12 | 0.55 | 9 | **0.4375** | **0.9453** | 0.2009 |
| 12 | 0.55 | 90 | **0.6875** | **0.9688** | 0.6513 |
| 12 | 0.55 | 153 | 0.8047 | 0.9141 | 0.7824 |
| 12 | 1.50 | 9 | 0.9219 | 1.0000 | 0.1078 |
| 12 | 1.50 | 90 | 0.9062 | 0.9609 | 0.8993 |
| 12 | 1.50 | 153 | 0.9453 | 0.9609 | 0.9397 |

The weak-signal/high-dimensional repair is large and systematic. The full-trace subtraction is therefore addressing a real finite-sample defect rather than merely imposing an arbitrary delay.

It is also visibly conservative early even for strong signal because high-dimensional posterior covariance contributes large radial energy before enough evidence accumulates.

## Strict d=12, B=1.5 diagnostic

At the hardest strong-signal target `epsilon*=0.15`:

| q | Fraction with true error ≤0.15 | Median raw q95 | Median radial q95 |
|---:|---:|---:|---:|
| 90 | 0.7188 | 0.1814 | 0.2035 |
| 117 | 0.9062 | 0.1584 | 0.1719 |
| 135 | 0.9453 | 0.1486 | 0.1608 |
| 144 | 0.9688 | 0.1445 | 0.1545 |
| 153 | 0.9688 | 0.1408 | 0.1499 |

By q=117, more than 90% of paths already meet the true target, yet the full-trace corrected posterior statistic remains above the target for many of them. This is the concrete overcorrection that causes the failed utility gate.

For this cell at target 0.15:

- raw two-consecutive: stop rate `0.6797`, false-stop-given-stop `0.0575`;
- radial single: stop rate `0.5547`, false-stop-given-stop `0.0141`;
- radial two-consecutive: stop rate `0.3281`, false-stop-given-stop `0.0238`.

The desired rule lies between the raw and full-trace-corrected extremes.

## What v12c establishes

Within the tested correctly specified synthetic model:

1. radial norm inflation is a major cause of the weak-signal/high-dimensional false-confidence defect;
2. subtracting posterior covariance energy from squared fitted norm dramatically improves fixed-checkpoint coverage;
3. combining that correction with two-round persistence gives aggregate false-stop Wilson upper bounds below 5% at all tested targets;
4. the correction removes the large adequately sampled subgroup failures seen in v12b;
5. subtracting the **entire** slope-covariance trace is too conservative for strict high-dimensional stopping, even when true signal is strong;
6. therefore v12c resolves the safety mechanism but not the safety–burden tradeoff;
7. a product query cap must still mean unresolved uncertainty, not automatic calibration success;
8. none of this validates the synthetic feature basis, human preference stability, transfer to real people, dyadic compatibility, or relationship outcomes.

## Next checkpoint

Do **not** promote the v12c rule as final S1 stopping semantics.

The next mechanistic refinement should distinguish covariance that changes **direction** from covariance that only changes **length**. Let

\[
u=\frac{m}{\|m\|},
\qquad
V_\parallel=u^T\Sigma_\beta u,
\qquad
V_\perp=\operatorname{tr}(\Sigma_\beta)-V_\parallel.
\]

First-order angular error depends on covariance projected into the tangent/transverse subspace, not on pure longitudinal uncertainty. A natural next diagnostic is therefore

\[
\widehat B_{\perp,db}^2
=
\max\left(\|m\|^2-V_\perp,0\right),
\]

rather than subtracting the entire trace.

A fresh-seed v12d should compare:

1. raw two-consecutive control;
2. full-trace radial two-consecutive control;
3. **transverse-debiased two-consecutive** as the primary rule;
4. optionally transverse-debiased single crossing as a burden/safety diagnostic.

Use seeds disjoint from v12a–v12c, preserve the same controlled `(d,B,target)` grid, and retain the v12c aggregate confidence-bound, subgroup-safety, and strong-signal utility gates unchanged.

If transverse-only debiasing cannot satisfy both safety and utility prospectively, stop tuning scalar corrections and move to a more principled confidence construction for angular error rather than inventing additional thresholds.