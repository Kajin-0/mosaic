from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v13k import (
    HISTORICAL,
    NESTED_COVER,
    run_benchmark_v13k,
)


def test_v13k_small_run_compares_only_acquisition_policy() -> None:
    result = run_benchmark_v13k(
        seeds=(832, 833),
        true_angles_degrees=(0.0, 30.0),
        horizons=(20,),
    )

    assert result["benchmark_version"] == "s1-acquisition-benchmark-v13k"
    assert result["config"]["historical_acquisition"] == HISTORICAL
    assert result["config"]["candidate_acquisition"] == NESTED_COVER
    assert result["config"]["numerator"] == "v13j 11-point outside-cone mixture"
    assert len(result["paths"]) == 8
    comparison = result["paired_comparisons"][0]
    total = (
        comparison["both"]
        + comparison["left_only"]
        + comparison["right_only"]
        + comparison["neither"]
    )
    assert total == 4
    for summary in result["summaries"]:
        assert summary["geometry_violations"] == 0
        assert 0.0 <= summary["stop_rate"] <= 1.0


def test_v13k_fresh_seed_block_starts_after_v13j() -> None:
    result = run_benchmark_v13k(
        seeds=(832,),
        true_angles_degrees=(0.0,),
        horizons=(5,),
    )
    assert result["config"]["seeds"] == (832,)
