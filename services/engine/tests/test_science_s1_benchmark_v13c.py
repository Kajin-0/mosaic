from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v13c import run_benchmark_v13c


def test_v13c_small_benchmark_shape_and_quantized_radius() -> None:
    result = run_benchmark_v13c(
        grid_spacings_degrees=(30.0, 15.0),
        true_angles_degrees=(0.0, 90.0, 180.0, 270.0),
        horizons=(6, 12),
        seeds=(0, 1),
        target_error=0.20,
        candidate_count=8,
    )

    assert result["benchmark_version"] == "s1-resolution-horizon-benchmark-v13c"
    assert result["method_version"] == "prequential-finite-confidence-radius-v1"
    assert len(result["grid_cells"]) == 2

    coarse, fine = result["grid_cells"]
    assert coarse["grid_spacing_degrees"] == 30.0
    assert coarse["parameter_count"] == 12
    assert coarse["target_degrees"] == 36.0
    assert coarse["effective_grid_radius_degrees"] == 30.0
    assert fine["grid_spacing_degrees"] == 15.0
    assert fine["parameter_count"] == 24
    assert fine["effective_grid_radius_degrees"] == 30.0

    for cell in result["grid_cells"]:
        assert cell["runs"] == 8
        assert len(cell["horizon_summaries"]) == 2
        earlier, later = cell["horizon_summaries"]
        assert earlier["horizon"] == 6
        assert later["horizon"] == 12
        assert earlier["stop_rate"] <= later["stop_rate"]
        assert earlier["true_excluded_ever_rate"] <= later["true_excluded_ever_rate"]


def test_v13c_rejects_truth_not_on_every_grid() -> None:
    try:
        run_benchmark_v13c(
            grid_spacings_degrees=(30.0,),
            true_angles_degrees=(15.0,),
            horizons=(4,),
            seeds=(0,),
            candidate_count=8,
        )
    except ValueError as error:
        assert "true angles" in str(error)
    else:
        raise AssertionError("expected off-grid truth to fail")


def test_v13c_rejects_invalid_grid_spacing() -> None:
    try:
        run_benchmark_v13c(
            grid_spacings_degrees=(17.0,),
            true_angles_degrees=(0.0,),
            horizons=(4,),
            seeds=(0,),
            candidate_count=8,
        )
    except ValueError as error:
        assert "divide 360" in str(error)
    else:
        raise AssertionError("expected nondividing grid spacing to fail")
