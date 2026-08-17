from decimal import Decimal
from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import _synthetic_observations
from mosaic_engine.science_s1_benchmark_v14f import (
    ConePenaltyDiagnostic,
    _cone_lower_bound_with_penalties,
    _ratio_lower_bound_with_penalties,
    _sensitivity_split_dimension,
)
from mosaic_engine.science_s1_continuous_geometry import ParameterBox
from mosaic_engine.science_s1_continuous_geometry_coupled import (
    grouped_coupled_cone_log_e_lower_bound,
    grouped_log_likelihood_ratio_lower_bound,
)
from mosaic_engine.science_s1_continuous_geometry_grouped import prepare_grouped_likelihood


def _test_box() -> ParameterBox:
    return ParameterBox(
        (
            (Fraction(-1, 2), Fraction(1, 2)),
            (Fraction(1, 4), Fraction(3, 2)),
            (Fraction(-3, 4), Fraction(1, 2)),
        )
    )


def test_ratio_penalty_diagnostic_preserves_production_lower_bound() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.2, 0.0),
        repeats=2,
        seed=14_601,
    )
    prepared = prepare_grouped_likelihood(observations)
    box = _test_box()

    diagnostic = _ratio_lower_bound_with_penalties(
        box,
        prepared,
        rotation_degrees=60.0,
    )
    production = grouped_log_likelihood_ratio_lower_bound(
        box,
        prepared,
        rotation_degrees=60.0,
    )

    assert diagnostic.lower_bound == production
    assert all(value >= 0 for value in diagnostic.axis_penalties)


def test_cone_penalty_diagnostic_preserves_production_cone_lower_bound() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.2, 0.0),
        repeats=2,
        seed=14_601,
    )
    prepared = prepare_grouped_likelihood(observations)
    box = _test_box()

    diagnostic = _cone_lower_bound_with_penalties(box, prepared)
    production = grouped_coupled_cone_log_e_lower_bound(box, prepared)

    assert diagnostic.log_e_lower_bound == production


def test_sensitivity_split_uses_largest_best_rotation_penalty() -> None:
    box = _test_box()
    diagnostic = ConePenaltyDiagnostic(
        log_e_lower_bound=Decimal(0),
        best_rotation_degrees=60.0,
        axis_penalties=(Decimal("1.0"), Decimal("7.0"), Decimal("3.0")),
    )

    assert _sensitivity_split_dimension(box, diagnostic) == 1
