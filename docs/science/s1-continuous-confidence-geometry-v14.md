# S1 continuous confidence geometry v14

## Purpose

v13 establishes a defensible finite-grid route, culminating in the v13j cone-cover numerator and the v13k acquisition boundary. The next problem is not another finite-grid efficiency tweak. It is to remove the angular grid and permit nuisance intercept and slope magnitude without losing anytime-valid coverage.

The central rule remains:

```text
construct a parameter confidence sequence first
        ↓
certify the geometry of the entire retained parameter set
        ↓
stop only if every retained parameter is inside the target directional cone
```

A moving data-dependent angular null is still not treated as fixed.

## Why a naive continuous extension is insufficient

A continuous logistic parameter is

\[
\theta=(b,\beta_x,\beta_y).
\]

A common predictable numerator produces the continuous confidence set

\[
C_t^{(0)}=\{\theta:\ell_t(\theta)>\log Q_t+\log\alpha_0\},
\]

and its running intersection is convex because every logistic log-likelihood superlevel set is convex.

That route is structurally clean, but the common numerator was already less efficient than the v13j candidate-specific cone-cover construction on the finite grid. Conversely, a direct continuous cone-cover ratio that rotates each candidate parameter preserves directional power but can leave nuisance intercept/magnitude weakly controlled or unbounded because the alternatives share those nuisance coordinates.

v14 therefore separates nuisance bounding from directional exclusion.

## Split-alpha hybrid confidence construction

Use two valid fixed-parameter e-process families.

### 1. Common-numerator nuisance confidence sequence

For every fixed continuous `theta`, use a normalized predictable common numerator `Q_t^(0)` independent of candidate `theta`.

Allocate error budget `alpha_0`.

This sequence is used primarily to:

- bound intercept and slope magnitude;
- provide a convex continuous outer set;
- reject grossly incompatible parameter regions.

### 2. Candidate-specific rotated cone-cover confidence sequence

For candidate

\[
\theta=(b,\beta),
\]

define the fixed 11-alternative mixture

\[
Q_t^{(c)}(\theta)
=\frac1{11}\sum_{m\in\mathcal O}L_t(T_m\theta),
\]

with

\[
\mathcal O=\{\pm30,\pm60,\pm90,\pm120,\pm150,180\}^{\circ},
\]

where `T_m` rotates only the slope vector and leaves the intercept and slope norm unchanged.

For every fixed candidate `theta`, `Q_t^(c)(theta)` is a normalized mixture likelihood, so

\[
E_t^{(c)}(\theta)=Q_t^{(c)}(\theta)/L_t(\theta)
\]

is a valid e-process under that fixed candidate parameter.

Allocate error budget `alpha_c`.

### Combined coverage

Use

\[
\alpha_0+\alpha_c\le 0.05.
\]

The operational retained set is the intersection of the two confidence sequences. By a union bound, simultaneous true-parameter coverage is at least `1 - alpha_0 - alpha_c` under correct likelihood specification and predictable acquisition.

The first implementation should use a prespecified split rather than tuning it on benchmark outcomes. A natural conservative starting point is `alpha_0=0.005`, `alpha_c=0.045`: the common sequence only needs enough budget to bound nuisance coordinates, while most of the error budget remains with the directional cone-cover sequence.

## Finite nuisance box without an optimizer

At a fixed time, let the common-numerator log-likelihood cutoff be

\[
c_t=\log Q_t^{(0)}+\log\alpha_0<0.
\]

For one repeated feature vector `x_j`, suppose there are `n_1>0` accepts and `n_0>0` rejects, and define

\[
\eta_j=b+\beta^T x_j.
\]

Because every other log-likelihood contribution is non-positive, any parameter satisfying `ell_t(theta)>c_t` must satisfy the same inequality for the grouped contribution at `x_j`.

The elementary logistic bounds imply

\[
\frac{c_t}{n_1}<\eta_j<\frac{-c_t}{n_0}.
\]

