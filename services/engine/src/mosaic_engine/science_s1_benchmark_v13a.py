from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import cos, log, pi, sin
from random import Random
from statistics import mean, median

from .science_s1 import acceptance_probability
from .science_s1_eprocess import anytime_log_threshold, binary_log_probability

BENCHMARK_VERSION = "s1-finite-null-eprocess-benchmark-v13a"
METHOD_VERSION = "prequential-finite-composite-null-v1"
FEATURE_DIMENSION = 2
NULL_ANGLES_DEGREES = (-135, -90, -60, -45, 45, 60, 90, 135, 180)
SLOPE_NORM = 0.9
ALTERNATIVE_ANGLE_DEGREES = 0.0
CANDIDATE_COUNT = 12
MAX_OBSERVATIONS = 80
ALPHA_LEVEL = 0.05
SEEDS = tuple(range(512))
LEAKY_OBSERVED_OUTCOME_PROBABILITY = 0.99


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


def _bernoulli_kl(left: float, right: float) -> float:
    return left * log(left / right) + (1.0 - left) * log((1.0 - left) / (1.0 - right))


def _select_predictable_feature(
    log_null_likelihoods: Sequence[float],
    null_parameters: Sequence[Sequence[float]],
    alternative_parameter: Sequence[float],
    candidates: Sequence[Sequence[float]],
) -> tuple[float, ...]:
    if len(log_null_likelihoods) != len(null_parameters) or not null_parameters:
        raise ValueError("null likelihood and parameter dimensions must agree and be nonempty")
    best_null_index = max(
        range(len(null_parameters)),
        key=lambda index: log_null_likelihoods[index],
    )
    best_null = null_parameters[best_null_index]

    def information_score(features: Sequence[float]) -> float:
        alternative_probability = acceptance_probability(alternative_parameter, features)
        null_probability = acceptance_probability(best_null, features)
        return _bernoulli_kl(alternative_probability, null_probability)

    selected = max(candidates, key=information_score)
    return tuple(float(value) for value in selected)


def _observed_log_probability(probability: float, accepted: bool) -> float:
    return log(probability if accepted else 1.0 - probability)


def _run_path(
    *,
    true_parameter: Sequence[float],
    null_parameters: Sequence[Sequence[float]],
    alternative_parameter: Sequence[float],
    candidates: Sequence[Sequence[float]],
    seed: int,
    max_observations: int,
    alpha_level: float,
    leaky_numerator: bool,
) -> dict[str, object]:
    random = Random(seed)
    log_null_likelihoods = [0.0] * len(null_parameters)
    log_predictive_joint = 0.0
    threshold = anytime_log_threshold(alpha_level)
    maximum_log_e = float("-inf")

    for observation_index in range(1, max_observations + 1):
        features = _select_predictable_feature(
            log_null_likelihoods,
            null_parameters,
            alternative_parameter,
            candidates,
        )
        predictive_probability = acceptance_probability(alternative_parameter, features)
        true_probability = acceptance_probability(true_parameter, features)
        accepted = random.random() < true_probability

        if leaky_numerator:
            log_predictive_joint += log(LEAKY_OBSERVED_OUTCOME_PROBABILITY)
        else:
            log_predictive_joint += _observed_log_probability(predictive_probability, accepted)

        for index, null_parameter in enumerate(null_parameters):
            log_null_likelihoods[index] += binary_log_probability(
                null_parameter,
                features,
                accepted,
            )

        log_e = log_predictive_joint - max(log_null_likelihoods)
        maximum_log_e = max(maximum_log_e, log_e)
        if log_e >= threshold:
            return {
                "rejected": True,
                "stopping_observation": observation_index,
                "maximum_log_e": maximum_log_e,
            }

    return {
        "rejected": False,
        "stopping_observation": None,
        "maximum_log_e": maximum_log_e,
    }


