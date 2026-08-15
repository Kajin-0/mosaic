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

Current experimental boundary: `results/s1-signal-scaling-benchmark-v11a.md`. Under the correctly specified passive controlled-geometry synthetic model, v11a prospectively supports

\[
\eta_F=B^2\kappa E[\sigma(BZ)(1-\sigma(BZ))]
\]

as the dominant large-dimensional **mean directional-ranking information coordinate** across `B=0.55–1.50`; at `d=12`, the large-dimensional law predicts the 15 tested cell means with about `0.0079` mean absolute error. This remains an oracle/theoretical coordinate because the true `B=||beta||` is unknown in operation, and the upper error tail remains too broad to use mean performance as a calibration stopping rule.

The active next checkpoint is v12a: test a posterior-observable angular uncertainty bound as a sequential stopping statistic and measure false-stop, missed-stop, stopping-time, and censoring behavior. Synthetic truth may be used to score the rule only after each simulated stopping decision; it must not enter the stop statistic itself.

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
5. retain posterior uncertainty;
6. version the feature basis, likelihood, model, and query policy;
7. preserve raw observations independently from derived outputs;
8. test model misspecification rather than automatically increasing complexity;
9. distinguish synthetic/analytic validation from real-world external validation; and
10. never treat infrastructure success as scientific validation.
