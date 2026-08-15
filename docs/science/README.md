# Mosaic Scientific Inference Program

## Status

Active. Preliminary infrastructure Phases 0–8 are complete; scientific model work begins here.

## Governing objective

Mosaic ultimately aims to improve the probability and expected quality of mutually satisfying long-term relationships. No single upstream model should be confused with that terminal objective.

The scientific program therefore separates at least four levels:

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

Current experimental boundary: `results/s1-tangent-stopping-benchmark-v12e.md`.

The controlled program now has two distinct results that must not be conflated:

1. **mean directional sample complexity:** v11a supports the large-dimensional synthetic coordinate

   \[
   \eta_F=B^2\kappa E[\sigma(BZ)(1-\sigma(BZ))]
   \]

   for mean ranking error under the correctly specified passive controlled-geometry model;
2. **individual sequential stopping:** v12a–v12e show that converting a Gaussian/Laplace posterior into an angular q95 statistic does not produce a trustworthy finite-sample sequential confidence guarantee.

The stopping failure chain is now mechanistically resolved far enough to leave that family:

- v12a found severe raw-q95 undercoverage;
- v12b showed that two-round persistence reduces aggregate false stopping but does not repair weak-signal/high-dimensional subgroup failure;
- v12c full-trace radial debiasing restored safety but became too conservative;
- v12d transverse-only norm debiasing improved utility while still failing the strict strong-signal burden gate;
- v12e projected posterior perturbations into tangent space and recovered utility, but false-stop-given-stop rose to roughly 10–12% under the primary rule, failing both aggregate and subgroup safety.

Therefore the active next checkpoint is **not another Laplace-q95 correction**. The next methodological branch should construct an anytime-valid finite-sample confidence object for logistic preference direction under predictable/adaptive queries. The leading candidate is a prequential likelihood-ratio / e-process confidence sequence, followed by a conservative angular certification problem over the resulting confidence set.

Synthetic truth may be used to score a stopping rule only after each simulated decision. It must never enter the operational stop statistic.

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
