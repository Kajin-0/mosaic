# S1 Local-Neighbor Mixture Benchmark v13i

## Status

Completed fresh-seed benchmark after the analytical v13h leave-one-out-mixture equivalence result.

The proposed two-neighbor parameter-specific numerator is a decisive efficiency failure. It preserves e-process validity but produces no directional certificates by 240 observations on any of the 1,536 fresh paths.

## Exact provenance

- GitHub Actions workflow run: `31915500591`
- benchmark job: `95086597749`
- exact successful benchmark head: `dcd7d09bb4d9b058c34f3c096118be7c8cc20c2c`
- artifact ID: `9254855290`
- artifact name: `s1-local-neighbor-benchmark-v13i`
- artifact ZIP SHA256: `cf41c7bf195ea71cf55880709f39c6aeea9ac3260d9e0a5709933cfbeb505a3f`
- artifact retention expiry: 2026-08-29

The exact head passed Ruff lint, Ruff formatting, mypy over 64 source files, and the complete engine pytest suite before benchmark execution.

A prior workflow head failed on formatting only; its output is not used.

## Design

Fresh seed block:

- seeds `576..703` inclusive;
- 128 seeds per true direction;
- 12 true directions every 30 degrees;
- 1,536 paths.

Frozen components:

- correctly specified finite two-dimensional logistic model;
- 5-degree, 72-direction parameter grid;
- `B=0.9`;
- target `epsilon=0.15 = 27 degrees`;
- nominal anytime `alpha=0.05`;
- candidate bank size 12;
- horizons 120, 180, and 240 observations;
- acquisition controller frozen to the historical current-time all-grid-mixture confidence set and probability-range disagreement policy;
- nested/running-intersection confidence sequences for certification;
- global finite-grid maximum-likelihood direction as the reported center.

Primary control:

- nested `mixture_all`.

New method:

- nested `local_neighbor`.

For null direction `theta_j`, the challenger is the posterior predictive induced by a fixed 50/50 prior on the two circularly adjacent grid directions `theta_{j-1}` and `theta_{j+1}`. Its cumulative joint numerator is

\[
Q_{t,j}^{local}=\frac12\left[L_t(\theta_{j-1})+L_t(\theta_{j+1})\right].
\]

The sequential predictive form is normalized and chosen from historical likelihoods before the current response, so the corresponding candidate-specific e-process remains valid under `theta_j`.

## Results

### Nested all-grid mixture control

| Horizon | Stop rate | False-stop rate | Truth excluded ever | Nested empty | Median stop |
|---:|---:|---:|---:|---:|---:|
| 120 | 0.065% | 0 | 2.995% | 0.260% | 115 |
| 180 | 2.409% | 0.065% | 3.451% | 0.326% | 169 |
| 240 | **71.745%** | 0.651% | 3.516% | 0.391% | 218 |

### Local-neighbor mixture

| Horizon | Stop rate | False-stop rate | Truth excluded ever | Nested empty | Median stop |
|---:|---:|---:|---:|---:|---:|
| 120 | **0%** | 0 | 0% | 0% | — |
| 180 | **0%** | 0 | 0% | 0% | — |
| 240 | **0%** | 0 | 0% | 0% | — |

At 240 observations, the paired stop table is:

- both stop: 0;
- local-neighbor only: 0;
- mixture-all only: 1,102;
- neither: 434.

The local-neighbor method is therefore not merely worse than the all-grid mixture; under this protocol it fails to produce a single certificate.

## Safety

Geometry violations are zero for both methods.

For the local-neighbor method, truth is never excluded and the nested set never becomes empty on the tested paths. This is not evidence of superior practical performance. It reflects an excessively weak e-process that rarely rejects any candidate parameter.

As throughout v13, theorem-level fixed-parameter validity comes from predictability, normalization, and the martingale/Ville argument rather than the empirical exclusion frequency.

## Why the local-neighbor idea fails

v13h correctly identified the `log N` prior-dilution cost of the all-grid mixture, but v13i shows that **mixture dilution is only one side of the efficiency tradeoff**.

The other side is separation from the null.

With a 5-degree grid, each local challenger differs from `theta_j` by only 5 degrees. Under the logistic observation model, the resulting Bernoulli probabilities are often extremely close. Therefore the expected log e-increment against `theta_j` is small even when the true direction is far from `theta_j`.

Informally, a useful challenger must balance

\[
\text{predictive regret / prior dilution}
\qquad\text{against}\qquad
\text{KL separation from the candidate null}.
\]

The two-neighbor construction minimizes prior dilution but collapses the second quantity. The all-grid mixture pays a larger universal-coding penalty but places some predictive mass on alternatives much closer to the truth, allowing evidence against false nulls to accumulate much faster.

This result also explains why simply concentrating the alternative prior as narrowly as possible is not a sound efficiency principle.

## Scientific conclusion

v13i falsifies the hypothesis that immediate angular neighbors are the right sparse alternative set for candidate-specific e-process certification.

The next numerator should not return to all 71 alternatives, but it should cover **multiple angular scales**. The design problem is now a sparse universal-prediction problem: retain enough alternatives that at least one is meaningfully closer to the unknown truth than the candidate null, while paying far less prior dilution than the 72-point all-grid mixture.

## Next exact checkpoint

Test a fixed **multiscale candidate-specific alternative mixture** with circular offsets chosen before seeing any response path, for example

\[
\Delta\in\{\pm 10^\circ,\pm 30^\circ,\pm 60^\circ,\pm 120^\circ,180^\circ\}.
\]

For candidate null `theta_j`, use a fixed prior over those offset alternatives and update their posterior weights predictably from historical likelihoods. This remains a valid candidate-specific e-process while reducing the support from 71 alternatives to 9 and retaining alternatives at several KL/separation scales.

The exact offset set and prior weights should be justified analytically before the next large benchmark. In particular, compute one-step or design-averaged expected log-e growth versus angular truth separation under the frozen candidate bank/query distribution, rather than choosing offsets only by intuition.

Do not modify acquisition and numerator simultaneously.

## Still unresolved before S1 closes

- efficient finite-grid numerator/query design under strict directional certification;
- conservative continuous-parameter cone certification including nuisance intercept and slope magnitude;
- higher-dimensional operating characteristics;
- deliberate likelihood misspecification: pair context/dependence, nonlinear curvature, interactions, multimodality, generator/feature error;
- validated visual feature basis;
- synthetic-to-real preference transfer;
- compatibility, relationship formation, and long-term outcome validation.
