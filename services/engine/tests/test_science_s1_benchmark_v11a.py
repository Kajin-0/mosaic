from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v11a import (
    BENCHMARK_VERSION,
    PAIR_SCHEDULE_VERSION,
    QUERY_DESIGN_VERSION,
    run_benchmark_v11a,
)


def test_v11a_signal_scaling_benchmark_records_iso_eta_cells() -> None:
    result = run_benchmark_v11a(
        feature_dimensions=(2,),
        slope_norms=(0.75, 0.9),
        eta_targets=(0.5,),
        seeds=(0, 1),
        candidate_count=6,
        heldout_count=12,
        top_k=3,
    )

    assert result["benchmark_version"] == BENCHMARK_VERSION
    assert result["query_design_version"] == QUERY_DESIGN_VERSION
    assert result["pair_schedule_version"] == PAIR_SCHEDULE_VERSION
    assert len(result["cells"]) == 2
    assert len(result["raw_runs"]) == 4
    assert len(result["collapse_groups"]) == 1

    for diagnostic in result["query_design_diagnostics"]:
        assert diagnostic["maximum_absolute_feature_mean"] < 1e-12
        assert diagnostic["maximum_absolute_gram_error"] < 1e-12

    for cell in result["cells"]:
        assert cell["eta_target"] == pytest.approx(0.5)
        assert cell["realized_eta"] > 0.0
        assert cell["runs"] == 2
        assert cell["policy"] == PAIR_SCHEDULE_VERSION
        assert cell["complete_matching_rounds"] >= 0
        assert 0 <= cell["partial_matching_pairs"] < 3
        assert cell["partial_round_endpoint_count"] == 2 * cell["partial_matching_pairs"]
        assert 0.0 <= cell["false_direction_rate"] <= 1.0

    collapse = result["collapse_groups"][0]
    assert collapse["feature_dimension"] == 2
    assert collapse["eta_target"] == pytest.approx(0.5)
    assert collapse["slope_norms"] == [0.75, 0.9]
    assert collapse["observed_mean_error_range"] >= 0.0


def test_v11a_rejects_eta_target_beyond_finite_pair_support() -> None:
    with pytest.raises(ValueError):
        run_benchmark_v11a(
            feature_dimensions=(2,),
            slope_norms=(0.55,),
            eta_targets=(1.5,),
            seeds=(0,),
            candidate_count=6,
            heldout_count=8,
            top_k=2,
        )
