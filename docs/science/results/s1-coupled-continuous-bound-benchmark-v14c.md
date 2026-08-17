# S1 coupled continuous bound benchmark v14c

## Question

Does preserving the dependence between the rotated-alternative likelihood and the null likelihood materially tighten the continuous cone e-process lower bound enough to close the current branch-and-bound certificate?

This checkpoint changes only the boxwise cone e-value lower bound. It keeps the grouped sufficient statistics, alpha split, conservative rational cone, nuisance box, branch order, node budget, and resolution fixed.

## Method

The v14a/v14b bound formed a lower bound on each rotated-alternative likelihood and an upper bound on the null likelihood separately before subtracting. That is safe but discards their common dependence on the same parameter vector inside the box.

v14c instead bounds, for each fixed rotation,

```text
log L_rot(theta) - log L_null(theta)
```

directly over the same parameter box. The implementation uses 60-digit directed `Decimal` arithmetic and interval-gradient / mean-value bounds. The candidate-specific cone-cover lower bound then uses the best certified rotated ratio minus the conservative upper bound on `log(11)`.

The statistical construction is unchanged:

- total alpha: 0.05;
- common nuisance-box e-process: 0.005;
- candidate-specific directional cone e-process: 0.045;
- certified cone tangent: exactly `1/2`, corresponding to `atan(1/2) ~= 26.565 degrees`, deliberately narrower than the nominal 27-degree target.

## Bound validation

Six randomized 3-D parameter boxes were checked on a 3 x 3 x 3 interior grid, for 162 direct high-precision points.

- old grouped-bound violations: **0**;
- coupled-bound violations: **0**;
- old minimum direct-minus-bound slack: **25.8971031082 log units**;
- coupled minimum slack: **5.16098324365 log units**;
- old median slack: **62.9354821429 log units**;
- coupled median slack: **27.5626566351 log units**.

The coupled lower bound improved every tested box:

- minimum improvement: **20.7361198645 log units**;
- median improvement: **32.6663860129 log units**;
- maximum improvement: **48.1824972979 log units**.

This confirms that dependence loss in the separate alternative/null enclosure was a real source of looseness.

## Closure result

The tighter bound did **not** close either aligned strong-signal scenario under the frozen 250-node-per-side budget.

### 240 observations

Grouped v14b-style search:

- certified: no;
- total nodes: 500;
- total runtime: 23.96 s;
- side 0: 250 nodes, node limit, 11 unresolved boxes;
- side 1: 250 nodes, node limit, 11 unresolved boxes.

Coupled v14c search:

- certified: no;
- total nodes: 500;
- total runtime: 100.27 s;
- side 0: 250 nodes, node limit, 13 unresolved boxes;
- side 1: 250 nodes, node limit, 9 unresolved boxes.

### 480 observations

Grouped v14b-style search:

- certified: no;
- total nodes: 464;
- total runtime: 22.55 s;
- side 0: 214 nodes, resolution limit, 10 unresolved boxes;
- side 1: 250 nodes, node limit, 9 unresolved boxes.

Coupled v14c search:

- certified: no;
- total nodes: 500;
- total runtime: 105.56 s;
- side 0: 250 nodes, resolution limit, 10 unresolved boxes;
- side 1: 250 nodes, node limit, 9 unresolved boxes.

## Interpretation

v14c is a **numerical-bound success but a certificate-closure failure**.

The result establishes two things simultaneously:

1. the v14a/v14b separate likelihood enclosure was materially loose because it ignored shared parameter dependence;
2. that looseness is not the dominant remaining reason the bounded branch-and-bound search fails to certify these scenarios.

The coupled method reduced direct-reference slack dramatically, including minimum slack from 25.90 to 5.16 log units, yet did not reduce the unresolved search enough to achieve a certificate. Its interval-gradient work also made the tested search roughly four to five times slower.

Do not respond by lowering arithmetic precision, increasing alpha, widening the certified cone, accepting a local optimizer, or simply raising the node budget until the search happens to terminate. Those changes would either weaken validity or obscure the actual bottleneck.

## Next checkpoint

Instrument the branch-and-bound search before designing another numerical bound.

For each visited box, record which condition prunes it:

1. entirely inside the target halfspace;
2. outside the common confidence sequence by the common-likelihood cutoff;
3. rejected by the cone e-process;
4. split and continued;
5. unresolved at the resolution limit;
6. left pending at the node limit.

For the final unresolved boxes, record widths, dimensions selected for splitting, common-likelihood margin, old grouped cone-e margin, coupled cone-e margin, and dense/high-precision diagnostic evidence where feasible.

This will distinguish among at least four different failure modes:

- common nuisance box/CS too broad;
- directional e-process evidence genuinely insufficient;
- interval bounds still too loose locally;
- branch-selection / box-splitting policy wasting nodes.

Only after this attribution should the next certificate change be chosen.

## Provenance

- workflow: `Science S1 Coupled Continuous Bound v14c`;
- run: `32038675988`;
- job: `95413986202`;
- exact benchmark head: `0fa9fb93ebd0cabc5fafb57044cfb045febab4b2`;
- artifact: `9291544853`, `s1-coupled-continuous-bound-v14c`;
- artifact ZIP SHA256: `6913f6d8156519d7475da067cfbd5b2d5ffcf8bcff0e817bb3d53b1046fe275f`;
- complete exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. It does not validate the linear preference model, synthetic feature basis, transfer to real people, compatibility, relationship formation, or long-term relationship quality.