# S1 Theta-Specific Challenger Benchmark v13g

## Status

Completed fresh-seed benchmark after `s1-nested-confidence-benchmark-v13f`.

v13f established the running-intersection confidence sequence as the preferred finite-grid representation and raised the nested all-grid-mixture stop rate to about 70% by 240 observations. v13g tests whether a different theorem-preserving efficiency lever can improve on that baseline: **a separate predictable challenger numerator for every candidate null parameter**.

The tested leave-null-out MLE challenger is a clear negative result. It behaves almost identically to ordinary MLE-face, underperforms SNML, and materially underperforms the nested all-grid mixture.

## Exact provenance

- GitHub Actions workflow run: `31914903057`
- benchmark job: `95085209711`
- exact successful benchmark head: `6d2bf7d97e4cd0aed26a2ee05de05a57ae2aca56`
- artifact ID: `9254738994`
- artifact name: `s1-theta-challenger-benchmark-v13g`
- artifact ZIP SHA256: `960ebc3e1f4a29faebc6e20ab675e120f48e462991b31af220f63519c77f0286`
- benchmark JSON SHA256: `a1dc351a677f0358d3cc7dd9ded47379310cfacd306be6479578ca3499e0b508`
- artifact retention expiry: 2026-08-29

The exact head passed Ruff lint, canonical Ruff formatting, mypy over 63 source files, and the complete engine pytest suite before benchmark execution.

Two prior workflow heads stopped before science on formatter-only differences. Their outputs are not used.

## Design

Fresh seed block:

- seeds `448..575` inclusive;
- 128 seeds per true direction;
- 12 true directions every 30 degrees;
- 1,536 paths.

Frozen components:

- correctly specified finite two-dimensional logistic model;
- 5-degree, 72-direction grid;
- `B=0.9`;
- target `epsilon=0.15 = 27 degrees`;
- nominal anytime `alpha=0.05`;
- candidate bank size 12;
- 240-observation cap;
- query controller frozen to the historical **current-time all-grid-mixture** confidence set and probability-range disagreement policy;
- all certification methods see the same `x_t,Y_t` path;
- running-intersection/nested confidence sequences for certification;
- global finite-grid MLE direction as the reported center.

Comparators:

- nested `mixture_all`;
- nested `mle_face`;
- nested `snml`.

New method:

- `theta_challenger`.

For candidate null `theta_j`, before observing the current response, select the maximum-likelihood face among all historical alternatives `theta_k != theta_j`. Average tied maximizers and use their binary acceptance probabilities as the normalized numerator `q_{t,j}`.

For every fixed null `j`,

\[
E_{t,j}=\prod_{s\le t}\frac{q_{s,j}(Y_s)}{p_{\theta_j}(Y_s\mid x_s)}
\]

is a valid e-process under `theta_j` because `q_{t,j}` is normalized and predictable.

## Results

| Predictor | Stops / 1536 | Stop rate | Median stop | False-stop rate | Truth excluded ever | Nested empty | Geometry violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| mixture_all | 1103 | **71.810%** | 217 | 0.586% | 4.362% | 0.651% | **0** |
| mle_face | 830 | 54.036% | 200 | 0.716% | 3.711% | 0.586% | **0** |
| snml | 894 | 58.203% | 205 | 0.716% | 4.036% | 0.651% | **0** |
| theta_challenger | 832 | **54.167%** | 201 | 0.716% | 3.646% | 0.586% | **0** |

Paired stop comparisons at 240 observations:

### Theta challenger vs nested mixture

- both stop: 746;
- challenger-only: 86;
- mixture-only: 357;
- neither: 347;
- paired exact `p = 2.70e-40`.

The direction is decisively unfavorable to the challenger.

### Theta challenger vs SNML

- both: 795;
- challenger-only: 37;
- SNML-only: 99;
- neither: 605;
- paired exact `p = 1.03e-7`.

SNML is materially better.

### Theta challenger vs MLE-face

