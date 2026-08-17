from __future__ import annotations

from math import log

import pytest

from mosaic_engine.science_s1_benchmark_v13c import _alpha_from_angle
from mosaic_engine.science_s1_benchmark_v13i import (
    LOCAL_NEIGHBOR,
    _local_neighbor_log_joint_numerators,
    _local_neighbor_predictive_probabilities,
    _neighbor_indices,
    run_benchmark_v13i,
)
from mosaic_engine.science_s1_eprocess import binary_log_probability, one_step_e_expectation


def test_neighbor_indices_wrap_circular_grid() -> None:
    assert _neighbor_indices(0, 72) == (71, 1)
    assert _neighbor_indices(71, 72) == (70, 0)
    assert _neighbor_indices(30, 72) == (29, 31)


def test_local_neighbor_predictive_is_valid_e_increment_for_every_null() -> None:
    parameters = tuple(_alpha_from_angle(angle) for angle in (0.0, 90.0, 180.0, 270.0))
    features = (0.35, -0.7)
    probabilities = _local_neighbor_predictive_probabilities(
        (0.0, -0.3, -0.8, -0.1),
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


def test_local_neighbor_predictive_matches_joint_mixture_recurrence() -> None:
    parameters = tuple(_alpha_from_angle(angle) for angle in (0.0, 90.0, 180.0, 270.0))
    features = (0.4, 0.9)
    prior_log_likelihoods = [0.0, -0.4, -1.1, -0.2]
    prior_log_q = _local_neighbor_log_joint_numerators(prior_log_likelihoods)
    probabilities = _local_neighbor_predictive_probabilities(
        prior_log_likelihoods,
        parameters,
        features,
    )

    accepted = True
    updated = [
        log_likelihood + binary_log_probability(parameter, features, accepted)
        for log_likelihood, parameter in zip(prior_log_likelihoods, parameters, strict=True)
    ]
    updated_log_q = _local_neighbor_log_joint_numerators(updated)

    for index, probability in enumerate(probabilities):
        assert updated_log_q[index] - prior_log_q[index] == pytest.approx(log(probability))


def test_v13i_small_run_preserves_geometry() -> None:
    result = run_benchmark_v13i(
        seeds=(576, 577),
        true_angles_degrees=(0.0, 30.0),
        horizons=(10, 20),
    )

    assert result["benchmark_version"] == "s1-local-neighbor-benchmark-v13i"
    assert result["config"]["candidate"] == LOCAL_NEIGHBOR
    assert len(result["paths"]) == 4
    for summary in result["summaries"]:
        assert summary["geometry_violations"] == 0
        assert 0.0 <= summary["stop_rate"] <= 1.0
