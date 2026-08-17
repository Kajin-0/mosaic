# Science S1 v10a — Fixed-Signal Directional Sample Complexity

## Status

Completed exploratory synthetic benchmark. This is a correctly specified synthetic-model study, not human-subject validation, attraction-transfer validation, compatibility validation, or evidence for relationship outcomes.

The principal purpose of v10a is to remove two major confounds exposed by v7a–v9a before deriving any calibration-burden rule:

1. every synthetic truth has the same effective slope norm in the standardized feature basis; and
2. only passive random pair sampling is used, so adaptive lock-in cannot contaminate the baseline statistical law.

## Provenance

- benchmark version: `s1-fixed-signal-sample-complexity-benchmark-v10a`
- model version: `visual-acceptance-linear-logit-v1`
- query-design version: `centered-orthogonalized-gaussian-v1`
- executed science head: `85bf8faec259374a1bdb085120b9071d47370c2b`
- GitHub Actions run: `31881658138`
- benchmark job: `95004997672`
- artifact: `9246209421`
- artifact ZIP SHA-256: `e1ba84456279093372feaa3b1abfa34ff2edbe6805093b6f973b65b4615b0549`
- benchmark JSON SHA-256: `eb7abe60b5c938537eaf46ca4ed501aa9d9e054928a639fd7b9ae266c761b374`
- benchmark JSON bytes: `1,962,504`
- raw simulations: `640`
- final converged Laplace fits: `634 / 640`
- seeds per `(d, kappa)` cell: `32`

The benchmark workflow reran Ruff, Ruff formatting, mypy, and the full engine pytest suite on the exact executed head before the science computation. All passed.

## Prespecified design

The dimensions and observation budgets are

\[
d\in\{2,4,8,12\},
\qquad
\kappa\in\{2,4,6,8,12\},
\]

with

\[
\kappa=\frac{N}{d+1}=\frac{2q}{d+1},
\]

where `q` is the number of pair queries and each pair is provisionally modeled as two binary acceptability observations.

For every synthetic truth,

\[
B\equiv\|\beta\|=0.9
\]

exactly in the fixed standardized feature basis. `B` is an effective coefficient norm under this synthetic parameterization; it must not be renamed a domain-general psychological preference-strength variable.

The 18 admissible query candidates are generated from iid Gaussian vectors and then centered and orthogonalized/rescaled so that

\[
1^T X=0,
\qquad
\frac1{18}X^T X=I_d.
\]

The held-out reference distribution remains iid isotropic Gaussian. The query policy is **random only** in v10a.

## Exact Gaussian-population ordering identity

For independent isotropic Gaussian candidates,

\[
\Delta X=X_a-X_b\sim N(0,2I).
\]

If the true and fitted score directions are `beta` and `m`, then their score differences are jointly Gaussian with correlation

\[
\rho=\frac{\beta^T m}{\|\beta\|\|m\|}=\cos\theta.
\]

The exact wrong-order probability is therefore

\[
\boxed{\epsilon_{ord}=\frac{\arccos\rho}{\pi}=\frac{\theta}{\pi}.}
\]

This is the primary directional-ranking metric for the synthetic Gaussian reference problem. The finite 96-candidate held-out bank is useful as an independent empirical check but is no longer needed to approximate the population ordering error.

Across all 640 v10a runs, the finite held-out ordering error versus the exact angle-derived population error has:

- mean absolute difference: `0.01759`;
- mean signed difference: `-0.000225`;
- Pearson correlation: `0.98473`;
- maximum absolute difference: `0.10451`.

Thus the held-out estimator is approximately unbiased but visibly noisy at 96 candidates.

## Prespecified asymptotic laws

### Boundary-information approximation

If every binary observation were at the logistic boundary, `p=1/2`, the per-observation Fisher weight is `1/4`. The large-dimensional directional coordinate is then

\[
\eta_0=\frac{B^2\kappa}{4},
\]

with the approximate ordering law