def _summarize(paths: Sequence[dict[str, object]]) -> dict[str, object]:
    rejected = [path for path in paths if bool(path["rejected"])]
    stopping = [int(path["stopping_observation"]) for path in rejected]
    return {
        "runs": len(paths),
        "rejections": len(rejected),
        "rejection_rate": len(rejected) / len(paths),
        "stopping_observation": {
            "mean": mean(stopping) if stopping else None,
            "median": median(stopping) if stopping else None,
        },
        "paths": paths,
    }


def run_benchmark_v13a(
    *,
    seeds: Iterable[int] = SEEDS,
    max_observations: int = MAX_OBSERVATIONS,
    alpha_level: float = ALPHA_LEVEL,
    candidate_count: int = CANDIDATE_COUNT,
) -> dict[str, object]:
    seed_values = tuple(int(seed) for seed in seeds)
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if max_observations <= 0:
        raise ValueError("max_observations must be positive")
    if alpha_level <= 0.0 or alpha_level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")

    null_parameters = tuple(_alpha_from_angle(angle) for angle in NULL_ANGLES_DEGREES)
    alternative_parameter = _alpha_from_angle(ALTERNATIVE_ANGLE_DEGREES)
    candidates = _candidate_bank(candidate_count)

    null_cells: list[dict[str, object]] = []
    all_valid_null_paths: list[dict[str, object]] = []
    all_leaky_null_paths: list[dict[str, object]] = []

    for null_index, true_parameter in enumerate(null_parameters):
        valid_paths = [
            _run_path(
                true_parameter=true_parameter,
                null_parameters=null_parameters,
                alternative_parameter=alternative_parameter,
                candidates=candidates,
                seed=10_000_000 + null_index * 100_000 + seed,
                max_observations=max_observations,
                alpha_level=alpha_level,
                leaky_numerator=False,
            )
            for seed in seed_values
        ]
        leaky_paths = [
            _run_path(
                true_parameter=true_parameter,
                null_parameters=null_parameters,
                alternative_parameter=alternative_parameter,
                candidates=candidates,
                seed=20_000_000 + null_index * 100_000 + seed,
                max_observations=max_observations,
                alpha_level=alpha_level,
                leaky_numerator=True,
            )
            for seed in seed_values
        ]
        all_valid_null_paths.extend(valid_paths)
        all_leaky_null_paths.extend(leaky_paths)
        null_cells.append(
            {
                "true_null_angle_degrees": NULL_ANGLES_DEGREES[null_index],
                "valid": _summarize(valid_paths),
                "leaky": _summarize(leaky_paths),
            }
        )

    alternative_paths = [
        _run_path(
            true_parameter=alternative_parameter,
            null_parameters=null_parameters,
            alternative_parameter=alternative_parameter,
            candidates=candidates,
            seed=30_000_000 + seed,
            max_observations=max_observations,
            alpha_level=alpha_level,
            leaky_numerator=False,
        )
        for seed in seed_values
    ]

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Finite composite-null verification harness for the S1 prequential e-process. "
            "The valid numerator is predictable and normalized before each outcome; the leaky "
            "control intentionally uses the current observed outcome and is invalid. The null "
            "parameter set is finite and contains the true parameter in every type-I run. This "
            "is a method sanity check, not a continuous angular certificate or human validation."
        ),
        "config": {
            "feature_dimension": FEATURE_DIMENSION,
            "null_angles_degrees": NULL_ANGLES_DEGREES,
            "slope_norm": SLOPE_NORM,
            "alternative_angle_degrees": ALTERNATIVE_ANGLE_DEGREES,
            "candidate_count": candidate_count,
            "max_observations": max_observations,
            "alpha_level": alpha_level,
            "seeds": seed_values,
            "query_design": (
                "predictably choose the candidate maximizing Bernoulli KL from the currently "
                "most likely finite-null parameter to the fixed alternative predictor"
            ),
            "valid_numerator": "fixed alternative Bernoulli predictive probability",
            "leaky_control": (
                "after observing Y_t assign 0.99 probability to the realized outcome; invalid"
            ),
        },
        "valid_null_aggregate": _summarize(all_valid_null_paths),
        "leaky_null_aggregate": _summarize(all_leaky_null_paths),
        "alternative_power": _summarize(alternative_paths),
        "null_cells": null_cells,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
