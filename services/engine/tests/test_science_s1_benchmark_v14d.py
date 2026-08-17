from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import _synthetic_observations
from mosaic_engine.science_s1_benchmark_v14d import (
    _halfspace_probe_theta,
    _trace_side,
)
from mosaic_engine.science_s1_continuous_geometry import (
    ParameterBox,
    _cone_halfspaces,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)


def test_halfspace_probe_uses_box_corner_that_minimizes_violation_halfspace() -> None:
    box = ParameterBox(
        (
            (Fraction(-1), Fraction(3)),
            (Fraction(-2), Fraction(4)),
            (Fraction(-5), Fraction(6)),
        )
    )
    halfspace = (Fraction(1, 2), Fraction(-1))

    probe = _halfspace_probe_theta(box, halfspace)

    assert probe == (Fraction(1), Fraction(-2), Fraction(6))
    assert halfspace[0] * probe[1] + halfspace[1] * probe[2] == Fraction(-7)


def test_trace_side_reports_attribution_without_changing_small_search_budget() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.2, 0.0),
        repeats=20,
        seed=14_601,
    )
    cutoff = common_log_likelihood_cutoff_lower(observations)
    box = initial_nuisance_box(observations, common_cutoff_lower=cutoff)
    assert box is not None
    halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[0]

    result = _trace_side(
        observations,
        box,
        halfspace,
        method="grouped",
        max_nodes=3,
        min_width=0.5,
    )

    assert 1 <= result["nodes_visited"] <= 3
    assert result["terminal_reason"] in {
        "node_limit",
        "resolution_limit",
        "all_violating_boxes_pruned",
    }
    counts = result["counts"]
    assert isinstance(counts, dict)
    assert set(counts) == {
        "geometry_prune",
        "common_prune",
        "cone_prune",
        "split",
        "resolution_unresolved",
        "degenerate_unresolved",
    }
