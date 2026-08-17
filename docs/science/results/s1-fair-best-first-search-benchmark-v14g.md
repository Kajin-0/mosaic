# S1 fair best-first search benchmark v14g

## Question

Does best-first frontier order materially improve the continuous S1 certificate when every certified bound evaluation is charged against the same finite work budget?

v14e showed a large frontier reduction, but it granted the candidate 2,286 extra child-preview evaluations in addition to 750 processed nodes. v14f removed that advantage and showed that sensitivity-guided split axes alone provide only a modest benefit. v14g therefore isolates frontier order under a fair accounting rule.

## Frozen construction

v14g preserves:

- the exact v14c coupled likelihood-ratio confidence bound;
- the v14f sensitivity-guided split dimension;
- `alpha_0=0.005` common nuisance-box e-process;
- `alpha_c=0.045` candidate-specific cone e-process;
- exact rational cone `tan(delta_cert)=1/2`;
- 60-digit directed arithmetic;
- the same finite nuisance box;
- minimum width `0.05`.

The only substantive change from v14f is frontier order and evaluation caching.

The aligned-240 side-0 case remains the mandatory negative control from v14d: a 120-digit direct parameter point is known to survive both confidence filters outside the target cone. A search-only method must not certify that case.

## Fair work accounting

Each box is evaluated once with the same certified predicates and cached.

When an unresolved box is split:

1. both children are evaluated immediately;
2. each child evaluation counts against the finite evaluation budget;
3. pruned children disappear;
4. unresolved children are cached in the frontier;
5. no child preview is free.

The evaluation budget is 250. Since a split requires two child evaluations, the candidate stops at 249 when only one unit of budget remains.

The best-first priority is the smaller of the certified common-confidence and cone-e survival margins, with box width as a secondary ordering key. Priority values affect processing order only; all pruning and certification decisions still use the directed safe bounds.

## Results

### Aligned 240 side 0 — mandatory negative control

v14f DFS reference:

- 250 evaluations;
- 11 unresolved boxes;
- node limit;
- 44.63 s.

v14g fair best-first:

- **not certified**, as required;
- 249 evaluations;
- **2 unresolved boxes**;
- 2 active, 0 resolution-frozen;
- evaluation-budget termination;
- common-confidence prunes: 91;
- cone-e prunes: 1;
- geometry prunes: 31;
- 124 splits;
- elapsed: **44.93 s**.

This is a large frontier reduction, `11 -> 2`, at essentially identical certified-bound work and runtime, while preserving the known-impossible negative control.

### Aligned 480 side 0

v14f DFS reference:

- 250 evaluations;
- 9 unresolved boxes;
- node limit;
- 46.09 s.

v14g fair best-first:

- not certified;
- 249 evaluations;
- **5 unresolved boxes**;
- 5 active, 0 resolution-frozen;
- evaluation-budget termination;
- common-confidence prunes: 98;
- cone-e prunes: 14;
- geometry prunes: 8;
- 124 splits;
- elapsed: **51.14 s**.

The frontier improves `9 -> 5`, but the certificate remains open.

### Aligned 480 side 1

v14f DFS reference:

- 250 evaluations;
- 7 unresolved boxes;
- node limit;
- 54.40 s.

v14g fair best-first:

- not certified;
- 249 evaluations;
- **4 unresolved boxes**;
- 4 active, 0 resolution-frozen;
- evaluation-budget termination;
- common-confidence prunes: 95;
- cone-e prunes: 11;
- geometry prunes: 15;
- 124 splits;
- elapsed: **51.15 s**.

The frontier improves `7 -> 4`, but again does not close.

## Interpretation

v14g gives the cleanest search-allocation result in the v14 sequence:

1. **frontier order matters strongly** — especially on the 240 negative control, where unresolved boxes fall from 11 to 2 under essentially equal charged work;
2. the improvement is not an artifact of free child previews, because every generated child is evaluated exactly once and charged;
3. runtime remains practical and comparable to v14f;
4. nevertheless **neither 480-observation side certifies under the same 250-evaluation budget**;
5. therefore search allocation is not the remaining scientific/numerical bottleneck sufficient to justify further policy tuning.

The search-policy branch should now be considered closed for the current certificate architecture. More hand-tuned frontier scores, split heuristics, or larger primary node budgets would be post-hoc optimization against these same scenarios.

## Next checkpoint: common confidence-region representation

v14d–v14g collectively point upstream.

The common nuisance confidence sequence is the largest prune class in every tested search, and the current implementation uses it first to create one broad axis-aligned initial nuisance box. That box is only an outer approximation to the true convex common-confidence superlevel set. Branch-and-bound then spends substantial work rediscovering that curved constraint box by box.

The next checkpoint should therefore keep the **same common e-process and same alpha allocation** but improve only its geometric representation.

A defensible route is certified coordinate-wise tightening of the initial nuisance box:

1. preserve the common likelihood cutoff exactly;
2. for each of intercept, `beta_x`, and `beta_y`, compute rigorous lower/upper coordinate bounds for the common-confidence set rather than using the current coarse analytic box alone;
3. the optimization/bounding procedure must be one-sided safe: the tightened interval must still contain every parameter satisfying the common-confidence likelihood constraint;
4. benchmark the volume/width reduction and then replay the frozen v14c/v14g directional search from the tighter certified outer box;
5. keep the 240 side-0 direct survivor as a negative-control invariant;
6. do **not** change `alpha_0/alpha_c`, arithmetic precision, cone geometry, numerator, or directional e-process in the same checkpoint.

Because logistic log-likelihood is concave and the retained common-confidence region is a convex superlevel set, rigorous coordinate extrema can in principle be formulated as convex optimization problems. However, an ordinary numerical optimizer is not sufficient for certification: any finite bounds used operationally must be conservative outer bounds, with solver/duality/interval error controlled in the safe direction.

If certified common-region tightening materially reduces the search burden, it becomes the next continuous certificate improvement. If it does not, the current v14 architecture should be reconsidered rather than tuned further.

## Provenance

- workflow: `Science S1 Fair Best First v14g`;
- run: `32042363933`;
- job: `95423839819`;
- exact benchmark head: `cc2d71a2d34328a31bd9d03d2c29d5d139159c78`;
- artifact: `9292214551`, `s1-fair-best-first-search-v14g`;
- artifact ZIP SHA256: `fd0e83adc84d116d47a6b196cb59e739b4f45497f4dd9f259d2842c2466d60a5`;
- JSON SHA256: `b7164e537e242c6e04d1e43711696a855d5352cf047a82ec2bae58aa7dd49acd`;
- JSON size: `3,074` bytes;
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. It does not validate the linear preference model, synthetic feature basis, synthetic-to-real transfer, compatibility, relationship formation, or long-term relationship quality.