# S1 Ground-Truth Benchmark v2 — Paired Replication

## Status

Completed synthetic replication under the correctly specified `visual-acceptance-linear-logit-v1` model.

This result is **not** human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

## Provenance

- benchmark version: `s1-ground-truth-benchmark-v2`
- branch head that triggered the benchmark: `dce887ba12ff20b96009289c5d776e3725b2709e`
- PR merge-ref checked out by the benchmark runner: `8a5b46ad80e4e3901e017fef8a7ffd42a7a63818`
- GitHub Actions run: `31842329516`
- benchmark job: `94901666071`
- artifact ID: `9234750185`
- artifact ZIP SHA-256: `16f82187268835ec282ce248fb39457b6a1e3937f5373aa2ba6c7cb390b2ff9b`
- uncompressed JSON SHA-256: `13f9bce144636c3385c089ef8834bda2f69a4ff76970641a2d7bfa05c6dc5999`
- raw simulation records: `2304`

The one-use benchmark workflow used read-only repository permission and was removed after artifact capture.

## Why v2 was run

V1 used only 12 seeds per cell and stored aggregate summaries. It produced a striking apparent D-optimal ranking advantage at `d=8, q=20`, while also showing cases where parameter/predictive fit and top-K decision quality moved in opposite directions.

V2 was intentionally a **replication and measurement correction**, not a new algorithm experiment:

1. increase from 12 to 64 scenario seeds per cell;
2. retain every seed-level result;
3. keep the same random, boundary-only, and plug-in D-optimal policies;
4. keep the same candidate/held-out geometry and true model family; and
5. split raw cross-entropy into oracle entropy plus reducible excess log loss.

## Configuration

