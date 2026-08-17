from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from random import Random
from statistics import mean, median
from typing import cast

from .science_s1 import acceptance_probability
from .science_s1_benchmark_v12a import (
    CANDIDATE_COUNT,
    FEATURE_DIMENSIONS,
    HELDOUT_COUNT,
    INTERCEPT,
    MODEL_VERSION,
    PAIR_SCHEDULE_VERSION,
    POSTERIOR_QUANTILE,
    POSTERIOR_SAMPLES,
    PRIOR_VARIANCE,
    QUERY_DESIGN_VERSION,
    SLOPE_NORMS,
    TARGET_ERRORS,
    _population_ordering_error,
    _response_seed,
    _risk_seed,
    _scenario_seed,
    _schedule_seed,
)
from .science_s1_benchmark_v12c import (
    PRIMARY_AGGREGATE_WILSON_UPPER_GATE,
    STRONG_SIGNAL_STOP_GATES,
    SUBGROUP_FALSE_STOP_GATE,
    SUBGROUP_MIN_STOPS,
    _quantile,
    _wilson_interval,
)
from .science_s1_controlled_design import centered_orthogonalized_candidate_bank
from .science_s1_directional_theory import normalize_effective_slope
from .science_s1_passive_design import balanced_round_robin_pair_schedule
from .science_s1_simulation import BinaryObservation, fit_logistic_laplace, make_gaussian_scenario
from .science_s1_stopping import (
    posterior_directional_risk,
    posterior_transverse_debiased_directional_risk,
    posterior_transverse_signal,
    posterior_transverse_tangent_directional_risk,
)

BENCHMARK_VERSION = "s1-tangent-stopping-benchmark-v12e"
STOPPING_VERSION = "laplace-transverse-tangent-angular-v5"
SEEDS = tuple(range(448, 576))
RULES = (
    "raw_two_consecutive",
    "transverse_full_noise_two_consecutive",
    "tangent_single",
    "tangent_two_consecutive",
)
PRIMARY_RULE = "tangent_two_consecutive"


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
        round_pairs = schedule[round_index * pairs_per_round : (round_index + 1) * pairs_per_round]
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
        risk_seed = _risk_seed(feature_dimension, seed, round_index)
        raw_risk = posterior_directional_risk(
            posterior,
            quantile=posterior_quantile,
            sample_count=posterior_samples,
            seed=risk_seed,
        )
        transverse_signal = posterior_transverse_signal(posterior)
        full_noise_risk = posterior_transverse_debiased_directional_risk(
            posterior,
            quantile=posterior_quantile,
            sample_count=posterior_samples,
            seed=risk_seed,
        )
        tangent_risk = posterior_transverse_tangent_directional_risk(
            posterior,
            quantile=posterior_quantile,
            sample_count=posterior_samples,
            seed=risk_seed,
        )
        query_count = (round_index + 1) * pairs_per_round
        checkpoints.append(
            {
                "round_index": round_index + 1,
                "query_count": query_count,
                "binary_observation_count": 2 * query_count,
                "raw_directional_risk": asdict(raw_risk),
                "transverse_full_noise_directional_risk": asdict(full_noise_risk),
                "tangent_directional_risk": asdict(tangent_risk),
                "posterior_transverse_signal": asdict(transverse_signal),
                "true_population_ordering_error": _population_ordering_error(
                    true_alpha,
                    posterior.mean,
                ),
                "converged": posterior.converged,
                "iterations": posterior.iterations,
            }
        )

    return checkpoints


def _risk_key(rule: str) -> str:
    if rule == "raw_two_consecutive":
        return "raw_directional_risk"
    if rule == "transverse_full_noise_two_consecutive":
        return "transverse_full_noise_directional_risk"
    if rule in {"tangent_single", "tangent_two_consecutive"}:
        return "tangent_directional_risk"
    raise ValueError(f"unknown rule: {rule}")


def _required_streak(rule: str) -> int:
    if rule == "tangent_single":
        return 1
    if rule in {
        "raw_two_consecutive",
        "transverse_full_noise_two_consecutive",
        "tangent_two_consecutive",
    }:
        return 2
    raise ValueError(f"unknown rule: {rule}")


def _risk_upper(checkpoint: dict[str, object], rule: str) -> float:
    risk = cast(dict[str, object], checkpoint[_risk_key(rule)])
    return float(cast(float, risk["upper_error"]))


def _first_stop(
    checkpoints: Sequence[dict[str, object]],
    *,
    target_error: float,
    rule: str,
) -> dict[str, object] | None:
    streak = 0
    required = _required_streak(rule)
    for checkpoint in checkpoints:
        if _risk_upper(checkpoint, rule) <= target_error:
            streak += 1
            if streak >= required:
                return checkpoint
        else:
            streak = 0
    return None


