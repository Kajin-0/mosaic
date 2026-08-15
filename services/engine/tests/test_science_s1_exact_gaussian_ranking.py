from __future__ import annotations

from math import erfc, exp, pi, sqrt

import pytest

from mosaic_engine.science_s1_exact_gaussian_ranking import (
    choose_exact_gaussian_ranking_pair,
    exact_gaussian_reference_ranking_risk,
    gaussian_expected_norm,
    gaussian_expected_norms,
    isotropic_zero_mean_expected_norm,
)
from mosaic_engine.science_s1_simulation import LaplacePosterior


def _folded_normal_mean(mean: float, standard_deviation: float) -> float:
    if standard_deviation == 0.0:
        return abs(mean)
    absolute_mean = abs(mean)
    standardized = absolute_mean / standard_deviation
    return (
        standard_deviation * sqrt(2.0 / pi) * exp(-0.5 * standardized * standardized)
        + absolute_mean * erfc(-standardized / sqrt(2.0))
        - absolute_mean
    )


@pytest.mark.parametrize("dimension", (1, 2, 4, 8))
def test_centered_isotropic_expected_norm_matches_chi_closed_form(dimension: int) -> None:
    standard_deviation = 1.7
    mean = (0.0,) * dimension
    covariance = tuple(
        tuple(
            standard_deviation**2 if row == column else 0.0 for column in range(dimension)
        )
        for row in range(dimension)
    )

    actual = gaussian_expected_norm(mean, covariance)
    expected = isotropic_zero_mean_expected_norm(
        dimension=dimension,
        standard_deviation=standard_deviation,
    )

    assert actual == pytest.approx(expected, rel=2e-5, abs=2e-5)


@pytest.mark.parametrize(
    ("mean", "standard_deviation"),
    ((0.0, 0.4), (0.7, 0.2), (-1.3, 0.9), (4.0, 2.0)),
)
def test_one_dimensional_expected_norm_matches_folded_normal(
    mean: float,
    standard_deviation: float,
) -> None:
    actual = gaussian_expected_norm((mean,), ((standard_deviation**2,),))
    expected = _folded_normal_mean(mean, standard_deviation)

    assert actual == pytest.approx(expected, rel=3e-5, abs=3e-5)


def test_zero_covariance_has_zero_jensen_gap_risk() -> None:
    mean = (0.5, -1.2, 0.3)
    covariance = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

    assert gaussian_expected_norm(mean, covariance) == pytest.approx(sqrt(1.78))
    assert exact_gaussian_reference_ranking_risk(mean, covariance) == 0.0


def test_batched_expected_norm_matches_individual_calls() -> None:
    means = ((0.2, -0.5), (1.1, 0.3), (-0.7, 1.4), (0.0, 0.0))
    covariance = ((0.8, 0.2), (0.2, 1.3))

    batched = gaussian_expected_norms(means, covariance)
    individual = tuple(gaussian_expected_norm(mean, covariance) for mean in means)

    assert batched == pytest.approx(individual, rel=1e-12, abs=1e-12)


def test_reference_risk_increases_with_isotropic_uncertainty_at_zero_mean() -> None:
    mean = (0.0, 0.0, 0.0)
    small = ((0.25, 0.0, 0.0), (0.0, 0.25, 0.0), (0.0, 0.0, 0.25))
    large = ((2.25, 0.0, 0.0), (0.0, 2.25, 0.0), (0.0, 0.0, 2.25))

    small_risk = exact_gaussian_reference_ranking_risk(mean, small)
    large_risk = exact_gaussian_reference_ranking_risk(mean, large)

    assert large_risk == pytest.approx(3.0 * small_risk, rel=3e-5)


def test_exact_reference_chooser_returns_valid_pair_and_finite_score() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.2, -0.4),
        covariance=((1.0, 0.0, 0.0), (0.0, 0.8, 0.1), (0.0, 0.1, 1.1)),
        precision=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        converged=True,
        iterations=1,
    )
    candidates = ((1.5, 0.0), (0.0, 1.5), (-1.0, 0.2), (0.2, -1.0))
    remaining = ((0, 1), (0, 2), (1, 3))

    pair, score = choose_exact_gaussian_ranking_pair(remaining, candidates, posterior)

    assert pair in remaining
    assert score == pytest.approx(score)
