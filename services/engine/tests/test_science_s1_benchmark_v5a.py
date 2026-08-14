from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v5a import run_benchmark_v5a


def test_v5a_tiny_benchmark_is_reproducible_and_keeps_banks_separate() -> None:
    arguments = {
        "feature_dimensions": (2,),
        "query_counts": (1,),
        "policies": ("random", "population_score_regret"),
        "seeds": (0,),
        "candidate_count": 4,
        "decision_count": 6,
        "reference_difference_count": 7,
        "heldout_count": 8,
        "top_k": 2,
    }

    first = run_benchmark_v5a(**arguments)
    second = run_benchmark_v5a(**arguments)

    assert first == second
    assert first["benchmark_version"] == "s1-population-ranking-benchmark-v5a"
    assert first["config"]["decision_bank_is_separate_from_heldout"] is True
    assert first["config"]["reference_differences_are_separate_from_heldout"] is True
    assert first["config"]["reference_difference_distribution"] == "Normal(0, 2 I)"
    assert len(first["cells"]) == 2
    assert len(first["raw_runs"]) == 2

    runs_by_policy = {run["policy"]: run for run in first["raw_runs"]}
    assert runs_by_policy["random"]["acquisition_score_mean"] is None
    ranking_run = runs_by_policy["population_score_regret"]
    assert ranking_run["acquisition_score_mean"] is not None
    assert ranking_run["ranking_metrics"]["pair_count"] == 28
    assert 0.0 <= ranking_run["ranking_metrics"]["ordering_error_rate"] <= 1.0
    assert 0.0 <= ranking_run["ranking_metrics"]["probability_regret"] <= 1.0
