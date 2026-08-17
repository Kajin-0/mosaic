# S1 Sample-Complexity Benchmark v7a — κ Is Not Sufficient Under a Fixed Random Query Bank

## Status

Completed exploratory synthetic benchmark under the correctly specified `visual-acceptance-linear-logit-v1` model.

This result is **screening evidence only**: four paired scenario seeds per cell. It is not human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

The principal result is negative but clarifying: normalizing pair-query budget by the number of fitted coefficients,

\[
\kappa=\frac{2q}{d+1},
\]

does **not** collapse held-out ranking performance across dimensions in the v7a design. However, v7a also reveals that the fixed 18-candidate random query bank becomes progressively ill-conditioned as dimension rises. Therefore the non-collapse cannot yet be attributed purely to intrinsic preference-dimensionality sample complexity.

The next experiment should hold query-bank information geometry approximately constant across dimensions before introducing sparse/low-rank preference structure.

## Provenance

- benchmark version: `s1-sample-complexity-benchmark-v7a`
- exact branch head executed: `2e854dd76743d0ff6cd5f9f75bc04b549c0e5ab9`
- GitHub Actions run: `31856320953`
- benchmark job: `94941657593`
- artifact ID: `9239312495`
- artifact ZIP SHA-256: `0d355c9b2fd894f48afbd6c8f6a472e8ccb746a5eb048c1184d32d3850b354df`
- uncompressed JSON SHA-256: `23886410dab0cdc8d7dc4ec39a8ea654890ddcf6f0234d8f6c6902ff123b3af0`
- raw simulation records: `240`
- numerical benchmark duration: approximately `790 s`

The benchmark workflow had read-only repository permission. It is one-use scientific infrastructure and should be removed after this result is recorded.

## Scientific objective

V6a showed that exact Gaussian-reference ranking acquisition can improve ranking, but posterior-Fisher remained stronger at `d=8,q=20`. The open question became whether this policy reversal was mainly a raw sample-complexity effect.

Each pair query is provisionally represented as two binary acceptability observations and the fitted linear-logistic state has `d+1` effective coefficients, including the intercept. V7a therefore compares dimensions at matched

\[
\kappa=\frac{\text{binary observations}}{\text{effective coefficients}}=\frac{2q}{d+1}.
\]

If ranking curves approximately collapsed by `κ`, then observations per coefficient would be a useful first-order scaling law. If they did not, some additional dimension-dependent quantity would be required.

## Configuration

```text
feature dimensions       d = 2, 4, 8, 12
κ targets                 2, 4, 6, 8, 12
scenario seeds            0..3
query candidate bank      18 iid Gaussian feature vectors
held-out candidate bank   96 iid Gaussian feature vectors
top-K                     8
prior variance            4 per effective coefficient
slope scale               0.9 / sqrt(d) per true coefficient
true intercept            0
response model            correctly specified linear-logistic Bernoulli acceptance
```

Policies:

1. `random`
2. `posterior_fisher_d_optimal`
3. `exact_gaussian_score_regret`

The target-to-query mapping is exact for the chosen dimensions:

| d | parameters d+1 | q at κ=2 | q at κ=4 | q at κ=6 | q at κ=8 | q at κ=12 |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 3 | 3 | 6 | 9 | 12 | 18 |
| 4 | 5 | 5 | 10 | 15 | 20 | 30 |
| 8 | 9 | 9 | 18 | 27 | 36 | 54 |
| 12 | 13 | 13 | 26 | 39 | 52 | 78 |

## Aggregate means

