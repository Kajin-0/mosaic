from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import log
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
from .science_s1_benchmark_v13d import (
    _mle_face_predictive_probability,
    _snml_predictive_probability,
)
from .science_s1_benchmark_v13e import _paired_exact_p_value
from .science_s1_benchmark_v13f import _intersection, _radius_about_center
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-theta-challenger-benchmark-v13g"
METHOD_VERSION = "prequential-theta-specific-nested-confidence-v1"
GRID_SPACING_DEGREES = 5.0
TRUE_ANGLES_DEGREES = tuple(float(value) for value in range(0, 360, 30))
TARGET_ERROR = 0.15
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
ALPHA_LEVEL = 0.05
MAX_OBSERVATIONS = 240
SEEDS = tuple(range(448, 576))
COMMON_PREDICTORS = ("mixture_all", "mle_face", "snml")
THETA_CHALLENGER = "theta_challenger"


def _average_parameter_probability(
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
    indices: Sequence[int],
) -> float:
    if not indices:
        raise ValueError("indices must not be empty")
    return sum(acceptance_probability(parameters[index], features) for index in indices) / len(
        indices
    )


def _maximizer_face(log_likelihoods: Sequence[float]) -> tuple[int, ...]:
    maximum = max(log_likelihoods)
    return tuple(index for index, value in enumerate(log_likelihoods) if value == maximum)


def _second_face_excluding_unique_max(
    log_likelihoods: Sequence[float],
    unique_max_index: int,
) -> tuple[int, ...]:
    alternatives = tuple(
        (index, value) for index, value in enumerate(log_likelihoods) if index != unique_max_index
    )
    maximum = max(value for _, value in alternatives)
    return tuple(index for index, value in alternatives if value == maximum)


def _theta_challenger_probabilities(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
) -> tuple[float, ...]:
    """Return leave-null-out one-step-lagged MLE predictive probabilities.

    For candidate null j, q_{t,j} is the average prediction over the historical
    maximum-likelihood face after excluding j. All choices are made before the
    current outcome is observed.
    """

    if len(log_likelihoods) != len(parameters):
        raise ValueError("likelihood and parameter dimensions must agree")
    if len(parameters) < 2:
        raise ValueError("theta-specific challengers require at least two parameters")

    global_face = _maximizer_face(log_likelihoods)
    global_probability = _average_parameter_probability(parameters, features, global_face)
    probabilities: list[float] = []

    if len(global_face) == 1:
        unique_max = global_face[0]
        second_face = _second_face_excluding_unique_max(log_likelihoods, unique_max)
        second_probability = _average_parameter_probability(parameters, features, second_face)
        for null_index in range(len(parameters)):
            probabilities.append(
                second_probability if null_index == unique_max else global_probability
            )
        return tuple(probabilities)

    face_lookup = set(global_face)
    for null_index in range(len(parameters)):
        if null_index not in face_lookup:
            probabilities.append(global_probability)
            continue
        reduced_face = tuple(index for index in global_face if index != null_index)
        probabilities.append(_average_parameter_probability(parameters, features, reduced_face))
    return tuple(probabilities)


def _theta_challenger_current_set(
    log_predictive_joint: Sequence[float],
    log_likelihoods: Sequence[float],
    *,
    alpha_level: float,
) -> tuple[int, ...]:
    if len(log_predictive_joint) != len(log_likelihoods):
        raise ValueError("challenger and likelihood dimensions must agree")
    cutoff_offset = log(alpha_level)
    return tuple(
        index
        for index, (log_q, log_likelihood) in enumerate(
            zip(log_predictive_joint, log_likelihoods, strict=True)
        )
        if log_likelihood > log_q + cutoff_offset
    )


def _run_path(
    *,
    parameter_angles: Sequence[float],
    true_angle_degrees: float,
    candidates: Sequence[Sequence[float]],
    seed: int,
    max_observations: int,
    target_error: float,
    alpha_level: float,
) -> dict[str, object]:
    parameters = tuple(_alpha_from_angle(angle) for angle in parameter_angles)
    try:
        true_index = tuple(parameter_angles).index(float(true_angle_degrees))
    except ValueError as error:
        raise ValueError("true angle must lie on the finite parameter grid") from error

    predictor_names = COMMON_PREDICTORS + (THETA_CHALLENGER,)
    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    common_log_q = {name: 0.0 for name in COMMON_PREDICTORS}
    challenger_log_q = [0.0] * len(parameters)
    current_sets = {name: tuple(range(len(parameters))) for name in predictor_names}
    nested_sets = {name: tuple(range(len(parameters))) for name in predictor_names}
    first_stop: dict[str, dict[str, object] | None] = {name: None for name in predictor_names}
    first_truth_exclusion: dict[str, int | None] = {name: None for name in predictor_names}
    first_nested_empty: dict[str, int | None] = {name: None for name in predictor_names}

    for observation_index in range(1, max_observations + 1):
        # Acquisition remains frozen to the historical current-time all-grid-mixture
        # controller. The challenger changes certification only, not the observed path.
        features = _select_disagreement_feature(
            current_sets["mixture_all"],
            parameters,
            candidates,
        )
        common_probability = {
            "mixture_all": _mixture_predictive_probability(
                log_likelihoods,
                parameters,
                features,
            ),
            "mle_face": _mle_face_predictive_probability(
                log_likelihoods,
                parameters,
                features,
            ),
            "snml": _snml_predictive_probability(
                log_likelihoods,
                parameters,
                features,
            ),
        }
        challenger_probability = _theta_challenger_probabilities(
            log_likelihoods,
            parameters,
            features,
        )

        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability

        for name in COMMON_PREDICTORS:
            common_log_q[name] += _observed_log_probability(common_probability[name], accepted)
        for index, probability in enumerate(challenger_probability):
            challenger_log_q[index] += _observed_log_probability(probability, accepted)
        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        common_current = {
            name: _confidence_indices(
                common_log_q[name],
                log_likelihoods,
                alpha_level=alpha_level,
            )
            for name in COMMON_PREDICTORS
        }
        challenger_current = _theta_challenger_current_set(
            challenger_log_q,
            log_likelihoods,
            alpha_level=alpha_level,
        )
        all_current = {**common_current, THETA_CHALLENGER: challenger_current}

        center_index = max(range(len(parameters)), key=lambda index: log_likelihoods[index])
        true_error = _directional_error(parameters[center_index], parameters[true_index])

        for name in predictor_names:
            current = all_current[name]
            if name in COMMON_PREDICTORS and not current:
                raise RuntimeError(f"{name} current-time finite confidence set became empty")
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


