from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import _synthetic_observations
from mosaic_engine.science_s1_benchmark_v14i import _run_active_polytope_side
from mosaic_engine.science_s1_common_polytope import (
    LinearUpperHalfspace,
    box_disjoint_from_halfspace_polytope,
    common_score_halfspaces,
    minimum_linear_form_over_box,
)
from mosaic_engine.science_s1_continuous_geometry import (
    COMMON_ALPHA,
    ParameterBox,
    _cone_halfspaces,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)


def test_exact_box_halfspace_disjointness_uses_linear_minimum() -> None:
    box = ParameterBox(
        (
            (Fraction(2), Fraction(3)),
            (Fraction(-1), Fraction(4)),
            (Fraction(-2), Fraction(5)),
        )
    )
    coefficients = (Fraction(1), Fraction(-2), Fraction(3))
    halfspace = LinearUpperHalfspace(coefficients, Fraction(-1), "test")

    minimum = minimum_linear_form_over_box(box, coefficients)

    assert minimum == Fraction(-21)
    assert not box_disjoint_from_halfspace_polytope(box, (halfspace,))

    excluding = LinearUpperHalfspace(coefficients, Fraction(-22), "exclude")
    assert box_disjoint_from_halfspace_polytope(box, (excluding,))


def test_active_polytope_search_respects_finite_evaluation_budget() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.2, 0.0),
        repeats=20,
        seed=14_601,
    )
    cutoff = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    box = initial_nuisance_box(observations, common_cutoff_lower=cutoff)
    assert box is not None
    halfspaces = common_score_halfspaces(
        observations,
        common_cutoff_lower=cutoff,
        coarse_box=box,
    )
    directional_halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[0]

    result = _run_active_polytope_side(
        observations,
        box,
        halfspaces,
        directional_halfspace=directional_halfspace,
        evaluation_budget=5,
    )

    assert result["evaluations"] <= 5
    assert not result["certified"]
    assert result["terminal_reason"] == "evaluation_budget"
