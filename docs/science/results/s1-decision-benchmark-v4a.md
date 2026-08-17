# S1 Decision Benchmark v4a — Finite-Pool Top-K EVSI

## Status

Completed exploratory synthetic benchmark under the correctly specified `visual-acceptance-linear-logit-v1` model.

This result is **hypothesis-generating only**. It uses eight seeds per cell and is not human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

The principal result is negative: a one-step top-K EVSI policy tied to one finite sampled decision bank does **not** show a sufficiently robust out-of-sample ranking advantage to justify simply increasing the seed count.

## Provenance

- benchmark version: `s1-decision-benchmark-v4a`
- exact branch head executed: `5e172543320d9cf7d5e9a3d6d51d2977611bcf20`
- GitHub Actions run: `31851302725`
- benchmark job: `94927469812`
- artifact ID: `9237639130`
- artifact ZIP SHA-256: `481c4ae56b179612a978b01d36eb023ff9e56f3518ffa036a04e5f847a9fe7d5`
- uncompressed JSON SHA-256: `1c3cab18d83a104aae084cee578c10ba74b5435cf26827f40a1a588c4a75157a`
- raw simulation records: `192`
- numerical benchmark duration on GitHub Actions: approximately `149 s`

The one-use workflow had read-only repository permission and was removed after artifact capture.

## Why v4a was run

V3 established that posterior-aware information acquisition repairs much of the defective plug-in Fisher behavior, but it did **not** establish a generally superior top-K ranking policy.

V4a therefore changed the acquisition objective from parameter-information volume to an approximation of the actual downstream decision value.

For a finite decision bank `B`, let

\[
V_K(D;B)
=
\max_{S\subset B,\ |S|=K}
\frac{1}{K}\sum_{x\in S}E[p_x\mid D],
\]

where `p_x` is the acceptance probability under the uncertain preference state.

For a candidate query pair `q` with possible binary response vector `Y_q`, v4a scores

\[
\operatorname{EVSI}_K(q;B)
=
E_{Y_q\mid D}[V_K(D\cup\{Y_q\};B)]-V_K(D;B).
\]

The acquisition decision bank is deliberately separate from the held-out evaluation bank.

## Hypothetical posterior approximation

The first implementation mixed independently approximated moment systems and failed a tiny benchmark with an **indefinite hypothetical covariance**. That failure was not clipped away.

The derivation was corrected so all score/response moments come from one coherent joint nine-by-nine Gauss-Hermite quadrature for the two latent candidate scores `S=(S_A,S_B)` and binary responses `Y=(Y_A,Y_B)`.

The linear-Bayes projection now uses

\[
\operatorname{Cov}(\alpha,Y)
=
\Sigma Z(Z^T\Sigma Z)^+\operatorname{Cov}(S,Y),
\]

with all covariance blocks derived from the same approximate joint distribution. The corrected covariance regression then passed Ruff, mypy, and the full engine test suite, including the tiny case that had exposed the defect.

This failed avenue is important: mathematically compatible moment identities can still produce an invalid covariance update if their finite numerical approximations are assembled inconsistently.

## Acquisition-only speed approximation

Exact logistic-normal means inside every hypothetical top-K calculation were too expensive for repeated query scoring. V4a therefore uses the standard approximation

\[
E[\sigma(S)]
\approx
\sigma\!\left(
\frac{\mu}{\sqrt{1+\pi v/8}}
\right)
\]

**only inside acquisition scoring**.

A committed numerical contract compares this approximation with the existing GH9 reference over

```text
mean      = -6,-4,-3,-2,-1,0,1,2,3,4,6
variance  = 0,0.1,0.5,1,2,4,8,16
```

and requires maximum absolute probability error below `0.02`.

Posterior fitting, response generation, and held-out benchmark metrics remain on the existing exact/reference path.

## Configuration

```text
feature dimensions       d = 2, 4, 8
pair-query budgets        q = 10, 20
scenario seeds            0..7
query candidate bank      18 synthetic feature vectors
acquisition decision bank 32 independently generated feature vectors
held-out evaluation bank  96 independently generated feature vectors
top-K                     8
prior mean                0
prior variance            4 per effective coefficient
slope scale               0.9 / sqrt(d) per generated coefficient
true intercept            0
response model            correctly specified linear-logistic Bernoulli acceptance
```

Policies:

1. `random`
2. `posterior_fisher_d_optimal`
3. `mutual_information_d_optimal`
4. `expected_top_k_evsi`

Total runs:

\[
3\times2\times4\times8=192.
\]

## Aggregate means

