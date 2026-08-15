# Science S1 v12d — Transverse-Debiased Directional Stopping

## Status

Completed prospective fresh-seed synthetic validation.

v12d tested the geometric refinement motivated by v12c: subtract only posterior covariance energy orthogonal to the fitted ranking direction,

\[
u=\frac{m}{\|m\|},\qquad
V_\parallel=u^T\Sigma_\beta u,\qquad
V_\perp=\operatorname{tr}(\Sigma_\beta)-V_\parallel,
\]

and use

\[
\widehat B_{\perp,db}^2
=\max\left(\|m\|^2-V_\perp,0\right)
\]

as the reference norm for posterior angular uncertainty.

The correction moved in the desired direction: it retained the strong safety improvement of v12c while increasing strict high-dimensional strong-signal stopping. However, the prespecified overall gate still **failed** because the primary two-consecutive rule stopped only `56/128 = 43.75%` of `d=12, B=1.5, target=0.15` paths, below the unchanged 60% utility floor.

Therefore transverse-only scalar norm debiasing is **not promoted as the final S1 stopping rule**.

## Provenance

- benchmark version: `s1-transverse-stopping-benchmark-v12d`
- stopping version: `laplace-transverse-debiased-angular-v4`
- executed science head: `e3cdbbbe47d63ab5eb089cc0357964822ec64722`
- GitHub Actions run: `31894267281`
- benchmark job: `95035012785`
- artifact: `9249574908`
- artifact ZIP SHA-256: `7024c1e2d2edc6469d194528921853ba22193d437a80d75ed6c5c984fcf02fed`
- benchmark JSON SHA-256: `cc53a9f26fa70cf25bea61786ab5c03526a939f7e77a9c91e238da3949cd878c`
- benchmark JSON bytes: `44,364,731`
- sequential paths: `1,152`
- seeds per `(d,B)` condition: `128`
- seeds: `320..447`, disjoint from v12a–v12c seeds `0..319`
- complete balanced rounds per path: `17`
- maximum pair queries per path: `153`
- benchmark compute time: approximately `17 min 23 s`

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before any v12d evaluation seed was simulated.

## Prespecified comparison

The scientific grid and data-generation protocol were unchanged from v12c.

Four rules were compared on identical response paths:

1. `raw_two_consecutive`;
2. `radial_debiased_two_consecutive` — full-trace v12c control;
3. `transverse_debiased_single`;
4. `transverse_debiased_two_consecutive` — primary.

The v12c gates were retained unchanged:

- aggregate false-stop-given-stop Wilson 95% upper bound ≤5% at every target;
- every cell with at least 32 stops must have false-stop-given-stop ≤10%;
- for `B=1.5`, stop rate ≥90% at targets 0.25 and 0.20 and ≥60% at target 0.15.

## Aggregate results

| Target | Rule | Stop rate | False stop given stop | Wilson 95% upper | Missed stop at cap | Median pair queries |
|---:|---|---:|---:|---:|---:|---:|
| 0.25 | raw two-consecutive | 0.9045 | 0.0393 | 0.0529 | 0.0833 | 63 |
| 0.25 | full-trace two-consecutive | 0.8003 | 0.0087 | 0.0170 | 0.1814 | 72 |
| 0.25 | transverse single | 0.8507 | 0.0286 | 0.0410 | 0.1319 | 63 |
| 0.25 | transverse two-consecutive | **0.8160** | **0.0138** | **0.0235** | 0.1658 | 72 |
| 0.20 | raw two-consecutive | 0.7387 | 0.0329 | 0.0471 | 0.1953 | 81 |
| 0.20 | full-trace two-consecutive | 0.6285 | 0.0124 | 0.0235 | 0.3012 | 90 |
| 0.20 | transverse single | 0.7049 | 0.0333 | 0.0479 | 0.2274 | 81 |
| 0.20 | transverse two-consecutive | **0.6441** | **0.0148** | **0.0264** | 0.2856 | 90 |
| 0.15 | raw two-consecutive | 0.4427 | 0.0373 | 0.0575 | 0.3359 | 108 |
| 0.15 | full-trace two-consecutive | 0.3733 | 0.0256 | 0.0452 | 0.4019 | 108 |
| 0.15 | transverse single | 0.4418 | 0.0472 | 0.0692 | 0.3394 | 99 |
| 0.15 | transverse two-consecutive | **0.3898** | **0.0245** | **0.0433** | 0.3854 | 108 |

