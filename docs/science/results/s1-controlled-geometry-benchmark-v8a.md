# S1 Controlled-Geometry Benchmark v8a — Static Query Geometry Explains a Large Part of the High-Dimension Penalty

## Status

Completed exploratory synthetic benchmark paired directly to `s1-sample-complexity-benchmark-v7a` under the correctly specified `visual-acceptance-linear-logit-v1` model.

This is **screening evidence only**: four paired scenario seeds per cell. It is not human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

The principal result is that v7a's fixed random query-bank geometry was a material confound. Replacing only that bank with an exactly centered orthogonal design substantially reduces cross-dimensional ranking spread for the active policies once the observation budget is moderate. It does not produce a universal `kappa` law, especially at low budget, and it does not prove that covariance conditioning alone explains the effect because the deterministic DCT frame also changes higher-order stimulus geometry.

## Provenance

- benchmark version: `s1-controlled-geometry-benchmark-v8a`
- model version: `visual-acceptance-linear-logit-v1`
- query-design version: `centered-dct-orthogonal-v1`
- exact branch head executed: `257ce59e91faa0b553cfb1b23ca714cc35188a0c`
- GitHub Actions run: `31879335118`
- benchmark job: `94999604088`
- artifact ID: `9245753119`
- artifact ZIP SHA-256: `569e0557345ad71c158497f45a38ad9c4fd8e5de245683a7ccfe2948bc8dd6c8`
- uncompressed JSON SHA-256: `91deed126cbfd7201e7cac339ebcd0c9d77b9c3fae8a6c570a37a5e6de3bd12c`
- raw simulation records: `240`
- authoritative repository gate on the same head: run `31879337252`, PASS

The benchmark workflow had read-only repository permission. It is one-use scientific infrastructure and should be removed after this result is recorded.

## Experimental contrast

V8a preserves from v7a:

```text
feature dimensions       d = 2, 4, 8, 12
kappa targets             2, 4, 6, 8, 12
scenario seeds            0..3
candidate count           18
held-out population       same 96 iid Gaussian candidates per paired seed
true alpha                same per paired seed
response RNG stream       same per paired seed
policies                   random / posterior-Fisher / exact Gaussian ranking regret
top-K                     8
prior variance            4 per effective coefficient
slope scale               0.9 / sqrt(d)
true intercept            0
response model            correctly specified linear-logistic Bernoulli acceptance
```

The only intended scientific change is the admissible **query candidate bank**.

V7a used 18 iid Gaussian query candidates. V8a uses the first `d` nonconstant columns of a DCT-II frame,

\[
x_{jk}=\sqrt{2}\cos\left[\frac{\pi(j+1/2)(k+1)}{18}\right],
\]

which satisfies, to floating-point precision,

\[
\frac{1}{18}X^TX=I_d,
\qquad
\mathbf 1^T X=0.
\]

Thus for the augmented design `Z=[1,X]`,

\[
\frac{1}{18}Z^TZ=I_{d+1}.
\]

The mean squared row norm remains `d`, matching the expectation of the v7a `N(0,I_d)` query distribution; this is not a trivial reduction in stimulus magnitude.

## Design invariant actually achieved

| d | max absolute feature mean | max absolute Gram error | min row norm | max row norm |
|---:|---:|---:|---:|---:|
| 2 | 4.59e-17 | 2.22e-16 | 0.944 | 1.981 |
| 4 | 4.59e-17 | 4.44e-16 | 1.632 | 2.749 |
| 8 | 3.15e-16 | 6.11e-16 | 2.374 | 3.635 |
| 12 | 3.15e-16 | 1.92e-15 | 3.213 | 4.025 |

The full query bank therefore has augmented condition number 1 up to floating-point error at every tested dimension.

## Aggregate means

