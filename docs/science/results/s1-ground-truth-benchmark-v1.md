# S1 Ground-Truth Benchmark v1

## Status

Completed computational result under a deliberately restricted synthetic model.

This is **not** human-subject evidence, attraction validation, matchmaking validation, or evidence that the linear-logistic model is adequate for real users.

## Provenance

- benchmark version: `s1-ground-truth-benchmark-v1`
- fitted model version: `visual-acceptance-linear-logit-v1`
- science branch source head used by the benchmark workflow: `06e1b3d3f3e234db427fbb651f942548dfddc57d`
- GitHub Actions run: `31841535276`
- benchmark artifact ID: `9234429023`
- artifact ZIP SHA-256: `fb05298e25c578d3fc395f98728b4f6c324fff10262e8975e89c307b935ed773`
- original pretty JSON SHA-256: `3614ecdfdc4102dd18baa7fc30127a49b03d2952e51a6ac8cb4c774621a4ba88`

The one-use benchmark workflow had read-only repository permission and was removed immediately after the result was captured.

## Experimental configuration

```text
feature dimensions       d = 2, 4, 8
pair-query budgets        q = 5, 10, 20, 30
policies                  random, boundary, d_optimal
scenario seeds            0..11 (12 per cell)
candidate query bank      18 synthetic feature vectors
held-out reference bank   96 synthetic feature vectors
top-K                     8
prior mean                0
prior variance            4 per effective coefficient
slope scale               0.9 / sqrt(d) per generated coefficient
true intercept            0
response model            correctly specified linear-logistic Bernoulli acceptance
```

Each pair yields two binary acceptability observations under the provisional conditional-independence model. The same synthetic scenario seed is reused across policies. Adaptive policies therefore face the same underlying true user state and candidate banks but select different observations.

## Mean results

| d | q | policy | log loss | prob MSE | top-K regret | top-K overlap | coef RMSE | coverage | conv |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | 5 | random | 0.7866 | 0.0463 | 0.0818 | 0.635 | 0.7843 | 1.000 | 1.000 |
| 2 | 5 | boundary | 0.8796 | 0.0696 | 0.1159 | 0.552 | 0.9446 | 1.000 | 1.000 |
| 2 | 5 | d_optimal | 0.8535 | 0.0630 | 0.0892 | 0.531 | 0.8800 | 0.972 | 1.000 |
| 2 | 10 | random | 0.7602 | 0.0439 | 0.0768 | 0.562 | 0.6726 | 0.972 | 1.000 |
| 2 | 10 | boundary | 0.8058 | 0.0474 | 0.0474 | 0.667 | 0.8574 | 1.000 | 1.000 |
| 2 | 10 | d_optimal | 0.7091 | 0.0290 | 0.0562 | 0.688 | 0.5398 | 0.972 | 1.000 |
| 2 | 20 | random | 0.6763 | 0.0176 | 0.0155 | 0.771 | 0.4046 | 0.944 | 1.000 |
| 2 | 20 | boundary | 0.7313 | 0.0286 | 0.0124 | 0.833 | 0.6791 | 1.000 | 1.000 |
| 2 | 20 | d_optimal | 0.6590 | 0.0124 | 0.0308 | 0.677 | 0.3515 | 0.972 | 1.000 |
| 2 | 30 | random | 0.6496 | 0.0088 | 0.0123 | 0.771 | 0.3008 | 1.000 | 1.000 |
| 2 | 30 | boundary | 0.6939 | 0.0204 | 0.0088 | 0.865 | 0.5104 | 1.000 | 1.000 |
| 2 | 30 | d_optimal | 0.6446 | 0.0074 | 0.0140 | 0.750 | 0.2607 | 0.972 | 0.917 |
| 4 | 5 | random | 0.9583 | 0.0949 | 0.1553 | 0.396 | 0.9092 | 0.983 | 1.000 |
| 4 | 5 | boundary | 0.9996 | 0.0862 | 0.1053 | 0.448 | 1.0251 | 1.000 | 1.000 |
| 4 | 5 | d_optimal | 0.9956 | 0.0996 | 0.1299 | 0.396 | 0.9924 | 0.983 | 1.000 |
| 4 | 10 | random | 0.8429 | 0.0641 | 0.1200 | 0.490 | 0.7241 | 0.983 | 1.000 |
| 4 | 10 | boundary | 1.0334 | 0.0830 | 0.0749 | 0.521 | 1.0953 | 0.933 | 1.000 |
| 4 | 10 | d_optimal | 0.9243 | 0.0787 | 0.1001 | 0.406 | 0.8821 | 0.933 | 1.000 |
| 4 | 20 | random | 0.7084 | 0.0314 | 0.0912 | 0.490 | 0.3924 | 0.967 | 1.000 |
| 4 | 20 | boundary | 0.9178 | 0.0685 | 0.0767 | 0.427 | 0.9052 | 0.883 | 1.000 |
| 4 | 20 | d_optimal | 0.7476 | 0.0383 | 0.0952 | 0.448 | 0.5570 | 0.933 | 1.000 |
| 4 | 30 | random | 0.6778 | 0.0222 | 0.0543 | 0.573 | 0.3312 | 0.983 | 1.000 |
| 4 | 30 | boundary | 0.7970 | 0.0469 | 0.0511 | 0.562 | 0.6717 | 0.917 | 1.000 |
| 4 | 30 | d_optimal | 0.6643 | 0.0180 | 0.0455 | 0.573 | 0.3314 | 0.967 | 1.000 |
| 8 | 5 | random | 1.0523 | 0.1011 | 0.1983 | 0.250 | 0.7712 | 1.000 | 1.000 |
| 8 | 5 | boundary | 1.1162 | 0.1110 | 0.1863 | 0.271 | 0.8488 | 1.000 | 1.000 |
| 8 | 5 | d_optimal | 1.1441 | 0.1254 | 0.2215 | 0.219 | 0.8727 | 1.000 | 1.000 |
| 8 | 10 | random | 1.0316 | 0.1031 | 0.1757 | 0.281 | 0.7173 | 0.991 | 1.000 |
| 8 | 10 | boundary | 1.2073 | 0.1196 | 0.1619 | 0.333 | 0.9489 | 0.954 | 1.000 |
| 8 | 10 | d_optimal | 1.1967 | 0.1174 | 0.1753 | 0.271 | 0.9717 | 0.926 | 1.000 |
| 8 | 20 | random | 0.9621 | 0.0900 | 0.1895 | 0.219 | 0.6564 | 0.917 | 1.000 |
| 8 | 20 | boundary | 1.2056 | 0.1208 | 0.1890 | 0.188 | 0.9557 | 0.917 | 1.000 |
| 8 | 20 | d_optimal | 1.0099 | 0.0815 | 0.0995 | 0.385 | 0.7732 | 0.944 | 1.000 |
| 8 | 30 | random | 0.7788 | 0.0525 | 0.1533 | 0.302 | 0.4212 | 0.963 | 1.000 |
| 8 | 30 | boundary | 1.1685 | 0.1151 | 0.1919 | 0.229 | 0.9183 | 0.843 | 1.000 |
| 8 | 30 | d_optimal | 0.9576 | 0.0798 | 0.1302 | 0.396 | 0.6794 | 0.926 | 1.000 |

