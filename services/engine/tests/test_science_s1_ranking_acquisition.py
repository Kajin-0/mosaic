from __future__ import annotations

from math import sqrt

import pytest

from mosaic_engine.science_s1_ranking_acquisition import (
    choose_population_score_regret_pair,
    expected_population_score_regret_reduction,
    pairwise_linear_score_regret,
    pairwise_misorder_probability,
    population_ranking_risk,
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


def test_misorder_probability_is_half_at_uncertain_zero_mean() -> None:
    assert pairwise_misorder_probability(0.0, 4.0) == pytest.approx(0.5)


def test_known_pairwise_order_has_zero_ranking_risk() -> None:
    assert pairwise_misorder_probability(2.0, 0.0) == 0.0
    assert pairwise_linear_score_regret(2.0, 0.0) == 0.0
    assert pairwise_linear_score_regret(0.0, 0.0) == 0.0


def test_zero_mean_score_regret_has_closed_form() -> None:
    standard_deviation = 2.5
    expected = standard_deviation / sqrt(2.0 * 3.141592653589793)

    actual = pairwise_linear_score_regret(0.0, standard_deviation**2)

    assert actual == pytest.approx(expected, rel=1e-12)


def test_score_regret_is_symmetric_and_homogeneous() -> None:
    base = pairwise_linear_score_regret(0.7, 1.3)

    assert pairwise_linear_score_regret(-0.7, 1.3) == pytest.approx(base)
    assert pairwise_linear_score_regret(2.1, 9.0 * 1.3) == pytest.approx(3.0 * base)


def test_score_regret_decreases_as_ordering_becomes_more_certain() -> None:
    variance = 1.0

    assert pairwise_linear_score_regret(0.0, variance) > pairwise_linear_score_regret(1.0, variance)
    assert pairwise_linear_score_regret(1.0, variance) > pairwise_linear_score_regret(3.0, variance)


def test_population_risk_ignores_intercept_only_uncertainty() -> None:
    posterior = _posterior(
        mean=(0.0, 0.5, -0.2),
        covariance=((9.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    )
    reference_differences = ((1.0, 0.0), (-0.5, 1.2), (0.3, -0.7))

    misorder, regret = population_ranking_risk(
        posterior.mean,
        posterior.covariance,
        reference_differences,
    )

    assert misorder == 0.0
    assert regret == 0.0


def test_population_risk_is_invariant_to_reversing_every_pair() -> None:
    posterior = _posterior(
        mean=(0.1, 0.5, -0.2),
        covariance=((1.0, 0.0, 0.0), (0.0, 0.8, 0.1), (0.0, 0.1, 0.6)),
    )
    differences = ((1.0, 0.0), (-0.5, 1.2), (0.3, -0.7))
    reversed_differences = tuple(tuple(-value for value in row) for row in differences)

    assert population_ranking_risk(
        posterior.mean,
        posterior.covariance,
        differences,
    ) == pytest.approx(
        population_ranking_risk(
            posterior.mean,
            posterior.covariance,
            reversed_differences,
        )
    )


def test_zero_slope_uncertainty_has_zero_expected_ranking_value_of_information() -> None:
    posterior = _posterior(
        mean=(0.0, 0.5, -0.2),
        covariance=((4.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    )
    reference_differences = ((1.0, 0.0), (-0.5, 1.2), (0.3, -0.7))

    reduction = expected_population_score_regret_reduction(
        posterior,
        (1.0, 0.0),
        (0.0, 1.0),
        reference_differences,
    )

    assert reduction == pytest.approx(0.0, abs=1e-12)


def test_population_regret_chooser_returns_pair_and_score() -> None:
    posterior = _posterior(
        mean=(0.0, 0.0, 0.0),
        covariance=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    )
    candidates = ((1.5, 0.0), (0.0, 1.5), (-1.0, 0.2), (0.2, -1.0))
    remaining = ((0, 1), (0, 2), (1, 3))
    reference_differences = ((1.0, 0.0), (0.0, 1.0), (0.8, -0.8), (-1.2, 0.4))

    pair, score = choose_population_score_regret_pair(
        remaining,
        candidates,
        posterior,
        reference_differences,
    )

    assert pair in remaining
    assert score == pytest.approx(score)