| d | κ | q | policy | pairwise probability regret | ordering error | top-K regret | probability MSE | excess log loss | slope cosine | slope SNR | convergence |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 3 | exact Gaussian regret | 0.003052 | 0.050822 | 0.007142 | 0.057600 | 0.176676 | 0.972967 | 1.087087 | 1.000000 |
| 2 | 2 | 3 | posterior-Fisher | 0.016977 | 0.149068 | 0.062044 | 0.045533 | 0.127365 | 0.856311 | 1.098745 | 1.000000 |
| 2 | 2 | 3 | random | 0.026126 | 0.177029 | 0.080645 | 0.032291 | 0.103297 | 0.731387 | 0.820014 | 1.000000 |
| 2 | 4 | 6 | exact Gaussian regret | 0.002437 | 0.058882 | 0.004920 | 0.023237 | 0.082441 | 0.979028 | 1.535814 | 1.000000 |
| 2 | 4 | 6 | posterior-Fisher | 0.005219 | 0.075658 | 0.017142 | 0.025498 | 0.075160 | 0.963402 | 1.558739 | 1.000000 |
| 2 | 4 | 6 | random | 0.020567 | 0.145340 | 0.071018 | 0.026822 | 0.094366 | 0.741812 | 1.294812 | 1.000000 |
| 2 | 6 | 9 | exact Gaussian regret | 0.001492 | 0.043586 | 0.001843 | 0.021286 | 0.070034 | 0.988949 | 1.926850 | 1.000000 |
| 2 | 6 | 9 | posterior-Fisher | 0.002423 | 0.056908 | 0.002379 | 0.012051 | 0.037535 | 0.981709 | 2.024987 | 1.000000 |
| 2 | 6 | 9 | random | 0.017979 | 0.150055 | 0.062077 | 0.025426 | 0.084498 | 0.807427 | 1.312020 | 1.000000 |
| 2 | 8 | 12 | exact Gaussian regret | 0.004885 | 0.074561 | 0.021179 | 0.010996 | 0.029348 | 0.968796 | 2.020444 | 1.000000 |
| 2 | 8 | 12 | posterior-Fisher | 0.002040 | 0.042599 | 0.002429 | 0.008692 | 0.023525 | 0.986061 | 2.316840 | 1.000000 |
| 2 | 8 | 12 | random | 0.032952 | 0.170504 | 0.087226 | 0.028076 | 0.099803 | 0.774216 | 1.448317 | 1.000000 |
| 2 | 12 | 18 | exact Gaussian regret | 0.006078 | 0.069956 | 0.021590 | 0.014323 | 0.042044 | 0.962026 | 2.189485 | 1.000000 |
| 2 | 12 | 18 | posterior-Fisher | 0.003180 | 0.058936 | 0.003735 | 0.008846 | 0.023364 | 0.976933 | 2.562235 | 1.000000 |
| 2 | 12 | 18 | random | 0.017848 | 0.133388 | 0.017039 | 0.020303 | 0.064240 | 0.890209 | 1.501291 | 1.000000 |
| 4 | 2 | 5 | exact Gaussian regret | 0.075410 | 0.421875 | 0.226610 | 0.129691 | 0.436943 | 0.198774 | 1.217542 | 1.000000 |
| 4 | 2 | 5 | posterior-Fisher | 0.098468 | 0.520779 | 0.251507 | 0.157631 | 0.488812 | -0.038164 | 1.063321 | 1.000000 |
| 4 | 2 | 5 | random | 0.059634 | 0.396382 | 0.177204 | 0.111065 | 0.373586 | 0.319398 | 0.869894 | 1.000000 |
| 4 | 4 | 10 | exact Gaussian regret | 0.057312 | 0.368969 | 0.157836 | 0.074607 | 0.253143 | 0.332740 | 1.144669 | 1.000000 |
| 4 | 4 | 10 | posterior-Fisher | 0.070435 | 0.440241 | 0.226312 | 0.051571 | 0.181407 | 0.190282 | 0.735462 | 1.000000 |
| 4 | 4 | 10 | random | 0.025181 | 0.235581 | 0.081202 | 0.040236 | 0.128630 | 0.715508 | 0.912612 | 1.000000 |
| 4 | 6 | 15 | exact Gaussian regret | 0.036584 | 0.279331 | 0.119029 | 0.054156 | 0.172399 | 0.580653 | 1.308949 | 1.000000 |
| 4 | 6 | 15 | posterior-Fisher | 0.056094 | 0.382730 | 0.199302 | 0.043137 | 0.138056 | 0.321378 | 0.940768 | 1.000000 |
| 4 | 6 | 15 | random | 0.025038 | 0.241831 | 0.065106 | 0.044288 | 0.139898 | 0.687387 | 1.339404 | 1.000000 |
| 4 | 8 | 20 | exact Gaussian regret | 0.035404 | 0.278070 | 0.111185 | 0.048800 | 0.155706 | 0.596658 | 1.468446 | 1.000000 |
| 4 | 8 | 20 | posterior-Fisher | 0.045793 | 0.319134 | 0.151519 | 0.036668 | 0.112820 | 0.478699 | 1.146357 | 1.000000 |
| 4 | 8 | 20 | random | 0.019309 | 0.202467 | 0.038388 | 0.027249 | 0.085591 | 0.766856 | 1.284212 | 1.000000 |
| 4 | 12 | 30 | exact Gaussian regret | 0.024039 | 0.222917 | 0.071931 | 0.033898 | 0.105548 | 0.723426 | 1.702987 | 1.000000 |
| 4 | 12 | 30 | posterior-Fisher | 0.018349 | 0.189254 | 0.050936 | 0.013728 | 0.038177 | 0.777111 | 1.267613 | 1.000000 |
| 4 | 12 | 30 | random | 0.006807 | 0.117599 | 0.014822 | 0.012332 | 0.035016 | 0.891832 | 1.362682 | 1.000000 |
| 8 | 2 | 9 | exact Gaussian regret | 0.031771 | 0.232456 | 0.071884 | 0.075668 | 0.260317 | 0.742365 | 1.076228 | 1.000000 |
| 8 | 2 | 9 | posterior-Fisher | 0.062772 | 0.335307 | 0.173601 | 0.105564 | 0.349834 | 0.533241 | 1.050355 | 1.000000 |
| 8 | 2 | 9 | random | 0.060364 | 0.320998 | 0.130791 | 0.097590 | 0.332023 | 0.541122 | 0.880412 | 1.000000 |
| 8 | 4 | 18 | exact Gaussian regret | 0.053242 | 0.304715 | 0.143320 | 0.091352 | 0.329386 | 0.512523 | 1.311037 | 1.000000 |
| 8 | 4 | 18 | posterior-Fisher | 0.042194 | 0.274890 | 0.080939 | 0.072603 | 0.249911 | 0.679267 | 1.191738 | 1.000000 |
| 8 | 4 | 18 | random | 0.051479 | 0.295011 | 0.114749 | 0.071104 | 0.247710 | 0.541855 | 1.137411 | 1.000000 |
| 8 | 6 | 27 | exact Gaussian regret | 0.052566 | 0.302083 | 0.145082 | 0.070367 | 0.256351 | 0.528364 | 1.471339 | 1.000000 |
| 8 | 6 | 27 | posterior-Fisher | 0.035928 | 0.252138 | 0.097030 | 0.051289 | 0.175020 | 0.689142 | 1.206926 | 1.000000 |
| 8 | 6 | 27 | random | 0.040221 | 0.253673 | 0.112032 | 0.048761 | 0.162937 | 0.655658 | 1.167044 | 1.000000 |
| 8 | 8 | 36 | exact Gaussian regret | 0.042572 | 0.268037 | 0.132258 | 0.056679 | 0.197401 | 0.617950 | 1.498062 | 1.000000 |
| 8 | 8 | 36 | posterior-Fisher | 0.030010 | 0.228235 | 0.059769 | 0.043084 | 0.145212 | 0.753347 | 1.425008 | 1.000000 |
| 8 | 8 | 36 | random | 0.031233 | 0.203783 | 0.095537 | 0.036326 | 0.119840 | 0.725026 | 1.208616 | 1.000000 |
| 8 | 12 | 54 | exact Gaussian regret | 0.045126 | 0.274836 | 0.125013 | 0.053672 | 0.183150 | 0.582679 | 1.778877 | 1.000000 |
| 8 | 12 | 54 | posterior-Fisher | 0.022856 | 0.194353 | 0.060060 | 0.033953 | 0.111477 | 0.801730 | 1.586650 | 1.000000 |
| 8 | 12 | 54 | random | 0.026554 | 0.182730 | 0.082446 | 0.033127 | 0.109146 | 0.768985 | 1.481328 | 1.000000 |
| 12 | 2 | 13 | exact Gaussian regret | 0.060767 | 0.370614 | 0.149950 | 0.114423 | 0.408983 | 0.439214 | 1.057346 | 1.000000 |
| 12 | 2 | 13 | posterior-Fisher | 0.043466 | 0.303673 | 0.126754 | 0.106386 | 0.371000 | 0.555368 | 0.980883 | 1.000000 |
| 12 | 2 | 13 | random | 0.055115 | 0.348026 | 0.205922 | 0.099755 | 0.341454 | 0.427515 | 0.686196 | 1.000000 |
| 12 | 4 | 26 | exact Gaussian regret | 0.041491 | 0.302741 | 0.090076 | 0.077223 | 0.286442 | 0.621034 | 1.105664 | 1.000000 |
| 12 | 4 | 26 | posterior-Fisher | 0.057742 | 0.354934 | 0.165069 | 0.093632 | 0.326719 | 0.468931 | 1.009903 | 1.000000 |
| 12 | 4 | 26 | random | 0.068800 | 0.392105 | 0.202055 | 0.117030 | 0.422241 | 0.376202 | 0.967368 | 1.000000 |
| 12 | 6 | 39 | exact Gaussian regret | 0.034627 | 0.277632 | 0.054677 | 0.081555 | 0.308814 | 0.672022 | 1.492256 | 1.000000 |
| 12 | 6 | 39 | posterior-Fisher | 0.053806 | 0.329331 | 0.183797 | 0.073538 | 0.267113 | 0.478616 | 1.010365 | 1.000000 |
| 12 | 6 | 39 | random | 0.064807 | 0.375329 | 0.159535 | 0.075468 | 0.265124 | 0.435813 | 0.981559 | 1.000000 |
| 12 | 8 | 52 | exact Gaussian regret | 0.030709 | 0.256908 | 0.085956 | 0.055643 | 0.212116 | 0.685980 | 1.424092 | 1.000000 |
| 12 | 8 | 52 | posterior-Fisher | 0.062705 | 0.366667 | 0.190949 | 0.066629 | 0.236389 | 0.413058 | 0.954194 | 0.750000 |
| 12 | 8 | 52 | random | 0.048396 | 0.320614 | 0.106662 | 0.051022 | 0.179491 | 0.586850 | 1.010087 | 0.750000 |
| 12 | 12 | 78 | exact Gaussian regret | 0.025893 | 0.236020 | 0.084135 | 0.039627 | 0.145698 | 0.730936 | 1.536513 | 1.000000 |
| 12 | 12 | 78 | posterior-Fisher | 0.054263 | 0.328893 | 0.176057 | 0.057381 | 0.209747 | 0.489099 | 1.125034 | 1.000000 |
| 12 | 12 | 78 | random | 0.039134 | 0.282511 | 0.060422 | 0.034099 | 0.119191 | 0.668279 | 1.090871 | 1.000000 |

