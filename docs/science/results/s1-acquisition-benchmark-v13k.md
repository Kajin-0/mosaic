# S1 acquisition-policy benchmark v13k

## Question

After v13j established the 11-point candidate-specific cone-cover numerator as the leading finite-grid certificate, does changing only the query controller reduce strict-target burden?

The comparison intentionally freezes the v13j numerator, nested confidence representation, 5-degree parameter grid, `B=0.9`, target directional error `0.15` (27 degrees), alpha `0.05`, 12-point candidate bank, logistic likelihood, and global finite-grid MLE reporting center.

Only acquisition changes:

- `historical_all_grid_current`: probability-range disagreement over the historical current-time all-grid-mixture confidence set;
- `nested_cone_cover`: probability-range disagreement over the surviving nested cone-cover confidence set.

The two controllers therefore generate different adaptive query/response trajectories. Fresh seeds `832..959` are coupled by true direction and RNG seed, giving 1,536 paths per arm over 12 true directions.

## Prospective endpoints

Primary endpoints were paired stopping probability at 180 and 240 observations plus stopping-time behavior. Zero geometric violations remained a hard structural invariant.

## Result

| acquisition | horizon | stop rate | false-stop rate | truth excluded ever | nested empty | median stop |
|---|---:|---:|---:|---:|---:|---:|
| historical all-grid current | 120 | 0.0651% | 0.0651% | 2.7344% | 0.1302% | 108 |
| nested cone-cover | 120 | 0.1953% | 0.0000% | 3.3854% | 0.0000% | 103 |
| historical all-grid current | 180 | 5.4688% | 0.1302% | 3.1250% | 0.2604% | 172.5 |
| nested cone-cover | 180 | **10.2865%** | 0.3255% | 3.6458% | 0.1302% | 170.5 |
| historical all-grid current | 240 | **88.6719%** | 0.4557% | 3.2552% | 0.5859% | 211 |
| nested cone-cover | 240 | 87.9557% | 1.3021% | 3.7760% | 0.1953% | **207** |

At 180 observations the nested-survivor controller materially accelerates early certification:

- candidate-only stops: 142;
- historical-only stops: 68;
- both: 16;
- neither: 1,310;
- paired exact `p = 3.61e-7`.

At 240 observations that advantage disappears:

- candidate-only stops: 126;
- historical-only stops: 137;
- both: 1,225;
- neither: 48;
- paired exact `p = 0.5376`.

Among paths stopping under both controllers by 240, nested-survivor acquisition finished earlier on 632 paths with median gain 18 observations, while historical acquisition finished earlier on 536 paths with median gain 13.5 observations. Thus the candidate changes the timing distribution, but not terminal completion probability at the prespecified horizon.

The candidate also increases path-level truth exclusion from `50/1536 = 3.2552%` to `58/1536 = 3.7760%` and false directional stops from `7/1536 = 0.4557%` to `20/1536 = 1.3021%` by 240. Both remain below the nominal 5% simultaneous-confidence budget, but the direction of change is adverse and there is no compensating 240-observation completion gain.

**Geometry violations were zero in both arms.** Every false directional stop occurred only after the true finite-grid parameter had already left the nested confidence sequence, exactly as the confidence-set geometry argument predicts.

## Interpretation

The acquisition result is mixed but not promotable as the new default.

The nested cone-cover survivor set is a more focused query target and approximately doubles the 180-observation stop rate. However, that gain is transient: by 240 observations the historical controller is statistically indistinguishable in completion probability and has lower observed truth-exclusion and false-stop rates.

The scientific conclusion is therefore:

1. query-policy choice can materially reshape *when* certificates arrive;
2. focusing only on current survivors can accelerate some paths without increasing final-horizon completion;
3. aggressive survivor-focused acquisition may increase the chance that an unlucky early confidence-sequence exclusion steers later queries into a narrower self-reinforcing region;
4. do not optimize acquisition against the 180-observation endpoint alone;
5. retain `historical_all_grid_current` as the finite-grid default unless a future acquisition rule improves the full burden/safety tradeoff prospectively.

This closes the immediate finite-grid acquisition-tuning checkpoint. Do not hand-tune mixtures of the two policies on v13k outcomes.

## Next checkpoint

Move to a **continuous confidence-geometry certificate** while preserving theorem-level validity.

The continuous parameter confidence set should be constructed first and only then evaluated geometrically around a data-dependent reporting direction. In the 2-D slope case, an angular cone with half-angle below 90 degrees is the intersection of two linear halfspaces in slope space. Its complement is the union of two halfspace violations. This gives a promising convex feasibility formulation for each side of the cone even with nuisance intercept and slope magnitude.

The unresolved numerical requirement is crucial: a claimed empty outside-cone intersection must come from a certified upper bound on the best feasible likelihood/confidence margin. A local optimizer or approximate grid that can underestimate the outside-cone supremum is anti-conservative and cannot certify stopping.

## Provenance

- workflow: `Science S1 Acquisition Benchmark v13k`
- successful run: `31975935483`
- job: `95235316730`
- exact benchmark head: `6e82ec5b752cd330a1db6f01ee5917a80a3fc3cc`
- artifact: `9271210161`, `s1-acquisition-benchmark-v13k`
- artifact ZIP SHA256: `ea129002963b6b7d8b82312e7c49a65b0471714b84ebc5e54e95bb6e222c690d`
- JSON SHA256: `c54203ce8046e84a6603e35de95367328d04201482267225ea79740236ab16e2`
- JSON size: `1,610,724` bytes
- validation on exact head: Ruff clean, Ruff format clean, mypy clean, full engine pytest passed

## Scope

This remains a correctly specified synthetic 2-D finite-grid logistic benchmark. It is not evidence for a validated human visual feature basis, synthetic-to-real transfer, an adequate linear model, relationship compatibility, or long-term relationship outcomes.