from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from math import acos, sqrt
from statistics import mean, median

from .science_s1_benchmark_v7a import pair_query_count, realized_kappa
from .science_s1_controlled_design import (
    centered_dct_candidate_bank,
    controlled_design_diagnostics,
)
from .science_s1_ranking_evaluation import PairwiseRankingMetrics
from .science_s1_simulation import SimulationMetrics, make_gaussian_scenario
from .science_s1_v6_simulation import run_ground_truth_simulation_v6

BENCHMARK_VERSION = "s1-controlled-geometry-benchmark-v8a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
QUERY_DESIGN_VERSION = "centered-dct-orthogonal-v1"
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


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be within [0, 1]")

    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * (len(ordered) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = position - lower_index
    return ordered[lower_index] * (1.0 - fraction) + ordered[upper_index] * fraction


def _summarize(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise ValueError("values must not be empty")
    return {
        "mean": mean(values),
        "median": median(values),
        "p10": _quantile(values, 0.10),
        "p90": _quantile(values, 0.90),
        "min": min(values),
        "max": max(values),
    }


def _metric_summary(metrics: Sequence[SimulationMetrics]) -> dict[str, dict[str, float]]:
    metric_names = tuple(asdict(metrics[0]))
    return {
        metric_name: _summarize([float(getattr(metric, metric_name)) for metric in metrics])
        for metric_name in metric_names
    }


def _ranking_summary(metrics: Sequence[PairwiseRankingMetrics]) -> dict[str, dict[str, float]]:
    return {
        "ordering_error_rate": _summarize([metric.ordering_error_rate for metric in metrics]),
        "probability_regret": _summarize([metric.probability_regret for metric in metrics]),
    }


def _scenario_seed(feature_dimension: int, seed: int) -> int:
    # Intentionally identical to v7a so true alpha and held-out population are paired.
    return 1_100_000 + feature_dimension * 1_000 + seed


def _response_seed(feature_dimension: int, seed: int) -> int:
    # Intentionally identical to v7a so stochastic response streams are paired.
    return 1_300_000 + feature_dimension * 1_000 + seed


def _slope_direction_metrics(
    true_alpha: Sequence[float],
    posterior_mean: Sequence[float],
    posterior_covariance: Sequence[Sequence[float]],
) -> dict[str, float]:
    true_slope = tuple(float(value) for value in true_alpha[1:])
    estimated_slope = tuple(float(value) for value in posterior_mean[1:])
    true_norm = sqrt(sum(value * value for value in true_slope))
    estimated_norm = sqrt(sum(value * value for value in estimated_slope))
    if true_norm <= 0.0:
        raise ValueError("true slope must be nonzero")

    if estimated_norm <= 1e-15:
        cosine = 0.0
    else:
        cosine = sum(
            true_value * estimated_value
            for true_value, estimated_value in zip(true_slope, estimated_slope, strict=True)
        ) / (true_norm * estimated_norm)
        cosine = min(max(cosine, -1.0), 1.0)

    slope_variance_trace = sum(
        float(posterior_covariance[index + 1][index + 1]) for index in range(len(true_slope))
    )
    uncertainty_scale = sqrt(max(slope_variance_trace, 0.0))
    signal_to_uncertainty = (
        estimated_norm / uncertainty_scale if uncertainty_scale > 0.0 else float("inf")
    )
    return {
        "slope_cosine": cosine,
        "slope_angle_radians": acos(cosine),
        "slope_signal_to_uncertainty": signal_to_uncertainty,
    }


def run_benchmark_v8a(
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
        raise ValueError("controlled DCT design requires candidate_count > feature_dimension")
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
        controlled_candidates = centered_dct_candidate_bank(
            candidate_count=candidate_count,
            feature_dimension=feature_dimension,
        )
        diagnostics = controlled_design_diagnostics(controlled_candidates)
        design_diagnostics.append(asdict(diagnostics))

        # Generate the same full v7a scenario stream, including and then discarding
        # the original iid-Gaussian query bank. This preserves true alpha and
        # held-out candidates exactly while changing only the admissible query bank.
        scenarios = {}
        for seed in seed_values:
            true_alpha, _v7_candidates, heldout = make_gaussian_scenario(
                feature_dimension=feature_dimension,
                candidate_count=candidate_count,
                heldout_count=heldout_count,
                seed=_scenario_seed(feature_dimension, seed),
                slope_scale=slope_scale,
                intercept=intercept,
            )
            scenarios[seed] = (true_alpha, heldout)

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
                    true_alpha, heldout = scenarios[seed]
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
                            name: _summarize([metric[name] for metric in direction_metrics])
                            for name in direction_metrics[0]
                        },
                    }
                )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "scientific_scope": (
            "Exploratory synthetic controlled-geometry test paired to S1 v7a. True preference "
            "states, held-out Gaussian populations, response seeds, policies, dimensions, kappa "
            "targets, and candidate count are retained; only the query bank changes from iid "
            "Gaussian samples to an exactly centered orthogonal DCT frame. Four seeds are "
            "screening evidence only; not human or matchmaking validation."
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
            "paired_to_benchmark": "s1-sample-complexity-benchmark-v7a",
            "paired_scenario_seed_rule": "1_100_000 + feature_dimension * 1_000 + seed",
            "paired_response_seed_rule": "1_300_000 + feature_dimension * 1_000 + seed",
            "controlled_query_gram_target": "X.T X / n = I and 1.T X = 0",
            "raw_runs_retain_selected_pairs": True,
        },
        "query_design_diagnostics": design_diagnostics,
        "cells": cells,
        "raw_runs": raw_runs,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v8a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