| d | κ | q | policy | pair regret | top-K regret | probability MSE | slope cosine | conv |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 2 | 2 | 3 | exact Gaussian regret | 0.017421 | 0.028463 | 0.056914 | 0.890663 | 1.00 |
| 2 | 2 | 3 | posterior-Fisher | 0.017610 | 0.025672 | 0.042413 | 0.885947 | 1.00 |
| 2 | 2 | 3 | random | 0.028708 | 0.064898 | 0.056272 | 0.760507 | 1.00 |
| 2 | 4 | 6 | exact Gaussian regret | 0.016974 | 0.027653 | 0.043308 | 0.905242 | 1.00 |
| 2 | 4 | 6 | posterior-Fisher | 0.028960 | 0.062315 | 0.042714 | 0.847882 | 1.00 |
| 2 | 4 | 6 | random | 0.034075 | 0.075313 | 0.048339 | 0.801801 | 1.00 |
| 2 | 6 | 9 | exact Gaussian regret | 0.010982 | 0.021916 | 0.030359 | 0.940576 | 1.00 |
| 2 | 6 | 9 | posterior-Fisher | 0.016024 | 0.021579 | 0.021184 | 0.903309 | 1.00 |
| 2 | 6 | 9 | random | 0.008573 | 0.022498 | 0.014549 | 0.942321 | 1.00 |
| 2 | 8 | 12 | exact Gaussian regret | 0.009476 | 0.011726 | 0.016971 | 0.951777 | 1.00 |
| 2 | 8 | 12 | posterior-Fisher | 0.008784 | 0.020917 | 0.014361 | 0.938279 | 1.00 |
| 2 | 8 | 12 | random | 0.009718 | 0.024843 | 0.017843 | 0.910070 | 1.00 |
| 2 | 12 | 18 | exact Gaussian regret | 0.008392 | 0.011726 | 0.014789 | 0.957506 | 1.00 |
| 2 | 12 | 18 | posterior-Fisher | 0.003833 | 0.002106 | 0.009042 | 0.971673 | 1.00 |
| 2 | 12 | 18 | random | 0.008044 | 0.029066 | 0.018259 | 0.942179 | 1.00 |
| 4 | 2 | 5 | exact Gaussian regret | 0.071501 | 0.218091 | 0.113418 | 0.103274 | 1.00 |
| 4 | 2 | 5 | posterior-Fisher | 0.074148 | 0.229294 | 0.112240 | 0.181615 | 1.00 |
| 4 | 2 | 5 | random | 0.076545 | 0.217543 | 0.114789 | 0.232857 | 1.00 |
| 4 | 4 | 10 | exact Gaussian regret | 0.065379 | 0.202021 | 0.092851 | 0.162744 | 1.00 |
| 4 | 4 | 10 | posterior-Fisher | 0.055676 | 0.174057 | 0.051765 | 0.338136 | 1.00 |
| 4 | 4 | 10 | random | 0.062020 | 0.167216 | 0.077037 | 0.374377 | 1.00 |
| 4 | 6 | 15 | exact Gaussian regret | 0.034496 | 0.103562 | 0.049077 | 0.554260 | 1.00 |
| 4 | 6 | 15 | posterior-Fisher | 0.030066 | 0.072649 | 0.030969 | 0.617120 | 1.00 |
| 4 | 6 | 15 | random | 0.033088 | 0.067368 | 0.048369 | 0.664328 | 1.00 |
| 4 | 8 | 20 | exact Gaussian regret | 0.021727 | 0.065664 | 0.026566 | 0.756146 | 1.00 |
| 4 | 8 | 20 | posterior-Fisher | 0.018281 | 0.048716 | 0.015912 | 0.754924 | 1.00 |
| 4 | 8 | 20 | random | 0.032575 | 0.095639 | 0.046423 | 0.653207 | 1.00 |
| 4 | 12 | 30 | exact Gaussian regret | 0.008004 | 0.018363 | 0.011319 | 0.877778 | 1.00 |
| 4 | 12 | 30 | posterior-Fisher | 0.008566 | 0.020013 | 0.012185 | 0.895029 | 1.00 |
| 4 | 12 | 30 | random | 0.017286 | 0.032417 | 0.032487 | 0.814866 | 1.00 |
| 8 | 2 | 9 | exact Gaussian regret | 0.050338 | 0.182424 | 0.094968 | 0.535511 | 1.00 |
| 8 | 2 | 9 | posterior-Fisher | 0.048659 | 0.116101 | 0.090380 | 0.526531 | 1.00 |
| 8 | 2 | 9 | random | 0.058721 | 0.195433 | 0.096955 | 0.454895 | 1.00 |
| 8 | 4 | 18 | exact Gaussian regret | 0.031327 | 0.131168 | 0.041717 | 0.667555 | 1.00 |
| 8 | 4 | 18 | posterior-Fisher | 0.031485 | 0.096475 | 0.064325 | 0.693331 | 1.00 |
| 8 | 4 | 18 | random | 0.021970 | 0.088119 | 0.031596 | 0.790138 | 1.00 |
| 8 | 6 | 27 | exact Gaussian regret | 0.025526 | 0.106881 | 0.031548 | 0.754834 | 1.00 |
| 8 | 6 | 27 | posterior-Fisher | 0.024758 | 0.069447 | 0.038015 | 0.778923 | 1.00 |
| 8 | 6 | 27 | random | 0.018756 | 0.053347 | 0.023036 | 0.820285 | 1.00 |
| 8 | 8 | 36 | exact Gaussian regret | 0.024688 | 0.070432 | 0.024415 | 0.778577 | 1.00 |
| 8 | 8 | 36 | posterior-Fisher | 0.021920 | 0.060892 | 0.033708 | 0.824472 | 1.00 |
| 8 | 8 | 36 | random | 0.023230 | 0.052632 | 0.021611 | 0.793138 | 1.00 |
| 8 | 12 | 54 | exact Gaussian regret | 0.017690 | 0.062780 | 0.017694 | 0.832167 | 1.00 |
| 8 | 12 | 54 | posterior-Fisher | 0.016464 | 0.047447 | 0.021678 | 0.871211 | 1.00 |
| 8 | 12 | 54 | random | 0.026816 | 0.060018 | 0.021985 | 0.755891 | 1.00 |
| 12 | 2 | 13 | exact Gaussian regret | 0.048599 | 0.080935 | 0.097596 | 0.496058 | 1.00 |
| 12 | 2 | 13 | posterior-Fisher | 0.053558 | 0.130401 | 0.101636 | 0.497881 | 1.00 |
| 12 | 2 | 13 | random | 0.065153 | 0.223516 | 0.113601 | 0.413028 | 1.00 |
| 12 | 4 | 26 | exact Gaussian regret | 0.036646 | 0.111332 | 0.051163 | 0.624872 | 1.00 |
| 12 | 4 | 26 | posterior-Fisher | 0.024203 | 0.073509 | 0.040215 | 0.772239 | 1.00 |
| 12 | 4 | 26 | random | 0.060684 | 0.198910 | 0.092166 | 0.490147 | 1.00 |
| 12 | 6 | 39 | exact Gaussian regret | 0.022344 | 0.064798 | 0.029019 | 0.778230 | 1.00 |
| 12 | 6 | 39 | posterior-Fisher | 0.024952 | 0.070411 | 0.033356 | 0.737887 | 1.00 |
| 12 | 6 | 39 | random | 0.057240 | 0.160186 | 0.060399 | 0.515845 | 1.00 |
| 12 | 8 | 52 | exact Gaussian regret | 0.017036 | 0.028566 | 0.021206 | 0.833050 | 1.00 |
| 12 | 8 | 52 | posterior-Fisher | 0.023289 | 0.077268 | 0.027650 | 0.745825 | 1.00 |
| 12 | 8 | 52 | random | 0.042187 | 0.108846 | 0.038324 | 0.608871 | 1.00 |
| 12 | 12 | 78 | exact Gaussian regret | 0.010752 | 0.029154 | 0.014348 | 0.887901 | 1.00 |
| 12 | 12 | 78 | posterior-Fisher | 0.013622 | 0.032372 | 0.017443 | 0.830752 | 1.00 |
| 12 | 12 | 78 | random | 0.033245 | 0.096983 | 0.029646 | 0.683160 | 1.00 |

