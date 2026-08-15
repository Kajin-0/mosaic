from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from math import atan, pi, sqrt
from statistics import mean, pstdev

from .science_s1_benchmark_v7a import pair_query_count, realized_kappa
from .science_s1_benchmark_v8a import (
    _metric_summary,
    _ranking_summary,
    _slope_direction_metrics,
    _summarize,
)
from .science_s1_benchmark_v9a import _metric_summary_value
from .science_s1_controlled_design import (
    centered_orthogonalized_candidate_bank,
    controlled_design_diagnostics,
)
from .science_s1_directional_theory import (
    gaussian_logistic_transverse_fisher_weight,
    gaussian_population_ordering_error_from_cosine,
    normalize_effective_slope,
)
from .science_s1_passive_design import (
    balanced_round_robin_pair_schedule,
    run_scheduled_ground_truth_simulation,
)
from .science_s1_simulation import make_gaussian_scenario

BENCHMARK_VERSION = "s1-signal-scaling-benchmark-v11a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
QUERY_DESIGN_VERSION = "centered-orthogonalized-gaussian-v1"
PAIR_SCHEDULE_VERSION = "balanced-round-robin-passive-v1"
FEATURE_DIMENSIONS = (2, 4, 8, 12)
SLOPE_NORMS = (0.55, 0.75, 0.9, 1.15, 1.5)
ETA_TARGETS = (0.5, 1.0, 1.5)
SEEDS = tuple(range(32))
CANDIDATE_COUNT = 18
HELDOUT_COUNT = 96
TOP_K = 8
PRIOR_VARIANCE = 4.0
INTERCEPT = 0.0


def _scenario_seed(feature_dimension: int, seed: int) -> int:
    return 1_500_000 + feature_dimension * 10_000 + seed


def _schedule_seed(feature_dimension: int, seed: int) -> int:
    return 2_000_000 + feature_dimension * 10_000 + seed


def _response_seed(feature_dimension: int, seed: int) -> int:
    return 2_200_000 + feature_dimension * 10_000 + seed


def _large_dimension_prediction(eta: float) -> float:
    if eta <= 0.0:
        raise ValueError("eta must be positive")
    return atan(1.0 / sqrt(eta)) / pi


def _finite_dimension_prediction(*, eta: float, feature_dimension: int) -> float:
    if feature_dimension <= 1:
        raise ValueError("feature_dimension must exceed one")
    corrected_eta = eta * (feature_dimension + 1) / (feature_dimension - 1)
    return _large_dimension_prediction(corrected_eta)


