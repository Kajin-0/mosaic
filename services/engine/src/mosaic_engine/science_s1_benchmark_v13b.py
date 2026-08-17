from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import acos, cos, exp, log, pi, sin
from random import Random
from statistics import mean, median
from typing import cast

from .science_s1 import acceptance_probability
from .science_s1_eprocess import anytime_log_threshold, binary_log_probability

BENCHMARK_VERSION = "s1-finite-confidence-geometry-benchmark-v13b"
METHOD_VERSION = "prequential-finite-confidence-radius-v1"
FEATURE_DIMENSION = 2
PARAMETER_ANGLES_DEGREES = tuple(range(0, 360, 15))
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
TARGET_ERRORS = (0.25, 0.20, 0.15)
MAX_OBSERVATIONS = 120
ALPHA_LEVEL = 0.05
SEEDS = tuple(range(256))


def _alpha_from_angle(angle_degrees: float, *, slope_norm: float = SLOPE_NORM) -> tuple[float, ...]:
    angle = angle_degrees * pi / 180.0
    return (0.0, slope_norm * cos(angle), slope_norm * sin(angle))


def _candidate_bank(candidate_count: int = CANDIDATE_COUNT) -> tuple[tuple[float, float], ...]:
    if candidate_count < 4:
        raise ValueError("candidate_count must be at least four")
    return tuple(
        (
            cos(2.0 * pi * index / candidate_count),
            sin(2.0 * pi * index / candidate_count),
        )
        for index in range(candidate_count)
    )


def _normalized_likelihood_weights(log_likelihoods: Sequence[float]) -> tuple[float, ...]:
    if not log_likelihoods:
        raise ValueError("log_likelihoods must not be empty")
    maximum = max(float(value) for value in log_likelihoods)
    raw = tuple(exp(float(value) - maximum) for value in log_likelihoods)
    total = sum(raw)
    return tuple(value / total for value in raw)


def _mixture_predictive_probability(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
) -> float:
    if len(log_likelihoods) != len(parameters):
        raise ValueError("likelihood and parameter dimensions must agree")
    weights = _normalized_likelihood_weights(log_likelihoods)
    return sum(
        weight * acceptance_probability(parameter, features)
        for weight, parameter in zip(weights, parameters, strict=True)
    )


def _confidence_indices(
    log_predictive_joint: float,
    log_likelihoods: Sequence[float],
    *,
    alpha_level: float,
) -> tuple[int, ...]:
    threshold = anytime_log_threshold(alpha_level)
    return tuple(
        index
        for index, log_likelihood in enumerate(log_likelihoods)
        if log_predictive_joint - float(log_likelihood) < threshold
    )


def _select_disagreement_feature(
    confidence_indices: Sequence[int],
    parameters: Sequence[Sequence[float]],
    candidates: Sequence[Sequence[float]],
) -> tuple[float, ...]:
    if not confidence_indices:
        raise ValueError("confidence_indices must not be empty")

    def disagreement(features: Sequence[float]) -> float:
        probabilities = [
            acceptance_probability(parameters[index], features) for index in confidence_indices
        ]
        return max(probabilities) - min(probabilities)

    selected = max(candidates, key=disagreement)
    return tuple(float(value) for value in selected)


def _directional_error(left: Sequence[float], right: Sequence[float]) -> float:
    left_slope = tuple(float(value) for value in left[1:])
    right_slope = tuple(float(value) for value in right[1:])
    left_norm = sum(value * value for value in left_slope) ** 0.5
    right_norm = sum(value * value for value in right_slope) ** 0.5
    if left_norm <= 1e-15 or right_norm <= 1e-15:
        return 0.5
    cosine = sum(a * b for a, b in zip(left_slope, right_slope, strict=True)) / (
        left_norm * right_norm
    )
    return acos(min(1.0, max(-1.0, cosine))) / pi


def _confidence_radius(
    center_index: int,
    confidence_indices: Sequence[int],
    parameters: Sequence[Sequence[float]],
) -> float:
    center = parameters[center_index]
    return max(_directional_error(center, parameters[index]) for index in confidence_indices)


def _observed_log_probability(probability: float, accepted: bool) -> float:
    return log(probability if accepted else 1.0 - probability)


