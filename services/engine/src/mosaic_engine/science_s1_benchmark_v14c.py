from __future__ import annotations

import json
from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction
from statistics import median
from time import perf_counter
from typing import cast

from .science_s1_benchmark_v14a import (
    _box_grid,
    _random_boxes,
    _reference_cone_log_e,
    _synthetic_observations,
)
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    ParameterBox,
    _cone_halfspaces,
    _log_fraction_upper,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_coupled import (
    _certify_cone_side_coupled,
    grouped_coupled_cone_log_e_lower_bound,
)
from .science_s1_continuous_geometry_grouped import (
    _certify_cone_side_grouped,
    grouped_cone_log_e_lower_bound,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-coupled-continuous-bound-v14c"
METHOD_VERSION = "continuous-coupled-log-ratio-bnb-v1"
VALIDATION_BOX_COUNT = 6
VALIDATION_GRID_SIZE = 3
NODE_BUDGET = 250
MIN_WIDTH = 0.05
SCENARIOS = (
    ("aligned_240", (0.15, 1.2, 0.0), 20, 14_601, (1.0, 0.0)),
    ("aligned_480", (0.15, 1.2, 0.0), 40, 14_602, (1.0, 0.0)),
)


def _validate_coupled_bounds(
    observations: Sequence[PrequentialBinaryObservation],
    boxes: Sequence[ParameterBox],
) -> dict[str, object]:
    prepared = prepare_grouped_likelihood(observations)
    old_violations = 0
    coupled_violations = 0
    point_count = 0
    old_slacks: list[Decimal] = []
    coupled_slacks: list[Decimal] = []
    bound_improvements: list[Decimal] = []

    for box in boxes:
        old_lower = grouped_cone_log_e_lower_bound(box, prepared)
        coupled_lower = grouped_coupled_cone_log_e_lower_bound(box, prepared)
        bound_improvements.append(coupled_lower - old_lower)
        for theta in _box_grid(box, grid_size=VALIDATION_GRID_SIZE):
            point_count += 1
            direct = _reference_cone_log_e(theta, observations)
            old_slack = direct - old_lower
            coupled_slack = direct - coupled_lower
            old_slacks.append(old_slack)
            coupled_slacks.append(coupled_slack)
            old_violations += int(old_slack < 0)
            coupled_violations += int(coupled_slack < 0)

    return {
        "boxes": len(boxes),
        "grid_size": VALIDATION_GRID_SIZE,
        "point_count": point_count,
        "unique_feature_groups": len(prepared.groups),
        "old_bound_violations": old_violations,
        "coupled_bound_violations": coupled_violations,
        "old_minimum_slack": str(min(old_slacks)),
        "coupled_minimum_slack": str(min(coupled_slacks)),
        "old_median_slack": str(median(old_slacks)),
        "coupled_median_slack": str(median(coupled_slacks)),
        "minimum_box_bound_improvement": str(min(bound_improvements)),
        "median_box_bound_improvement": str(median(bound_improvements)),
        "maximum_box_bound_improvement": str(max(bound_improvements)),
    }


def _time_side(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    box: ParameterBox,
    halfspace: Sequence[Fraction],
    common_cutoff: Decimal,
    cone_threshold: Decimal,
    coupled: bool,
) -> dict[str, object]:
    prepared = prepare_grouped_likelihood(observations)
    start = perf_counter()
    if coupled:
        result = _certify_cone_side_coupled(
            box,
            prepared,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff,
            cone_log_threshold_upper=cone_threshold,
            max_nodes=NODE_BUDGET,
            min_width=MIN_WIDTH,
        )
    else:
        result = _certify_cone_side_grouped(
            box,
            prepared,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff,
            cone_log_threshold_upper=cone_threshold,
            max_nodes=NODE_BUDGET,
            min_width=MIN_WIDTH,
        )
    elapsed = perf_counter() - start
    return {
        "certified": result.certified,
        "elapsed_seconds": elapsed,
        "nodes_visited": result.nodes_visited,
        "unresolved_boxes": result.unresolved_boxes,
        "reason": result.reason,
    }


def _nested(side: dict[str, object], name: str) -> dict[str, object]:
    return cast(dict[str, object], side[name])


def _run_scenario(
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
    box = initial_nuisance_box(observations, common_cutoff_lower=common_cutoff)
    if box is None:
        raise AssertionError(f"{name} did not produce a finite nuisance box")
    cone_threshold = _log_fraction_upper(1 / CONE_ALPHA)
    halfspaces = _cone_halfspaces(center, target_error=0.15)

    sides: list[dict[str, object]] = []
    for side_index, halfspace in enumerate(halfspaces):
        grouped = _time_side(
            observations,
            box=box,
            halfspace=halfspace,
            common_cutoff=common_cutoff,
            cone_threshold=cone_threshold,
            coupled=False,
        )
        coupled = _time_side(
            observations,
            box=box,
            halfspace=halfspace,
            common_cutoff=common_cutoff,
            cone_threshold=cone_threshold,
            coupled=True,
        )
        sides.append({"side": side_index, "grouped": grouped, "coupled": coupled})

    return {
        "scenario": name,
        "observation_count": len(observations),
        "grouped_certified": all(
            cast(bool, _nested(side, "grouped")["certified"]) for side in sides
        ),
        "coupled_certified": all(
            cast(bool, _nested(side, "coupled")["certified"]) for side in sides
        ),
        "grouped_nodes_total": sum(
            cast(int, _nested(side, "grouped")["nodes_visited"]) for side in sides
        ),
        "coupled_nodes_total": sum(
            cast(int, _nested(side, "coupled")["nodes_visited"]) for side in sides
        ),
        "grouped_seconds_total": sum(
            cast(float, _nested(side, "grouped")["elapsed_seconds"]) for side in sides
        ),
        "coupled_seconds_total": sum(
            cast(float, _nested(side, "coupled")["elapsed_seconds"]) for side in sides
        ),
        "sides": sides,
    }


def run_benchmark_v14c() -> dict[str, object]:
    validation_observations = _synthetic_observations(
        alpha=(0.2, 0.9, -0.35),
        repeats=8,
        seed=14_600,
    )
    validation_boxes = _random_boxes(count=VALIDATION_BOX_COUNT, seed=14_699)
    validation = _validate_coupled_bounds(validation_observations, validation_boxes)
    if validation["coupled_bound_violations"] != 0:
        raise AssertionError("coupled cone lower-bound violation")

    scenarios = [
        _run_scenario(name, alpha, repeats, seed, center)
        for name, alpha, repeats, seed, center in SCENARIOS
    ]
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Safety-preserving dependency-aware lower bounds for each rotated-alternative versus "
            "null log-likelihood ratio. The comparison keeps grouped sufficient statistics, alpha "
            "split, conservative rational cone, nuisance box, branch order, node budget, and "
            "resolution fixed."
        ),
        "config": {
            "validation_box_count": VALIDATION_BOX_COUNT,
            "validation_grid_size": VALIDATION_GRID_SIZE,
            "node_budget_per_side": NODE_BUDGET,
            "min_width": MIN_WIDTH,
        },
        "bound_validation": validation,
        "closure_scenarios": scenarios,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14c(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