Therefore three affinely independent feature vectors that have both outcomes bound three independent linear scores. Inverting their `3 x 3` design matrix gives a finite axis-aligned box containing the entire common confidence set.

If three such mixed-outcome feature vectors do not yet exist, v14 must return **not certified** rather than inventing a nuisance box.

## Continuous directional cone geometry

Let the reported unit slope direction be `u`, let `v` be its 90-degree rotation, and let target half-angle be `delta<90 degrees`.

The acceptable 2-D directional cone is exactly

\[
(\sin\delta\,u+\cos\delta\,v)^T\beta\ge0,
\]

and

\[
(\sin\delta\,u-\cos\delta\,v)^T\beta\ge0.
\]

Thus the outside-cone region is the union of two linear halfspace violations. The two sides can be certified independently.

The center may be data-dependent because it is used only after the simultaneous parameter confidence set has been constructed.

## Branch-and-bound certificate

Start from the finite nuisance box supplied by the common sequence. For each outside-cone halfspace:

1. prune a box if it lies entirely inside the acceptable halfspace;
2. prune a box if a genuine **upper bound** on its common-numerator log likelihood is below the common confidence cutoff;
3. prune a box if a genuine **lower bound** on its cone-cover log e-value is above the cone-cover rejection threshold;
4. otherwise subdivide the box;
5. certify the side only when every potentially violating box has been pruned.

A node limit, minimum-width limit, or numerical difficulty can only return **not certified**. It can never be converted into a positive certificate.

## Outward likelihood bounds

For a parameter box, each linear score has an exact interval `[eta_min, eta_max]` by interval arithmetic.

Bernoulli-logistic log probabilities are monotone in the score:

- accepted outcome: `log sigmoid(eta)` is increasing;
- rejected outcome: `log(1-sigmoid(eta))` is decreasing.

Therefore endpoint evaluation supplies convergent interval likelihood bounds.

The implementation should use standard-library `Decimal` at high precision and explicitly step outward after correctly rounded `exp`/`ln` evaluation. Linear score intervals should be formed from exact rational representations of the stored binary floating-point feature values. This avoids the anti-conservative failure mode in which an approximate local optimizer or rounded likelihood maximum understates the best surviving outside-cone parameter.

## Cone-cover box lower bound

For candidate box `B`, let

- `UB_L(B)` be an upper bound on the candidate null log likelihood;
- `LB_m(B)` be a lower bound on the log likelihood of rotated alternative `T_m theta` for all `theta in B`.

Then

\[
\log Q_t^{(c)}(\theta)
\ge \max_m LB_m(B)-\log 11,
\]

so every candidate in the box satisfies

\[
\log E_t^{(c)}(\theta)
\ge \max_m LB_m(B)-\log 11-UB_L(B).
\]

If this lower bound exceeds an **upper bound** on `log(1/alpha_c)`, the whole box is safely rejected.

## Required validation sequence

v14 should proceed in this order:

1. unit-test exact score-box geometry and outward likelihood bounds;
2. unit-test that branch-and-bound never certifies a box containing a known feasible outside-cone point;
3. compare the certificate against dense brute-force grids in tiny synthetic cases, requiring the certificate to be one-sided conservative;
4. validate the nuisance box against randomly sampled parameters known to survive the common confidence cutoff;
5. only then run fresh-seed sequential operating-characteristic benchmarks;
6. record node counts and unresolved rates separately from scientific stopping rates.

## Nonclaims

Even a successful v14 certificate would establish only continuous-parameter validity for the tested synthetic logistic model. It would not establish:

- adequacy of a linear visual-preference surface;
- a validated synthetic feature basis;
- robustness to pair-context dependence;
- robustness to nonlinear or multimodal preferences;
- synthetic-to-real transfer;
- compatibility or long-term relationship prediction.

Those are later S1/S2+ validation gates, not consequences of continuous numerical certification.