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
from .science_s1_eprocess import binary_log_probability

BENCHMARK_VERSION = "s1-numerator-efficiency-benchmark-v13d"
METHOD_VERSION = "prequential-finite-confidence-radius-v1"
GRID_SPACING_DEGREES = 5.0
TRUE_ANGLES_DEGREES = tuple(float(value) for value in range(0, 360, 30))
HORIZONS = (120, 180, 240)
TARGET_ERROR = 0.15
SLOPE_NORM = 0.9
CANDIDATE_COUNT = 12
ALPHA_LEVEL = 0.05
SEEDS = tuple(range(64, 192))
OPERATIONAL_PREDICTORS = (
    "mixture_all",
    "mle_face",
    "snml",
    "confidence_mixture",
)
ORACLE_PREDICTOR = "oracle_true"


def _likelihood_weighted_probability(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
    indices: Sequence[int],
) -> float:
    if not indices:
        raise ValueError("indices must not be empty")
    maximum = max(float(log_likelihoods[index]) for index in indices)
    raw_weights = tuple(exp(float(log_likelihoods[index]) - maximum) for index in indices)
    total = sum(raw_weights)
    return sum(
        weight * acceptance_probability(parameters[index], features)
        for weight, index in zip(raw_weights, indices, strict=True)
    ) / total


def _mle_face_predictive_probability(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
) -> float:
    if not log_likelihoods:
        raise ValueError("log_likelihoods must not be empty")
    maximum = max(float(value) for value in log_likelihoods)
    maximizers = tuple(
        index
        for index, value in enumerate(log_likelihoods)
        if abs(float(value) - maximum) <= 1e-12
    )
    return sum(acceptance_probability(parameters[index], features) for index in maximizers) / len(
        maximizers
    )


def _logsumexp_pair(left: float, right: float) -> float:
    maximum = max(left, right)
    return maximum + log(exp(left - maximum) + exp(right - maximum))


def _snml_predictive_probability(
    log_likelihoods: Sequence[float],
    parameters: Sequence[Sequence[float]],
    features: Sequence[float],
) -> float:
    if len(log_likelihoods) != len(parameters):
        raise ValueError("likelihood and parameter dimensions must agree")
    score_one = max(
        float(log_likelihood) + binary_log_probability(parameter, features, True)
        for log_likelihood, parameter in zip(log_likelihoods, parameters, strict=True)
    )
    score_zero = max(
        float(log_likelihood) + binary_log_probability(parameter, features, False)
        for log_likelihood, parameter in zip(log_likelihoods, parameters, strict=True)
    )
    normalizer = _logsumexp_pair(score_one, score_zero)
    return exp(score_one - normalizer)


def _confidence_radius(
    center_index: int,
    confidence_indices: Sequence[int],
    parameters: Sequence[Sequence[float]],
) -> float:
    return max(
        _directional_error(parameters[center_index], parameters[index])
        for index in confidence_indices
    )


def _run_common_path(
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
        raise ValueError("true angle must lie exactly on the finite parameter grid") from error

    predictor_names = OPERATIONAL_PREDICTORS + (ORACLE_PREDICTOR,)
    max_observations = max(horizons)
    random = Random(seed)
    log_likelihoods = [0.0] * len(parameters)
    log_predictive_joint = {name: 0.0 for name in predictor_names}
    confidence_sets = {name: tuple(range(len(parameters))) for name in predictor_names}
    first_stop: dict[str, dict[str, object] | None] = {name: None for name in predictor_names}
    first_exclusion: dict[str, int | None] = {name: None for name in predictor_names}
    log_q_at_horizon: dict[str, dict[str, float]] = {name: {} for name in predictor_names}

    for observation_index in range(1, max_observations + 1):
        # Keep the observed data path identical across numerator variants. The existing
        # all-grid mixture confidence set is the fixed design controller. This makes v13d
        # a numerator comparison rather than a simultaneous query-policy comparison.
        controller_confidence = confidence_sets["mixture_all"]
        features = _select_disagreement_feature(controller_confidence, parameters, candidates)

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
            "confidence_mixture": _likelihood_weighted_probability(
                log_likelihoods,
                parameters,
                features,
                confidence_sets["confidence_mixture"],
            ),
            # Synthetic-truth diagnostic only. This is not an operational predictor and
            # must never be used to select a production confidence rule.
            ORACLE_PREDICTOR: acceptance_probability(parameters[true_index], features),
        }

        true_probability = acceptance_probability(parameters[true_index], features)
        accepted = random.random() < true_probability

        for name in predictor_names:
            log_predictive_joint[name] += _observed_log_probability(
                predictive_probability[name],
                accepted,
            )

        for index, parameter in enumerate(parameters):
            log_likelihoods[index] += binary_log_probability(parameter, features, accepted)

        for name in predictor_names:
            confidence_indices = _confidence_indices(
                log_predictive_joint[name],
                log_likelihoods,
                alpha_level=alpha_level,
            )
            if not confidence_indices:
                raise RuntimeError(f"{name} finite e-process confidence set became empty")
            confidence_sets[name] = confidence_indices

            if true_index not in confidence_indices and first_exclusion[name] is None:
                first_exclusion[name] = observation_index

            center_index = max(confidence_indices, key=lambda index: log_likelihoods[index])
            radius = _confidence_radius(center_index, confidence_indices, parameters)
            true_error = _directional_error(parameters[center_index], parameters[true_index])
            if first_stop[name] is None and radius <= target_error:
                first_stop[name] = {
                    "observation_count": observation_index,
                    "center_angle_degrees": parameter_angles[center_index],
                    "certified_radius": radius,
                    "confidence_size": len(confidence_indices),
                    "true_directional_error": true_error,
                    "true_in_confidence_set": true_index in confidence_indices,
                    "false_stop": true_error > target_error,
                }

        if observation_index in horizons:
            key = str(observation_index)
            for name in predictor_names:
                log_q_at_horizon[name][key] = log_predictive_joint[name]

    return {
        "true_angle_degrees": true_angle_degrees,
        "first_stop": first_stop,
        "first_exclusion_observation": first_exclusion,
        "log_q_at_horizon": log_q_at_horizon,
    }


