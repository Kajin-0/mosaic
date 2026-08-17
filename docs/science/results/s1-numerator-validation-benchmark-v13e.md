# S1 Prospective Numerator Validation v13e

## Status

Completed fresh-seed prospective validation after `s1-numerator-efficiency-benchmark-v13d`.

v13d identified prequential predictive regret as the dominant finite-grid efficiency bottleneck and found two promising predictable adaptive numerators, `mle_face` and `snml`. Because those candidates were selected after inspecting v13d, v13e freezes the design and evaluates both on a disjoint synthetic seed block.

**Both adaptive numerators prospectively replicate the v13d efficiency gain.** MLE-face also edges SNML under the prespecified paired ranking criterion, although the practical difference is small.

## Exact provenance

- GitHub Actions workflow run: `31913535325`
- benchmark job: `95082020456`
- exact successful benchmark head: `70f08890047effc27f3263caa73082ff54f650a5`
- artifact ID: `9254407900`
- artifact name: `s1-numerator-validation-benchmark-v13e`
- artifact ZIP SHA256: `81d3a6128c885e02a861547c82e216a5dd27e9951b7f26c4403f7becd4485924`
- benchmark JSON SHA256: `1b2d872c8e705ab1a7a59f7994583bf91fec7d7f1f84c5e1d4944a18e2827716`
- artifact retention expiry: 2026-08-29

The successful run passed Ruff lint, canonical Ruff formatting, mypy over 61 source files, and the complete engine pytest suite before benchmark execution.

Two earlier workflow attempts did not execute any science: the first stopped at canonical formatting and the second at two mypy narrowing errors. Neither changed seeds, predictors, endpoints, gates, target, alpha, query policy, or benchmark semantics.

## Frozen prospective design

Fresh seed block:

- seeds `192..319` inclusive;
- 128 seeds per true direction;
- 12 true directions, every 30 degrees;
- total `12 × 128 = 1,536` common paths.

This block is disjoint from the v13c seed block `0..63` and v13d block `64..191`.

Frozen scientific components:

- correctly specified finite two-dimensional logistic model;
- `B=0.9`;
- 5-degree, 72-direction parameter grid;
- candidate bank size 12;
- target `epsilon=0.15 = 27 degrees`;
- nominal anytime `alpha=0.05`;
- 240-observation primary horizon;
- same all-grid-mixture confidence-set disagreement policy controls every query path;
- all predictors see the exact same query/response path for a synthetic subject;
- exact finite confidence-set directional-radius stopping rule.

Control:

- `mixture_all`.

Prespecified adaptive candidates:

- `mle_face`;
- `snml`.

`oracle_true` remains a synthetic diagnostic ceiling only and is not an operational candidate.

## Prespecified replication gate

Before the fresh responses were scored, each adaptive candidate was required to satisfy all three conditions at observation 240:

1. absolute stop-rate lift over `mixture_all` at least 0.10;
2. paired exact candidate-versus-control `p <= 0.01`;
3. zero geometric violations, where a geometric violation means a false directional stop while the true finite-grid parameter is still inside that predictor's confidence set.

MLE-face versus SNML would be ranked only if their fresh paired exact comparison reached `p <= 0.05`.

## Primary prospective result

| Predictor | Stops / 1536 | Stop rate | Absolute lift vs control | Candidate-only vs control | Control-only | Paired exact p | Geometry violations | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| mixture_all | 110 | 7.161% | — | — | — | — | 0 | control |
| mle_face | 413 | **26.888%** | **+19.727 pp** | 317 | 14 | `7.87e-76` | **0** | **PASS** |
| snml | 395 | **25.716%** | **+18.555 pp** | 297 | 12 | `2.55e-72` | **0** | **PASS** |

The v13d mechanism therefore replicates decisively on fresh paths. Adaptive predictable numerators approximately quadruple strict-target certification relative to the original universal mixture without changing a query or response.

## Burden and safety diagnostics

| Predictor | Stop rate @120 | Stop rate @180 | Stop rate @240 | Median stop by 240 | False stops by 240 | Truth excluded ever by 240 |
|---|---:|---:|---:|---:|---:|---:|
| mixture_all | 0.000% | 0.000% | 7.161% | 236 | 0 | 3.516% |
| mle_face | 0.000% | 0.456% | **26.888%** | **220** | 1 | 3.385% |
| snml | 0.000% | 0.000% | **25.716%** | 224 | 1 | 3.190% |
| confidence_mixture | 0.000% | 0.000% | 7.422% | 236 | 0 | 3.516% |
| oracle_true | 1.497% | **77.214%** | **96.354%** | 154 | 0 | 0.000% |

The fresh oracle result reproduces the large v13d efficiency ceiling: on exactly the same query/response paths, nearly all subjects could be certified by 240 observations if the prequential numerator tracked the true predictive law perfectly.

The remaining burden is therefore still principally a numerator-regret problem, not an absence of directional information in the current query path.

