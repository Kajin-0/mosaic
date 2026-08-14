from __future__ import annotations

import pytest

from mosaic_engine.science_s1_decision_acquisition import (
    choose_expected_top_k_value_pair,
    expected_top_k_value_of_information,
    linear_bayes_pair_outcomes,
    pair_predictive_moments,
    top_k_posterior_value,
)
from mosaic_engine.science_s1_simulation import LaplacePosterior


def _posterior(
    *,
    mean: tuple[float, ...],
    covariance: tuple[tuple[float, ...], ...],
) -> LaplacePosterior:
    dimension = len(mean)
    precision = tuple(
        tuple(1.0 if row == column else 0.0 for column in range(dimension))
        for row in range(dimension)
    )
    return LaplacePosterior(
        mean=mean,
        covariance=covariance,
        precision=precision,
        converged=True,
        iterations=1,
    )


def test_pair_predictive_moments_obey_binary_probability_bounds() -> None:
    posterior = _posterior(
        mean=(0.1, 0.4, -0.3),
        covariance=((1.0, 0.1, 0.0), (0.1, 0.8, 0.2), (0.0, 0.2, 0.7)),
    )

    moments = pair_predictive_moments(posterior, (1.2, -0.4), (-0.5, 0.9))

    lower = max(0.0, moments.probability_a + moments.probability_b - 1.0)
    upper = min(moments.probability_a, moments.probability_b)
    assert 0.0 <= moments.probability_a <= 1.0
    assert 0.0 <= moments.probability_b <= 1.0
    assert lower <= moments.probability_both <= upper
    assert moments.covariance[0][1] == pytest.approx(moments.covariance[1][0])


def test_zero_parameter_uncertainty_makes_binary_responses_independent() -> None:
    posterior = _posterior(
        mean=(0.2, -0.3),
        covariance=((0.0, 0.0), (0.0, 0.0)),
    )

    moments = pair_predictive_moments(posterior, (1.0,), (-2.0,))

    assert moments.probability_both == pytest.approx(
        moments.probability_a * moments.probability_b,
        rel=1e-12,
        abs=1e-12,
    )
    assert moments.covariance[0][1] == pytest.approx(0.0, abs=1e-12)


def test_linear_bayes_outcome_probabilities_sum_to_one() -> None:
    posterior = _posterior(
        mean=(0.0, 0.2, -0.1),
        covariance=((1.5, 0.1, 0.0), (0.1, 1.0, 0.2), (0.0, 0.2, 0.9)),
    )

    outcomes = linear_bayes_pair_outcomes(posterior, (0.8, -0.4), (-0.2, 1.1))

    assert len(outcomes) == 4
    assert sum(outcome.probability for outcome in outcomes) == pytest.approx(1.0)
    assert all(outcome.probability >= 0.0 for outcome in outcomes)


def test_linear_bayes_mean_obeys_predictive_martingale_property() -> None:
    posterior = _posterior(
        mean=(0.15, -0.25, 0.4),
        covariance=((1.2, 0.1, 0.05), (0.1, 0.9, 0.1), (0.05, 0.1, 0.7)),
    )

    outcomes = linear_bayes_pair_outcomes(posterior, (1.0, 0.2), (-0.4, 0.9))

    expected_mean = tuple(
        sum(outcome.probability * outcome.mean[index] for outcome in outcomes)
        for index in range(len(posterior.mean))
    )
    assert expected_mean == pytest.approx(posterior.mean, abs=1e-10)


def test_linear_bayes_covariance_contracts_on_the_diagonal() -> None:
    posterior = _posterior(
        mean=(0.0, 0.0, 0.0),
        covariance=((2.0, 0.1, 0.0), (0.1, 1.5, 0.2), (0.0, 0.2, 1.0)),
    )

    outcomes = linear_bayes_pair_outcomes(posterior, (1.0, -0.3), (-0.5, 1.1))
    updated = outcomes[0].covariance

    for index in range(len(posterior.mean)):
        assert 0.0 <= updated[index][index] <= posterior.covariance[index][index] + 1e-12
    for outcome in outcomes[1:]:
        assert outcome.covariance == pytest.approx(updated)


def test_top_k_posterior_value_is_bounded_probability_average() -> None:
    mean = (0.0, 0.7, -0.4)
    covariance = ((0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.5))
    decision_features = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (-1.0, -1.0))

    value = top_k_posterior_value(mean, covariance, decision_features, top_k=2)

    assert 0.0 <= value <= 1.0


def test_zero_uncertainty_has_zero_value_of_information() -> None:
    posterior = _posterior(
        mean=(0.0, 0.5, -0.2),
        covariance=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    )
    decision_features = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (-1.0, 0.5))

    value = expected_top_k_value_of_information(
        posterior,
        (0.8, -0.4),
        (-0.2, 1.1),
        decision_features,
        top_k=2,
    )

    assert value == pytest.approx(0.0, abs=1e-12)


def test_expected_top_k_value_policy_returns_a_valid_remaining_pair() -> None:
    posterior = _posterior(
        mean=(0.0, 0.0, 0.0),
        covariance=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    )
    candidates = ((1.5, 0.0), (0.0, 1.5), (-1.0, 0.2), (0.2, -1.0))
    remaining = ((0, 1), (0, 2), (1, 3))
    decision_features = ((1.0, 0.0), (0.0, 1.0), (0.8, 0.8), (-0.8, -0.8))

    pair = choose_expected_top_k_value_pair(
        remaining,
        candidates,
        posterior,
        decision_features,
        top_k=2,
    )

    assert pair in remaining
