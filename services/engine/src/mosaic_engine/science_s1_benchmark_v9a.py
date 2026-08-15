from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from statistics import mean

from .science_s1_benchmark_v7a import pair_query_count, realized_kappa
from .science_s1_benchmark_v8a import (
    _metric_summary,
    _ranking_summary,
    _response_seed,
    _scenario_seed,
    _slope_direction_metrics,
)
from .science_s1_controlled_design import (
    centered_orthogonalized_candidate_bank,
    controlled_design_diagnostics,
)
from .science_s1_simulation import make_gaussian_scenario
from .science_s1_v6_simulation import run_ground_truth_simulation_v6

BENCHMARK_VERSION = "s1-gaussian-controlled-geometry-benchmark-v9a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
QUERY_DESIGN_VERSION = "centered-orthogonalized-gaussian-v1"
POLICIES = (
    "random",
    "posterior_fisher_d_optimal",
    "exact_gaussian_score_regret",
)
FEATURE_DIMENSIONS = (2, 4, 8, 12)
KAPPA_TARGETS = (2.0, 4.0, 6.0, 8.0, 12.0)
SEEDS = tuple(range(4))
CANDIDATE_COUNT = 18
HELDOUT_COUNT = 96
TOP_K = 8
PRIOR_VARIANCE = 4.0
SLOPE_SCALE = 0.9
INTERCEPT = 0.0


