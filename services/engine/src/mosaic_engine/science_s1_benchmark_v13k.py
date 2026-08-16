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
from .science_s1_benchmark_v13e import _paired_exact_p_value
from .science_s1_benchmark_v13f import _intersection, _radius_about_center
from .science_s1_benchmark_v13j import (
    ALPHA_LEVEL,
    CANDIDATE_COUNT,
    GRID_SPACING_DEGREES,
    SLOPE_NORM,
    TARGET_ERROR,
    TRUE_ANGLES_DEGREES,
    _cone_cover_current_set,
)
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-acquisition-benchmark-v13k"
METHOD_VERSION = "prequential-cone-cover-acquisition-v1"
HORIZONS = (120, 180, 240)
SEEDS = tuple(range(832, 960))
HISTORICAL = "historical_all_grid_current"
NESTED_COVER = "nested_cone_cover"


def _run_path(
    *,
    acquisition: str,
    parameter_angles: Sequence[float],
    true_angle_degrees: float,
    candidates: Sequence[Sequence[float]],
    seed: int,
    horizons: Sequence[int],
    target_error: float,
    alpha_level: float,
) -> dict[str, object]:
    if acquisition not in (HISTORICAL, NESTED_COVER):
        raise ValueError(f"unknown acquisition controller {acquisition}")

    parameters = tuple(_alpha_from_angle(angle) for angle in parameter_angles)
    try:
        true_index = tuple(parameter_angles).index(float(true_angle_degrees))
    except ValueError as error:
        raise ValueError("true angle must lie on the finite parameter grid") from error

    max_observations = max(horizons)
    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    all_grid_log_q = 0.0
    all_grid_current = tuple(range(len(parameters)))
    cover_nested = tuple(range(len(parameters)))
    first_stop: dict[str, object] | None = None
    first_truth_exclusion: int | None = None
    first_nested_empty: int | None = None

    for observation_index in range(1, max_observations + 1):
        acquisition_set = all_grid_current if acquisition == HISTORICAL else cover_nested
        if not acquisition_set:
            break
        features = _select_disagreement_feature(acquisition_set, parameters, candidates)

        # The all-grid mixture is retained only to reproduce the frozen historical
        # acquisition controller. Certification in both arms uses cone-cover only.
        all_grid_probability = _mixture_predictive_probability(
            log_likelihoods,
            parameters,
            features,
        )
        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability
        all_grid_log_q += _observed_log_probability(all_grid_probability, accepted)

        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        all_grid_current = _confidence_indices(
            all_grid_log_q,
            log_likelihoods,
            alpha_level=alpha_level,
        )
        if not all_grid_current:
            raise RuntimeError("historical all-grid current-time confidence set became empty")

        cover_current = _cone_cover_current_set(log_likelihoods, alpha_level=alpha_level)
        cover_nested = _intersection(cover_nested, cover_current)

        if true_index not in cover_nested and first_truth_exclusion is None:
            first_truth_exclusion = observation_index
        if not cover_nested:
            first_nested_empty = observation_index
            break
        if first_stop is not None:
            continue

        center_index = max(range(len(parameters)), key=lambda index: log_likelihoods[index])
        radius = _radius_about_center(center_index, cover_nested, parameters)
        true_error = _directional_error(parameters[center_index], parameters[true_index])
        if radius <= target_error:
            true_in_set = true_index in cover_nested
            first_stop = {
                "observation_count": observation_index,
                "center_angle_degrees": parameter_angles[center_index],
                "certified_radius": radius,
                "confidence_size": len(cover_nested),
                "true_directional_error": true_error,
                "true_in_confidence_set": true_in_set,
                "false_stop": true_error > target_error,
                "geometry_violation": true_error > target_error and true_in_set,
            }

    return {
        "acquisition": acquisition,
        "true_angle_degrees": true_angle_degrees,
        "first_stop": first_stop,
        "first_truth_exclusion_observation": first_truth_exclusion,
        "first_nested_empty_observation": first_nested_empty,
    }


