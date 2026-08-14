# Science S1 — Synthetic Ground-Truth Study

## Status

Planned computational experiment. No human subjects and no real-world dating outcome claims.

## Purpose

Before Mosaic changes the live calibration instrument, test whether the proposed S1 model and active-query logic can recover a **known** synthetic acceptance surface under controlled conditions.

The study is a falsification exercise. If Mosaic cannot recover a known low-dimensional model under favorable synthetic conditions, the model/query machinery is not ready for human calibration.

## Ground-truth model

For trial user `i`, generate a known effective state

\[
\alpha_i^*=[b_i^*,\beta_i^*]
\]

and candidate features

\[
\phi(x)\in\mathbb R^d.
\]

Base response generator:

\[
P(Y_i=1\mid x)=\sigma((\alpha_i^*)^Tz(x)).
\]

One displayed pair generates the four-option response by drawing binary `Y_A` and `Y_B` under the base conditional-independence model.

## Parameter families

The simulation must vary, rather than silently fix:

### Feature dimension

At minimum include a low, moderate, and deliberately difficult regime, for example:

```text
d = 2, 4, 8, 12
```

These are simulation conditions, not proposed claims about human preference dimensionality.

### Effective slope geometry

Include:

- dense coefficient vectors;
- sparse coefficient vectors;
- one dominant dimension;
- several similarly important dimensions; and
- coefficient directions poorly aligned with the initial query bank.

### Acceptance prevalence

Vary intercepts so reference-population acceptance is approximately:

```text
low
moderate
high
```

The exact operational values should be recorded with the simulation output rather than encoded as psychological categories.

### Prior quality

Evaluate at least:

- correctly centered weak prior;
- correctly centered informative prior;
- moderately shifted prior mean;
- overconfident wrong prior; and
- covariance misspecification.

A group prior that helps only when correct is not sufficient evidence for safe deployment.

## Query policies

### P0 — Passive random

Uniform/random admissible candidate pairs. This is the baseline.

### P1 — Boundary-only

Prefer candidates with posterior predictive acceptance near `0.5`.

This policy is intentionally included because the Fisher scalar `p(1-p)` is largest near the decision boundary, but boundary sampling alone may repeatedly probe the same feature direction and leave other directions unresolved.

### P2 — D-optimal / local information gain

Use

\[
G(q)\approx\frac12\log\det(I+\Sigma_i\mathcal I_q)
\]

or the equivalent precision-matrix determinant increment.

This policy should jointly favor the current boundary and unresolved directions.

### P3 — Burden-aware information gain

Use

\[
J(q)=G(q)/E[C(q)].
\]

In the first synthetic study, cost may initially be constant; later simulations can make cost depend on candidate similarity, expected response time, or generation/QC burden.

### P4 — Information + diagnostic allocation

Reserve a prespecified fraction of queries for model checks rather than pure exploitation of the assumed likelihood.

Examples:

- repeat candidate under changed pair context;
- symmetric local perturbations;
- sparse factorial interaction probes; and
- delayed repetitions.

## Deliberate misspecification regimes

A scientifically useful active learner must recognize when its assumed model is wrong.

### M1 — Pair-context effect

Generate

\[
P(Y_A=1)=\sigma(\alpha^Tz_A + c\,h(z_A,z_B))
\]

for a nonzero contrast/context term `c`.

Question: do context probes detect the violation before the stopping rule declares calibration complete?

### M2 — Quadratic curvature

Generate utility with one or more quadratic terms not included in the fitted linear model.

### M3 — Sparse interaction

Add one controlled feature interaction.

### M4 — Multiple attraction basins

Generate a response surface with two separated high-acceptance regions that no single linear hyperplane can represent correctly.

### M5 — Generator/feature error

Perturb realized feature values away from intended feature specifications and fit under the nominal values.

This quantifies sensitivity to imperfect synthetic control.

## Inference

The first implementation may use a Gaussian prior plus a Laplace approximation to Bayesian logistic regression because:

- the base linear-logistic posterior is log-concave with a Gaussian prior;
- posterior covariance is directly useful for local information design; and
- the approximation is transparent enough to audit against exact/sampled methods later.

The inference implementation is not considered validated merely because optimization converges.

## Primary metrics

### Parameter-space metrics

Useful for synthetic ground truth only:

- effective coefficient error;
- intercept error;
- posterior coverage of the known `alpha*`.

These are secondary to decision performance because coefficient coordinates depend on the basis.

### Predictive metrics

On a large held-out reference bank:

- log loss;
- Brier score;
- probability calibration;
- held-out accept/reject classification at prespecified thresholds.

### Ranking/decision metrics

- top-K overlap;
- expected top-K regret under the known true acceptance probabilities;
- pair-ordering error;
- probability that posterior uncertainty changes a downstream top-K decision.

### Efficiency metrics

- pair queries used;
- binary decisions used;
- expected burden/cost;
- information gain per query/cost.

### Safety/scientific-diagnostic metrics

- false-stop rate;
- misspecification detection rate;
- frequency of an overconfident posterior under a wrong model;
- sensitivity to prior misspecification;
- sensitivity to generator-feature error.

## Stopping-rule evaluation

The simulation must distinguish:

```text
stopped because target decision precision was achieved
```

from

```text
stopped because the product query cap was reached.
```

A provisional scientific stopping rule may combine:

1. adequate design/information coverage;
2. stable top-K decisions under posterior draws;
3. best admissible expected information gain below threshold; and
4. no triggered model-diagnostic failure.

Thresholds should be swept in simulation and reported as operating curves rather than selected because they produce a desired query count.

## Required comparisons

For each policy/scenario report the distribution, not only the mean, of:

```text
query count to scientific stop
held-out log loss
Brier score
top-K regret
false-stop indicator
misspecification-detected indicator
```

The key question is not whether active querying wins every metric in every regime. It is **where** each policy helps, fails, or becomes overconfident.

## Initial falsification criteria

Do not advance the S1 model toward live scientific calibration if any of these occurs systematically under the correctly specified base regime:

- posterior predictive quality does not improve materially with additional informative observations;
- active design frequently leaves feature directions unresolved despite available admissible probes;
- the stopping rule declares success while held-out ranking regret remains high;
- posterior uncertainty is severely undercalibrated; or
- results depend pathologically on small arbitrary changes in prior specification.

For misspecified regimes, failure to detect model inadequacy should be treated as a scientific defect even if average ranking metrics appear acceptable.

## Reproducibility requirements

Every simulation result must record:

- simulation code version/commit;
- model version;
- feature-basis simulator version;
- prior version/parameters;
- query-policy version;
- stopping-rule version;
- random seed set;
- full scenario parameters; and
- metric definitions.

Raw simulation draws should be reproducible from seed/config rather than stored as opaque summary claims.

## First implementation boundary

The first code checkpoint should implement only:

1. known linear-logistic ground truth;
2. Gaussian-prior MAP/Laplace inference;
3. passive random, boundary-only, and D-optimal query policies;
4. a fixed held-out candidate bank; and
5. predictive/ranking metrics.

Misspecification regimes and burden-aware/diagnostic allocation should be added after the base inference and policy comparison are numerically verified.
