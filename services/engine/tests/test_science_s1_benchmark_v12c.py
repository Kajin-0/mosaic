from typing import cast

from mosaic_engine.science_s1_benchmark_v12c import run_benchmark_v12c


def test_v12c_small_benchmark_shape_and_radial_semantics() -> None:
    result = run_benchmark_v12c(
        feature_dimensions=(2,),
        slope_norms=(0.9,),
        target_errors=(0.30, 0.20),
        seeds=(192, 193),
        candidate_count=6,
        posterior_samples=32,
    )

    assert result["benchmark_version"] == "s1-radial-stopping-benchmark-v12c"
    assert result["stopping_version"] == "laplace-radial-debiased-angular-v3"
    paths = cast(list[dict[str, object]], result["paths"])
    cells = cast(list[dict[str, object]], result["cells"])
    assert len(paths) == 2
    assert len(cells) == 1

    cell = cells[0]
    assert cell["feature_dimension"] == 2
    assert cell["slope_norm"] == 0.9
    summaries = cast(list[dict[str, object]], cell["rule_summaries"])
    assert len(summaries) == 6

    for path in paths:
        checkpoints = cast(list[dict[str, object]], path["checkpoints"])
        assert len(checkpoints) == 5
        assert [checkpoint["query_count"] for checkpoint in checkpoints] == [3, 6, 9, 12, 15]
        for checkpoint in checkpoints:
            raw = cast(dict[str, object], checkpoint["raw_directional_risk"])
            corrected = cast(
                dict[str, object],
                checkpoint["radial_debiased_directional_risk"],
            )
            radial = cast(dict[str, object], checkpoint["posterior_radial_signal"])
            assert 0.0 <= float(cast(float, raw["upper_error"])) <= 1.0
            assert 0.0 <= float(cast(float, corrected["upper_error"])) <= 1.0
            assert float(cast(float, radial["debiased_norm"])) <= float(
                cast(float, radial["raw_norm"])
            )
            assert float(cast(float, corrected["slope_norm"])) == float(
                cast(float, radial["debiased_norm"])
            )

    gate = cast(dict[str, object], result["primary_gate"])
    assert gate["primary_rule"] == "radial_debiased_two_consecutive"
    assert gate["aggregate_wilson_upper_gate"] == 0.05


def test_v12c_rejects_nonfresh_seed() -> None:
    try:
        run_benchmark_v12c(
            feature_dimensions=(2,),
            slope_norms=(0.9,),
            target_errors=(0.2,),
            seeds=(191,),
            candidate_count=6,
            posterior_samples=8,
        )
    except ValueError as error:
        assert "disjoint" in str(error)
    else:
        raise AssertionError("expected reused v12 seed to fail")
