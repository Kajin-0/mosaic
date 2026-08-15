from typing import cast

from mosaic_engine.science_s1_benchmark_v12e import run_benchmark_v12e


def test_v12e_small_benchmark_shape_and_tangent_semantics() -> None:
    result = run_benchmark_v12e(
        feature_dimensions=(2,),
        slope_norms=(0.9,),
        target_errors=(0.30, 0.20),
        seeds=(448, 449),
        candidate_count=6,
        posterior_samples=32,
    )

    assert result["benchmark_version"] == "s1-tangent-stopping-benchmark-v12e"
    assert result["stopping_version"] == "laplace-transverse-tangent-angular-v5"
    paths = cast(list[dict[str, object]], result["paths"])
    cells = cast(list[dict[str, object]], result["cells"])
    assert len(paths) == 2
    assert len(cells) == 1

    cell = cells[0]
    summaries = cast(list[dict[str, object]], cell["rule_summaries"])
    assert len(summaries) == 8

    for path in paths:
        checkpoints = cast(list[dict[str, object]], path["checkpoints"])
        assert [checkpoint["query_count"] for checkpoint in checkpoints] == [3, 6, 9, 12, 15]
        for checkpoint in checkpoints:
            full_noise = cast(
                dict[str, object],
                checkpoint["transverse_full_noise_directional_risk"],
            )
            tangent = cast(dict[str, object], checkpoint["tangent_directional_risk"])
            signal = cast(dict[str, object], checkpoint["posterior_transverse_signal"])
            expected_norm = float(cast(float, signal["debiased_norm"]))
            assert float(cast(float, full_noise["slope_norm"])) == expected_norm
            assert float(cast(float, tangent["slope_norm"])) == expected_norm
            assert 0.0 <= float(cast(float, tangent["upper_error"])) <= 0.5

    gate = cast(dict[str, object], result["primary_gate"])
    assert gate["primary_rule"] == "tangent_two_consecutive"
    assert gate["aggregate_wilson_upper_gate"] == 0.05


def test_v12e_rejects_reused_seed() -> None:
    try:
        run_benchmark_v12e(
            feature_dimensions=(2,),
            slope_norms=(0.9,),
            target_errors=(0.2,),
            seeds=(447,),
            candidate_count=6,
            posterior_samples=8,
        )
    except ValueError as error:
        assert "disjoint" in str(error)
    else:
        raise AssertionError("expected reused v12 seed to fail")
