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

Current experimental boundary: `results/s1-cone-cover-benchmark-v13j.md`.

The controlled S1 program has six distinct conclusions that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate `eta_F=B^2 kappa E[sigma(BZ)(1-sigma(BZ))]` for mean ranking error under the correctly specified passive controlled-geometry model;
2. **rejected posterior stopping family:** v12a–v12e show that Gaussian/Laplace angular-q95 statistics do not provide trustworthy finite-sample sequential confidence under the tested protocol;
3. **anytime-valid confidence route:** v13a–v13b establish `predictable normalized numerator -> e-process confidence sequence -> exact confidence-set geometry -> stop` on a finite grid;
4. **nested representation:** v13f establishes the running intersection `C_t^cap=intersection_{s<=t} C_s` as the preferred finite-grid confidence representation because valid past rejections must not be allowed to re-enter;
5. **numerator-design boundary:** v13g–v13i show that neither leave-null-out MLE, near-equivalent leave-one-out all-alternative mixtures, nor extremely local ±5-degree alternatives solve efficiency. Prior dilution and null/alternative separation must be considered jointly;
6. **current leading finite-grid numerator:** v13j's geometrically prespecified 11-point outside-cone mixture reaches **88.48%** strict-target stopping by 240 observations versus **71.29%** for the nested all-grid mixture on 1,536 fresh paths, with 264 cone-cover-only stops, zero mixture-only stops, and zero geometry violations.

The v12 family is closed. Do not resume Laplace-q95 tuning without a new theorem-level justification.

For any normalized numerator chosen predictably before the current outcome,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under fixed correctly specified `theta`, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.

The preferred finite-grid representation is

\[
C_t^{\cap}=\bigcap_{s\le t}\{\theta:E_s(\theta)<1/\alpha\}
=\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\}.
\]

Rejected parameters do not re-enter later. An empty nested set is a confidence/model failure state, not a successful certificate.

### v13 finite-confidence progression

- **v13a:** valid true-null rejection `22/4608=0.477%` at nominal alpha 5%; an intentionally outcome-leaking numerator rejected 100%, demonstrating the predictability requirement.
- **v13b:** exact finite confidence-set geometry produced zero false directional stops while truth remained in the confidence set.
- **v13c:** grid refinement helps strict-target efficiency but does not explain the dominant horizon burden.
- **v13d/v13e:** numerator choice materially changes efficiency under current-time sets, but that ranking was representation-dependent.
- **v13f:** nesting increased all-grid-mixture strict-target stopping from about 7% to about 70% by 240 observations and became the required finite-grid representation.
- **v13g:** theta-specific leave-null-out MLE collapsed onto ordinary MLE-face and underperformed nested all-grid mixture.
- **v13h:** leave-one-out all-alternative mixture is analytically only a near-threshold-equivalent affine transform of all-grid mixture.
- **v13i:** immediate ±5-degree alternatives produced zero certificates by 240; sparse support without meaningful separation is ineffective.
- **v13j:** fixed support at offsets `{±30,±60,±90,±120,±150,180}` degrees covers the entire region outside the 27-degree target cone at 30-degree spacing. On fresh seeds `704..831`, stop rate was 88.48% by 240 versus 71.29% for all-grid mixture; median stop improved 216 -> 210; geometry violations remained zero. Cone-cover is the current leading finite-grid numerator.

### Current finite-grid conclusion

The current route is:

```text
candidate-specific cone-cover e-process
        ↓
nested confidence sequence
        ↓
global finite-grid MLE reporting direction
        ↓
exact radius over every retained direction
        ↓
strict directional certificate
```

Do not hand-tune further numerator supports on the v13j result. The next isolated efficiency lever is **acquisition policy** while keeping the cone-cover numerator fixed.

Compare prospectively:

- historical current-time all-grid-mixture disagreement acquisition + cone-cover certification;
- disagreement acquisition over the surviving nested cone-cover confidence set + the identical cone-cover certification.

Keep the grid, likelihood, slope norm, target, alpha, candidate bank, numerator, nested representation, and reporting center fixed. Zero geometry violations remains a hard invariant.

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
