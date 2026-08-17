# S1 Numerator-Efficiency Benchmark v13d

## Status

Completed finite-grid efficiency benchmark after `s1-resolution-horizon-benchmark-v13c`.

v13c showed that the strict directional target `epsilon=0.15` is primarily evidence-limited under the current e-process construction rather than merely grid-resolution-limited. v13d isolates the **prequential numerator** as a possible source of that inefficiency while holding the observed adaptive data path fixed across all predictor variants.

The result is decisive at the mechanism level:

> **The current query sequence contains enough directional information for efficient certification. Most of the remaining burden is caused by operational predictive regret in the e-process numerator.**

An oracle-truth numerator certifies 76.4% of paths by 180 observations and 96.5% by 240 on exactly the same query/response paths on which the existing finite Bayesian-mixture numerator certifies only 0% and 7.8%, respectively.

Two theorem-valid adaptive predictors — lagged finite-grid MLE-face and SNML — recover part of this gap, reaching about 26% certification by 240 without changing a single query or response.

## Exact provenance

- GitHub Actions workflow run: `31912867546`
- benchmark job: `95080449144`
- exact benchmark head: `7dd1ad2f8666a1222a6475379cb254ba9693645f`
- artifact ID: `9254246118`
- artifact name: `s1-numerator-efficiency-benchmark-v13d`
- artifact ZIP SHA256: `9184bcad1571327bb0bd873b4a37e21b86d0dbc3550b4a4fb1edf7b2e8b2af16`
- benchmark JSON SHA256: `5ef0fa27cf7197519d3327828d24d3a6389e0d6fcf23f6a3f3da8aab14558610`
- artifact retention expiry: 2026-08-29

The benchmark executed only after Ruff lint, canonical Ruff formatting, mypy, and the complete engine pytest suite passed on the exact benchmark head.

Two earlier workflow attempts were blocked before benchmark execution by formatting-only CI failures. They did not produce scientific data and did not alter the benchmark design, seeds, predictors, target, or policy.

## Frozen design

The following components are common to every predictor:

- correctly specified finite two-dimensional logistic model;
- slope norm `B=0.9`;
- 5-degree angular parameter grid, 72 directions;
- shared true directions every 30 degrees;
- candidate bank size 12;
- target `epsilon=0.15 = 27 degrees`;
- nominal anytime level `alpha=0.05`;
- horizons 120, 180, and 240 binary observations;
- 128 fresh seeds per true direction, seeds `64..191`;
- 12 true directions × 128 seeds = 1,536 common paths;
- exact finite-grid directional-radius stopping geometry;
- **one common adaptive query/response path per synthetic subject**.

The common-path design is load-bearing. Query selection is controlled by the existing all-grid likelihood-mixture confidence set and probability-range disagreement policy. Every numerator is then evaluated on those exact same `x_t,Y_t` observations. Therefore differences in confidence-set contraction are attributable to the numerator rather than simultaneous changes in the query policy or stochastic response path.

## Predictors

### Operational, theorem-valid predictors

All operational predictors are normalized and chosen before the current response, so the fixed-parameter martingale/Ville validity argument is unchanged.

1. `mixture_all` — existing uniform-prior finite likelihood-mixture predictive.
2. `mle_face` — one-step-lagged finite-grid maximum-likelihood predictive, averaging exactly tied maximizers.
3. `snml` — sequential normalized maximum-likelihood predictor: compute the best hypothetical joint likelihood after `Y_t=0` and `Y_t=1`, then normalize those two scores.
4. `confidence_mixture` — likelihood-weighted predictive restricted to its previous confidence set.

### Non-operational oracle diagnostic

`oracle_true` uses the known synthetic generating parameter to set `q_t=p_true`.

This predictor is **not available operationally and must never be promoted into a production rule**. Its only purpose is to answer a mechanistic question: if prediction were perfect but the query sequence stayed unchanged, would the same observations be sufficient for certification?

## Results

