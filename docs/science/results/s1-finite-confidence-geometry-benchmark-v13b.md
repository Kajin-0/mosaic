# Science S1 v13b — Finite Confidence-Set Geometry

## Status

Completed synthetic finite-grid stopping benchmark.

v13b is the first checkpoint that executes the intended operational logic directly:

```text
predictable prequential numerator
        ↓
anytime-valid parameter confidence set
        ↓
exact geometry of all retained directions
        ↓
stop only when the entire retained set lies inside the target cone
```

The finite-grid construction is strongly safe in the tested correctly specified setting, but conservative.

Across 6,144 paths:

- target `0.25`: stop rate `65.90%`, false-stop rate `0.130%`, false-stop-given-stop `0.198%`, median stop 100 observations;
- target `0.20`: stop rate `25.57%`, false-stop rate `0.081%`, false-stop-given-stop `0.318%`, median stop 114 observations;
- target `0.15`: no paths stopped by the 120-observation cap.

The true grid parameter was excluded from the anytime confidence sequence at some point on `2.865%` of paths. **No false stop occurred while the true parameter was still in the confidence set.** Every observed false stop therefore belongs to the confidence-sequence failure event, exactly as the geometric construction predicts.

The result is therefore qualitatively different from v12a–v12e. The finite-grid safety mechanism is working; the unresolved problem is now efficiency and continuous-resolution certification rather than posterior-calibration repair.

This is not a continuous parameter guarantee, not a validated human preference model, and not synthetic-to-real attraction or relationship validation.

## Provenance

- benchmark version: `s1-finite-confidence-geometry-benchmark-v13b`
- method version: `prequential-finite-confidence-radius-v1`
- executed science head: `bfb594726b83794d3e28bbd4ede3f5bad1b7db13`
- GitHub Actions run: `31903240369`
- benchmark job: `95057098875`
- artifact: `9251706708`
- artifact ZIP SHA-256: `0fefd3a94ed54238b595fdbe7b371b997474d2fc67178e220397b8470d8653b3`
- benchmark JSON SHA-256: `f5e582df25a0efcadd7659173679513cd36b5c30ca7f4fd547000bce3984f62b`
- benchmark JSON bytes: `3,207,909`
- total paths: `6,144`
- true directions: `24`
- seeds per true direction: `256`
- maximum observations per path: `120`
- nominal alpha: `0.05`
- benchmark compute time: approximately `4 min 13 s` after validation

The exact executed head passed Ruff lint, Ruff formatting, mypy, and the complete engine pytest suite before the benchmark ran.

## Finite model

The benchmark deliberately removes continuous optimization from the problem.

The parameter set contained 24 directions on a 15° grid:

```text
0°, 15°, 30°, ..., 345°
```

with fixed

\[
\|\beta\|=0.9,
\qquad b=0.
\]

Every simulated truth was exactly one of those finite grid parameters.

The candidate bank contained 12 unit-circle feature vectors.

## Predictable numerator

Before each current outcome was observed, v13b formed likelihood weights over the full finite parameter grid,

\[
w_t(\theta_j)
\propto L_{t-1}(\theta_j),
\]

starting from the uniform prior, and used the finite-mixture predictive probability

\[
q_t(Y_t\mid x_t)
=\sum_j w_t(\theta_j)
p_{\theta_j}(Y_t\mid x_t).
\]

This is normalized and predictable. Its sequential product is the finite Bayesian mixture marginal likelihood associated with that prior.

For each fixed grid parameter,

\[
E_t(\theta_j)=Q_t/L_t(\theta_j)
\]

is therefore covered by the v13 prequential e-process construction.

The retained finite confidence set was

\[
C_t(\alpha)
=\left\{\theta_j:
\log Q_t-\log L_t(\theta_j)<\log(1/\alpha)
\right\}.
\]

## Adaptive query selection

The current candidate was selected **before** observing `Y_t`.

Among the 12 available feature vectors, the policy chose the one maximizing the range of predicted acceptance probabilities over the current confidence set:

\[
x_t
=\arg\max_x
\left[
\max_{\theta\in C_{t-1}}p_\theta(Y=1\mid x)
-
\min_{\theta\in C_{t-1}}p_\theta(Y=1\mid x)
\right].
\]

This is a simple predictable disagreement policy. It was chosen as a verification instrument, not asserted to be optimal.

## Exact finite-grid stopping rule

After updating the confidence set, the reported center was the retained maximum-likelihood parameter

\[
\hat\theta_t
=\arg\max_{\theta\in C_t}L_t(\theta).
\]

The exact finite-grid directional radius was

\[
r_t
=\max_{\theta\in C_t}
\frac{\operatorname{angle}(\beta(\hat\theta_t),\beta(\theta))}{\pi}.
\]

For target `epsilon`, the path stopped only when

\[
r_t\le\epsilon.
\]

This differs fundamentally from the v12 posterior-q95 family. The statistic is not trying to estimate a frequentist error percentile. It certifies a deterministic geometric fact about every parameter still present in an anytime-valid confidence set.

