from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v13d import (
    OPERATIONAL_PREDICTORS,
    _alpha_from_angle,
    _likelihood_weighted_probability,
    _mle_face_predictive_probability,
    _snml_predictive_probability,
    run_benchmark_v13d,
)


def test_predictable_numerators_return_valid_binary_probabilities() -> None:
    parameters = tuple(_alpha_from_angle(float(angle)) for angle in range(0, 360, 30))
    log_likelihoods = tuple(-0.17 * index for index in range(len(parameters)))
    features = (0.6, -0.8)

    probabilities = (
        _mle_face_predictive_probability(log_likelihoods, parameters, features),
        _snml_predictive_probability(log_likelihoods, parameters, features),
        _likelihood_weighted_probability(
            log_likelihoods,
            parameters,
            features,
            tuple(range(2, 9)),
        ),
    )

    for probability in probabilities:
        assert 0.0 < probability < 1.0


def test_mle_face_preserves_initial_rotational_symmetry() -> None:
    parameters = tuple(_alpha_from_angle(float(angle)) for angle in range(0, 360, 30))
    probability = _mle_face_predictive_probability(
        (0.0,) * len(parameters),
        parameters,
        (1.0, 0.0),
    )

    assert probability == pytest.approx(0.5, abs=1e-12)


def test_v13d_small_run_uses_common_paths_and_reports_oracle_regret() -> None:
    result = run_benchmark_v13d(
        seeds=(64, 65),
        true_angles_degrees=(0.0, 30.0),
        horizons=(8, 12),
    )

    assert result["benchmark_version"] == "s1-numerator-efficiency-benchmark-v13d"
    config = result["config"]
    assert config["operational_predictors"] == OPERATIONAL_PREDICTORS
    assert config["oracle_predictor"] == "oracle_true"

    paths = result["paths"]
    assert len(paths) == 4
    for path in paths:
        log_q = path["log_q_at_horizon"]
        assert set(log_q) == set(OPERATIONAL_PREDICTORS) | {"oracle_true"}
        for predictor in log_q:
            assert set(log_q[predictor]) == {"8", "12"}

    summaries = result["predictor_summaries"]
    assert len(summaries) == (len(OPERATIONAL_PREDICTORS) + 1) * 2
    oracle = [item for item in summaries if item["predictor"] == "oracle_true"]
    assert len(oracle) == 2
    for summary in oracle:
        assert summary["predictive_regret_vs_oracle"]["mean_log_loss_excess"] == pytest.approx(0.0)
        assert summary["true_excluded_ever_rate"] == pytest.approx(0.0)