## Result 1 — active-policy cross-dimensional spread contracts sharply at moderate/high kappa

The most direct v7→v8 comparison is the range of the four dimension-specific cell means at a common `kappa`.

| policy | κ | top-K range v7 | top-K range v8 | pair-regret range v7 | pair-regret range v8 | slope-cosine range v7 | slope-cosine range v8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| posterior-Fisher | 2 | 0.189463 | 0.203622 | 0.081491 | 0.056538 | 0.894475 | 0.704332 |
| posterior-Fisher | 4 | 0.209170 | 0.111742 | 0.065216 | 0.031473 | 0.773121 | 0.509747 |
| posterior-Fisher | 6 | 0.196923 | 0.051070 | 0.053671 | 0.014042 | 0.660331 | 0.286189 |
| posterior-Fisher | 8 | 0.188520 | 0.056351 | 0.060664 | 0.014504 | 0.573003 | 0.192454 |
| posterior-Fisher | 12 | 0.172322 | 0.045341 | 0.051083 | 0.012631 | 0.487835 | 0.140920 |
| exact Gaussian regret | 2 | 0.219468 | 0.189628 | 0.072358 | 0.054080 | 0.774193 | 0.787389 |
| exact Gaussian regret | 4 | 0.152915 | 0.174367 | 0.054875 | 0.048405 | 0.646288 | 0.742498 |
| exact Gaussian regret | 6 | 0.143239 | 0.084965 | 0.051074 | 0.023514 | 0.460584 | 0.386315 |
| exact Gaussian regret | 8 | 0.111078 | 0.058707 | 0.037687 | 0.015212 | 0.372138 | 0.195631 |
| exact Gaussian regret | 12 | 0.103423 | 0.051055 | 0.039048 | 0.009687 | 0.379347 | 0.125339 |

