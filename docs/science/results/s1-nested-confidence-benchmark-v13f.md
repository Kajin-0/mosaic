# S1 Nested Confidence-Sequence Benchmark v13f

## Status

Completed fresh-seed benchmark after `s1-numerator-validation-benchmark-v13e`.

v13b–v13e used the current-time e-process confidence set

\[
C_t=\{\theta:E_t(\theta)<1/\alpha\},
\]

which allows a parameter rejected at an earlier time to re-enter later if its e-value falls back below threshold. v13f isolates a theorem-preserving alternative: the running intersection

\[
C_t^{\cap}=\bigcap_{s\le t}C_s
=\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\}.
\]

The numerical result is large: **remembering past valid rejections roughly doubles or better the strict-target stopping rate, with no geometric violations.** It also changes the observed numerator ranking: under nesting, the original all-grid mixture becomes the strongest of the three tested operational predictors.

## Exact provenance

- GitHub Actions workflow run: `31914196650`
- benchmark job: `95083587659`
- exact successful benchmark head: `648c58af8f31686332898cd3b5424d0fde12ba77`
- artifact ID: `9254573869`
- artifact name: `s1-nested-confidence-benchmark-v13f`
- artifact ZIP SHA256: `fe19bcae76f84f7923e88756d18671ddd4ca6f4416ee5c2ab6ef314554aedb88`
- benchmark JSON SHA256: `d7af4395a3fb3ec08b6bb7183f7a78860d30eed539f90c48ee0c19743ee09db7`
- artifact retention expiry: 2026-08-29

The exact benchmark head passed Ruff lint, canonical Ruff formatting, mypy over 62 source files, and the complete engine pytest suite before benchmark execution.

Two earlier v13f workflow attempts stopped before science: one at canonical formatting and one at a mypy type narrowing. Neither changed the seed block, predictors, target, alpha, estimator, query controller, or nested-set definition.

## Theorem-level construction

For each fixed correctly specified parameter `theta`, Ville's inequality gives

\[
P_\theta\left(\sup_t E_t(\theta)\ge 1/\alpha\right)\le\alpha.
\]

Therefore the event

\[
\theta_*\in C_t\quad\forall t
\]

has probability at least `1-alpha` under the true fixed parameter. The running-intersection representation satisfies

\[
\theta_*\in C_t^{\cap}\quad\forall t
\iff
\theta_*\in C_t\quad\forall t.
\]

Thus nesting does **not** spend another alpha or weaken the coverage theorem. It only prevents previously rejected parameters from re-entering.

To isolate set representation rather than silently change the reported estimate, v13f uses the same global finite-grid maximum-likelihood direction `c_t` for both comparisons at every observation. Because

\[
C_t^{\cap}\subseteq C_t,
\]

the corresponding finite-grid directional radii obey pathwise whenever the nested set is nonempty:

\[
r_t(c_t;C_t^{\cap})\le r_t(c_t;C_t).
\]

The implementation hard-aborts if this inequality is violated. No such violation occurred.

## Frozen design

Fresh seed block:

- seeds `320..447` inclusive;
- 128 seeds per true direction;
- 12 true directions every 30 degrees;
- 1,536 total paths.

Scientific configuration:

- correctly specified finite two-dimensional logistic model;
- 5-degree, 72-direction grid;
- `B=0.9`;
- candidate bank size 12;
- strict target `epsilon=0.15 = 27 degrees`;
- nominal anytime `alpha=0.05`;
- 240-observation cap;
- query controller frozen to the **current-time all-grid-mixture confidence set** with the existing probability-range disagreement rule;
- same query/response path for current versus nested representations;
- same global finite-grid MLE center for both representations.

Predictors:

- `mixture_all`;
- prospectively selected v13e `mle_face`;
- close comparator `snml`.

Only the confidence-set representation changes: current-time versus running intersection.

## Primary results

| Predictor | Representation | Stops / 1536 | Stop rate | Median stop | False stops | Geometry violations |
|---|---|---:|---:|---:|---:|---:|
| mixture_all | current | 111 | 7.227% | 236 | 0 | 0 |
| mixture_all | **nested** | **1079** | **70.247%** | **217** | 7 | **0** |
| mle_face | current | 408 | 26.563% | 219.5 | 0 | 0 |
| mle_face | **nested** | **829** | **53.971%** | **201** | 6 | **0** |
| snml | current | 402 | 26.172% | 224 | 1 | 0 |
| snml | **nested** | **899** | **58.529%** | **204** | 6 | **0** |

### Horizon decomposition

| Predictor | Representation | Stop @120 | Stop @180 | Stop @240 |
|---|---|---:|---:|---:|
| mixture_all | current | 0.000% | 0.000% | 7.227% |
| mixture_all | nested | 0.065% | 3.125% | **70.247%** |
| mle_face | current | 0.000% | 0.391% | 26.563% |
| mle_face | nested | 0.065% | **13.997%** | **53.971%** |
| snml | current | 0.000% | 0.000% | 26.172% |
| snml | nested | 0.065% | **11.328%** | **58.529%** |

Nesting therefore improves both the number of subjects certified and the stopping time of subjects that would eventually certify under the current-time representation.

## Paired pathwise gains

### mixture_all

