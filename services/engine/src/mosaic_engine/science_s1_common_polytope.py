from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from itertools import combinations

from .science_s1_continuous_geometry import (
    ParameterBox,
    _design_vector,
    _invert_three_by_three,
    initial_nuisance_box,
)
from .science_s1_eprocess import PrequentialBinaryObservation


@dataclass(frozen=True)
class LinearUpperHalfspace:
    coefficients: tuple[Fraction, Fraction, Fraction]
    upper_bound: Fraction
    source: str


@dataclass(frozen=True)
class CommonPolytopeOuterBox:
    coarse_box: ParameterBox
    tightened_box: ParameterBox
    halfspace_count: int
    feasible_vertex_count: int


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction(0))


def _matvec(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    if len(matrix) != 3 or len(vector) != 3:
        raise ValueError("matrix-vector product requires dimension three")
    values = tuple(_dot(row, vector) for row in matrix)
    return values[0], values[1], values[2]


def common_score_halfspaces(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    common_cutoff_lower: Decimal,
    coarse_box: ParameterBox,
) -> tuple[LinearUpperHalfspace, ...]:
    """Return necessary linear constraints for every common-CS parameter."""

    if not observations:
        raise ValueError("observations must not be empty")
    cutoff = Fraction(common_cutoff_lower)
    if cutoff >= 0:
        raise ValueError("common cutoff must be negative")

    counts: dict[tuple[float, float], list[int]] = defaultdict(lambda: [0, 0])
    for observation in observations:
        if len(observation.features) != 2:
            raise ValueError("continuous S1 common polytope requires two slope features")
        key = (float(observation.features[0]), float(observation.features[1]))
        if observation.accepted:
            counts[key][1] += 1
        else:
            counts[key][0] += 1

    halfspaces: list[LinearUpperHalfspace] = []
    for axis, (lower, upper) in enumerate(coarse_box.intervals):
        positive = [Fraction(0), Fraction(0), Fraction(0)]
        positive[axis] = Fraction(1)
        halfspaces.append(
            LinearUpperHalfspace(
                coefficients=(positive[0], positive[1], positive[2]),
                upper_bound=upper,
                source=f"coarse_upper_{axis}",
            )
        )
        negative = [Fraction(0), Fraction(0), Fraction(0)]
        negative[axis] = Fraction(-1)
        halfspaces.append(
            LinearUpperHalfspace(
                coefficients=(negative[0], negative[1], negative[2]),
                upper_bound=-lower,
                source=f"coarse_lower_{axis}",
            )
        )

    for features, (reject_count, accept_count) in sorted(counts.items()):
        design = _design_vector(features)
        if accept_count > 0:
            # log(sigmoid(z)) <= z and total log likelihood >= cutoff imply
            # z >= cutoff / accept_count.
            halfspaces.append(
                LinearUpperHalfspace(
                    coefficients=(-design[0], -design[1], -design[2]),
                    upper_bound=-(cutoff / accept_count),
                    source=f"accept_{features[0]}_{features[1]}",
                )
            )
        if reject_count > 0:
            # log(sigmoid(-z)) <= -z implies z <= -cutoff / reject_count.
            halfspaces.append(
                LinearUpperHalfspace(
                    coefficients=design,
                    upper_bound=-(cutoff / reject_count),
                    source=f"reject_{features[0]}_{features[1]}",
                )
            )

    return tuple(halfspaces)


def _feasible_vertex(
    selected: Sequence[LinearUpperHalfspace],
    all_halfspaces: Sequence[LinearUpperHalfspace],
) -> tuple[Fraction, Fraction, Fraction] | None:
    rows = tuple(halfspace.coefficients for halfspace in selected)
    inverse = _invert_three_by_three(rows)
    if inverse is None:
        return None
    bounds = tuple(halfspace.upper_bound for halfspace in selected)
    candidate = _matvec(inverse, bounds)
    if all(
        _dot(halfspace.coefficients, candidate) <= halfspace.upper_bound
        for halfspace in all_halfspaces
    ):
        return candidate
    return None


def exact_bounding_box_from_halfspaces(
    halfspaces: Sequence[LinearUpperHalfspace],
) -> tuple[ParameterBox, int] | None:
    """Return exact coordinate extrema of a bounded three-dimensional polytope."""

    if len(halfspaces) < 6:
        raise ValueError("at least the six coarse-box halfspaces are required")

    vertices: set[tuple[Fraction, Fraction, Fraction]] = set()
    for selected in combinations(halfspaces, 3):
        candidate = _feasible_vertex(selected, halfspaces)
        if candidate is not None:
            vertices.add(candidate)

    if not vertices:
        return None

    intervals = tuple(
        (
            min(vertex[axis] for vertex in vertices),
            max(vertex[axis] for vertex in vertices),
        )
        for axis in range(3)
    )
    return ParameterBox(intervals), len(vertices)


def certified_common_polytope_outer_box(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    common_cutoff_lower: Decimal,
) -> CommonPolytopeOuterBox | None:
    coarse_box = initial_nuisance_box(
        observations,
        common_cutoff_lower=common_cutoff_lower,
    )
    if coarse_box is None:
        return None

    halfspaces = common_score_halfspaces(
        observations,
        common_cutoff_lower=common_cutoff_lower,
        coarse_box=coarse_box,
    )
    result = exact_bounding_box_from_halfspaces(halfspaces)
    if result is None:
        return CommonPolytopeOuterBox(
            coarse_box=coarse_box,
            tightened_box=coarse_box,
            halfspace_count=len(halfspaces),
            feasible_vertex_count=0,
        )
    tightened_box, vertex_count = result
    return CommonPolytopeOuterBox(
        coarse_box=coarse_box,
        tightened_box=tightened_box,
        halfspace_count=len(halfspaces),
        feasible_vertex_count=vertex_count,
    )
