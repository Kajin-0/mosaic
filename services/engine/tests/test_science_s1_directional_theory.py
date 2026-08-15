from __future__ import annotations

import pytest

from mosaic_engine.science_s1_directional_theory import (
    asymptotic_gaussian_logistic_ordering_error,
    asymptotic_isotropic_ordering_error,
    asymptotic_isotropic_slope_cosine,
    asymptotic_kappa_for_ordering_error,
    boundary_directional_information_coordinate,
    gaussian_logistic_directional_information_coordinate,
    gaussian_logistic_transverse_fisher_weight,
    gaussian_population_ordering_error_from_cosine,
    normalize_effective_slope,
)


def test_exact_gaussian_population_ordering_error_has_expected_limits() -> None:
    assert gaussian_population_ordering_error_from_cosine(1.0) == pytest.approx(0.0)
    assert gaussian_population_ordering_error_from_cosine(0.0) == pytest.approx(0.5)
    assert gaussian_population_ordering_error_from_cosine(-1.0) == pytest.approx(1.0)


def test_gaussian_logistic_transverse_fisher_weight_recovers_boundary_limit() -> None:
    assert gaussian_logistic_transverse_fisher_weight(0.0) == pytest.approx(0.25, abs=1e-10)
    assert gaussian_logistic_transverse_fisher_weight(0.9) == pytest.approx(
        0.2128579611,
        rel=1e-8,
    )


def test_boundary_and_fisher_weighted_directional_laws_are_consistent() -> None:
    slope_norm = 0.9
    kappa = 6.0
    eta_boundary = boundary_directional_information_coordinate(
        kappa=kappa,
        slope_norm=slope_norm,
    )
    eta_fisher = gaussian_logistic_directional_information_coordinate(
        kappa=kappa,
        slope_norm=slope_norm,
    )
    cosine = asymptotic_isotropic_slope_cosine(kappa=kappa, slope_norm=slope_norm)
    boundary_error = asymptotic_isotropic_ordering_error(
        kappa=kappa,
        slope_norm=slope_norm,
    )
    fisher_error = asymptotic_gaussian_logistic_ordering_error(
        kappa=kappa,
        slope_norm=slope_norm,
    )

    assert eta_boundary == pytest.approx(0.9**2 * 6.0 / 4.0)
    assert eta_fisher < eta_boundary
    assert cosine**2 == pytest.approx(eta_boundary / (1.0 + eta_boundary))
    assert gaussian_population_ordering_error_from_cosine(cosine) == pytest.approx(boundary_error)
    assert boundary_error == pytest.approx(0.2345, abs=0.001)
    assert fisher_error == pytest.approx(0.2473, abs=0.001)
    assert fisher_error > boundary_error


def test_boundary_ordering_law_inverse_recovers_kappa() -> None:
    slope_norm = 0.9
    for kappa in (2.0, 4.0, 8.0, 12.0):
        target = asymptotic_isotropic_ordering_error(kappa=kappa, slope_norm=slope_norm)
        recovered = asymptotic_kappa_for_ordering_error(
            target_error=target,
            slope_norm=slope_norm,
        )
        assert recovered == pytest.approx(kappa)


def test_normalize_effective_slope_preserves_intercept_and_direction() -> None:
    normalized = normalize_effective_slope((0.3, 3.0, 4.0), target_norm=0.9)
    assert normalized[0] == pytest.approx(0.3)
    assert normalized[1] / normalized[2] == pytest.approx(3.0 / 4.0)
    assert normalized[1] ** 2 + normalized[2] ** 2 == pytest.approx(0.9**2)


def test_directional_theory_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        gaussian_population_ordering_error_from_cosine(1.01)
    with pytest.raises(ValueError):
        gaussian_logistic_transverse_fisher_weight(-0.1)
    with pytest.raises(ValueError):
        gaussian_logistic_transverse_fisher_weight(0.9, intervals=3)
    with pytest.raises(ValueError):
        boundary_directional_information_coordinate(kappa=0.0, slope_norm=0.9)
    with pytest.raises(ValueError):
        asymptotic_isotropic_ordering_error(kappa=1.0, slope_norm=0.0)
    with pytest.raises(ValueError):
        asymptotic_kappa_for_ordering_error(target_error=0.5, slope_norm=0.9)
    with pytest.raises(ValueError):
        normalize_effective_slope((0.0, 0.0), target_norm=0.9)
