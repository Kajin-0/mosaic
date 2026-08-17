# S1 unresolved-box attribution benchmark v14d

## Question

Why does the continuous S1 branch-and-bound certificate remain unresolved after v14b grouping and the materially tighter v14c coupled likelihood-ratio bound?

This checkpoint is attribution only. It replays the same aligned 240- and 480-observation scenarios with the same:

- confidence construction;
- `alpha_0=0.005` common nuisance-box e-process;
- `alpha_c=0.045` candidate-specific cone e-process;
- exact rational cone `tan(delta_cert)=1/2`;
- 60-digit directed arithmetic;
- nuisance box;
- 250-node-per-side budget;
- minimum width `0.05`;
- DFS branch order and largest-width split policy.

No statistical threshold or certificate semantics are changed.

## Instrumentation

Every visited box is classified as:

1. entirely inside the target halfspace (`geometry_prune`);
2. excluded by the common confidence likelihood cutoff (`common_prune`);
3. excluded by the directional cone e-process (`cone_prune`);
4. split and continued (`split`);
5. unresolved at the minimum width (`resolution_unresolved`);
6. left pending when the node budget is exhausted.

Each final unresolved/pending box also records:

- parameter intervals and widths;
- largest-width split dimension;
- halfspace minimum;
- common-confidence bound survival margin;
- v14b grouped cone-bound survival margin;
- v14c coupled cone-bound survival margin;
- a 120-digit direct probe at the slope corner that maximally violates the target halfspace, with midpoint intercept;
- the exact direct common-confidence margin;
- the exact direct cone-e survival margin;
- whether that probe is a directly verified outside-cone point surviving both filters.

The direct probe is diagnostic, not an exhaustive proof that a box does or does not contain another survivor.

## Attribution counts

### Aligned 240 observations

#### Side 0

Grouped v14b-style bound:

- nodes: 250, node limit;
- geometry prunes: 47;
- common-confidence prunes: 73;
- cone-e prunes: **0**;
- splits: 130;
- final boxes: 11;
- direct probe joint survivors: **1**.

Coupled v14c bound:

- nodes: 250, node limit;
- geometry prunes: 47;
- common-confidence prunes: 71;
- cone-e prunes: **1**;
- splits: 131;
- final boxes: 13;
- direct probe joint survivors: **1**.

The directly surviving probe is the same physical frontier region under both methods:

```text
theta ~= [0.67584, 1.25355, -0.69181]
halfspace value ~= -0.06503
common direct survival margin ~= +9.8953 log units
cone direct survival margin ~= +4.0638 log units
```

This point lies just outside the certified cone and genuinely survives both current confidence filters. Therefore **the aligned-240 side-0 certificate is mathematically unavailable under the current confidence construction**, not merely hidden by numerical looseness or poor search order. Even an exact optimizer would have to report failure for this fixed center and evidence.

#### Side 1

Grouped:

- geometry prunes: 11;
- common prunes: 109;
- cone prunes: 0;
- splits: 130;
- final boxes: 11;
- direct probe joint survivors: 0.

Coupled:

- geometry prunes: 15;
- common prunes: 86;
- cone prunes: **20**;
- splits: 129;
- final boxes: 9;
- direct probe joint survivors: 0.

This is the clearest demonstration that v14c's tighter directional bound changes the search qualitatively: it converts 20 visited boxes into genuine cone-e prunes where the old grouped bound produced none.

## Aligned 480 observations

### Side 0

Grouped:

- nodes: 214, resolution limit;
- geometry prunes: 40;
- common prunes: 62;
- cone prunes: 0;
- splits: 111;
- one resolution-unresolved box;
- final boxes including pending stack: 10;
- direct probe joint survivors: 0.

Coupled:

- nodes: 250, resolution limit;
- geometry prunes: 49;
- common prunes: 57;
- cone prunes: **14**;
- splits: 129;
- one resolution-unresolved box;
- final boxes including pending stack: 10;
- direct probe joint survivors: 0.

The coupled resolution-blocking box is already very small: maximum parameter width about **0.04044**, below the frozen `0.05` resolution floor. Its conservative survival margins are only:

```text
common bound survival margin ~= +2.1877 log units
coupled cone-bound survival margin ~= +0.5965 log units
```

but the high-precision halfspace-violating probe is rejected by both filters:

```text
common direct margin ~= -5.6890 log units
cone direct survival margin ~= -1.2496 log units
```

