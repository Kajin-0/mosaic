# S1 grouped continuous runtime benchmark v14b

## Question

Can the continuous v14 interval certificate be accelerated materially without changing its confidence logic, outward numerical bounds, branch order, or pruning decisions?

v14a established that the first continuous kernel was numerically conservative on the tested reference points but computationally unusable: a small validation benchmark took about 1,523 seconds and the branch-and-bound search still failed to close its aligned scenarios within the bounded search budget.

v14b changes **evaluation strategy only**. Repeated observations at the same controlled feature vector are collapsed into exact accept/reject counts. Score intervals are then evaluated once per unique feature/rotation and multiplied by integer counts using directed `Decimal` rounding.

## Frozen mathematics

The following are unchanged from v14a:

- 60-digit directed `Decimal` arithmetic;
- exact `Fraction` representation of stored binary floating-point feature values;
- common confidence allocation `alpha_0=0.005`;
- cone-exclusion allocation `alpha_c=0.045`;
- total confidence budget at most `0.05`;
- exact conservative cone slope `tan(delta_cert)=1/2`, i.e. `delta_cert≈26.565° < 27°`;
- 11 rotated outside-cone alternatives;
- nuisance-box construction;
- branch order and box splitting;
- null-likelihood and cone-e pruning criteria.

Thus a grouped/raw difference is a computational difference, not a different statistical certificate.

## Bound-equivalence check

The grouped implementation was checked on four randomized parameter boxes using a `3 x 3 x 3` point grid, for 108 point evaluations over 96 observations and 12 unique controlled feature groups.

Results:

- grouped likelihood-enclosure violations: **0**;
- grouped cone lower-bound violations: **0**.

The grouped code preserves outward rounding under integer multiplication: lower log-probability bounds are multiplied with floor rounding, upper bounds with ceiling rounding, and the final sums retain the corresponding directed rounding.

## Runtime comparison

The benchmark fixed a budget of 40 branch nodes per cone side and `min_width=0.05`.

| scenario | observations | raw time | grouped time | speedup |
|---|---:|---:|---:|---:|
| aligned strong signal | 240 | 38.572 s | 3.689 s | **10.46x** |
| aligned strong signal | 480 | 80.978 s | 3.904 s | **20.74x** |
| combined | — | 119.550 s | 7.593 s | **15.74x** |

The larger speedup at 480 observations is expected: the raw method scales with the number of observations while the grouped method evaluates only the 12 unique controlled feature vectors per rotation.

## Search-equivalence result

The raw and grouped searches reached the **same branch-and-bound states** under the frozen node budget:

### 240 observations

- side 0: raw and grouped both hit `node_limit` after 40 nodes with 5 unresolved boxes;
- side 1: raw and grouped both hit `node_limit` after 40 nodes with 7 unresolved boxes.

### 480 observations

- side 0: raw and grouped both hit `node_limit` after 40 nodes with 7 unresolved boxes;
- side 1: raw and grouped both hit `node_limit` after 40 nodes with 5 unresolved boxes.

This is strong evidence that the speedup came from sufficient-statistic reuse rather than silently changing the mathematical search.

## Conclusion

**Promote grouped likelihood evaluation as the continuous-v14 implementation default.** It preserves the tested one-sided bounds and gives an order-of-magnitude runtime reduction.

However, v14b does **not** solve the central certificate-power problem. The same unresolved boxes remain. v14a already showed a large boxwise cone-e lower-bound slack (minimum observed slack about 23.10 log units), so simply spending the 15.7x speedup on a much larger node budget is not the best next scientific move.

The next checkpoint should tighten the continuous cone-e lower bound itself while preserving one-sided safety. In particular, the existing bound independently encloses rotated-alternative and null log likelihoods before subtraction, losing their strong dependence on the same candidate parameter `theta`. A preferable v14c route is a **coupled log-likelihood-ratio lower bound**:

1. evaluate the rotated-vs-null log-likelihood ratio at a box center with high precision;
2. bound each component of its gradient over the entire parameter box using score intervals and monotonic logistic probabilities;
3. apply the mean-value theorem to obtain a rigorous lower bound over the box;
4. retain directed outward arithmetic and validate the new ratio bound against 120-digit direct references;
5. compare pruning/closure against the grouped v14b baseline under identical alpha, cone, node budget, and branch order.

This directly attacks the dependency slack rather than relaxing precision or confidence.

Do **not** reduce arithmetic precision, widen the certified cone, relax alpha, or accept a local optimizer as a substitute for a global upper/lower certificate.

## Provenance

- workflow: `Science S1 Grouped Continuous Runtime v14b`
- run: `32037967195`
- job: `95412029071`
- exact benchmark head: `825a62d7ecaf05b9a7093c318fb3bb27a105f77c`
- artifact: `9291327587`, `s1-grouped-continuous-runtime-v14b`
- artifact ZIP SHA256: `df1be0324fbe2e39878da8cc19294eaf10dd6ba32735ec0b292d33aadf830831`
- JSON SHA256: `8acbb7f8472bf899480ef68e9be62ff99b7ead315fbe17ebc34139706f6d4b1b`
- JSON size: `3,443` bytes
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed

## Scope

This remains a synthetic, correctly specified 2-D-slope logistic numerical-method benchmark. It does not validate the underlying human preference model, the synthetic feature basis, transfer to real profiles, compatibility, or relationship outcomes.
