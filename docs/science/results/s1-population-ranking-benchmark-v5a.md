# S1 Population-Ranking Benchmark v5a

## Status

Completed exploratory synthetic benchmark under the correctly specified `visual-acceptance-linear-logit-v1` model.

This is **hypothesis-generating only**: eight paired scenario seeds per cell. It is not human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

The principal result is mixed but scientifically useful: population score-regret acquisition produces broad low/moderate-dimensional ranking gains and fixes much of finite-pool EVSI's failure, but it is **not** a universal winner at `d=8`.

## Provenance

- benchmark version: `s1-population-ranking-benchmark-v5a`
- exact branch head executed: `704ded00481f998b45325a878d6470fe276f1dc7`
- GitHub Actions run: `31852142282`
- benchmark job: `94929754869`
- artifact ID: `9237981075`
- artifact ZIP SHA-256: `2ccb4f09e0c79c8eab3e7d0f267ab4cad676e7ad16f32ed2140f23aa8464b18c`
- uncompressed JSON SHA-256: `4d328e5e96aa2e91625bfca77206445a348c4d1b76571905b4225dbfbb78d400`
- raw simulation records: `240`
- numerical benchmark duration: approximately `548 s`

The one-use benchmark workflow had read-only repository permission and was removed after artifact capture.

## Scientific objective

V4a optimized top-K value on one finite 32-candidate decision bank. That could be useful for a current-pool allocation problem, but S1 is currently asking a different question: can the learned preference state rank **future** candidates from a reference population?

V5a therefore defines pairwise future-candidate score difference

\[
\Delta s=\alpha^T\delta z
\sim N(\mu_\Delta,\sigma_\Delta^2),
\]

under the Gaussian/Laplace posterior. The probability that the current mean ordering is wrong is

\[
\Phi\!\left(-\frac{|\mu_\Delta|}{\sigma_\Delta}\right),
\]

but this treats an inconsequential near-zero tie like a consequential uncertain ordering. The primary acquisition loss is therefore expected wrong-order **linear score regret**

\[
\rho(\mu,\sigma)
=
\sigma\phi\!\left(\frac{|\mu|}{\sigma}\right)
-|\mu|\Phi\!\left(-\frac{|\mu|}{\sigma}\right).
\]

V5a approximates population ranking risk by averaging this loss over 96 independently generated reference feature-difference vectors and chooses the query pair with maximum expected reduction in that risk under the coherent v4 linear-Bayes hypothetical update.

## Configuration

```text
feature dimensions         d = 2, 4, 8
pair-query budgets          q = 10, 20
scenario seeds              0..7
query candidate bank        18
finite EVSI decision bank   32
population reference diffs  96
held-out candidates         96
top-K                       8
prior variance              4 per effective coefficient
slope scale                 0.9 / sqrt(d)
true intercept              0
```

Five policies:

1. `random`
2. `posterior_fisher_d_optimal`
3. `mutual_information_d_optimal`
4. `expected_top_k_evsi`
5. `population_score_regret`

For the correctly specified synthetic candidate distribution,

\[
X_a,X_b\overset{iid}{\sim}N(0,I)
\quad\Rightarrow\quad
\Delta X=X_a-X_b\sim N(0,2I),
\]

so the 96 population reference differences were sampled independently from `Normal(0, 2 I)`. Query, finite-decision, population-reference, and held-out banks use disjoint deterministic seed streams.

## Aggregate means

