from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from math import acos, pi, sqrt
from random import Random
from statistics import mean, median

from .science_s1 import acceptance_probability
from .science_s1_controlled_design import centered_orthogonalized_candidate_bank
from .science_s1_directional_theory import normalize_effective_slope
from .science_s1_passive_design import balanced_round_robin_pair_schedule
from .science_s1_simulation import BinaryObservation, fit_logistic_laplace, make_gaussian_scenario
from .science_s1_stopping import posterior_directional_risk

BENCHMARK_VERSION = "s1-stopping-calibration-benchmark-v12a"
MODEL_VERSION = "visual-acceptance-linear-logit-v1"
QUERY_DESIGN_VERSION = "centered-orthogonalized-gaussian-v1"
PAIR_SCHEDULE_VERSION = "balanced-round-robin-passive-v1"
STOPPING_VERSION = "laplace-angular-q95-v1"
FEATURE_DIMENSIONS = (4, 8, 12)
SLOPE_NORMS = (0.55, 0.9, 1.5)
TARGET_ERRORS = (0.25, 0.20, 0.15)
SEEDS = tuple(range(64))
CANDIDATE_COUNT = 18
HELDOUT_COUNT = 8
PRIOR_VARIANCE = 4.0
INTERCEPT = 0.0
POSTERIOR_QUANTILE = 0.95
POSTERIOR_SAMPLES = 256


def _scenario_seed(feature_dimension: int, seed: int) -> int:
    return 3_000_000 + feature_dimension * 10_000 + seed


def _schedule_seed(feature_dimension: int, seed: int) -> int:
    return 3_500_000 + feature_dimension * 10_000 + seed


def _response_seed(feature_dimension: int, seed: int) -> int:
    return 4_000_000 + feature_dimension * 10_000 + seed


def _risk_seed(feature_dimension: int, seed: int, round_index: int) -> int:
    return 4_500_000 + feature_dimension * 100_000 + seed * 100 + round_index


def _slope_norm(alpha: Sequence[float]) -> float:
    return sqrt(sum(float(value) ** 2 for value in alpha[1:]))


def _population_ordering_error(true_alpha: Sequence[float], fitted_alpha: Sequence[float]) -> float:
    true_slope = tuple(float(value) for value in true_alpha[1:])
    fitted_slope = tuple(float(value) for value in fitted_alpha[1:])
    true_norm = sqrt(sum(value * value for value in true_slope))
    fitted_norm = sqrt(sum(value * value for value in fitted_slope))
    if true_norm <= 1e-15 or fitted_norm <= 1e-15:
        return 0.5
    cosine = sum(a * b for a, b in zip(true_slope, fitted_slope, strict=True)) / (
        true_norm * fitted_norm
    )
    cosine = min(1.0, max(-1.0, cosine))
    return acos(cosine) / pi


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if probability < 0.0 or probability > 1.0:
        raise ValueError("probability must lie in [0, 1]")
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _run_path(
    *,
    feature_dimension: int,
    slope_norm: float,
    seed: int,
    candidate_count: int,
    prior_variance: float,
    intercept: float,
    posterior_quantile: float,
    posterior_samples: int,
) -> list[dict[str, object]]:
    raw_alpha, raw_candidates, _ = make_gaussian_scenario(
        feature_dimension=feature_dimension,
        candidate_count=candidate_count,
        heldout_count=HELDOUT_COUNT,
        seed=_scenario_seed(feature_dimension, seed),
        slope_scale=1.0,
        intercept=intercept,
    )
    true_alpha = normalize_effective_slope(raw_alpha, target_norm=slope_norm)
    candidates = centered_orthogonalized_candidate_bank(raw_candidates)
    schedule = balanced_round_robin_pair_schedule(
        candidate_count,
        seed=_schedule_seed(feature_dimension, seed),
    )
    pairs_per_round = candidate_count // 2
    prior_mean = (0.0,) * (feature_dimension + 1)
    prior_variances = (prior_variance,) * (feature_dimension + 1)
    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    response_random = Random(_response_seed(feature_dimension, seed) ^ 0xC0FFEE)
    checkpoints: list[dict[str, object]] = []

    for round_index in range(candidate_count - 1):
        round_pairs = schedule[
            round_index * pairs_per_round : (round_index + 1) * pairs_per_round
        ]
        for first, second in round_pairs:
            for candidate_index in (first, second):
                features = tuple(float(value) for value in candidates[candidate_index])
                probability = acceptance_probability(true_alpha, features)
                observations.append(
                    BinaryObservation(
                        features=features,
                        accepted=response_random.random() < probability,
                    )
                )

        posterior = fit_logistic_laplace(
            observations,
            prior_mean,
            prior_variances,
            initial_mean=posterior.mean,
        )
        risk = posterior_directional_risk(
            posterior,
            quantile=posterior_quantile,
            sample_count=posterior_samples,
            seed=_risk_seed(feature_dimension, seed, round_index),
        )
        query_count = (round_index + 1) * pairs_per_round
        checkpoints.append(
            {
                "round_index": round_index + 1,
                "query_count": query_count,
                "binary_observation_count": 2 * query_count,
                "posterior_directional_risk": asdict(risk),
                "posterior_slope_norm": _slope_norm(posterior.mean),
                "true_population_ordering_error": _population_ordering_error(
                    true_alpha,
                    posterior.mean,
                ),
                "converged": posterior.converged,
                "iterations": posterior.iterations,
            }
        )

    return checkpoints