| d | q | policy | excess log loss | probability MSE | top-K regret | top-K overlap | coefficient RMSE | coverage | convergence |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | 10 | random | 0.129199 | 0.043195 | 0.092049 | 0.546875 | 0.637444 | 0.958333 | 1.000000 |
| 2 | 10 | posterior_fisher_d_optimal | 0.063844 | 0.022909 | 0.064531 | 0.656250 | 0.501706 | 1.000000 | 1.000000 |
| 2 | 10 | mutual_information_d_optimal | 0.060837 | 0.020178 | 0.075557 | 0.578125 | 0.495414 | 1.000000 | 1.000000 |
| 2 | 10 | expected_top_k_evsi | 0.087427 | 0.022639 | **0.019987** | **0.687500** | 0.548728 | 1.000000 | 1.000000 |
| 2 | 20 | random | 0.048675 | 0.016852 | **0.006537** | 0.828125 | 0.400344 | 0.958333 | 1.000000 |
| 2 | 20 | posterior_fisher_d_optimal | 0.054173 | 0.015520 | 0.056528 | 0.640625 | 0.430730 | 0.916667 | 1.000000 |
| 2 | 20 | mutual_information_d_optimal | **0.035799** | **0.013365** | 0.016742 | 0.765625 | **0.328287** | 0.958333 | 1.000000 |
| 2 | 20 | expected_top_k_evsi | 0.043231 | 0.014043 | 0.007257 | **0.859375** | 0.360032 | 1.000000 | 1.000000 |
| 4 | 10 | random | 0.196686 | 0.059698 | 0.136554 | 0.484375 | 0.623931 | 1.000000 | 1.000000 |
| 4 | 10 | posterior_fisher_d_optimal | 0.224607 | 0.074675 | 0.187392 | 0.421875 | 0.719496 | 0.950000 | 1.000000 |
| 4 | 10 | mutual_information_d_optimal | **0.160763** | **0.048585** | **0.074882** | **0.562500** | **0.587906** | 1.000000 | 1.000000 |
| 4 | 10 | expected_top_k_evsi | 0.208661 | 0.055579 | 0.097832 | 0.500000 | 0.717391 | 0.925000 | 1.000000 |
| 4 | 20 | random | **0.053206** | **0.019141** | 0.069694 | 0.531250 | **0.319979** | 0.975000 | 1.000000 |
| 4 | 20 | posterior_fisher_d_optimal | 0.076190 | 0.030166 | 0.123838 | 0.406250 | 0.398153 | 0.975000 | 1.000000 |
| 4 | 20 | mutual_information_d_optimal | 0.078172 | 0.025285 | **0.043161** | **0.578125** | 0.428392 | 0.975000 | 1.000000 |
| 4 | 20 | expected_top_k_evsi | 0.097915 | 0.030382 | 0.061483 | 0.546875 | 0.458135 | 0.975000 | 1.000000 |
| 8 | 10 | random | 0.495577 | 0.119593 | 0.201074 | 0.250000 | 0.819915 | 0.986111 | 1.000000 |
| 8 | 10 | posterior_fisher_d_optimal | **0.423958** | **0.103894** | 0.200684 | 0.218750 | 0.785163 | 0.958333 | 1.000000 |
| 8 | 10 | mutual_information_d_optimal | 0.572293 | 0.126288 | **0.175042** | **0.265625** | 0.901925 | 0.944444 | 1.000000 |
| 8 | 10 | expected_top_k_evsi | 0.499435 | 0.127787 | 0.250186 | 0.125000 | **0.766507** | 0.972222 | 1.000000 |
| 8 | 20 | random | 0.409442 | 0.106641 | 0.228831 | 0.156250 | 0.735004 | 0.875000 | 1.000000 |
| 8 | 20 | posterior_fisher_d_optimal | **0.155778** | **0.052239** | **0.107240** | **0.359375** | **0.441177** | 0.958333 | 1.000000 |
| 8 | 20 | mutual_information_d_optimal | 0.263987 | 0.072628 | 0.133288 | **0.359375** | 0.580719 | 0.916667 | 1.000000 |
| 8 | 20 | expected_top_k_evsi | 0.304075 | 0.093300 | 0.217218 | 0.218750 | 0.543644 | 0.944444 | 1.000000 |

## Result 1 — finite-pool EVSI does not dominate out of sample

By mean held-out top-K regret, `expected_top_k_evsi` is the best policy in only **one of six** cells:

```text
d = 2, q = 10
```

At `d=2,q=20` it is nearly tied with random. At `d=4` it is competitive but does not beat mutual-information acquisition. At `d=8` it is poor, particularly at `q=10`.

With only eight paired scenarios, these differences must not be treated as inferentially established. The important screening result is that the pattern is not sufficiently uniform to justify a large replication of the same finite-bank objective.

## Result 2 — the low-dimensional signal is real enough to preserve, but not enough to promote

At `d=2,q=10`, mean held-out regret falls from

```text
random                         0.092049
posterior_fisher_d_optimal     0.064531
mutual_information_d_optimal   0.075557
expected_top_k_evsi            0.019987
```

The paired EVSI-vs-random mean delta is `-0.0721`, but the median paired delta is only about `-0.0100`; EVSI is better in five of eight seeds with one tie. The large mean improvement therefore contains substantial seed-to-seed heterogeneity.

