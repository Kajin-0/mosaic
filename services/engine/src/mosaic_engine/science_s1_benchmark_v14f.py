from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from fractions import Fraction
from time import perf_counter

from .science_s1_benchmark_v14a import _synthetic_observations
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    CONE_OFFSETS_DEGREES,
    ParameterBox,
    _cone_halfspaces,
    _decimal_from_fraction,
    _directed_sum,
    _log_fraction_upper,
    _minimum_halfspace_value,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_coupled import (
    _box_center,
    _difference_interval,
    _directed_multiply,
    _directed_subtract,
    _gradient_term_bounds,
    _half_widths,
    _interval_scale_nonnegative_integer,
    _point_box,
    _residual_bounds,
)
from .science_s1_continuous_geometry_grouped import (
    PreparedGroupedLikelihood,
    _designs_for_rotation,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-sensitivity-guided-split-v14f"
METHOD_VERSION = "coupled-best-rotation-penalty-dfs-v1"
NODE_BUDGET = 250
MIN_WIDTH = 0.05

CASES = (
    ("aligned_240_side0_negative_control", (0.15, 1.2, 0.0), 20, 14_601, 0),
    ("aligned_480_side0", (0.15, 1.2, 0.0), 40, 14_602, 0),
    ("aligned_480_side1", (0.15, 1.2, 0.0), 40, 14_602, 1),
)

REFERENCE_V14D = {
    "aligned_240_side0_negative_control": {
        "nodes_visited": 250,
        "terminal_reason": "node_limit",
        "unresolved_boxes": 13,
    },
    "aligned_480_side0": {
        "nodes_visited": 250,
        "terminal_reason": "resolution_limit",
        "unresolved_boxes": 10,
    },
    "aligned_480_side1": {
        "nodes_visited": 250,
        "terminal_reason": "node_limit",
        "unresolved_boxes": 9,
    },
}


@dataclass(frozen=True)
class RatioPenaltyDiagnostic:
    rotation_degrees: float
    lower_bound: Decimal
    axis_penalties: tuple[Decimal, Decimal, Decimal]


@dataclass(frozen=True)
class ConePenaltyDiagnostic:
    log_e_lower_bound: Decimal
    best_rotation_degrees: float
    axis_penalties: tuple[Decimal, Decimal, Decimal]


def _ratio_lower_bound_with_penalties(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    *,
    rotation_degrees: float,
) -> RatioPenaltyDiagnostic:
    if float(rotation_degrees) == 0.0:
        return RatioPenaltyDiagnostic(
            rotation_degrees=0.0,
            lower_bound=Decimal(0),
            axis_penalties=(Decimal(0), Decimal(0), Decimal(0)),
        )

    center = _box_center(box)
    center_box = _point_box(center)
    null_center = grouped_likelihood_bounds(center_box, prepared)
    rotated_center = grouped_likelihood_bounds(
        center_box,
        prepared,
        rotation_degrees=rotation_degrees,
    )
    center_ratio_lower = _directed_subtract(
        rotated_center.lower,
        null_center.upper,
        rounding=ROUND_FLOOR,
    )

    null_designs = _designs_for_rotation(prepared, 0.0)
    rotated_designs = _designs_for_rotation(prepared, rotation_degrees)
    gradient_lower_terms: list[list[Decimal]] = [[], [], []]
    gradient_upper_terms: list[list[Decimal]] = [[], [], []]

    for group, null_design, rotated_design in zip(
        prepared.groups,
        null_designs,
        rotated_designs,
        strict=True,
    ):
        from .science_s1_continuous_geometry import _score_interval

        null_score = _score_interval(box, null_design)
        rotated_score = _score_interval(box, rotated_design)
        for accepted, count in (
            (True, group.accept_count),
            (False, group.reject_count),
        ):
            if count == 0:
                continue
            null_residual = _residual_bounds(null_score, accepted=accepted)
            rotated_residual = _residual_bounds(rotated_score, accepted=accepted)
            for axis in range(3):
                rotated_term = _gradient_term_bounds(
                    rotated_residual,
                    rotated_design[axis],
                )
                null_term = _gradient_term_bounds(null_residual, null_design[axis])
                difference = _difference_interval(rotated_term, null_term)
                scaled = _interval_scale_nonnegative_integer(difference, count)
                gradient_lower_terms[axis].append(scaled[0])
                gradient_upper_terms[axis].append(scaled[1])

    penalties: list[Decimal] = []
    for width, lower_terms, upper_terms in zip(
        _half_widths(box),
        gradient_lower_terms,
        gradient_upper_terms,
        strict=True,
    ):
        gradient_lower = _directed_sum(lower_terms, rounding=ROUND_FLOOR)
        gradient_upper = _directed_sum(upper_terms, rounding=ROUND_CEILING)
        width_upper = _decimal_from_fraction(width, rounding=ROUND_CEILING)
        gradient_abs_upper = max(abs(gradient_lower), abs(gradient_upper))
        penalties.append(
            _directed_multiply(
                width_upper,
                gradient_abs_upper,
                rounding=ROUND_CEILING,
            )
        )

    total_penalty = _directed_sum(penalties, rounding=ROUND_CEILING)
    lower_bound = _directed_subtract(
        center_ratio_lower,
        total_penalty,
        rounding=ROUND_FLOOR,
    )
    return RatioPenaltyDiagnostic(
        rotation_degrees=float(rotation_degrees),
        lower_bound=lower_bound,
        axis_penalties=(penalties[0], penalties[1], penalties[2]),
    )


def _cone_lower_bound_with_penalties(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
) -> ConePenaltyDiagnostic:
    diagnostics = tuple(
        _ratio_lower_bound_with_penalties(
            box,
            prepared,
            rotation_degrees=float(offset),
        )
        for offset in CONE_OFFSETS_DEGREES
    )
    best = max(diagnostics, key=lambda item: item.lower_bound)
    log_support_upper = _log_fraction_upper(Fraction(len(CONE_OFFSETS_DEGREES)))
    lower_bound = _directed_subtract(
        best.lower_bound,
        log_support_upper,
        rounding=ROUND_FLOOR,
    )
    return ConePenaltyDiagnostic(
        log_e_lower_bound=lower_bound,
        best_rotation_degrees=best.rotation_degrees,
        axis_penalties=best.axis_penalties,
    )


def _split_box_dimension(box: ParameterBox, dimension: int) -> tuple[ParameterBox, ParameterBox]:
    lower, upper = box.intervals[dimension]
    if lower == upper:
        raise ValueError("cannot split zero-width dimension")
    midpoint = (lower + upper) / 2
    left = list(box.intervals)
    right = list(box.intervals)
    left[dimension] = (lower, midpoint)
    right[dimension] = (midpoint, upper)
    return ParameterBox(tuple(left)), ParameterBox(tuple(right))


def _sensitivity_split_dimension(
    box: ParameterBox,
    diagnostic: ConePenaltyDiagnostic,
) -> int:
    legal = [
        index
        for index, (lower, upper) in enumerate(box.intervals)
        if lower != upper
    ]
    if not legal:
        raise ValueError("box has no splittable dimension")
    return max(
        legal,
        key=lambda index: (diagnostic.axis_penalties[index], -index),
    )


def _run_sensitivity_dfs_side(
    observations: Sequence[PrequentialBinaryObservation],
    initial_box: ParameterBox,
    *,
    halfspace: Sequence[Fraction],
    max_nodes: int = NODE_BUDGET,
    min_width: float = MIN_WIDTH,
) -> dict[str, object]:
    prepared = prepare_grouped_likelihood(observations)
    common_cutoff_lower = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    cone_threshold_upper = _log_fraction_upper(1 / CONE_ALPHA)

    stack = [initial_box]
    nodes_visited = 0
    counts: Counter[str] = Counter()
    selected_dimensions: Counter[int] = Counter()
    chosen_rotations: Counter[float] = Counter()
    start = perf_counter()

    while stack:
        if nodes_visited >= max_nodes:
            return {
                "certified": False,
                "nodes_visited": nodes_visited,
                "unresolved_boxes": len(stack),
                "terminal_reason": "node_limit",
                "counts": dict(counts),
                "selected_dimensions": {
                    str(index): selected_dimensions[index] for index in range(3)
                },
                "best_rotation_counts": {
                    str(key): value for key, value in sorted(chosen_rotations.items())
                },
                "elapsed_seconds": perf_counter() - start,
            }

        box = stack.pop()
        nodes_visited += 1

        if _minimum_halfspace_value(box, halfspace) >= 0:
            counts["geometry_prune"] += 1
            continue

        null_upper = grouped_likelihood_bounds(box, prepared).upper
        if null_upper <= common_cutoff_lower:
            counts["common_prune"] += 1
            continue

        diagnostic = _cone_lower_bound_with_penalties(box, prepared)
        if diagnostic.log_e_lower_bound >= cone_threshold_upper:
            counts["cone_prune"] += 1
            continue

        widths = [float(upper - lower) for lower, upper in box.intervals]
        if max(widths) <= min_width:
            counts["resolution_unresolved"] += 1
            return {
                "certified": False,
                "nodes_visited": nodes_visited,
                "unresolved_boxes": len(stack) + 1,
                "terminal_reason": "resolution_limit",
                "counts": dict(counts),
                "selected_dimensions": {
                    str(index): selected_dimensions[index] for index in range(3)
                },
                "best_rotation_counts": {
                    str(key): value for key, value in sorted(chosen_rotations.items())
                },
                "elapsed_seconds": perf_counter() - start,
            }

        dimension = _sensitivity_split_dimension(box, diagnostic)
        selected_dimensions[dimension] += 1
        chosen_rotations[diagnostic.best_rotation_degrees] += 1
        counts["split"] += 1
        stack.extend(_split_box_dimension(box, dimension))

    return {
        "certified": True,
        "nodes_visited": nodes_visited,
        "unresolved_boxes": 0,
        "terminal_reason": "all_violating_boxes_pruned",
        "counts": dict(counts),
        "selected_dimensions": {
            str(index): selected_dimensions[index] for index in range(3)
        },
        "best_rotation_counts": {
            str(key): value for key, value in sorted(chosen_rotations.items())
        },
        "elapsed_seconds": perf_counter() - start,
    }


def _run_case(
    name: str,
    alpha: Sequence[float],
    repeats: int,
    seed: int,
    side_index: int,
) -> dict[str, object]:
    observations = _synthetic_observations(alpha=alpha, repeats=repeats, seed=seed)
    common_cutoff = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    initial_box = initial_nuisance_box(observations, common_cutoff_lower=common_cutoff)
    if initial_box is None:
        raise AssertionError(f"{name} did not produce a finite nuisance box")
    halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[side_index]

    candidate = _run_sensitivity_dfs_side(
        observations,
        initial_box,
        halfspace=halfspace,
    )
    if name == "aligned_240_side0_negative_control" and candidate["certified"]:
        raise AssertionError(
            "v14f search-only policy certified the v14d direct-survivor negative control"
        )

    return {
        "case": name,
        "observation_count": len(observations),
        "side": side_index,
        "reference_v14d": REFERENCE_V14D[name],
        "sensitivity_dfs": candidate,
    }


def run_benchmark_v14f() -> dict[str, object]:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Split-dimension-only comparison. The v14c coupled confidence bound, alpha split, "
            "nuisance box, rational cone, precision, DFS frontier order, node budget, and "
            "resolution floor are unchanged. Split dimensions use the per-axis mean-value "
            "penalties already required to construct the best rotated coupled lower bound."
        ),
        "config": {
            "node_budget": NODE_BUDGET,
            "min_width": MIN_WIDTH,
            "common_alpha": float(COMMON_ALPHA),
            "cone_alpha": float(CONE_ALPHA),
        },
        "cases": [
            _run_case(name, alpha, repeats, seed, side_index)
            for name, alpha, repeats, seed, side_index in CASES
        ],
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14f(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
