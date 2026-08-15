from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from math import sqrt
from statistics import mean

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
    asymptotic_gaussian_logistic_ordering_error,
    asymptotic_isotropic_ordering_error,
    boundary_directional_information_coordinate,
    gaussian_logistic_directional_information_coordinate,
    gaussian_population_ordering_error_from_cosine,
    normalize_effective_slope,
)
from .science_s1_simulation import make_gaussian_scenario
from .science_s1_v6_simulation import run_ground_truth_simulation_v6

BENCHMARK_VERSION = "s1-fixed-signal-sample-complexity-benchmark-v10a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
QUERY_DESIGN_VERSION = "centered-orthogonalized-gaussian-v1"
POLICY = "random"
FEATURE_DIMENSIONS = (2, 4, 8, 12)
KAPPA_TARGETS = (2.0, 4.0, 6.0, 8.0, 12.0)
SEEDS = tuple(range(32))
CANDIDATE_COUNT = 18
HELDOUT_COUNT = 96
TOP_K = 8
PRIOR_VARIANCE = 4.0
FIXED_SLOPE_NORM = 0.9
INTERCEPT = 0.0


def _scenario_seed(feature_dimension: int, seed: int) -> int:
    return 1_500_000 + feature_dimension * 10_000 + seed


def _response_seed(feature_dimension: int, seed: int) -> int:
    return 1_700_000 + feature_dimension * 10_000 + seed


def _slope_norm(alpha: tuple[float, ...]) -> float:
    return sqrt(sum(float(value) * float(value) for value in alpha[1:]))


