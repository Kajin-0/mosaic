# S1 Anytime-Valid Likelihood Confidence — v13 Method Boundary

## Status

Method-development checkpoint after `s1-tangent-stopping-benchmark-v12e`.

v12a–v12e falsified the current Laplace-posterior q95 family as a finite-sample sequential stopping guarantee. The next confidence object should therefore be valid under predictable adaptive query selection and optional stopping by construction, rather than repaired empirically with another posterior correction.

This document defines the first v13 candidate: a **prequential likelihood-ratio e-process**.

## Observable model

For one binary willingness-to-meet observation at time `t`, let

\[
Y_t\in\{0,1\},\qquad
P_\theta(Y_t=1\mid x_t)=\sigma(\theta^T z_t),
\]

where `z_t=(1,x_t)` includes the intercept and `x_t` is predictable: it may depend on all prior observations and internal randomized design choices, but not on the current unseen outcome.

The model remains the provisional S1 linear-logistic acceptance surface. This method does not validate that model; deliberate misspecification tests remain required later.

## Prequential numerator

Before observing `Y_t`, choose any normalized predictive distribution

\[
q_t(y\mid H_{t-1},x_t),\qquad q_t(0)+q_t(1)=1.
\]

The predictor may use the current Laplace fit, another fitted model, a mixture, or a deliberately simple baseline. **Its calibration is not required for validity.** It is only required to be predictable and normalized before `Y_t` is revealed.

For a fixed candidate parameter `theta`, define

\[
E_t(\theta)
=\prod_{s=1}^t
\frac{q_s(Y_s\mid H_{s-1},x_s)}
{p_\theta(Y_s\mid x_s)}.
\]

Conditional on the past and current predictable design,

\[
\begin{aligned}
\mathbb E_\theta\left[
\frac{q_t(Y_t)}{p_\theta(Y_t)}
\middle|H_{t-1},x_t
\right]
&=\sum_{y\in\{0,1\}}
p_\theta(y)\frac{q_t(y)}{p_\theta(y)}\\
&=q_t(0)+q_t(1)\\
&=1.
\end{aligned}
\]

Therefore `E_t(theta)` is a nonnegative martingale under `theta`, including when `x_t` is adaptively selected from the past.

By Ville's inequality,

\[
P_\theta\left(\sup_t E_t(\theta)\ge 1/\alpha\right)\le\alpha.
\]

This gives the anytime-valid confidence sequence

\[
C_t(\alpha)
=\{\theta:E_t(\theta)<1/\alpha\}.
\]

Equivalently, writing

\[
Q_t=\prod_s q_s(Y_s),
\qquad
L_t(\theta)=\prod_s p_\theta(Y_s\mid x_s),
\]

a parameter remains plausible whenever

\[
\log L_t(\theta)>
\log Q_t+\log\alpha.
\]

The strict/boundary convention has probability-zero relevance in continuous parameter settings but should remain explicit in code.

## Why this addresses the v12 failure mode

The v12 family asked a local Gaussian posterior approximation to behave like a finite-sample confidence sequence. It did not:

- raw q95 undercovered badly for weak signal/high dimension;
- persistence reduced but did not eliminate false stopping;
- radial/transverse corrections restored safety by becoming conservative;
- tangent projection restored utility by becoming anti-conservative.

The e-process changes the logical order. Optional-stopping validity is established **before** simulation. Simulation then measures power, burden, numerical conservatism, and model misspecification rather than discovering after the fact whether a nominal posterior percentile behaves like a confidence bound.

## Composite null needed for ranking-direction certification

The operational question is not whether one fixed `theta` is rejected. To certify a ranking-direction target `epsilon`, define a bad-direction null relative to an operational reference direction `u_t`:

\[
H_{0,t}(\epsilon)
=\{\theta:\operatorname{angle}(\beta(\theta),u_t)\ge\pi\epsilon\}.
\]

A safe composite-null statistic is

\[
E_t(H_0)
=\frac{Q_t}{\sup_{\theta\in H_0}L_t(\theta)}.
\]

For every true `theta_0 in H_0`,

\[
E_t(H_0)
\le\frac{Q_t}{L_t(\theta_0)}.
\]

