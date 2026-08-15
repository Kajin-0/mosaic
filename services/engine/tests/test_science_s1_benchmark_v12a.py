from mosaic_engine.science_s1_benchmark_v12a import run_benchmark_v12a


def test_v12a_small_benchmark_shape_and_stop_semantics() -> None:
    result = run_benchmark_v12a(
        feature_dimensions=(2,),
        slope_norms=(0.9,),
        target_errors=(0.30, 0.20),
        seeds=(0, 1),
        candidate_count=6,
        posterior_samples=32,
    )

    assert result["benchmark_version"] == "s1-stopping-calibration-benchmark-v12a"
    assert result["stopping_version"] == "laplace-angular-q95-v1"
    assert len(result["paths"]) == 2
    assert len(result["cells"]) == 1

    cell = result["cells"][0]
    assert cell["feature_dimension"] == 2
    assert cell["slope_norm"] == 0.9
    assert len(cell["target_summaries"]) == 2

    for path in result["paths"]:
        assert len(path["checkpoints"]) == 5
        query_counts = [checkpoint["query_count"] for checkpoint in path["checkpoints"]]
        assert query_counts == [3, 6, 9, 12, 15]
        for checkpoint in path["checkpoints"]:
            risk = checkpoint["posterior_directional_risk"]
            assert 0.0 <= risk["mean_error"] <= 1.0
            assert 0.0 <= risk["upper_error"] <= 1.0
            assert risk["upper_error"] >= risk["mean_error"]

    for summary in cell["target_summaries"]:
        assert 0.0 <= summary["stop_rate"] <= 1.0
        assert 0.0 <= summary["false_stop_rate"] <= 1.0
        assert 0.0 <= summary["false_stop_given_stop"] <= 1.0
        assert 0.0 <= summary["missed_stop_at_cap_rate"] <= 1.0


def test_v12a_rejects_invalid_target_error() -> None:
    try:
        run_benchmark_v12a(
            feature_dimensions=(2,),
            slope_norms=(0.9,),
            target_errors=(0.5,),
            seeds=(0,),
            candidate_count=6,
            posterior_samples=8,
        )
    except ValueError as error:
        assert "target errors" in str(error)
    else:
        raise AssertionError("expected invalid target error to fail")