def run_benchmark_v10a(
    *,
    feature_dimensions: Iterable[int] = FEATURE_DIMENSIONS,
    kappa_targets: Iterable[float] = KAPPA_TARGETS,
    seeds: Iterable[int] = SEEDS,
    candidate_count: int = CANDIDATE_COUNT,
    heldout_count: int = HELDOUT_COUNT,
    top_k: int = TOP_K,
    prior_variance: float = PRIOR_VARIANCE,
    fixed_slope_norm: float = FIXED_SLOPE_NORM,
    intercept: float = INTERCEPT,
) -> dict[str, object]:
    dimensions = tuple(feature_dimensions)
    targets = tuple(float(value) for value in kappa_targets)
    seed_values = tuple(seeds)

    if not dimensions or any(dimension <= 0 for dimension in dimensions):
        raise ValueError("feature dimensions must be positive")
    if not targets or any(target <= 0.0 for target in targets):
        raise ValueError("kappa targets must be positive")
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if candidate_count < 2 or heldout_count <= 0:
        raise ValueError("synthetic bank counts must be positive")
    if any(dimension >= candidate_count for dimension in dimensions):
        raise ValueError("controlled Gaussian design requires candidate_count > feature_dimension")
    if top_k <= 0 or top_k > heldout_count:
        raise ValueError("top_k must be within the held-out bank")
    if prior_variance <= 0.0:
        raise ValueError("prior_variance must be positive")
    if fixed_slope_norm <= 0.0:
        raise ValueError("fixed_slope_norm must be positive")

    maximum_unique_pairs = candidate_count * (candidate_count - 1) // 2
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
            true_alpha = normalize_effective_slope(
                raw_alpha,
                target_norm=fixed_slope_norm,
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
            eta_boundary = boundary_directional_information_coordinate(
                kappa=kappa,
                slope_norm=fixed_slope_norm,
            )
            eta_fisher = gaussian_logistic_directional_information_coordinate(
                kappa=kappa,
                slope_norm=fixed_slope_norm,
            )
            boundary_prediction = asymptotic_isotropic_ordering_error(
                kappa=kappa,
                slope_norm=fixed_slope_norm,
            )
            fisher_prediction = asymptotic_gaussian_logistic_ordering_error(
                kappa=kappa,
                slope_norm=fixed_slope_norm,
            )

            results = []
            direction_metrics = []
            population_ordering_errors = []
            heldout_population_discrepancies = []
            boundary_law_residuals = []
            fisher_law_residuals = []

            for seed in seed_values:
                true_alpha, controlled_candidates, heldout = scenarios[seed]
                result = run_ground_truth_simulation_v6(
                    policy=POLICY,
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

                population_error = gaussian_population_ordering_error_from_cosine(
                    direction["slope_cosine"]
                )
                heldout_error = result.ranking_metrics.ordering_error_rate
                heldout_population_discrepancy = heldout_error - population_error
                boundary_residual = population_error - boundary_prediction
                fisher_residual = population_error - fisher_prediction
                population_ordering_errors.append(population_error)
                heldout_population_discrepancies.append(heldout_population_discrepancy)
                boundary_law_residuals.append(boundary_residual)
                fisher_law_residuals.append(fisher_residual)

                raw_runs.append(
                    {
                        "feature_dimension": feature_dimension,
                        "parameter_count": feature_dimension + 1,
                        "kappa_target": target,
                        "realized_kappa": kappa,
                        "query_count": query_count,
                        "binary_observation_count": 2 * query_count,
                        "policy": POLICY,
                        "seed": seed,
                        "query_design_version": QUERY_DESIGN_VERSION,
                        "true_slope_norm": _slope_norm(true_alpha),
                        "boundary_directional_information_coordinate": eta_boundary,
                        "gaussian_logistic_directional_information_coordinate": eta_fisher,
                        "boundary_ordering_prediction": boundary_prediction,
                        "gaussian_logistic_ordering_prediction": fisher_prediction,
                        "gaussian_population_ordering_error": population_error,
                        "heldout_minus_population_ordering_error": heldout_population_discrepancy,
                        "boundary_law_residual": boundary_residual,
                        "gaussian_logistic_law_residual": fisher_residual,
                        "false_direction": direction["slope_cosine"] < 0.0,
                        "converged": result.posterior.converged,
                        "iterations": result.posterior.iterations,
                        "selected_pairs": result.selected_pairs,
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
                    "policy": POLICY,
                    "runs": len(results),
                    "query_design_version": QUERY_DESIGN_VERSION,
                    "true_slope_norm": fixed_slope_norm,
                    "boundary_directional_information_coordinate": eta_boundary,
                    "gaussian_logistic_directional_information_coordinate": eta_fisher,
                    "boundary_ordering_prediction": boundary_prediction,
                    "gaussian_logistic_ordering_prediction": fisher_prediction,
                    "convergence_rate": mean(
                        1.0 if result.posterior.converged else 0.0 for result in results
                    ),
                    "false_direction_rate": mean(
                        1.0 if metric["slope_cosine"] < 0.0 else 0.0
                        for metric in direction_metrics
                    ),
                    "mean_absolute_boundary_law_residual": mean(
                        abs(value) for value in boundary_law_residuals
                    ),
                    "mean_absolute_gaussian_logistic_law_residual": mean(
                        abs(value) for value in fisher_law_residuals
                    ),
                    "mean_absolute_heldout_population_discrepancy": mean(
                        abs(value) for value in heldout_population_discrepancies
                    ),
                    "metrics": _metric_summary([result.metrics for result in results]),
                    "ranking_metrics": _ranking_summary(
                        [result.ranking_metrics for result in results]
                    ),
                    "direction_metrics": {
                        name: _metric_summary_value(direction_metrics, name)
                        for name in direction_metrics[0]
                    },
                    "gaussian_population_ordering_error": _summarize(population_ordering_errors),
                    "heldout_minus_population_ordering_error": _summarize(
                        heldout_population_discrepancies
                    ),
                    "boundary_law_residual": _summarize(boundary_law_residuals),
                    "gaussian_logistic_law_residual": _summarize(fisher_law_residuals),
                }
            )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "scientific_scope": (
            "Synthetic fixed-signal passive-law test for S1 directional sample complexity. "
            "Every true effective slope is normalized to one common norm in the standardized "
            "feature basis; query banks are centered Gaussian-derived tight frames; only "
            "passive random pair sampling is used so adaptive lock-in is excluded from this "
            "baseline. The benchmark compares the p=0.5 boundary approximation with the "
            "Gaussian-logistic transverse-Fisher correction. This is not human or matchmaking "
            "validation and does not define a production stopping rule."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "kappa_targets": targets,
            "policy": POLICY,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "heldout_count": heldout_count,
            "top_k": top_k,
            "prior_variance": prior_variance,
            "fixed_slope_norm": fixed_slope_norm,
            "intercept": intercept,
            "kappa_definition": "2 * pair_query_count / (feature_dimension + 1)",
            "boundary_eta_definition": "fixed_slope_norm^2 * realized_kappa / 4",
            "gaussian_logistic_eta_definition": (
                "fixed_slope_norm^2 * realized_kappa * "
                "E[sigmoid(BZ)*(1-sigmoid(BZ))], Z~N(0,1)"
            ),
            "paired_binary_observations_per_pair": 2,
            "scenario_seed_rule": "1_500_000 + feature_dimension * 10_000 + seed",
            "response_seed_rule": "1_700_000 + feature_dimension * 10_000 + seed",
            "controlled_query_gram_target": "X.T X / n = I and 1.T X = 0",
            "raw_runs_retain_selected_pairs": True,
        },
        "query_design_diagnostics": design_diagnostics,
        "cells": cells,
        "raw_runs": raw_runs,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v10a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
