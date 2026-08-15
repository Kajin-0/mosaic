# Science S1 v9a — Gaussian Controlled-Geometry Replication

## Status

Completed exploratory synthetic benchmark. Four seeds remain screening evidence only. This is not human-subject, attraction-transfer, compatibility, or relationship-outcome validation.

## Question

v8a replaced the fixed 18-candidate iid-Gaussian query bank with a deterministic centered DCT tight frame and found that much of the apparent high-dimensional penalty contracted when the augmented static design was exactly conditioned.

v9a asks a narrower falsification question:

> Does that recovery survive when the DCT support is replaced by a stochastic Gaussian-derived query bank whose columns are centered and orthogonalized/rescaled so that the same first- and second-moment geometry is exact?

A positive result would implicate well-conditioned query geometry rather than one special DCT pattern. A negative result would show that higher-order support geometry and/or adaptive response paths remain material even after covariance conditioning is fixed.

## Provenance

- benchmark version: `s1-gaussian-controlled-geometry-benchmark-v9a`
- query-design version: `centered-orthogonalized-gaussian-v1`
- model version: `visual-acceptance-linear-logit-v1`
- executed science head: `4821aa71c652dc34a94507bdef20e4e6e0520538`
- GitHub Actions run: `31880429036`
- benchmark job: `95002120601`
- artifact: `9246020259`
- artifact ZIP SHA-256: `2d5413103189eeae73457c05a193dc4f71c2b8e784532b41dd4afc7b5f7b4a02`
- benchmark JSON SHA-256: `36a3a7d1521f23c0faf6576ffadc99789cb1993f7c70baf7b3fed718c1d66ac9`
- authoritative Phase 7 repository gate on the same executed head: run `31880431194`, PASS
- raw simulations: 240
- converged final Laplace fits: 239 / 240

The one non-converged final fit is `d=8`, `kappa=12`, posterior-Fisher, seed 1. Its metrics are retained rather than silently dropped.

The one-use workflow was removed after the artifact was harvested.

## Construction

For every `(d, seed)`, v9a regenerates the exact v7a iid-Gaussian candidate bank `X`, centers each feature column, and applies two-pass modified Gram-Schmidt. The resulting columns are rescaled to norm `sqrt(n)`:

\[
X_c = HX,
\qquad
X_c = QR,
\qquad
X_9 = \sqrt n\,Q,
\]

with

\[
H=I-\frac{11^T}{n}.
\]

Therefore, up to floating-point error,

\[
1^T X_9=0,
\qquad
\frac{1}{n}X_9^T X_9=I_d.
\]

For the augmented design

\[
Z=[1,X_9],
\]

this gives

\[
\frac{1}{n}Z^T Z=I_{d+1}.
\]

Everything else is paired to v7a/v8a:

- `d = {2,4,8,12}`;
- target `kappa = {2,4,6,8,12}`;
- four scenario seeds;
- 18 admissible query candidates;
- 96 held-out Gaussian candidates;
- the same true `alpha` and held-out bank for a given `(d, seed)`;
- the same Bernoulli response RNG stream;
- the same query counts;
- the same prior;
- random, posterior-Fisher D-optimal, and exact-Gaussian score-regret policies.

The Gaussian-derived orthogonalized bank is therefore a stochastic tight-frame control rather than another deterministic DCT design.

## Local analytic interpretation

If every binary observation were exactly on the logistic boundary, `p=1/2`, then

\[
\mathcal I = \sum_j p_j(1-p_j)z_jz_j^T
            = \frac14 Z^T Z.
\]

For a balanced controlled bank,

\[
\mathcal I=\frac{n}{4}I.
\]

Under fixed total design energy, equal information eigenvalues simultaneously maximize the weakest eigenvalue and the determinant. This gives the v8/v9 construction a local E-/D-optimal interpretation rather than treating conditioning as an empirical trick.

At the actual nonzero synthetic slopes, the logistic weights are unequal. A deterministic post-run reconstruction using the recorded seeds still gives the following mean full-bank true-Fisher geometry at `d=12`:

| query bank | mean minimum Fisher eigenvalue | mean Fisher condition |
|---|---:|---:|
| v7 raw Gaussian | 0.301 | 58.67 |
| v8 DCT tight frame | 2.846 | 1.61 |
| v9 Gaussian-derived tight frame | 2.732 | 1.68 |

Thus v8 and v9 remain nearly equivalent at the level of the complete true weighted information spectrum even after logistic weighting.

## Primary result

### 1. High-dimensional recovery largely replicates

For `d=12`, posterior-Fisher retains most of the v8 recovery relative to v7:

