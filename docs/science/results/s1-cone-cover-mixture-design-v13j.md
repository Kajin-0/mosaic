# S1 Cone-Cover Mixture Design v13j

## Status

Analytical design checkpoint after the negative `s1-local-neighbor-benchmark-v13i`.

v13i showed that minimizing prior dilution alone is not enough: a two-neighbor mixture at ±5 degrees produced zero certificates by 240 observations because the challenger distribution remained too close to each candidate null.

## Design principle

The certification target is `epsilon=0.15`, or 27 degrees. On the active 5-degree circular parameter grid, a candidate null that must be eliminated for a valid directional certificate is therefore at least 30 degrees away from the reported direction/truth on the modeled grid.

That creates a natural sparse alternative set for each candidate null `theta_j`: cover the **outside-cone** region rather than the immediate neighborhood of the null.

Use offsets

\[
\Delta \in \{\pm30,\pm60,\pm90,\pm120,\pm150,180\}\ \text{degrees}.
\]

There are 11 unique alternatives.

For candidate null `theta_j`, define a fixed uniform prior over those 11 offset alternatives and use the corresponding posterior predictive sequentially. Equivalently, the cumulative joint numerator is

\[
Q_{t,j}^{cover}=\frac1{11}\sum_{\Delta\in\mathcal D}L_t(\theta_j+\Delta),
\]

with circular indexing.

The e-process

\[
E_{t,j}^{cover}=Q_{t,j}^{cover}/L_t(\theta_j)
\]

is valid under `theta_j`: the mixture prior is fixed in advance, and its sequential posterior predictive is normalized and predictable before the current response.

## Why this support is geometrically justified

On the 5-degree grid, every direction outside the 27-degree target cone is at least 30 degrees from the null. The 30-degree-spaced support covers the full outside-cone circle.

For every grid direction outside the target cone, at least one support point lies within 15 degrees of it. Thus the challenger avoids v13i's local-separation collapse while retaining a substantially smaller mixture support than the 72-point all-grid predictor.

The construction therefore balances two terms that v13i showed cannot be optimized independently:

1. **prior/universal-prediction dilution** — only 11 alternatives rather than the full grid;
2. **separation/coverage** — an outside-cone truth is always close to a supported alternative.

This is a design consequence of the certification geometry, not a support set selected by inspecting v13i response paths.

## Benchmark contract

Prospectively test the cone-cover mixture on a fresh disjoint seed block.

Freeze:

- 5-degree, 72-direction grid;
- `B=0.9`;
- target `epsilon=0.15`;
- alpha `0.05`;
- candidate bank size 12;
- horizons 120, 180, 240;
- running-intersection/nested confidence sequences;
- global finite-grid MLE reporting center;
- acquisition controller: historical current-time all-grid-mixture confidence set with probability-range disagreement.

Use fresh seeds `704..831` inclusive and the same 12 true directions every 30 degrees.

Primary control: nested `mixture_all`.

Primary endpoint: paired stop-probability difference by 240 observations.

Hard invariant: zero geometry violations. An empty nested confidence set remains a confidence/model failure state, not a successful stop.

## Interpretation rule

- If cone-cover materially exceeds the nested all-grid mixture while preserving geometry, it becomes the leading finite-grid numerator candidate.
- If it roughly matches the all-grid mixture, the support reduction is still useful computationally but does not solve query burden.
- If it underperforms materially, then hand-designed sparse support is not sufficient; move toward a theorem-preserving adaptive universal predictor or acquisition-policy improvement rather than tuning more angular support sets on the same data.

Do not change numerator and acquisition policy in the same checkpoint.

## Nonclaims

This design is confined to the finite 2-D circular synthetic model. It does not establish continuous cone certification, higher-dimensional behavior, human likelihood correctness, visual-feature validity, synthetic-to-real transfer, compatibility, or relationship outcomes.