For posterior-Fisher, by `kappa=6` the top-K range is about one quarter of the v7 value. The same contraction appears in pairwise ranking regret and slope-direction recovery. Exact Gaussian ranking shows the same qualitative contraction at `kappa=6,8,12`, though not at the lowest budgets.

Therefore a large fraction of v7's apparent high-dimensional non-collapse was not parameter count alone; it was the interaction between dimension and a deteriorating random candidate design.

## Result 2 — the strongest effect is the d=12 posterior-Fisher recovery

At `d=12`, posterior-Fisher changes as follows:

| κ | top-K regret v7 | top-K regret v8 | pair regret v7 | pair regret v8 | slope cosine v7 | slope cosine v8 |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0.165069 | 0.073509 | 0.057742 | 0.024203 | 0.468931 | 0.772239 |
| 6 | 0.183797 | 0.070411 | 0.053806 | 0.024952 | 0.478616 | 0.737887 |
| 8 | 0.190949 | 0.077268 | 0.062705 | 0.023289 | 0.413058 | 0.745825 |
| 12 | 0.176057 | 0.032372 | 0.054263 | 0.013622 | 0.489099 | 0.830752 |

All four paired seeds improve in top-K regret at each of these four cells. This is strong screening evidence for a geometry mechanism, though four seeds are not a confirmatory sample.

## Result 3 — selected-observation geometry improves, not only the unused full bank

A post-benchmark reconstruction used the retained `selected_pairs` and exact candidate generators to form the actual observed augmented design matrix, counting repeated candidate observations exactly as the likelihood does. At `d=12`, mean selected-design geometry is:

| policy | κ | min eigenvalue v7 | min eigenvalue v8 | condition v7 | condition v8 |
|---|---:|---:|---:|---:|---:|
| posterior-Fisher | 4 | 0.067 | 0.570 | 97.322 | 3.783 |
| posterior-Fisher | 6 | 0.078 | 0.632 | 66.467 | 3.063 |
| posterior-Fisher | 8 | 0.078 | 0.645 | 64.994 | 2.653 |
| posterior-Fisher | 12 | 0.080 | 0.563 | 65.393 | 2.552 |
| exact Gaussian regret | 4 | 0.084 | 0.542 | 56.673 | 4.153 |
| exact Gaussian regret | 6 | 0.092 | 0.685 | 47.649 | 2.664 |
| exact Gaussian regret | 8 | 0.091 | 0.736 | 44.827 | 2.144 |
| exact Gaussian regret | 12 | 0.091 | 0.812 | 46.333 | 1.490 |

Thus the active learner actually receives a much more isotropic observed design under v8. The full-bank invariant is not merely cosmetic.

