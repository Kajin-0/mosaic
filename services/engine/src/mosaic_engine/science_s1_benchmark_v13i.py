from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import exp, log
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
from .science_s1_benchmark_v13c import _alpha_from_angle, _parameter_angles
from .science_s1_benchmark_v13e import _paired_exact_p_value
from .science_s1_benchmark_v13f import _intersection, _radius_about_center
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-local-neighbor-benchmark-v13i"
METHOD_VERSION = "prequential-local-neighbor-nested-confidence-v1"
GRID_SPACING_DEGREES = 5.0
TRUE_ANGLES_DEGREES = tuple(float(value) for value in range(0, 360, 30))
TARGET_ERROR = 0.15
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
ALPHA_LEVEL = 0.05
HORIZONS = (120, 180, 240)
SEEDS = tuple(range(576, 704))
BASELINE = "mixture_all"
LOCAL_NEIGHBOR = "local_neighbor"


def _logsumexp_pair(left: float, right: float) -> float:
    maximum = max(left, right)
    return maximum + log(exp(left - maximum) + exp(right - maximum))


def _neighbor_indices(index: int, parameter_count: int) -> tuple[int, int]:
    if parameter_count < 3:
        raise ValueError("local-neighbor mixture requires at least three parameters")
    return ((index - 1) % parameter_count, (index + 1) % parameter_count)


def _local_neighbor_log_joint_numerators(
    log_likelihoods: Sequence[float],
) -> tuple[float, ...]:
    parameter_count = len(log_likelihoods)
    if parameter_count < 3:
        raise ValueError("local-neighbor mixture requires at least three parameters")
    log_two = log(2.0)
    return tuple(
        _logsumexp_pair(
            log_likelihoods[_neighbor_indices(index, parameter_count)[0]],
            log_likelihoods[_neighbor_indices(index, parameter_count)[1]],
        )
        - log_two
        for index in range(parameter_count)
    )


def _local_neighbor_predictive_probabilities(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
) -> tuple[float, ...]:
    if len(log_likelihoods) != len(parameters):
        raise ValueError("likelihood and parameter dimensions must agree")
    parameter_count = len(parameters)
    probabilities: list[float] = []
    for index in range(parameter_count):
        left, right = _neighbor_indices(index, parameter_count)
        maximum = max(log_likelihoods[left], log_likelihoods[right])
        left_weight = exp(log_likelihoods[left] - maximum)
        right_weight = exp(log_likelihoods[right] - maximum)
        denominator = left_weight + right_weight
        probability = (
            left_weight * acceptance_probability(parameters[left], features)
            + right_weight * acceptance_probability(parameters[right], features)
        ) / denominator
        probabilities.append(probability)
    return tuple(probabilities)


def _local_neighbor_current_set(
    log_likelihoods: Sequence[float],
    *,
    alpha_level: float,
) -> tuple[int, ...]:
    if not 0.0 < alpha_level < 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")
    log_q = _local_neighbor_log_joint_numerators(log_likelihoods)
    cutoff = log(alpha_level)
    return tuple(
        index
        for index, (log_likelihood, log_numerator) in enumerate(
            zip(log_likelihoods, log_q, strict=True)
        )
        if log_likelihood > log_numerator + cutoff
    )