Thus if the composite statistic crosses `1/alpha`, the fixed-parameter martingale for every possible true null parameter must also be at least as large at that time. Rejecting `H_0` is therefore conservative provided the denominator is a **genuine upper bound** on the null likelihood supremum.

This point is numerically critical:

```text
underestimate sup_H0 L  -> invalid, anti-conservative certificate
upper-bound sup_H0 L    -> valid, possibly conservative certificate
```

The next numerical problem is therefore not posterior sampling. It is certified optimization.

## Geometry of the angular null

For nonzero reference direction `u` and target half-angle `theta0=pi*epsilon`, decompose a candidate slope

\[
\beta=\beta_\parallel u+\beta_\perp,
\qquad
u^T\beta_\perp=0.
\]

The good-direction cone is

\[
\beta_\parallel\ge0,
\qquad
\|\beta_\perp\|\le \tan(\theta_0)\beta_\parallel.
\]

For the tested S1 targets `epsilon in {0.15,0.20,0.25}`, `theta0<pi/2`, so this is a second-order cone. The bad-direction null is its complement.

The logistic log likelihood is concave in the full coefficient vector, but maximizing a concave function over the complement of a cone is not directly a convex optimization problem. Any v13 angular certificate must therefore provide a conservative upper bound on the best bad-direction likelihood rather than rely on a local optimizer whose failure could create false confidence.

## Candidate numerical strategy

Do not launch a large v13 operating benchmark until this step is resolved.

A defensible staged path is:

1. **fixed-parameter e-process kernel** — implemented now;
2. **finite composite-null sanity problem** — on a deliberately finite prespecified null grid, where the exact maximum likelihood over the grid is computable and sequential validity is straightforward;
3. **continuous angular-null upper bound** — develop branch-and-bound, a convex relaxation, or another method that provably upper-bounds the null supremum;
4. **fresh-seed correctly specified benchmark** — measure power and burden only after the numerical certificate itself is conservative;
5. **misspecification regimes** — pair context, curvature, interactions, multimodality, and generator error must then be tested because e-process validity is conditional on the likelihood family containing the truth.

The finite-grid checkpoint is not a product stopping rule; it is a verification harness for the sequential likelihood logic.

## Predictor semantics

The numerator predictor influences power but not fixed-parameter validity, provided it is chosen predictably.

For an initial implementation, one reasonable predictor is a clipped plug-in probability from the previous posterior/MAP fit:

```text
q_t(1) = clip(sigmoid(alpha_hat_{t-1}^T z_t), epsilon_q, 1-epsilon_q)
```

with the first observations using a fixed baseline such as 0.5.

Clipping is a numerical/power choice, not a validity repair: after clipping, `(q_t(0),q_t(1))` still forms a normalized predictable distribution.

Future work may compare plug-in, posterior predictive, and mixture predictors on efficiency. The stopping guarantee must not depend on selecting the predictor that looks best on evaluation seeds.

## Current implementation checkpoint

`services/engine/src/mosaic_engine/science_s1_eprocess.py` implements:

- numerically stable binary-logistic log probabilities;
- one-step prequential log e-increments;
- cumulative fixed-parameter log e-values;
- the exact two-outcome conditional normalization identity;
- anytime thresholds;
- the equivalent likelihood confidence cutoff; and
- conservative composite-null rejection given an externally supplied upper bound on the null log-likelihood supremum.

The module intentionally does **not** yet claim to solve the continuous angular-null optimization.

## Nonclaims

This method does not establish:

- that the linear-logistic S1 likelihood is correct for people;
- a valid synthetic visual feature basis;
- transfer from synthetic willingness-to-meet to real-person attraction;
- compatibility or relationship outcome prediction;
- that the current numerical optimizer can certify a continuous angular null;
- that 5% is the final product risk tolerance; or
- that the new method will have acceptable user burden.

It establishes a mathematically different route whose sequential validity can be audited independently from the failed Laplace-q95 calibration family.

## Next exact checkpoint

Build a **finite-grid composite-null benchmark** with known candidate parameter sets and predictable adaptive designs. The benchmark should verify empirically that false rejection of a true grid null remains at or below the nominal level under optional stopping, while also confirming that deliberately non-predictable numerators break the construction.

Only after that harness is correct should continuous angular-null certification be implemented.