| benchmark | kappa | pair regret | ordering error | top-K regret | slope cosine |
|---|---:|---:|---:|---:|---:|
| v7 | 4 | 0.0577 | 0.3549 | 0.1651 | 0.4689 |
| v8 | 4 | 0.0242 | 0.2182 | 0.0735 | 0.7722 |
| v9 | 4 | 0.0316 | 0.2624 | 0.0886 | 0.6273 |
| v7 | 6 | 0.0538 | 0.3293 | 0.1838 | 0.4786 |
| v8 | 6 | 0.0250 | 0.2303 | 0.0704 | 0.7379 |
| v9 | 6 | 0.0238 | 0.2257 | 0.0577 | 0.7224 |
| v7 | 8 | 0.0627 | 0.3667 | 0.1909 | 0.4131 |
| v8 | 8 | 0.0233 | 0.2181 | 0.0773 | 0.7458 |
| v9 | 8 | 0.0197 | 0.2027 | 0.0499 | 0.7642 |
| v7 | 12 | 0.0543 | 0.3289 | 0.1761 | 0.4891 |
| v8 | 12 | 0.0136 | 0.1666 | 0.0324 | 0.8308 |
| v9 | 12 | 0.0156 | 0.1778 | 0.0379 | 0.8085 |

At `d=12, kappa={6,8,12}`, posterior-Fisher v9 improves top-K regret over v7 in all four paired seeds. At `kappa={8,12}`, pair regret also improves in all four seeds.

The exact-Gaussian ranking policy shows the same broad high-dimensional recovery, although individual cells move above or below the DCT result.

### 2. High-budget cross-dimensional contraction is robust

At `kappa=12`, the range across `d={2,4,8,12}` contracts strongly relative to v7:

| policy | benchmark | pair-regret range | top-K-regret range | slope-cosine range |
|---|---|---:|---:|---:|
| posterior-Fisher | v7 | 0.0511 | 0.1723 | 0.4878 |
| posterior-Fisher | v8 | 0.0126 | 0.0453 | 0.1409 |
| posterior-Fisher | v9 | 0.0165 | 0.0403 | 0.1700 |
| exact ranking | v7 | 0.0390 | 0.1034 | 0.3793 |
| exact ranking | v8 | 0.0097 | 0.0511 | 0.1253 |
| exact ranking | v9 | 0.0156 | 0.0463 | 0.1752 |

The v8 contraction is therefore not simply a DCT-specific high-budget artifact.

### 3. But covariance conditioning is not sufficient at moderate budget

v9a also creates a real counterexample to the stronger claim.

At `d=4`, both active policies can become substantially worse than random at moderate `kappa`, despite the full admissible bank satisfying exact identity empirical covariance.

For example:

| d | kappa | policy | pair regret | ordering error | top-K regret | slope cosine |
|---:|---:|---|---:|---:|---:|---:|
| 4 | 4 | random | 0.0283 | 0.2548 | 0.0875 | 0.6823 |
| 4 | 4 | posterior-Fisher | 0.0907 | 0.5145 | 0.2655 | -0.0854 |
| 4 | 4 | exact ranking | 0.0909 | 0.5122 | 0.2659 | -0.0188 |
| 4 | 6 | random | 0.0226 | 0.2296 | 0.0660 | 0.7263 |
| 4 | 6 | posterior-Fisher | 0.0767 | 0.4650 | 0.2321 | 0.0885 |
| 4 | 6 | exact ranking | 0.0425 | 0.3080 | 0.1132 | 0.4961 |

This is not explained by static rank deficiency.

A deterministic reconstruction of the selected `d=4`, posterior-Fisher, seed-2, `kappa=6` observations gives an unweighted selected-design condition of about `4.53` and a true weighted-Fisher condition of about `4.75`, yet the final slope cosine is `-0.770`.

The response stream itself is strongly misleading on that adaptive path. Defining the descriptive signed true-utility signal

\[
S=\sum_t (2Y_t-1)s_t,
\qquad s_t=\beta^T x_t,
\]

that path realizes

```text
observed S          = -1.255
conditional E[S]    =  4.733
conditional SD[S]   =  2.937
standardized offset = -2.04
```

Likewise, the `d=4`, exact-ranking, seed-1, `kappa=4` path realizes a standardized offset of approximately `-2.82` and finishes with the wrong slope direction.

These offsets are descriptive diagnostics, not valid unconditional p-values, because the selected candidate sequence is itself adaptive to earlier responses. They nevertheless identify the mechanism: **finite Bernoulli noise can steer an adaptive learner onto a bad path even when the admissible stimulus bank is perfectly conditioned.**

Geometry repairs the available experiment. It does not make every finite adaptive response history informative.

## A second confound exposed by v9a: realized slope signal was not held fixed

The generator uses coefficient component scale

\[
0.9/\sqrt d,
\]

so `E[||beta||^2]=0.9^2`, but v7-v9 use only four seeds per dimension. The realized mean slope norms are therefore substantially different:

| d | mean `||beta||` | min | max |
|---:|---:|---:|---:|
| 2 | 1.1547 | 0.7024 | 1.5340 |
| 4 | 0.6811 | 0.5166 | 0.8509 |
| 8 | 0.9811 | 0.8537 | 1.1825 |
| 12 | 0.8115 | 0.5621 | 1.0004 |