## MLE-face versus SNML

Fresh paired stop counts at 240:

- MLE-only stops: 44;
- SNML-only stops: 26;
- paired exact `p = 0.04139`.

This crosses the prespecified `p<=0.05` ranking threshold, so **MLE-face becomes the current preferred finite-grid operational numerator candidate for the next isolated efficiency experiments**.

The magnitude must not be overstated:

- MLE stop rate: 26.888%;
- SNML stop rate: 25.716%;
- absolute difference: only about 1.17 percentage points.

Thus the ranking is statistically resolved under the prespecified test but practically modest. SNML remains an important close comparator rather than a failed method.

## Direction-level audit

MLE-face improved over the mixture control at every one of the 12 tested true directions. Its 240-observation stop rates ranged from about 14.1% to 37.5% across those directions, rather than being driven by one favorable orientation.

This does not prove rotational invariance of the finite candidate/query geometry, but it rules out the simplest interpretation that the aggregate replication is caused by a single directional subgroup.

## The observed false-stop path

MLE-face and SNML each record one false directional stop, and both occur on the same synthetic path with true direction 330 degrees.

- truth first leaves the MLE/SNML confidence sequence at observation 143;
- MLE later stops at observation 218 with center 0 degrees and certified radius 25 degrees;
- SNML later stops at observation 219 with the same center/radius geometry;
- the true directional error is 30 degrees;
- `true_in_confidence_set=False` at both stops.

Therefore neither is a geometric-certification failure. The false stop occurs inside the allowed anytime confidence-sequence failure event. **There are zero false directional stops while truth remains in the confidence set.**

## Predictive regret on fresh paths

Mean realized excess log loss versus the oracle at observation 240:

- mixture_all: 2.275 nats;
- MLE-face: 2.601 nats;
- SNML: 2.474 nats.

As in v13d, mean log loss does not rank stopping efficiency. MLE/SNML create more favorable realized-`Q_t` paths despite heavier adverse tails, and geometric stopping is a nonlinear tail event.

This reinforces the v13d conclusion that numerator evaluation must include pathwise confidence contraction and stopping distributions rather than only average predictive regret.

## Scientific conclusion

v13e prospectively establishes, within the correctly specified finite-grid synthetic harness, that:

1. prequential numerator choice is a reproducible major efficiency lever;
2. both MLE-face and SNML materially outperform the original finite Bayesian mixture under unchanged observations;
3. MLE-face has a small but prospectively significant stop-rate advantage over SNML under the prespecified paired comparison;
4. the structural confidence-set geometry remains intact — no false stop occurs while truth remains inside the corresponding confidence set;
5. the oracle gap remains very large, so most theoretically available efficiency has not yet been recovered.

## Important theorem-level opportunity not yet benchmarked

The v13b–v13e implementations use the **current-time** confidence set

\[
C_t=\{\theta:E_t(\theta)<1/\alpha\}.
\]

An anytime confidence sequence can instead be represented by its running intersection

\[
C_t^{\cap}=\bigcap_{s\le t}C_s
=\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\}.
\]

This nested set has three immediate properties:

1. `C_t^cap` is always a subset of `C_t`;
2. the same simultaneous `1-alpha` coverage event guarantees that the true parameter remains in every `C_t^cap`;
3. for a subset-monotone directional-radius certificate, replacing `C_t` by `C_t^cap` can only certify at the same time or earlier because rejected parameters cannot re-enter later.

This is a theorem-preserving efficiency improvement, not an empirical relaxation of alpha. It should be isolated before inventing another predictor or changing query policy.

## Next exact checkpoint

**v13f: nested/running-intersection confidence-set efficiency.**

Freeze:

- the 5-degree model/grid;
- `B=0.9`;
- target 0.15;
- alpha 0.05;
- candidate bank and current disagreement-query controller;
- MLE-face as the prospectively preferred operational numerator;
- SNML and mixture as comparators;
- common-path semantics.

Compare current-time `C_t` against `C_t^cap` on fresh or otherwise prespecified paths, with the same directional-radius geometry.

The implementation-level invariant should be exact: on every path and every time, the nested confidence set must be a subset of the current-time set, and its first certification time may never be later.

After quantifying that free monotonicity gain, the next numerator-level idea should be a **theta-specific predictable challenger/test numerator**. For each candidate null `theta_j`, a separately predictable normalized challenger can define a valid e-process for that null; this may reduce the universal-prediction penalty substantially. Test it with query policy frozen before optimizing the acquisition policy itself.

## What remains unresolved before S1 can close

- conservative continuous-parameter cone certification with nuisance intercept and slope magnitude;
- higher-dimensional operating characteristics;
- deliberate likelihood misspecification: pair context/dependence, nonlinear curvature, interactions, multimodality, generator/feature error;
- a validated synthetic visual feature basis;
- synthetic-to-real profile-choice transfer;
- any inference about compatibility, relationship formation, or long-term relationship quality.