def run_benchmark_v9a(
    *,
    feature_dimensions: Iterable[int] = FEATURE_DIMENSIONS,
    kappa_targets: Iterable[float] = KAPPA_TARGETS,
    policies: Iterable[str] = POLICIES,
    seeds: Iterable[int] = SEEDS,
    candidate_count: int = CANDIDATE_COUNT,
    heldout_count: int = HELDOUT_COUNT,
    top_k: int = TOP_K,
    prior_variance: float = PRIOR_VARIANCE,
    slope_scale: float = SLOPE_SCALE,
    intercept: float = INTERCEPT,
) -> dict[str, object]:
    dimensions = tuple(feature_dimensions)
    targets = tuple(float(value) for value in kappa_targets)
    policy_names = tuple(policies)
    seed_values = tuple(seeds)

    if not dimensions or any(dimension <= 0 for dimension in dimensions):
        raise ValueError("feature dimensions must be positive")
    if not targets or any(target <= 0.0 for target in targets):
        raise ValueError("kappa targets must be positive")
    if not policy_names or not seed_values:
        raise ValueError("policies and seeds must not be empty")
    if candidate_count < 2 or heldout_count <= 0:
        raise ValueError("synthetic bank counts must be positive")
    if any(dimension >= candidate_count for dimension in dimensions):
        raise ValueError("controlled Gaussian design requires candidate_count > feature_dimension")
    if top_k <= 0 or top_k > heldout_count:
        raise ValueError("top_k must be within the held-out bank")
    if prior_variance <= 0.0:
        raise ValueError("prior_variance must be positive")

    maximum_unique_pairs = candidate_count * (candidate_count - 1) // 2
    cells: list[dict[str, object]] = []
    raw_runs: list[dict[str, object]] = []
    design_diagnostics: list[dict[str, object]] = []

    for feature_dimension in dimensions:
        prior_mean = (0.0,) * (feature_dimension + 1)
        prior_variances = (prior_variance,) * (feature_dimension + 1)
        scenarios = {}
        for seed in seed_values:
            true_alpha, raw_candidates, heldout = make_gaussian_scenario(
                feature_dimension=feature_dimension,
                candidate_count=candidate_count,
                heldout_count=heldout_count,
                seed=_scenario_seed(feature_dimension, seed),
                slope_scale=slope_scale,
                intercept=intercept,
            )
            controlled_candidates = centered_orthogonalized_candidate_bank(raw_candidates)
            diagnostics = controlled_design_diagnostics(controlled_candidates)
            design_diagnostics.append(
                {
                    "seed": seed,
                    **asdict(diagnostics),
                }
            )
            scenarios[seed] = (true_alpha, controlled_candidates, heldout)

        ignored_reference = ((0.0,) * feature_dimension,)

        for target in targets:
            query_count = pair_query_count(
                feature_dimension=feature_dimension,
                kappa_target=target,
            )
            if query_count > maximum_unique_pairs:
                raise ValueError("kappa target exceeds the finite unique candidate-pair pool")
            kappa = realized_kappa(
                feature_dimension=feature_dimension,
                query_count=query_count,
            )

            for policy in policy_names:
                results = []
                direction_metrics = []
                for seed in seed_values:
                    true_alpha, controlled_candidates, heldout = scenarios[seed]
                    result = run_ground_truth_simulation_v6(
                        policy=policy,
                        true_alpha=true_alpha,
                        candidates=controlled_candidates,
                        reference_differences=ignored_reference,
                        heldout_features=heldout,
                        prior_mean=prior_mean,
                        prior_variances=prior_variances,
                        query_count=query_count,
                        top_k=top_k,
                        seed=_response_seed(feature_dimension, seed),
                    )
                    results.append(result)
                    direction = _slope_direction_metrics(
                        true_alpha,
                        result.posterior.mean,
                        result.posterior.covariance,
                    )
                    direction_metrics.append(direction)
                    scores = result.selected_acquisition_scores
                    raw_runs.append(
                        {
                            "feature_dimension": feature_dimension,
                            "parameter_count": feature_dimension + 1,
                            "kappa_target": target,
                            "realized_kappa": kappa,
                            "query_count": query_count,
                            "binary_observation_count": 2 * query_count,
                            "policy": policy,
                            "seed": seed,
                            "query_design_version": QUERY_DESIGN_VERSION,
                            "converged": result.posterior.converged,
                            "iterations": result.posterior.iterations,
                            "selected_pairs": result.selected_pairs,
                            "acquisition_score_mean": mean(scores) if scores else None,
                            "acquisition_score_min": min(scores) if scores else None,
                            "acquisition_score_max": max(scores) if scores else None,
                            "negative_acquisition_score_count": sum(
                                score < -1e-12 for score in scores
                            ),
                            "metrics": asdict(result.metrics),
                            "ranking_metrics": asdict(result.ranking_metrics),
                            "direction_metrics": direction,
                        }
                    )

                cells.append(
                    {
                        "feature_dimension": feature_dimension,
                        "parameter_count": feature_dimension + 1,
                        "kappa_target": target,
                        "realized_kappa": kappa,
                        "query_count": query_count,
                        "binary_observation_count": 2 * query_count,
                        "policy": policy,
                        "runs": len(results),
                        "query_design_version": QUERY_DESIGN_VERSION,
                        "convergence_rate": mean(
                            1.0 if result.posterior.converged else 0.0 for result in results
                        ),
                        "metrics": _metric_summary([result.metrics for result in results]),
                        "ranking_metrics": _ranking_summary(
                            [result.ranking_metrics for result in results]
                        ),
                        "direction_metrics": {
                            name: _metric_summary_value(direction_metrics, name)
                            for name in direction_metrics[0]
                        },
                    }
                )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "scientific_scope": (
            "Exploratory synthetic replication of the S1 v8a geometry result using a stochastic "
            "Gaussian-derived query bank. Each v7a iid-Gaussian bank is column-centered and "
            "orthogonalized/rescaled to identity empirical covariance. True alpha, held-out "
            "population, response stream, policies, dimensions, kappa targets, and candidate "
            "count remain paired to v7a. Four seeds are screening evidence only."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "kappa_targets": targets,
            "policies": policy_names,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "heldout_count": heldout_count,
            "top_k": top_k,
            "prior_variance": prior_variance,
            "slope_scale": slope_scale,
            "intercept": intercept,
            "kappa_definition": "2 * pair_query_count / (feature_dimension + 1)",
            "pair_query_provisional_binary_observations": 2,
            "paired_to_benchmarks": (
                "s1-sample-complexity-benchmark-v7a",
                "s1-controlled-geometry-benchmark-v8a",
            ),
            "paired_scenario_seed_rule": "1_100_000 + feature_dimension * 1_000 + seed",
            "paired_response_seed_rule": "1_300_000 + feature_dimension * 1_000 + seed",
            "controlled_query_gram_target": "X.T X / n = I and 1.T X = 0",
            "raw_runs_retain_selected_pairs": True,
        },
        "query_design_diagnostics": design_diagnostics,
        "cells": cells,
        "raw_runs": raw_runs,
    }


def _metric_summary_value(
    direction_metrics: list[dict[str, float]],
    name: str,
) -> dict[str, float]:
    values = [metric[name] for metric in direction_metrics]
    return {
        "mean": mean(values),
        "median": sorted(values)[len(values) // 2]
        if len(values) % 2 == 1
        else 0.5 * (sorted(values)[len(values) // 2 - 1] + sorted(values)[len(values) // 2]),
        "p10": _linear_quantile(values, 0.10),
        "p90": _linear_quantile(values, 0.90),
        "min": min(values),
        "max": max(values),
    }


def _linear_quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def main() -> None:
    print(json.dumps(run_benchmark_v9a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
