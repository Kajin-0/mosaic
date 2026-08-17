# S1 Anytime-Valid Likelihood Confidence — v13 Method Boundary

## Status

Active method-development line after the v12 Laplace-posterior stopping family was falsified.

v13 replaces posterior-percentile calibration with a **prequential likelihood-ratio e-process** whose fixed-parameter optional-stopping validity is established before simulation. The finite-grid program has now progressed through v13f and materially refined the operational confidence object.

Current result boundary: `results/s1-nested-confidence-benchmark-v13f.md`.

## Observable model

For one binary willingness-to-meet observation at time `t`, let

\[
Y_t\in\{0,1\},\qquad
P_\theta(Y_t=1\mid x_t)=\sigma(\theta^T z_t),
\]

where `z_t=(1,x_t)` includes the intercept and `x_t` is predictable: it may depend on all previous observations and internal randomized design choices, but not on the current unseen outcome.

This remains the provisional S1 linear-logistic acceptance model. The e-process does **not** validate that likelihood family. Misspecification remains a separate required research problem.

## Fixed-parameter prequential e-process

Before observing `Y_t`, choose any normalized predictive distribution

\[
q_t(y\mid H_{t-1},x_t),\qquad q_t(0)+q_t(1)=1.
\]

For a fixed candidate parameter `theta`, define

\[
E_t(\theta)
=\prod_{s=1}^t
\frac{q_s(Y_s\mid H_{s-1},x_s)}
{p_\theta(Y_s\mid x_s)}.
\]

Conditional on the past and the current predictable design,

\[
\mathbb E_\theta\left[
\frac{q_t(Y_t)}{p_\theta(Y_t)}
\middle|H_{t-1},x_t
\right]
=\sum_y p_\theta(y)\frac{q_t(y)}{p_\theta(y)}
=1.
\]

Therefore `E_t(theta)` is a nonnegative martingale under correctly specified fixed `theta`, including predictable adaptive query selection.

Ville's inequality gives

\[
P_\theta\left(\sup_t E_t(\theta)\ge1/\alpha\right)\le\alpha.
\]

Writing

\[
Q_t=\prod_s q_s(Y_s),\qquad
L_t(\theta)=\prod_s p_\theta(Y_s\mid x_s),
\]

the current-time confidence set is

\[
C_t=\left\{\theta:\log L_t(\theta)>\log Q_t+\log\alpha\right\}.
\]

The exact strict/boundary convention should remain explicit in code.

## Preferred representation: the running intersection

The sequence of current-time sets is not necessarily nested because an e-process may cross its threshold and later fall below it. A parameter rejected at one time can therefore re-enter a later `C_t`.

The operational confidence sequence should instead remember all previous valid rejections:

\[
C_t^{\cap}
=\bigcap_{s\le t}C_s
=\left\{\theta:\max_{s\le t}E_s(\theta)<1/\alpha\right\}.
\]

This does **not** spend additional error probability. Under the true fixed parameter,

\[
\{\theta_*\in C_t^{\cap}\ \forall t\}
=\{\sup_t E_t(\theta_*)<1/\alpha\},
\]

so the same Ville event yields simultaneous coverage at least `1-alpha`.

### Geometric consequence

If the same reported center `c_t` is used for current and nested sets, then

\[
C_t^{\cap}\subseteq C_t
\]

implies any subset-monotone directional radius obeys

\[
r(c_t;C_t^{\cap})\le r(c_t;C_t)
\]

whenever the nested set is nonempty.

v13f enforces this pathwise as a hard implementation assertion and observes no violation.

An **empty nested set is a confidence/model failure state, not a successful certificate**.

## Parameter-specific predictable numerators are valid

A single common numerator is convenient but not required.

For every candidate parameter `theta_j`, one may choose its own normalized predictable distribution

\[
q_{t,j}(y\mid H_{t-1},x_t),
\qquad
\sum_y q_{t,j}(y)=1,
\]

before observing `Y_t`. Define

\[
E_{t,j}
=\prod_{s\le t}
\frac{q_{s,j}(Y_s)}{p_{\theta_j}(Y_s\mid x_s)}.
\]

Under the fixed null `theta_j`, exactly the same conditional expectation identity gives

\[
\mathbb E_{\theta_j}[E_{t,j}\mid H_{t-1}]=E_{t-1,j}.
\]

Thus each candidate parameter may have a **different challenger/test-specific predictor** without invalidating its own e-process. The resulting nested confidence sequence is

\[
C_t^{\cap}
=\left\{\theta_j:\max_{s\le t}E_{s,j}<1/\alpha\right\}.
\]

This is the next finite-grid efficiency lever. The numerator for candidate `j` may use all historical data and the current predictable query, but it must not use the current unseen response or synthetic truth.

A natural first finite-grid construction is the one-step-lagged maximum-likelihood alternative excluding `theta_j`, averaging exactly tied maximizers before forming the binary predictive distribution.

## Why this route replaced v12

The v12 family asked a local Gaussian/Laplace posterior approximation to behave like a finite-sample confidence sequence. It failed:

- raw angular q95 undercovered;
- persistence did not repair weak/high-dimensional subgroup failure;
- radial/transverse debiasing regained safety by becoming too conservative;
- tangent projection regained utility by becoming anti-conservative.

v13 establishes the error event first. Simulation then measures burden, power, predictor regret, numerical conservatism, and misspecification rather than empirically tuning a nominal confidence percentile.

