# S1 Ground-Truth Benchmark v3 — Posterior-Aware Acquisition Ablation

## Status

Completed synthetic mechanistic ablation under the correctly specified `visual-acceptance-linear-logit-v1` model.

This result is **not** human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

## Provenance

- benchmark version: `s1-ground-truth-benchmark-v3`
- exact branch head executed by the authoritative v3 benchmark: `56514243317145ea2e7603be811aa15a4eae45bd`
- GitHub Actions run: `31843618651`
- benchmark job: `94905501754`
- artifact ID: `9235296406`
- artifact ZIP SHA-256: `5a3515e166ac12dd81d3ea426dd5bcbc61eb62d64a67d94ce273d080bcc883a9`
- uncompressed JSON SHA-256: `d5d527a9032625c2dbfebd421663322b7b2b19a55dafa91f966c1b2e7b3df2b2`
- raw simulation records: `3072`
- numerical benchmark duration on GitHub Actions: approximately `444 s`

The one-use benchmark workflow had read-only repository permission and was removed after artifact capture. Earlier PR-triggered v3 workflow runs were deliberately ignored because they did not execute the final validated head. Run `31843618651` was branch-scoped and checked out the exact source head above.

## Why v3 was run

V2 established two separate facts:

1. plug-in D-optimal acquisition can make the global inferred probability surface worse than random sampling, especially at larger effective dimension; and
2. none of the existing information-oriented policies had demonstrated a stable top-K advantage over random sampling.

The leading mechanism for the first failure was plug-in uncertainty neglect. At a broad zero-centered posterior, evaluating Bernoulli Fisher information only at the MAP state can treat extreme/high-leverage candidates as if their latent score were known to lie near the logistic decision boundary.

V3 therefore changed **only the acquisition calculation**, not the synthetic ground truth, response model, candidate distribution, fitting model, prior, metrics, or query budgets.

## Policies

V3 compares four policies:

1. `random`
2. `d_optimal` — original plug-in MAP Bernoulli Fisher determinant gain
3. `posterior_fisher_d_optimal` — determinant gain using posterior-averaged Bernoulli Fisher weight
4. `mutual_information_d_optimal` — determinant gain using a rank-one Gaussian-equivalent update whose entropy gain equals the candidate's Bayesian binary mutual information

For augmented feature vector `z` and Laplace posterior

\[
\alpha\sim N(m,\Sigma),
\]

the score distribution is

\[
s=\alpha^Tz\sim N(m^Tz,z^T\Sigma z).
\]

### Posterior-averaged Fisher policy

The local Bernoulli weight is replaced by

\[
\bar w(z)=E[\sigma(s)(1-\sigma(s))],
\]

and the candidate information matrix is

\[
\bar{\mathcal I}(z)=\bar w(z)zz^T.
\]

The expectation is evaluated by deterministic nine-point Gauss-Hermite quadrature.

### Bounded mutual-information policy

For one binary acceptance response,

\[
I(\alpha;Y\mid z,D)
=H(E[p])-E[H(p)],
\]

so

\[
0\le I(\alpha;Y\mid z,D)\le \log 2.
\]

V3 maps this finite information gain to a rank-one Gaussian-equivalent precision update by choosing `lambda` such that

\[
\frac12\log(1+\lambda z^T\Sigma z)
=I(\alpha;Y\mid z,D).
\]

Thus

\[
\lambda=
\frac{\exp(2I)-1}{z^T\Sigma z}.
\]

In the small-posterior-variance limit this converges to the local Bernoulli Fisher update; at broad uncertainty it cannot silently assign more information than a binary response can contain.

## Configuration

```text
feature dimensions       d = 2, 4, 8
pair-query budgets        q = 5, 10, 20, 30
policies                  random, d_optimal,
                          posterior_fisher_d_optimal,
                          mutual_information_d_optimal
scenario seeds            0..63 (64 per cell)
candidate query bank      18 synthetic feature vectors
held-out reference bank   96 synthetic feature vectors
top-K                     8
prior mean                0
prior variance            4 per effective coefficient
slope scale               0.9 / sqrt(d) per generated coefficient
true intercept            0
response model            correctly specified linear-logistic Bernoulli acceptance
```

Total runs:

\[
3\times4\times4\times64=3072.
\]

## Aggregate means

