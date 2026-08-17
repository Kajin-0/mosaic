from typing import cast

from mosaic_engine.science_s1_benchmark_v12d import run_benchmark_v12d


def test_v12d_small_benchmark_shape_and_transverse_semantics() -> None:
    result = run_benchmark_v12d(
        feature_dimensions=(2,),
        slope_norms=(0.9,),
        target_errors=(0.30, 0.20),
        seeds=(320, 321),
        candidate_count=6,
        posterior_samples=32,
    )

    assert result["benchmark_version"] == "s1-transverse-stopping-benchmark-v12d"
    assert result["stopping_version"] == "laplace-transverse-debiased-angular-v4"
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
            raw = cast(dict[str, object], checkpoint["raw_directional_risk"])
            radial = cast(
                dict[str, object],
                checkpoint["radial_debiased_directional_risk"],
            )
            transverse = cast(
                dict[str, object],
                checkpoint["transverse_debiased_directional_risk"],
            )
            radial_signal = cast(dict[str, object], checkpoint["posterior_radial_signal"])
            transverse_signal = cast(
                dict[str, object],
                checkpoint["posterior_transverse_signal"],
            )

            raw_norm = float(cast(float, raw["slope_norm"]))
            radial_norm = float(cast(float, radial["slope_norm"]))
            transverse_norm = float(cast(float, transverse["slope_norm"]))
            assert radial_norm <= transverse_norm <= raw_norm
            assert radial_norm == float(cast(float, radial_signal["debiased_norm"]))
            assert transverse_norm == float(cast(float, transverse_signal["debiased_norm"]))

    gate = cast(dict[str, object], result["primary_gate"])
    assert gate["primary_rule"] == "transverse_debiased_two_consecutive"
    assert gate["aggregate_wilson_upper_gate"] == 0.05


def test_v12d_rejects_reused_seed() -> None:
    try:
        run_benchmark_v12d(
            feature_dimensions=(2,),
            slope_norms=(0.9,),
            target_errors=(0.2,),
            seeds=(319,),
            candidate_count=6,
            posterior_samples=8,
        )
    except ValueError as error:
        assert "disjoint" in str(error)
    else:
        raise AssertionError("expected reused v12 seed to fail")
