from decimal import Decimal
from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import _synthetic_observations
from mosaic_engine.science_s1_benchmark_v14f import ConePenaltyDiagnostic
from mosaic_engine.science_s1_benchmark_v14g import (
    EvaluatedBox,
    _frontier_priority,
    _run_fair_best_first_side,
)
from mosaic_engine.science_s1_continuous_geometry import (
    ParameterBox,
    _cone_halfspaces,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)


def _unresolved_box(distance: str, width: float) -> EvaluatedBox:
    box = ParameterBox(
        (
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
        )
    )
    diagnostic = ConePenaltyDiagnostic(
        log_e_lower_bound=Decimal(0),
        best_rotation_degrees=30.0,
        axis_penalties=(Decimal(1), Decimal(2), Decimal(3)),
    )
    value = Decimal(distance)
    return EvaluatedBox(
        box=box,
        status="unresolved",
        diagnostic=diagnostic,
        common_survival_margin=value,
        cone_survival_margin=value,
        maximum_width=width,
    )


def test_frontier_priority_prefers_near_prunable_box() -> None:
    near = _unresolved_box("0.2", 2.0)
    far = _unresolved_box("5.0", 0.5)

    assert _frontier_priority(near, serial=1) < _frontier_priority(far, serial=0)


def test_fair_best_first_never_exceeds_bound_evaluation_budget() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.2, 0.0),
        repeats=20,
        seed=14_601,
    )
    cutoff = common_log_likelihood_cutoff_lower(observations)
    box = initial_nuisance_box(observations, common_cutoff_lower=cutoff)
    assert box is not None
    halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[0]

    result = _run_fair_best_first_side(
        observations,
        box,
        halfspace=halfspace,
        evaluation_budget=5,
        min_width=0.05,
    )

    assert result["evaluations"] <= 5
    assert not result["certified"]
    assert result["terminal_reason"] == "evaluation_budget"
