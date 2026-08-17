# S1 exact common-polytope benchmark v14h

## Question

Can the common-confidence nuisance region be represented more tightly without changing the common e-process, alpha allocation, directional e-process, cone geometry, numerical precision, or directional search policy?

The previous continuous implementation converted the 0.5% common confidence sequence into one broad axis-aligned nuisance box. v14h strengthens only that outer geometry.

## Exact necessary score constraints

Let the common confidence cutoff be `c < 0`. For a repeated feature vector with logistic score `z`, every Bernoulli log-likelihood contribution is nonpositive. Therefore any parameter with total log likelihood at least `c` must have each grouped contribution sum individually at least `c`.

For accepted responses,

```text
n_accept * log(sigmoid(z)) >= c
```

and because `log(sigmoid(z)) <= z`, every retained parameter necessarily satisfies

```text
z >= c / n_accept.
```

For rejected responses,

```text
n_reject * log(sigmoid(-z)) >= c
```

and `log(sigmoid(-z)) <= -z` gives

```text
z <= -c / n_reject.
```

These are necessary, not sufficient, conditions. They therefore define a safe outer approximation to the common confidence set.

v14h uses every observed feature group, including one-sided groups, plus the already-certified coarse nuisance-box limits. In three parameters `(intercept, beta_x, beta_y)`, all constraints are exact rational halfspaces. The bounded polytope is solved by exact `Fraction` arithmetic: enumerate every intersection of three independent boundary planes, retain feasible vertices, and take exact coordinate minima/maxima. No numerical optimizer or solver tolerance is involved.

If vertex recovery ever fails, the implementation falls back to the existing coarse box rather than constructing an empty confidence region.

## Safety checks

The exact-head tests establish:

- exact coordinate extrema on a known cube-plus-halfspace polytope;
- correct one-sided accepted/rejected score constraints;
- retained zero parameter remains inside the tightened outer box in a balanced fixture.

The prospective benchmark additionally checked a 125-point high-precision parameter grid for each aligned scenario.

### Aligned 240

- direct retained grid points: **72**;
- retained points excluded by tightened box: **0**.

The v14d direct retained outside-cone negative-control point remained inside the tightened common box:

```text
theta = [0.6758436374, 1.2535511059, -0.6918084478]
direct common survival margin = +9.8953440529 log units
contained in tightened box = true
```

### Aligned 480

- direct retained grid points: **77**;
- retained points excluded by tightened box: **0**.

No empirical safety failure was detected. The analytical halfspace implication is the validity argument; the direct grids are independent implementation checks.

## Common-box reduction

### Aligned 240

- halfspaces: **30**;
- feasible exact vertices: **28**;
- axis width ratios, tightened/coarse:
  - intercept: **0.76590**;
  - beta_x: **0.87047**;
  - beta_y: **0.71035**;
- volume ratio: **0.47358**.

Thus the exact all-score polytope coordinate box occupies only **47.36%** of the old coarse-box volume.

### Aligned 480

- halfspaces: **30**;
- feasible exact vertices: **38**;
- axis width ratios:
  - intercept: **0.87035**;
  - beta_x: **0.81044**;
  - beta_y: **0.88984**;
- volume ratio: **0.62767**.

The tightened coordinate box occupies **62.77%** of the old volume.

## Directional replay

The directional replay freezes the v14g fair cached best-first search, v14f sensitivity split rule, v14c coupled directional bound, rational cone, 60-digit arithmetic, and 250-evaluation budget. Only the initial common outer box changes.

### 240 side 0 negative control

v14g reference:

- 249 evaluations;
- 2 unresolved boxes;
- not certified.

v14h:

- 249 evaluations;
- **6 unresolved boxes**;
- not certified, as required;
- elapsed 48.85 s.

The smaller bounding box is not monotonically better under the fixed best-first priority geometry. This is an important negative result rather than a validity defect.

### 480 side 0

v14g reference:

- 5 unresolved boxes.

v14h:

- **3 unresolved boxes**;
- not certified;
- elapsed 48.04 s.

### 480 side 1

v14g reference:

- 4 unresolved boxes.

v14h:

- **3 unresolved boxes**;
- not certified;
- elapsed 53.31 s.

The exact coordinate box improves both 480 frontiers modestly but does not close either certificate.

## Interpretation

v14h establishes that the current coarse nuisance box is materially looser than necessary: exact score implications cut its volume by roughly 37–53% on the tested paths while preserving all checked retained points and the known 240 negative control.

However, reducing the polytope to its coordinate bounding box immediately discards the non-axis-aligned shape information supplied by the 30 halfspaces. The directional search then has to rediscover those same constraints by likelihood bounding. That explains why the geometric improvement is modest and can even interact adversely with best-first ordering on the 240 negative control.

The **axis-aligned bounding-box version of the score-polytope route is therefore not a complete solution**.

## Next checkpoint: v14i active common-polytope pruning

The next checkpoint should retain the same exact necessary score halfspaces throughout the directional branch-and-bound search instead of using them only once to derive a smaller bounding box.

For every axis-aligned search box and every exact common halfspace

```text
a^T theta <= b,
```

compute the exact minimum of `a^T theta` over that box. If the minimum exceeds `b`, the search box has empty intersection with the common score polytope and can be pruned immediately. This is an exact rational feasibility prune.

v14i must keep fixed:

- common e-process and cutoff;
- `alpha_0=0.005`, `alpha_c=0.045`;
- candidate-specific directional e-process;
- rational cone;
- coupled v14c bound;
- sensitivity split rule;
- fair cached best-first frontier order;
- 60-digit arithmetic;
- 250 charged bound-evaluation budget.

The primary comparison should use the original coarse nuisance box plus active polytope constraints, so any gain comes from preserving common-region shape rather than changing starting coordinates.

Required invariants:

- aligned-240 side 0 remains uncertified;
- the known v14d retained outside-cone point satisfies all common-polytope constraints;
- common-polytope pruning is exact and never replaces the nonlinear common likelihood check;
- every generated child remains charged once under the fair-work accounting.

If active polytope pruning materially closes or reduces the 480 frontiers, the exact score-polytope should become part of the continuous common-region representation. If it still fails, the score-linearization family should be closed and the next common-region improvement should use stronger certified nonlinear/tangent outer constraints rather than search-policy tuning or alpha reallocation.

## Provenance

- workflow: `Science S1 Exact Common Polytope v14h`;
- run: `32043584053`;
- job: `95427034166`;
- exact benchmark head: `c5082e3ec163724dc5b631eae1af485a4acf05ec`;
- artifact: `9292430415`, `s1-exact-common-polytope-v14h`;
- artifact ZIP SHA256: `027fb352a2a375b2c27166c3695e5d77ba3996f36c32c92645b1bf800ac12c5e`;
- JSON SHA256: `7910b739088810e269d7c3d3d95240e7297a306bb24a529216b28c9724e36499`;
- JSON size: `6,169` bytes;
- exact-head validation before benchmark: Ruff clean, Ruff format clean, mypy clean, complete engine pytest passed.

## Scope

This remains a synthetic, correctly specified two-slope logistic numerical-method study. It does not validate the linear preference model, synthetic feature basis, synthetic-to-real transfer, compatibility, relationship formation, or long-term relationship quality.