# S1 continuous-bound method validation v14a

## Question

Can the first continuous S1 confidence-geometry kernel provide one-sided numerical bounds that are safe enough to support a future anytime-valid directional certificate?

This checkpoint is **numerical-method validation**, not a sequential operating-characteristic or power study.

The v14 construction splits the total 5% confidence budget:

- common predictable-numerator confidence sequence: `alpha_0 = 0.005`, used to bound nuisance intercept and slope magnitude;
- candidate-specific rotated cone-cover e-process: `alpha_c = 0.045`, used for directional exclusion;
- union-bound total: `alpha_0 + alpha_c = 0.05`.

The current continuous certificate uses 60-digit `Decimal` interval arithmetic with exact `Fraction` representations of stored binary floating-point feature values. Transcendental operations are bounded outward at each monotone step. The certified directional wedge uses the exact rational slope `tan(delta_cert)=1/2`, so `delta_cert=atan(1/2)≈26.565°`, deliberately narrower than the nominal 27° target and therefore conservative.

## Adversarial validation design

The deterministic harness used:

- 8 randomized 3-D parameter boxes;
- a `3 x 3 x 3` interior grid = 27 points per box;
- 216 parameter points total;
- four likelihood rotations per point: `0°, +30°, -60°, +120°`;
- 120-digit direct-reference likelihood calculations;
- an independent direct cone-cover log-e calculation at every point;
- four bounded full-certificate scenarios using at most 250 branch-and-bound nodes per cone side and minimum box width `0.05`.

Any likelihood enclosure failure or cone-e lower-bound violation raises an exception and fails the workflow.

## Bound-validation result

The one-sided bounds passed every adversarial point check:

- likelihood-enclosure violations: **0**;
- cone-cover e-value lower-bound violations: **0**;
- point evaluations: **216**;
- likelihood rotations per point: **4**;
- total rotated likelihood enclosure checks: **864**;
- minimum observed direct-cone minus certified-lower-bound slack: **23.0957976951 log units**.

The large positive cone-e slack shows that the current boxwise lower bound is safe but quite loose. That matters for computational efficiency and certificate power.

## Full-certificate scenarios

Dense diagnostic grids found **zero outside-cone survivors** under the exact split-alpha criteria in every scenario, but the branch-and-bound implementation did not prove a positive certificate within its bounded search budget:

| scenario | observations | dense outside survivors | result | limiting behavior |
|---|---:|---:|---|---|
| aligned strong signal | 240 | 0 | not certified | both sides hit 250-node limit, 11 boxes unresolved each |
| aligned strong signal | 480 | 0 | not certified | one side hit resolution limit after 204 nodes; other hit 250-node limit |
| off-axis signal | 240 | 0 | not certified | both sides hit 250-node limit |
| weak signal | 240 | 0 | not certified | both sides hit 250-node limit |

This is a useful separation of concerns:

1. **No anti-conservative numerical failure was detected.** The outward interval machinery survived the direct high-precision checks.
2. **The current bounds are too loose for efficient proof.** Dense diagnostics say no tested outside survivor remains, yet branch-and-bound cannot eliminate every box within the bounded search.
3. **No continuous stopping claim is established yet.** Failure to certify is conservative and does not imply an outside survivor exists.

## Runtime result

The method benchmark step ran from approximately `05:09:40.86Z` to `05:35:04.26Z`, about **1,523.4 seconds = 25 minutes 23 seconds**.

This is computationally unacceptable for a per-response production certificate. The cause is structural: every branch node recomputes 60-digit likelihood intervals across every raw observation for the candidate null and each of 11 rotated alternatives.

Do **not** solve this by reducing arithmetic precision, relaxing the confidence thresholds, or accepting approximate local optima.

## Next checkpoint: grouped sufficient-statistic bounds

For the current 12-point controlled candidate bank, repeated observations at the same feature vector can be grouped exactly by:

- feature vector;
- accept count;
- reject count.

For each parameter box and rotation, the score interval then needs to be evaluated once per unique feature vector rather than once per raw observation. The accepted and rejected log-probability interval bounds can be multiplied by their integer counts with directed rounding and summed.

For 240–480 observations on a 12-point bank, this should reduce the dominant per-likelihood work by roughly one to two orders of magnitude while preserving the same mathematical bound. Rotated design vectors should also be precomputed once for every feature/offset pair.

The grouped implementation must be validated against the same 120-digit direct references before any speedup is accepted.

The next checkpoint should therefore measure two independent endpoints:

1. **bound equivalence/safety:** zero high-precision enclosure and cone-lower-bound violations;
2. **runtime:** substantial reduction from the v14a 1,523-second benchmark while keeping the same alpha split, precision, rational cone, scenarios, node budget, and search widths.

Only after the continuous certificate is both sound and computationally usable should S1 proceed to fresh-seed sequential operating-characteristic studies.

## Provenance

- workflow: `Science S1 Continuous Bound Validation v14a`
- run: `31996869868`
- job: `95289981102`
- exact benchmark head: `0e9f3543c2128e8bec33589d4c0af483417b81b2`
- artifact: `9277581585`, `s1-continuous-bound-validation-v14a`
- artifact ZIP SHA256: `3e6ee8eab2a4ae5c0819ac4259089bf8858ee92b70d40464fdce20bffa701d7f`
- JSON SHA256: `de04ad2d259ff237be26d24ae1671fb8388e3c2fbf41919f351bf787dd680706`
- JSON size: `3,154` bytes
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed

## Scope

This remains a synthetic, correctly specified 2-D-slope logistic method test. It does not validate the linear preference model, the synthetic feature basis, human preference transfer, compatibility, or relationship outcomes.