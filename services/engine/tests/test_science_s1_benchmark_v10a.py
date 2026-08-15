from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v10a import (
    BENCHMARK_VERSION,
    FIXED_SLOPE_NORM,
    POLICY,
    QUERY_DESIGN_VERSION,
    run_benchmark_v10a,
)


def test_v10a_fixed_signal_passive_benchmark_records_theory_and_geometry() -> None:
    result = run_benchmark_v10a(
        feature_dimensions=(2,),
        kappa_targets=(2.0,),
        seeds=(0, 1),
        candidate_count=6,
        heldout_count=12,
        top_k=3,
    )

    assert result["benchmark_version"] == BENCHMARK_VERSION
    assert result["query_design_version"] == QUERY_DESIGN_VERSION
    assert result["config"]["policy"] == POLICY
    assert len(result["raw_runs"]) == 2
    assert len(result["cells"]) == 1
    assert len(result["query_design_diagnostics"]) == 2

    for diagnostic in result["query_design_diagnostics"]:
        assert diagnostic["maximum_absolute_feature_mean"] < 1e-12
        assert diagnostic["maximum_absolute_gram_error"] < 1e-12

    for run in result["raw_runs"]:
        assert run["policy"] == "random"
        assert run["true_slope_norm"] == pytest.approx(FIXED_SLOPE_NORM)
        assert (
            run["gaussian_logistic_directional_information_coordinate"]
            < run["boundary_directional_information_coordinate"]
        )
        assert 0.0 <= run["gaussian_population_ordering_error"] <= 1.0
        assert isinstance(run["false_direction"], bool)

    cell = result["cells"][0]
    assert cell["runs"] == 2
    assert cell["policy"] == "random"
    assert cell["true_slope_norm"] == pytest.approx(FIXED_SLOPE_NORM)
    assert 0.0 <= cell["false_direction_rate"] <= 1.0
    assert cell["mean_absolute_boundary_law_residual"] >= 0.0
    assert cell["mean_absolute_gaussian_logistic_law_residual"] >= 0.0
    assert cell["mean_absolute_heldout_population_discrepancy"] >= 0.0


def test_v10a_rejects_candidate_bank_too_small_for_dimension() -> None:
    with pytest.raises(ValueError):
        run_benchmark_v10a(
            feature_dimensions=(4,),
            kappa_targets=(2.0,),
            seeds=(0,),
            candidate_count=4,
            heldout_count=8,
            top_k=2,
        )
