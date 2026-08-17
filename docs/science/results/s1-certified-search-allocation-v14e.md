# S1 certified search-allocation benchmark v14e

## Question

Can branch-and-bound allocation alone materially improve the continuous S1 certificate under the same statistical construction and the same processed-node budget?

v14d separated two regimes: aligned-240 side 0 contains a directly verified retained outside-cone point and therefore cannot certify under the current confidence construction, while the aligned-480 frontiers appeared dominated by numerical/search inefficiency. v14e therefore changes **only search allocation**.

## Frozen statistical and numerical construction

The benchmark preserves:

- the v14c coupled rotated-alternative/null likelihood-ratio bound;
- `alpha_0=0.005` common nuisance-box e-process;
- `alpha_c=0.045` candidate-specific cone e-process;
- exact rational cone `tan(delta_cert)=1/2`;
- 60-digit directed arithmetic;
- the same finite nuisance box;
- node budget: 250 processed boxes per side;
- minimum width: 0.05.

The aligned-240 side-0 path is a mandatory negative control. v14d directly found an outside-cone parameter surviving both confidence filters there. If a search-only change certifies it, the search implementation is wrong.

## Candidate policy

For every unresolved box:

1. preview every legal split dimension;
2. evaluate both children with the same certified geometry/common/cone predicates;
3. prefer the dimension yielding the most immediate certified child prunes;
4. break ties by minimizing the worst and then total unresolved conservative survival distance;
5. place unresolved children in a best-first priority queue, with near-prunable boxes processed first.

Floating-point scores affect processing order only. All prune/certificate decisions continue to use the directed safe bounds.

Preview evaluations are reported separately; they are not treated as free work.

## Results

### Aligned 240 side 0 — negative control

v14d reference:

- 250 processed nodes;
- node limit;
- 13 unresolved frontier boxes.

v14e:

- **not certified**, as required;
- 250 processed nodes;
- 768 child-preview evaluations;
- node limit;
- **7 unresolved boxes**;
- elapsed time: **222.62 s**;
- selected split dimensions: intercept 48, slope-1 46, slope-2 34.

The search substantially reduced the frontier but correctly could not remove genuine statistical uncertainty.

### Aligned 480 side 0

v14d reference:

- 250 processed nodes;
- resolution limit;
- 10 unresolved boxes.

v14e:

- not certified;
- 250 processed nodes;
- 756 child-preview evaluations;
- node limit rather than premature resolution-limit termination;
- **3 unresolved boxes**;
- 96 common-confidence prunes;
- 22 cone-e prunes;
- 6 geometry prunes;
- elapsed time: **252.41 s**;
- selected dimensions: intercept 52, slope-1 38, slope-2 36.

This is a substantial frontier reduction, `10 -> 3`, and confirms that the v14d fixed DFS/largest-width allocation was inefficient. It still does not produce a certificate under the same 250-node budget.

### Aligned 480 side 1

v14d reference:

- 250 processed nodes;
- node limit;
- 9 unresolved boxes.

v14e:

- not certified;
- 250 processed nodes;
- 762 child-preview evaluations;
- node limit;
- **5 unresolved boxes**;
- 96 common-confidence prunes;
- 13 cone-e prunes;
- 14 geometry prunes;
- elapsed time: **249.95 s**;
- selected dimensions: intercept 49, slope-1 37, slope-2 41.

Again the search tree improves but does not close.

## Interpretation

v14e establishes that **search allocation matters**, but this exact exhaustive-preview policy is not promotable.

Positive result:

- unresolved frontier size improved in every case: `13 -> 7`, `10 -> 3`, and `9 -> 5`;
- the known-impossible negative control remained uncertified;
- aligned-480 side 0 avoided the earlier early resolution-limit termination;
- the chosen dimensions are not dominated by raw absolute width, confirming that confidence-bound sensitivity contains useful allocation information.

Negative result:

- zero cases certified within the same 250 processed nodes;
- the three cases required **2,286** child-preview evaluations in addition to 750 processed nodes;
- benchmark compute time was roughly **725 s = 12.1 min** across the three cases;
- each individual case took about 223–252 seconds.

The result therefore rejects exhaustive child preview as a practical production search policy. It spends too much certified-bound work to obtain a smaller but still nonempty frontier.

## Next checkpoint: cheap sensitivity-guided splitting

v14e shows that better split dimensions are useful, but evaluating every possible child is too expensive. The next checkpoint should recover most of the allocation signal from quantities already computed inside the v14c coupled bound.

The v14c mean-value lower bound has the form

```text
center_ratio_lower - sum_j half_width_j * gradient_abs_upper_j.
```

The per-axis terms

```text
penalty_j = half_width_j * gradient_abs_upper_j
```

already measure how much each parameter dimension contributes to conservative ratio-bound looseness. A cheap splitter can expose these diagnostics and split the dimension with the largest relevant penalty rather than evaluating six preview children.

The next prospective comparison should:

- keep the exact v14c statistical procedure and all thresholds fixed;
- use the same 250 processed-node budget and 0.05 resolution floor;
- preserve the aligned-240 side-0 negative-control invariant;
- compare the current DFS/largest-width reference against a sensitivity-guided splitter/frontier policy;
- report processed nodes, unresolved boxes, cone/common/geometry prunes, runtime, and any extra diagnostic computation;
- avoid changing alpha allocation or simply increasing node budget.

A useful implementation should be materially cheaper than v14e while retaining its frontier improvement. If it cannot do that, search-policy tuning should stop and the continuous construction should move to a different certified representation.

## Provenance

- workflow: `Science S1 Certified Search Allocation v14e`;
- run: `32040635064`;
- job: `95419196384`;
- exact benchmark head: `e5a34364a9ebdd91a0366a4b660be06efa497a57`;
- artifact: `9292006352`, `s1-certified-search-allocation-v14e`;
- artifact ZIP SHA256: `3282261ff88e34b5bf3045a4c0371763a38ebd42c16768c1878b37ef76a49982`;
- JSON SHA256: `c9ad991253934b80172b7caa06b61a37511aa941b75e6902e4beb9c7e3f48858`;
- JSON size: `2,826` bytes;
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. It does not validate the linear preference model, synthetic feature basis, synthetic-to-real transfer, compatibility, relationship formation, or long-term relationship quality.