def _run_path(
    *,
    parameter_angles: Sequence[float],
    true_angle_degrees: float,
    candidates: Sequence[Sequence[float]],
    seed: int,
    horizons: Sequence[int],
    target_error: float,
    alpha_level: float,
) -> dict[str, object]:
    parameters = tuple(_alpha_from_angle(angle) for angle in parameter_angles)
    try:
        true_index = tuple(parameter_angles).index(float(true_angle_degrees))
    except ValueError as error:
        raise ValueError("true angle must lie on the finite parameter grid") from error

    max_observations = max(horizons)
    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    baseline_log_q = 0.0
    current_sets = {
        BASELINE: tuple(range(len(parameters))),
        LOCAL_NEIGHBOR: tuple(range(len(parameters))),
    }
    nested_sets = dict(current_sets)
    first_stop: dict[str, dict[str, object] | None] = {BASELINE: None, LOCAL_NEIGHBOR: None}
    first_truth_exclusion: dict[str, int | None] = {BASELINE: None, LOCAL_NEIGHBOR: None}
    first_nested_empty: dict[str, int | None] = {BASELINE: None, LOCAL_NEIGHBOR: None}

    for observation_index in range(1, max_observations + 1):
        # Freeze acquisition to the historical current-time all-grid-mixture controller.
        features = _select_disagreement_feature(
            current_sets[BASELINE],
            parameters,
            candidates,
        )
        baseline_probability = _mixture_predictive_probability(
            log_likelihoods,
            parameters,
            features,
        )
        # Explicitly form the predictable local numerators before the response. The
        # benchmark computes their cumulative joint values algebraically after the response.
        _local_neighbor_predictive_probabilities(log_likelihoods, parameters, features)

        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability
        baseline_log_q += _observed_log_probability(baseline_probability, accepted)
        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        baseline_current = _confidence_indices(
            baseline_log_q,
            log_likelihoods,
            alpha_level=alpha_level,
        )
        if not baseline_current:
            raise RuntimeError("baseline current-time confidence set became empty")
        local_current = _local_neighbor_current_set(
            log_likelihoods,
            alpha_level=alpha_level,
        )
        all_current = {BASELINE: baseline_current, LOCAL_NEIGHBOR: local_current}
        center_index = max(range(len(parameters)), key=lambda index: log_likelihoods[index])
        true_error = _directional_error(parameters[center_index], parameters[true_index])

        for name in (BASELINE, LOCAL_NEIGHBOR):
            current = all_current[name]
            current_sets[name] = current
            nested = _intersection(nested_sets[name], current)
            nested_sets[name] = nested

            if true_index not in nested and first_truth_exclusion[name] is None:
                first_truth_exclusion[name] = observation_index
            if not nested and first_nested_empty[name] is None:
                first_nested_empty[name] = observation_index
            if not nested or first_stop[name] is not None:
                continue

            radius = _radius_about_center(center_index, nested, parameters)
            if radius <= target_error:
                true_in_set = true_index in nested
                first_stop[name] = {
                    "observation_count": observation_index,
                    "center_angle_degrees": parameter_angles[center_index],
                    "certified_radius": radius,
                    "confidence_size": len(nested),
                    "true_directional_error": true_error,
                    "true_in_confidence_set": true_in_set,
                    "false_stop": true_error > target_error,
                    "geometry_violation": true_error > target_error and true_in_set,
                }

    return {
        "true_angle_degrees": true_angle_degrees,
        "first_stop": first_stop,
        "first_truth_exclusion_observation": first_truth_exclusion,
        "first_nested_empty_observation": first_nested_empty,
    }


def _summarize(
    paths: Sequence[dict[str, object]],
    *,
    predictor: str,
    horizon: int,
) -> dict[str, object]:
    stopped: list[dict[str, object]] = []
    false_stops = 0
    geometry_violations = 0
    truth_exclusions = 0
    empty_sets = 0

    for path in paths:
        stop = cast(dict[str, object], path["first_stop"])[predictor]
        if stop is not None:
            record = cast(dict[str, object], stop)
            if cast(int, record["observation_count"]) <= horizon:
                stopped.append(record)
                false_stops += int(bool(record["false_stop"]))
                geometry_violations += int(bool(record["geometry_violation"]))

        exclusion = cast(dict[str, object], path["first_truth_exclusion_observation"])[predictor]
        truth_exclusions += int(exclusion is not None and cast(int, exclusion) <= horizon)
        empty = cast(dict[str, object], path["first_nested_empty_observation"])[predictor]
        empty_sets += int(empty is not None and cast(int, empty) <= horizon)

    observations = [cast(int, record["observation_count"]) for record in stopped]
    return {
        "predictor": predictor,
        "horizon": horizon,
        "runs": len(paths),
        "stops": len(stopped),
        "stop_rate": len(stopped) / len(paths),
        "false_stops": false_stops,
        "false_stop_rate": false_stops / len(paths),
        "false_stop_given_stop": false_stops / len(stopped) if stopped else 0.0,
        "geometry_violations": geometry_violations,
        "truth_excluded_ever_rate": truth_exclusions / len(paths),
        "nested_empty_rate": empty_sets / len(paths),
        "stopping_observation": {
            "mean": mean(observations) if observations else None,
            "median": median(observations) if observations else None,
        },
    }


