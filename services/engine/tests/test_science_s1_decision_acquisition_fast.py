from __future__ import annotations

import pytest

from mosaic_engine.science_s1 import sigmoid
from mosaic_engine.science_s1_bayesian_acquisition import posterior_mean_acceptance
from mosaic_engine.science_s1_decision_acquisition_fast import (
    choose_expected_top_k_value_pair_approximation,
    logistic_normal_mean_approximation,
)
from mosaic_engine.science_s1_simulation import LaplacePosterior


def _scalar_posterior(mean: float, variance: float) -> LaplacePosterior:
    precision_value = 1.0 / variance if variance > 0.0 else 1.0
    return LaplacePosterior(
        mean=(mean,),
        covariance=((variance,),),
        precision=((precision_value,),),
        converged=True,
        iterations=1,
    )


def test_logistic_normal_approximation_is_exact_at_zero_variance() -> None:
    for mean in (-6.0, -2.0, 0.0, 1.5, 6.0):
        assert logistic_normal_mean_approximation(mean, 0.0) == pytest.approx(sigmoid(mean))


def test_logistic_normal_approximation_stays_close_to_gh9_reference_grid() -> None:
    means = (-6.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 6.0)
    variances = (0.0, 0.1, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
    absolute_errors = []

    for mean in means:
        for variance in variances:
            exact = posterior_mean_acceptance(_scalar_posterior(mean, variance), ())
            approximate = logistic_normal_mean_approximation(mean, variance)
            absolute_errors.append(abs(approximate - exact))

    assert max(absolute_errors) < 0.02


def test_fast_evsi_chooser_returns_score_and_valid_pair() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.0, 0.0),
        covariance=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        precision=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        converged=True,
        iterations=1,
    )
    candidates = ((1.5, 0.0), (0.0, 1.5), (-1.0, 0.2), (0.2, -1.0))
    remaining = ((0, 1), (0, 2), (1, 3))
    decision_features = ((1.0, 0.0), (0.0, 1.0), (0.8, 0.8), (-0.8, -0.8))

    pair, score = choose_expected_top_k_value_pair_approximation(
        remaining,
        candidates,
        posterior,
        decision_features,
        top_k=2,
    )

    assert pair in remaining
    assert score == pytest.approx(score)