At `d=4,q=10`, EVSI's mean improvement over random is also driven by heterogeneous scenarios: its mean regret is lower than random (`0.0978` vs `0.1366`), while its median paired difference is slightly unfavorable.

This is exactly why v4a was prespecified as an exploratory screen.

## Result 3 — high dimension exposes a scope mismatch

At `d=8`, EVSI does not improve the held-out ranking problem:

```text
q = 10: EVSI regret 0.250186 vs random 0.201074
q = 20: EVSI regret 0.217218 vs random 0.228831,
        but posterior-Fisher reaches 0.107240
```

The most plausible interpretation is not simply that decision alignment is useless. V4a aligns the query policy to **one sampled 32-candidate bank** while evaluating on a different 96-candidate bank. In higher effective dimension, one finite bank is a noisier representation of the future candidate distribution and can steer acquisition toward idiosyncratic local ranking boundaries.

Therefore the scientific target must be distinguished:

- **pool-specific decision optimization** — learn what is needed to choose among the candidates currently present;
- **general preference identification** — learn a state that ranks future candidates drawn from a reference population.

S1 is presently testing the second target. A one-bank top-K EVSI objective is not the cleanest decision functional for that target.

## Result 4 — negative EVSI diagnostics are tiny approximation residuals

Across 48 EVSI simulation runs, seven selected query scores were slightly negative. All occurred late in `q=20` runs:

- three affected runs at `d=2`;
- one affected run at `d=4`;
- none at `d=8`.

The most negative selected value was approximately

\[
-4.89\times10^{-5}.
\]

The mean selected EVSI across all EVSI runs was approximately `0.03695`.

Exact Bayesian EVSI cannot be negative. These tiny values are therefore retained as a diagnostic of the linear-Bayes / logistic-normal acquisition approximation rather than clipped to zero. Their scale is small relative to the early-query EVSI scores (~0.17–0.25 maxima in these runs), and they do not explain the large `d=8` ranking failure.

## What v4a establishes

Under the exact synthetic assumptions tested:

1. a coherent joint-moment linear-Bayes update can support one-step decision-valued query scoring without the indefinite covariance defect of the first implementation;
2. the fast logistic-normal mean approximation makes the benchmark computationally practical while leaving held-out evaluation unchanged;
3. finite-bank top-K EVSI can be highly effective in some low-dimensional scenarios;
4. it does not robustly dominate posterior-information policies or random sampling out of sample;
5. a larger replication of the **same one-bank objective** is not the strongest next experiment; and
6. the distinction between current-pool optimization and general future-candidate ranking is now scientifically material.

## What v4a does not establish

V4a does not establish:

- that decision-aligned acquisition is inferior in general;
- that the `d=8` result survives larger replication;
- that 32 candidates is an adequate Monte Carlo representation of a future candidate population;
- that the linear-Bayes hypothetical update is accurate enough for human-scale posterior uncertainty;
- that the logistic-normal acquisition approximation preserves pair ordering for every possible query;
- the effective dimensionality of real attraction preference;
- the transfer of synthetic preference judgments to real profiles; or
- any universal query budget.

## Next scientific objective — population ranking risk

The next branch should remove the arbitrary single top-K decision bank and optimize out-of-sample **ranking uncertainty** directly.

For two future candidate feature vectors `x_a,x_b`, define augmented difference

\[
\delta z=z_a-z_b.
\]

Under the current Gaussian/Laplace preference posterior,

\[
\Delta s=\alpha^T\delta z
\sim
N(\mu_\Delta,\sigma_\Delta^2),
\]

with

\[
\mu_\Delta=m^T\delta z,
\qquad
\sigma_\Delta^2=\delta z^T\Sigma\delta z.
\]

Because sigmoid is monotone, the posterior probability that the current mean-score ordering is wrong is

\[
r(x_a,x_b\mid D)
=
\Phi\!\left(-\frac{|\mu_\Delta|}{\sigma_\Delta}\right).
\]

Average this over a versioned reference distribution of future candidate pairs:

\[
R_{\mathrm{rank}}(D)
=
E_{x_a,x_b\sim P_{\mathrm{ref}}}
[r(x_a,x_b\mid D)].
\]

For a calibration query `q`, choose the expected reduction

\[
q^*
=
\arg\max_q
\left[
R_{\mathrm{rank}}(D)
-
E_{Y_q\mid D}R_{\mathrm{rank}}(D\cup\{Y_q\})
\right].
\]

This objective has three advantages for S1:

1. it directly targets future ranking rather than parameter-volume reduction;
2. it integrates over the reference candidate distribution rather than one sampled decision pool; and
3. score-order risk is analytic under the Gaussian posterior because sigmoid is monotone.

It should be benchmarked against random, posterior-Fisher, mutual-information, and finite-bank EVSI acquisition while retaining held-out probability calibration as a guardrail.