def _summarize_target(
    paths: Sequence[dict[str, object]],
    *,
    target_error: float,
) -> dict[str, object]:
    outcomes: list[dict[str, object]] = []
    for path in paths:
        checkpoints = path["checkpoints"]
        assert isinstance(checkpoints, list)
        stop_checkpoint = None
        for checkpoint in checkpoints:
            assert isinstance(checkpoint, dict)
            risk = checkpoint["posterior_directional_risk"]
            assert isinstance(risk, dict)
            if float(risk["upper_error"]) <= target_error:
                stop_checkpoint = checkpoint
                break

        final_checkpoint = checkpoints[-1]
        assert isinstance(final_checkpoint, dict)
        if stop_checkpoint is None:
            final_error = float(final_checkpoint["true_population_ordering_error"])
            outcomes.append(
                {
                    "seed": path["seed"],
                    "stopped": False,
                    "false_stop": False,
                    "missed_stop_at_cap": final_error <= target_error,
                    "query_count": None,
                    "true_error_at_decision": final_error,
                    "posterior_upper_at_decision": float(
                        final_checkpoint["posterior_directional_risk"]["upper_error"]
                    ),
                }
            )
        else:
            true_error = float(stop_checkpoint["true_population_ordering_error"])
            outcomes.append(
                {
                    "seed": path["seed"],
                    "stopped": True,
                    "false_stop": true_error > target_error,
                    "missed_stop_at_cap": False,
                    "query_count": int(stop_checkpoint["query_count"]),
                    "true_error_at_decision": true_error,
                    "posterior_upper_at_decision": float(
                        stop_checkpoint["posterior_directional_risk"]["upper_error"]
                    ),
                }
            )

    stopped = [outcome for outcome in outcomes if outcome["stopped"]]
    false_stops = [outcome for outcome in outcomes if outcome["false_stop"]]
    query_counts = [int(outcome["query_count"]) for outcome in stopped]
    stopped_errors = [float(outcome["true_error_at_decision"]) for outcome in stopped]

    return {
        "target_error": target_error,
        "runs": len(outcomes),
        "stop_rate": len(stopped) / len(outcomes),
        "false_stop_rate": len(false_stops) / len(outcomes),
        "false_stop_given_stop": (len(false_stops) / len(stopped)) if stopped else 0.0,
        "missed_stop_at_cap_rate": mean(
            1.0 if outcome["missed_stop_at_cap"] else 0.0 for outcome in outcomes
        ),
        "stopping_query_count": {
            "mean": mean(query_counts) if query_counts else None,
            "median": median(query_counts) if query_counts else None,
            "p90": _quantile(query_counts, 0.9) if query_counts else None,
        },
        "true_error_given_stop": {
            "mean": mean(stopped_errors) if stopped_errors else None,
            "p90": _quantile(stopped_errors, 0.9) if stopped_errors else None,
            "max": max(stopped_errors) if stopped_errors else None,
        },
        "outcomes": outcomes,
    }