```text
feature dimensions       d = 2, 4, 8
pair-query budgets        q = 5, 10, 20, 30
policies                  random, boundary, d_optimal
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
3\times4\times3\times64=2304.
\]

## Corrected predictive metric

For true probability `p` and fitted probability `p_hat`, v2 records

\[
L_{oracle}=E[-p\log p-(1-p)\log(1-p)],
\]

\[
L_{cross}=E[-p\log\hat p-(1-p)\log(1-\hat p)],
\]

and the reducible loss

\[
L_{excess}=L_{cross}-L_{oracle}
=E[D_{KL}(Bern(p)\Vert Bern(\hat p))].
\]

This removes irreducible Bernoulli entropy from the model-error comparison. `probability_mse` remains the reducible/excess Brier component.

## Paired analysis

Policies were compared seed-by-seed within the same `(d,q)` scenario. For each metric,

\[
\Delta_m=m_{policy}-m_{random}.
\]

Thus negative deltas are better for excess log loss, probability MSE, coefficient RMSE, and top-K regret. Positive deltas are better for top-K overlap.

The intervals below are 95% percentile bootstrap intervals for the **paired mean delta**, using 10,000 resamples of the 64 seed-level differences. They are Monte-Carlo uncertainty summaries for this synthetic experiment, not human-population confidence intervals.

## D-optimal versus random

| d | q | Δ excess log loss | Δ probability MSE | Δ top-K regret | Δ top-K overlap |
|---:|---:|---:|---:|---:|---:|
| 2 | 5 | +0.0225 [-0.0286,+0.0729] | +0.0043 [-0.0094,+0.0177] | -0.0101 [-0.0514,+0.0300] | -0.0059 [-0.1152,+0.1016] |
| 2 | 10 | -0.0103 [-0.0404,+0.0181] | -0.0052 [-0.0140,+0.0030] | -0.0289 [-0.0664,+0.0027] | +0.0176 [-0.0820,+0.1191] |
| 2 | 20 | -0.0033 [-0.0202,+0.0141] | -0.0022 [-0.0066,+0.0022] | +0.0073 [-0.0030,+0.0188] | -0.0605 [-0.1309,+0.0078] |
| 2 | 30 | -0.0061 [-0.0138,+0.0011] | **-0.0029 [-0.0059,-0.0002]** | -0.0040 [-0.0221,+0.0125] | -0.0195 [-0.0957,+0.0566] |
| 4 | 5 | +0.0419 [-0.0181,+0.1020] | +0.0025 [-0.0114,+0.0162] | -0.0311 [-0.0725,+0.0084] | +0.0547 [-0.0332,+0.1445] |
| 4 | 10 | **+0.0892 [+0.0275,+0.1514]** | +0.0112 [-0.0005,+0.0235] | -0.0208 [-0.0492,+0.0070] | +0.0469 [-0.0352,+0.1289] |
| 4 | 20 | **+0.0846 [+0.0370,+0.1373]** | **+0.0153 [+0.0055,+0.0255]** | -0.0018 [-0.0186,+0.0150] | -0.0020 [-0.0605,+0.0586] |
| 4 | 30 | +0.0312 [-0.0043,+0.0738] | +0.0068 [-0.0014,+0.0160] | +0.0032 [-0.0147,+0.0197] | +0.0039 [-0.0508,+0.0625] |
| 8 | 5 | **+0.0560 [+0.0074,+0.1032]** | +0.0062 [-0.0059,+0.0181] | -0.0024 [-0.0389,+0.0339] | -0.0391 [-0.1016,+0.0234] |
| 8 | 10 | **+0.1231 [+0.0678,+0.1802]** | **+0.0124 [+0.0012,+0.0239]** | +0.0003 [-0.0288,+0.0301] | -0.0391 [-0.1035,+0.0234] |
| 8 | 20 | **+0.1217 [+0.0546,+0.1862]** | **+0.0130 [+0.0016,+0.0244]** | -0.0198 [-0.0468,+0.0073] | +0.0117 [-0.0645,+0.0820] |
| 8 | 30 | **+0.1628 [+0.1114,+0.2126]** | **+0.0244 [+0.0151,+0.0337]** | -0.0003 [-0.0260,+0.0273] | -0.0059 [-0.0840,+0.0703] |

### Replication result

The central v1 claim must be weakened.

At `d=8, q=20`, v1 suggested a very large D-optimal ranking benefit:

```text
v1 random top-K regret      0.1895
v1 D-opt top-K regret       0.0995
v1 mean difference         -0.0900
```

V2 gives:

```text
v2 random top-K regret      0.134062
v2 D-opt top-K regret       0.114273
v2 paired mean difference  -0.019789
95% paired bootstrap CI    [-0.04684, +0.00727]
D-opt lower regret in       41 / 64 scenarios approximately (64.1%)
```

The direction survives, but the magnitude collapses and the paired interval includes zero.

**Therefore v2 does not establish that plug-in D-optimal querying improves top-K ranking.**

This is precisely why the 12-seed v1 result was treated as provisional rather than promoted into the product.

## Stronger replicated result — plug-in D-optimal can harm global recovery

The more stable v2 result is negative: once dimension reaches 4–8, the current plug-in D-optimal policy often makes the inferred probability surface **worse** than random sampling.

Across the 12 `(d,q)` cells, D-optimal has a paired 95% interval showing:

```text
excess log loss significantly better than random    0 / 12 cells
excess log loss significantly worse than random     6 / 12 cells

probability MSE significantly better than random    1 / 12 cells
probability MSE significantly worse than random     4 / 12 cells

coefficient RMSE significantly better than random   0 / 12 cells
coefficient RMSE significantly worse than random    7 / 12 cells

top-K regret significantly better than random       0 / 12 cells
top-K regret significantly worse than random        0 / 12 cells
```

This rejects the idea that the current plug-in D-optimal score is a generally safe improvement over a random baseline.

## Boundary-only versus random

Boundary-only querying replicates as a clear failure for global model recovery.

Across all 12 `(d,q)` cells:

```text
excess log loss significantly better than random    0 / 12
excess log loss significantly worse than random    12 / 12

probability MSE significantly better than random    0 / 12
probability MSE significantly worse than random    11 / 12