`prob MSE` is the mean squared error between the inferred and true acceptance probabilities on the held-out bank. It is equivalent to the reducible/excess part of expected Brier risk under the known Bernoulli ground truth. `coverage` is the average fraction of true effective coefficients falling inside nominal marginal Laplace `mean ± 1.96 sigma` intervals; it is only a rough small-sample diagnostic.

## Main result 1 — no policy dominates all scientific objectives

The benchmark rejects the simple proposition:

```text
maximize local Fisher/D-optimal information
        ⇒
best out-of-sample candidate ranking
```

The objectives can diverge materially.

At `d=2, q=20`, D-optimal querying improved the global model relative to random sampling:

```text
probability MSE   0.0176 → 0.0124
coefficient RMSE  0.4046 → 0.3515
log loss          0.6763 → 0.6590
```

but mean top-K regret worsened:

```text
0.0155 → 0.0308
```

and mean top-K overlap fell:

```text
0.771 → 0.677
```

The reverse pattern appears strongly in the harder `d=8, q=20` regime. D-optimal querying reduced mean top-K regret from

```text
0.1895 → 0.0995
```

and increased top-K overlap from

```text
0.219 → 0.385
```

while raw expected log loss was slightly worse than random (`1.0099` versus `0.9621`). Probability MSE was slightly better (`0.0815` versus `0.0900`), showing that different global scoring rules can themselves emphasize different errors.

Therefore Mosaic should not use generic parameter information gain as a proxy for the terminal ranking objective without testing that correspondence.

## Main result 2 — boundary-only querying is not a sufficient active policy

Sampling candidates merely because the current model predicts acceptance near `p=0.5` is not enough. It often has substantially worse coefficient/probability recovery because it does not explicitly ensure coverage of unresolved feature directions.

The clearest failure is `d=8, q=30`:

```text
                        random      boundary
probability MSE         0.0525      0.1151
coefficient RMSE        0.4212      0.9183
top-K regret            0.1533      0.1919
top-K overlap           0.302       0.229
nominal interval cover  0.963       0.843
```

Boundary sampling remains useful as a component of query design because `p(1-p)` is largest near 0.5, but it is not a complete design criterion.

## Main result 3 — a fixed 20–30 pair budget is not justified

Even in the **correctly specified** synthetic model, with perfectly known feature vectors and no generator confounding, 30 pair queries (= 60 binary acceptability observations) do not reliably reconstruct the `d=8` state well enough to call calibration complete.

At `d=8, q=30`:

```text
policy      top-K regret   top-K overlap   probability MSE
random          0.1533          0.302           0.0525
d_optimal       0.1302          0.396           0.0798
```

The exact values belong only to this simulation regime, but the qualitative conclusion is robust: satisfying the rank lower bound is far weaker than achieving useful predictive precision. A product query cap must leave unresolved uncertainty explicit.

## Main result 4 — the nominal D-optimal policy has an early-design vulnerability

At a broad zero-centered prior, every candidate initially has plug-in MAP acceptance near `p=0.5`. The local D-optimal criterion can therefore be driven strongly by feature leverage before enough response evidence exists to localize the decision surface.

The v1 result is consistent with an early aggressive-design penalty in several cells. This is not yet proven as the causal mechanism because the benchmark does not retain per-query diagnostic trajectories. It motivates testing:

- a short random/space-filling bootstrap before D-optimal selection;
- posterior-integrated rather than plug-in-MAP information gain; and
- an acquisition objective aligned directly with downstream ranking regret/stability.

## Numerical diagnostic

All fits reported `converged=True` except one of 12 `d=2, q=30, d_optimal` runs, giving convergence rate `0.9167` in that cell. The result was still scored, but the failure must be investigated before a larger benchmark. The current `1e-9` Newton-step tolerance plus final gradient check is intentionally strict; the cause should be diagnosed rather than simply loosening the criterion.

## Important v1 metric limitation discovered after execution

`expected_log_loss` is cross-entropy against the true Bernoulli probability. Its absolute value includes irreducible Bernoulli entropy:

\[
H(p)=-p\log p-(1-p)\log(1-p).
\]

Therefore absolute raw log loss should **not** be compared across different ground-truth scenario distributions as though all of it were model error.

The next benchmark must record:

\[
L_{excess}
=
L_{cross-entropy}-E[H(p)]
=
E[D_{KL}(Bern(p)\|Bern(\hat p))],
\]

which is the reducible calibration/prediction loss.

The existing `probability_mse` already has a clean reducible interpretation: it is the excess Brier component above the oracle Bernoulli variance.

## Distribution examples

The 12-seed distributions are broad enough that means should not be treated as stable policy rankings.

For `d=8, q=20` top-K regret:

```text
policy       median    p10     p90
random       0.1584   0.0620  0.3139
d_optimal    0.0650   0.0398  0.2136
```

For `d=2, q=20` top-K regret:

```text
policy       median    p10     p90
random       0.0065   0.0000  0.0188
d_optimal    0.0098   0.0011  0.0947
```

These distributions motivate a larger paired scenario study rather than significance claims from 12 seeds.

## Limitations

V1 deliberately does **not** answer the deployment question.

Major limitations:

1. only 12 scenario seeds per cell;
2. aggregate summaries were stored, not per-seed results, so paired uncertainty on policy differences cannot be reconstructed from the artifact;
3. one prior variance, slope scale, intercept, Gaussian feature distribution, candidate-bank size, and top-K were tested;
4. the fitted model exactly matched the ground-truth likelihood;
5. there were no pair-context effects, nonlinearities, interactions, multimodal preference regions, generator errors, or prior misspecification;
6. all synthetic feature values were observed without error;
7. the four-option response was represented by conditionally independent Bernoulli acceptance outcomes;
8. Laplace marginal coverage is only an approximation; and
9. the shared response-RNG sequence is a common-random-number device across adaptive policies, not a literal candidate-level counterfactual response.

## Next benchmark requirements

Before drawing a query-policy conclusion:

1. store per-seed/per-cell metrics;
2. add oracle entropy and excess log loss;
3. investigate the one convergence failure;
4. expand seeds substantially for the most informative cells;
5. test a bootstrap/hybrid D-optimal policy;
6. test a ranking-aligned acquisition criterion against generic D-optimal information gain;
7. then introduce prior misspecification and deliberate model misspecification.

The first benchmark has therefore succeeded mainly by **rejecting an overly simple design rule**. Mosaic should optimize the information that changes downstream decisions, not assume that all parameter information has equal matchmaking value.