## Moving composite nulls remain unsafe without a separate theorem

For a fixed prespecified composite null `H0`, a safe statistic is

\[
E_t(H_0)=\frac{Q_t}{\sup_{\theta\in H_0}L_t(\theta)},
\]

provided the denominator is a genuine upper bound on the null likelihood supremum.

```text
underestimate sup_H0 L  -> invalid / anti-conservative
upper-bound sup_H0 L    -> valid / possibly conservative
```

But an angular null centered on a current fitted direction is data-dependent and changes over time. Repeatedly selecting a new cone and testing it as though it were fixed is not automatically covered by the fixed-null argument.

The safe operational order remains:

```text
construct anytime-valid parameter confidence sequence
        ↓
choose a reported center
        ↓
certify a geometric property of every retained parameter
        ↓
stop only if the full retained set satisfies the target
```

## Directional certification

For a retained slope-direction set

\[
D_t=\left\{
\beta(\theta)/\|\beta(\theta)\|:
\theta\in C_t^{\cap},\ \|\beta(\theta)\|>0
\right\},
\]

a reported center `c_t` may be data-dependent because it is chosen after the confidence set has been constructed. The certificate must then control every retained direction:

\[
r_t(c_t)
=\sup_{u\in D_t}\frac{\arccos(c_t^Tu)}{\pi}
\le\epsilon_*.
\]

On the simultaneous coverage event, the true direction is necessarily inside the certified cone at every stopping time.

The finite-grid harness computes this maximum exactly.

## Continuous cone problem

For a fixed center `u` and half-angle `theta_0=pi epsilon`, write

\[
\beta=\beta_\parallel u+\beta_\perp,\qquad u^T\beta_\perp=0.
\]

The target cone is

\[
\beta_\parallel\ge0,\qquad
\|\beta_\perp\|\le\tan(\theta_0)\beta_\parallel.
\]

To certify the continuous confidence set inside the cone, one must prove that no parameter outside the cone meets the confidence threshold. Equivalently, obtain a conservative upper bound on

\[
\sup_{\theta\notin K(u,\epsilon)}\log L_t(\theta)
\]

and show it lies below the relevant e-process confidence cutoff.

A local optimizer that can underestimate this outside-cone supremum is unacceptable: an underestimate can create false confidence. Continuous S1 therefore still requires branch-and-bound, convex relaxation, or another numerically certified upper-bound construction, including nuisance intercept and slope magnitude.

## Finite-grid result chain

- **v13a:** finite fixed-null sanity check; valid construction rejected 0.477% at nominal 5%, while an outcome-leaking numerator rejected 100%.
- **v13b:** exact finite confidence-set geometry; zero directional false stops while truth remained in the confidence set.
- **v13c:** grid refinement helped but did not solve strict-target burden.
- **v13d:** common-path numerator comparison identified a large oracle gap under current-time sets.
- **v13e:** fresh-seed validation replicated large current-time-set gains for MLE-face and SNML over the all-grid mixture.
- **v13f:** replacing current-time sets by the running intersection produced the largest finite-grid efficiency gain so far: by 240 observations mixture `7.23% -> 70.25%`, MLE `26.56% -> 53.97%`, SNML `26.17% -> 58.53%`, with zero geometric violations. It also demonstrated that numerator ranking depends strongly on confidence-sequence representation.

Future finite-grid benchmarks should use `C_t^cap` by default.

## Current implementation checkpoint

`services/engine/src/mosaic_engine/science_s1_eprocess.py` implements the stable fixed-parameter e-process primitives.

Finite-grid benchmark modules v13a–v13f additionally exercise:

- predictable adaptive query selection;
- exact finite confidence sets;
- exact finite directional radii;
- several common predictable numerators;
- fresh-seed prospective validation; and
- running-intersection confidence sequences with hard subset/radius invariants.

These are verification harnesses, not a production matchmaking model.

## Nonclaims

The v13 method does not establish:

- that the linear-logistic S1 likelihood is correct for people;
- a valid synthetic visual feature basis;
- transfer from synthetic willingness-to-meet to real-person attraction;
- compatibility or relationship outcome prediction;
- a certified continuous cone optimizer;
- validity of a moving data-dependent composite-null test;
- that 5% is the final product risk tolerance; or
- acceptable human calibration burden in the real application.

## Next exact checkpoint

Run a fresh-seed finite-grid **theta-specific predictable challenger** benchmark with the acquisition policy frozen.

Preserve:

- 5-degree grid;
- `B=0.9`;
- target `epsilon=0.15`;
- `alpha=0.05`;
- candidate bank size 12;
- the existing current-time all-grid-mixture disagreement controller for query selection, so the observed data path is not changed by the new numerator;
- running-intersection confidence sequences for certification;
- the same global finite-grid MLE center for directional reporting.

Baseline: nested all-grid mixture.

Candidate: for each tested `theta_j`, construct a normalized predictable challenger from the one-step-lagged maximum-likelihood alternative set excluding `theta_j`, averaging tied alternatives.

Primary endpoint: paired difference in stop probability by 240 observations. Secondary endpoint: stopping-time burden. Hard safety invariant: zero false directional stops while truth remains in the nested confidence set.

Do not change query policy in this checkpoint. After the challenger-numerator mechanism is understood, continuous certification and deliberate likelihood-misspecification work remain mandatory before S1 can close.