\[
\epsilon_0(\kappa,B)
\approx
\frac1\pi\arctan\left(\eta_0^{-1/2}\right).
\]

### Gaussian-logistic Fisher correction

For a natural isotropic Gaussian candidate population, observations do not all lie at `p=1/2`. Define the transverse Fisher weight

\[
a(B)
=
E_{Z\sim N(0,1)}\left[\sigma(BZ)(1-\sigma(BZ))\right].
\]

At `B=0.9`,

\[
a(0.9)=0.2128579611,
\]

below the boundary maximum `0.25`.

The corresponding large-dimensional coordinate is

\[
\eta_F=B^2\kappa a(B),
\]

and

\[
\boxed{
\epsilon_F(\kappa,B)
\approx
\frac1\pi\arctan\left(\eta_F^{-1/2}\right).
}
\]

v10a tests these laws at **one fixed signal level, `B=0.9`**. It does not yet validate the predicted scaling across different values of `B`.

## Primary results

### Cell means

The primary exact Gaussian-population ordering-error means are:

| d | kappa=2 | kappa=4 | kappa=6 | kappa=8 | kappa=12 |
|---:|---:|---:|---:|---:|---:|
| 2 | 0.2925 | 0.2004 | 0.1619 | 0.1647 | 0.1121 |
| 4 | 0.3409 | 0.2479 | 0.2038 | 0.1932 | 0.1624 |
| 8 | 0.3750 | 0.2985 | 0.2671 | 0.2131 | 0.1708 |
| 12 | 0.3228 | 0.2757 | 0.2384 | 0.2188 | 0.1975 |

Fixing `B` and the full admissible-bank covariance therefore does **not** produce exact cross-dimensional collapse against `kappa` alone.

That is not evidence that the controlled-geometry idea failed. `kappa=N/(d+1)` counts all fitted coefficients, while ranking direction has only `d-1` transverse rotational modes. At fixed `kappa`, low-dimensional problems therefore need not have the same directional error as the large-`d` limit.

### Large-dimensional law is quantitatively strong at d=12

For `d=12`, observed cell means are close to both prespecified large-`d` predictions:

| kappa | q pairs | observed | boundary prediction | Fisher prediction |
|---:|---:|---:|---:|---:|
| 2 | 13 | 0.3228 | 0.3196 | 0.3310 |
| 4 | 26 | 0.2757 | 0.2667 | 0.2794 |
| 6 | 39 | 0.2384 | 0.2345 | 0.2473 |
| 8 | 52 | 0.2188 | 0.2120 | 0.2245 |
| 12 | 78 | 0.1975 | 0.1816 | 0.1934 |

The mean absolute cell-mean error at `d=12` is approximately:

- boundary approximation: `0.00776`;
- Gaussian-logistic Fisher approximation: `0.00615`.

All five Fisher predictions lie inside the corresponding approximate 95% seed-mean intervals.

Across all 20 dimension/budget cells, however, the raw large-`d` laws overpredict much of the low-dimensional error:

| law | cell-mean MAE | signed bias `observed - predicted` | RMSE |
|---|---:|---:|---:|
| boundary `eta_0` | 0.02810 | -0.01001 | 0.03578 |
| Fisher `eta_F` | 0.03194 | -0.02225 | 0.04103 |

Therefore the large-`d` formula should be treated as an asymptotic reference, not a dimension-free finite-sample identity.

## Post-hoc finite-dimensional analysis

Everything in this section was derived **after inspecting the v10a result**. It is explanatory analysis, not a prespecified validation claim.

### Transverse-mode correction

If only the `d-1` slope directions orthogonal to the true `beta` rotate the ranking direction, the approximate transverse error energy under isotropic Fisher information is

\[
E\|e_\perp\|^2
\approx
\frac{d-1}{N a(B)}.
\]

Using `N=kappa(d+1)` gives the finite-dimensional directional coordinate

\[
\eta_{F,d}
=
B^2\kappa a(B)\frac{d+1}{d-1}.
\]

