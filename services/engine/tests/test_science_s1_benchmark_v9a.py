from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v9a import run_benchmark_v9a


def test_tiny_v9a_benchmark_records_gaussian_controlled_geometry() -> None:
    result = run_benchmark_v9a(
        feature_dimensions=(2,),
        kappa_targets=(2.0,),
        policies=("random", "exact_gaussian_score_regret"),
        seeds=(0,),
        candidate_count=6,
        heldout_count=12,
        top_k=3,
    )

    assert result["benchmark_version"] == "s1-gaussian-controlled-geometry-benchmark-v9a"
    assert result["query_design_version"] == "centered-orthogonalized-gaussian-v1"
    assert result["config"]["paired_to_benchmarks"] == (
        "s1-sample-complexity-benchmark-v7a",
        "s1-controlled-geometry-benchmark-v8a",
    )
    assert len(result["cells"]) == 2
    assert len(result["raw_runs"]) == 2

    diagnostics = result["query_design_diagnostics"]
    assert len(diagnostics) == 1
    assert diagnostics[0]["seed"] == 0
    assert diagnostics[0]["candidate_count"] == 6
    assert diagnostics[0]["feature_dimension"] == 2
    assert diagnostics[0]["maximum_absolute_feature_mean"] < 1e-12
    assert diagnostics[0]["maximum_absolute_gram_error"] < 1e-12

    for cell in result["cells"]:
        assert cell["query_design_version"] == "centered-orthogonalized-gaussian-v1"
        assert cell["feature_dimension"] == 2
        assert cell["query_count"] == 3
        assert cell["realized_kappa"] == pytest.approx(2.0)
        assert cell["convergence_rate"] == pytest.approx(1.0)


def test_v9a_requires_more_candidates_than_features() -> None:
    with pytest.raises(ValueError):
        run_benchmark_v9a(
            feature_dimensions=(6,),
            kappa_targets=(2.0,),
            policies=("random",),
            seeds=(0,),
            candidate_count=6,
            heldout_count=12,
            top_k=3,
        )