def run_benchmark_v11a(
    *,
    feature_dimensions: Iterable[int] = FEATURE_DIMENSIONS,
    slope_norms: Iterable[float] = SLOPE_NORMS,
    eta_targets: Iterable[float] = ETA_TARGETS,
    seeds: Iterable[int] = SEEDS,
    candidate_count: int = CANDIDATE_COUNT,
    heldout_count: int = HELDOUT_COUNT,
    top_k: int = TOP_K,
    prior_variance: float = PRIOR_VARIANCE,
    intercept: float = INTERCEPT,
) -> dict[str, object]:
    dimensions = tuple(feature_dimensions)
    signal_levels = tuple(float(value) for value in slope_norms)
    targets = tuple(float(value) for value in eta_targets)
    seed_values = tuple(seeds)

    if not dimensions or any(dimension <= 1 for dimension in dimensions):
        raise ValueError("feature dimensions must exceed one")
    if not signal_levels or any(value <= 0.0 for value in signal_levels):
        raise ValueError("slope norms must be positive")
    if not targets or any(value <= 0.0 for value in targets):
        raise ValueError("eta targets must be positive")
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if candidate_count < 2 or candidate_count % 2 != 0:
        raise ValueError("candidate_count must be an even integer of at least two")
    if any(dimension >= candidate_count for dimension in dimensions):
        raise ValueError("controlled Gaussian design requires candidate_count > feature_dimension")
    if heldout_count <= 0 or top_k <= 0 or top_k > heldout_count:
        raise ValueError("heldout_count and top_k must define a valid held-out bank")
    if prior_variance <= 0.0:
        raise ValueError("prior_variance must be positive")

    maximum_unique_pairs = candidate_count * (candidate_count - 1) // 2
    pairs_per_round = candidate_count // 2
    cells: list[dict[str, object]] = []
    raw_runs: list[dict[str, object]] = []
    design_diagnostics: list[dict[str, object]] = []

    for feature_dimension in dimensions:
        prior_mean = (0.0,) * (feature_dimension + 1)
        prior_variances = (prior_variance,) * (feature_dimension + 1)
        scenarios = {}
        for seed in seed_values:
            raw_alpha, raw_candidates, heldout = make_gaussian_scenario(
                feature_dimension=feature_dimension,
                candidate_count=candidate_count,
                heldout_count=heldout_count,
                seed=_scenario_seed(feature_dimension, seed),
                slope_scale=1.0,
                intercept=intercept,
            )
            controlled_candidates = centered_orthogonalized_candidate_bank(raw_candidates)
            schedule = balanced_round_robin_pair_schedule(
                candidate_count,
                seed=_schedule_seed(feature_dimension, seed),
            )
            diagnostics = controlled_design_diagnostics(controlled_candidates)
            design_diagnostics.append({"seed": seed, **asdict(diagnostics)})
            scenarios[seed] = (raw_alpha, controlled_candidates, heldout, schedule)

        for slope_norm in signal_levels:
            fisher_weight = gaussian_logistic_transverse_fisher_weight(slope_norm)
            signal_information_factor = slope_norm * slope_norm * fisher_weight

            for eta_target in targets:
                requested_kappa = eta_target / signal_information_factor
                query_count = pair_query_count(
                    feature_dimension=feature_dimension,
                    kappa_target=requested_kappa,
                )
                if query_count > maximum_unique_pairs:
                    raise ValueError("eta target exceeds finite unique candidate-pair support")
                kappa = realized_kappa(
                    feature_dimension=feature_dimension,
                    query_count=query_count,
                )
                realized_eta = signal_information_factor * kappa
                large_prediction = _large_dimension_prediction(realized_eta)
                finite_prediction = _finite_dimension_prediction(
                    eta=realized_eta,
                    feature_dimension=feature_dimension,
                )

                results = []
                direction_metrics = []
                population_ordering_errors = []
                large_residuals = []
                finite_residuals = []
                heldout_discrepancies = []

                for seed in seed_values:
                    raw_alpha, controlled_candidates, heldout, schedule = scenarios[seed]
                    true_alpha = normalize_effective_slope(
                        raw_alpha,
                        target_norm=slope_norm,
                    )
                    result = run_scheduled_ground_truth_simulation(
                        true_alpha=true_alpha,
                        candidates=controlled_candidates,
                        heldout_features=heldout,
                        prior_mean=prior_mean,
                        prior_variances=prior_variances,
                        pair_schedule=schedule,
                        query_count=query_count,
                        top_k=top_k,
                        response_seed=_response_seed(feature_dimension, seed),
                    )
                    results.append(result)
                    direction = _slope_direction_metrics(
                        true_alpha,
                        result.posterior.mean,
                        result.posterior.covariance,
                    )
                    direction_metrics.append(direction)
                    population_error = gaussian_population_ordering_error_from_cosine(
                        direction["slope_cosine"]
                    )
                    heldout_discrepancy = (
                        result.ranking_metrics.ordering_error_rate - population_error
                    )
                    large_residual = population_error - large_prediction
                    finite_residual = population_error - finite_prediction
                    population_ordering_errors.append(population_error)
                    heldout_discrepancies.append(heldout_discrepancy)
                    large_residuals.append(large_residual)
                    finite_residuals.append(finite_residual)

                    raw_runs.append(
                        {
                            "feature_dimension": feature_dimension,
                            "parameter_count": feature_dimension + 1,
                            "slope_norm": slope_norm,
                            "transverse_fisher_weight": fisher_weight,
                            "signal_information_factor": signal_information_factor,
                            "eta_target": eta_target,
                            "requested_kappa": requested_kappa,
                            "realized_kappa": kappa,
                            "realized_eta": realized_eta,
                            "query_count": query_count,
                            "binary_observation_count": 2 * query_count,
                            "policy": PAIR_SCHEDULE_VERSION,
                            "seed": seed,
                            "query_design_version": QUERY_DESIGN_VERSION,
                            "large_dimension_prediction": large_prediction,
                            "finite_dimension_prediction": finite_prediction,
                            "gaussian_population_ordering_error": population_error,
                            "large_dimension_residual": large_residual,
                            "finite_dimension_residual": finite_residual,
                            "heldout_minus_population_ordering_error": heldout_discrepancy,
                            "false_direction": direction["slope_cosine"] < 0.0,
                            "converged": result.posterior.converged,
                            "iterations": result.posterior.iterations,
                            "selected_pairs": result.selected_pairs,
                            "metrics": asdict(result.metrics),
                            "ranking_metrics": asdict(result.ranking_metrics),
                            "direction_metrics": direction,
                        }
                    )

                complete_rounds, partial_pairs = divmod(query_count, pairs_per_round)
                cells.append(
                    {
                        "feature_dimension": feature_dimension,
                        "parameter_count": feature_dimension + 1,
                        "slope_norm": slope_norm,
                        "transverse_fisher_weight": fisher_weight,
                        "signal_information_factor": signal_information_factor,
                        "eta_target": eta_target,
                        "requested_kappa": requested_kappa,
                        "realized_kappa": kappa,
                        "realized_eta": realized_eta,
                        "query_count": query_count,
                        "binary_observation_count": 2 * query_count,
                        "policy": PAIR_SCHEDULE_VERSION,
                        "runs": len(results),
                        "query_design_version": QUERY_DESIGN_VERSION,
                        "complete_matching_rounds": complete_rounds,
                        "partial_matching_pairs": partial_pairs,
                        "partial_round_endpoint_count": 2 * partial_pairs,
                        "large_dimension_prediction": large_prediction,
                        "finite_dimension_prediction": finite_prediction,
                        "convergence_rate": mean(
                            1.0 if result.posterior.converged else 0.0 for result in results
                        ),
                        "false_direction_rate": mean(
                            1.0 if metric["slope_cosine"] < 0.0 else 0.0
                            for metric in direction_metrics
                        ),
                        "mean_absolute_large_dimension_residual": mean(
                            abs(value) for value in large_residuals
                        ),
                        "mean_absolute_finite_dimension_residual": mean(
                            abs(value) for value in finite_residuals
                        ),
                        "mean_absolute_heldout_population_discrepancy": mean(
                            abs(value) for value in heldout_discrepancies
                        ),
                        "metrics": _metric_summary([result.metrics for result in results]),
                        "ranking_metrics": _ranking_summary(
                            [result.ranking_metrics for result in results]
                        ),
                        "direction_metrics": {
                            name: _metric_summary_value(direction_metrics, name)
                            for name in direction_metrics[0]
                        },
                        "gaussian_population_ordering_error": _summarize(
                            population_ordering_errors
                        ),
                        "large_dimension_residual": _summarize(large_residuals),
                        "finite_dimension_residual": _summarize(finite_residuals),
                        "heldout_minus_population_ordering_error": _summarize(
                            heldout_discrepancies
                        ),
                    }
                )

    collapse_groups: list[dict[str, object]] = []
    for feature_dimension in dimensions:
        for eta_target in targets:
            matching_cells = [
                cell
                for cell in cells
                if cell["feature_dimension"] == feature_dimension
                and cell["eta_target"] == eta_target
            ]
            observed = [
                float(cell["gaussian_population_ordering_error"]["mean"]) for cell in matching_cells
            ]
            realized_etas = [float(cell["realized_eta"]) for cell in matching_cells]
            large_residual_means = [
                float(cell["large_dimension_residual"]["mean"]) for cell in matching_cells
            ]
            finite_residual_means = [
                float(cell["finite_dimension_residual"]["mean"]) for cell in matching_cells
            ]
            collapse_groups.append(
                {
                    "feature_dimension": feature_dimension,
                    "eta_target": eta_target,
                    "slope_norms": [float(cell["slope_norm"]) for cell in matching_cells],
                    "realized_eta_min": min(realized_etas),
                    "realized_eta_max": max(realized_etas),
                    "observed_mean_error_min": min(observed),
                    "observed_mean_error_max": max(observed),
                    "observed_mean_error_range": max(observed) - min(observed),
                    "observed_mean_error_pstdev": pstdev(observed),
                    "large_residual_mean_range": max(large_residual_means)
                    - min(large_residual_means),
                    "finite_residual_mean_range": max(finite_residual_means)
                    - min(finite_residual_means),
                }
            )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "pair_schedule_version": PAIR_SCHEDULE_VERSION,
        "scientific_scope": (
            "Synthetic signal-scaling falsification of the S1 Gaussian-logistic directional "
            "information coordinate. True effective slope norms are fixed by condition and "
            "query budgets are chosen to target common eta_F values across signal levels. A "
            "response-independent balanced round-robin pair schedule removes the random "
            "endpoint-imbalance confound exposed by v10a. This is not human or matchmaking "
            "validation and does not define a production stopping rule."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "slope_norms": signal_levels,
            "eta_targets": targets,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "heldout_count": heldout_count,
            "top_k": top_k,
            "prior_variance": prior_variance,
            "intercept": intercept,
            "eta_definition": "B^2 * kappa * E[sigmoid(BZ)*(1-sigmoid(BZ))], Z~N(0,1)",
            "kappa_definition": "2 * pair_query_count / (feature_dimension + 1)",
            "pair_schedule": (
                "Randomized 1-factorization of K_n. Every n/2-pair complete round uses every "
                "candidate exactly once; all unique pairs are exhausted after n-1 rounds."
            ),
            "scenario_seed_rule": "1_500_000 + feature_dimension * 10_000 + seed",
            "schedule_seed_rule": "2_000_000 + feature_dimension * 10_000 + seed",
            "response_seed_rule": "2_200_000 + feature_dimension * 10_000 + seed",
            "common_random_numbers_across_signal_levels": True,
            "controlled_query_gram_target": "X.T X / n = I and 1.T X = 0",
        },
        "query_design_diagnostics": design_diagnostics,
        "collapse_groups": collapse_groups,
        "cells": cells,
        "raw_runs": raw_runs,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v11a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