def _summarize(paths: Sequence[dict[str, object]], predictor: str) -> dict[str, object]:
    stopped: list[dict[str, object]] = []
    false_stops = 0
    geometry_violations = 0
    truth_exclusions = 0
    empty_sets = 0

    for path in paths:
        stop = cast(dict[str, object], path["first_stop"])[predictor]
        if stop is not None:
            record = cast(dict[str, object], stop)
            stopped.append(record)
            false_stops += int(bool(record["false_stop"]))
            geometry_violations += int(bool(record["geometry_violation"]))
        truth_exclusions += int(
            cast(dict[str, object], path["first_truth_exclusion_observation"])[predictor]
            is not None
        )
        empty_sets += int(
            cast(dict[str, object], path["first_nested_empty_observation"])[predictor] is not None
        )

    observations = [cast(int, record["observation_count"]) for record in stopped]
    return {
        "predictor": predictor,
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


def _paired_comparison(
    paths: Sequence[dict[str, object]],
    *,
    left: str,
    right: str,
) -> dict[str, object]:
    left_only = 0
    right_only = 0
    both = 0
    neither = 0
    for path in paths:
        stops = cast(dict[str, object], path["first_stop"])
        left_stopped = stops[left] is not None
        right_stopped = stops[right] is not None
        if left_stopped and right_stopped:
            both += 1
        elif left_stopped:
            left_only += 1
        elif right_stopped:
            right_only += 1
        else:
            neither += 1
    return {
        "left": left,
        "right": right,
        "left_only": left_only,
        "right_only": right_only,
        "both": both,
        "neither": neither,
        "paired_exact_p_value": _paired_exact_p_value(left_only, right_only),
    }


def run_benchmark_v13g(
    *,
    seeds: Iterable[int] = SEEDS,
    true_angles_degrees: Iterable[float] = TRUE_ANGLES_DEGREES,
    max_observations: int = MAX_OBSERVATIONS,
    target_error: float = TARGET_ERROR,
    alpha_level: float = ALPHA_LEVEL,
) -> dict[str, object]:
    seed_values = tuple(int(value) for value in seeds)
    true_angles = tuple(float(value) for value in true_angles_degrees)
    if not seed_values:
        raise ValueError("seeds must not be empty")
    if not true_angles:
        raise ValueError("true_angles_degrees must not be empty")
    if max_observations <= 0:
        raise ValueError("max_observations must be positive")
    if not 0.0 < alpha_level < 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")

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
                    seed=80_000_000 + true_angle_index * 100_000 + seed,
                    max_observations=max_observations,
                    target_error=target_error,
                    alpha_level=alpha_level,
                )
            )

    predictor_names = COMMON_PREDICTORS + (THETA_CHALLENGER,)
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Fresh-seed finite-grid test of theta-specific predictable challenger numerators "
            "under the nested confidence representation established by v13f. Query selection "
            "is frozen to the historical current-time all-grid-mixture disagreement controller. "
            "For candidate null j, q_{t,j} is the one-step-lagged maximum-likelihood alternative "
            "predictive after excluding j, with tied maximizers averaged before the response."
        ),
        "config": {
            "grid_spacing_degrees": GRID_SPACING_DEGREES,
            "parameter_count": len(parameter_angles),
            "true_angles_degrees": true_angles,
            "seeds": seed_values,
            "max_observations": max_observations,
            "target_error": target_error,
            "target_degrees": target_error * 180.0,
            "slope_norm": SLOPE_NORM,
            "candidate_count": CANDIDATE_COUNT,
            "alpha_level": alpha_level,
            "common_predictors": COMMON_PREDICTORS,
            "theta_specific_predictor": THETA_CHALLENGER,
            "confidence_representation": "running intersection / nested",
            "query_design_controller": (
                "current-time all-grid mixture confidence set with probability-range disagreement"
            ),
            "reported_center": "global finite-grid maximum-likelihood direction at each time",
            "primary_endpoint": "paired stop-probability difference by 240 observations",
        },
        "summaries": [_summarize(paths, predictor) for predictor in predictor_names],
        "paired_comparisons": [
            _paired_comparison(paths, left=THETA_CHALLENGER, right="mixture_all"),
            _paired_comparison(paths, left=THETA_CHALLENGER, right="snml"),
            _paired_comparison(paths, left=THETA_CHALLENGER, right="mle_face"),
        ],
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13g(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
