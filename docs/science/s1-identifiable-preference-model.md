# Science S1 — Identifiable Individual Preference Model

## Status

Active theoretical specification.

This document defines Mosaic's first real scientific model target. It does **not** claim validated attraction inference or real-world matchmaking validity.

## 1. Scientific quantity

The first quantity Mosaic can defensibly attempt to infer from controlled synthetic visual calibration is not an abstract essence called “attraction.” It is an operational response surface:

```text
probability that user i says they would be willing to meet a synthetic candidate
under a fixed calibration instrument and fixed candidate representation.
```

For candidate representation `x`:

\[
A_i(x) = P(Y_i=1\mid x, D_i, \mathcal M, \mathcal B),
\]

where:

- `Y_i = 1` means “willing to meet” under the specified calibration question;
- `D_i` is the user's accumulated calibration evidence;
- `M` is the model/likelihood version; and
- `B` is the feature-basis/stimulus-space version.

Only later external-validation work can determine how well this quantity transfers to real profile interest, conversation, dates, or relationship outcomes.

## 2. Versioned candidate feature space

Let

\[
\phi(x)\in\mathbb R^d
\]

be a versioned feature representation of a synthetic candidate.

The feature basis must be fixed while a stored model version is interpreted. Centering, scaling, whitening, learned embeddings, controlled generator attributes, and any mapping from image bytes to features are part of the basis version.

A coefficient value has no invariant psychological meaning when the basis changes. Predictions over a fixed candidate space are more fundamental than the raw numerical coefficients.

## 3. Minimal identifiable model

Define the effective latent state

\[
\alpha_i =
\begin{bmatrix}
 b_i\\
 \beta_i
\end{bmatrix}
\in\mathbb R^{d+1}
\]

and augmented feature vector

\[
z(x)=
\begin{bmatrix}
1\\
\phi(x)
\end{bmatrix}.
\]

The provisional linear-logistic acceptance model is

\[
P(Y_i=1\mid x,\alpha_i)
=\sigma(\alpha_i^T z(x))
=\frac{1}{1+e^{-\alpha_i^Tz(x)}}.
\]

This model should be interpreted as an **effective decision surface in the calibration task**.

It is intentionally simpler than a general nonlinear “attraction utility.” Complexity is added only when diagnostics show the simpler model is inadequate.

### Model name

Provisional semantic name:

```text
visual-acceptance-linear-logit-v1
```

The name is a specification label, not evidence of validity.

## 4. Why preference magnitude and choice noise are not separately identified

A tempting model is

\[
P(A\succ B)
=\sigma\left[\gamma_i w_i^T(\phi_A-\phi_B)\right],
\]

where `w_i` is called preference strength/direction and `gamma_i` is called consistency or inverse noise.

But define

\[
\eta_i=\gamma_iw_i.
\]

Then the likelihood becomes

\[
P(A\succ B)=\sigma\left[\eta_i^T(\phi_A-\phi_B)\right].
\]

For any positive constant `c`, the pair

\[
(w_i,\gamma_i)
\]

and

\[
(cw_i,\gamma_i/c)
\]

produce exactly the same probabilities for every possible comparison.

Therefore the observations do not distinguish them.

### S1 decision

Do **not** persist separately named `preference_strength` and `choice_consistency` parameters from ordinary pairwise/acceptance data.

Persist only the effective identifiable coefficients until a later protocol adds an independent scale anchor or repeated-observation model that makes the decomposition testable.

This is an identifiability result, not an implementation preference.

## 5. Why pairwise comparisons alone cannot identify selectivity

For a linear score

\[
s_i(x)=b_i+\beta_i^T\phi(x),
\]

a forced comparison uses

\[
s_i(A)-s_i(B)
=\beta_i^T(\phi_A-\phi_B).
\]

The intercept `b_i` cancels exactly.

Thus forced `A versus B` choices can estimate relative preference direction but cannot identify whether the user would pursue either candidate at all.

### Consequence

A Mosaic calibration instrument that aims to learn **pursuit selectivity** must include an outside option / absolute acceptability observation.

## 6. Four-option pair response as two acceptability observations