| d | q | policy | pairwise probability regret | ordering error | top-K regret | probability MSE | excess log loss |
|---:|---:|---|---:|---:|---:|---:|---:|
| 2 | 10 | random | 0.031878 | 0.237664 | 0.092049 | 0.043195 | 0.129199 |
| 2 | 10 | posterior-Fisher | 0.019371 | 0.211239 | 0.064531 | 0.022909 | 0.063844 |
| 2 | 10 | mutual information | 0.023231 | 0.242708 | 0.075557 | **0.020178** | **0.060837** |
| 2 | 10 | finite-pool EVSI | 0.008713 | 0.121793 | 0.019987 | 0.022639 | 0.087427 |
| 2 | 10 | **population score regret** | **0.004860** | **0.071436** | **0.008450** | 0.022998 | 0.092358 |
| 2 | 20 | random | 0.004343 | 0.093640 | **0.006537** | 0.016852 | 0.048675 |
| 2 | 20 | posterior-Fisher | 0.019932 | 0.218065 | 0.056528 | 0.015520 | 0.054173 |
| 2 | 20 | mutual information | 0.005937 | 0.104907 | 0.016742 | **0.013365** | **0.035799** |
| 2 | 20 | finite-pool EVSI | 0.005064 | 0.085992 | 0.007257 | 0.014043 | 0.043231 |
| 2 | 20 | **population score regret** | **0.002674** | **0.062281** | 0.009163 | 0.016378 | 0.063125 |
| 4 | 10 | random | 0.051231 | 0.300713 | 0.136554 | 0.059698 | 0.196686 |
| 4 | 10 | posterior-Fisher | 0.066602 | 0.351562 | 0.187392 | 0.074675 | 0.224607 |
| 4 | 10 | mutual information | 0.033269 | 0.257703 | **0.074882** | 0.048585 | 0.160763 |
| 4 | 10 | finite-pool EVSI | 0.034317 | 0.247259 | 0.097832 | 0.055579 | 0.208661 |
| 4 | 10 | **population score regret** | **0.029310** | **0.219819** | 0.084199 | **0.046019** | **0.151218** |
| 4 | 20 | random | 0.021815 | 0.190461 | 0.069694 | 0.019141 | 0.053206 |
| 4 | 20 | posterior-Fisher | 0.041188 | 0.265872 | 0.123838 | 0.030166 | 0.076190 |
| 4 | 20 | mutual information | 0.018327 | 0.183361 | 0.043161 | 0.025285 | 0.078172 |
| 4 | 20 | finite-pool EVSI | 0.020696 | 0.191694 | 0.061483 | 0.030382 | 0.097915 |
| 4 | 20 | **population score regret** | **0.011587** | **0.133196** | **0.021749** | **0.017319** | **0.047019** |
| 8 | 10 | random | 0.070495 | 0.412253 | 0.201074 | 0.119593 | 0.495577 |
| 8 | 10 | **posterior-Fisher** | **0.064401** | **0.389145** | 0.200684 | **0.103894** | **0.423958** |
| 8 | 10 | mutual information | 0.067906 | 0.404304 | **0.175042** | 0.126288 | 0.572293 |
| 8 | 10 | finite-pool EVSI | 0.087930 | 0.482374 | 0.250186 | 0.127787 | 0.499435 |
| 8 | 10 | population score regret | 0.070580 | 0.415214 | 0.175492 | 0.122715 | 0.538372 |
| 8 | 20 | random | 0.072362 | 0.439172 | 0.228831 | 0.106641 | 0.409442 |
| 8 | 20 | **posterior-Fisher** | **0.039143** | **0.294435** | **0.107240** | **0.052239** | **0.155778** |
| 8 | 20 | mutual information | 0.046940 | 0.317982 | 0.133288 | 0.072628 | 0.263987 |
| 8 | 20 | finite-pool EVSI | 0.079541 | 0.428043 | 0.217218 | 0.093300 | 0.304075 |
| 8 | 20 | population score regret | 0.047438 | 0.335718 | 0.142733 | 0.058950 | 0.188509 |

All cells converged in all eight runs.

## Paired descriptive analysis

Because `n=8` per cell is exploratory, the correct interpretation is paired direction and heterogeneity, not significance testing.

### Population score regret versus random

For held-out pairwise probability regret / top-K regret:

```text
d=2 q=10   7/8 wins   / 7/8 wins
d=2 q=20   5/8 wins   / 5/8 wins (+1 top-K tie)
d=4 q=10   6/8 wins   / 5/8 wins
d=4 q=20   5/8 wins   / 5/8 wins
d=8 q=10   4/8 wins   / 3/8 wins
d=8 q=20   8/8 wins   / 7/8 wins
```

The `d=2,q=10` result is particularly broad rather than purely mean-driven: median paired deltas are `-0.00997` in pairwise probability regret and `-0.02684` in top-K regret.

At `d=8,q=20`, the population policy also beats random broadly and improves probability MSE in `7/8` seeds. Therefore the policy is not simply failing at high dimension; the harder question is whether it beats the stronger information-oriented baseline.

### Population score regret versus posterior-Fisher

For held-out pairwise probability regret / top-K regret:

```text
d=2 q=10   6/8 wins / 4/8 wins (+2 ties)
d=2 q=20   6/8 wins / 5/8 wins
d=4 q=10   4/8 wins / 4/8 wins
d=4 q=20   6/8 wins / 7/8 wins
d=8 q=10   4/8 wins / 4/8 wins
d=8 q=20   3/8 wins / 1/8 wins
```

The strongest cross-metric population result is `d=4,q=20`: relative to posterior-Fisher, population ranking lowers mean pairwise regret by `0.02960`, mean top-K regret by `0.10209`, probability MSE by `0.01285`, and excess log loss by `0.02917`; it wins `6/8`, `7/8`, `6/8`, and `6/8` paired seeds respectively.

The high-dimensional limitation is also broad: at `d=8,q=20`, posterior-Fisher beats population ranking in `5/8` seeds on pairwise probability regret and `7/8` on top-K regret. This is not a single outlier artifact.

### Population score regret versus mutual information

The comparison is more mixed:

- `d=2,q=10`: population wins pairwise regret `6/8` and top-K regret `6/8` (+1 tie).
- `d=2,q=20`: `5/8` pairwise-regret wins, but top-K is effectively mixed.
- `d=4,q=10`: `4/8` pairwise-regret wins and `3/8` top-K wins.
- `d=4,q=20`: mean population metrics are better, but paired ranking wins are only `4/8` for each ranking metric; calibration is more favorable (`5/8` probability-MSE wins, `6/8` excess-log-loss wins).
- `d=8,q=10`: essentially unresolved.
- `d=8,q=20`: mutual information has better mean ranking, while population has better probability MSE and excess log loss in the majority of seeds.

Thus v5a does **not** establish population ranking as superior to every posterior-aware information policy.

### Population score regret versus finite-pool EVSI

Population ranking fixes much of the finite-bank pathology:

- at `d=2,q=10`, it wins pairwise regret `6/8` and top-K regret `5/8` (+2 ties);
- at `d=8,q=10`, it wins top-K regret **8/8**;
- at `d=8,q=20`, it wins pairwise regret `7/8` and top-K regret `5/8`.

This supports the v4a diagnosis that conditioning acquisition on one finite 32-candidate pool was an important scope mismatch for the S1 future-ranking objective.

## Acquisition-score diagnostics

Across 48 population-score-regret runs:

- 44 runs had no selected negative acquisition score;
- one run (`d=2,q=20,seed=6`) contained four very small negative selected scores;
- the minimum was approximately `-2.54497e-06`;
- mean selected population-regret reduction across all runs was approximately `0.172589`.

Exact Bayesian value of information cannot be negative. These values are therefore retained as approximation diagnostics. Their scale is negligible relative to the early selected scores, whose maxima are approximately `0.95–1.22` in this benchmark.

## What v5a establishes

Under the exact synthetic assumptions tested:

1. population-distribution ranking loss is a materially better decision scope for S1 than one finite candidate-bank top-K objective;
2. the population policy's gains in `d=2,q=10`, `d=4,q=20`, and versus finite EVSI are not explained solely by one extreme scenario;
3. ranking-directed acquisition can coexist with good probability calibration in some cells rather than necessarily trading it away;
4. `d=8,q=20` remains a genuine counterexample to a universal population-ranking policy claim because posterior-Fisher is broadly better there; and
5. eight seeds are insufficient to promote any policy to product use or to establish universal query-count recommendations.

## New exact simplification of the Gaussian reference problem

V5a used 96 Monte Carlo reference differences. For the exact synthetic reference distribution used here, that Monte Carlo layer can be removed analytically.

Let future candidates satisfy

\[
X_a,X_b\overset{iid}{\sim}N(0,I),
\qquad
\delta=X_a-X_b\sim N(0,2I).
\]

For a fixed posterior-mean slope vector `m` and a fixed possible true slope vector `beta`, define

\[
U=m^T\delta,
\qquad
V=\beta^T\delta.
\]

`U,V` are zero-mean bivariate Gaussian with correlation

\[
\rho=\frac{m^T\beta}{\|m\|\,\|\beta\|}.
\]

The expected wrong-order linear score loss over future candidate pairs has the exact form

\[
E_\delta[|V|1\{UV<0\}]
=
\frac{\|\beta\|}{\sqrt{\pi}}(1-\rho).
\]

Now average over the Gaussian slope posterior

\[
\beta\sim N(m,\Sigma_\beta).
\]

Because `E[beta]=m`, the angular term collapses:

\[
\boxed{
R_{\rm rank}(m,\Sigma_\beta)
=
\frac{E\|\beta\|-\|m\|}{\sqrt{\pi}}
}
\]

with the same continuous result at `m=0`.

Direct Monte Carlo checks in `d=2,4,8` agree with this identity to sampling error.

This is a stronger result than the original v5a Monte Carlo policy. Under the Gaussian reference model, population ranking risk is a scaled **Jensen gap of the slope-vector norm**. Intercept uncertainty cancels exactly, and the arbitrary 96-direction reference bank is unnecessary.

## Next experiment

Do **not** immediately scale the 96-direction v5a implementation to 64 seeds.

The next branch should implement the exact Gaussian-reference identity

\[
R_{\rm rank}
=
\frac{E\|\beta\|-\|m\|}{\sqrt{\pi}}
\]

and use it as the population acquisition risk. The only remaining numerical expectation is over the Gaussian slope posterior itself, not over an arbitrary sampled future-candidate bank.

That expectation should be approximated by a deterministic low-cost Gaussian rule and validated against high-accuracy Monte Carlo / reference integration. Then benchmark the exact-reference acquisition against:

- random;
- posterior-Fisher;
- mutual information; and
- the v5a 96-direction population approximation.

If the exact-reference policy preserves the low/moderate-dimensional signal and reduces reference-bank variance, a larger replication becomes justified. If it still loses broadly to posterior-Fisher at `d=8,q=20`, the next scientific question is then **sample complexity / effective dimension**, not acquisition-objective design.
