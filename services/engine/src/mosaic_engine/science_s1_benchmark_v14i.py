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
from .science_s1_common_polytope import (
    LinearUpperHalfspace,
    box_disjoint_from_halfspace_polytope,
    common_score_halfspaces,
    point_satisfies_halfspace_polytope,
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

BENCHMARK_VERSION = "s1-active-common-polytope-v14i"
METHOD_VERSION = "score-halfspace-prune-fair-best-first-v1"
EVALUATION_BUDGET = 250
MIN_WIDTH = 0.05

CASES = (
    ("aligned_240_side0_negative_control", (0.15, 1.2, 0.0), 20, 14_601, 0),
    ("aligned_480_side0", (0.15, 1.2, 0.0), 40, 14_602, 0),
    ("aligned_480_side1", (0.15, 1.2, 0.0), 40, 14_602, 1),
)

REFERENCE_V14G = {
    "aligned_240_side0_negative_control": {
        "evaluations": 249,
        "unresolved_boxes": 2,
        "certified": False,
        "elapsed_seconds": 44.929193590000005,
    },
    "aligned_480_side0": {
        "evaluations": 249,
        "unresolved_boxes": 5,
        "certified": False,
        "elapsed_seconds": 51.13619508999999,
    },
    "aligned_480_side1": {
        "evaluations": 249,
        "unresolved_boxes": 4,
        "certified": False,
        "elapsed_seconds": 51.15366469100001,
    },
}

KNOWN_240_SURVIVOR = (
    0.6758436374323773,
    1.253551105895155,
    -0.6918084477654259,
)


@dataclass(frozen=True)
class EvaluatedPolytopeBox:
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
    values = tuple(float(upper - lower) for lower, upper in box.intervals)
    return values[0], values[1], values[2]


def _evaluate_box(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    halfspaces: Sequence[LinearUpperHalfspace],
    *,
    directional_halfspace: Sequence[Fraction],
    common_cutoff_lower: Decimal,
    cone_threshold_upper: Decimal,
) -> EvaluatedPolytopeBox:
    maximum_width = max(_box_widths(box))
    if _minimum_halfspace_value(box, directional_halfspace) >= 0:
        return EvaluatedPolytopeBox(box, "geometry_prune", None, None, None, maximum_width)

    if box_disjoint_from_halfspace_polytope(box, halfspaces):
        return EvaluatedPolytopeBox(box, "polytope_prune", None, None, None, maximum_width)

    common_margin = grouped_likelihood_bounds(box, prepared).upper - common_cutoff_lower
    if common_margin <= 0:
        return EvaluatedPolytopeBox(
            box, "common_prune", None, common_margin, None, maximum_width
        )

    diagnostic = _cone_lower_bound_with_penalties(box, prepared)
    cone_margin = cone_threshold_upper - diagnostic.log_e_lower_bound
    if cone_margin <= 0:
        return EvaluatedPolytopeBox(
            box,
            "cone_prune",
            diagnostic,
            common_margin,
            cone_margin,
            maximum_width,
        )

    return EvaluatedPolytopeBox(
        box,
        "unresolved",
        diagnostic,
        common_margin,
        cone_margin,
        maximum_width,
    )


def _frontier_priority(
    evaluated: EvaluatedPolytopeBox,
    *,
    serial: int,
) -> tuple[float, float, int]:
    if not evaluated.unresolved:
        raise ValueError("only unresolved boxes belong on the active frontier")
    return (evaluated.priority_distance, evaluated.maximum_width, serial)


def _run_active_polytope_side(
    observations: Sequence[PrequentialBinaryObservation],
    initial_box: ParameterBox,
    halfspaces: Sequence[LinearUpperHalfspace],
    *,
    directional_halfspace: Sequence[Fraction],
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
    active: list[tuple[float, float, int, EvaluatedPolytopeBox]] = []
    frozen_resolution: list[EvaluatedPolytopeBox] = []
    start = perf_counter()

    root = _evaluate_box(
        initial_box,
        prepared,
        halfspaces,
        directional_halfspace=directional_halfspace,
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
                halfspaces,
                directional_halfspace=directional_halfspace,
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
    cutoff = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    coarse_box = initial_nuisance_box(
        observations,
        common_cutoff_lower=cutoff,
    )
    if coarse_box is None:
        raise AssertionError(f"{name} did not produce a finite nuisance box")
    halfspaces = common_score_halfspaces(
        observations,
        common_cutoff_lower=cutoff,
        coarse_box=coarse_box,
    )

    if name == "aligned_240_side0_negative_control":
        survivor = tuple(Fraction.from_float(value) for value in KNOWN_240_SURVIVOR)
        if not point_satisfies_halfspace_polytope(survivor, halfspaces):
            raise AssertionError("active common polytope excluded v14d retained survivor")

    directional_halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[side_index]
    candidate = _run_active_polytope_side(
        observations,
        coarse_box,
        halfspaces,
        directional_halfspace=directional_halfspace,
    )
    if name == "aligned_240_side0_negative_control" and candidate["certified"]:
        raise AssertionError(
            "v14i active common polytope certified the known retained outside-cone negative control"
        )

    return {
        "case": name,
        "observation_count": len(observations),
        "side": side_index,
        "halfspace_count": len(halfspaces),
        "reference_v14g": REFERENCE_V14G[name],
        "active_common_polytope": candidate,
    }


def run_benchmark_v14i() -> dict[str, object]:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Common-region representation change only. The original coarse nuisance "
            "box is retained, but every exact necessary score halfspace from v14h "
            "remains active as a certified disjointness prune at every charged box "
            "evaluation. The common e-process, alpha split, directional e-process, "
            "rational cone, coupled bound, sensitivity split, fair best-first order, "
            "precision, and 250-evaluation budget are unchanged."
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
    print(json.dumps(run_benchmark_v14i(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
