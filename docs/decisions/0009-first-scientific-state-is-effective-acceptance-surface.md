# ADR 0009 — First scientific preference state is an effective acceptance surface

## Status

Proposed for Science S1.

## Context

Mosaic's infrastructure program intentionally used deterministic questionnaire, synthetic-candidate, and ranking fixtures. The first scientific phase must now replace placeholders without giving psychologically meaningful names to parameters that the observations cannot identify.

The original concept separated preference direction, pursuit threshold, and response consistency. That decomposition is intuitively attractive but is not automatically identifiable from ordinary pairwise choices.

For a logistic pairwise model

\[
P(A\succ B)=\sigma[\gamma_i w_i^T(\phi_A-\phi_B)],
\]

only the product

\[
\eta_i=\gamma_iw_i
\]

appears in the likelihood. Rescaling `w_i` and inversely rescaling `gamma_i` leaves every observable choice probability unchanged.

Likewise, an absolute intercept/selectivity term cancels from forced pairwise differences, so pairwise comparisons alone cannot reveal whether either candidate is acceptable at all.

The first model therefore needs an operational observable, an identifiable parameterization, and an explicit outside option.

## Decision

### 1. S1 targets synthetic-candidate willingness-to-meet, not abstract attraction

The first scientific target is

\[
A_i(x)=P(Y_i=1\mid x,D_i,\mathcal M,\mathcal B),
\]

where `Y_i=1` is a user's willingness-to-meet response under a fixed calibration instrument and `x` is a candidate represented in a versioned synthetic feature basis.

Transfer from this response surface to real-person attraction is a later validation question.

### 2. Persist the effective identifiable state

The provisional model is

\[
P(Y_i=1\mid x,\alpha_i)
=\sigma(\alpha_i^Tz(x)),
\]

with

\[
\alpha_i=[b_i,\beta_i]^T,
\qquad
z(x)=[1,\phi(x)]^T.
\]

`alpha_i` is an **effective decision-state parameter**, not a decomposition into separate psychological preference magnitude and response noise.

Do not persist independent `preference_strength`, `choice_consistency`, or equivalent latent scalars unless a later protocol establishes a scale anchor that makes them identifiable.

### 3. The initial instrument includes an outside option

The preferred S1 pair response is:

```text
A only
B only
Both
Neither
```

under wording equivalent to “Which of these people would you be open to meeting?”

This is initially modeled as two binary acceptability observations. It preserves absolute pursuit information that forced `A versus B` comparisons destroy.

### 4. Pair independence is testable, not assumed silently

The conditional-independence likelihood is provisional. S1 protocols must include repeated candidate presentations against different comparison partners so pair-context/contrast effects can be detected.

A detected context effect is model misspecification and must not be hidden by relabeling it as user noise.

### 5. Selectivity is initially a derived reference-distribution quantity

The raw intercept is coordinate-dependent. Therefore Mosaic should initially summarize operational selectivity through the posterior predictive acceptance rate over a versioned reference candidate distribution:

\[
q_i=E_{X\sim P_{ref}}[A_i(X)],
\qquad
S_i=1-q_i.
\]

The reference distribution and feature-basis version are part of the semantics.

### 6. Population information enters as a prior, not a final rule

The model interface may support

\[
\alpha_i\mid g_i\sim N(\mu_{g_i},\Sigma_{g_i}),
\]

but group-specific priors may only be introduced from suitable evidence and must be versioned. Direct individual evidence determines the posterior state.

### 7. Query count is adaptive

Science S1 will not define “20” or “30” comparisons as sufficient by fiat.

For a `d`-feature model plus intercept, a four-option pair contributes local Fisher-information rank at most two, so

\[
N_{pair}\ge\lceil(d+1)/2\rceil
\]

is only a necessary rank lower bound, not a precision guarantee.

Individual calibration stops by coverage, posterior/predictive ranking stability, information exhaustion, and model-diagnostic adequacy, subject to a product burden cap.

### 8. Feature-basis semantics are versioned independently

A coefficient vector is only interpretable with the exact feature basis that produced it. Centering, scaling, whitening, controllable attributes, learned encoders, or image-to-feature mappings therefore require explicit basis versions.

Changing the basis cannot silently reinterpret a historical posterior.

## Consequences

- The first scientific model claims only what the controlled observation can support.
- Relative preference and pursuit selectivity are not conflated.
- A psychologically appealing but unidentifiable `preference × consistency` decomposition is avoided.
- Existing infrastructure can persist future posterior/model outputs without rewriting raw responses.
- The synthetic calibration protocol must include context, repetition, and model-misspecification probes rather than only maximally informative queries under one assumed model.
- No universal feature dimension or query budget is asserted before synthetic ground-truth studies and later human validation.

## Rejected alternatives

### Infer `w_i`, `tau_i`, and `gamma_i` as independent user traits immediately

Rejected because ordinary pairwise/acceptance likelihoods do not identify all of these quantities separately without additional anchors and assumptions.

### Use forced A/B comparisons only

Rejected for the base S1 instrument because the intercept/outside-option information cancels, making absolute pursuit selectivity unidentifiable.

### Call the first model “attraction utility” and treat it as domain-general

Rejected because the observable is a response to controlled synthetic candidates under a specific instrument. Transfer to real profiles and in-person attraction must be demonstrated rather than assumed.

### Fix calibration at 20–30 pair questions

Rejected because required evidence depends on feature dimension, design geometry, prior strength, response variability, model misspecification, and the downstream decision-precision target.

## References

- Guo, Sanner & Bonilla. *Gaussian Process Preference Elicitation*. NeurIPS 2010.
- Ge, Juba & Vorobeychik. *Learning Linear Utility Functions From Pairwise Comparison Queries*. 2024.
- Bergström et al. *Active preference learning for ordering items in- and out-of-sample*. NeurIPS 2024.
- De Peuter et al. *Preference Learning of Latent Decision Utilities with a Human-like Model of Preferential Choice*. NeurIPS 2024.
- Eastwick & Finkel. *Sex differences in mate preferences revisited: do people know what they initially desire in a romantic partner?* JPSP 2008.
- Eastwick et al. *A Worldwide Test of the Predictive Validity of Ideal Partner Preference-Matching*. JPSP 2025 (online 2024).

## Detailed specification

See `docs/science/s1-identifiable-preference-model.md`.
