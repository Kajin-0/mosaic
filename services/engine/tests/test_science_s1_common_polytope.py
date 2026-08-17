from fractions import Fraction

from mosaic_engine.science_s1_common_polytope import (
    LinearUpperHalfspace,
    certified_common_polytope_outer_box,
    common_score_halfspaces,
    exact_bounding_box_from_halfspaces,
)
from mosaic_engine.science_s1_continuous_geometry import (
    ParameterBox,
    common_log_likelihood_cutoff_lower,
)
from mosaic_engine.science_s1_eprocess import PrequentialBinaryObservation


def _cube_halfspaces() -> tuple[LinearUpperHalfspace, ...]:
    result: list[LinearUpperHalfspace] = []
    for axis in range(3):
        positive = [Fraction(0), Fraction(0), Fraction(0)]
        positive[axis] = Fraction(1)
        result.append(
            LinearUpperHalfspace(
                (positive[0], positive[1], positive[2]),
                Fraction(1),
                f"upper_{axis}",
            )
        )
        negative = [Fraction(0), Fraction(0), Fraction(0)]
        negative[axis] = Fraction(-1)
        result.append(
            LinearUpperHalfspace(
                (negative[0], negative[1], negative[2]),
                Fraction(1),
                f"lower_{axis}",
            )
        )
    return tuple(result)


def _balanced_observations() -> tuple[PrequentialBinaryObservation, ...]:
    observations: list[PrequentialBinaryObservation] = []
    for features in ((1.0, 0.0), (0.0, 1.0), (-1.0, -1.0)):
        observations.append(PrequentialBinaryObservation(features, False, 0.5))
        observations.append(PrequentialBinaryObservation(features, True, 0.5))
    return tuple(observations)


def test_exact_polytope_bounding_box_uses_all_halfspaces() -> None:
    halfspaces = (*_cube_halfspaces(), LinearUpperHalfspace((Fraction(1), Fraction(0), Fraction(0)), Fraction(1, 2), "x_cap"))

    result = exact_bounding_box_from_halfspaces(halfspaces)

    assert result is not None
    box, vertex_count = result
    assert vertex_count == 8
    assert box.intervals == (
        (Fraction(-1), Fraction(1, 2)),
        (Fraction(-1), Fraction(1)),
        (Fraction(-1), Fraction(1)),
    )


def test_one_sided_observation_adds_one_sided_score_constraint() -> None:
    coarse = ParameterBox(
        (
            (Fraction(-10), Fraction(10)),
            (Fraction(-10), Fraction(10)),
            (Fraction(-10), Fraction(10)),
        )
    )
    observations = (PrequentialBinaryObservation((1.0, 0.0), True, 0.5),)

    halfspaces = common_score_halfspaces(
        observations,
        common_cutoff_lower=common_log_likelihood_cutoff_lower(observations),
        coarse_box=coarse,
    )

    assert len(halfspaces) == 7
    assert any(halfspace.source.startswith("accept_") for halfspace in halfspaces)
    assert not any(halfspace.source.startswith("reject_") for halfspace in halfspaces)


def test_balanced_retained_zero_parameter_stays_inside_tightened_outer_box() -> None:
    observations = _balanced_observations()
    cutoff = common_log_likelihood_cutoff_lower(observations)

    result = certified_common_polytope_outer_box(
        observations,
        common_cutoff_lower=cutoff,
    )

    assert result is not None
    for coarse_interval, tight_interval in zip(
        result.coarse_box.intervals,
        result.tightened_box.intervals,
        strict=True,
    ):
        assert coarse_interval[0] <= tight_interval[0] <= 0
        assert 0 <= tight_interval[1] <= coarse_interval[1]
    assert result.halfspace_count == 12
    assert result.feasible_vertex_count > 0
