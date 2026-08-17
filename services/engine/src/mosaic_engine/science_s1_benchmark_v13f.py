from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
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
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-nested-confidence-benchmark-v13f"
METHOD_VERSION = "prequential-nested-finite-confidence-radius-v1"
GRID_SPACING_DEGREES = 5.0
TRUE_ANGLES_DEGREES = tuple(float(value) for value in range(0, 360, 30))
TARGET_ERROR = 0.15
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
ALPHA_LEVEL = 0.05
MAX_OBSERVATIONS = 240
SEEDS = tuple(range(320, 448))
PREDICTORS = ("mixture_all", "mle_face", "snml")
PRIMARY_PREDICTOR = "mle_face"


def _radius_about_center(
    center_index: int,
    confidence_indices: Sequence[int],
    parameters: Sequence[Sequence[float]],
) -> float:
    if not confidence_indices:
        raise ValueError("confidence_indices must not be empty")
    return max(
        _directional_error(parameters[center_index], parameters[index])
        for index in confidence_indices
    )


def _intersection(previous: Sequence[int], current: Sequence[int]) -> tuple[int, ...]:
    current_lookup = set(current)
    return tuple(index for index in previous if index in current_lookup)


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

    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    log_predictive_joint = {name: 0.0 for name in PREDICTORS}
    current_sets = {name: tuple(range(len(parameters))) for name in PREDICTORS}
    nested_sets = {name: tuple(range(len(parameters))) for name in PREDICTORS}
    first_stop: dict[str, dict[str, dict[str, object] | None]] = {
        name: {"current": None, "nested": None} for name in PREDICTORS
    }
    first_exclusion: dict[str, int | None] = {name: None for name in PREDICTORS}
    first_nested_empty: dict[str, int | None] = {name: None for name in PREDICTORS}
    maximum_radius_gap = {name: 0.0 for name in PREDICTORS}

    for observation_index in range(1, max_observations + 1):
        # Freeze the acquisition controller to the existing current-time all-grid mixture
        # confidence set. v13f changes only the representation used for certification.
        features = _select_disagreement_feature(
            current_sets["mixture_all"],
            parameters,
            candidates,
        )
        predictive_probability = {
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

        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability
        for name in PREDICTORS:
            log_predictive_joint[name] += _observed_log_probability(
                predictive_probability[name],
                accepted,
            )
        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        center_index = max(range(len(parameters)), key=lambda index: log_likelihoods[index])
        true_error = _directional_error(parameters[center_index], parameters[true_index])

        for name in PREDICTORS:
            current = _confidence_indices(
                log_predictive_joint[name],
                log_likelihoods,
                alpha_level=alpha_level,
            )
            if not current:
                raise RuntimeError(f"{name} current-time finite confidence set became empty")
            current_sets[name] = current
            nested = _intersection(nested_sets[name], current)
            nested_sets[name] = nested

            if true_index not in current and first_exclusion[name] is None:
                first_exclusion[name] = observation_index
            if not nested and first_nested_empty[name] is None:
                first_nested_empty[name] = observation_index

            current_radius = _radius_about_center(center_index, current, parameters)
            if nested:
                nested_radius = _radius_about_center(center_index, nested, parameters)
                if nested_radius > current_radius + 1e-12:
                    raise AssertionError("nested confidence radius exceeded current-time radius")
                maximum_radius_gap[name] = max(
                    maximum_radius_gap[name],
                    current_radius - nested_radius,
                )
            else:
                nested_radius = None

            for representation, indices, radius in (
                ("current", current, current_radius),
                ("nested", nested, nested_radius),
            ):
                if radius is None or first_stop[name][representation] is not None:
                    continue
                if radius <= target_error:
                    true_in_set = true_index in indices
                    first_stop[name][representation] = {
                        "observation_count": observation_index,
                        "center_angle_degrees": parameter_angles[center_index],
                        "certified_radius": radius,
                        "confidence_size": len(indices),
                        "true_directional_error": true_error,
                        "true_in_confidence_set": true_in_set,
                        "false_stop": true_error > target_error,
                        "geometry_violation": true_error > target_error and true_in_set,
                    }

    return {
        "true_angle_degrees": true_angle_degrees,
        "first_stop": first_stop,
        "first_exclusion_observation": first_exclusion,
        "first_nested_empty_observation": first_nested_empty,
        "maximum_radius_gap": maximum_radius_gap,
    }


def _summarize(
    paths: Sequence[dict[str, object]],
    *,
    predictor: str,
    representation: str,
) -> dict[str, object]:
    stopped: list[dict[str, object]] = []
    false_stops = 0
    geometry_violations = 0
    for path in paths:
        by_predictor = cast(dict[str, object], path["first_stop"])
        by_representation = cast(dict[str, object], by_predictor[predictor])
        stop = by_representation[representation]
        if stop is None:
            continue
        record = cast(dict[str, object], stop)
        stopped.append(record)
        false_stops += int(bool(record["false_stop"]))
        geometry_violations += int(bool(record["geometry_violation"]))

    observations = [cast(int, record["observation_count"]) for record in stopped]
    return {
        "predictor": predictor,
        "representation": representation,
        "runs": len(paths),
        "stops": len(stopped),
        "stop_rate": len(stopped) / len(paths),
        "false_stops": false_stops,
        "false_stop_rate": false_stops / len(paths),
        "geometry_violations": geometry_violations,
        "stopping_observation": {
            "mean": mean(observations) if observations else None,
            "median": median(observations) if observations else None,
        },
    }


def _paired_gain(paths: Sequence[dict[str, object]], predictor: str) -> dict[str, object]:
    nested_earlier = 0
    equal = 0
    current_only = 0
    nested_only = 0
    both = 0
    delays: list[int] = []

    for path in paths:
        by_predictor = cast(dict[str, object], path["first_stop"])
        stops = cast(dict[str, object], by_predictor[predictor])
        current = stops["current"]
        nested = stops["nested"]
        if current is None and nested is None:
            continue
        if current is None:
            nested_only += 1
            continue
        if nested is None:
            current_only += 1
            continue
        both += 1
        current_observation = cast(int, cast(dict[str, object], current)["observation_count"])
        nested_observation = cast(int, cast(dict[str, object], nested)["observation_count"])
        if nested_observation < current_observation:
            nested_earlier += 1
            delays.append(current_observation - nested_observation)
        elif nested_observation == current_observation:
            equal += 1
        else:
            raise AssertionError("nested certification occurred later than current certification")

    return {
        "predictor": predictor,
        "nested_earlier": nested_earlier,
        "equal": equal,
        "nested_only": nested_only,
        "current_only": current_only,
        "both": both,
        "observation_gain_when_earlier": {
            "mean": mean(delays) if delays else None,
            "median": median(delays) if delays else None,
        },
    }


def run_benchmark_v13f(
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
                    seed=70_000_000 + true_angle_index * 100_000 + seed,
                    max_observations=max_observations,
                    target_error=target_error,
                    alpha_level=alpha_level,
                )
            )

    nested_empty_rates = {}
    truth_exclusion_rates = {}
    maximum_radius_gaps = {}
    for predictor in PREDICTORS:
        nested_empty_rates[predictor] = sum(
            cast(dict[str, object], path["first_nested_empty_observation"])[predictor] is not None
            for path in paths
        ) / len(paths)
        truth_exclusion_rates[predictor] = sum(
            cast(dict[str, object], path["first_exclusion_observation"])[predictor] is not None
            for path in paths
        ) / len(paths)
        maximum_radius_gaps[predictor] = max(
            cast(float, cast(dict[str, object], path["maximum_radius_gap"])[predictor])
            for path in paths
        )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Fresh-seed finite-grid isolation of the running-intersection confidence-sequence "
            "gain. The current-time and nested sets use identical predictors, observations, "
            "global finite-grid MLE centers, target, alpha, and acquisition path. The nested "
            "set is the exact intersection of all current-time confidence sets observed so far."
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
            "predictors": PREDICTORS,
            "primary_predictor": PRIMARY_PREDICTOR,
            "query_design_controller": (
                "current-time all-grid mixture confidence set with probability-range disagreement"
            ),
            "reported_center": "global finite-grid maximum-likelihood direction at each time",
        },
        "summaries": [
            _summarize(paths, predictor=predictor, representation=representation)
            for predictor in PREDICTORS
            for representation in ("current", "nested")
        ],
        "paired_gains": [_paired_gain(paths, predictor) for predictor in PREDICTORS],
        "truth_exclusion_rates": truth_exclusion_rates,
        "nested_empty_rates": nested_empty_rates,
        "maximum_radius_gaps": maximum_radius_gaps,
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13f(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