The primary rule passes the aggregate confidence-bound safety gate at all three targets.

## Primary gate

```text
aggregate_safe = true
subgroup_safe = true
strong_signal_safe = false
overall_pass = false
```

Nineteen cells had at least 32 primary-rule stops; all satisfied the ≤10% subgroup point-error requirement.

## Primary cell results

| d | B | Target | Stops / 128 | Stop rate | False stop given stop |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.55 | 0.25 | 103 | 0.8047 | 0.0097 |
| 4 | 0.55 | 0.20 | 72 | 0.5625 | 0.0278 |
| 4 | 0.55 | 0.15 | 11 | 0.0859 | 0.0909 |
| 4 | 0.90 | 0.25 | 128 | 1.0000 | 0.0078 |
| 4 | 0.90 | 0.20 | 127 | 0.9922 | 0.0157 |
| 4 | 0.90 | 0.15 | 109 | 0.8516 | 0.0275 |
| 4 | 1.50 | 0.25 | 128 | 1.0000 | 0.0000 |
| 4 | 1.50 | 0.20 | 128 | 1.0000 | 0.0000 |
| 4 | 1.50 | 0.15 | 128 | 1.0000 | 0.0078 |
| 8 | 0.55 | 0.25 | 61 | 0.4766 | 0.0820 |
| 8 | 0.55 | 0.20 | 10 | 0.0781 | 0.1000 |
| 8 | 0.55 | 0.15 | 0 | 0.0000 | — |
| 8 | 0.90 | 0.25 | 127 | 0.9922 | 0.0236 |
| 8 | 0.90 | 0.20 | 103 | 0.8047 | 0.0291 |
| 8 | 0.90 | 0.15 | 18 | 0.1406 | 0.1111 |
| 8 | 1.50 | 0.25 | 128 | 1.0000 | 0.0078 |
| 8 | 1.50 | 0.20 | 128 | 1.0000 | 0.0000 |
| 8 | 1.50 | 0.15 | 127 | 0.9922 | 0.0315 |
| 12 | 0.55 | 0.25 | 27 | 0.2109 | 0.0741 |
| 12 | 0.55 | 0.20 | 0 | 0.0000 | — |
| 12 | 0.55 | 0.15 | 0 | 0.0000 | — |
| 12 | 0.90 | 0.25 | 112 | 0.8750 | 0.0000 |
| 12 | 0.90 | 0.20 | 48 | 0.3750 | 0.0625 |
| 12 | 0.90 | 0.15 | 0 | 0.0000 | — |
| 12 | 1.50 | 0.25 | 126 | 0.9844 | 0.0000 |
| 12 | 1.50 | 0.20 | 126 | 0.9844 | 0.0000 |
| 12 | 1.50 | 0.15 | **56** | **0.4375** | **0.0000** |

The strict high-dimensional strong-signal cell is completely safe in this 56-stop sample but remains too reluctant to stop.

## Improvement over v12c

For `d=12, B=1.5, target=0.15`:

| Rule | v12c/v12d stop rate | False stop given stop |
|---|---:|---:|
| v12c full-trace two-consecutive | 0.3281 | 0.0238 |
| v12d transverse two-consecutive | **0.4375** | **0.0000** |
| v12d transverse single | **0.6094** | 0.0128 |
| v12d raw two-consecutive | 0.7031 | 0.0111 |

Transverse-only debiasing therefore recovers a meaningful fraction of the utility lost by full-trace subtraction. It does not recover enough under the required two-round persistence rule.

The transverse **single-crossing** rule happens to exceed the 60% utility floor in this cell, but it fails the aggregate confidence-bound safety gate at target 0.15: aggregate false-stop-given-stop is `4.72%` with Wilson upper endpoint `6.92%`. It is therefore not a valid escape hatch.

## Fixed-checkpoint coverage

Selected q95 coverage:

