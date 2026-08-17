# Science S1 v12a — Posterior Stopping Calibration

## Status

Completed synthetic operating-characteristic study. The proposed posterior q95 angular stopping statistic is **not sufficiently calibrated for direct product use** under the tested sequential protocol.

This result is deliberately negative: the statistic has useful monotonic behavior, but its nominal 95% posterior upper quantile does not control sequential false stops at 5% across the tested S1 conditions.

This remains a correctly specified synthetic-model study, not human-subject validation, attraction-transfer validation, compatibility validation, or relationship-outcome evidence.

## Provenance

- benchmark version: `s1-stopping-calibration-benchmark-v12a`
- stopping version: `laplace-angular-q95-v1`
- model version: `visual-acceptance-linear-logit-v1`
- query-design version: `centered-orthogonalized-gaussian-v1`
- pair-schedule version: `balanced-round-robin-passive-v1`
- executed science head: `1346b9f6c200235c38facc44db6f50119fb3a8eb`
- GitHub Actions run: `31883843945`
- benchmark job: `95010090790`
- artifact: `9246801701`
- artifact ZIP SHA-256: `db26b5bdae25fc5c03fea5475aa8af65a87aaa3f897e8ba7d9c568b8acaadb02`
- benchmark JSON SHA-256: `9e58565435022b9b47067719ae1039bf262371cba00a18c6aaa5fec9ac584e00`
- benchmark JSON bytes: `6,052,951`
- sequential paths: `576`
- posterior refits: `9,792`
- complete balanced rounds per path: `17`
- maximum pair queries per path: `153`
- seeds per `(d,B)` condition: `64`
- benchmark compute time: approximately `7 min 23 s`

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before benchmark execution.

## Prespecified design

The tested conditions are

\[
d\in\{4,8,12\},
\qquad
B\in\{0.55,0.90,1.50\},
\qquad
\epsilon_*\in\{0.25,0.20,0.15\}.
\]

For every `(d,B,seed)` path, 18 controlled synthetic candidates are queried using a response-independent balanced round-robin schedule. Each complete round contains 9 candidate pairs and therefore 18 provisional binary acceptability observations. The posterior is refit after each complete round.

The operational ranking direction is the fitted slope mean `m`. At each checkpoint, samples

\[
\beta^{(s)}\sim N(m,\Sigma_\beta)
\]

are drawn from the Laplace slope marginal, and each draw is converted to Gaussian-population directional ordering error relative to `m`,

\[
e^{(s)}=\frac{1}{\pi}\arccos\left(
\frac{m^T\beta^{(s)}}{\|m\|\,\|\beta^{(s)}\|}
\right).
\]

The candidate stopping statistic is the posterior 95th percentile

\[
U_{0.95}=Q_{0.95}(e^{(s)}\mid D).
\]

The rule is

\[
\text{stop at the first complete round such that }U_{0.95}\le\epsilon_*.
\]

Importantly, the synthetic ground-truth coefficient vector is **not used by the stopping rule**. It is consulted only after each simulated decision to score whether the stop was correct.

The oracle population ordering error used for evaluation is

\[
\epsilon_{true}
=\frac{1}{\pi}\arccos\left(
\frac{\beta^T m}{\|\beta\|\,\|m\|}
\right).
\]

A false stop occurs when the rule stops while

\[
\epsilon_{true}>\epsilon_*.
\]

## Aggregate operating characteristics

Pooling all 576 paths at each target:

| Target error | Stop rate | False-stop rate over all paths | False stop given stop | Missed-stop-at-cap rate | Median stopping queries | Mean true error given stop |
|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.9444 | 0.0885 | **0.0938** | 0.0503 | 45 | 0.1691 |
| 0.20 | 0.7882 | 0.0660 | **0.0837** | 0.1406 | 72 | 0.1321 |
| 0.15 | 0.4913 | 0.0347 | **0.0707** | 0.2899 | 99 | 0.0968 |