def _summarize_rule(
    paths: Sequence[dict[str, object]],
    *,
    target_error: float,
    rule: str,
) -> dict[str, object]:
    outcomes: list[dict[str, object]] = []
    for path in paths:
        checkpoints = cast(list[dict[str, object]], path["checkpoints"])
        stop = _first_stop(checkpoints, target_error=target_error, rule=rule)
        final_error = float(cast(float, checkpoints[-1]["true_population_ordering_error"]))

        if stop is None:
            outcomes.append(
                {
                    "seed": path["seed"],
                    "stopped": False,
                    "false_stop": False,
                    "missed_stop_at_cap": final_error <= target_error,
                    "query_count": None,
                    "true_error_at_decision": final_error,
                    "transverse_retained_fraction": None,
                }
            )
            continue

        true_error = float(cast(float, stop["true_population_ordering_error"]))
        signal = cast(dict[str, object], stop["posterior_transverse_signal"])
        outcomes.append(
            {
                "seed": path["seed"],
                "stopped": True,
                "false_stop": true_error > target_error,
                "missed_stop_at_cap": False,
                "query_count": int(cast(int, stop["query_count"])),
                "true_error_at_decision": true_error,
                "transverse_retained_fraction": float(cast(float, signal["retained_fraction"])),
            }
        )

    stopped = [outcome for outcome in outcomes if outcome["stopped"]]
    false_stops = [outcome for outcome in stopped if outcome["false_stop"]]
    missed = [outcome for outcome in outcomes if outcome["missed_stop_at_cap"]]
    query_counts = [cast(int, outcome["query_count"]) for outcome in stopped]
    stopped_errors = [cast(float, outcome["true_error_at_decision"]) for outcome in stopped]
    retained = [cast(float, outcome["transverse_retained_fraction"]) for outcome in stopped]
    false_interval = _wilson_interval(len(false_stops), len(stopped))

    return {
        "rule": rule,
        "target_error": target_error,
        "runs": len(outcomes),
        "stops": len(stopped),
        "false_stops": len(false_stops),
        "stop_rate": len(stopped) / len(outcomes),
        "false_stop_rate": len(false_stops) / len(outcomes),
        "false_stop_given_stop": (len(false_stops) / len(stopped)) if stopped else 0.0,
        "false_stop_given_stop_wilson95": {
            "lower": false_interval[0],
            "upper": false_interval[1],
        },
        "missed_stop_at_cap_rate": len(missed) / len(outcomes),
        "stopping_query_count": {
            "mean": mean(query_counts) if query_counts else None,
            "median": median(query_counts) if query_counts else None,
            "p90": _quantile(query_counts, 0.90) if query_counts else None,
        },
        "true_error_given_stop": {
            "mean": mean(stopped_errors) if stopped_errors else None,
            "p90": _quantile(stopped_errors, 0.90) if stopped_errors else None,
            "max": max(stopped_errors) if stopped_errors else None,
        },
        "transverse_retained_fraction_given_stop": {
            "mean": mean(retained) if retained else None,
            "median": median(retained) if retained else None,
            "p10": _quantile(retained, 0.10) if retained else None,
        },
        "outcomes": outcomes,
    }


