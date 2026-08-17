# S1 sensitivity-guided split benchmark v14f

## Question

Can most of v14e's search-allocation benefit be recovered cheaply by choosing only the split dimension from sensitivity information already computed by the v14c coupled likelihood-ratio bound?

This checkpoint changes only the split-axis rule. The depth-first frontier order remains unchanged.

## Frozen construction

v14f preserves:

- the exact v14c coupled confidence bound;
- `alpha_0=0.005` common nuisance-box e-process;
- `alpha_c=0.045` candidate-specific cone e-process;
- exact rational cone `tan(delta_cert)=1/2`;
- 60-digit directed arithmetic;
- the same finite nuisance box;
- depth-first frontier order;
- 250 processed nodes per side;
- minimum width `0.05`.

The aligned-240 side-0 case remains the mandatory negative control from v14d: a directly verified outside-cone point survives both confidence filters there, so a search-only change must not certify it.

## Sensitivity rule

For each rotation, the v14c mean-value lower bound already has the form

```text
center_ratio_lower - sum_j half_width_j * gradient_abs_upper_j.
```

v14f exposes the three existing axis contributions

```text
penalty_j = half_width_j * gradient_abs_upper_j
```

for the rotation that supplies the best certified cone-cover lower bound. The unresolved box is split along the legal axis with the largest penalty.

No child boxes are previewed. The diagnostic lower bound is required by tests to be exactly equal to the production v14c `Decimal` lower bound, both for an individual rotation and for the final cone-cover e-value lower bound.

## Results

### Aligned 240 side 0 — negative control

v14d reference:

- 250 nodes;
- node limit;
- 13 unresolved boxes.

v14f:

- **not certified**, as required;
- 250 nodes;
- node limit;
- **11 unresolved boxes**;
- common-confidence prunes: 68;
- cone-e prunes: 1;
- geometry prunes: 51;
- split dimensions: intercept 37, slope-1 49, slope-2 44;
- elapsed: **44.63 s**.

The negative-control invariant is preserved and the frontier improves modestly.

### Aligned 480 side 0

v14d reference:

- 250 nodes;
- resolution limit;
- 10 unresolved boxes.

v14f:

- not certified;
- 250 nodes;
- node limit;
- **9 unresolved boxes**;
- common-confidence prunes: 65;
- cone-e prunes: 3;
- geometry prunes: 53;
- split dimensions: intercept 32, slope-1 44, slope-2 53;
- elapsed: **46.09 s**.

The sensitivity splitter avoids the old resolution-limit termination but produces only a small frontier reduction.

### Aligned 480 side 1

v14d reference:

- 250 nodes;
- node limit;
- 9 unresolved boxes.

v14f:

- not certified;
- 250 nodes;
- node limit;
- **7 unresolved boxes**;
- common-confidence prunes: 79;
- cone-e prunes: **29**;
- geometry prunes: 14;
- split dimensions: intercept 32, slope-1 50, slope-2 46;
- elapsed: **54.40 s**.

The side-1 cone pruning exceeds the v14d coupled search's 21 cone prunes, showing that penalty-guided splitting can expose directional exclusions earlier without exhaustive previews.

## Comparison with v14e

The tradeoff is clear:

| case | v14d unresolved | v14e exhaustive-preview unresolved | v14f sensitivity unresolved | v14e elapsed | v14f elapsed |
|---|---:|---:|---:|---:|---:|
| 240 side 0 | 13 | 7 | 11 | 222.62 s | 44.63 s |
| 480 side 0 | 10 | 3 | 9 | 252.41 s | 46.09 s |
| 480 side 1 | 9 | 5 | 7 | 249.95 s | 54.40 s |

v14f recovers some search benefit at roughly ordinary coupled-search cost, but nowhere near the frontier reduction of v14e. Neither method certifies any case at 250 processed nodes.

## Interpretation

v14f is a useful negative/partial result:

1. the per-axis v14c bound penalties contain genuine split-allocation information;
2. that information can be exploited without changing the certificate or paying v14e's child-preview cost;
3. split-axis selection alone is not sufficient to close the 480-observation certificate;
4. v14e's larger frontier improvement therefore came substantially from additional frontier/child evaluation, not merely from choosing better axes.

The next step should not be another hand-tuned split score. The remaining numerical question is whether a **fair best-first branch order** can improve closure when every certified bound evaluation is counted as work, rather than v14e's processed-node metric plus uncharged preview tree.

A valid next benchmark should eagerly evaluate generated children once, count each evaluation against a fixed bound-evaluation budget, cache the result, and prioritize only already-evaluated unresolved boxes. This would isolate frontier order without granting the candidate free previews. The 240 side-0 negative control must remain uncertified.

If a fair best-first policy still cannot close the 480 cases at practical work, further search-policy tuning should stop and attention should move upstream to the common confidence-region representation / nuisance-box construction.

## Provenance

- workflow: `Science S1 Sensitivity Split v14f`;
- run: `32041812151`;
- job: `95422341619`;
- exact benchmark head: `c47ba897345c175cba96580a1a5552ad385b877e`;
- artifact: `9292130909`, `s1-sensitivity-guided-split-v14f`;
- artifact ZIP SHA256: `1da96ede9d969ee4d4f3127b09d5d9a71bc9ae2324763de43568aa32a1dfe93c`;
- JSON SHA256: `450cb4fcb4cb3269a8edbe22a8d0de172ac07de2732060464522145b44735b03`;
- JSON size: `3,040` bytes;
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed, focused v14 tests passed, and diagnostic/production lower-bound equality tests passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. It does not validate the linear preference model, synthetic feature basis, synthetic-to-real transfer, compatibility, relationship formation, or long-term relationship quality.