The q95 statistic is therefore directionally useful but not calibrated to a 5% sequential false-stop interpretation.

The conditional false-stop probabilities exceed 5% at all three targets. Tightening the target error alone does not repair the calibration defect.

## Dimension dependence

Pooling the three signal levels within each dimension gives:

| d | Target | Stop rate | False stop given stop |
|---:|---:|---:|---:|
| 4 | 0.25 | 0.9844 | 0.0794 |
| 4 | 0.20 | 0.9219 | 0.0621 |
| 4 | 0.15 | 0.7240 | 0.0647 |
| 8 | 0.25 | 0.9323 | 0.0615 |
| 8 | 0.20 | 0.7708 | 0.0811 |
| 8 | 0.15 | 0.4531 | 0.0920 |
| 12 | 0.25 | 0.9167 | **0.1420** |
| 12 | 0.20 | 0.6719 | **0.1163** |
| 12 | 0.15 | 0.2969 | 0.0526 |

The worst broad regime is high dimension at moderate stopping targets, not simply the strictest target.

## Worst structured cells

The most concerning individual conditions are weak-signal/high-dimensional cells.

At `d=12, B=0.55`:

| Target | Stop rate | False stop given stop | Missed stop at cap | Median queries |
|---:|---:|---:|---:|---:|
| 0.25 | 0.7500 | **0.3333** | 0.2188 | 108 |
| 0.20 | 0.1250 | **0.5000** | 0.4219 | 108 |
| 0.15 | 0.0156 | 1.0000 | 0.1250 | 54 |

The `0.15` row contains only one stop and must not be interpreted as a stable 100% rate. It is nevertheless exactly the type of catastrophic isolated false confidence that a calibration stopping rule must guard against.

By contrast, strong-signal cells behave much better. For example, `d=8, B=1.5, target=0.25` had zero false stops in 64 paths, and `d=12, B=1.5` remained near 3% false-stop-given-stop at targets 0.25 and 0.20.

## Static posterior coverage is already subnominal

The failure is not solely optional stopping. At fixed checkpoints, the empirical coverage event

\[
\epsilon_{true}\le U_{0.95}
\]

is below 95% through much of the trajectory.

Selected pooled fixed-checkpoint coverage values are:

| Pair queries | d=4 | d=8 | d=12 | All dimensions |
|---:|---:|---:|---:|---:|
| 9 | 0.8177 | 0.7500 | **0.6458** | 0.7378 |
| 18 | 0.9063 | 0.8125 | 0.7604 | 0.8264 |
| 36 | 0.8906 | 0.8542 | 0.7760 | 0.8403 |
| 54 | 0.9323 | 0.9115 | 0.8177 | 0.8872 |
| 81 | 0.9531 | 0.9271 | 0.8490 | 0.9097 |
| 108 | 0.9427 | 0.9010 | 0.8542 | 0.8993 |
| 153 | 0.9323 | 0.9115 | 0.9167 | 0.9201 |

Thus a nominal posterior q95 angular bound is substantially anti-conservative early, particularly at high dimension. Sequentially stopping on the first crossing then compounds that fixed-checkpoint miscalibration.

## Radial inflation is a primary diagnostic

v12a explicitly tracked the fitted posterior slope norm relative to the true synthetic norm,

\[
r_B=\frac{\|m\|}{B}.
\]

The early estimate is not shrunk toward zero. It is strongly **inflated**, especially for weak signals in higher dimensions:

| d | B | Mean norm ratio after first round | Mean norm ratio at 153 queries |
|---:|---:|---:|---:|
| 4 | 0.55 | 2.534 | 1.108 |
| 4 | 0.90 | 1.701 | 1.024 |
| 4 | 1.50 | 1.340 | 1.014 |
| 8 | 0.55 | 4.548 | 1.162 |
| 8 | 0.90 | 2.995 | 1.085 |
| 8 | 1.50 | 1.918 | 1.056 |
| 12 | 0.55 | **5.880** | **1.234** |
| 12 | 0.90 | 3.578 | 1.146 |
| 12 | 1.50 | 2.179 | 1.114 |

