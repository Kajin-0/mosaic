# S1 Exact Gaussian Ranking Benchmark v6a

## Status

Completed exploratory synthetic benchmark under the correctly specified `visual-acceptance-linear-logit-v1` model.

This is **hypothesis-generating only**: eight paired scenario seeds per cell. It is not human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

The principal result is mixed but decisive for branch direction: replacing the sampled 96-direction population reference bank with the exact Gaussian-reference ranking-risk functional removes one important approximation layer and improves ranking behavior in several cells, but it does **not** make ranking-directed acquisition universally superior. In particular, posterior-Fisher remains stronger at `d=8,q=20`. The next scientific question is therefore sample complexity / effective dimension rather than further acquisition-objective invention.

## Provenance

- benchmark version: `s1-exact-gaussian-ranking-benchmark-v6a`
- exact branch head executed: `309d5a67b07a8a7a653c52f39ca398c283259d61`
- GitHub Actions run: `31855573136`
- benchmark job: `94939580603`
- artifact ID: `9239008929`
- artifact ZIP SHA-256: `00c1135c2cacb173ab9daa2321f78952b977f984e16dec5a86688426abd0c509`
- uncompressed JSON SHA-256: `d5669773ff750b0d7f49f43f27b7b1519e53afddfdac33718e7af8f10104401e`
- raw simulation records: `240`
- numerical benchmark duration: approximately `445 s`

The one-use benchmark workflow had read-only repository permission and is removed after artifact capture.

## Scientific objective

V5a used a Monte Carlo reference bank of 96 future-candidate feature differences to approximate out-of-sample population ranking risk. Under the exact synthetic reference model

\[
X_a,X_b\overset{iid}{\sim}N(0,I),
\qquad
\delta=X_a-X_b\sim N(0,2I),
\]

that Monte Carlo layer can be eliminated.

For posterior slope state

\[
\beta\sim N(m,\Sigma_\beta),
\]

the expected wrong-order linear score regret over future candidate pairs is

\[
\boxed{
R_{\rm rank}(m,\Sigma_\beta)
=
\frac{E\|\beta\|-\|m\|}{\sqrt{\pi}}
}.
\]

This is a Jensen gap of the Euclidean norm. The acceptance intercept cancels exactly because future-candidate ordering depends only on score differences.

V6a evaluates the one-step expected reduction in this exact-reference risk under the same coherent linear-Bayes hypothetical response update used in v4/v5.

The remaining Gaussian expectation `E||beta||` is evaluated deterministically using a one-dimensional integral representation and a fixed 24-point Gauss-Legendre rule. Dedicated tests compare the implementation against isotropic closed forms and numerical references.

## Configuration

```text
feature dimensions         d = 2, 4, 8
pair-query budgets          q = 10, 20
scenario seeds              0..7
query candidate bank        18
sampled-reference diffs     96  (used only by v5a policy)
held-out candidates         96
top-K                       8
prior variance              4 per effective coefficient
slope scale                 0.9 / sqrt(d)
true intercept              0
response model              correctly specified linear-logistic Bernoulli acceptance
```

Five policies:

1. `random`
2. `posterior_fisher_d_optimal`
3. `mutual_information_d_optimal`
4. `population_score_regret` — v5a sampled-reference policy
5. `exact_gaussian_score_regret` — v6a exact-reference policy

Total runs:

\[
3\times2\times5\times8=240.
\]

All cells converged in all eight runs.

## Aggregate means

