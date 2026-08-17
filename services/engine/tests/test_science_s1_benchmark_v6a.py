from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v6a import run_benchmark_v6a


def test_v6a_tiny_benchmark_is_reproducible_and_marks_exact_reference() -> None:
    arguments = {
        "feature_dimensions": (2,),
        "query_counts": (1,),
        "policies": ("population_score_regret", "exact_gaussian_score_regret"),
        "seeds": (0,),
        "candidate_count": 4,
        "reference_difference_count": 7,
        "heldout_count": 8,
        "top_k": 2,
    }

    first = run_benchmark_v6a(**arguments)
    second = run_benchmark_v6a(**arguments)

    assert first == second
    assert first["benchmark_version"] == "s1-exact-gaussian-ranking-benchmark-v6a"
    assert first["config"]["reference_difference_distribution"] == "Normal(0, 2 I)"
    assert first["config"]["exact_policy_uses_reference_samples"] is False
    assert first["config"]["raw_runs_retain_selected_pairs"] is True
    assert len(first["cells"]) == 2
    assert len(first["raw_runs"]) == 2

    runs_by_policy = {run["policy"]: run for run in first["raw_runs"]}
    sampled_run = runs_by_policy["population_score_regret"]
    exact_run = runs_by_policy["exact_gaussian_score_regret"]
    assert sampled_run["acquisition_score_mean"] is not None
    assert exact_run["acquisition_score_mean"] is not None
    assert len(sampled_run["selected_pairs"]) == 1
    assert len(exact_run["selected_pairs"]) == 1
    assert exact_run["ranking_metrics"]["pair_count"] == 28