## Result 1 — κ does not collapse the ranking curves

At fixed `κ`, held-out ranking error still varies strongly with dimension.

For example, at `κ=4`, mean top-K regret is:

```text
random                  d=2: 0.071018   d=4: 0.081202   d=8: 0.114749   d=12: 0.202055
posterior-Fisher        d=2: 0.017142   d=4: 0.226312   d=8: 0.080939   d=12: 0.165069
exact Gaussian regret   d=2: 0.004920   d=4: 0.157836   d=8: 0.143320   d=12: 0.090076
```

At `κ=12`, the separation remains:

```text
random                  d=2: 0.017039   d=4: 0.014822   d=8: 0.082446   d=12: 0.060422
posterior-Fisher        d=2: 0.003735   d=4: 0.050936   d=8: 0.060060   d=12: 0.176057
exact Gaussian regret   d=2: 0.021590   d=4: 0.071931   d=8: 0.125013   d=12: 0.084135
```

The same non-collapse appears in pairwise probability regret and slope-direction recovery. Therefore `2q/(d+1)` is not an adequate standalone coordinate for this experimental design.

Because only four seeds were used, v7a does not support a precise dimension penalty. It does support rejecting the simple hypothesis that dimension enters only through parameter count.

## Result 2 — acquisition-policy ranking changes with dimension and budget

