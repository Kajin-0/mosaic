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
from .science_s1_benchmark_v14f import (
    ConePenaltyDiagnostic,
    _cone_lower_bound_with_penalties,
    _sensitivity_split_dimension,
    _split_box_dimension,
)
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
from .science_s1_continuous_geometry_grouped import (
    PreparedGroupedLikelihood,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-fair-best-first-search-v14g"
METHOD_VERSION = "sensitivity-split-cached-best-first-v1"
EVALUATION_BUDGET = 250
MIN_WIDTH = 0.05

CASES = (
    ("aligned_240_side0_negative_control", (0.15, 1.2, 0.0), 20, 14_601, 0),
    ("aligned_480_side0", (0.15, 1.2, 0.0), 40, 14_602, 0),
    ("aligned_480_side1", (0.15, 1.2, 0.0), 40, 14_602, 1),
)

REFERENCE_V14F = {
    "aligned_240_side0_negative_control": {
        "evaluations": 250,
        "unresolved_boxes": 11,
        "terminal_reason": "node_limit",
        "elapsed_seconds": 44.62736254100001,
    },
    "aligned_480_side0": {
        "evaluations": 250,
        "unresolved_boxes": 9,
        "terminal_reason": "node_limit",
        "elapsed_seconds": 46.085466389000004,
    },
    "aligned_480_side1": {
        "evaluations": 250,
        "unresolved_boxes": 7,
        "terminal_reason": "node_limit",
        "elapsed_seconds": 54.399670894000025,
    },
}


@dataclass(frozen=True)
class EvaluatedBox:
    box: ParameterBox
    status: str
    diagnostic: ConePenaltyDiagnostic | None
    common_survival_margin: Decimal | None
    cone_survival_margin: Decimal | None
    maximum_width: float

    @property
    def unresolved(self) -> bool:
        return self.status == "unresolved"

    @property
    def priority_distance(self) -> float:
        if not self.unresolved:
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


def _evaluate_box(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    *,
    halfspace: Sequence[Fraction],
    common_cutoff_lower: Decimal,
    cone_threshold_upper: Decimal,
) -> EvaluatedBox:
    maximum_width = max(_box_widths(box))
    if _minimum_halfspace_value(box, halfspace) >= 0:
        return EvaluatedBox(
            box,
            "geometry_prune",
            None,
            None,
            None,
            maximum_width,
        )

    common_margin = grouped_likelihood_bounds(box, prepared).upper - common_cutoff_lower
    if common_margin <= 0:
        return EvaluatedBox(
            box,
            "common_prune",
            None,
            common_margin,
            None,
            maximum_width,
        )

    diagnostic = _cone_lower_bound_with_penalties(box, prepared)
    cone_margin = cone_threshold_upper - diagnostic.log_e_lower_bound
    if cone_margin <= 0:
        return EvaluatedBox(
            box,
            "cone_prune",
            diagnostic,
            common_margin,
            cone_margin,
            maximum_width,
        )

    return EvaluatedBox(
        box,
        "unresolved",
        diagnostic,
        common_margin,
        cone_margin,
        maximum_width,
    )


def _frontier_priority(
    evaluated: EvaluatedBox,
    *,
    serial: int,
) -> tuple[float, float, int]:
    if not evaluated.unresolved:
        raise ValueError("only unresolved boxes belong on the active frontier")
    return (evaluated.priority_distance, evaluated.maximum_width, serial)


def _run_fair_best_first_side(
    observations: Sequence[PrequentialBinaryObservation],
    initial_box: ParameterBox,
    *,
    halfspace: Sequence[Fraction],
    evaluation_budget: int = EVALUATION_BUDGET,
    min_width: float = MIN_WIDTH,
) -> dict[str, object]:
    if evaluation_budget <= 0:
        raise ValueError("evaluation_budget must be positive")

    prepared = prepare_grouped_likelihood(observations)
    common_cutoff_lower = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    cone_threshold_upper = _log_fraction_upper(1 / CONE_ALPHA)

    evaluations = 0
    counts: Counter[str] = Counter()
    selected_dimensions: Counter[int] = Counter()
    serials = count()
    active: list[tuple[float, float, int, EvaluatedBox]] = []
    frozen_resolution: list[EvaluatedBox] = []
    start = perf_counter()

    root = _evaluate_box(
        initial_box,
        prepared,
        halfspace=halfspace,
        common_cutoff_lower=common_cutoff_lower,
        cone_threshold_upper=cone_threshold_upper,
    )
    evaluations += 1
    counts[root.status] += 1
    if not root.unresolved:
        return {
            "certified": True,
            "evaluations": evaluations,
            "unresolved_boxes": 0,
            "terminal_reason": "root_pruned",
            "counts": dict(counts),
            "selected_dimensions": {str(index): 0 for index in range(3)},
            "elapsed_seconds": perf_counter() - start,
        }
    if root.maximum_width <= min_width:
        frozen_resolution.append(root)
    else:
        serial = next(serials)
        heapq.heappush(active, (*_frontier_priority(root, serial=serial), root))

    while active:
        _, _, _, current = heapq.heappop(active)
        assert current.diagnostic is not None

        # Splitting creates two boxes that both require certified evaluation.
        # Do not grant partial/free child work when fewer than two evaluations remain.
        if evaluations + 2 > evaluation_budget:
            serial = next(serials)
            heapq.heappush(active, (*_frontier_priority(current, serial=serial), current))
            break

        dimension = _sensitivity_split_dimension(current.box, current.diagnostic)
        selected_dimensions[dimension] += 1
        counts["split"] += 1
        children = _split_box_dimension(current.box, dimension)

        for child in children:
            evaluated = _evaluate_box(
                child,
                prepared,
                halfspace=halfspace,
                common_cutoff_lower=common_cutoff_lower,
                cone_threshold_upper=cone_threshold_upper,
            )
            evaluations += 1
            counts[evaluated.status] += 1
            if not evaluated.unresolved:
                continue
            if evaluated.maximum_width <= min_width:
                counts["resolution_frozen"] += 1
                frozen_resolution.append(evaluated)
                continue
            serial = next(serials)
            heapq.heappush(
                active,
                (*_frontier_priority(evaluated, serial=serial), evaluated),
            )

    unresolved_boxes = len(active) + len(frozen_resolution)
    if unresolved_boxes == 0:
        certified = True
        terminal_reason = "all_violating_boxes_pruned"
    elif evaluations + 2 > evaluation_budget and active:
        certified = False
        terminal_reason = "evaluation_budget"
    elif frozen_resolution:
        certified = False
        terminal_reason = "resolution_limit"
    else:
        certified = False
        terminal_reason = "unresolved"

    return {
        "certified": certified,
        "evaluations": evaluations,
        "unresolved_boxes": unresolved_boxes,
        "active_unresolved_boxes": len(active),
        "resolution_frozen_boxes": len(frozen_resolution),
        "terminal_reason": terminal_reason,
        "counts": dict(counts),
        "selected_dimensions": {
            str(index): selected_dimensions[index] for index in range(3)
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

    candidate = _run_fair_best_first_side(
        observations,
        initial_box,
        halfspace=halfspace,
    )
    if name == "aligned_240_side0_negative_control" and candidate["certified"]:
        raise AssertionError(
            "v14g search-only policy certified the v14d direct-survivor negative control"
        )

    return {
        "case": name,
        "observation_count": len(observations),
        "side": side_index,
        "reference_v14f": REFERENCE_V14F[name],
        "fair_best_first": candidate,
    }


def run_benchmark_v14g() -> dict[str, object]:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Frontier-order comparison with v14f sensitivity splitting held fixed. Every generated "
            "child is evaluated once with the exact v14c coupled predicates, cached, and counted "
            "against the same finite bound-evaluation budget. No child preview is free."
        ),
        "config": {
            "evaluation_budget": EVALUATION_BUDGET,
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
    print(json.dumps(run_benchmark_v14g(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