The corresponding simple angle approximation reduces the 20-cell mean MAE from `0.03194` for the uncorrected Fisher law to `0.01749`.

This supports the interpretation that part of the remaining cross-dimensional structure is the ordinary geometry of estimating a direction, not a new preference-model pathology.

### Local Gaussian/MAP approximation

A second post-hoc approximation includes prior shrinkage and separates parallel from transverse logistic Fisher information.

Define

\[
c(B)
=
E_{Z\sim N(0,1)}
\left[\sigma(BZ)(1-\sigma(BZ))Z^2\right].
\]

At `B=0.9`,

\[
c(0.9)=0.1568694691.
\]

With prior precision `lambda=1/4` and `N=kappa(d+1)`, a local Gaussian MAP approximation aligned with the true slope has

\[
\mu_\parallel
=
B\frac{Nc(B)}{Nc(B)+\lambda},
\]

\[
V_\parallel
=
\frac{Nc(B)}{[Nc(B)+\lambda]^2},
\]

and each transverse coordinate has approximate variance

\[
V_\perp
=
\frac{Na(B)}{[Na(B)+\lambda]^2}.
\]

Sampling only this analytic Gaussian approximation and converting its angle to `theta/pi` gives a 20-cell mean MAE of approximately `0.0137`, signed bias approximately `+0.0066`, and RMSE approximately `0.0192`. Nineteen of the 20 v10a cell means contain the no-fitted-parameter local-MAP prediction inside their approximate 95% seed-mean interval; the exception is `d=8, kappa=6`.

This is promising but must be tested prospectively before it becomes part of the S1 sample-complexity claim.

## Tail behavior: why the mean law is not a stopping rule

A calibration system needs a false-stop/tail guarantee, not only a mean expected ordering error.

For `d=12`, the exact population-error distribution is:

| kappa | mean | p90 | P(error < 0.25) | P(error < 0.15) |
|---:|---:|---:|---:|---:|
| 2 | 0.3228 | 0.4422 | 0.2188 | 0.0313 |
| 4 | 0.2757 | 0.3488 | 0.3750 | 0.0313 |
| 6 | 0.2384 | 0.3141 | 0.5313 | 0.0625 |
| 8 | 0.2188 | 0.2954 | 0.8125 | 0.0625 |
| 12 | 0.1975 | 0.2697 | 0.8438 | 0.1875 |

At `d=12, kappa=12`, no one of the 32 runs achieved population ordering error below `0.10`; the maximum error was `0.2931`.

The false-direction rate `P(beta^T m < 0)` also remains nonzero at the smallest budgets. At `kappa=2`, the observed rates over 32 seeds are:

- `d=2`: 12.5%;
- `d=4`: 12.5%;
- `d=8`: 15.625%;
- `d=12`: 6.25%.

These are only 32-seed screening estimates and should not be interpreted as precise tail probabilities.

## Convergence sensitivity

Six of 640 final Laplace fits were flagged non-converged:

- `d=8, kappa=8, seed=9`;
- `d=8, kappa=12, seed=17`;
- `d=12, kappa=8, seeds=16,21`;
- `d=12, kappa=12, seeds=7,14`.

Their metrics were retained rather than silently discarded. Excluding them changes the affected population-error cell means by no more than approximately `0.002`, so the main conclusions do not depend on these six fits.

## Finite random-query geometry remains a separate effect

The **full 18-candidate admissible bank** has exact identity empirical covariance, but a random set of `q` pair queries observes only a subset of those endpoints and repeats some candidates more than others. Therefore the *accumulated observation design* is not generally isotropic at low budget.

A deterministic post-run reconstruction of the selected-pair geometry shows the expected improvement with budget. Examples for the augmented selected design include:

| d | kappa | mean minimum Gram eigenvalue | mean condition number | mean unique endpoints / 18 |
|---:|---:|---:|---:|---:|
| 2 | 2 | 2.07 | 25.9 | 5.22 |
| 2 | 12 | 26.25 | 1.80 | 16.44 |
| 4 | 2 | 2.12 | 79.1 | 8.09 |
| 4 | 12 | 39.11 | 2.08 | 17.66 |
| 8 | 6 | 25.05 | 3.77 | 17.38 |
| 8 | 12 | 73.83 | 2.02 | 18.00 |
| 12 | 6 | 34.73 | 4.00 | 17.91 |
| 12 | 12 | 103.26 | 2.06 | 18.00 |

This explains why controlling the admissible bank is necessary but still not identical to controlling the information accumulated by a finite query sequence.

## Synthetic burden relation

In the large-dimensional passive Gaussian-logistic ideal, solving the Fisher law for `kappa` gives

\[
\kappa
\approx
\frac{1}{B^2a(B)\tan^2(\pi\epsilon)},
\]

and hence

\[
\boxed{
q
\approx
\frac{d+1}{2B^2a(B)}\cot^2(\pi\epsilon).
}
\]

For `B=0.9`, `a(B)=0.21286`, and `d=12`, the ideal **mean-error** pair-query budgets are approximately:

| target mean ordering error | ideal q pairs |
|---:|---:|
| 0.25 | 37.7 |
| 0.20 | 71.4 |
| 0.15 | 145.2 |
| 0.10 | 357.1 |
| 0.05 | 1502.8 |

The observed v10a `d=12, q=78` mean error of `0.1975` is close to the ideal `q≈71` prediction for mean error `0.20`.

These numbers are **not product calibration budgets**. They assume the current synthetic likelihood is correct, a standardized isotropic Gaussian reference population, one fixed signal level, passive sampling, asymptotic information geometry, and a mean-error objective rather than a tail guarantee. The current finite 18-candidate pair pool also contains only 153 unique pairs.

The equation does, however, show why a universal fixed claim such as “20–30 questions is enough” is scientifically unjustified. Required burden can scale strongly with dimension, effective signal, reference-population Fisher weight, finite query geometry, prior information, and the desired tail criterion.

## Scientific disposition

v10a establishes the following within the synthetic S1 model:

1. Fixing true effective slope norm removes a real v7–v9 confound but does **not** imply exact dimension-free collapse against `kappa=N/(d+1)`.
2. The exact Gaussian-population ordering error is the slope angle divided by `pi`; finite held-out ranking estimates are unnecessary for this specific synthetic reference geometry.
3. At `d=12`, the large-dimensional Fisher-weighted sample-complexity law predicts mean ordering error to roughly `0.006` absolute error across the tested budgets.
4. Finite-dimensional transverse-mode geometry and prior shrinkage explain a substantial fraction of the remaining cross-dimensional pattern.
5. Mean performance is insufficient for calibration stopping. Tail and false-direction behavior remain materially worse than the means.
6. Exact conditioning of the full admissible candidate bank does not ensure that a finite random or adaptive query path has a well-conditioned accumulated design.
7. v10a tested only `B=0.9`; it therefore **does not validate the proposed `B^2 a(B) kappa` scaling across signal levels**.

## Next checkpoint

Do **not** turn the v10a mean law directly into a product stopping rule, and do not invent another greedy acquisition score yet.

The next falsification should be a **signal-scaling phase diagram** under the same correctly specified passive controlled-geometry model:

1. prespecify several fixed effective slope norms `B` spanning weak to strong preference surfaces;
2. normalize every synthetic truth exactly to its assigned `B`;
3. retain centered identity-covariance Gaussian-derived query banks;
4. retain passive random querying initially;
5. use enough seeds to resolve both means and lower-tail/false-direction rates;
6. test collapse against

\[
\eta_F=B^2\kappa a(B)
\]

rather than `kappa` alone;
7. prospectively test the finite-dimensional/local-MAP refinements derived after v10a; and
8. only after the signal law survives, construct a posterior-observable stopping statistic and measure false-stop operating curves.

A later active-policy study should then enforce explicit exploration/conditioning while testing whether boundary-focused selection can approach the maximum per-observation Fisher weight `1/4` without reintroducing the adaptive lock-in observed in v9a.