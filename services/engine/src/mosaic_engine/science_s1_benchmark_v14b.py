from __future__ import annotations

import json
from collections.abc import Sequence
from fractions import Fraction
from time import perf_counter

from .science_s1_benchmark_v14a import (
    _box_grid,
    _random_boxes,
    _reference_cone_log_e,
    _reference_log_likelihood,
    _synthetic_observations,
)
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    ParameterBox,
    _certify_cone_side,
    _cone_halfspaces,
    _log_fraction_upper,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_grouped import (
    _certify_cone_side_grouped,
    grouped_cone_log_e_lower_bound,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-grouped-continuous-runtime-v14b"
METHOD_VERSION = "continuous-grouped-sufficient-statistics-v1"
NODE_BUDGET = 40
MIN_WIDTH = 0.05
VALIDATION_BOX_COUNT = 4
VALIDATION_GRID_SIZE = 3
SCENARIOS = (
    ("aligned_240", (0.15, 1.2, 0.0), 20, 14_301, (1.0, 0.0)),
    ("aligned_480", (0.15, 1.2, 0.0), 40, 14_302, (1.0, 0.0)),
)


def _validate_grouped_bounds(
    observations: Sequence[PrequentialBinaryObservation],
    boxes: Sequence[ParameterBox],
) -> dict[str, object]:
    prepared = prepare_grouped_likelihood(observations)
    likelihood_violations = 0
    cone_lower_violations = 0
    point_count = 0

    for box in boxes:
        bounds = grouped_likelihood_bounds(box, prepared)
        cone_lower = grouped_cone_log_e_lower_bound(box, prepared)
        for theta in _box_grid(box, grid_size=VALIDATION_GRID_SIZE):
            point_count += 1
            direct_likelihood = _reference_log_likelihood(theta, observations)
            direct_cone = _reference_cone_log_e(theta, observations)
            likelihood_violations += int(
                not bounds.lower <= direct_likelihood <= bounds.upper
            )
            cone_lower_violations += int(cone_lower > direct_cone)

    return {
        "boxes": len(boxes),
        "grid_size": VALIDATION_GRID_SIZE,
        "point_count": point_count,
        "unique_feature_groups": len(prepared.groups),
        "observation_count": prepared.observation_count,
        "likelihood_enclosure_violations": likelihood_violations,
        "cone_lower_bound_violations": cone_lower_violations,
    }


def _time_certificate_side(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    initial_box: ParameterBox,
    halfspace: Sequence[Fraction],
    common_cutoff_lower: object,
    cone_log_threshold_upper: object,
    grouped: bool,
) -> dict[str, object]:
    if grouped:
        prepared = prepare_grouped_likelihood(observations)
        start = perf_counter()
        result = _certify_cone_side_grouped(
            initial_box,
            prepared,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            max_nodes=NODE_BUDGET,
            min_width=MIN_WIDTH,
        )
        elapsed = perf_counter() - start
    else:
        start = perf_counter()
        result = _certify_cone_side(
            initial_box,
            observations,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            max_nodes=NODE_BUDGET,
            min_width=MIN_WIDTH,
        )
        elapsed = perf_counter() - start

    return {
        "elapsed_seconds": elapsed,
        "certified": result.certified,
        "nodes_visited": result.nodes_visited,
        "unresolved_boxes": result.unresolved_boxes,
        "reason": result.reason,
    }


def _run_runtime_scenario(
    name: str,
    alpha: Sequence[float],
    repeats: int,
    seed: int,
    center: Sequence[float],
) -> dict[str, object]:
    observations = _synthetic_observations(alpha=alpha, repeats=repeats, seed=seed)
    common_cutoff = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    initial_box = initial_nuisance_box(
        observations,
        common_cutoff_lower=common_cutoff,
    )
    if initial_box is None:
        raise AssertionError(f"{name} did not produce a finite nuisance box")
    cone_threshold = _log_fraction_upper(1 / CONE_ALPHA)
    halfspaces = _cone_halfspaces(center, target_error=0.15)

    raw_total = 0.0
    grouped_total = 0.0
    sides: list[dict[str, object]] = []
    for side_index, halfspace in enumerate(halfspaces):
        raw = _time_certificate_side(
            observations,
            initial_box=initial_box,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff,
            cone_log_threshold_upper=cone_threshold,
            grouped=False,
        )
        grouped = _time_certificate_side(
            observations,
            initial_box=initial_box,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff,
            cone_log_threshold_upper=cone_threshold,
            grouped=True,
        )
        raw_total += float(raw["elapsed_seconds"])
        grouped_total += float(grouped["elapsed_seconds"])
        sides.append({"side": side_index, "raw": raw, "grouped": grouped})

    return {
        "scenario": name,
        "observation_count": len(observations),
        "unique_feature_groups": len(prepare_grouped_likelihood(observations).groups),
        "raw_elapsed_seconds": raw_total,
        "grouped_elapsed_seconds": grouped_total,
        "speedup": raw_total / grouped_total if grouped_total > 0.0 else None,
        "sides": sides,
    }


def run_benchmark_v14b(*, include_runtime: bool = True) -> dict[str, object]:
    validation_observations = _synthetic_observations(
        alpha=(0.2, 0.9, -0.35),
        repeats=8,
        seed=14_300,
    )
    validation_boxes = _random_boxes(count=VALIDATION_BOX_COUNT, seed=14_399)
    validation = _validate_grouped_bounds(validation_observations, validation_boxes)
    if validation["likelihood_enclosure_violations"] != 0:
        raise AssertionError("grouped likelihood enclosure violation")
    if validation["cone_lower_bound_violations"] != 0:
        raise AssertionError("grouped cone lower-bound violation")

    runtime_scenarios = (
        [
            _run_runtime_scenario(name, alpha, repeats, seed, center)
            for name, alpha, repeats, seed, center in SCENARIOS
        ]
        if include_runtime
        else []
    )
    raw_total = sum(float(item["raw_elapsed_seconds"]) for item in runtime_scenarios)
    grouped_total = sum(float(item["grouped_elapsed_seconds"]) for item in runtime_scenarios)

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Safety-preserving sufficient-statistic regrouping of the validated v14a interval "
            "likelihood calculation. The runtime comparison changes only evaluation strategy; "
            "precision, alpha split, cone, node budget, branch order, and pruning rules are fixed."
        ),
        "config": {
            "node_budget_per_side": NODE_BUDGET,
            "min_width": MIN_WIDTH,
            "validation_box_count": VALIDATION_BOX_COUNT,
            "validation_grid_size": VALIDATION_GRID_SIZE,
            "include_runtime": include_runtime,
        },
        "grouped_bound_validation": validation,
        "runtime_scenarios": runtime_scenarios,
        "runtime_total": {
            "raw_seconds": raw_total,
            "grouped_seconds": grouped_total,
            "speedup": raw_total / grouped_total if grouped_total > 0.0 else None,
        },
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14b(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