| d | q | policy | excess log loss | probability MSE | top-K regret | top-K overlap | coefficient RMSE | coverage | convergence |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | 5 | random | 0.188615 | 0.057356 | 0.108833 | 0.533203 | 0.771080 | 0.989583 | 1.000000 |
| 2 | 5 | d_optimal | 0.211116 | 0.061611 | 0.098760 | 0.527344 | 0.835802 | 0.968750 | 1.000000 |
| 2 | 5 | posterior_fisher_d_optimal | 0.162790 | 0.053538 | 0.115051 | 0.494141 | 0.707534 | 0.968750 | 1.000000 |
| 2 | 5 | mutual_information_d_optimal | 0.166796 | 0.053934 | 0.104217 | 0.535156 | 0.723418 | 0.984375 | 1.000000 |
| 2 | 10 | random | 0.113283 | 0.037560 | 0.075021 | 0.632812 | 0.589849 | 0.958333 | 1.000000 |
| 2 | 10 | d_optimal | 0.102939 | 0.032353 | 0.046160 | 0.650391 | 0.583207 | 0.968750 | 1.000000 |
| 2 | 10 | posterior_fisher_d_optimal | 0.093793 | 0.031145 | 0.040352 | 0.662109 | 0.561557 | 0.973958 | 1.000000 |
| 2 | 10 | mutual_information_d_optimal | 0.079829 | 0.027671 | 0.041918 | 0.660156 | 0.507004 | 0.979167 | 1.000000 |
| 2 | 20 | random | 0.051823 | 0.018429 | 0.027725 | 0.736328 | 0.397667 | 0.947917 | 1.000000 |
| 2 | 20 | d_optimal | 0.048487 | 0.016205 | 0.035072 | 0.675781 | 0.394853 | 0.937500 | 1.000000 |
| 2 | 20 | posterior_fisher_d_optimal | 0.042277 | 0.015028 | 0.025383 | 0.716797 | 0.359533 | 0.958333 | 1.000000 |
| 2 | 20 | mutual_information_d_optimal | 0.040345 | 0.014039 | 0.020888 | 0.751953 | 0.331250 | 0.953125 | 1.000000 |
| 2 | 30 | random | 0.030055 | 0.012038 | 0.026784 | 0.771484 | 0.302566 | 0.963542 | 1.000000 |
| 2 | 30 | d_optimal | 0.023940 | 0.009142 | 0.022822 | 0.751953 | 0.279340 | 0.958333 | 0.984375 |
| 2 | 30 | posterior_fisher_d_optimal | 0.027967 | 0.010299 | 0.021018 | 0.755859 | 0.287248 | 0.942708 | 1.000000 |
| 2 | 30 | mutual_information_d_optimal | 0.028727 | 0.010224 | 0.018108 | 0.787109 | 0.294397 | 0.958333 | 1.000000 |
| 4 | 5 | random | 0.356398 | 0.094763 | 0.153654 | 0.330078 | 0.905289 | 0.993750 | 1.000000 |
| 4 | 5 | d_optimal | 0.398276 | 0.097249 | 0.122512 | 0.384766 | 0.997162 | 0.981250 | 1.000000 |
| 4 | 5 | posterior_fisher_d_optimal | 0.344465 | 0.093739 | 0.143759 | 0.343750 | 0.891115 | 0.990625 | 1.000000 |
| 4 | 5 | mutual_information_d_optimal | 0.346411 | 0.088715 | 0.139485 | 0.359375 | 0.900896 | 0.984375 | 1.000000 |
| 4 | 10 | random | 0.242692 | 0.066024 | 0.105152 | 0.408203 | 0.729795 | 0.971875 | 1.000000 |
| 4 | 10 | d_optimal | 0.331886 | 0.077201 | 0.084312 | 0.455078 | 0.903485 | 0.940625 | 1.000000 |
| 4 | 10 | posterior_fisher_d_optimal | 0.198339 | 0.056927 | 0.094090 | 0.492188 | 0.641693 | 0.962500 | 1.000000 |
| 4 | 10 | mutual_information_d_optimal | 0.226414 | 0.058542 | 0.086586 | 0.458984 | 0.705746 | 0.953125 | 1.000000 |
| 4 | 20 | random | 0.104210 | 0.033935 | 0.072821 | 0.494141 | 0.461377 | 0.962500 | 1.000000 |
| 4 | 20 | d_optimal | 0.188762 | 0.049227 | 0.070978 | 0.492188 | 0.626026 | 0.887500 | 1.000000 |
| 4 | 20 | posterior_fisher_d_optimal | 0.091124 | 0.030676 | 0.069501 | 0.498047 | 0.420268 | 0.953125 | 1.000000 |
| 4 | 20 | mutual_information_d_optimal | 0.094993 | 0.029567 | 0.050721 | 0.544922 | 0.442958 | 0.943750 | 1.000000 |
| 4 | 30 | random | 0.070277 | 0.023198 | 0.048838 | 0.554688 | 0.372642 | 0.953125 | 1.000000 |
| 4 | 30 | d_optimal | 0.101489 | 0.030036 | 0.052083 | 0.558594 | 0.429873 | 0.909375 | 1.000000 |
| 4 | 30 | posterior_fisher_d_optimal | 0.052175 | 0.018810 | 0.041622 | 0.593750 | 0.312654 | 0.962500 | 1.000000 |
| 4 | 30 | mutual_information_d_optimal | 0.058930 | 0.020242 | 0.037414 | 0.599609 | 0.337540 | 0.953125 | 1.000000 |
| 8 | 5 | random | 0.457812 | 0.113985 | 0.209578 | 0.244141 | 0.784994 | 0.998264 | 1.000000 |
| 8 | 5 | d_optimal | 0.513802 | 0.120192 | 0.207141 | 0.205078 | 0.868776 | 0.998264 | 1.000000 |
| 8 | 5 | posterior_fisher_d_optimal | 0.488427 | 0.115656 | 0.191213 | 0.226562 | 0.839822 | 0.998264 | 1.000000 |
| 8 | 5 | mutual_information_d_optimal | 0.512815 | 0.117984 | 0.186576 | 0.267578 | 0.845673 | 0.987847 | 1.000000 |
| 8 | 10 | random | 0.442137 | 0.102535 | 0.168104 | 0.291016 | 0.795083 | 0.986111 | 1.000000 |
| 8 | 10 | d_optimal | 0.565266 | 0.114919 | 0.168362 | 0.251953 | 0.961912 | 0.967014 | 1.000000 |
| 8 | 10 | posterior_fisher_d_optimal | 0.499945 | 0.111506 | 0.185192 | 0.257812 | 0.861331 | 0.973958 | 1.000000 |
| 8 | 10 | mutual_information_d_optimal | 0.545621 | 0.115453 | 0.153717 | 0.322266 | 0.918118 | 0.954861 | 1.000000 |
| 8 | 20 | random | 0.311313 | 0.077852 | 0.134062 | 0.337891 | 0.650509 | 0.944444 | 1.000000 |
| 8 | 20 | d_optimal | 0.432964 | 0.090883 | 0.114273 | 0.349609 | 0.830344 | 0.918403 | 1.000000 |
| 8 | 20 | posterior_fisher_d_optimal | 0.310407 | 0.078341 | 0.137500 | 0.347656 | 0.639408 | 0.935764 | 1.000000 |
| 8 | 20 | mutual_information_d_optimal | 0.353883 | 0.084868 | 0.132019 | 0.349609 | 0.689152 | 0.911458 | 1.000000 |
| 8 | 30 | random | 0.173397 | 0.051477 | 0.106946 | 0.410156 | 0.470125 | 0.946181 | 1.000000 |
| 8 | 30 | d_optimal | 0.336157 | 0.075898 | 0.106611 | 0.404297 | 0.713944 | 0.883681 | 1.000000 |
| 8 | 30 | posterior_fisher_d_optimal | 0.252188 | 0.065221 | 0.113679 | 0.382812 | 0.555723 | 0.909722 | 1.000000 |
| 8 | 30 | mutual_information_d_optimal | 0.210171 | 0.058737 | 0.100337 | 0.419922 | 0.503829 | 0.920139 | 1.000000 |