def _summarize_predictor(
    paths: Sequence[dict[str, object]],
    *,
    predictor_name: str,
    horizon: int,
) -> dict[str, object]:
    stopped: list[dict[str, object]] = []
    false_stops: list[dict[str, object]] = []
    excluded = 0
    predictor_log_q: list[float] = []
    oracle_log_q: list[float] = []

    for path in paths:
        stop_by_name = cast(dict[str, object], path["first_stop"])
        stop = stop_by_name[predictor_name]
        if stop is not None:
            stop_record = cast(dict[str, object], stop)
            if cast(int, stop_record["observation_count"]) <= horizon:
                stopped.append(stop_record)
                if bool(stop_record["false_stop"]):
                    false_stops.append(stop_record)

        exclusion_by_name = cast(dict[str, object], path["first_exclusion_observation"])
        exclusion = exclusion_by_name[predictor_name]
        if exclusion is not None and cast(int, exclusion) <= horizon:
            excluded += 1

        log_q_by_name = cast(dict[str, object], path["log_q_at_horizon"])
        predictor_log_q.append(
            float(cast(dict[str, float], log_q_by_name[predictor_name])[str(horizon)])
        )
        oracle_log_q.append(
            float(cast(dict[str, float], log_q_by_name[ORACLE_PREDICTOR])[str(horizon)])
        )

    stopping_observations = [cast(int, stop["observation_count"]) for stop in stopped]
    regrets = [
        oracle - predictor
        for oracle, predictor in zip(oracle_log_q, predictor_log_q, strict=True)
    ]
    return {
        "predictor": predictor_name,
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
        "predictive_regret_vs_oracle": {
            "mean_log_loss_excess": mean(regrets),
            "median_log_loss_excess": median(regrets),
        },
    }


def run_benchmark_v13d(
    *,
    seeds: Iterable[int] = SEEDS,
    true_angles_degrees: Iterable[float] = TRUE_ANGLES_DEGREES,
    horizons: Iterable[int] = HORIZONS,
    target_error: float = TARGET_ERROR,
    candidate_count: int = CANDIDATE_COUNT,
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
        raise ValueError("horizons must contain positive integers")
    if target_error <= 0.0 or target_error >= 0.5:
        raise ValueError("target_error must lie strictly between zero and 0.5")
    if alpha_level <= 0.0 or alpha_level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")

    parameter_angles = _parameter_angles(GRID_SPACING_DEGREES)
    missing = [angle for angle in true_angles if angle not in parameter_angles]
    if missing:
        raise ValueError(f"all true angles must lie on the finite grid; missing {missing}")

    candidates = _candidate_bank(candidate_count)
    paths: list[dict[str, object]] = []
    for true_angle_index, true_angle in enumerate(true_angles):
        for seed in seed_values:
            paths.append(
                _run_common_path(
                    parameter_angles=parameter_angles,
                    true_angle_degrees=true_angle,
                    candidates=candidates,
                    seed=60_000_000 + true_angle_index * 100_000 + seed,
                    horizons=horizon_values,
                    target_error=target_error,
                    alpha_level=alpha_level,
                )
            )

    predictor_names = OPERATIONAL_PREDICTORS + (ORACLE_PREDICTOR,)
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Common-path finite-grid decomposition of prequential numerator efficiency. "
            "The likelihood, 5-degree parameter grid, true directions, candidate bank, "
            "target, alpha, and adaptive disagreement design controller are fixed. Every "
            "numerator is evaluated on the same query/response path. Operational predictors "
            "are normalized and predictable before the current outcome. The oracle predictor "
            "uses synthetic truth only as a non-operational efficiency ceiling."
        ),
        "config": {
            "grid_spacing_degrees": GRID_SPACING_DEGREES,
            "parameter_count": len(parameter_angles),
            "true_angles_degrees": true_angles,
            "horizons": horizon_values,
            "seeds": seed_values,
            "target_error": target_error,
            "target_degrees": target_error * 180.0,
            "slope_norm": SLOPE_NORM,
            "candidate_count": candidate_count,
            "alpha_level": alpha_level,
            "operational_predictors": OPERATIONAL_PREDICTORS,
            "oracle_predictor": ORACLE_PREDICTOR,
            "query_design_controller": (
                "all-grid likelihood-mixture confidence set with probability-range disagreement"
            ),
            "stopping_rule": (
                "exact finite-grid confidence radius around the retained maximum-likelihood "
                "direction is at most target"
            ),
        },
        "predictor_summaries": [
            _summarize_predictor(paths, predictor_name=name, horizon=horizon)
            for name in predictor_names
            for horizon in horizon_values
        ],
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v13d(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
