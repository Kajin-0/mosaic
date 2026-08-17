# S1 Resolution–Horizon Benchmark v13c

## Status

Completed synthetic method benchmark after `s1-finite-confidence-geometry-benchmark-v13b`.

v13b established that the finite-grid e-process confidence-set geometry can give structurally safe directional stopping, but the strict target `epsilon = 0.15` did not stop at all by 120 observations on the 15-degree grid. v13c separates two candidate explanations:

1. angular-grid quantization; and
2. insufficient evidence accumulation under the current predictable numerator/query policy.

The conclusion is that **both matter, but evidence accumulation is the dominant bottleneck over the tested range**.

## Exact provenance

- GitHub Actions workflow run: `31903626748`
- benchmark job: `95058040578`
- exact benchmark head: `1c4f6e530bcf6d41201eb4a2813909dbcd53b6d4`
- artifact ID: `9251807785`
- artifact name: `s1-resolution-horizon-benchmark-v13c`
- artifact ZIP SHA256: `f2fc6048ad7dc5779b9206a0d3d7933c7af444bcae855a6b9a4100cd99872f8b`
- benchmark JSON SHA256: `b557cb48f491666de2e6a45efa7db7cb11a7c8f6015cfe1ebfb6c6f69f35995a`
- artifact retention expiry: 2026-08-29

The Actions gate passed Ruff lint, Ruff formatting, mypy, and the full engine pytest suite before the benchmark executed.

## Frozen method components

v13c intentionally does **not** tune the e-process after seeing v13b outcomes. The following components are frozen:

- binary linear-logistic likelihood;
- slope norm `B = 0.9`;
- nominal anytime level `alpha = 0.05`;
- candidate bank size `12`;
- predictable numerator: uniform-prior finite likelihood-mixture predictive;
- query design: maximize the acceptance-probability range over the previous confidence set;
- strict target `epsilon = 0.15`, equivalent to `27 degrees`;
- stopping semantics: stop only when the exact finite confidence-set directional radius around the retained maximum-likelihood direction is at most the target.

Only grid spacing and observation horizon vary.

## Design

Angular grid spacings:

- `15 degrees` -> 24 parameter directions;
- `10 degrees` -> 36 parameter directions;
- `5 degrees` -> 72 parameter directions.

All truth directions are shared and lie exactly on every grid:

`0, 30, 60, ..., 330 degrees`.

Each grid uses 64 synthetic response seeds per true direction, for `12 × 64 = 768` paths per spacing.

Observation horizons:

- 120;
- 180;
- 240 binary observations.

Because the finite-grid radius can only move in grid increments, the nominal `27 degree` target has the following effective finite-grid radii:

- 15-degree grid -> 15 degrees;
- 10-degree grid -> 20 degrees;
- 5-degree grid -> 25 degrees.

Thus finer resolution removes an artificial conservatism that is especially severe on the 15-degree grid.

## Results

| Grid spacing | Parameters | Effective radius | Horizon | Stop rate | False-stop rate | Truth excluded ever | Median stop |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 15° | 24 | 15° | 120 | 0.0000 | 0.0000 | 0.0313 | — |
| 15° | 24 | 15° | 180 | 0.0000 | 0.0000 | 0.0326 | — |
| 15° | 24 | 15° | 240 | 0.0273 | 0.0000 | 0.0326 | 235 |
| 10° | 36 | 20° | 120 | 0.0000 | 0.0000 | 0.0247 | — |
| 10° | 36 | 20° | 180 | 0.0000 | 0.0000 | 0.0273 | — |
| 10° | 36 | 20° | 240 | 0.0339 | 0.0000 | 0.0273 | 236.5 |
| 5° | 72 | 25° | 120 | 0.0000 | 0.0000 | 0.0299 | — |
| 5° | 72 | 25° | 180 | 0.0000 | 0.0000 | 0.0339 | — |
| 5° | 72 | 25° | 240 | 0.0755 | 0.0000 | 0.0339 | 237 |

At 240 observations, grid refinement from 15 degrees to 5 degrees increases the stop rate from `21/768 = 2.73%` to `58/768 = 7.55%`, roughly a 2.76× relative increase.

However, **all three resolutions have zero stops through 180 observations**. Even at 240 observations, more than 92% of paths on the finest grid remain uncertified.

No false stop occurred in any v13c cell.

The anytime truth-exclusion rate remains about 2.5–3.4%, compatible with the nominal 5% structural guarantee and broadly similar across resolution choices.

## Interpretation

### 1. Grid quantization is real

The 15-degree grid forces a nominal 27-degree certificate to satisfy an effective 15-degree finite-grid radius. Refining the grid to 5 degrees relaxes that artificial requirement to 25 degrees and measurably increases stopping.

Therefore the zero-stop v13b result at `epsilon = 0.15` was partly a discretization artifact.

### 2. Discretization is not the main burden problem

If discretization were the dominant issue, the 5-degree grid should have produced substantial stopping well before the 240-observation cap. It does not.

The median stop among the few successful 5-degree paths is observation 237. The certificate is therefore accumulating enough directional evidence only at the very end of the tested horizon.

The dominant unresolved issue is **confidence-set contraction rate under the current predictable numerator and disagreement query policy**.

### 3. The safety/efficiency separation is now useful

Unlike the v12 posterior-q95 family, v13 does not need to trade safety away to investigate efficiency. Any normalized predictable numerator preserves the fixed-parameter e-process validity theorem, and predictable adaptive queries are permitted.

The next experiments can therefore optimize evidence accumulation while retaining the same confidence-set geometric stopping semantics.

## What v13c establishes

Within the correctly specified finite two-dimensional logistic harness:

- the v13 confidence-set stopping construction remains safe under finer grids and longer optional stopping;
- coarse angular discretization contributes material conservatism;
- removing most of that discretization penalty is insufficient to make the strict target practical;
- the current method is primarily **evidence-limited**, not resolution-limited, at `epsilon = 0.15`.

## What it does not establish

v13c does not establish:

- a continuous-parameter confidence certificate;
- acceptable human calibration burden;
- that the current numerator is efficient or optimal;
- that the current disagreement query rule is efficient or optimal;
- validity under model misspecification;
- a validated visual feature basis;
- synthetic-to-real preference transfer;
- compatibility or relationship prediction.

## Next exact checkpoint

The next isolated efficiency question should be **predictable-numerator regret**, before changing query design.

On the 5-degree finite grid, keep the likelihood, target, confidence geometry, candidate bank, truth set, and disagreement query policy fixed. Prospectively compare a small set of theorem-valid predictable numerators, including:

1. the existing finite likelihood-mixture predictive control;
2. a one-step-lagged finite-grid maximum-likelihood plug-in predictive;
3. a likelihood-weighted predictive restricted to the previous confidence set.

All are normalized and chosen before the current response, so the e-process validity argument is unchanged. The primary outcome is strict-target stop rate / stopping burden; truth-exclusion and false stopping remain safety diagnostics.

Do not choose a winning numerator and then evaluate it on the same paths as though that were prospective validation. A subsequent fresh-seed checkpoint is required before promoting an efficiency change.
