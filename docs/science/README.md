# Mosaic Scientific Inference Program

## Status

Active. Preliminary infrastructure Phases 0–8 are complete; scientific model work begins here.

## Governing objective

Mosaic ultimately aims to improve the probability and expected quality of mutually satisfying long-term relationships. No single upstream model should be confused with that terminal objective.

The scientific program separates:

```text
controlled observation
        ↓
latent/effective individual state
        ↓
directional candidate prediction
        ↓
dyadic/relationship outcome prediction
```

A model is only allowed to claim the level its evidence validates.

## Scientific workstreams

### S1 — Identifiable individual preference model — ACTIVE

Question: what is the smallest user-specific preference state that can actually be identified from controlled synthetic-candidate choices strongly enough to support stable out-of-sample ranking?

Primary document: `s1-identifiable-preference-model.md`.

Current experimental boundary: `results/s1-nested-confidence-benchmark-v13f.md`.

The controlled program now has five distinct results that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate

   \[
   \eta_F=B^2\kappa E[\sigma(BZ)(1-\sigma(BZ))]
   \]

   for mean ranking error under the correctly specified passive controlled-geometry model;
2. **rejected posterior stopping family:** v12a–v12e show that Gaussian/Laplace angular-q95 statistics do not provide trustworthy finite-sample sequential confidence under the tested S1 protocol;
3. **anytime-valid confidence route:** v13a–v13b establish the finite-grid prequential e-process route `predictable numerator -> confidence sequence -> exact confidence-set geometry -> stop`;
4. **efficiency mechanism:** v13c–v13e show that grid resolution is secondary and that prequential numerator choice materially changes strict-target burden under the current-time-set representation;
5. **correct confidence-sequence representation:** v13f shows that the running intersection `C_t^cap=intersection_{s<=t} C_s` retains past valid rejections, has the same simultaneous truth-coverage event, and produces a very large burden reduction without changing alpha, the likelihood, query policy, responses, or geometric target.

The v12 family is closed. Do not resume Laplace-q95 tuning without a new theorem-level justification.

For any normalized numerator chosen predictably before the current outcome,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under fixed correctly specified `theta`, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.

The preferred finite-grid representation is now the nested running intersection

\[
C_t^{\cap}=\bigcap_{s\le t}\{\theta:E_s(\theta)<1/\alpha\}
=\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\}.
\]

This uses the same `1-alpha` simultaneous coverage event as the sequence of current-time sets. Rejected parameters do not re-enter later.

### v13 finite-confidence results

- **v13a:** valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an intentionally outcome-leaking numerator rejected 100%, demonstrating the predictability requirement.
- **v13b:** exact finite confidence-set geometry produced zero false directional stops while truth remained in the confidence set. The strict target 0.15 did not stop by 120 observations under the original 15-degree grid.
- **v13c:** refining the grid from 15° to 5° increased strict-target stopping at 240 observations from 2.73% to 7.55%, but all grids remained at zero through 180 and the finest-grid median stop was 237. Resolution is a secondary burden.
- **v13d:** on common 5-degree-grid query/response paths using current-time sets, the all-grid mixture stopped on 7.81% by 240, MLE-face on 26.30%, SNML on 25.85%, while a synthetic-truth oracle stopped on 96.55% on exactly the same observations. This localized a major efficiency penalty to the prequential numerator rather than the query sequence.
- **v13e:** fresh seeds `192..319` prospectively replicated that current-time-set result. Mixture stopped 7.16%; MLE-face 26.89% (+19.73 pp, paired `p≈7.9e-76`); SNML 25.72% (+18.55 pp, `p≈2.5e-72`); zero geometry violations. MLE beat SNML by only ~1.17 pp (`p=0.0414`), so the practical gap was small.
- **v13f:** fresh seeds `320..447` corrected the confidence representation. With the same global finite-grid MLE center for both representations, nesting changed stop rates from `7.23% -> 70.25%` for mixture, `26.56% -> 53.97%` for MLE-face, and `26.17% -> 58.53%` for SNML. No current-time stop was lost; no geometric violation occurred. Among MLE paths where both representations stopped and nesting was earlier, the median gain was 33 observations.

### Current finite-grid conclusion

Future finite-grid v13 work should use **nested confidence sequences by default**. Current-time-only sets are historical comparators.

v13f also changes the interpretation of numerator experiments. Under the nested representation the observed ordering is:

1. all-grid mixture: 70.25%;
2. SNML: 58.53%;
3. MLE-face: 53.97%.

This does not establish a formally prespecified nested-numerator ranking, but it shows that v13e's MLE preference was specific to the inferior current-time-set representation. Do not carry that ranking forward unqualified.

The next isolated checkpoint is a **theta-specific predictable challenger numerator** with the query policy frozen. A common numerator is not required for fixed-parameter e-process validity: each candidate null `theta_j` may have its own normalized predictable `q_{t,j}`. The natural finite-grid first test uses the one-step-lagged maximum-likelihood alternative excluding `theta_j`, with ties averaged before the current response is observed. The resulting per-null e-processes are then accumulated into nested confidence sets.

Use nested `mixture_all` as the baseline control. Do not change the acquisition policy in the same checkpoint.

A continuous S1 stopping rule still requires a conservative continuous confidence-set geometry certificate, including nuisance parameters. A local optimizer that can underestimate the best outside-cone likelihood is unacceptable because that error is anti-conservative.

Synthetic truth may be used for evaluation and explicitly labeled oracle diagnostics only. It must never enter an operational confidence statistic or query decision.

### Later workstreams

These are deliberately not yet treated as solved:

- transfer from synthetic candidates to real profile decisions;
- contextual/profile preference inference;
- visual × contextual interactions;
- relationship-relevant self/partner psychometrics;
- directional attraction `A → B` and `B → A`;
- dyadic compatibility and risk;
- relationship formation and longitudinal quality `Q_AB(t)`;
- population-level allocation/global matching.

## Scientific discipline

For every model:

1. define the observable quantity first;
2. state the latent/effective parameterization;
3. prove or state identifiability assumptions;
4. distinguish population prior from individual evidence;
5. retain uncertainty;
6. version the feature basis, likelihood, model, and query policy;
7. preserve raw observations independently from derived outputs;
8. test model misspecification rather than automatically increasing complexity;
9. distinguish synthetic/analytic validation from real-world external validation; and
10. never treat infrastructure success as scientific validation.