The lowest-burden S1 instrument is:

> Which of these people would you be open to meeting?

Responses:

```text
A only
B only
Both
Neither
```

Encode this as two binary observations:

```text
A only   -> (Y_A, Y_B) = (1, 0)
B only   -> (0, 1)
Both     -> (1, 1)
Neither  -> (0, 0)
```

Under the provisional conditional-independence model,

\[
P(Y_A,Y_B\mid\alpha_i)
=P(Y_A\mid\alpha_i)P(Y_B\mid\alpha_i).
\]

This gives both an absolute outside-option signal and information about feature preference.

### Important diagnostic

Conditional independence is a scientific assumption, not a UI fact.

The same candidate should sometimes be paired with materially different comparison partners. If its acceptance probability changes systematically with the co-presented candidate after accounting for the model, Mosaic has detected a **pair-context/contrast effect** and the independent-threshold likelihood is misspecified.

Do not hide such an effect by merely widening posterior uncertainty.

## 7. Selectivity should initially be a derived operational quantity

Calling `-b_i` a universal psychological “threshold” is coordinate-dependent. If the feature representation is shifted or rescaled, the numerical intercept changes.

A more operationally stable quantity is the user's predicted acceptance rate over a versioned reference candidate distribution `P_ref`:

\[
q_i
=
E_{X\sim P_{ref}}
\left[\sigma(\alpha_i^Tz(X))\right].
\]

Define operational selectivity as

\[
S_i=1-q_i.
\]

This quantity remains tied to an explicit reference population and feature-basis version rather than pretending there is a coordinate-free scalar threshold.

The geometric `p=0.5` acceptance boundary remains useful:

\[
\alpha_i^Tz(x)=0,
\]

but its interpretation must remain basis-aware.

## 8. Bayesian individual state

Use a population-informed prior interface:

\[
\alpha_i\mid g_i
\sim
\mathcal N(\mu_{g_i},\Sigma_{g_i}),
\]

then update with individual observations:

\[
p(\alpha_i\mid D_i)
\propto
p(\alpha_i\mid g_i)
\prod_n p(y_{in}\mid z_n,\alpha_i).
\]

### Population prior rule

Group characteristics may change a **prior distribution** only when learned from suitable data and versioned explicitly. They must not hard-code final individual predictions.

The posterior from direct individual evidence is the operative state.

S1 does not yet establish which demographic/group variables improve priors or by how much.

## 9. Local Fisher information

For one binary acceptance observation with

\[
p=\sigma(\alpha_i^Tz),
\]

the Fisher information is

\[
\mathcal I(z)
=p(1-p)zz^T.
\]

The scalar multiplier is maximized at

\[
p=0.5,
\]

so, all else equal, a candidate near the current acceptance boundary is more locally informative than one the model believes will almost certainly be accepted or rejected.

For one four-option pair query under conditional independence:

\[
\mathcal I_q
=
 p_A(1-p_A)z_Az_A^T
+
 p_B(1-p_B)z_Bz_B^T.
\]

Each term is rank at most one, so each pair query contributes rank at most two to the local information matrix.

## 10. Minimal rank lower bound

The S1 linear model contains `d+1` effective parameters.

Because a four-option pair query contributes at most rank two,

\[
N_{pair}
\ge
\left\lceil\frac{d+1}{2}\right\rceil
\]

is a necessary local rank condition even in an idealized setting.

It is **not** sufficient for useful precision.

Noise, weak feature leverage, collinearity, prior misspecification, generator error, and the need for out-of-sample prediction all increase the required evidence.

For pure forced pairwise comparisons, one comparison contributes rank at most one and the intercept is never identified at all.

This is why Mosaic must not promise a fixed “20-question” or “30-question” calibration until dimension, prior strength, response noise, and target ranking precision are empirically characterized.

## 11. Active query design

Let the current posterior covariance be `Sigma_i`. A computationally convenient local Bayesian/D-optimal approximation to information gain from query `q` is

\[
G(q)
\approx
\frac12
\log\det\left(I+\Sigma_i\mathcal I_q\right).
\]

A burden-aware query score is

\[
J(q)
=
\frac{G(q)}{E[C(q)]},
\]

