# Science S1 v11a — Signal-Scaling Phase Diagram

## Status

Completed exploratory synthetic benchmark. This is a correctly specified synthetic-model study, not human-subject validation, attraction-transfer validation, compatibility validation, or evidence for relationship outcomes.

v11a prospectively tests the signal coordinate proposed after v10a,

\[
\eta_F = B^2\kappa a(B),
\qquad
a(B)=E_{Z\sim N(0,1)}[\sigma(BZ)(1-\sigma(BZ))],
\]

by varying the fixed effective slope norm `B` while choosing query budgets to target common values of `eta_F`.

The benchmark also removes the random endpoint-imbalance confound noted in v10a. Query pairs follow a response-independent balanced round-robin schedule over an 18-candidate centered identity-covariance Gaussian-derived design.

## Provenance

- benchmark version: `s1-signal-scaling-benchmark-v11a`
- model version: `visual-acceptance-linear-logit-v1`
- query-design version: `centered-orthogonalized-gaussian-v1`
- pair-schedule version: `balanced-round-robin-passive-v1`
- executed science head: `d29f7b092a8f7cd5289159cdc6ade3a88522582a`
- GitHub Actions run: `31882484452`
- benchmark job: `95006889361`
- artifact: `9246495793`
- artifact ZIP SHA-256: `b5af32071c7c23f01dd2810f3325426d1aab9e634647525f83ed1621bf86f879`
- benchmark JSON SHA-256: `b90775126355b2237e117277a30fcc052b31b06d14270853cf6a0e26da223c22`
- benchmark JSON bytes: `6,098,112`
- raw simulations: `1,920`
- final converged Laplace fits: `1,905 / 1,920`
- seeds per `(d,B,eta_target)` cell: `32`

The benchmark workflow reran Ruff, Ruff formatting, mypy, and the full engine pytest suite on the exact executed head before computation. All passed.

## Prespecified design

The phase diagram is

\[
d\in\{2,4,8,12\},
\qquad
B\in\{0.55,0.75,0.90,1.15,1.50\},
\qquad
\eta_{target}\in\{0.5,1.0,1.5\}.
\]

For each signal level,

\[
B=\|\beta\|
\]

is imposed exactly by normalizing the synthetic truth in the fixed standardized feature basis. `B` remains an effective coefficient norm under this synthetic parameterization, not a domain-general psychological preference-strength variable.

The requested observation coordinate is converted to a pair-query budget through

\[
\kappa_{request}=\frac{\eta_{target}}{B^2a(B)},
\qquad
q=\operatorname{round\_up\_to\_pair\_budget}\left(\frac{\kappa_{request}(d+1)}{2}\right).
\]

Because `q` is integer-valued, realized `eta_F` differs slightly from its target.

The 18 admissible candidates satisfy

\[
1^T X=0,
\qquad
\frac1{18}X^TX=I_d.
\]

The passive pair schedule is a randomized 1-factorization of the complete candidate graph. Each complete round uses every candidate exactly once, so response-dependent adaptive lock-in and random endpoint imbalance are both removed from this experiment.

## Prespecified ranking laws

For an isotropic Gaussian reference population, exact population ordering error is

\[
\epsilon_{ord}=\frac{\arccos(\cos(\beta,m))}{\pi}.
\]

The large-dimensional signal law tested prospectively is

\[
\boxed{
\epsilon_{\infty}(\eta_F)
=\frac1\pi\arctan(\eta_F^{-1/2}).
}
\]

v11a also prospectively evaluates the simple finite-dimensional transverse-mode correction derived post hoc after v10a,

\[
\eta_{F,d}=\eta_F\frac{d+1}{d-1},
\]

with

\[
\epsilon_d
=\frac1\pi\arctan(\eta_{F,d}^{-1/2}).
\]

## Primary result: signal scaling survives strongly at d=12

For each `(d, eta_target)` group, the primary collapse diagnostic is the range of mean exact Gaussian-population ordering error across the five signal norms.

| d | eta target | observed mean-error range across B | population SD of the five cell means |
|---:|---:|---:|---:|
| 2 | 0.5 | 0.03629 | 0.01276 |
| 2 | 1.0 | 0.04173 | 0.01503 |
| 2 | 1.5 | 0.02793 | 0.00896 |
| 4 | 0.5 | 0.03832 | 0.01352 |
| 4 | 1.0 | 0.03707 | 0.01579 |
| 4 | 1.5 | 0.02143 | 0.00808 |
| 8 | 0.5 | 0.05621 | 0.02127 |
| 8 | 1.0 | 0.02220 | 0.00808 |
| 8 | 1.5 | 0.02982 | 0.01089 |
| 12 | 0.5 | **0.00639** | **0.00212** |
| 12 | 1.0 | **0.01550** | **0.00620** |
| 12 | 1.5 | **0.02315** | **0.00921** |

At `d=12`, holding `eta_F` approximately fixed therefore produces nearly invariant mean ranking error across the full signal interval `B=0.55` to `1.50`, a factor of about `2.73` in effective slope norm.

The five `d=12` cell means at each target are:

| B | eta≈0.5 | eta≈1.0 | eta≈1.5 |
|---:|---:|---:|---:|
| 0.55 | 0.31523 | 0.25095 | 0.20552 |
| 0.75 | 0.31097 | 0.24812 | 0.20829 |
| 0.90 | 0.30883 | 0.26362 | 0.22151 |
| 1.15 | 0.31288 | 0.25996 | 0.22867 |
| 1.50 | 0.31234 | 0.26196 | 0.22492 |