There is no universal policy ordering.

- At `d=2`, exact Gaussian ranking is strongest at low `κ`, while posterior-Fisher catches and then surpasses it at `κ=8` and `12`.
- At `d=4`, exact Gaussian ranking beats posterior-Fisher broadly through `κ=8`, but the advantage reverses by `κ=12`.
- At `d=8`, exact ranking is very strong at `κ=2`, but posterior-Fisher is better in mean top-K regret at `κ=4,6,8,12`.
- At `d=12`, exact ranking is worse at `κ=2` but substantially better than posterior-Fisher at `κ=4,6,8,12`.

This interaction is inconsistent with a single policy-independent sample-count law.

## Result 3 — slope direction is the latent quantity most visibly tracking ranking quality

V7a records the cosine between the true and posterior-mean slope vectors. Cells with very low ranking regret generally have high slope cosine, while poor-ranking cells often correspond to weak or even wrong recovered direction.

Examples:

```text
d=2, κ=6, exact ranking:     slope cosine 0.988949, top-K regret 0.001843
d=4, κ=2, posterior-Fisher:  slope cosine -0.038164, top-K regret 0.251507
d=12, κ=6, exact ranking:    slope cosine 0.672022, top-K regret 0.054677
d=12, κ=6, posterior-Fisher: slope cosine 0.478616, top-K regret 0.183797
```

