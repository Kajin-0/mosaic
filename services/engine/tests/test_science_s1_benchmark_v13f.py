from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v13f import (
    PREDICTORS,
    _intersection,
    run_benchmark_v13f,
)


def test_intersection_is_order_preserving_subset() -> None:
    assert _intersection((0, 2, 4, 6), (1, 2, 4, 7)) == (2, 4)
    assert _intersection((2, 4), (0, 2, 3, 4, 5)) == (2, 4)


def test_v13f_small_run_preserves_nested_radius_and_stop_dominance() -> None:
    result = run_benchmark_v13f(
        seeds=(320, 321),
        true_angles_degrees=(0.0, 30.0),
        max_observations=30,
    )

    assert result["benchmark_version"] == "s1-nested-confidence-benchmark-v13f"
    assert result["config"]["predictors"] == PREDICTORS
    assert len(result["paths"]) == 4

    for path in result["paths"]:
        for predictor in PREDICTORS:
            assert path["maximum_radius_gap"][predictor] >= 0.0
            current = path["first_stop"][predictor]["current"]
            nested = path["first_stop"][predictor]["nested"]
            if current is not None and nested is not None:
                assert nested["observation_count"] <= current["observation_count"]

    for summary in result["summaries"]:
        assert summary["geometry_violations"] == 0
        assert 0.0 <= summary["stop_rate"] <= 1.0


def test_v13f_uses_fresh_seed_block_by_default() -> None:
    result = run_benchmark_v13f(
        seeds=(320,),
        true_angles_degrees=(0.0,),
        max_observations=2,
    )
    assert result["config"]["seeds"] == (320,)