This is the first direct synthetic evidence that the `B^2 a(B)` factor captures the dominant large-dimensional signal dependence rather than merely fitting the single `B=0.9` slice used in v10a.

## Prediction accuracy

Across all 60 `(d,B,eta_target)` cells, the prespecified large-dimensional law has:

- mean absolute cell-mean error: `0.04769`;
- signed bias `observed - predicted`: `-0.04347`;
- RMSE: `0.06144`.

The poor all-dimensional aggregate is driven by known finite-dimensional directional geometry. Broken down by dimension:

| d | large-d MAE | large-d signed bias |
|---:|---:|---:|
| 2 | 0.10374 | -0.10374 |
| 4 | 0.05704 | -0.05704 |
| 8 | 0.02209 | -0.01777 |
| 12 | **0.00789** | **+0.00467** |

Thus the same asymptotic law that fails quantitatively at `d=2` becomes accurate by `d=12` across both signal and information level.

### Prospective finite-dimensional correction

The simple transverse-mode correction improves the 60-cell aggregate substantially:

- mean absolute cell-mean error: `0.01769`;
- signed bias: `-0.00494`;
- RMSE: `0.02177`.

Dimension-wise MAE becomes:

| d | finite-d MAE |
|---:|---:|
| 2 | 0.02552 |
| 4 | 0.01801 |
| 8 | **0.00959** |
| 12 | 0.01762 |

The correction is therefore useful as a compact finite-dimensional approximation, especially at `d=2–8`, but it is **not uniformly superior**. At `d=12` the uncorrected large-dimensional law is more accurate. The correction must not be promoted to an exact finite-dimensional identity.

## Tail behavior remains the blocking issue

The mean collapse does not imply a reliable stopping rule.

Pooling the five signal levels at `d=12` gives 160 runs per `eta_target`:

| eta target | mean population error | p90 | p95 | P(error < 0.25) | P(error < 0.20) | P(error < 0.15) | maximum |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 0.31205 | 0.39938 | 0.42667 | 0.1875 | 0.0438 | 0.0063 | 0.51947 |
| 1.0 | 0.25692 | 0.33211 | 0.34860 | 0.5125 | 0.1563 | 0.0188 | 0.45619 |
| 1.5 | 0.21778 | 0.27864 | 0.29617 | 0.7375 | 0.3375 | 0.0813 | 0.34183 |

Even where mean scaling is clean, the upper tail remains broad. A system that stops because the **expected** error is acceptable would therefore false-stop for a nontrivial fraction of synthetic users.

Across all 1,920 runs, 25 fitted slopes point into the wrong half-space (`beta^T m < 0`). Those events concentrate at low information and low-dimensional/small-query cells. They are retained rather than hidden.

## Convergence sensitivity

`1,905 / 1,920` final Laplace fits were flagged converged (`99.22%`). The 15 flagged fits remain in all summaries. No cell-level result is conditioned on successful convergence.

The principal collapse result is based on cell means and is not driven by removing difficult fits.

## Scientific disposition

v11a establishes the following **within the correctly specified synthetic S1 model**:

1. `eta_F = B^2 kappa a(B)` captures the dominant **large-dimensional mean directional-ranking signal dependence** across `B=0.55–1.50`.
2. At `d=12`, the large-dimensional ordering law predicts the 15 cell means with about `0.0079` absolute error on average.
3. Equal `eta_F` does not produce exact finite-dimensional collapse at `d=2–8`; ordinary directional degrees of freedom and finite query geometry remain visible.
4. The prespecified `(d+1)/(d-1)` transverse correction materially improves the all-dimensional approximation but is not uniformly best and must remain an approximation.
5. Balanced round-robin passive querying removes the endpoint-imbalance confound without destroying the high-dimensional signal collapse.
6. Mean-error collapse is **not** a calibration stopping guarantee. The error distribution remains broad enough that false stops would be material.
7. This benchmark does not validate synthetic-to-human transfer, the feature basis, the linear-logistic likelihood in people, compatibility, or relationship outcomes.

## Next checkpoint

Do **not** invent another acquisition heuristic yet and do not convert `eta_F` directly into a product query-count claim.

The next experiment should move from an oracle coordinate that depends on the unknown truth `B=||beta||` to a **posterior-observable stopping statistic** and measure its operating characteristics under the same controlled synthetic model.

A defensible v12 should:

1. define one or more stopping statistics using only quantities available from the fitted posterior and known versioned design, never the true synthetic `beta`;
2. prespecify target population-ordering error thresholds such as `0.25`, `0.20`, and `0.15`;
3. run sequential passive balanced-round-robin observations over enough seeds to estimate false-stop probability, missed-stop probability, stopping-time distribution, and residual error conditional on stopping;
4. stratify by `d` and `B` so a statistic cannot appear calibrated only because heterogeneous conditions average together;
5. compare posterior-predicted directional uncertainty against the exact oracle error `acos(cos(beta,m))/pi` only for evaluation;
6. retain product query caps as censoring events rather than declaring unresolved users calibrated;
7. explicitly test whether prior shrinkage makes a posterior norm estimate of `B` optimistic at low information; and
8. only after a stopping statistic has acceptable operating curves should active acquisition be reconsidered.

The scientific objective has therefore shifted from **mean sample-complexity scaling** to **calibrated uncertainty and false-stop control**.