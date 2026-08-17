# S1 Leave-One-Out Mixture Equivalence v13h

## Status

Analytical checkpoint after the negative `s1-theta-challenger-benchmark-v13g`.

No Monte Carlo benchmark is required for this checkpoint because the proposed method is an exact monotone transformation of the existing all-grid-mixture e-process.

## Question

After v13g showed that a leave-null-out **MLE** challenger collapses onto ordinary MLE-face, the next apparent parameter-specific candidate is a leave-null-out **Bayesian alternative mixture**.

For candidate null `theta_j`, use a uniform prior over all `N-1` alternatives `theta_k != theta_j`. The sequential posterior predictive over those alternatives has cumulative joint numerator

\[
Q_{t,j}^{(-j)}
=\frac{1}{N-1}\sum_{k\ne j}L_t(\theta_k).
\]

This is normalized, predictable, and therefore yields a valid e-process under `theta_j`.

The question is whether it can materially improve the nested all-grid mixture from v13f/v13g.

## Exact algebra

Let

\[
S_{t,j}=\sum_{k\ne j}L_t(\theta_k).
\]

The existing uniform all-grid mixture uses

\[
Q_t^{all}=\frac{L_t(\theta_j)+S_{t,j}}{N}.
\]

Its candidate-`j` e-value is

\[
E_{t,j}^{all}
=\frac{Q_t^{all}}{L_t(\theta_j)}
=\frac{1+S_{t,j}/L_t(\theta_j)}{N}.
\]

The leave-one-out alternative mixture gives

\[
E_{t,j}^{(-j)}
=\frac{Q_{t,j}^{(-j)}}{L_t(\theta_j)}
=\frac{S_{t,j}/L_t(\theta_j)}{N-1}.
\]

Eliminating the likelihood ratio gives the exact identity

\[
\boxed{
E_{t,j}^{(-j)}
=\frac{N E_{t,j}^{all}-1}{N-1}
}
\]

at every time, on every response path, under every predictable query policy.

The transformation is strictly increasing. Therefore

\[
\max_{s\le t}E_{s,j}^{(-j)}
=\frac{N\max_{s\le t}E_{s,j}^{all}-1}{N-1}.
\]

The same equivalence holds for running-intersection rejection times.

## Threshold equivalence

The leave-one-out method rejects candidate `j` at nominal level `alpha` when

\[
E_{t,j}^{(-j)}\ge\frac1\alpha.
\]

Using the identity above, this occurs exactly when

\[
E_{t,j}^{all}
\ge
\frac{1+(N-1)/\alpha}{N}.
\]

For the active finite-grid protocol,

\[
N=72,\qquad \alpha=0.05,\qquad 1/\alpha=20.
\]

Hence the equivalent all-grid threshold is

\[
\frac{1+71\times20}{72}
=\frac{1421}{72}
\approx19.736111.
\]

So the proposed alternative mixture does nothing more than move the existing all-grid e-value threshold from

\[
20\quad\text{to}\quad19.7361.
\]

That is only about a 1.32% reduction in the e-value threshold.

Equivalently, the universal-prediction worst-case regret bound changes only from

\[
\log N=\log72
\]

to

\[
\log(N-1)=\log71,
\]

a gain of

\[
\log(72/71)\approx0.0140\ \text{nat}.
\]

## Scientific consequence

The leave-one-out all-alternative mixture is mathematically valid, but it is **not a substantively new efficiency mechanism**. Its running-intersection confidence sequence is an almost imperceptibly more aggressive version of the already-tested nested all-grid mixture.

The observed finite-grid gap is much larger:

- nested all-grid mixture in v13f/v13g: about 70–72% stopping by 240;
- historical oracle-predictive ceiling on the same class of query paths: about 96% by 240.

A deterministic threshold change from 20 to 19.736 cannot plausibly explain or close that gap. Running another 1,536-path benchmark would mostly measure Monte Carlo noise around an analytically predetermined small change.

Therefore **v13h stops this branch analytically rather than spending another benchmark run**.

## What this teaches about numerator design

A parameter-specific numerator is useful only if it materially changes the predictive distribution for the difficult false nulls.

Two failed/weak constructions now have different reasons:

1. v13g leave-null-out MLE differs from common MLE only when the null lies on the current MLE face;
2. v13h leave-null-out all-alternative mixture differs from the common all-grid mixture only by removing one `1/N` null component, giving the affine identity above.

The next candidate must therefore concentrate predictive mass on a **small, scientifically relevant alternative set** rather than all alternatives.

## Next exact checkpoint

On the circular 5-degree finite-direction grid, the hardest alternatives to a candidate null `theta_j` are its immediate directional neighbors. Test a **local-neighbor alternative mixture**:

\[
Q_{t,j}^{local}
=\frac12\left[
L_t(\theta_{j-1})+L_t(\theta_{j+1})
\right],
\]

with circular indexing.

Its sequential form is the posterior predictive under a fixed 50/50 prior on the two neighboring alternatives. It is normalized and predictable, so

\[
E_{t,j}^{local}=Q_{t,j}^{local}/L_t(\theta_j)
\]

is a valid e-process under `theta_j`.

This construction differs for every null and replaces the `log72` universal dilution with at most `log2` prior dilution against the nearest directional alternatives. It is also aligned with the certification geometry: neighboring directions are the hardest false hypotheses to distinguish from `j`; farther directions should ordinarily be easier to reject once a local likelihood slope is established.

Benchmark it on a fresh seed block with:

- nested/running-intersection confidence sequences;
- 5-degree grid;
- `B=0.9`;
- target 0.15;
- alpha 0.05;
- candidate bank size 12;
- acquisition controller frozen to the historical current-time all-grid-mixture disagreement policy;
- nested all-grid mixture as primary control;
- same global finite-grid MLE reporting center;
- paired stop probability by 240 as the primary efficiency endpoint;
- zero geometry violations as a hard invariant.

Do not modify acquisition in the same checkpoint.

## Nonclaims

This analytical result is confined to the finite uniform parameter grid and the specific all-grid versus leave-one-out mixture definitions above. It does not establish continuous confidence geometry, higher-dimensional performance, model correctness for humans, synthetic-to-real transfer, compatibility, or relationship outcomes.