- both representations stop: 111;
- nested stops earlier: 94;
- equal stop time: 17;
- nested-only stops: **968**;
- current-only stops: **0**;
- among paths where both stop and nesting is earlier, median gain: **25 observations**.

### mle_face

- both stop: 408;
- nested earlier: 372;
- equal: 36;
- nested-only: **421**;
- current-only: **0**;
- median gain when earlier: **33 observations**.

### snml

- both stop: 402;
- nested earlier: 365;
- equal: 37;
- nested-only: **497**;
- current-only: **0**;
- median gain when earlier: **33 observations**.

On this benchmark, no current-time certification is lost by switching to nesting.

## Safety interpretation

Truth is ever excluded by the underlying current-time confidence sequence on:

- mixture_all: 4.232% of paths;
- mle_face: 3.451%;
- snml: 3.646%.

These are below the nominal 5% level in this finite synthetic sample, but the theorem rather than the empirical rate is the source of validity.

The nested set becomes empty by 240 on only about 1% of paths:

- mixture_all: 0.977%;
- mle_face: 1.042%;
- snml: 1.042%.

An empty nested set occurs only on the confidence-sequence failure side of the experiment and must be treated operationally as a confidence/model failure, **not** as a successful certificate.

The nested representation records more false directional stops than the current-time representation because an early erroneous exclusion of truth is permanent instead of being allowed to recover later. This is expected and does not enlarge the theorem-level error event.

Crucially:

> **Geometry violations = 0 for every predictor and representation.**

Every false directional stop occurs after the true parameter has already left the corresponding confidence sequence. No path falsely certifies a direction outside target while truth is still represented in the certified set.

Conditional on never excluding truth, nested stop rates by 240 are approximately:

- mixture_all: **71.0%**;
- mle_face: **54.3%**;
- snml: **59.3%**.

## Numerator ranking reversal

This is an important scientific consequence.

Under the non-nested current-time representation, v13d/v13e found MLE-face and SNML to be far more efficient than the all-grid mixture, and v13e prospectively selected MLE-face by a small margin over SNML.

Under the correctly nested representation in v13f, the ranking reverses:

1. mixture_all nested: **70.25%** stop;
2. SNML nested: **58.53%**;
3. MLE-face nested: **53.97%**.

The likely mechanism is that the stable all-grid mixture may reject different false directions transiently at different times. The current-time representation forgets those valid crossings when their e-values later fall back below threshold; the running intersection remembers all of them. MLE/SNML's favorable current-time tail is therefore less decisive once valid historical evidence is retained.

This means the v13e conclusion must be scoped precisely:

- MLE-face is preferred among the tested **current-time-set** numerators;
- it is **not** the preferred numerator under the newly established nested confidence representation;
- the all-grid mixture is the current observed leader under nesting, but v13f did not prespecify a formal numerator-ranking gate for this new representation, so that ranking should not be overstated as prospectively selected.

## Scientific conclusion

v13f establishes a stronger finite-grid operational boundary:

1. the running-intersection confidence sequence has the same fixed-parameter anytime coverage event as the non-nested sets;
2. with a common reported MLE center, its directional radius is pathwise no larger whenever nonempty;
3. in the tested finite logistic harness, remembering historical e-process crossings produces a **large** practical efficiency gain rather than a cosmetic one;
4. the improvement does not require changing alpha, target, likelihood, query policy, or observations;
5. no geometric-certification failure is observed;
6. numerator ranking depends materially on whether the confidence sequence is represented correctly as a running intersection.

Accordingly, **future finite-grid v13 work should use the nested confidence sequence by default.** The current-time-only representation remains useful as a historical comparator but should no longer be the primary operational object.

## Next exact checkpoint

The remaining gap is still substantial: the strongest observed nested method certifies about 70% by 240, whereas the v13d/e oracle predictive ceiling on the same class of query paths is about 96%.

The next isolated numerator experiment should therefore preserve the nested confidence representation and the frozen acquisition policy while testing a **theta-specific predictable challenger numerator**.

For each candidate null parameter `theta_j`, define its own normalized predictable numerator `q_{t,j}` before observing `Y_t`, for example from the one-step-lagged maximum-likelihood parameter among the alternative grid points `theta_k != theta_j`.

Then

\[
E_{t,j}=\prod_{s\le t}\frac{q_{s,j}(Y_s)}{p_{\theta_j}(Y_s\mid x_s)}
\]

remains a valid e-process under `theta_j` because `q_{t,j}` is normalized and predictable. A single common universal predictor is **not required** for confidence-sequence validity. This construction can target each false null against its strongest historical challenger and may reduce universal-prediction regret substantially.

Test it on a fresh seed block with:

- 5-degree grid;
- `B=0.9`;
- target 0.15;
- alpha 0.05;
- current acquisition controller frozen;
- nested confidence sets for all methods;
- `mixture_all` nested as the baseline control;
- MLE-face/SNML nested retained as comparators if computationally useful;
- zero geometric violations as a hard invariant.

Do not change the query policy in the same checkpoint.

## Still unresolved before S1 closes

- conservative continuous-parameter cone certification including nuisance intercept and slope magnitude;
- higher-dimensional operating characteristics;
- deliberate likelihood misspecification: pair context/dependence, nonlinear curvature, interactions, multimodality, generator/feature error;
- validated visual feature basis;
- synthetic-to-real preference transfer;
- compatibility, relationship formation, and long-term outcome validation.
