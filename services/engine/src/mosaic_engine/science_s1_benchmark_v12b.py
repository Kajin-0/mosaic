from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from math import sqrt
from statistics import mean, median
from typing import cast

from .science_s1_benchmark_v12a import (
    CANDIDATE_COUNT,
    FEATURE_DIMENSIONS,
    INTERCEPT,
    POSTERIOR_QUANTILE,
    POSTERIOR_SAMPLES,
    PRIOR_VARIANCE,
    SLOPE_NORMS,
    TARGET_ERRORS,
    _run_path,
)

BENCHMARK_VERSION = "s1-stopping-validation-benchmark-v12b"
STOPPING_VERSION = "laplace-angular-sequential-rules-v2"
SEEDS = tuple(range(64, 192))
RULES = ("single_crossing", "two_consecutive", "burnin_90")


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


def _wilson_interval(
    successes: int,
    trials: int,
    *,
    z: float = 1.959963984540054,
) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 1.0)
    if successes < 0 or successes > trials:
        raise ValueError("successes must lie between zero and trials")
    proportion = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = (proportion + z2 / (2.0 * trials)) / denominator
    half_width = (
        z
        * sqrt(proportion * (1.0 - proportion) / trials + z2 / (4.0 * trials * trials))
        / denominator
    )
    return (max(0.0, center - half_width), min(1.0, center + half_width))


def _posterior_upper(checkpoint: dict[str, object]) -> float:
    risk = cast(dict[str, object], checkpoint["posterior_directional_risk"])
    return float(cast(float, risk["upper_error"]))


def _first_stop(
    checkpoints: Sequence[dict[str, object]],
    *,
    target_error: float,
    rule: str,
) -> dict[str, object] | None:
    if rule not in RULES:
        raise ValueError(f"unknown rule: {rule}")

    if rule == "single_crossing":
        return next(
            (
                checkpoint
                for checkpoint in checkpoints
                if _posterior_upper(checkpoint) <= target_error
            ),
            None,
        )

    if rule == "burnin_90":
        return next(
            (
                checkpoint
                for checkpoint in checkpoints
                if int(cast(int, checkpoint["query_count"])) >= 90
                and _posterior_upper(checkpoint) <= target_error
            ),
            None,
        )

    streak = 0
    for checkpoint in checkpoints:
        if _posterior_upper(checkpoint) <= target_error:
            streak += 1
            if streak >= 2:
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
                }
            )
            continue

        true_error = float(cast(float, stop["true_population_ordering_error"]))
        outcomes.append(
            {
                "seed": path["seed"],
                "stopped": True,
                "false_stop": true_error > target_error,
                "missed_stop_at_cap": False,
                "query_count": int(cast(int, stop["query_count"])),
                "true_error_at_decision": true_error,
            }
        )

    stopped = [outcome for outcome in outcomes if outcome["stopped"]]
    false_stops = [outcome for outcome in stopped if outcome["false_stop"]]
    missed = [outcome for outcome in outcomes if outcome["missed_stop_at_cap"]]
    query_counts = [cast(int, outcome["query_count"]) for outcome in stopped]
    stopped_errors = [cast(float, outcome["true_error_at_decision"]) for outcome in stopped]
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
        "outcomes": outcomes,
    }


def _fixed_checkpoint_coverage(
    paths: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    first_path = cast(list[dict[str, object]], paths[0]["checkpoints"])
    summaries: list[dict[str, object]] = []
    for index, first_checkpoint in enumerate(first_path):
        covered = 0
        gaps: list[float] = []
        for path in paths:
            checkpoints = cast(list[dict[str, object]], path["checkpoints"])
            checkpoint = checkpoints[index]
            upper = _posterior_upper(checkpoint)
            truth = float(cast(float, checkpoint["true_population_ordering_error"]))
            covered += truth <= upper
            gaps.append(upper - truth)
        summaries.append(
            {
                "round_index": int(cast(int, first_checkpoint["round_index"])),
                "query_count": int(cast(int, first_checkpoint["query_count"])),
                "coverage": covered / len(paths),
                "mean_upper_minus_truth": mean(gaps),
            }
        )
    return summaries


def run_benchmark_v12b(
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

    if not seed_values or any(seed < 64 for seed in seed_values):
        raise ValueError("v12b seeds must be fresh and disjoint from v12a seeds 0-63")

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
                    "fixed_checkpoint_coverage": _fixed_checkpoint_coverage(condition_paths),
                }
            )

    aggregate: list[dict[str, object]] = []
    for target in targets:
        for rule in RULES:
            rule_paths: list[dict[str, object]] = []
            for cell in cells:
                feature_dimension = int(cast(int, cell["feature_dimension"]))
                slope_norm = float(cast(float, cell["slope_norm"]))
                rule_paths.extend(
                    path
                    for path in paths
                    if int(cast(int, path["feature_dimension"])) == feature_dimension
                    and float(cast(float, path["slope_norm"])) == slope_norm
                )
            aggregate.append(_summarize_rule(rule_paths, target_error=target, rule=rule))

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "stopping_version": STOPPING_VERSION,
        "scientific_scope": (
            "Prospective fresh-seed validation of three prespecified posterior-observable "
            "sequential stopping rules identified before v12b execution. Seeds are disjoint "
            "from v12a. Synthetic truth is used only for operating-characteristic evaluation. "
            "This is not human or matchmaking validation."
        ),
        "config": {
            "feature_dimensions": dimensions,
            "slope_norms": signals,
            "target_errors": targets,
            "seeds": seed_values,
            "candidate_count": candidate_count,
            "prior_variance": prior_variance,
            "intercept": intercept,
            "posterior_quantile": posterior_quantile,
            "posterior_samples": posterior_samples,
            "rules": RULES,
            "primary_safety_metric": "false_stop_given_stop",
            "primary_point_estimate_gate": 0.05,
            "fresh_seed_requirement": "all seeds >=64; v12a used 0-63",
        },
        "aggregate_rule_summaries": aggregate,
        "cells": cells,
        "paths": paths,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v12b(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