where `C(q)` can include expected response time, cognitive burden, generation cost, or other protocol costs.

### Query-design implications

Good queries should jointly:

1. lie near the current acceptance boundary when possible;
2. span directions in feature space that remain poorly identified;
3. avoid repeatedly sampling the same high-uncertainty region;
4. satisfy stimulus-generation/QC constraints; and
5. include deliberate model-diagnostic probes rather than maximizing information under a potentially wrong model forever.

When a real candidate pool exists, an even more relevant acquisition objective is expected reduction in downstream ranking regret rather than generic parameter entropy. S1 treats that as the preferred later policy target.

## 12. Information ceiling of the response format

A four-category response carries at most

\[
\log_2 4=2
\]

bits in an ideal noiseless balanced query.

Therefore `N` four-option queries provide at most `2N` raw response bits before accounting for noise or response imbalance.

This is a coarse information ceiling only. Continuous-parameter precision is governed by the likelihood geometry/Fisher information, not simply by counting nominal response bits.

## 13. Identifiability conditions

The effective S1 state is only identifiable to the extent that these conditions hold:

### 13.1 Fixed link scale

The logistic link is part of the model definition. Do not add a free global/person-specific noise scale and claim it is independently learned without a separate anchor.

### 13.2 Full-rank augmented design

The observed `z(x)` vectors must span the effective parameter space. A prior can regularize a weak direction but does not create experimental identification where the likelihood contains none.

### 13.3 Feature-space validity

The candidate representation must be versioned and the intended manipulated dimensions must actually correspond to generated stimuli.

### 13.4 No hidden perfect confounding

If the generator changes multiple attributes together whenever one nominal attribute changes, their causal effects cannot be separated from those observations.

### 13.5 Instrument invariance

Question wording, response semantics, presentation mode, and other instrument details are part of the measurement model. A changed instrument requires explicit versioning or a demonstrated bridge.

### 13.6 Domain restriction

Identification within a synthetic feature space does not imply transport to real photographs/profiles or face-to-face attraction.

## 14. Model misspecification tests

S1 should try to falsify the linear-logistic model before adding complexity.

### 14.1 Pair-context test

Present the same candidate against different comparison partners. Test whether its acceptance residual depends on partner context.

### 14.2 Local curvature test

Probe symmetric perturbations around a candidate region. Systematic residual curvature suggests a missing nonlinear term.

### 14.3 Interaction test

Use sparse factorial probes for selected feature pairs. Add an interaction only when predictive evidence supports it.

### 14.4 Multibasin/type test

Use broad held-out candidates. If one linear decision surface cannot predict separated high-acceptance regions without also predicting the intervening region, a multimodal/nonlinear representation is indicated.

### 14.5 Repetition/consistency test

Repeat a small randomized subset after sufficient spacing. This measures empirical response reproducibility but should not automatically be reified as an independent `gamma_i` parameter.

### 14.6 Synthetic-generator confounding test

Use image/feature QC and, where possible, independent encoders or human-neutral audits to detect unintended correlated changes between nominally controlled stimuli.

## 15. Complexity ladder

Do not begin with a universal high-dimensional neural utility.

Use the smallest model that survives diagnostics:

```text
M0: intercept only
    ↓
M1: low-dimensional linear logistic acceptance
    ↓
M2: sparse selected interactions / curvature
    ↓
M3: low-rank nonlinear/shared basis
    ↓
M4: mixture / multibasin model if specifically supported
```

Every step must improve held-out predictive behavior or downstream decision quality enough to justify the added sample burden and loss of interpretability.

## 16. Defining the minimum useful dimension

There is no justified universal value of `d` yet.

Define the operational dimension

\[
d^*
\]

as the smallest nested/shared representation for which additional dimensions fail to produce a meaningful improvement in predefined held-out objectives such as:

- predictive log loss on unseen controlled candidates;
- calibration of acceptance probabilities;
- held-out pair ordering;
- top-K/ranking regret on a reference bank; and
- posterior stability across resampling/model refits.

The chosen basis must also remain experimentally manipulable enough that informative queries can be generated.