def _run_path(
    *,
    true_index: int,
    parameters: Sequence[Sequence[float]],
    candidates: Sequence[Sequence[float]],
    seed: int,
    target_errors: Sequence[float],
    max_observations: int,
    alpha_level: float,
) -> dict[str, object]:
    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    log_predictive_joint = 0.0
    confidence_indices = tuple(range(len(parameters)))
    stops: dict[str, dict[str, object] | None] = {str(target): None for target in target_errors}
    true_excluded_ever = False

    for observation_index in range(1, max_observations + 1):
        features = _select_disagreement_feature(confidence_indices, parameters, candidates)
        predictive_probability = _mixture_predictive_probability(
            log_likelihoods,
            parameters,
            features,
        )
        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability
        log_predictive_joint += _observed_log_probability(predictive_probability, accepted)

        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        confidence_indices = _confidence_indices(
            log_predictive_joint,
            log_likelihoods,
            alpha_level=alpha_level,
        )
        if not confidence_indices:
            raise RuntimeError("finite e-process confidence set became empty")

        true_excluded = true_index not in confidence_indices
        true_excluded_ever = true_excluded_ever or true_excluded
        center_index = max(confidence_indices, key=lambda index: log_likelihoods[index])
        radius = _confidence_radius(center_index, confidence_indices, parameters)
        true_error = _directional_error(parameters[center_index], parameters[true_index])

        for target_error in target_errors:
            key = str(target_error)
            if stops[key] is None and radius <= target_error:
                stops[key] = {
                    "observation_count": observation_index,
                    "center_index": center_index,
                    "center_angle_degrees": PARAMETER_ANGLES_DEGREES[center_index],
                    "confidence_size": len(confidence_indices),
                    "certified_radius": radius,
                    "true_directional_error": true_error,
                    "true_in_confidence_set": not true_excluded,
                    "false_stop": true_error > target_error,
                }

        if all(stop is not None for stop in stops.values()):
            break

    return {
        "true_index": true_index,
        "true_angle_degrees": PARAMETER_ANGLES_DEGREES[true_index],
        "true_excluded_ever": true_excluded_ever,
        "final_confidence_size": len(confidence_indices),
        "stops": stops,
    }


def _summarize_target(paths: Sequence[dict[str, object]], target_error: float) -> dict[str, object]:
    key = str(target_error)
    stops = [
        cast(dict[str, object], cast(dict[str, object], path["stops"])[key])
        for path in paths
        if cast(dict[str, object], path["stops"])[key] is not None
    ]
    false_stops = [stop for stop in stops if bool(stop["false_stop"])]
    observation_counts = [cast(int, stop["observation_count"]) for stop in stops]
    excluded_paths = [path for path in paths if bool(path["true_excluded_ever"])]
    return {
        "target_error": target_error,
        "runs": len(paths),
        "stops": len(stops),
        "stop_rate": len(stops) / len(paths),
        "false_stops": len(false_stops),
        "false_stop_rate": len(false_stops) / len(paths),
        "false_stop_given_stop": len(false_stops) / len(stops) if stops else 0.0,
        "true_excluded_ever_rate": len(excluded_paths) / len(paths),
        "stopping_observation": {
            "mean": mean(observation_counts) if observation_counts else None,
            "median": median(observation_counts) if observation_counts else None,
        },
    }


def run_benchmark_v13b(
    *,
    seeds: Iterable[int] = SEEDS,
    target_errors: Iterable[float] = TARGET_ERRORS,
    max_observations: int = MAX_OBSERVATIONS,
    alpha_level: float = ALPHA_LEVEL,
    candidate_count: int = CANDIDATE_COUNT,
) -> dict[str, object]:
    seed_values = tuple(int(seed) for seed in seeds)
    targets = tuple(float(target) for target in target_errors)
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if not targets or any(target <= 0.0 or target >= 0.5 for target in targets):
        raise ValueError("target_errors must lie strictly between zero and 0.5")
    if max_observations <= 0:
        raise ValueError("max_observations must be positive")
    if alpha_level <= 0.0 or alpha_level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")

    parameters = tuple(_alpha_from_angle(angle) for angle in PARAMETER_ANGLES_DEGREES)
    candidates = _candidate_bank(candidate_count)
    paths: list[dict[str, object]] = []
    angle_cells: list[dict[str, object]] = []

    for true_index, true_angle in enumerate(PARAMETER_ANGLES_DEGREES):
        cell_paths = [
            _run_path(
                true_index=true_index,
                parameters=parameters,
                candidates=candidates,
                seed=40_000_000 + true_index * 100_000 + seed,
                target_errors=targets,
                max_observations=max_observations,
                alpha_level=alpha_level,
            )
            for seed in seed_values
        ]
        paths.extend(cell_paths)
        angle_cells.append(
            {
                "true_angle_degrees": true_angle,
                "runs": len(cell_paths),
                "target_summaries": [
                    _summarize_target(cell_paths, target_error) for target_error in targets
                ],
            }
        )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Finite-grid verification of the intended S1 operational sequence: construct an "
            "anytime-valid e-process confidence set, choose queries predictably from its prior "
            "state, and stop only when the exact finite-grid directional radius around the "
            "retained maximum-likelihood direction is below target. The true parameter is on "
            "the finite grid. This is not a continuous certificate or human validation."
        ),
        "config": {
            "feature_dimension": FEATURE_DIMENSION,
            "parameter_angles_degrees": PARAMETER_ANGLES_DEGREES,
            "slope_norm": SLOPE_NORM,
            "candidate_count": candidate_count,
            "target_errors": targets,
            "max_observations": max_observations,
            "alpha_level": alpha_level,
            "seeds": seed_values,
            "predictive_numerator": "uniform-prior finite likelihood-mixture predictive",
            "query_design": "maximize probability range over the prior confidence set",
            "stopping_rule": (
                "stop when every retained finite-grid slope direction lies within target of "
                "the retained maximum-likelihood direction"
            ),
        },
        "aggregate_target_summaries": [
            _summarize_target(paths, target_error) for target_error in targets
        ],
        "angle_cells": angle_cells,
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13b(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