If the true parameter is in `C_t`, then necessarily

\[
\operatorname{angle}(\beta(\hat\theta_t),\beta_*)/\pi
\le r_t.
\]

Therefore a false directional stop can occur only on a path where the confidence sequence has already excluded truth.

The benchmark confirms this exactly: there were **zero** false stops with `true_in_confidence_set = true`.

## Aggregate results

| Target | Stop rate | False-stop rate | False stop given stop | True excluded ever | Mean stop | Median stop |
|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.659017 | 0.001302 | 0.001976 | 0.028646 | 98.50 | 100 |
| 0.20 | 0.255697 | 0.000814 | 0.003183 | 0.028646 | 113.22 | 114 |
| 0.15 | 0.000000 | 0.000000 | 0.000000 | 0.028646 | — | — |

The observed confidence-sequence exclusion rate, `2.865%`, remains below nominal alpha `5%`. The experiment is not large enough to treat 2.865% as an exact coverage rate; the theorem supplies the validity statement under the finite correctly specified model.

## Worst observed directional cells

At target 0.25, the largest false-stop-given-stop cell was:

```text
direction 75°
stop rate = 59.38%
false-stop rate = 1.172%
false-stop-given-stop = 1.974%
true-excluded-ever = 3.906%
```

The next largest were 255° (`0.730%` false-stop-given-stop) and 225° (`0.621%`).

At target 0.20, the largest false-stop-given-stop cells were:

```text
195°: 1.852%
150°: 1.563%
 90°: 1.449%
```

No target-0.15 cell stopped.

These cell differences are small-count finite-sample variation, not evidence of intrinsic directional anisotropy in the circular setup.

## Main interpretation

v13b separates two questions that the v12 family mixed together:

### Safety

On the finite grid, safety is now structural.

The relevant event is not whether a posterior percentile happens to be calibrated. It is whether the anytime-valid confidence sequence contains the true parameter. Conditional on containment, the geometric radius makes a false stop impossible.

This is the strongest stopping result in S1 so far.

### Efficiency

The current method is conservative:

- median stopping is near the 120-observation cap even at target 0.25;
- only about one quarter of paths reach target 0.20;
- none reaches target 0.15.

That conservatism can arise from several sources that are deliberately confounded in this verification benchmark:

1. the 5% anytime confidence threshold;
2. a mixture numerator optimized for validity rather than short-horizon power;
3. the simple disagreement query policy;
4. the finite 15° parameter grid;
5. the requirement that **every** retained direction lie inside the reported cone;
6. fixed slope norm/intercept geometry that is much simpler than the eventual nuisance-parameter problem.

The correct next move is to improve efficiency while preserving the confidence-sequence invariant—not to loosen the safety threshold after seeing these results.

## What v13b establishes

Within the tested finite correctly specified synthetic problem:

1. the prequential e-process can be converted into an anytime-valid finite parameter confidence sequence;
2. adaptive predictable disagreement queries are compatible with that construction;
3. a data-dependent reported center is safe when it is merely a summary of the already-constructed confidence set;
4. exact confidence-set geometry provides a valid stopping certificate in the finite grid;
5. false stops occur only when the confidence sequence has first excluded the true grid parameter;
6. observed false-stop rates are far below the nominal 5% confidence-sequence failure budget;
7. the current construction is too conservative for the strict 0.15 target at a 120-observation cap;
8. the remaining finite-grid challenge is power/query efficiency, while the larger methodological challenge is conservative continuous confidence-set geometry.

## What v13b does not establish

It does not establish:

- a continuous-parameter angular confidence certificate;
- nuisance-robust inference over unknown intercept and slope magnitude;
- an optimal numerator predictor;
- an optimal active query policy;
- acceptable production calibration burden;
- correctness of the linear-logistic human model;
- a validated synthetic visual basis;
- transfer to real-person attraction;
- compatibility or relationship-outcome prediction.

## Next checkpoint — v13c resolution/efficiency decomposition

Before attacking continuous optimization, use the finite setting to determine **why** target 0.15 never stops.

The next experiment should be a prespecified finite-grid decomposition rather than threshold tuning. Candidate factors:

1. grid angular spacing — e.g. compare 15°, 10°, and 7.5° grids while holding the data-generating truth on-grid;
2. observation horizon — extend the cap enough to estimate when 0.15 certification becomes feasible;
3. numerator predictor — compare the current finite mixture predictive against a predictable plug-in/tempered mixture only if each remains normalized and fixed before evaluation seeds are seen;
4. query policy — compare disagreement-range selection to passive balanced angular queries and a predictive information criterion;
5. report confidence-set cardinality/radius trajectories to identify whether the bottleneck is likelihood concentration or directional discretization.

The first v13c design should vary as few factors as possible. A clean starting point is **grid spacing × observation horizon with the current numerator and query policy frozen**. This will separate resolution from information accumulation without contaminating the safety construction.

Only after that decomposition should S1 implement a continuous outside-cone likelihood upper bound.