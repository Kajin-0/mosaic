from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import cos, floor, pi, sin
from random import Random
from statistics import mean, median
from typing import cast

from .science_s1 import acceptance_probability
from .science_s1_benchmark_v13b import (
    _candidate_bank,
    _confidence_indices,
    _directional_error,
    _mixture_predictive_probability,
    _observed_log_probability,
    _select_disagreement_feature,
)
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-resolution-horizon-benchmark-v13c"
METHOD_VERSION = "prequential-finite-confidence-radius-v1"
GRID_SPACINGS_DEGREES = (15.0, 10.0, 5.0)
TRUE_ANGLES_DEGREES = tuple(float(value) for value in range(0, 360, 30))
HORIZONS = (120, 180, 240)
TARGET_ERROR = 0.15
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
ALPHA_LEVEL = 0.05
SEEDS = tuple(range(64))


def _parameter_angles(grid_spacing_degrees: float) -> tuple[float, ...]:
    spacing = float(grid_spacing_degrees)
    if spacing <= 0.0 or spacing >= 180.0:
        raise ValueError("grid_spacing_degrees must lie strictly between zero and 180")
    count = round(360.0 / spacing)
    if abs(count * spacing - 360.0) > 1e-9:
        raise ValueError("grid_spacing_degrees must evenly divide 360 degrees")
    return tuple(index * spacing for index in range(count))


def _alpha_from_angle(angle_degrees: float) -> tuple[float, ...]:
    angle = float(angle_degrees) * pi / 180.0
    return (0.0, SLOPE_NORM * cos(angle), SLOPE_NORM * sin(angle))


def _confidence_radius(
    center_index: int,
    confidence_indices: Sequence[int],
    parameters: Sequence[Sequence[float]],
) -> float:
    center = parameters[center_index]
    return max(_directional_error(center, parameters[index]) for index in confidence_indices)


def _run_path(
    *,
    parameter_angles: Sequence[float],
    true_angle_degrees: float,
    candidates: Sequence[Sequence[float]],
    seed: int,
    target_error: float,
    max_observations: int,
    alpha_level: float,
) -> dict[str, object]:
    parameters = tuple(_alpha_from_angle(angle) for angle in parameter_angles)
    try:
        true_index = tuple(parameter_angles).index(float(true_angle_degrees))
    except ValueError as error:
        raise ValueError("true angle must lie exactly on the finite parameter grid") from error

    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    log_predictive_joint = 0.0
    confidence_indices = tuple(range(len(parameters)))
    first_stop: dict[str, object] | None = None
    first_exclusion_observation: int | None = None
    radius_at_horizon: dict[int, float] = {}
    confidence_size_at_horizon: dict[int, int] = {}

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

        true_in_confidence_set = true_index in confidence_indices
        if not true_in_confidence_set and first_exclusion_observation is None:
            first_exclusion_observation = observation_index

        center_index = max(confidence_indices, key=lambda index: log_likelihoods[index])
        radius = _confidence_radius(center_index, confidence_indices, parameters)
        true_error = _directional_error(parameters[center_index], parameters[true_index])

        if first_stop is None and radius <= target_error:
            first_stop = {
                "observation_count": observation_index,
                "center_angle_degrees": parameter_angles[center_index],
                "certified_radius": radius,
                "confidence_size": len(confidence_indices),
                "true_directional_error": true_error,
                "true_in_confidence_set": true_in_confidence_set,
                "false_stop": true_error > target_error,
            }

        radius_at_horizon[observation_index] = radius
        confidence_size_at_horizon[observation_index] = len(confidence_indices)

    return {
        "true_angle_degrees": true_angle_degrees,
        "first_stop": first_stop,
        "first_exclusion_observation": first_exclusion_observation,
        "radius_at_horizon": {
            str(index): radius_at_horizon[index]
            for index in radius_at_horizon
            if index == max_observations
        },
        "confidence_size_at_horizon": {
            str(index): confidence_size_at_horizon[index]
            for index in confidence_size_at_horizon
            if index == max_observations
        },
    }