## Paired analysis method

All policy comparisons use the same 64 scenario seeds within each `(d,q)` cell. For a metric `m`,

\[
\Delta_m=m_{policy}-m_{baseline}.
\]

Negative deltas are favorable for excess log loss, probability MSE, coefficient RMSE, and top-K regret. Positive deltas are favorable for top-K overlap.

The significance summaries below use 95% percentile bootstrap intervals for the paired mean delta with 10,000 resamples of the 64 seed-level differences. They are Monte-Carlo uncertainty summaries for this synthetic experiment, not human-population confidence intervals.

## Result 1 — posterior integration repairs much of the plug-in D-optimal failure

Against the original plug-in `d_optimal` baseline, `posterior_fisher_d_optimal` is significantly better in:

```text
excess log loss       9 / 12 cells
probability MSE       5 / 12 cells
coefficient RMSE      9 / 12 cells
top-K regret          1 / 12 cells
top-K overlap         0 / 12 cells
```

It is significantly worse than plug-in D-optimal in **zero** cells for those five metrics.

`mutual_information_d_optimal` is also materially better than the plug-in policy:

```text
excess log loss       6 / 12 cells
probability MSE       4 / 12 cells
coefficient RMSE      7 / 12 cells
top-K regret          1 / 12 cells
top-K overlap         3 / 12 cells
```