This falsifies the specific concern that low-information Gaussian-prior shrinkage would necessarily make the posterior norm estimate too small. Under this benchmark, estimation noise and high-dimensional radial bias dominate: `||m||` can be much too large while the posterior angular distribution around `m` is simultaneously too confident about the true direction.

This is a crucial distinction. The stopping failure should not be repaired by simply replacing the unknown oracle `B` with `||m||` inside the v11 signal law.

## Post-hoc diagnostics — hypotheses only

The stored sequential paths allow diagnostic counterfactuals without rerunning the model. They are **not prospective validation** and must not be promoted to product rules.

### Two consecutive crossings

If stopping had required two consecutive complete rounds satisfying `U_0.95 <= target`, the same v12a paths would have produced:

| Target | Stop rate | False stop given stop | Missed-stop-at-cap rate | Median queries |
|---:|---:|---:|---:|---:|
| 0.25 | 0.9149 | **0.0455** | 0.0747 | 63 |
| 0.20 | 0.7535 | **0.0415** | 0.1736 | 81 |
| 0.15 | 0.4323 | **0.0361** | 0.3420 | 108 |

### Minimum-information burn-in

If the first admissible stopping checkpoint had been round 10, i.e. 90 pair queries, the same paths would have produced:

| Target | Stop rate | False stop given stop | Missed-stop-at-cap rate | Median queries |
|---:|---:|---:|---:|---:|
| 0.25 | 0.9427 | **0.0331** | 0.0521 | 90 |
| 0.20 | 0.7795 | **0.0401** | 0.1493 | 90 |
| 0.15 | 0.4896 | **0.0461** | 0.2899 | 99 |

Both diagnostics suppress false stopping, but they do so by different mechanisms and costs. The two-crossing rule is much less burdensome at loose/moderate targets, whereas the 90-query burn-in sacrifices most of the potential early-stop benefit.

These numbers were discovered using v12a and therefore require fresh-seed confirmation.

## Scientific disposition

v12a establishes the following within the tested correctly specified synthetic S1 model:

1. A posterior-observable angular uncertainty statistic is operationally feasible; no oracle truth is required to compute it.
2. The raw Laplace posterior q95 is **not a calibrated sequential confidence bound**.
3. False-stop-given-stop is about 7–9% in aggregate and reaches materially worse levels in weak-signal/high-dimensional cells.
4. Fixed-checkpoint q95 coverage is already subnominal, so optional stopping is not the sole defect.
5. Early posterior slope norms are strongly inflated rather than conservatively shrunk, with mean inflation up to 5.88× after one balanced round in the tested grid.
6. Mean fitted norm approaches the truth with information, but residual high-dimensional inflation remains at the 153-query cap.
7. Post-hoc persistence and burn-in rules can reduce false stopping below 5% on this artifact, but that evidence is exploratory because those rules were selected after seeing v12a.
8. None of these results validate human attraction measurement, the synthetic feature basis, transfer to real profiles, dyadic compatibility, or relationship outcomes.

## Next checkpoint

The strongest next experiment is a **fresh-seed prospective v12b**, not a new acquisition heuristic.

Prespecify before execution:

- the original single-crossing q95 rule as a control;
- a two-consecutive-crossing q95 rule;
- a 90-query minimum-information q95 rule as a conservative comparator;
- fresh seeds disjoint from v12a;
- the same `(d,B,target)` grid and controlled passive geometry;
- false-stop-given-stop as the primary safety metric;
- stop rate, missed-stop-at-cap rate, and stopping-query distribution as burden metrics;
- fixed-checkpoint coverage as a secondary diagnostic;
- explicit success criterion: no aggregate target above 5% false-stop-given-stop, with cell-level uncertainty reported rather than hidden.

The goal is to test whether the apparent repair generalizes, not to tune another rule on the same 576 paths.