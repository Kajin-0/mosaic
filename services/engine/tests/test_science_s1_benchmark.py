from __future__ import annotations

from mosaic_engine.science_s1_benchmark import run_benchmark


def test_small_benchmark_is_reproducible_and_versions_its_scope() -> None:
    arguments = {
        "feature_dimensions": (2,),
        "query_counts": (2,),
        "policies": ("random", "d_optimal"),
        "seeds": (0, 1),
        "candidate_count": 6,
        "heldout_count": 12,
        "top_k": 3,
        "prior_variance": 4.0,
        "slope_scale": 0.9,
        "intercept": 0.0,
    }

    first = run_benchmark(**arguments)
    second = run_benchmark(**arguments)

    assert first == second
    assert first["benchmark_version"] == "s1-ground-truth-benchmark-v1"
    assert first["model_version"] == "visual-acceptance-linear-logit-v1"
    assert "not human or matchmaking validation" in str(first["scientific_scope"])

    cells = first["cells"]
    assert isinstance(cells, list)
    assert len(cells) == 2
    assert {cell["policy"] for cell in cells} == {"random", "d_optimal"}
    assert all(cell["runs"] == 2 for cell in cells)
    assert all(cell["convergence_rate"] == 1.0 for cell in cells)