Again, no cell shows a significant degradation relative to plug-in D-optimal on these metrics.

This strongly supports the v2 mechanism hypothesis: evaluating candidate information at a single uncertain MAP state was a major cause of the original D-optimal policy's global-recovery failures.

## Result 2 — repairing information estimation does not solve the ranking objective

The stronger product-relevant question is not whether a policy beats the defective plug-in D-optimal score. It is whether it beats a simple random baseline on the **decision metric Mosaic actually cares about at this stage**.

Against random sampling, `posterior_fisher_d_optimal` gives significantly lower top-K regret in only one cell:

```text
d = 2, q = 10
```

The other 11 cells are unresolved. It also remains significantly worse than random in some global-recovery cells at `d=8`.

Against random sampling, `mutual_information_d_optimal` gives significantly lower top-K regret in two cells:

```text
d = 2, q = 10
d = 4, q = 20
```

The remaining ten cells are unresolved. It likewise remains significantly worse than random in selected `d=8` global-recovery cells.

Therefore:

> **Posterior uncertainty integration repairs the information model, but does not establish a generally superior ranking policy.**

This is the key v3 result.

## Result 3 — the finite one-bit bound is theoretically cleaner, but not the missing performance ingredient here

The Bayesian mutual-information construction is preferable conceptually because one binary response cannot contain more than `log(2)` nats of information. It removes an unbounded local-Gaussian-information interpretation that can become misleading for broad posteriors.

However, paired `mutual_information_d_optimal` versus `posterior_fisher_d_optimal` comparisons show:

```text
significant difference in excess log loss       0 / 12 cells
significant difference in probability MSE       0 / 12 cells
significant difference in top-K regret           0 / 12 cells
significant difference in top-K overlap          0 / 12 cells
significant difference in coefficient RMSE       1 / 12 cells
```

The lone coefficient-RMSE difference is at `d=8,q=10`, where mutual-information D-optimal is worse.

Thus the finite-response-information bound is a sound theoretical correction, but **posterior integration itself explains most of the practical repair observed in this benchmark regime**.

## What v3 establishes

Under the exact synthetic assumptions tested:

1. the v2 plug-in-uncertainty failure mechanism is substantially supported;
2. posterior-averaged Fisher and bounded Bayesian mutual-information acquisition both repair much of the original D-optimal global-recovery defect;
3. the bounded mutual-information construction does not materially outperform posterior-averaged Fisher in this regime;
4. a better information-acquisition objective is still not the same thing as a better top-K decision objective;
5. neither posterior-aware information policy has demonstrated a robust, general top-K advantage over random sampling; and
6. the next scientific step should change the **decision objective**, not add another variant of Fisher-information estimation.

## What v3 does not establish

V3 still does not establish:

- the effective dimensionality of human visual preference;
- the adequacy of a linear-logistic acceptance surface;
- the realism of the Gaussian feature bank;
- the transfer of synthetic-candidate willingness-to-meet judgments to real profile choices;
- the conditional-independence assumption of the four-option instrument;
- whether posterior-aware acquisition remains advantageous under likelihood misspecification;
- whether a ranking-aligned policy can beat random sampling; or
- any universal calibration-query count.

## Next scientific experiment — expected ranking-regret reduction

The next acquisition experiment should optimize the **decision Mosaic will actually make** rather than a surrogate parameter-information volume.

Let `D` be current evidence and let the downstream decision be the top-`K` candidate set. Define current posterior decision risk

\[
\mathcal R_K(D)
=E_{\alpha\sim p(\alpha\mid D)}
[L_K(a^*(\alpha),\hat a(D))],
\]

where `L_K` is a ranking/set decision loss and `a*(alpha)` is the oracle top-`K` decision under state `alpha`.

For candidate query `q` with possible response `Y_q`, define one-step expected value of information for the actual decision:

\[
\mathrm{ERV}_K(q)
=
\mathcal R_K(D)
-
E_{Y_q\mid D}[\mathcal R_K(D\cup\{Y_q\})].
\]

The next benchmark should compare a tractable approximation to `ERV_K(q)` against:

- random sampling;
- posterior-averaged Fisher D-optimal; and
- bounded mutual-information D-optimal.

The ranking-aligned policy should be considered successful only if it lowers out-of-sample top-K regret without silently producing pathological probability calibration or posterior instability.

This is now the strongest S1 path because v3 has separated two problems:

\[
\boxed{\text{uncertainty-aware information acquisition}}
\]

from

\[
\boxed{\text{decision-aligned query acquisition}}.
\]

The first is substantially repaired. The second remains open.
