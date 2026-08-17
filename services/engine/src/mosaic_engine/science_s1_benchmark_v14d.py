from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction

from .science_s1_benchmark_v14a import (
    _common_exact_cutoff,
    _cone_exact_threshold,
    _reference_cone_log_e,
    _reference_log_likelihood,
    _synthetic_observations,
)
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    ParameterBox,
    _cone_halfspaces,
    _largest_width_dimension,
    _log_fraction_upper,
    _minimum_halfspace_value,
    _split_box,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_coupled import (
    grouped_coupled_cone_log_e_lower_bound,
)
from .science_s1_continuous_geometry_grouped import (
    grouped_cone_log_e_lower_bound,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-unresolved-box-attribution-v14d"
METHOD_VERSION = "continuous-bnb-attribution-v1"
NODE_BUDGET = 250
MIN_WIDTH = 0.05
SCENARIOS = (
    ("aligned_240", (0.15, 1.2, 0.0), 20, 14_601, (1.0, 0.0)),
    ("aligned_480", (0.15, 1.2, 0.0), 40, 14_602, (1.0, 0.0)),
)


def _float_intervals(box: ParameterBox) -> list[list[float]]:
    return [[float(lower), float(upper)] for lower, upper in box.intervals]


def _box_widths(box: ParameterBox) -> tuple[float, float, float]:
    return tuple(float(upper - lower) for lower, upper in box.intervals)  # type: ignore[return-value]


def _halfspace_probe_theta(
    box: ParameterBox,
    halfspace: Sequence[Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    intercept_lower, intercept_upper = box.intervals[0]
    intercept = (intercept_lower + intercept_upper) / 2
    slopes: list[Fraction] = []
    for coefficient, (lower, upper) in zip(halfspace, box.intervals[1:], strict=True):
        slopes.append(lower if coefficient >= 0 else upper)
    return intercept, slopes[0], slopes[1]


def _final_box_diagnostic(
    box: ParameterBox,
    halfspace: Sequence[Fraction],
    observations: Sequence[PrequentialBinaryObservation],
    *,
    common_cutoff_lower: Decimal,
    cone_threshold_upper: Decimal,
    common_exact_cutoff: Decimal,
    cone_exact_threshold: Decimal,
) -> dict[str, object]:
    prepared = prepare_grouped_likelihood(observations)
    null_upper = grouped_likelihood_bounds(box, prepared).upper
    grouped_lower = grouped_cone_log_e_lower_bound(box, prepared)
    coupled_lower = grouped_coupled_cone_log_e_lower_bound(box, prepared)
    probe = _halfspace_probe_theta(box, halfspace)
    probe_halfspace = halfspace[0] * probe[1] + halfspace[1] * probe[2]
    direct_log_likelihood = _reference_log_likelihood(probe, observations)
    direct_cone_log_e = _reference_cone_log_e(probe, observations)
    common_direct_margin = direct_log_likelihood - common_exact_cutoff
    cone_direct_margin = cone_exact_threshold - direct_cone_log_e
    widths = _box_widths(box)

    return {
        "intervals": _float_intervals(box),
        "widths": list(widths),
        "largest_width_dimension": max(range(3), key=widths.__getitem__),
        "halfspace_minimum": float(_minimum_halfspace_value(box, halfspace)),
        "common_bound_survival_margin": str(null_upper - common_cutoff_lower),
        "grouped_cone_bound_survival_margin": str(cone_threshold_upper - grouped_lower),
        "coupled_cone_bound_survival_margin": str(cone_threshold_upper - coupled_lower),
        "probe_theta": [float(value) for value in probe],
        "probe_halfspace_value": float(probe_halfspace),
        "probe_common_direct_margin": str(common_direct_margin),
        "probe_cone_direct_survival_margin": str(cone_direct_margin),
        "probe_joint_survivor": bool(
            probe_halfspace < 0 and common_direct_margin > 0 and cone_direct_margin > 0
        ),
    }


def _trace_side(
    observations: Sequence[PrequentialBinaryObservation],
    initial_box: ParameterBox,
    halfspace: Sequence[Fraction],
    *,
    method: str,
    max_nodes: int = NODE_BUDGET,
    min_width: float = MIN_WIDTH,
) -> dict[str, object]:
    if method not in {"grouped", "coupled"}:
        raise ValueError("method must be 'grouped' or 'coupled'")

    prepared = prepare_grouped_likelihood(observations)
    common_cutoff_lower = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    cone_threshold_upper = _log_fraction_upper(1 / CONE_ALPHA)
    common_exact_cutoff = _common_exact_cutoff(observations, alpha_level=COMMON_ALPHA)
    cone_exact_threshold = _cone_exact_threshold(alpha_level=CONE_ALPHA)

    stack = [initial_box]
    counts: Counter[str] = Counter()
    nodes_visited = 0
    terminal_reason = "all_violating_boxes_pruned"
    final_boxes: list[ParameterBox] = []

    while stack:
        if nodes_visited >= max_nodes:
            terminal_reason = "node_limit"
            final_boxes = list(stack)
            break

        box = stack.pop()
        nodes_visited += 1

        if _minimum_halfspace_value(box, halfspace) >= 0:
            counts["geometry_prune"] += 1
            continue

        null_upper = grouped_likelihood_bounds(box, prepared).upper
        if null_upper <= common_cutoff_lower:
            counts["common_prune"] += 1
            continue

        if method == "grouped":
            cone_lower = grouped_cone_log_e_lower_bound(box, prepared)
        else:
            cone_lower = grouped_coupled_cone_log_e_lower_bound(box, prepared)
        if cone_lower >= cone_threshold_upper:
            counts["cone_prune"] += 1
            continue

        widths = _box_widths(box)
        if max(widths) <= min_width:
            counts["resolution_unresolved"] += 1
            terminal_reason = "resolution_limit"
            final_boxes = [box, *stack]
            break

        dimension = _largest_width_dimension(box)
        if box.intervals[dimension][0] == box.intervals[dimension][1]:
            counts["degenerate_unresolved"] += 1
            terminal_reason = "degenerate_unresolved_box"
            final_boxes = [box, *stack]
            break

        counts["split"] += 1
        stack.extend(_split_box(box))

    if not stack and terminal_reason == "all_violating_boxes_pruned":
        final_boxes = []

    diagnostics = [
        _final_box_diagnostic(
            box,
            halfspace,
            observations,
            common_cutoff_lower=common_cutoff_lower,
            cone_threshold_upper=cone_threshold_upper,
            common_exact_cutoff=common_exact_cutoff,
            cone_exact_threshold=cone_exact_threshold,
        )
        for box in final_boxes
    ]

    return {
        "method": method,
        "nodes_visited": nodes_visited,
        "terminal_reason": terminal_reason,
        "final_unresolved_boxes": len(final_boxes),
        "counts": {
            key: counts[key]
            for key in (
                "geometry_prune",
                "common_prune",
                "cone_prune",
                "split",
                "resolution_unresolved",
                "degenerate_unresolved",
            )
        },
        "final_box_probe_joint_survivors": sum(
            int(bool(item["probe_joint_survivor"])) for item in diagnostics
        ),
        "final_boxes": diagnostics,
    }


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
    initial_box = initial_nuisance_box(observations, common_cutoff_lower=common_cutoff)
    if initial_box is None:
        raise AssertionError(f"{name} did not produce a finite nuisance box")
    halfspaces = _cone_halfspaces(center, target_error=0.15)

    return {
        "scenario": name,
        "observation_count": len(observations),
        "initial_box": _float_intervals(initial_box),
        "sides": [
            {
                "side": side_index,
                "grouped": _trace_side(
                    observations,
                    initial_box,
                    halfspace,
                    method="grouped",
                ),
                "coupled": _trace_side(
                    observations,
                    initial_box,
                    halfspace,
                    method="coupled",
                ),
            }
            for side_index, halfspace in enumerate(halfspaces)
        ],
    }


def run_benchmark_v14d() -> dict[str, object]:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Attribution-only replay of the frozen continuous branch-and-bound search. "
            "No confidence threshold, cone geometry, numerical precision, branch order, "
            "node budget, or likelihood/e-process definition is changed."
        ),
        "config": {
            "node_budget_per_side": NODE_BUDGET,
            "min_width": MIN_WIDTH,
            "common_alpha": float(COMMON_ALPHA),
            "cone_alpha": float(CONE_ALPHA),
        },
        "scenarios": [
            _run_scenario(name, alpha, repeats, seed, center)
            for name, alpha, repeats, seed, center in SCENARIOS
        ],
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14d(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