This supports retaining directional posterior diagnostics as first-class sample-complexity outputs rather than relying only on coefficient RMSE or global probability fit.

## Result 4 — the fixed 18-candidate query bank is a major dimension-dependent geometry confound

A post-benchmark deterministic reconstruction used the exact v7a scenario seed rule and candidate-generation code to inspect the augmented query-bank design matrix

\[
Z=[\mathbf 1, X].
\]

Every bank is full column rank, but conditioning degrades sharply as `d` approaches the fixed candidate count `n=18`:

| d | columns d+1 | mean rank | mean cond(Z) | max cond(Z) | mean λ_min(ZᵀZ/n) | minimum λ_min |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 3 | 3 | 1.428 | 1.576 | 0.696058 | 0.499077 |
| 4 | 5 | 5 | 2.097 | 2.388 | 0.369736 | 0.268975 |
| 8 | 9 | 9 | 3.907 | 4.842 | 0.155632 | 0.089402 |
| 12 | 13 | 13 | 7.273 | 10.570 | 0.073844 | 0.024295 |

Thus matched `κ` did **not** imply matched directional information. A binary observation collected along an already well-covered direction is not equivalent to one collected along a weakly represented direction.

This is not merely a nuisance in Mosaic's setting. Synthetic calibration gives the system control over stimulus generation, so query-bank geometry is itself a design variable rather than an unavoidable population sample.

## Result 5 — convergence is nearly complete but one high-dimensional cell is not clean

Overall, `238/240` runs report Laplace convergence.

The two non-converged runs are both at `d=12, κ=8`:

```text
random, seed 3
posterior_fisher_d_optimal, seed 1
```

Each hit the solver's 50-iteration ceiling. Therefore the `d=12,κ=8` random and posterior-Fisher aggregate cells should not be used as clean evidence for a scaling law without a solver-sensitivity check.

## What v7a establishes

Under the exact synthetic assumptions tested:

1. raw binary observations per fitted coefficient, `κ=2q/(d+1)`, do not by themselves collapse out-of-sample ranking performance across `d=2,4,8,12`;
2. policy ordering is dimension- and budget-dependent;
3. slope-direction recovery is a useful diagnostic for ranking sample complexity;
4. the fixed-size random query bank becomes substantially more ill-conditioned with dimension, creating a material confound in the attempted `κ` scaling test;
5. two high-dimensional runs hit the Laplace iteration cap, so solver convergence should remain explicitly monitored; and
6. v7a is too small to estimate a universal dimension penalty or promote a query budget to product use.

## What v7a does not establish

V7a does not establish:

- the intrinsic sample-complexity exponent of preference dimension;
- that the observed dimension effects would remain under equally conditioned stimulus designs;
- that 18 candidates is an appropriate design-bank size for every feature dimension;
- that exact Gaussian ranking or posterior-Fisher is universally superior;
- that the two non-converged runs materially change the qualitative result;
- the effective dimensionality or structure of real human preference;
- transfer from synthetic judgments to real profiles or dates; or
- any relationship-quality prediction claim.

## Next experiment — controlled stimulus geometry

Before introducing sparse, low-rank, or non-isotropic preference structure, repeat the matched-`κ` experiment with a query bank whose empirical geometry is controlled across dimensions.

A clean construction is a centered orthogonal frame with

\[
\frac{1}{n}X^T X=I_d,
\qquad
\mathbf 1^T X=0,
\]

so the augmented bank satisfies

\[
\frac{1}{n}Z^T Z=I_{d+1}.
\]

With `n=18` and `d≤12`, a deterministic nonconstant DCT frame can provide this exactly without numerical whitening.

Keep the true slope distribution, held-out Gaussian population, response model, policies, seeds, and `κ` targets fixed. Change only the query-bank geometry.

The discriminating prediction is:

- if the dimensional curves become substantially closer, v7a's non-collapse was driven in important part by stimulus-design conditioning;
- if the curves remain separated despite `ZᵀZ/n = I`, then dimension has an additional effect beyond raw observation count and static query-bank covariance, and the next branch should test sparse/low-rank/non-isotropic preference structure.

This experiment is preferable to another acquisition-objective variant because it tests a concrete confound already present in v7a.