So the exact probe is already outside the retained confidence region while the box enclosure remains just too loose to prove it. This is a localized numerical-resolution obstruction, not evidence that the probe survives.

### Side 1

Grouped:

- nodes: 250, node limit;
- geometry prunes: 17;
- common prunes: 104;
- cone prunes: 0;
- splits: 129;
- final boxes: 9;
- direct probe joint survivors: 0.

Coupled:

- nodes: 250, node limit;
- geometry prunes: 16;
- common prunes: 84;
- cone prunes: **21**;
- splits: 129;
- final boxes: 9;
- direct probe joint survivors: 0.

Again the coupled bound materially transfers work from the common-CS route into directional cone pruning without changing validity.

## Main conclusions

### 1. There are two different failure regimes

The continuous certificate should no longer be described as having one generic “branch-and-bound problem.”

At **240 observations**, at least one outside-cone parameter is directly verified to survive both current confidence filters. For that path, the failure is genuine statistical uncertainty. Numerical optimization cannot legitimately turn it into a certificate.

At **480 observations**, no final frontier probe survives both filters, and the side-0 blocking box is tiny with only a 0.596-log-unit coupled cone-bound gap. This regime is consistent with numerical/search inefficiency rather than clearly insufficient evidence.

### 2. The coupled bound is scientifically useful despite its runtime cost

The old grouped cone bound produced zero visited cone prunes in all four searches. The coupled bound produced:

- 1 cone prune at aligned-240 side 0;
- **20** at aligned-240 side 1;
- **14** at aligned-480 side 0;
- **21** at aligned-480 side 1.

That is direct evidence that preserving alternative/null dependence exposes directional exclusion that the old bound cannot see at practical box sizes.

### 3. Common-confidence pruning remains the largest single prune class

Across all searches, the common nuisance confidence sequence removes 57–109 visited boxes. Its role is therefore substantial, but the v14d evidence does not justify changing the `0.005/0.045` alpha allocation. Reallocating alpha would change the statistical procedure and requires a separate prospective design, not post-hoc tuning on these scenarios.

### 4. Search policy and local resolution are now legitimate numerical targets

The 480-observation frontier contains no directly surviving probes, while multiple pending boxes are already prunable if/when visited and the resolution-blocking box is close to cone exclusion. The current depth-first, largest-absolute-width splitter is therefore not established as computationally efficient.

This motivates a numerical search-policy checkpoint that leaves every confidence threshold and bound unchanged.

## Next checkpoint: v14e certified search allocation

The next experiment should change **only branch-and-bound search allocation**, not the statistical certificate.

A defensible candidate is a deterministic child-preview / best-first policy:

1. preserve the v14c coupled bound and all confidence thresholds;
2. for an unresolved box, consider each legal split dimension;
3. evaluate the two children with the same safe geometry/common/cone pruning predicates;
4. choose the split that maximizes immediate certified pruning and, secondarily, minimizes the worst remaining conservative survival margin;
5. maintain a priority queue over unresolved boxes so near-prunable boxes are completed before spending the entire budget on a single depth-first branch;
6. keep the same 250-node budget for the primary comparison.

The primary v14e endpoints should be:

- certificate status under the same budget;
- nodes required when both policies certify;
- number of unresolved boxes at budget exhaustion;
- preservation of every pruning inequality and exact certificate semantics;
- confirmation that aligned-240 side 0 still **does not certify**, because v14d directly found a true retained outside-cone point. If a new search policy certifies that case without changing the statistical construction, it is a bug.

The aligned-240 side-0 survivor is therefore a useful negative-control invariant for v14e.

Do not lower precision, relax alpha, widen the cone, or substitute a local optimizer. Do not use a larger node budget as the primary experimental change.

## Provenance

- workflow: `Science S1 Unresolved Box Attribution v14d`;
- run: `32039824342`;
- job: `95417036144`;
- exact benchmark head: `34ba694b0beff3fc94634d3cb29710803d13a0b6`;
- artifact: `9291792563`, `s1-unresolved-box-attribution-v14d`;
- artifact ZIP SHA256: `229d88f778c2494cf0ceed7920bce9724cf8629e0cfa874557f2d0ede259fd16`;
- JSON SHA256: `8b4748d58c7b4b23a69f328f2f27dd54e01566b61fb998dcca7e9ff3a9448e12`;
- JSON size: `120,507` bytes;
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. The direct retained parameter at 240 observations is evidence about this confidence construction under this synthetic path, not about human attraction, synthetic-to-real transfer, compatibility, relationship formation, or long-term relationship quality.