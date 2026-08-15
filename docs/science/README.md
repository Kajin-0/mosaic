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

Current experimental boundary: `results/s1-finite-confidence-geometry-benchmark-v13b.md`.

The controlled program now has three distinct results that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate

   \[
   \eta_F=B^2\kappa E[\sigma(BZ)(1-\sigma(BZ))]
   \]

   for mean ranking error under the correctly specified passive controlled-geometry model;
2. **rejected posterior stopping family:** v12a–v12e show that converting a Gaussian/Laplace posterior into an angular q95 statistic does not produce a trustworthy finite-sample sequential confidence guarantee;
3. **anytime-valid confidence route:** v13a verifies the prequential e-process on an exact finite composite null, and v13b verifies the intended operational sequence `confidence set -> exact finite directional geometry -> stop`.

The v12 failure chain is closed:

- v12a found severe raw-q95 undercoverage;
- v12b showed persistence does not repair weak-signal/high-dimensional subgroup failure;
- v12c/v12d restored safety only by becoming too conservative;
- v12e tangent projection restored utility but became strongly anti-conservative.

Do not resume that Laplace-q95 tuning family without a new theorem-level justification.

The v13 route changes the logic. For a normalized numerator chosen predictably before the current outcome,

\[
E_t(\theta)=\prod_{s\le t}\frac{q_s(Y_s)}{p_\theta(Y_s\mid x_s)}
\]

is a nonnegative martingale under fixed correctly specified `theta`, including predictable adaptive query selection. Ville's inequality supplies an anytime-valid parameter confidence sequence.

v13a's finite-null harness rejected only `22/4608 = 0.477%` true-null paths at nominal alpha 5%, while a deliberately outcome-leaking numerator rejected `4608/4608 = 100%`.

v13b then maintained an exact finite confidence set over 24 directions and stopped only when every retained direction lay within the requested angular radius of the retained maximum-likelihood direction. Across 6,144 paths:

- target 0.25: 65.9% stopped by 120 observations; false-stop rate 0.130%;
- target 0.20: 25.6% stopped; false-stop rate 0.081%;
- target 0.15: no paths stopped;
- truth was excluded from the anytime confidence sequence on 2.865% of paths;
- **zero false stops occurred while truth remained in the confidence set.**

Thus the finite-grid safety mechanism is working, but the current construction is conservative. The active next checkpoint is v13c: decompose the strict-target efficiency/resolution bottleneck while preserving the confidence-sequence invariant. Start with grid spacing × observation horizon while freezing the numerator and query policy. Do not loosen the safety threshold after seeing v13b.

A continuous S1 stopping rule still requires a conservative continuous confidence-set geometry certificate, including nuisance parameters. A local optimizer that can underestimate the best outside-cone likelihood is not acceptable because such an error would be anti-conservative.

Synthetic truth may be used to score a stopping rule only after each simulated decision. It must never enter the operational confidence statistic.

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