| Predictor | Horizon | Stop rate | False-stop rate | Truth excluded ever | Mean realized regret vs oracle | Median realized regret | Median stop |
|---|---:|---:|---:|---:|---:|---:|---:|
| mixture_all | 120 | 0.0000 | 0.0000 | 0.0339 | 1.874 | 2.141 | — |
| mixture_all | 180 | 0.0000 | 0.0000 | 0.0371 | 2.120 | 2.398 | — |
| mixture_all | 240 | 0.0781 | 0.000651 | 0.0391 | 2.280 | 2.558 | 237 |
| mle_face | 120 | 0.0000 | 0.0000 | 0.0293 | 2.252 | 2.228 | — |
| mle_face | 180 | 0.00326 | 0.0000 | 0.0313 | 2.501 | 2.446 | 178 |
| mle_face | 240 | **0.2630** | 0.000651 | 0.0326 | 2.666 | 2.623 | **221** |
| snml | 120 | 0.0000 | 0.0000 | 0.0299 | 2.095 | 2.167 | — |
| snml | 180 | 0.0000 | 0.0000 | 0.0319 | 2.343 | 2.389 | — |
| snml | 240 | **0.2585** | 0.001302 | 0.0332 | 2.506 | 2.546 | **224** |
| confidence_mixture | 120 | 0.0000 | 0.0000 | 0.0339 | 1.874 | 2.140 | — |
| confidence_mixture | 180 | 0.0000 | 0.0000 | 0.0371 | 2.119 | 2.395 | — |
| confidence_mixture | 240 | 0.0807 | 0.000651 | 0.0391 | 2.279 | 2.565 | 237 |
| oracle_true | 120 | 0.00911 | 0.0000 | 0.0000 | 0.000 | 0.000 | 119.5 |
| oracle_true | 180 | **0.7643** | 0.0000 | 0.0000 | 0.000 | 0.000 | **147.5** |
| oracle_true | 240 | **0.9655** | 0.0000 | 0.0000 | 0.000 | 0.000 | **153** |

Counts at 240 observations:

- `mixture_all`: 120/1536 stops;
- `mle_face`: 404/1536 stops;
- `snml`: 397/1536 stops;
- `confidence_mixture`: 124/1536 stops;
- `oracle_true`: 1483/1536 stops.

## The main mechanistic result

The oracle comparison falsifies the hypothesis that the current disagreement-query sequence is intrinsically too weak to reach the strict target within the tested horizon.

On exactly the same observations:

- current mixture numerator: 7.8% stop by 240;
- oracle numerator: 96.5% stop by 240.

The query path therefore contains enough likelihood separation for almost universal certification when `Q_t` tracks the generating law closely. **Prequential predictive regret is now the dominant identified efficiency bottleneck.**

This does not prove the current query policy is optimal. It shows that changing the query policy is not necessary to explain the present 92% non-stop rate.

## Why MLE/SNML can stop more despite worse mean realized regret

The result initially looks paradoxical: `mle_face` and `snml` have slightly larger *mean* realized log-loss regret than the finite Bayesian mixture, yet they stop more than three times as often.

The path-level artifact resolves this.

At 240 observations:

- `mle_face` has larger realized `log Q` than `mixture_all` on about 40.2% of paths;
- `snml` does so on about 41.9%;
- on paths where MLE stops but the mixture does not, MLE's `log Q` advantage over the mixture averages about **0.63 nat**;
- on SNML-only stops, the corresponding advantage is about **0.53 nat**.

The adaptive predictors have substantially heavier regret tails, which worsens their mean log loss, but they also create a large favorable-path tail with a tighter confidence threshold. Stopping is a nonlinear tail event, not a function of mean predictive regret alone.

For reference, 240-observation realized regret quantiles are qualitatively different:

- `mixture_all` is comparatively concentrated;
- MLE and SNML have both a larger favorable low-regret tail and a much heavier adverse high-regret tail.

Therefore future numerator evaluation must report the **distribution of predictive regret and confidence contraction**, not just a mean log-loss score.