coefficient RMSE significantly better than random   0 / 12
coefficient RMSE significantly worse than random   12 / 12
```

It also has significantly worse top-K regret in three later-budget cells (`d=4,q=20`, `d=4,q=30`, `d=8,q=30`) and never has a significant ranking advantage.

Thus the local fact

\[
p(1-p)\text{ is maximal at }p=0.5
\]

is **not** a sufficient acquisition policy. Boundary sampling ignores unresolved feature directions and can repeatedly collect locally ambiguous but globally redundant evidence.

## The likely D-optimal failure mechanism

The current policy uses plug-in MAP information:

\[
\mathcal I_q(\hat\alpha)
\]

with the posterior mean/MAP substituted into the Bernoulli Fisher weight.

At the broad zero-centered prior used here,

\[
\hat\alpha=0
\]

initially implies

\[
\hat p(x)=0.5
\]

for every candidate, regardless of feature magnitude.

The first D-optimal queries can therefore be dominated by geometric leverage: extreme feature vectors appear maximally informative because the plug-in model assigns them the maximal Bernoulli weight `p(1-p)=0.25`.

But under posterior uncertainty, an extreme candidate can have a very broad latent score and substantial probability mass in saturated logistic regions where the **true conditional Fisher weight is much smaller**.

This gives a concrete theoretical hypothesis:

> the current D-optimal policy is overconfident about information at high-leverage points because it evaluates Fisher information at a single uncertain MAP state rather than integrating over the posterior.

V2 does not yet prove this mechanism, but it makes it the strongest next hypothesis to test.

## Convergence result

Only two of 2304 fits failed the deliberately strict `converged=True` criterion:

```text
d=2, q=30, d_optimal, seed=6      iterations=6
d=4, q=30, boundary,  seed=42     iterations=17
```

Both still produced nonpathological predictive/ranking metrics. The earlier v1 D-optimal nonconvergence therefore was not a broad instability, but the convergence flag should remain visible rather than silently discarded.

## What v2 establishes

Under the exact synthetic assumptions tested:

1. boundary-only active sampling is clearly inferior to random sampling for recovering the full acceptance surface;
2. plug-in D-optimal design is **not** a generally superior replacement for random sampling;
3. v1's apparent large D-optimal top-K benefit at `d=8,q=20` was substantially inflated by the small 12-seed sample;
4. the objectives “learn the global probability surface” and “make the correct top-K decision” remain distinct;
5. none of the present active policies has yet demonstrated a reliable top-K advantage over random sampling; and
6. a fixed 20–30 pair budget still has no theoretical or empirical justification as a universal stopping point.

## What v2 does not establish

It still does not tell us:

- the dimensionality of human visual preference;
- whether the Gaussian synthetic feature distribution resembles a usable image-feature basis;
- whether willingness-to-meet synthetic candidates transfers to real profiles;
- whether pair responses are conditionally independent;
- whether a linear-logistic surface is adequate;
- whether D-optimal design fails for the hypothesized posterior-uncertainty reason; or
- which active query policy should be deployed.

## Next theoretical experiment

The next experiment should test the failure mechanism **before** introducing a ranking-specific acquisition objective.

Replace the plug-in Bernoulli Fisher weight

\[
\hat p(1-\hat p)
\]

with its posterior expectation.

For augmented candidate feature vector `z`, under the Laplace posterior

\[
\alpha\sim N(m,\Sigma),
\]

the latent score is

\[
s=\alpha^Tz\sim N(\mu_s,v_s),
\]

where

\[
\mu_s=m^Tz,
\qquad
v_s=z^T\Sigma z.
\]

Define the posterior-integrated local weight

\[
\bar w(z)
=E_{s\sim N(\mu_s,v_s)}[\sigma(s)(1-\sigma(s))].
\]

Then use

\[
\bar{\mathcal I}(z)=\bar w(z)zz^T
\]

inside the same determinant-gain framework.

This directly tests whether accounting for uncertainty prevents the current policy from overvaluing extreme/high-leverage candidates.

Only after that comparison should Mosaic introduce a ranking-aligned acquisition objective. If posterior-integrated information improves global recovery but still does not improve top-K decisions, that will be evidence that **objective alignment**, rather than merely uncertainty integration, is the remaining problem.
