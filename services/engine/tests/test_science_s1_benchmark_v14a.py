from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v14a import run_benchmark_v14a


def test_v14a_small_method_validation_has_no_bound_violations() -> None:
    result = run_benchmark_v14a(
        box_count=2,
        grid_size=2,
        include_full_certificates=False,
    )

    assert result["benchmark_version"] == "s1-continuous-bound-validation-v14a"
    box_validation = result["box_validation"]
    assert box_validation["likelihood_enclosure_violations"] == 0
    assert box_validation["cone_lower_bound_violations"] == 0
    assert result["full_certificate_scenarios"] == []


def test_v14a_is_explicitly_method_validation_not_operating_characteristics() -> None:
    result = run_benchmark_v14a(
        box_count=1,
        grid_size=2,
        include_full_certificates=False,
    )

    assert "not a sequential operating-characteristic study" in result["scientific_scope"]
    assert result["config"]["common_alpha"] == 0.005
    assert result["config"]["cone_alpha"] == 0.045
