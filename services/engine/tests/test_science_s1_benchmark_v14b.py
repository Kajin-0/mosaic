from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v14b import run_benchmark_v14b


def test_v14b_grouped_bound_validation_has_no_one_sided_failures() -> None:
    result = run_benchmark_v14b(include_runtime=False)

    assert result["benchmark_version"] == "s1-grouped-continuous-runtime-v14b"
    validation = result["grouped_bound_validation"]
    assert validation["likelihood_enclosure_violations"] == 0
    assert validation["cone_lower_bound_violations"] == 0
    assert validation["unique_feature_groups"] == 12
    assert result["runtime_scenarios"] == []


def test_v14b_runtime_harness_preserves_certificate_configuration() -> None:
    result = run_benchmark_v14b(include_runtime=False)

    assert result["config"]["node_budget_per_side"] == 40
    assert result["config"]["min_width"] == 0.05
    assert "changes only evaluation strategy" in result["scientific_scope"]
