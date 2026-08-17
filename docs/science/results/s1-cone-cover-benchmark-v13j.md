# S1 Cone-Cover Benchmark v13j

## Status

Completed fresh-seed benchmark after the negative v13i local-neighbor result and the prospective analytical design in `s1-cone-cover-mixture-design-v13j.md`.

The candidate-specific outside-cone mixture is a strong positive finite-grid result. It materially improves strict directional certification relative to the nested all-grid mixture while preserving the same geometric safety invariant.

## Exact provenance

- GitHub Actions workflow run: `31975307672`
- benchmark job: `95233764704`
- exact successful benchmark head: `67e5cdcbbaa1bdbc0dcefa6b9730d459ae5faad9`
- artifact ID: `9270976955`
- artifact name: `s1-cone-cover-benchmark-v13j`
- artifact ZIP SHA256: `3661ab9ec520ad039ca24d43beecb3af433b67c6b65c13c6159346bbfdf7a7b6`
- artifact retention expiry: 2026-08-30

The exact head passed Ruff lint, canonical Ruff formatting, mypy over 65 source files, and the complete engine pytest suite before benchmark execution.

The first workflow head stopped before science on a formatting-only difference. Its outputs are not used.

## Design

Fresh seed block:

- seeds `704..831` inclusive;
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
- running-intersection/nested confidence sequences;
- global finite-grid maximum-likelihood direction as the reporting center;
- acquisition controller frozen to the historical **current-time all-grid-mixture** confidence set with probability-range disagreement.

Primary control:

- nested `mixture_all`.

Candidate:

- nested `cone_cover`.

For candidate null `theta_j`, the cone-cover numerator uses a fixed uniform prior over the 11 offsets

\[
\{-150,-120,-90,-60,-30,+30,+60,+90,+120,+150,180\}\ \text{degrees}.
\]

Its cumulative joint numerator is

\[
Q_{t,j}^{cover}
=\frac1{11}\sum_{\Delta\in\mathcal D}L_t(\theta_j+\Delta),
\]

with circular indexing. The support was fixed from the 27-degree certification geometry before benchmark responses were observed: every 5-degree-grid direction outside the target cone is within 15 degrees of at least one supported alternative.

The sequential posterior predictive representation is normalized and predictable, so `Q/L_j` remains a valid e-process under candidate null `j`.

## Results

| Predictor | Horizon | Stop rate | False-stop rate | Truth excluded ever | Nested empty | Median stop | Geometry violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| mixture_all | 120 | 0.065% | 0 | 2.734% | 0.195% | 87 | 0 |
| cone_cover | 120 | 0.130% | 0 | 2.799% | 0.260% | 97.5 | 0 |
| mixture_all | 180 | 2.734% | 0.065% | 2.930% | 0.586% | 171 | 0 |
| cone_cover | 180 | **5.013%** | 0.130% | 2.995% | 0.586% | 173 | 0 |
| mixture_all | 240 | 71.289% | 0.260% | 2.930% | 0.716% | 216 | 0 |
| cone_cover | 240 | **88.477%** | 0.326% | 3.060% | 0.911% | **210** | 0 |

At 240 observations the paired stop table is especially informative:

- both stop: 1,095;
- cone-cover only: **264**;
- mixture-all only: **0**;
- neither: 177;
- paired exact `p = 6.75e-80`.

Thus every path certified by the all-grid mixture by 240 was also certified by cone-cover, while cone-cover additionally certified 264 paths.

At 180 observations:

- both stop: 42;
- cone-cover only: 35;
- mixture-only: 0;
- paired exact `p = 5.82e-11`.

The advantage is already visible before the final horizon.

## Safety

Geometry violations are zero for both methods at every reported horizon.

The cone-cover truth-exclusion rate by 240 is 3.060%, versus 2.930% for the all-grid mixture. Both are below the nominal 5% in this finite Monte Carlo sample, but empirical frequency is not the source of validity. Fixed-parameter validity follows from the predictable normalized numerator and the martingale/Ville argument.

Nested-set emptiness remains a failure state. Cone-cover's 0.911% empty-set frequency by 240 must not be counted as successful certification.

## Scientific interpretation

v13j confirms the efficiency principle suggested by the v13h/v13i contrast:

> A useful sparse challenger must jointly control universal-prediction dilution and maintain meaningful separation/coverage against the candidate null.

v13i minimized support size to two immediate ±5-degree neighbors and failed completely because those alternatives were too close to the null. v13j instead covers the entire outside-cone region at 30-degree spacing. It reduces support from the full grid to 11 alternatives while guaranteeing that every outside-cone grid truth is close to at least one supported challenger.

The resulting gain is large, pathwise, and prospective on fresh seeds. The cone-cover mixture is therefore the **leading finite-grid S1 numerator** under the current 2-D strict-target protocol.

The result does not establish that these 11 offsets are globally optimal. They are a geometrically motivated finite support that beats the previous baseline decisively without response-path tuning.

## Next exact checkpoint

Freeze the v13j cone-cover numerator and test **acquisition efficiency separately**.

The historical query controller still chooses the candidate feature with the largest probability range over the current-time all-grid-mixture confidence set. That controller predates both nested confidence sequences and the cone-cover numerator.

A natural theorem-preserving candidate is to choose the next feature using the **current surviving nested cone-cover set**, maximizing probability-range disagreement over retained parameters. Query covariates remain predictable from past observations, so changing acquisition this way does not alter the fixed-parameter e-process validity argument.

Prospectively compare on a fresh disjoint seed block:

1. frozen historical acquisition + cone-cover certification (control);
2. nested cone-cover disagreement acquisition + the same cone-cover certification.

Do not change numerator, target, grid, confidence representation, or reporting center in the same checkpoint.

Primary endpoint: paired stop probability at 180 and 240 observations, with stopping-time distribution as a secondary endpoint and zero geometry violations as a hard invariant.

## Still unresolved before S1 closes

- practical query burden even under the improved finite-grid certificate;
- conservative continuous-parameter cone certification including nuisance intercept and slope magnitude;
- higher-dimensional operating characteristics;
- deliberate likelihood misspecification: pair context/dependence, nonlinear curvature, interactions, multimodality, generator/feature error;
- validated visual feature basis;
- synthetic-to-real preference transfer;
- compatibility, relationship formation, and long-term outcome validation.
