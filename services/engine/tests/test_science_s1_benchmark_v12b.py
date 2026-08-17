from mosaic_engine.science_s1_benchmark_v12b import run_benchmark_v12b


def test_v12b_small_benchmark_is_fresh_seed_and_compares_three_rules() -> None:
    result = run_benchmark_v12b(
        feature_dimensions=(2,),
        slope_norms=(0.9,),
        target_errors=(0.30,),
        seeds=(64, 65),
        candidate_count=6,
        posterior_samples=32,
    )

    assert result["benchmark_version"] == "s1-stopping-validation-benchmark-v12b"
    assert len(result["paths"]) == 2
    assert len(result["cells"]) == 1
    assert len(result["aggregate_rule_summaries"]) == 3

    summaries = result["cells"][0]["rule_summaries"]
    assert {summary["rule"] for summary in summaries} == {
        "single_crossing",
        "two_consecutive",
        "burnin_90",
    }

    for summary in summaries:
        assert 0.0 <= summary["stop_rate"] <= 1.0
        assert 0.0 <= summary["false_stop_given_stop"] <= 1.0
        interval = summary["false_stop_given_stop_wilson95"]
        assert 0.0 <= interval["lower"] <= interval["upper"] <= 1.0


def test_v12b_rejects_reuse_of_v12a_seed() -> None:
    try:
        run_benchmark_v12b(
            feature_dimensions=(2,),
            slope_norms=(0.9,),
            target_errors=(0.25,),
            seeds=(63,),
            candidate_count=6,
            posterior_samples=8,
        )
    except ValueError as error:
        assert "fresh" in str(error)
    else:
        raise AssertionError("expected reused v12a seed to fail")