def _summarize(
    paths: Sequence[dict[str, object]],
    *,
    acquisition: str,
    horizon: int,
) -> dict[str, object]:
    selected = [path for path in paths if path["acquisition"] == acquisition]
    stopped: list[dict[str, object]] = []
    false_stops = 0
    geometry_violations = 0
    truth_exclusions = 0
    empty_sets = 0

    for path in selected:
        stop = path["first_stop"]
        if stop is not None:
            record = cast(dict[str, object], stop)
            if cast(int, record["observation_count"]) <= horizon:
                stopped.append(record)
                false_stops += int(bool(record["false_stop"]))
                geometry_violations += int(bool(record["geometry_violation"]))
        exclusion = path["first_truth_exclusion_observation"]
        truth_exclusions += int(exclusion is not None and cast(int, exclusion) <= horizon)
        empty = path["first_nested_empty_observation"]
        empty_sets += int(empty is not None and cast(int, empty) <= horizon)

    observations = [cast(int, record["observation_count"]) for record in stopped]
    return {
        "acquisition": acquisition,
        "horizon": horizon,
        "runs": len(selected),
        "stops": len(stopped),
        "stop_rate": len(stopped) / len(selected),
        "false_stops": false_stops,
        "false_stop_rate": false_stops / len(selected),
        "false_stop_given_stop": false_stops / len(stopped) if stopped else 0.0,
        "geometry_violations": geometry_violations,
        "truth_excluded_ever_rate": truth_exclusions / len(selected),
        "nested_empty_rate": empty_sets / len(selected),
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
    lookup: dict[tuple[float, int], dict[str, dict[str, object]]] = {}
    for path in paths:
        key = (cast(float, path["true_angle_degrees"]), cast(int, path["path_seed"]))
        lookup.setdefault(key, {})[cast(str, path["acquisition"])] = path

    candidate_only = 0
    historical_only = 0
    both = 0
    neither = 0
    earlier_candidate: list[int] = []
    earlier_historical: list[int] = []

    for arms in lookup.values():
        candidate_path = arms[NESTED_COVER]
        historical_path = arms[HISTORICAL]
        candidate_stop = candidate_path["first_stop"]
        historical_stop = historical_path["first_stop"]
        candidate_observation = (
            cast(int, cast(dict[str, object], candidate_stop)["observation_count"])
            if candidate_stop is not None
            else None
        )
        historical_observation = (
            cast(int, cast(dict[str, object], historical_stop)["observation_count"])
            if historical_stop is not None
            else None
        )
        candidate = candidate_observation is not None and candidate_observation <= horizon
        historical = historical_observation is not None and historical_observation <= horizon
        if candidate and historical:
            both += 1
            candidate_count = cast(int, candidate_observation)
            historical_count = cast(int, historical_observation)
            if candidate_count < historical_count:
                earlier_candidate.append(historical_count - candidate_count)
            elif historical_count < candidate_count:
                earlier_historical.append(candidate_count - historical_count)
        elif candidate:
            candidate_only += 1
        elif historical:
            historical_only += 1
        else:
            neither += 1

    return {
        "horizon": horizon,
        "left": NESTED_COVER,
        "right": HISTORICAL,
        "left_only": candidate_only,
        "right_only": historical_only,
        "both": both,
        "neither": neither,
        "paired_exact_p_value": _paired_exact_p_value(candidate_only, historical_only),
        "among_both_candidate_earlier": len(earlier_candidate),
        "among_both_historical_earlier": len(earlier_historical),
        "candidate_earlier_median_gain": (median(earlier_candidate) if earlier_candidate else None),
        "historical_earlier_median_gain": (
            median(earlier_historical) if earlier_historical else None
        ),
    }


def run_benchmark_v13k(
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
            path_seed = 110_000_000 + true_angle_index * 100_000 + seed
            for acquisition in (HISTORICAL, NESTED_COVER):
                path = _run_path(
                    acquisition=acquisition,
                    parameter_angles=parameter_angles,
                    true_angle_degrees=true_angle,
                    candidates=candidates,
                    seed=path_seed,
                    horizons=horizon_values,
                    target_error=target_error,
                    alpha_level=alpha_level,
                )
                path["path_seed"] = path_seed
                paths.append(path)

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Fresh-seed isolation of acquisition policy with the v13j cone-cover numerator, "
            "nested confidence representation, target, grid, likelihood, candidate bank, and "
            "reporting center fixed. Historical acquisition uses the current-time all-grid-mixture "
            "confidence set; the candidate uses the surviving nested cone-cover set."
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
            "numerator": "v13j 11-point outside-cone mixture",
            "confidence_representation": "running intersection / nested cone-cover",
            "reported_center": "global finite-grid maximum-likelihood direction at each time",
            "historical_acquisition": HISTORICAL,
            "candidate_acquisition": NESTED_COVER,
            "primary_endpoints": "paired stop probability at 180 and 240 observations",
        },
        "summaries": [
            _summarize(paths, acquisition=name, horizon=horizon)
            for name in (HISTORICAL, NESTED_COVER)
            for horizon in horizon_values
        ],
        "paired_comparisons": [
            _paired_at_horizon(paths, horizon=horizon) for horizon in horizon_values
        ],
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13k(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
