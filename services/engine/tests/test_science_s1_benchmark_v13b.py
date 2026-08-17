from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v13b import run_benchmark_v13b


def test_v13b_small_benchmark_shape_and_geometric_stop_semantics() -> None:
    result = run_benchmark_v13b(
        seeds=(0, 1),
        target_errors=(0.25, 0.15),
        max_observations=12,
        candidate_count=8,
    )

    assert result["benchmark_version"] == "s1-finite-confidence-geometry-benchmark-v13b"
    assert result["method_version"] == "prequential-finite-confidence-radius-v1"
    assert len(result["angle_cells"]) == 24
    assert len(result["paths"]) == 48
    assert len(result["aggregate_target_summaries"]) == 2

    for path in result["paths"]:
        assert path["final_confidence_size"] >= 1
        stops = path["stops"]
        for target in ("0.25", "0.15"):
            stop = stops[target]
            if stop is None:
                continue
            assert stop["certified_radius"] <= float(target)
            if stop["true_in_confidence_set"]:
                assert stop["true_directional_error"] <= stop["certified_radius"] + 1e-12
                assert not stop["false_stop"]


def test_v13b_rejects_invalid_configuration() -> None:
    try:
        run_benchmark_v13b(seeds=())
    except ValueError as error:
        assert "seeds" in str(error)
    else:
        raise AssertionError("expected empty seeds to fail")

    try:
        run_benchmark_v13b(seeds=(0,), target_errors=(0.5,))
    except ValueError as error:
        assert "target_errors" in str(error)
    else:
        raise AssertionError("expected invalid target to fail")