- both: 823;
- challenger-only: 9;
- MLE-only: 7;
- neither: 697;
- paired exact `p = 0.804`.

The theta-specific challenger is statistically indistinguishable from ordinary MLE-face in this benchmark.

## Direction-level audit

The nested mixture exceeds the theta challenger at every tested true direction. Challenger stop rates range roughly from 47.7% to 58.6%, while nested-mixture rates range roughly from 66.4% to 82.8%.

The aggregate negative result is therefore not driven by one unfavorable orientation.

## Why the proposed challenger collapses onto MLE-face

The negative result has a simple analytical explanation.

Let `M_t` be the historical global maximum-likelihood face before response `Y_t`.

For candidate null `j`:

- if `j` is **not** in `M_t`, excluding `j` does not alter the maximizing alternative set;
- therefore `q_{t,j}` is exactly the ordinary MLE-face predictive;
- only when `j` itself lies on the current MLE face does the leave-null-out predictor differ.

In the common case of a unique current MLE:

- every non-leading candidate null uses the same ordinary MLE numerator;
- only the currently leading null uses the second-best likelihood face.

This is poorly aligned with the certification objective. Most candidate directions we want to reject are non-leading directions, precisely where the new method is **identical** to ordinary MLE-face. The construction spends its distinct behavior on the current leader, which is usually the least urgent hypothesis to eliminate.

That mechanism explains both observations:

1. `theta_challenger` and `mle_face` have nearly identical stop rates and stopping times;
2. neither recovers the large advantage of the nested all-grid mixture.

## Safety

All four methods have **zero geometric violations**. Every false directional stop occurs only after truth has left the corresponding nested confidence sequence.

The empirical truth-exclusion rates remain below 5% in this synthetic sample, but the martingale/Ville theorem rather than those observed frequencies is the source of fixed-parameter validity.

As in v13f, nested-set emptiness is a confidence/model failure state and must not be interpreted as successful certification.

## Scientific conclusion

v13g falsifies the specific hypothesis that a leave-null-out one-step-lagged **MLE** challenger will improve nested finite-grid certification.

It does **not** falsify parameter-specific numerators in general. It identifies why this particular construction fails: for almost every non-leading null it degenerates to the same common MLE predictor.

The result also strengthens v13f's empirical finding that the nested all-grid mixture is unusually effective because it can accumulate transient valid evidence against different directions over time.

## Next exact checkpoint

The next parameter-specific construction should differ for **every** candidate null and have an exact mixture interpretation.

For candidate null `theta_j`, use a uniform prior over all alternatives `theta_k != theta_j`. The one-step predictive is the posterior likelihood-weighted mixture over those alternatives. Its cumulative joint numerator is exactly

\[
Q_{t,j}^{(-j)}
=\frac{1}{N-1}\sum_{k\ne j}L_t(\theta_k),
\]

and the corresponding e-process is

\[
E_{t,j}^{(-j)}
=\frac{Q_{t,j}^{(-j)}}{L_t(\theta_j)}.
\]

This **leave-one-out alternative-mixture** numerator is normalized and predictable in sequential form, differs for every null `j`, and directly measures evidence for the composite finite alternative against `j`.

Run it on a fresh seed block with:

- nested confidence sequences;
- 5-degree grid;
- `B=0.9`;
- target 0.15;
- alpha 0.05;
- candidate bank size 12;
- acquisition controller frozen exactly as in v13f/v13g;
- nested all-grid mixture as the primary baseline;
- zero geometry violations as a hard safety invariant.

Do not change the query policy in the same checkpoint.

## Still unresolved before S1 closes

- conservative continuous-parameter cone certification including nuisance intercept and slope magnitude;
- higher-dimensional operating characteristics;
- deliberate likelihood misspecification: pair context/dependence, nonlinear curvature, interactions, multimodality, generator/feature error;
- validated visual feature basis;
- synthetic-to-real preference transfer;
- compatibility, relationship formation, and long-term outcome validation.