def run_benchmark_v12a(
    *,
    feature_dimensions: Iterable[int] = FEATURE_DIMENSIONS,
    slope_norms: Iterable[float] = SLOPE_NORMS,
    target_errors: Iterable[float] = TARGET_ERRORS,
    seeds: Iterable[int] = SEEDS,
    candidate_count: int = CANDIDATE_COUNT,
    prior_variance: float = PRIOR_VARIANCE,
    intercept: float = INTERCEPT,
    posterior_quantile: float = POSTERIOR_QUANTILE,
    posterior_samples: int = POSTERIOR_SAMPLES,
) -> dict[str, object]:
    dimensions = tuple(feature_dimensions)
    signals = tuple(float(value) for value in slope_norms)
    targets = tuple(float(value) for value in target_errors)
    seed_values = tuple(seeds)

    if not dimensions or any(value <= 1 or value >= candidate_count for value in dimensions):
        raise ValueError("feature dimensions must lie between one and candidate_count")
    if not signals or any(value <= 0.0 for value in signals):
        raise ValueError("slope norms must be positive")
    if not targets or any(value <= 0.0 or value >= 0.5 for value in targets):
        raise ValueError("target errors must lie strictly between zero and 0.5")
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if candidate_count < 2 or candidate_count % 2 != 0:
        raise ValueError("candidate_count must be an even integer of at least two")
    if prior_variance <= 0.0:
        raise ValueError("prior_variance must be positive")
    if posterior_quantile <= 0.0 or posterior_quantile > 1.0:
        raise ValueError("posterior_quantile must lie in (0, 1]")
    if posterior_samples <= 0:
        raise ValueError("posterior_samples must be positive")

    paths: list[dict[str, object]] = []
    cells: list[dict[str, object]] = []

    for feature_dimension in dimensions:
        for slope_norm in signals:
            condition_paths: list[dict[str, object]] = []
            for seed in seed_values:
                checkpoints = _run_path(
                    feature_dimension=feature_dimension,
                    slope_norm=slope_norm,
                    seed=seed,
                    candidate_count=candidate_count,
                    prior_variance=prior_variance,
                    intercept=intercept,
                    posterior_quantile=posterior_quantile,
                    posterior_samples=posterior_samples,
                )
                path = {
                    "feature_dimension": feature_dimension,
                    "slope_norm": slope_norm,
                    "seed": seed,
                    "checkpoints": checkpoints,
                }
                paths.append(path)
                condition_paths.append(path)

            target_summaries = [
                _summarize_target(condition_paths, target_error=target) for target in targets
            ]
            first_round_norm_ratios = [
                float(path["checkpoints"][0]["posterior_slope_norm"]) / slope_norm
                for path in condition_paths
            ]
            final_norm_ratios = [
                float(path["checkpoints"][-1]["posterior_slope_norm"]) / slope_norm
                for path in condition_paths
            ]
            cells.append(
                {
                    "feature_dimension": feature_dimension,
                    "slope_norm": slope_norm,
                    "runs": len(condition_paths),
                    "target_summaries": target_summaries,
                    "posterior_norm_ratio": {
                        "first_round_mean": mean(first_round_norm_ratios),
                        "first_round_p90": _quantile(first_round_norm_ratios, 0.9),
                        "final_mean": mean(final_norm_ratios),
                        "final_p90": _quantile(final_norm_ratios, 0.9),
                    },
                }
            )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "pair_schedule_version": PAIR_SCHEDULE_VERSION,
        "stopping_version": STOPPING_VERSION,
        "scientific_scope": (
            "Synthetic operating-characteristic test of a posterior-observable S1 directional "
            "stopping statistic. The stop rule uses only the Laplace posterior and known design; "
            "synthetic truth is consulted only after the decision to measure false-stop and "
            "missed-stop behavior. This is not human or matchmaking validation."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "slope_norms": signals,
            "target_errors": targets,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "complete_rounds": candidate_count - 1,
            "pairs_per_round": candidate_count // 2,
            "maximum_pair_queries": candidate_count * (candidate_count - 1) // 2,
            "prior_variance": prior_variance,
            "intercept": intercept,
            "posterior_quantile": posterior_quantile,
            "posterior_samples": posterior_samples,
            "stopping_rule": "stop at first complete round with posterior angular-error q95 <= target",
            "common_random_numbers_across_signal_levels": True,
        },
        "cells": cells,
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v12a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
