from __future__ import annotations

from mosaic_engine.science_s1_benchmark_v13a import run_benchmark_v13a


def test_v13a_small_benchmark_shape_and_semantics() -> None:
    result = run_benchmark_v13a(
        seeds=(0, 1),
        max_observations=8,
        candidate_count=8,
    )

    assert result["benchmark_version"] == "s1-finite-null-eprocess-benchmark-v13a"
    assert result["method_version"] == "prequential-finite-composite-null-v1"
    assert len(result["null_cells"]) == 9

    valid = result["valid_null_aggregate"]
    leaky = result["leaky_null_aggregate"]
    alternative = result["alternative_power"]

    assert valid["runs"] == 18
    assert leaky["runs"] == 18
    assert alternative["runs"] == 2

    for summary in (valid, leaky, alternative):
        assert 0.0 <= summary["rejection_rate"] <= 1.0
        assert summary["rejections"] <= summary["runs"]


def test_v13a_rejects_invalid_configuration() -> None:
    try:
        run_benchmark_v13a(seeds=())
    except ValueError as error:
        assert "seeds" in str(error)
    else:
        raise AssertionError("expected empty seeds to fail")

    try:
        run_benchmark_v13a(seeds=(0,), max_observations=0)
    except ValueError as error:
        assert "max_observations" in str(error)
    else:
        raise AssertionError("expected nonpositive observation cap to fail")
