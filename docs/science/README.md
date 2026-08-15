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

Current experimental boundary: `results/s1-numerator-efficiency-benchmark-v13d.md`.

The controlled program now has four distinct results that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate

   \[
   \eta_F=B^2\kappa E[\sigma(BZ)(1-\sigma(BZ))]
   \]

   for mean ranking error under the correctly specified passive controlled-geometry model;
2. **rejected posterior stopping family:** v12a–v12e show that Gaussian/Laplace angular-q95 statistics do not provide trustworthy finite-sample sequential confidence under the tested S1 protocol;
3. **anytime-valid confidence route:** v13a–v13b establish the finite-grid prequential e-process route `predictable numerator -> anytime C_t -> exact confidence-set geometry -> stop`;
4. **efficiency mechanism:** v13c–v13d show that strict-target burden is primarily caused by prequential predictive regret, not angular-grid resolution or an intrinsically uninformative query path.

The v12 family is closed. Do not resume Laplace-q95 tuning without a new theorem-level justification.

For a normalized numerator chosen predictably before the current outcome,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under fixed correctly specified `theta`, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.

### v13 finite confidence results

- **v13a:** valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an intentionally outcome-leaking numerator rejected 100% and therefore validated the harness's ability to detect the predictability violation.
- **v13b:** exact finite confidence-set geometry produced zero false directional stops while truth remained in the confidence set. The strict target 0.15 did not stop by 120 observations under the original 15-degree grid.
- **v13c:** refining the grid from 15° to 5° increased strict-target stopping at 240 observations from 2.73% to 7.55%, but all grids remained at zero through 180 and the finest-grid median stop was 237. Resolution is a secondary burden, not the main one.
- **v13d:** on common 5-degree-grid query/response paths, the current all-grid mixture stopped on 7.81% by 240, MLE-face on 26.30%, SNML on 25.85%, and confidence-restricted mixture on 8.07%. A synthetic-truth oracle numerator stopped on **76.43% by 180 and 96.55% by 240 on exactly the same observations**. Therefore the current query path contains enough directional information; predictive regret in the operational numerator is the dominant identified efficiency bottleneck.

MLE-face and SNML are not yet ranked scientifically. Their 240-observation stop counts were 404 and 397, with paired discordant counts 45 versus 38 (`p≈0.51`). Both require fresh-seed prospective replication against the original mixture control.

The immediate checkpoint is therefore a **prospective numerator validation** with the v13d design frozen. Do not select a winner from the v13d evaluation paths and call it validated.

After prospective replication, the remaining oracle gap should be attacked with theorem-preserving predictable challenger/test-specific numerators or another justified regret-reduction construction before query-policy optimization is mixed into the same experiment.

A continuous S1 stopping rule still requires a conservative continuous confidence-set geometry certificate, including nuisance parameters. A local optimizer that can underestimate the best outside-cone likelihood is unacceptable because that error is anti-conservative.

Synthetic truth may be used for evaluation and explicit oracle diagnostics only. It must never enter an operational confidence statistic or query decision.

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