## MLE versus SNML is not resolved

MLE has the highest observed operational stop rate, but the difference from SNML is tiny:

- MLE: 404 stops;
- SNML: 397 stops.

On paired common paths:

- MLE-only stops: 45;
- SNML-only stops: 38;
- both stop: 359;
- neither stops: 1094.

An exact paired sign/McNemar-style comparison of the discordant paths gives no evidence that the seven-stop difference is reproducible (`p≈0.51`).

Accordingly, **v13d does not establish that MLE is scientifically superior to SNML**. Both should be treated as promising adaptive-numerator candidates requiring fresh-seed prospective validation.

## Safety audit

Observed false stops by 240:

- mixture_all: 1/1536;
- MLE: 1/1536;
- SNML: 2/1536;
- confidence_mixture: 1/1536;
- oracle: 0/1536.

Every observed false stop occurred only after the true finite-grid parameter had already been excluded from that predictor's anytime confidence sequence. **No false stop violated the confidence-set geometry implication while truth remained inside the set.**

This is the same structural safety mechanism established in v13b: the geometric certificate is not the source of the observed error; the nominal `alpha` event is.

The theorem, not these empirical rates, remains the basis of fixed-parameter anytime validity.

## A useful deterministic bound for the control numerator

For the uniform 72-point Bayesian-mixture predictor,

\[
Q_t^{mix}=\frac1{72}\sum_{j=1}^{72}L_t(\theta_j).
\]

Because the true finite-grid parameter is one term in that sum,

\[
\log L_t(\theta_*)-\log Q_t^{mix}\le \log 72\approx4.277.
\]

The nominal e-process crossing threshold is only

\[
\log(1/\alpha)=\log20\approx2.996.
\]

Thus universal-prediction regret is large enough, in principle, to add an evidence penalty comparable to or larger than the nominal testing threshold itself. v13d shows that this is not merely an algebraic curiosity: the oracle gap is operationally enormous.

## What v13d establishes

Within the correctly specified finite-grid synthetic harness:

- the strict-target burden is **not primarily caused by an uninformative query path**;
- prequential numerator efficiency is a major controllable determinant of confidence-set contraction;
- predictable adaptive numerators can improve stop probability materially without sacrificing the e-process theorem;
- MLE-face and SNML are promising but not distinguished from one another by this experiment;
- the existing confidence-restricted mixture is almost identical operationally to the all-grid mixture and does not solve the burden problem;
- the oracle gap remains large, so substantial efficiency headroom remains even after MLE/SNML.

## What it does not establish

v13d does not establish:

- that MLE or SNML should be promoted without fresh prospective validation;
- that either predictor will retain its operating characteristics in higher dimension;
- that the current disagreement query policy is optimal;
- a continuous-parameter confidence certificate;
- validity under model misspecification;
- a validated synthetic feature basis;
- synthetic-to-real preference transfer;
- compatibility or relationship prediction.

## Next exact checkpoint

Run a **fresh-seed prospective numerator validation** on a disjoint seed block with the v13d design frozen.

Prespecify:

- `mixture_all` as control;
- `mle_face` and `snml` as the two candidate adaptive numerators;
- the same 5-degree grid, `B=0.9`, target 0.15, alpha 0.05, candidate bank, disagreement-query controller, and 240-observation cap;
- primary efficacy endpoint: stop rate by 240;
- burden endpoint: median stopping observation among stops;
- safety diagnostics: truth-exclusion and false-stop rates, with the invariant that any false directional stop while truth remains in the confidence set is a critical implementation failure.

The prospective study should test whether the ~26% stop rate for MLE/SNML replicates against the ~8% mixture control. It should **not** use the seven-stop MLE-vs-SNML difference as an established ranking.

After prospective replication, the next methodological branch should attack the remaining oracle gap. A natural theorem-preserving direction is a predictable test-specific or challenger-tracking numerator, rather than immediately changing the query rule. Query-policy optimization can then be isolated separately if substantial burden remains.
