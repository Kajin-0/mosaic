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

## Fixed composite nulls are valid; data-dependent nulls require care

For a **fixed, prespecified** composite null `H0`, a safe statistic is

\[
E_t(H_0)
=\frac{Q_t}{\sup_{\theta\in H_0}L_t(\theta)}.
\]

For every true `theta_0 in H0`,

\[
E_t(H_0)
\le\frac{Q_t}{L_t(\theta_0)}.
\]

Thus a crossing of `1/alpha` by the composite statistic implies a crossing by the fixed-parameter e-process for the true null parameter, and type-I error is bounded by `alpha` provided the denominator is a **genuine upper bound** on the null likelihood supremum.

This point is numerically critical:

```text
underestimate sup_H0 L  -> invalid, anti-conservative certificate
upper-bound sup_H0 L    -> valid, possibly conservative certificate
```

However, an angular null centered on a **current fitted direction**,

\[
H_{0,t}(\epsilon)
=\{\theta:\operatorname{angle}(\beta(\theta),u_t)\ge\pi\epsilon\},
\]

is data-dependent and changes with `t`. The fixed-composite-null domination argument does **not** automatically provide an anytime guarantee when the tested null itself is adaptively selected from the same data. Repeatedly selecting a new cone and testing it as if it had been fixed in advance can reintroduce optional-selection error.

Therefore S1 should not operationalize stopping by repeatedly testing a moving fitted-direction null unless a separate selective/sequential theorem is supplied.

## Safe operational route: certify the geometry of the confidence sequence

The cleaner construction is to build the anytime-valid parameter confidence sequence first and then ask whether its entire directional geometry is sufficiently concentrated.

On the event

\[
\theta_*\in C_t(\alpha)\quad\text{for every }t,
\]

which has probability at least `1-alpha`, any deterministic geometric statement established about **all** parameters in `C_t` also applies to the truth at every stopping time.

For example, define the slope-direction set

\[
D_t=\left\{
\frac{\beta(\theta)}{\|\beta(\theta)\|}:\theta\in C_t(\alpha),\ \|\beta(\theta)\|>0
\right\}.
\]

Two safe certification targets are:

### Directional diameter

\[
\operatorname{diam}(D_t)
=\sup_{u,v\in D_t}\frac{\arccos(u^Tv)}{\pi}.
\]

Stop only if

\[
\operatorname{diam}(D_t)\le\epsilon_*.
\]

This is strongest but can be unnecessarily conservative because it controls the maximum disagreement between any two plausible directions.

### Certified directional radius

Choose a reported center `c_t` after seeing `C_t` and compute

\[
r_t(c_t)
=\sup_{u\in D_t}\frac{\arccos(c_t^Tu)}{\pi}.
\]

Stop only if a certified bound shows

\[
r_t(c_t)\le\epsilon_*.
\]

The center may be data-dependent because it is merely a summary chosen **after the confidence set is constructed**; validity comes from requiring every parameter in the already-anytime-valid set to lie inside the reported cone.

This distinction is load-bearing:

```text
unsafe shortcut:
select moving cone -> test that data-dependent null as though fixed

safe route:
construct anytime-valid C_t -> certify a geometric property of all theta in C_t
```

## Geometry of a directional cone

For a fixed candidate center `u` and target half-angle `theta0=pi*epsilon`, decompose a candidate slope

\[
\beta=\beta_\parallel u+\beta_\perp,
\qquad
u^T\beta_\perp=0.
\]

The cone around `u` is

\[
\beta_\parallel\ge0,
\qquad
\|\beta_\perp\|\le \tan(\theta_0)\beta_\parallel.
\]

For the tested S1 targets `epsilon in {0.15,0.20,0.25}`, `theta0<pi/2`, so the cone is second-order-cone representable.

To prove that the confidence set lies inside the cone, it is sufficient to prove that **no parameter outside the cone satisfies the likelihood confidence threshold**. Equivalently, one needs a conservative upper bound on

\[
\sup_{\theta\notin K(u,\epsilon)}\log L_t(\theta).
\]

If that certified upper bound is below

\[
\log Q_t+\log\alpha,
\]

then every point in `C_t(alpha)` lies inside the cone.

The logistic log likelihood is concave in the full coefficient vector, but maximizing a concave function over the complement of a cone is not directly a convex optimization problem. Any continuous v13 angular certificate must therefore provide a conservative **upper bound** on the best outside-cone likelihood rather than trust a local optimizer whose failure could create false confidence.

## Candidate numerical strategy

Do not launch a large continuous-angular v13 operating benchmark until this step is resolved.

A defensible staged path is:

1. **fixed-parameter e-process kernel** — implemented;
2. **finite fixed-composite-null sanity problem** — on a deliberately finite prespecified null grid, where the exact maximum likelihood over the grid is computable and sequential validity is straightforward;
3. **confidence-set geometry harness** — on a finite parameter grid, certify angular diameter/radius directly from the e-process confidence set rather than from a moving null test;
4. **continuous outside-cone likelihood upper bound** — develop branch-and-bound, a convex relaxation, or another method that provably upper-bounds the likelihood outside a candidate cone;
5. **fresh-seed correctly specified benchmark** — measure safety, power, and burden only after the numerical certificate itself is conservative;
6. **misspecification regimes** — pair context, curvature, interactions, multimodality, and generator error must then be tested because e-process validity is conditional on the likelihood family containing the truth.

The finite-grid checkpoints are verification harnesses, not product stopping rules.

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
- conservative rejection for a **fixed** composite null given an externally supplied upper bound on its log-likelihood supremum.

The module intentionally does **not** claim that a time-varying data-dependent composite null inherits fixed-null anytime validity, and it does not yet solve continuous confidence-set angular certification.

## Nonclaims

This method does not establish:

- that the linear-logistic S1 likelihood is correct for people;
- a valid synthetic visual feature basis;
- transfer from synthetic willingness-to-meet to real-person attraction;
- compatibility or relationship outcome prediction;
- that the current numerical optimizer can certify a continuous angular cone;
- that a moving data-dependent composite-null test is automatically anytime-valid;
- that 5% is the final product risk tolerance; or
- that the new method will have acceptable user burden.

It establishes a mathematically different route whose fixed-parameter sequential validity can be audited independently from the failed Laplace-q95 calibration family.

## Next exact checkpoint

Run the **finite fixed-grid composite-null benchmark** already implemented in `science_s1_benchmark_v13a.py`. It must verify empirically that false rejection of a true grid null remains at or below the nominal level under optional stopping and adaptive predictable design, while a deliberately non-predictable numerator should visibly break the construction.

After that, extend the finite-grid harness to certify the angular diameter/radius of the full e-process confidence set. Only then should continuous outside-cone optimization be attempted.