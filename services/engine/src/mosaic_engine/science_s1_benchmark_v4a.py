from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from random import Random
from statistics import mean, median

from .science_s1_simulation import SimulationMetrics, make_gaussian_scenario
from .science_s1_v4_simulation import run_ground_truth_simulation_v4

BENCHMARK_VERSION = "s1-decision-benchmark-v4a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
POLICIES = (
    "random",
    "posterior_fisher_d_optimal",
    "mutual_information_d_optimal",
    "expected_top_k_evsi",
)
FEATURE_DIMENSIONS = (2, 4, 8)
QUERY_COUNTS = (10, 20)
SEEDS = tuple(range(8))
CANDIDATE_COUNT = 18
DECISION_COUNT = 32
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
    if not metrics:
        raise ValueError("metrics must not be empty")
    metric_names = tuple(asdict(metrics[0]))
    return {
        metric_name: _summarize([float(getattr(metric, metric_name)) for metric in metrics])
        for metric_name in metric_names
    }


def _scenario_seed(feature_dimension: int, seed: int) -> int:
    return 100_000 + feature_dimension * 1_000 + seed


def _decision_seed(feature_dimension: int, seed: int) -> int:
    return 500_000 + feature_dimension * 1_000 + seed


def _response_seed(feature_dimension: int, seed: int) -> int:
    return 900_000 + feature_dimension * 1_000 + seed


def _make_decision_bank(
    *,
    feature_dimension: int,
    decision_count: int,
    seed: int,
) -> tuple[tuple[float, ...], ...]:
    random = Random(seed)
    return tuple(
        tuple(random.gauss(0.0, 1.0) for _ in range(feature_dimension))
        for _ in range(decision_count)
    )


def run_benchmark_v4a(
    *,
    feature_dimensions: Iterable[int] = FEATURE_DIMENSIONS,
    query_counts: Iterable[int] = QUERY_COUNTS,
    policies: Iterable[str] = POLICIES,
    seeds: Iterable[int] = SEEDS,
    candidate_count: int = CANDIDATE_COUNT,
    decision_count: int = DECISION_COUNT,
    heldout_count: int = HELDOUT_COUNT,
    top_k: int = TOP_K,
    prior_variance: float = PRIOR_VARIANCE,
    slope_scale: float = SLOPE_SCALE,
    intercept: float = INTERCEPT,
) -> dict[str, object]:
    dimensions = tuple(feature_dimensions)
    budgets = tuple(query_counts)
    policy_names = tuple(policies)
    seed_values = tuple(seeds)

    if not dimensions or any(dimension <= 0 for dimension in dimensions):
        raise ValueError("feature dimensions must be positive")
    if not budgets or any(query_count <= 0 for query_count in budgets):
        raise ValueError("query counts must be positive")
    if not policy_names:
        raise ValueError("policies must not be empty")
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if candidate_count < 2 or decision_count <= 0 or heldout_count <= 0:
        raise ValueError("candidate, decision, and held-out counts must be positive")
    if top_k <= 0 or top_k > decision_count or top_k > heldout_count:
        raise ValueError("top_k must be within decision and held-out banks")
    if prior_variance <= 0.0:
        raise ValueError("prior_variance must be positive")

    cells: list[dict[str, object]] = []
    raw_runs: list[dict[str, object]] = []
    for feature_dimension in dimensions:
        prior_mean = (0.0,) * (feature_dimension + 1)
        prior_variances = (prior_variance,) * (feature_dimension + 1)
        scenarios = {
            seed: make_gaussian_scenario(
                feature_dimension=feature_dimension,
                candidate_count=candidate_count,
                heldout_count=heldout_count,
                seed=_scenario_seed(feature_dimension, seed),
                slope_scale=slope_scale,
                intercept=intercept,
            )
            for seed in seed_values
        }
        decision_banks = {
            seed: _make_decision_bank(
                feature_dimension=feature_dimension,
                decision_count=decision_count,
                seed=_decision_seed(feature_dimension, seed),
            )
            for seed in seed_values
        }

        for query_count in budgets:
            for policy in policy_names:
                results = []
                for seed in seed_values:
                    true_alpha, candidates, heldout = scenarios[seed]
                    result = run_ground_truth_simulation_v4(
                        policy=policy,
                        true_alpha=true_alpha,
                        candidates=candidates,
                        decision_features=decision_banks[seed],
                        heldout_features=heldout,
                        prior_mean=prior_mean,
                        prior_variances=prior_variances,
                        query_count=query_count,
                        top_k=top_k,
                        seed=_response_seed(feature_dimension, seed),
                    )
                    results.append(result)
                    decision_scores = result.selected_decision_scores
                    raw_runs.append(
                        {
                            "feature_dimension": feature_dimension,
                            "query_count": query_count,
                            "policy": policy,
                            "seed": seed,
                            "converged": result.posterior.converged,
                            "iterations": result.posterior.iterations,
                            "decision_score_mean": (
                                mean(decision_scores) if decision_scores else None
                            ),
                            "decision_score_min": min(decision_scores) if decision_scores else None,
                            "decision_score_max": max(decision_scores) if decision_scores else None,
                            "negative_decision_score_count": sum(
                                score < -1e-12 for score in decision_scores
                            ),
                            "metrics": asdict(result.metrics),
                        }
                    )

                cells.append(
                    {
                        "feature_dimension": feature_dimension,
                        "query_count": query_count,
                        "policy": policy,
                        "runs": len(results),
                        "convergence_rate": mean(
                            1.0 if result.posterior.converged else 0.0 for result in results
                        ),
                        "metrics": _metric_summary([result.metrics for result in results]),
                    }
                )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "scientific_scope": (
            "Exploratory synthetic decision-aligned acquisition benchmark under the correctly "
            "specified linear-logistic acceptance model. Eight seeds are hypothesis-generating "
            "only; this is not human or matchmaking validation."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "query_counts": budgets,
            "policies": policy_names,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "decision_count": decision_count,
            "heldout_count": heldout_count,
            "top_k": top_k,
            "prior_variance": prior_variance,
            "slope_scale": slope_scale,
            "intercept": intercept,
            "decision_bank_is_separate_from_heldout": True,
        },
        "cells": cells,
        "raw_runs": raw_runs,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v4a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
