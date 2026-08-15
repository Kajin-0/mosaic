from __future__ import annotations

import pytest

from mosaic_engine.science_s1 import acceptance_probability
from mosaic_engine.science_s1_benchmark_v13c import _alpha_from_angle
from mosaic_engine.science_s1_benchmark_v13g import (
    THETA_CHALLENGER,
    _theta_challenger_current_set,
    _theta_challenger_probabilities,
    run_benchmark_v13g,
)
from mosaic_engine.science_s1_eprocess import one_step_e_expectation


def test_theta_challenger_excludes_candidate_null_from_mle_face() -> None:
    parameters = tuple(_alpha_from_angle(angle) for angle in (0.0, 90.0, 180.0))
    features = (1.0, 0.0)
    probabilities = _theta_challenger_probabilities(
        (0.0, -1.0, -2.0),
        parameters,
        features,
    )

    assert probabilities[0] == pytest.approx(
        acceptance_probability(parameters[1], features)
    )
    assert probabilities[1] == pytest.approx(
        acceptance_probability(parameters[0], features)
    )
    assert probabilities[2] == pytest.approx(
        acceptance_probability(parameters[0], features)
    )


def test_theta_challenger_is_normalized_predictable_e_increment_for_every_null() -> None:
    parameters = tuple(_alpha_from_angle(angle) for angle in (0.0, 90.0, 180.0, 270.0))
    features = (0.6, -0.8)
    probabilities = _theta_challenger_probabilities(
        (0.0, -0.4, -0.9, -0.4),
        parameters,
        features,
    )

    for parameter, probability in zip(parameters, probabilities, strict=True):
        assert 0.0 < probability < 1.0
        assert one_step_e_expectation(
            parameter,
            features,
            predictive_probability=probability,
        ) == pytest.approx(1.0, abs=1e-12)


def test_theta_specific_current_set_uses_candidate_specific_cutoffs() -> None:
    retained = _theta_challenger_current_set(
        (-3.0, -5.0, -2.0),
        (-4.0, -6.5, -5.5),
        alpha_level=0.05,
    )
    assert retained == (0, 1)


def test_v13g_small_run_has_no_geometric_violation() -> None:
    result = run_benchmark_v13g(
        seeds=(448, 449),
        true_angles_degrees=(0.0, 30.0),
        max_observations=20,
    )

    assert result["benchmark_version"] == "s1-theta-challenger-benchmark-v13g"
    assert result["config"]["theta_specific_predictor"] == THETA_CHALLENGER
    assert len(result["paths"]) == 4
    for summary in result["summaries"]:
        assert summary["geometry_violations"] == 0
        assert 0.0 <= summary["stop_rate"] <= 1.0