Thus “low dimensional” is a hypothesis to test, not a number to assume.

## 17. Stopping rule

A fixed number of questions is not the S1 stopping criterion.

Stop individual calibration only when all required conditions are satisfied:

1. **coverage:** the effective information/design matrix has no unresolved required direction;
2. **predictive stability:** posterior draws rarely change decisions/rankings that matter on the reference bank;
3. **information exhaustion:** the best admissible next query has expected gain below a predefined burden-adjusted threshold;
4. **diagnostic adequacy:** prespecified misspecification checks do not show a material failure requiring a richer model; and
5. **minimum reliability:** the instrument has enough repeated/control evidence to detect gross inconsistency or stimulus failure.

A hard maximum query budget may still be imposed for product burden, but reaching the budget means “uncertainty remains,” not “the user is fully calibrated.”

## 18. What S1 can establish analytically/synthetically

Without real-world human outcome data, S1 can still establish:

- exact parameter invariances/non-identifiabilities;
- rank conditions for experimental designs;
- correctness of Bayesian/posterior computation on synthetic ground truth;
- active-policy efficiency relative to passive policies under known simulations;
- whether stopping rules achieve target synthetic ranking regret under stated generative assumptions;
- sensitivity to noise, dimensionality, priors, interactions, and multimodality; and
- recovery/provenance behavior of derived posterior state.

## 19. What S1 cannot establish without external validation

S1 alone cannot establish:

- that synthetic facial/image dimensions match the perceptual dimensions people actually use;
- that a user's synthetic-candidate acceptance surface transfers to real-person attraction;
- that profile interest predicts in-person chemistry;
- that initial attraction predicts relationship formation;
- that any preinteraction model predicts long-term relationship quality;
- that a group prior is fair, transportable, or beneficial in a deployment population; or
- that one model class is universally adequate across users/cultures/orientations.

These remain later validation problems.

## 20. Literature anchors

This specification is consistent with several relevant results, while not treating them as proof that Mosaic's specific model is valid:

- Guo, Sanner & Bonilla (NeurIPS 2010), *Gaussian Process Preference Elicitation*: Bayesian preference elicitation can share information across users and use value-of-information query selection.
- Ge, Juba & Vorobeychik (2024), *Learning Linear Utility Functions From Pairwise Comparison Queries*: parameter recovery from pairwise queries depends strongly on assumptions; active querying can qualitatively improve learnability over passive sampling.
- Bergström et al. (NeurIPS 2024), *Active preference learning for ordering items in- and out-of-sample*: contextual item structure and explicit aleatoric/epistemic uncertainty can improve active pair selection and out-of-sample ordering.
- De Peuter et al. (NeurIPS 2024), *Preference Learning of Latent Decision Utilities with a Human-like Model of Preferential Choice*: simplified Bradley-Terry-style choice models can miss human context effects, motivating explicit misspecification checks.
- Eastwick & Finkel (JPSP 2008): stated ideal preferences failed to predict what inspired desire in their speed-dating study, supporting Mosaic's decision not to equate self-reported ideals with revealed preference.
- Eastwick et al. (JPSP 2025; published online 2024), *A Worldwide Test of the Predictive Validity of Ideal Partner Preference-Matching*: highly powered cross-national results found statistically significant but modest person-specific preference-matching effects after accounting for normative desirability, reinforcing the need to distinguish common population attractiveness from individualized preference structure.

## 21. Immediate next theoretical/engineering checkpoint

Implement a **pure synthetic ground-truth study** of the S1 model and active policy before changing the live calibration semantics.

The study should vary:

```text
dimension d
prior concentration / misspecification
true coefficient geometry
acceptance prevalence
response noise induced through the effective logistic slope
generator-feature perturbation error
query policy: random vs boundary-only vs D-optimal/burden-aware
model misspecification: interaction / nonlinear / multibasin
```

Primary outputs:

```text
posterior coefficient error
predictive log loss
probability calibration
top-K/ranking regret
number of pair queries to stopping
false stopping rate
misspecification detection rate
```

Only after this simulation should Mosaic choose a provisional feature dimension and query budget for an actual scientific calibration protocol.