This reconstruction is an unweighted second-moment diagnostic. Logistic Fisher information additionally weights each observation by `p(1-p)`, so it is not itself the complete information matrix.

## Result 4 — kappa still does not become a universal stopping coordinate

V8 does **not** make all dimensions or policies equivalent.

At low budgets (`kappa=2,4`), substantial dimension dependence remains and exact Gaussian ranking can become worse under the DCT frame in some cells. For example:

```text
exact ranking, d=8, kappa=2:
    v7 top-K regret 0.071884
    v8 top-K regret 0.182424

posterior-Fisher, d=2, kappa=4:
    v7 top-K regret 0.017142
    v8 top-K regret 0.062315
```

Even at high budget the active policies are not perfectly coincident across dimensions. The correct conclusion is therefore not “kappa works after whitening.” It is:

\[
\boxed{\text{raw observation count is incomplete; experimental information geometry is material.}}
\]

The remaining variation can arise from finite-budget stochastic responses, nonlinear logistic weights, repeated use of only 18 stimulus locations, active-policy path dependence, and higher-order query-bank geometry.

## Result 5 — numerical convergence also improves

V8a reports `240/240` converged Laplace fits.

V7a reported `238/240`, with both failures at `d=12,kappa=8`. The v8 result is consistent with better conditioned experimental data improving numerical behavior as well as inference quality. With only two prior failures, this is supporting evidence rather than a standalone solver claim.

## Result 6 — random querying does not receive the same universal benefit

The random policy remains mixed after replacing the bank. Some cells improve substantially and others degrade. The cleanest cross-dimensional contraction occurs for the active policies that can exploit the better-conditioned admissible set.

This matters mechanistically: simply replacing a random Gaussian cloud with bounded orthogonal points is not automatically sufficient. **Query policy and stimulus geometry interact.**

## What v8a establishes

Under the exact synthetic assumptions tested:

1. the dimension-dependent conditioning of v7's fixed 18-candidate random bank was a material confound;
2. controlling static query-bank geometry sharply reduces cross-dimensional ranking spread for active policies at moderate/high observation budgets;
3. the benefit propagates into the geometry of the actually selected observations;
4. high-dimensional posterior-Fisher performance can improve dramatically without changing the model, prior, number of candidates, held-out population, response model, or acquisition objective;
5. all 240 controlled-geometry runs converge; and
6. `kappa=2q/(d+1)` remains insufficient as a universal sample-complexity or stopping coordinate.

## What v8a does not establish

V8a does not establish:

- that covariance condition number alone caused every v7→v8 change;
- that a deterministic DCT frame is an optimal or realistic production stimulus design;
- that a centered orthogonal design guarantees good low-budget performance;
- that posterior-Fisher or exact Gaussian ranking is universally superior;
- an intrinsic sample-complexity exponent for preference dimension;
- a universal fixed query count;
- the effective dimensionality or structure of real human preference;
- transfer from synthetic judgments to real profiles or dates; or
- any relationship-quality prediction claim.

## Remaining confound and next experiment

The DCT frame controls first and second moments exactly but also changes higher-order stimulus geometry and support relative to an iid Gaussian cloud. Therefore v8 is not yet a unique causal attribution to conditioning.

The next clean replication should start from each v7 seed's **original Gaussian query bank**, center its columns, then orthogonalize/rescale those centered columns so that

\[
X^TX/n=I_d,
\qquad
\mathbf 1^T X=0,
\]

while retaining a stochastic Gaussian-derived row pattern for each seed.

A modified Gram-Schmidt transform on the centered columns is sufficient for `n=18,d<=12` and avoids introducing a heavy numerical dependency. The next benchmark should preserve the same true alpha, held-out candidates, response streams, policies, dimensions, `kappa` targets, and candidate count.

Discriminating interpretation:

- if the v8 contraction replicates with the Gaussian-derived orthogonalized bank, static information geometry is strongly implicated rather than DCT-specific support;
- if it does not, higher-order candidate geometry matters and the design problem is richer than covariance conditioning;
- only after that control should S1 decide whether to derive an information-spectrum stopping coordinate or introduce sparse/low-rank preference structure.