The mean effective slope signal therefore varies by about 69% between the sampled `d=4` and `d=2` conditions.

Because the feature basis is standardized, `||beta||` is an identifiable effective signal magnitude for this synthetic model. It must not be renamed a domain-general psychological preference strength, and it would change under a different feature scaling.

This realized-signal imbalance means `kappa = N/(d+1)` cannot be expected to collapse the four-seed cells by itself even after query geometry is controlled.

## Exact bridge from slope direction to Gaussian-population ordering error

For two independent isotropic Gaussian candidates,

\[
\Delta X=X_a-X_b\sim N(0,2I).
\]

The true and fitted score differences

\[
U=\beta^T\Delta X,
\qquad
V=m^T\Delta X
\]

are jointly zero-mean Gaussian with correlation

\[
\rho=\frac{\beta^T m}{\|\beta\|\|m\|}=\cos\theta.
\]

The Gaussian sign identity therefore gives the exact population wrong-order probability

\[
\boxed{
\epsilon_{ord}=\frac{\arccos(\rho)}{\pi}=\frac{\theta}{\pi}
}
\]

for fixed nonzero `beta` and `m`.

This explains why slope direction has been so diagnostic throughout S1. Across all 240 v9a finite held-out evaluations, `acos(slope_cosine)/pi` tracks the empirical 96-candidate ordering-error metric with correlation approximately `0.988` and mean absolute discrepancy approximately `0.0168`. The discrepancy is expected because the benchmark uses a finite held-out bank and averages over finite runs.

## Ideal controlled-geometry sample-complexity coordinate

Under an additional asymptotic idealization:

1. the accumulated observation design is isotropic;
2. observations remain near enough to the logistic boundary that Fisher weight is approximately `1/4`;
3. the posterior/MAP slope error is approximately isotropic Gaussian; and
4. `N = kappa(d+1)` binary observations with large `d`,

the per-coordinate variance approaches `4/N`, while the total slope-error energy concentrates near

\[
\frac{4d}{N}\to\frac4\kappa.
\]

For true effective slope norm

\[
B=\|\beta\|,
\]

the fitted slope cosine then concentrates near

\[
\rho(\kappa,B)
\approx
\frac{B}{\sqrt{B^2+4/\kappa}}.
\]

Combining this with the exact Gaussian ordering identity gives

\[
\boxed{
\epsilon_{ord}(\kappa,B)
\approx
\frac1\pi\arctan\left(\frac{2}{B\sqrt\kappa}\right)
}
\]

or, defining

\[
\eta=\frac{B^2\kappa}{4},
\]

\[
\epsilon_{ord}\approx\frac1\pi\arctan(\eta^{-1/2}).
\]

This suggests that the more natural idealized directional sample-complexity coordinate is **effective signal times observations per parameter**, `B^2 kappa`, rather than `kappa` alone.

This is an analytic asymptotic hypothesis, not yet a validated stopping rule.

## Scientific disposition

v9a supports all of the following simultaneously:

1. **The v7 high-dimensional penalty was substantially contaminated by poor finite-bank geometry.**
2. **The v8 recovery is not merely DCT-specific at moderate/high dimension and high budget.** A stochastic Gaussian-derived tight frame preserves most of the recovery.
3. **Exact covariance conditioning is not sufficient for reliable active learning at small samples.** Response noise and adaptive path dependence can still reverse the inferred direction.
4. **`kappa` alone was incompletely controlled.** Four seeds leave substantial realized variation in effective slope norm `B`.
5. **Ordering error has a clean exact geometric representation for the Gaussian reference population.** This exposes a theoretically motivated combined coordinate `B^2 kappa` for the next falsification test.

Do **not** respond to the `d=4` failures by inventing another acquisition heuristic yet. The next experiment should first determine whether the new signal-normalized analytic law survives when the known confounds are deliberately removed.

## Next checkpoint

Run an **exact-slope-norm, broader-seed controlled-geometry benchmark** before adding model complexity or changing live calibration semantics.

The next study should:

1. draw slope directions randomly but normalize every synthetic truth to the same prespecified `||beta|| = B`;
2. retain centered identity-covariance query geometry;
3. use many more seeds than four;
4. validate the exact relation `ordering error = angle/pi` on the held-out Gaussian population;
5. test whether cells collapse more cleanly against

\[
\eta=B^2\kappa/4
\]

than against `kappa` alone;
6. quantify the lower tail / false-direction rate of adaptive policies rather than reporting only cell means; and
7. separate a passive/random-policy law-validation stage from a later adaptive-policy robustness stage so adaptive lock-in is not confused with the base statistical limit.

Only after that should S1 convert the analytic coordinate into a candidate stopping rule and test false-stop operating curves under misspecification.