| d | q | policy | pairwise probability regret | ordering error | top-K regret | probability MSE | excess log loss |
|---:|---:|---|---:|---:|---:|---:|---:|
| 2 | 10 | random | 0.031878 | 0.237664 | 0.092049 | 0.043195 | 0.129199 |
| 2 | 10 | posterior-Fisher | 0.019371 | 0.211239 | 0.064531 | 0.022909 | 0.063844 |
| 2 | 10 | mutual information | 0.023231 | 0.242708 | 0.075557 | **0.020178** | **0.060837** |
| 2 | 10 | sampled population regret | **0.004860** | **0.071436** | **0.008450** | 0.022998 | 0.092358 |
| 2 | 10 | exact Gaussian regret | 0.005460 | 0.094737 | 0.014073 | 0.027148 | 0.111301 |
| 2 | 20 | random | 0.004343 | 0.093640 | **0.006537** | 0.016852 | 0.048675 |
| 2 | 20 | posterior-Fisher | 0.019932 | 0.218065 | 0.056528 | 0.015520 | 0.054173 |
| 2 | 20 | mutual information | 0.005937 | 0.104907 | 0.016742 | **0.013365** | **0.035799** |
| 2 | 20 | sampled population regret | **0.002674** | **0.062281** | 0.009163 | 0.016378 | 0.063125 |
| 2 | 20 | exact Gaussian regret | 0.002810 | 0.068723 | 0.009303 | 0.020183 | 0.068962 |
| 4 | 10 | random | 0.051231 | 0.300713 | 0.136554 | 0.059698 | 0.196686 |
| 4 | 10 | posterior-Fisher | 0.066602 | 0.351562 | 0.187392 | 0.074675 | 0.224607 |
| 4 | 10 | mutual information | 0.033269 | 0.257703 | 0.074882 | **0.048585** | **0.160763** |
| 4 | 10 | sampled population regret | 0.029310 | 0.219819 | 0.084199 | 0.046019 | 0.151218 |
| 4 | 10 | exact Gaussian regret | **0.020035** | **0.186404** | **0.063955** | 0.055707 | 0.230509 |
| 4 | 20 | random | 0.021815 | 0.190461 | 0.069694 | 0.019141 | 0.053206 |
| 4 | 20 | posterior-Fisher | 0.041188 | 0.265872 | 0.123838 | 0.030166 | 0.076190 |
| 4 | 20 | mutual information | 0.018327 | 0.183361 | 0.043161 | 0.025285 | 0.078172 |
| 4 | 20 | sampled population regret | **0.011587** | **0.133196** | **0.021749** | **0.017319** | **0.047019** |
| 4 | 20 | exact Gaussian regret | 0.013715 | 0.159293 | 0.042816 | 0.037190 | 0.169251 |
| 8 | 10 | random | 0.070495 | 0.412253 | 0.201074 | 0.119593 | 0.495577 |
| 8 | 10 | posterior-Fisher | 0.064401 | 0.389145 | 0.200684 | **0.103894** | **0.423958** |
| 8 | 10 | mutual information | 0.067906 | 0.404304 | **0.175042** | 0.126288 | 0.572293 |
| 8 | 10 | sampled population regret | 0.070580 | 0.415214 | 0.175492 | 0.122715 | 0.538372 |
| 8 | 10 | exact Gaussian regret | **0.064260** | **0.380948** | 0.184167 | 0.121063 | 0.587149 |
| 8 | 20 | random | 0.072362 | 0.439172 | 0.228831 | 0.106641 | 0.409442 |
| 8 | 20 | **posterior-Fisher** | **0.039143** | **0.294435** | **0.107240** | **0.052239** | **0.155778** |
| 8 | 20 | mutual information | 0.046940 | 0.317982 | 0.133288 | 0.072628 | 0.263987 |
| 8 | 20 | sampled population regret | 0.047438 | 0.335718 | 0.142733 | 0.058950 | 0.188509 |
| 8 | 20 | exact Gaussian regret | 0.044149 | 0.303810 | 0.128700 | 0.069779 | 0.275584 |

## Result 1 — exact reference removes reference-bank noise, but not the policy tradeoff

The exact-reference policy is very close to the sampled-reference policy in `d=2`, confirming that the 96-direction approximation was already adequate in the easiest regime.

At `d=4,q=10`, removing the sampled reference bank improves mean ranking strongly:

```text
sampled population pairwise regret  0.029310
exact Gaussian pairwise regret      0.020035

sampled population top-K regret     0.084199
exact Gaussian top-K regret         0.063955
```

At `d=8,q=20`, the exact policy also improves on the sampled-reference policy:

```text
pairwise regret  0.047438 -> 0.044149
top-K regret     0.142733 -> 0.128700
ordering error   0.335718 -> 0.303810
```

Paired across the eight scenarios, exact Gaussian regret beats sampled population regret in `6/8` seeds on pairwise probability regret and `5/8` on top-K regret at `d=8,q=20`.

Therefore v5a's finite reference bank was a real source of policy variance, especially in the harder regime.

## Result 2 — the high-dimensional posterior-Fisher counterexample survives

Removing reference-bank Monte Carlo does **not** make exact ranking acquisition dominate posterior-Fisher at `d=8,q=20`.

Means:

```text
posterior-Fisher pairwise regret    0.039143
exact Gaussian pairwise regret      0.044149

posterior-Fisher top-K regret       0.107240
exact Gaussian top-K regret         0.128700
```

Paired scenarios:

```text
exact vs posterior-Fisher
pairwise-regret wins   3/8
top-K-regret wins      4/8
```

The mean and paired direction therefore both fail to support a claim that exact ranking acquisition is superior in this regime.

This is the key branch result. The `d=8,q=20` limitation cannot now be explained away as an arbitrary 96-direction reference-bank artifact.

## Result 3 — exact ranking can improve ranking while degrading probability calibration

The exact policy optimizes an ordering loss, not global probability fit. V6a shows that distinction clearly.

For example, at `d=4,q=10`, exact Gaussian regret gives the best mean pairwise and top-K ranking metrics in the cell, while its excess log loss (`0.230509`) is worse than random (`0.196686`), sampled population regret (`0.151218`), and mutual information (`0.160763`).

At `d=8,q=10`, exact ranking has the best mean pairwise probability regret (`0.064260`) but the worst mean excess log loss (`0.587149`).

Thus a query policy can learn enough directional geometry to improve ordering while remaining poorly calibrated in absolute acceptance probability. These are distinct scientific objectives and should remain separately measured.

## Result 4 — exact ranking still beats random substantially once enough high-dimensional observations accumulate

At `d=8,q=20`, exact Gaussian regret beats random in:

```text
pairwise probability regret  6/8 seeds
top-K regret                 6/8 seeds
probability MSE              5/8 seeds
excess log loss              5/8 seeds
```

Mean top-K regret falls from `0.228831` to `0.128700`.

So the exact ranking objective is not intrinsically broken at high dimension. The unresolved issue is whether it needs a different observation budget than posterior-Fisher to identify the relevant slope directions reliably.

## What v6a establishes

Under the exact synthetic assumptions tested:

1. the exact Gaussian-reference identity is computationally usable in active acquisition without a sampled future-candidate reference bank;
2. sampled-reference variance materially affected v5a in some moderate/high-dimensional cells;
3. removing that variance improves the ranking-directed policy but does not eliminate the `d=8,q=20` posterior-Fisher advantage;
4. ranking quality and global acceptance-probability calibration can diverge strongly under a ranking-specific acquisition objective;
5. the high-dimensional limitation is now better framed as a **sample-complexity / effective-dimension problem** than as an acquisition-reference approximation problem; and
6. no policy is ready for product use and no universal query budget is established.

## What v6a does not establish

V6a does not establish:

- that posterior-Fisher is universally optimal at high dimension;
- the query budget at which exact ranking acquisition catches or surpasses posterior-Fisher;
- the effective dimensionality of real attraction preference;
- whether sparse or low-rank preference structure changes the sample-complexity curve;
- whether the linear-logistic model is adequate for real users;
- transfer from synthetic acceptance judgments to real profile choices or dates; or
- any relationship-quality prediction claim.

## Next experiment — sample complexity / effective dimension

Stop changing the acquisition objective for the next experiment.

The next branch should map ranking error against **dimension and observation budget** using fixed policies, especially:

- posterior-Fisher;
- exact Gaussian ranking regret;
- mutual information; and
- random as a passive reference.

The scientific variables should be expressed in dimension-normalized form as well as raw pair-query count. A useful first axis is binary observations per effective coefficient,

\[
\kappa=\frac{2q}{d+1},
\]

because each pair query currently yields two provisional binary acceptability observations and the fitted state has `d+1` effective coefficients including the intercept.

The next study should determine whether the apparent high-dimensional policy reversal collapses when plotted against `kappa`, or whether dimension has an additional effect even at matched observations per coefficient.

Recommended exploratory grid:

```text
d = 2, 4, 8, 12
kappa targets approximately = 2, 4, 6, 8, 12
```

Convert each target to a feasible integer pair-query budget

\[
q\approx\frac{\kappa(d+1)}{2},
\]

subject to the finite candidate-pair pool.

Primary outcomes:

- held-out pairwise probability regret;
- ordering error;
- top-K regret;
- probability MSE;
- excess log loss;
- posterior interval coverage; and
- posterior directional uncertainty.

If ranking curves approximately collapse by `kappa`, Mosaic has evidence for a useful sample-complexity scaling law under the S1 synthetic model. If they do not, the next explanation to test is **preference structure** (sparsity/low rank/non-isotropic priors), not another acquisition-score heuristic.
