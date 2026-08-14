from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v3 import run_benchmark_v3


def test_small_v3_benchmark_is_reproducible_and_retains_raw_runs() -> None:
    arguments = {
        "feature_dimensions": (2,),
        "query_counts": (2,),
        "policies": (
            "random",
            "d_optimal",
            "posterior_fisher_d_optimal",
            "mutual_information_d_optimal",
        ),
        "seeds": (0, 1),
        "candidate_count": 6,
        "heldout_count": 12,
        "top_k": 3,
        "prior_variance": 4.0,
        "slope_scale": 0.9,
        "intercept": 0.0,
    }

    first = run_benchmark_v3(**arguments)
    second = run_benchmark_v3(**arguments)

    assert first == second
    assert first["benchmark_version"] == "s1-ground-truth-benchmark-v3"
    assert first["model_version"] == "visual-acceptance-linear-logit-v1"
    assert "not human or matchmaking validation" in str(first["scientific_scope"])

    cells = first["cells"]
    raw_runs = first["raw_runs"]
    assert isinstance(cells, list)
    assert isinstance(raw_runs, list)
    assert len(cells) == 4
    assert len(raw_runs) == 8
    assert {cell["policy"] for cell in cells} == set(arguments["policies"])
    assert all(cell["convergence_rate"] == 1.0 for cell in cells)
    assert all("excess_log_loss" in cell["metrics"] for cell in cells)