def _summarize_horizon(
    paths: Sequence[dict[str, object]],
    *,
    horizon: int,
) -> dict[str, object]:
    stopped: list[dict[str, object]] = []
    false_stops: list[dict[str, object]] = []
    excluded = 0

    for path in paths:
        stop = path["first_stop"]
        if stop is not None:
            stop_record = cast(dict[str, object], stop)
            if cast(int, stop_record["observation_count"]) <= horizon:
                stopped.append(stop_record)
                if bool(stop_record["false_stop"]):
                    false_stops.append(stop_record)
        first_exclusion = path["first_exclusion_observation"]
        if first_exclusion is not None and cast(int, first_exclusion) <= horizon:
            excluded += 1

    stopping_observations = [cast(int, stop["observation_count"]) for stop in stopped]
    return {
        "horizon": horizon,
        "runs": len(paths),
        "stops": len(stopped),
        "stop_rate": len(stopped) / len(paths),
        "false_stops": len(false_stops),
        "false_stop_rate": len(false_stops) / len(paths),
        "false_stop_given_stop": len(false_stops) / len(stopped) if stopped else 0.0,
        "true_excluded_ever_rate": excluded / len(paths),
        "stopping_observation": {
            "mean": mean(stopping_observations) if stopping_observations else None,
            "median": median(stopping_observations) if stopping_observations else None,
        },
    }


def run_benchmark_v13c(
    *,
    grid_spacings_degrees: Iterable[float] = GRID_SPACINGS_DEGREES,
    true_angles_degrees: Iterable[float] = TRUE_ANGLES_DEGREES,
    horizons: Iterable[int] = HORIZONS,
    seeds: Iterable[int] = SEEDS,
    target_error: float = TARGET_ERROR,
    candidate_count: int = CANDIDATE_COUNT,
    alpha_level: float = ALPHA_LEVEL,
) -> dict[str, object]:
    spacings = tuple(float(value) for value in grid_spacings_degrees)
    true_angles = tuple(float(value) for value in true_angles_degrees)
    horizon_values = tuple(sorted(int(value) for value in horizons))
    seed_values = tuple(int(value) for value in seeds)

    if not spacings:
        raise ValueError("grid_spacings_degrees must not be empty")
    if not true_angles:
        raise ValueError("true_angles_degrees must not be empty")
    if not horizon_values or horizon_values[0] <= 0:
        raise ValueError("horizons must contain positive integers")
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if target_error <= 0.0 or target_error >= 0.5:
        raise ValueError("target_error must lie strictly between zero and 0.5")
    if alpha_level <= 0.0 or alpha_level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")

    candidates = _candidate_bank(candidate_count)
    max_observations = max(horizon_values)
    grid_cells: list[dict[str, object]] = []

    for spacing in spacings:
        parameter_angles = _parameter_angles(spacing)
        missing = [angle for angle in true_angles if angle not in parameter_angles]
        if missing:
            raise ValueError(f"all true angles must lie on every grid; missing {missing}")

        paths: list[dict[str, object]] = []
        for true_angle_index, true_angle in enumerate(true_angles):
            for seed in seed_values:
                paths.append(
                    _run_path(
                        parameter_angles=parameter_angles,
                        true_angle_degrees=true_angle,
                        candidates=candidates,
                        seed=(
                            50_000_000
                            + int(round(spacing * 1000.0)) * 100_000
                            + true_angle_index * 10_000
                            + seed
                        ),
                        target_error=target_error,
                        max_observations=max_observations,
                        alpha_level=alpha_level,
                    )
                )

        target_degrees = target_error * 180.0
        effective_grid_radius_degrees = floor(target_degrees / spacing + 1e-12) * spacing
        grid_cells.append(
            {
                "grid_spacing_degrees": spacing,
                "parameter_count": len(parameter_angles),
                "target_degrees": target_degrees,
                "effective_grid_radius_degrees": effective_grid_radius_degrees,
                "runs": len(paths),
                "horizon_summaries": [
                    _summarize_horizon(paths, horizon=horizon) for horizon in horizon_values
                ],
            }
        )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Finite-grid decomposition of strict directional-certification efficiency. The "
            "e-process numerator, nominal alpha, disagreement query policy, slope norm, and "
            "target are frozen from v13b. Only angular grid spacing and observation horizon "
            "vary. Shared true directions lie exactly on every grid. This is not continuous "
            "certification or human validation."
        ),
        "config": {
            "grid_spacings_degrees": spacings,
            "true_angles_degrees": true_angles,
            "horizons": horizon_values,
            "seeds": seed_values,
            "target_error": target_error,
            "target_degrees": target_error * 180.0,
            "slope_norm": SLOPE_NORM,
            "candidate_count": candidate_count,
            "alpha_level": alpha_level,
            "predictive_numerator": "uniform-prior finite likelihood-mixture predictive",
            "query_design": "maximize probability range over the prior confidence set",
        },
        "grid_cells": grid_cells,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13c(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