def _paired_at_horizon(
    paths: Sequence[dict[str, object]],
    *,
    horizon: int,
) -> dict[str, object]:
    local_only = 0
    baseline_only = 0
    both = 0
    neither = 0
    for path in paths:
        stops = cast(dict[str, object], path["first_stop"])
        local_stop = stops[LOCAL_NEIGHBOR]
        baseline_stop = stops[BASELINE]
        local = local_stop is not None and cast(
            int, cast(dict[str, object], local_stop)["observation_count"]
        ) <= horizon
        baseline = baseline_stop is not None and cast(
            int, cast(dict[str, object], baseline_stop)["observation_count"]
        ) <= horizon
        if local and baseline:
            both += 1
        elif local:
            local_only += 1
        elif baseline:
            baseline_only += 1
        else:
            neither += 1
    return {
        "horizon": horizon,
        "left": LOCAL_NEIGHBOR,
        "right": BASELINE,
        "left_only": local_only,
        "right_only": baseline_only,
        "both": both,
        "neither": neither,
        "paired_exact_p_value": _paired_exact_p_value(local_only, baseline_only),
    }


def run_benchmark_v13i(
    *,
    seeds: Iterable[int] = SEEDS,
    true_angles_degrees: Iterable[float] = TRUE_ANGLES_DEGREES,
    horizons: Iterable[int] = HORIZONS,
    target_error: float = TARGET_ERROR,
    alpha_level: float = ALPHA_LEVEL,
) -> dict[str, object]:
    seed_values = tuple(int(value) for value in seeds)
    true_angles = tuple(float(value) for value in true_angles_degrees)
    horizon_values = tuple(sorted(int(value) for value in horizons))
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if not true_angles:
        raise ValueError("true_angles_degrees must not be empty")
    if not horizon_values or horizon_values[0] <= 0:
        raise ValueError("horizons must contain positive values")

    parameter_angles = _parameter_angles(GRID_SPACING_DEGREES)
    missing = [angle for angle in true_angles if angle not in parameter_angles]
    if missing:
        raise ValueError(f"all true angles must lie on the finite grid; missing {missing}")
    candidates = _candidate_bank(CANDIDATE_COUNT)

    paths: list[dict[str, object]] = []
    for true_angle_index, true_angle in enumerate(true_angles):
        for seed in seed_values:
            paths.append(
                _run_path(
                    parameter_angles=parameter_angles,
                    true_angle_degrees=true_angle,
                    candidates=candidates,
                    seed=90_000_000 + true_angle_index * 100_000 + seed,
                    horizons=horizon_values,
                    target_error=target_error,
                    alpha_level=alpha_level,
                )
            )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Fresh-seed finite-grid test of a per-null local-neighbor alternative mixture under "
            "nested confidence sequences. Candidate j uses the posterior predictive induced by "
            "a fixed 50/50 prior on angular neighbors j-1 and j+1. Acquisition remains frozen "
            "to the historical current-time all-grid-mixture disagreement controller."
        ),
        "config": {
            "grid_spacing_degrees": GRID_SPACING_DEGREES,
            "parameter_count": len(parameter_angles),
            "true_angles_degrees": true_angles,
            "seeds": seed_values,
            "horizons": horizon_values,
            "target_error": target_error,
            "target_degrees": target_error * 180.0,
            "slope_norm": SLOPE_NORM,
            "candidate_count": CANDIDATE_COUNT,
            "alpha_level": alpha_level,
            "baseline": BASELINE,
            "candidate": LOCAL_NEIGHBOR,
            "confidence_representation": "running intersection / nested",
            "query_design_controller": (
                "current-time all-grid mixture confidence set with probability-range disagreement"
            ),
            "reported_center": "global finite-grid maximum-likelihood direction at each time",
            "primary_endpoint": "paired stop-probability difference by 240 observations",
        },
        "summaries": [
            _summarize(paths, predictor=predictor, horizon=horizon)
            for predictor in (BASELINE, LOCAL_NEIGHBOR)
            for horizon in horizon_values
        ],
        "paired_comparisons": [
            _paired_at_horizon(paths, horizon=horizon) for horizon in horizon_values
        ],
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13i(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
