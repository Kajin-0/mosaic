from __future__ import annotations

from math import log

import pytest

from mosaic_engine.science_s1_benchmark_v13j import (
    CONE_COVER,
    COVER_OFFSETS_DEGREES,
    _cone_cover_current_set,
    _cone_cover_log_joint_numerators,
    _cover_indices,
    run_benchmark_v13j,
)


def test_cone_cover_has_eleven_unique_outside_cone_offsets() -> None:
    indices = _cover_indices(0, 72)
    assert len(indices) == 11
    assert len(set(indices)) == 11
    assert 0 not in indices
    assert COVER_OFFSETS_DEGREES == (-150, -120, -90, -60, -30, 30, 60, 90, 120, 150, 180)


def test_cone_cover_joint_numerator_is_uniform_mixture_over_support() -> None:
    logs = tuple(float(-index) for index in range(72))
    numerators = _cone_cover_log_joint_numerators(logs)
    support = _cover_indices(0, 72)
    expected = log(sum(pow(2.718281828459045, logs[index]) for index in support) / len(support))
    assert numerators[0] == pytest.approx(expected)


def test_cone_cover_current_set_rejects_only_by_candidate_specific_e_threshold() -> None:
    logs = [0.0] * 72
    retained = _cone_cover_current_set(logs, alpha_level=0.05)
    assert retained == tuple(range(72))


def test_v13j_small_run_has_no_geometry_violation() -> None:
    result = run_benchmark_v13j(
        seeds=(704, 705),
        true_angles_degrees=(0.0, 30.0),
        horizons=(20,),
    )
    assert result["benchmark_version"] == "s1-cone-cover-benchmark-v13j"
    assert result["config"]["candidate"] == CONE_COVER
    assert len(result["paths"]) == 4
    for summary in result["summaries"]:
        assert summary["geometry_violations"] == 0
        assert 0.0 <= summary["stop_rate"] <= 1.0
