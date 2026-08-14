from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v4a import run_benchmark_v4a


def test_v4a_tiny_benchmark_is_reproducible_and_separates_decision_bank() -> None:
    arguments = {
        "feature_dimensions": (2,),
        "query_counts": (1,),
        "policies": ("random", "expected_top_k_evsi"),
        "seeds": (0,),
        "candidate_count": 4,
        "decision_count": 6,
        "heldout_count": 8,
        "top_k": 2,
    }

    first = run_benchmark_v4a(**arguments)
    second = run_benchmark_v4a(**arguments)

    assert first == second
    assert first["benchmark_version"] == "s1-decision-benchmark-v4a"
    assert first["config"]["decision_bank_is_separate_from_heldout"] is True
    assert len(first["cells"]) == 2
    assert len(first["raw_runs"]) == 2

    runs_by_policy = {run["policy"]: run for run in first["raw_runs"]}
    assert runs_by_policy["random"]["decision_score_mean"] is None
    assert runs_by_policy["expected_top_k_evsi"]["decision_score_mean"] is not None
    assert runs_by_policy["expected_top_k_evsi"]["negative_decision_score_count"] >= 0