def _fixed_checkpoint_diagnostics(
    paths: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    first = cast(list[dict[str, object]], paths[0]["checkpoints"])
    summaries: list[dict[str, object]] = []
    for index, first_checkpoint in enumerate(first):
        raw_covered = 0
        full_noise_covered = 0
        tangent_covered = 0
        retained: list[float] = []
        for path in paths:
            checkpoints = cast(list[dict[str, object]], path["checkpoints"])
            checkpoint = checkpoints[index]
            truth = float(cast(float, checkpoint["true_population_ordering_error"]))
            raw = cast(dict[str, object], checkpoint["raw_directional_risk"])
            full_noise = cast(
                dict[str, object],
                checkpoint["transverse_full_noise_directional_risk"],
            )
            tangent = cast(dict[str, object], checkpoint["tangent_directional_risk"])
            signal = cast(dict[str, object], checkpoint["posterior_transverse_signal"])
            raw_covered += truth <= float(cast(float, raw["upper_error"]))
            full_noise_covered += truth <= float(cast(float, full_noise["upper_error"]))
            tangent_covered += truth <= float(cast(float, tangent["upper_error"]))
            retained.append(float(cast(float, signal["retained_fraction"])))
        summaries.append(
            {
                "round_index": int(cast(int, first_checkpoint["round_index"])),
                "query_count": int(cast(int, first_checkpoint["query_count"])),
                "raw_q95_coverage": raw_covered / len(paths),
                "transverse_full_noise_q95_coverage": full_noise_covered / len(paths),
                "tangent_q95_coverage": tangent_covered / len(paths),
                "mean_transverse_retained_fraction": mean(retained),
            }
        )
    return summaries


def _evaluate_primary_gate(
    cells: Sequence[dict[str, object]],
    aggregate: Sequence[dict[str, object]],
) -> dict[str, object]:
    primary_aggregate = [summary for summary in aggregate if summary["rule"] == PRIMARY_RULE]
    aggregate_safe = all(
        float(
            cast(
                float,
                cast(
                    dict[str, object],
                    summary["false_stop_given_stop_wilson95"],
                )["upper"],
            )
        )
        <= PRIMARY_AGGREGATE_WILSON_UPPER_GATE
        for summary in primary_aggregate
    )

    sampled_subgroups = 0
    subgroup_safe = True
    strong_signal_safe = True
    for cell in cells:
        signal = float(cast(float, cell["slope_norm"]))
        summaries = cast(list[dict[str, object]], cell["rule_summaries"])
        for summary in summaries:
            if summary["rule"] != PRIMARY_RULE:
                continue
            stops = int(cast(int, summary["stops"]))
            target = float(cast(float, summary["target_error"]))
            if stops >= SUBGROUP_MIN_STOPS:
                sampled_subgroups += 1
                subgroup_safe = subgroup_safe and (
                    float(cast(float, summary["false_stop_given_stop"])) <= SUBGROUP_FALSE_STOP_GATE
                )
            if signal == 1.5:
                strong_signal_safe = strong_signal_safe and (
                    float(cast(float, summary["stop_rate"])) >= STRONG_SIGNAL_STOP_GATES[target]
                )

    return {
        "primary_rule": PRIMARY_RULE,
        "aggregate_wilson_upper_gate": PRIMARY_AGGREGATE_WILSON_UPPER_GATE,
        "aggregate_safe": aggregate_safe,
        "subgroup_min_stops": SUBGROUP_MIN_STOPS,
        "subgroup_false_stop_gate": SUBGROUP_FALSE_STOP_GATE,
        "sampled_subgroups": sampled_subgroups,
        "subgroup_safe": subgroup_safe,
        "strong_signal_stop_gates": STRONG_SIGNAL_STOP_GATES,
        "strong_signal_safe": strong_signal_safe,
        "overall_pass": aggregate_safe and subgroup_safe and strong_signal_safe,
    }


def run_benchmark_v12e(
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
    if not seed_values or any(seed < 448 for seed in seed_values):
        raise ValueError("v12e seeds must be disjoint from v12a-v12d seeds 0-447")
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

            rule_summaries = [
                _summarize_rule(
                    condition_paths,
                    target_error=target,
                    rule=rule,
                )
                for target in targets
                for rule in RULES
            ]
            cells.append(
                {
                    "feature_dimension": feature_dimension,
                    "slope_norm": slope_norm,
                    "runs": len(condition_paths),
                    "rule_summaries": rule_summaries,
                    "fixed_checkpoint_diagnostics": _fixed_checkpoint_diagnostics(condition_paths),
                }
            )

    aggregate = [
        _summarize_rule(paths, target_error=target, rule=rule)
        for target in targets
        for rule in RULES
    ]
    primary_gate = _evaluate_primary_gate(cells, aggregate)

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "model_version": MODEL_VERSION,
        "query_design_version": QUERY_DESIGN_VERSION,
        "pair_schedule_version": PAIR_SCHEDULE_VERSION,
        "stopping_version": STOPPING_VERSION,
        "scientific_scope": (
            "Prospective fresh-seed test of tangent-space posterior angular uncertainty for "
            "S1 directional stopping. Posterior slope perturbations are projected orthogonal "
            "to the fitted ranking direction before conversion to angular error, while the "
            "v12d transverse-debiased signal norm is retained. Synthetic truth is used only "
            "for operating-characteristic scoring. This is not human or matchmaking validation."
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
            "rules": RULES,
            "primary_rule": PRIMARY_RULE,
            "fresh_seed_requirement": "all seeds >=448; v12a-v12d used 0-447",
            "common_random_numbers_across_signal_levels": True,
            "tangent_projection": "delta_perp=(I-u u^T) delta",
            "tangent_angle": "atan2(||delta_perp||, B_perp_db)/pi",
        },
        "primary_gate": primary_gate,
        "aggregate_rule_summaries": aggregate,
        "cells": cells,
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v12e(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