| d | B | q | Raw | Full trace | Transverse | Mean B_perp,db / ||m|| |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0.55 | 9 | 0.7656 | 0.8984 | 0.8828 | 0.5216 |
| 4 | 0.55 | 90 | 0.9375 | 0.9766 | 0.9609 | 0.8711 |
| 8 | 0.55 | 9 | 0.6172 | 0.9141 | 0.8750 | 0.5439 |
| 8 | 0.55 | 90 | 0.8984 | 0.9766 | 0.9609 | 0.7536 |
| 12 | 0.55 | 9 | **0.4766** | 0.9141 | **0.8984** | 0.3278 |
| 12 | 0.55 | 90 | 0.7891 | 0.9531 | **0.9375** | 0.6742 |
| 12 | 0.55 | 153 | 0.9297 | 0.9922 | **0.9844** | 0.7806 |
| 12 | 1.50 | 9 | 0.8672 | 0.9922 | 0.9922 | 0.2313 |
| 12 | 1.50 | 90 | 0.9375 | 0.9922 | 0.9922 | 0.9211 |
| 12 | 1.50 | 153 | 0.9609 | 0.9609 | 0.9609 | 0.9520 |

The transverse construction preserves most of the weak-signal coverage repair while retaining more effective signal norm than full-trace correction.

## Why the utility failure remains

For `d=12, B=1.5`, the true strict-target state is learned earlier than the current q95 statistic admits:

| q | Fraction true error ≤0.15 | Median raw q95 | Median full-trace q95 | Median transverse q95 | Fraction transverse q95 ≤0.15 |
|---:|---:|---:|---:|---:|---:|
| 90 | 0.8438 | 0.1815 | 0.2013 | 0.1974 | 0.0078 |
| 108 | 0.9219 | 0.1648 | 0.1813 | 0.1776 | 0.0391 |
| 117 | 0.9375 | 0.1602 | 0.1735 | 0.1712 | 0.1172 |
| 126 | 0.9453 | 0.1533 | 0.1667 | 0.1636 | 0.1641 |
| 135 | 0.9844 | 0.1485 | 0.1594 | 0.1577 | 0.2891 |
| 144 | 0.9844 | 0.1445 | 0.1547 | 0.1529 | 0.4375 |
| 153 | 0.9922 | 0.1390 | 0.1484 | 0.1469 | 0.5859 |

The remaining conservatism is therefore not adequately explained by scalar signal-norm correction.

The current angular posterior simulation perturbs the corrected reference vector with the **full covariance**, including longitudinal noise. Large longitudinal perturbations can change the sampled vector length or sign and contribute nonlinear angular error even though longitudinal covariance does not rotate the direction in the first-order tangent geometry.

## What v12d establishes

Within the correctly specified synthetic model:

1. transverse-only debiasing is directionally superior to subtracting the entire covariance trace for the safety–utility tradeoff;
2. it preserves aggregate and adequately sampled subgroup safety under the unchanged v12c gates;
3. it improves the failed strict strong-signal stop rate from 32.8% to 43.8%;
4. it still fails the 60% utility requirement, so scalar norm correction alone is insufficient;
5. removing two-round persistence restores utility in the hardest strong-signal cell but loses aggregate confidence-bound safety at the strict target;
6. the next problem is the construction of angular uncertainty itself, not another scalar threshold or burn-in constant;
7. no human, real-profile, compatibility, or relationship-outcome claim follows from this result.

## Next checkpoint

Stop tuning scalar norm corrections.

A mechanistically stronger v12e should construct uncertainty directly in the **tangent space of ranking direction**. For fitted unit direction `u` and posterior perturbation `delta`, use

\[
\delta_\perp=(I-uu^T)\delta,
\]

and evaluate angular uncertainty from transverse perturbations only, with the v12d transverse-debiased signal norm retained as the denominator/reference scale. A Monte Carlo implementation can preserve the full anisotropic transverse covariance without allowing pure longitudinal perturbations to manufacture angular error.

Conceptually, for small error,

\[
\theta\approx\arctan\left(\frac{\|\delta_\perp\|}{\widehat B_{\perp,db}}\right),
\qquad
\epsilon_{rank}\approx\frac{\theta}{\pi}.
\]

A fresh-seed v12e should compare:

1. v12d transverse-debiased full-noise two-consecutive control;
2. tangent-space single crossing;
3. tangent-space two-consecutive as primary;
4. optionally the raw control for calibration context.

Use seeds disjoint from `0..447`, preserve the same controlled grid, and retain all v12c/v12d gates unchanged. If the tangent-space construction still cannot satisfy both confidence-bound safety and strong-signal utility prospectively, stop refining the Laplace q95 family and investigate a different finite-sample confidence construction rather than adding empirical constants.