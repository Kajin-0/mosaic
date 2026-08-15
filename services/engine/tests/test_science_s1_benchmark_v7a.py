from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v7a import (
    pair_query_count,
    realized_kappa,
    run_benchmark_v7a,
)


def test_dimension_normalized_query_schedule_matches_definition() -> None:
    expected = {
        2: {2.0: 3, 4.0: 6, 6.0: 9, 8.0: 12, 12.0: 18},
        4: {2.0: 5, 4.0: 10, 6.0: 15, 8.0: 20, 12.0: 30},
        8: {2.0: 9, 4.0: 18, 6.0: 27, 8.0: 36, 12.0: 54},
        12: {2.0: 13, 4.0: 26, 6.0: 39, 8.0: 52, 12.0: 78},
    }

    for dimension, schedule in expected.items():
        for target, expected_queries in schedule.items():
            queries = pair_query_count(feature_dimension=dimension, kappa_target=target)
            assert queries == expected_queries
            assert realized_kappa(
                feature_dimension=dimension,
                query_count=queries,
            ) == pytest.approx(target)


def test_query_schedule_rejects_nonpositive_inputs() -> None:
    with pytest.raises(ValueError):
        pair_query_count(feature_dimension=0, kappa_target=2.0)
    with pytest.raises(ValueError):
        pair_query_count(feature_dimension=2, kappa_target=0.0)
    with pytest.raises(ValueError):
        realized_kappa(feature_dimension=0, query_count=3)
    with pytest.raises(ValueError):
        realized_kappa(feature_dimension=2, query_count=0)


def test_tiny_benchmark_records_dimension_normalization_and_direction_metrics() -> None:
    result = run_benchmark_v7a(
        feature_dimensions=(2,),
        kappa_targets=(2.0,),
        policies=("random", "exact_gaussian_score_regret"),
        seeds=(0,),
        candidate_count=6,
        heldout_count=12,
        top_k=3,
    )

    assert result["benchmark_version"] == "s1-sample-complexity-benchmark-v7a"
    assert len(result["cells"]) == 2
    assert len(result["raw_runs"]) == 2

    for cell in result["cells"]:
        assert cell["feature_dimension"] == 2
        assert cell["parameter_count"] == 3
        assert cell["query_count"] == 3
        assert cell["binary_observation_count"] == 6
        assert cell["realized_kappa"] == pytest.approx(2.0)
        assert cell["convergence_rate"] == pytest.approx(1.0)
        direction = cell["direction_metrics"]
        assert set(direction) == {
            "slope_angle_radians",
            "slope_cosine",
            "slope_signal_to_uncertainty",
        }
        assert -1.0 <= direction["slope_cosine"]["mean"] <= 1.0
        assert 0.0 <= direction["slope_angle_radians"]["mean"] <= pytest.approx(3.141592653589793)

    for raw in result["raw_runs"]:
        assert raw["binary_observation_count"] == 2 * raw["query_count"]
        assert raw["realized_kappa"] == pytest.approx(
            raw["binary_observation_count"] / raw["parameter_count"]
        )
