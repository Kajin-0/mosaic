from __future__ import annotations

from math import log

import pytest

from mosaic_engine.science_s1_bayesian_acquisition import (
    bernoulli_entropy,
    binary_parameter_mutual_information,
    mutual_information_equivalent_information,
    posterior_expected_fisher_weight,
    posterior_mean_acceptance,
    posterior_score_moments,
)
from mosaic_engine.science_s1_simulation import LaplacePosterior


def _posterior(
    *,
    mean: tuple[float, ...],
    covariance: tuple[tuple[float, ...], ...],
) -> LaplacePosterior:
    # The acquisition functions tested here use mean/covariance only. Precision is
    # included to preserve a valid LaplacePosterior value for the shared type.
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


def test_score_moments_match_linear_gaussian_projection() -> None:
    posterior = _posterior(
        mean=(0.2, 0.5),
        covariance=((0.4, 0.1), (0.1, 0.9)),
    )

    mean, variance = posterior_score_moments(posterior, (2.0,))

    assert mean == pytest.approx(1.2)
    assert variance == pytest.approx(4.4)


def test_zero_mean_predictive_acceptance_is_one_half_by_symmetry() -> None:
    posterior = _posterior(
        mean=(0.0, 0.0),
        covariance=((4.0, 0.0), (0.0, 9.0)),
    )

    assert posterior_mean_acceptance(posterior, (3.0,)) == pytest.approx(0.5)


def test_posterior_averaging_reduces_fisher_weight_under_large_uncertainty() -> None:
    narrow = _posterior(
        mean=(0.0, 0.0),
        covariance=((1e-10, 0.0), (0.0, 1e-10)),
    )
    broad = _posterior(
        mean=(0.0, 0.0),
        covariance=((4.0, 0.0), (0.0, 4.0)),
    )

    narrow_weight = posterior_expected_fisher_weight(narrow, (2.0,))
    broad_weight = posterior_expected_fisher_weight(broad, (2.0,))

    assert narrow_weight == pytest.approx(0.25, rel=1e-6)
    assert 0.0 < broad_weight < narrow_weight


def test_binary_parameter_mutual_information_is_bounded_by_one_bit() -> None:
    posterior = _posterior(
        mean=(0.0, 0.0),
        covariance=((25.0, 0.0), (0.0, 25.0)),
    )

    information = binary_parameter_mutual_information(posterior, (5.0,))

    assert 0.0 <= information <= log(2.0)
    assert information > 0.0


def test_known_parameter_has_zero_mutual_information_about_parameter() -> None:
    posterior = _posterior(
        mean=(0.3, -0.2),
        covariance=((0.0, 0.0), (0.0, 0.0)),
    )

    assert binary_parameter_mutual_information(posterior, (1.5,)) == pytest.approx(0.0)


def test_mi_equivalent_rank_one_update_reproduces_single_candidate_entropy_gain() -> None:
    posterior = _posterior(
        mean=(0.1, -0.3),
        covariance=((1.2, 0.2), (0.2, 0.8)),
    )
    features = (1.4,)
    augmented = (1.0, *features)
    _, variance = posterior_score_moments(posterior, features)
    information = binary_parameter_mutual_information(posterior, features)
    equivalent = mutual_information_equivalent_information(posterior, features)

    # For a rank-one update lambda z z^T, lambda can be recovered from any
    # nonzero z_i z_j entry.  The matrix-determinant lemma then gives the gain.
    equivalent_weight = equivalent[0][0]
    reconstructed_gain = 0.5 * log(1.0 + equivalent_weight * variance)

    assert augmented[0] == 1.0
    assert reconstructed_gain == pytest.approx(information, rel=1e-10, abs=1e-12)


def test_bernoulli_entropy_boundary_values_are_zero() -> None:
    assert bernoulli_entropy(0.0) == 0.0
    assert bernoulli_entropy(1.0) == 0.0
    assert bernoulli_entropy(0.5) == pytest.approx(log(2.0))
