from __future__ import annotations

import heapq
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from itertools import count
from time import perf_counter

from .science_s1_benchmark_v14a import _synthetic_observations
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    ParameterBox,
    _cone_halfspaces,
    _log_fraction_upper,
    _minimum_halfspace_value,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_coupled import (
    grouped_coupled_cone_log_e_lower_bound,
)
from .science_s1_continuous_geometry_grouped import (
    PreparedGroupedLikelihood,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-certified-search-allocation-v14e"
METHOD_VERSION = "coupled-child-preview-best-first-v1"
NODE_BUDGET = 250
MIN_WIDTH = 0.05

# v14d established that aligned_240 side 0 contains a directly verified
# outside-cone point surviving both confidence filters. It is a mandatory
# negative control: a search-only change must not certify it.
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
class BoxEvaluation:
    status: str
    common_survival_margin: Decimal | None
    cone_survival_margin: Decimal | None
    maximum_width: float

    @property
    def pruned(self) -> bool:
        return self.status != "unresolved"

    @property
    def prune_distance(self) -> float:
        if self.pruned:
            return 0.0
        assert self.common_survival_margin is not None
        assert self.cone_survival_margin is not None
        return max(
            0.0,
            min(
                float(self.common_survival_margin),
                float(self.cone_survival_margin),
            ),
        )


def _box_widths(box: ParameterBox) -> tuple[float, float, float]:
    return tuple(float(upper - lower) for lower, upper in box.intervals)  # type: ignore[return-value]


def _split_box_dimension(box: ParameterBox, dimension: int) -> tuple[ParameterBox, ParameterBox]:
    if dimension not in (0, 1, 2):
        raise ValueError("dimension must be 0, 1, or 2")
    lower, upper = box.intervals[dimension]
    if lower == upper:
        raise ValueError("cannot split a zero-width dimension")
    midpoint = (lower + upper) / 2
    left = list(box.intervals)
    right = list(box.intervals)
    left[dimension] = (lower, midpoint)
    right[dimension] = (midpoint, upper)
    return ParameterBox(tuple(left)), ParameterBox(tuple(right))


def _evaluate_box(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    *,
    halfspace: Sequence[Fraction],
    common_cutoff_lower: Decimal,
    cone_threshold_upper: Decimal,
) -> BoxEvaluation:
    maximum_width = max(_box_widths(box))
    if _minimum_halfspace_value(box, halfspace) >= 0:
        return BoxEvaluation("geometry_prune", None, None, maximum_width)

    common_margin = grouped_likelihood_bounds(box, prepared).upper - common_cutoff_lower
    if common_margin <= 0:
        return BoxEvaluation("common_prune", common_margin, None, maximum_width)

    cone_margin = cone_threshold_upper - grouped_coupled_cone_log_e_lower_bound(box, prepared)
    if cone_margin <= 0:
        return BoxEvaluation("cone_prune", common_margin, cone_margin, maximum_width)

    return BoxEvaluation("unresolved", common_margin, cone_margin, maximum_width)


def _preview_dimension(
    box: ParameterBox,
    dimension: int,
    prepared: PreparedGroupedLikelihood,
    *,
    halfspace: Sequence[Fraction],
    common_cutoff_lower: Decimal,
    cone_threshold_upper: Decimal,
) -> tuple[
    tuple[ParameterBox, BoxEvaluation],
    tuple[ParameterBox, BoxEvaluation],
]:
    children = _split_box_dimension(box, dimension)
    return tuple(
        (
            child,
            _evaluate_box(
                child,
                prepared,
                halfspace=halfspace,
                common_cutoff_lower=common_cutoff_lower,
                cone_threshold_upper=cone_threshold_upper,
            ),
        )
        for child in children
    )  # type: ignore[return-value]


def _dimension_score(
    preview: Sequence[tuple[ParameterBox, BoxEvaluation]],
    *,
    dimension: int,
) -> tuple[float, float, float, int]:
    pruned_count = sum(int(evaluation.pruned) for _, evaluation in preview)
    unresolved_distances = [
        evaluation.prune_distance for _, evaluation in preview if not evaluation.pruned
    ]
    worst_distance = max(unresolved_distances, default=0.0)
    total_distance = sum(unresolved_distances)
    return (-float(pruned_count), worst_distance, total_distance, dimension)


def _frontier_priority(evaluation: BoxEvaluation, *, serial: int) -> tuple[float, float, int]:
    # Safe bounds determine the score, but the score only changes processing order.
    # Correctness never depends on the floating-point priority value.
    return (evaluation.prune_distance, evaluation.maximum_width, serial)


def _run_preview_best_first_side(
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

    serials = count()
    frontier: list[tuple[float, float, int, ParameterBox]] = [
        (0.0, max(_box_widths(initial_box)), next(serials), initial_box)
    ]
    nodes_visited = 0
    preview_evaluations = 0
    counts: Counter[str] = Counter()
    selected_dimensions: Counter[int] = Counter()
    start = perf_counter()

    while frontier:
        if nodes_visited >= max_nodes:
            return {
                "certified": False,
                "nodes_visited": nodes_visited,
                "preview_evaluations": preview_evaluations,
                "unresolved_boxes": len(frontier),
                "terminal_reason": "node_limit",
                "counts": dict(counts),
                "selected_dimensions": {
                    str(index): selected_dimensions[index] for index in range(3)
                },
                "elapsed_seconds": perf_counter() - start,
            }

        _, _, _, box = heapq.heappop(frontier)
        nodes_visited += 1
        evaluation = _evaluate_box(
            box,
            prepared,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff_lower,
            cone_threshold_upper=cone_threshold_upper,
        )
        counts[evaluation.status] += 1
        if evaluation.pruned:
            continue

        if evaluation.maximum_width <= min_width:
            return {
                "certified": False,
                "nodes_visited": nodes_visited,
                "preview_evaluations": preview_evaluations,
                "unresolved_boxes": len(frontier) + 1,
                "terminal_reason": "resolution_limit",
                "counts": dict(counts),
                "selected_dimensions": {
                    str(index): selected_dimensions[index] for index in range(3)
                },
                "elapsed_seconds": perf_counter() - start,
            }

        legal_dimensions = [
            index for index, (lower, upper) in enumerate(box.intervals) if lower != upper
        ]
        if not legal_dimensions:
            return {
                "certified": False,
                "nodes_visited": nodes_visited,
                "preview_evaluations": preview_evaluations,
                "unresolved_boxes": len(frontier) + 1,
                "terminal_reason": "degenerate_unresolved_box",
                "counts": dict(counts),
                "selected_dimensions": {
                    str(index): selected_dimensions[index] for index in range(3)
                },
                "elapsed_seconds": perf_counter() - start,
            }

        previews: dict[
            int,
            tuple[
                tuple[ParameterBox, BoxEvaluation],
                tuple[ParameterBox, BoxEvaluation],
            ],
        ] = {}
        for dimension in legal_dimensions:
            preview = _preview_dimension(
                box,
                dimension,
                prepared,
                halfspace=halfspace,
                common_cutoff_lower=common_cutoff_lower,
                cone_threshold_upper=cone_threshold_upper,
            )
            preview_evaluations += 2
            previews[dimension] = preview

        chosen_dimension = min(
            legal_dimensions,
            key=lambda dimension: _dimension_score(
                previews[dimension],
                dimension=dimension,
            ),
        )
        selected_dimensions[chosen_dimension] += 1
        counts["split"] += 1

        for child, child_preview in previews[chosen_dimension]:
            serial = next(serials)
            priority = _frontier_priority(child_preview, serial=serial)
            heapq.heappush(frontier, (*priority, child))

    return {
        "certified": True,
        "nodes_visited": nodes_visited,
        "preview_evaluations": preview_evaluations,
        "unresolved_boxes": 0,
        "terminal_reason": "all_violating_boxes_pruned",
        "counts": dict(counts),
        "selected_dimensions": {str(index): selected_dimensions[index] for index in range(3)},
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

    candidate = _run_preview_best_first_side(
        observations,
        initial_box,
        halfspace=halfspace,
    )
    if name == "aligned_240_side0_negative_control" and candidate["certified"]:
        raise AssertionError(
            "v14e search-only policy certified the v14d direct-survivor negative control"
        )

    return {
        "case": name,
        "observation_count": len(observations),
        "side": side_index,
        "reference_v14d": REFERENCE_V14D[name],
        "preview_best_first": candidate,
    }


def run_benchmark_v14e() -> dict[str, object]:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Search-allocation-only comparison. The v14c coupled confidence predicates, "
            "alpha split, nuisance box, rational cone, precision, node budget, and "
            "resolution floor are unchanged. Child previews affect only split dimension "
            "and frontier order; preview evaluations are reported separately."
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
    print(json.dumps(run_benchmark_v14e(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
