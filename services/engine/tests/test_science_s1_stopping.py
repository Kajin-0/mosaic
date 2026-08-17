from math import sqrt

from mosaic_engine.science_s1_simulation import LaplacePosterior
from mosaic_engine.science_s1_stopping import (
    posterior_directional_risk,
    posterior_radial_debiased_directional_risk,
    posterior_radial_signal,
    posterior_transverse_debiased_directional_risk,
    posterior_transverse_signal,
    posterior_transverse_tangent_directional_risk,
)


def test_posterior_directional_risk_shrinks_with_covariance() -> None:
    broad = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.4, 0.0), (0.0, 0.0, 0.4)),
        precision=((10.0, 0.0, 0.0), (0.0, 2.5, 0.0), (0.0, 0.0, 2.5)),
        converged=True,
        iterations=1,
    )
    tight = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.04, 0.0), (0.0, 0.0, 0.04)),
        precision=((10.0, 0.0, 0.0), (0.0, 25.0, 0.0), (0.0, 0.0, 25.0)),
        converged=True,
        iterations=1,
    )

    broad_risk = posterior_directional_risk(broad, sample_count=1024, seed=7)
    tight_risk = posterior_directional_risk(tight, sample_count=1024, seed=7)

    assert tight_risk.mean_error < broad_risk.mean_error
    assert tight_risk.upper_error < broad_risk.upper_error
    assert tight_risk.slope_norm == broad_risk.slope_norm == 1.0


def test_posterior_directional_risk_is_deterministic_for_seed() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.7, -0.2),
        covariance=((0.2, 0.0, 0.0), (0.0, 0.1, 0.02), (0.0, 0.02, 0.15)),
        precision=((5.0, 0.0, 0.0), (0.0, 10.274, -1.370), (0.0, -1.370, 6.849)),
        converged=True,
        iterations=1,
    )

    first = posterior_directional_risk(posterior, sample_count=128, seed=19)
    second = posterior_directional_risk(posterior, sample_count=128, seed=19)

    assert first == second


def test_zero_slope_mean_is_conservative() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.0, 0.0),
        covariance=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        precision=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        converged=True,
        iterations=1,
    )

    risk = posterior_directional_risk(posterior, sample_count=32, seed=1)

    assert risk.mean_error == 0.5
    assert risk.upper_error == 0.5


def test_radial_signal_subtracts_covariance_trace_from_squared_norm() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, 0.0, 0.2)),
        precision=((10.0, 0.0, 0.0), (0.0, 10.0, 0.0), (0.0, 0.0, 5.0)),
        converged=True,
        iterations=1,
    )

    signal = posterior_radial_signal(posterior)

    assert signal.raw_norm == 1.0
    assert signal.raw_norm_sq == 1.0
    assert abs(signal.covariance_trace - 0.3) < 1e-12
    assert abs(signal.debiased_norm_sq - 0.7) < 1e-12
    assert abs(signal.debiased_norm - sqrt(0.7)) < 1e-12
    assert signal.retained_fraction < 1.0


def test_transverse_signal_excludes_longitudinal_covariance_energy() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.12, 0.0), (0.0, 0.0, 0.18)),
        precision=((10.0, 0.0, 0.0), (0.0, 8.3333333333, 0.0), (0.0, 0.0, 5.5555555556)),
        converged=True,
        iterations=1,
    )

    radial = posterior_radial_signal(posterior)
    transverse = posterior_transverse_signal(posterior)

    assert abs(transverse.covariance_trace - 0.30) < 1e-12
    assert abs(transverse.parallel_variance - 0.12) < 1e-12
    assert abs(transverse.transverse_variance - 0.18) < 1e-12
    assert abs(transverse.debiased_norm_sq - 0.82) < 1e-12
    assert abs(transverse.debiased_norm - sqrt(0.82)) < 1e-12
    assert radial.debiased_norm < transverse.debiased_norm < transverse.raw_norm


def test_radial_debiased_risk_is_more_conservative_when_noise_inflates_norm() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.12, 0.0), (0.0, 0.0, 0.18)),
        precision=((10.0, 0.0, 0.0), (0.0, 8.3333333333, 0.0), (0.0, 0.0, 5.5555555556)),
        converged=True,
        iterations=1,
    )

    ordinary = posterior_directional_risk(posterior, sample_count=4096, seed=23)
    corrected = posterior_radial_debiased_directional_risk(
        posterior,
        sample_count=4096,
        seed=23,
    )

    assert corrected.slope_norm < ordinary.slope_norm
    assert corrected.mean_error > ordinary.mean_error
    assert corrected.upper_error > ordinary.upper_error


def test_transverse_risk_lies_between_raw_and_full_trace_corrections() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.12, 0.0), (0.0, 0.0, 0.18)),
        precision=((10.0, 0.0, 0.0), (0.0, 8.3333333333, 0.0), (0.0, 0.0, 5.5555555556)),
        converged=True,
        iterations=1,
    )

    raw = posterior_directional_risk(posterior, sample_count=4096, seed=23)
    transverse = posterior_transverse_debiased_directional_risk(
        posterior,
        sample_count=4096,
        seed=23,
    )
    full = posterior_radial_debiased_directional_risk(
        posterior,
        sample_count=4096,
        seed=23,
    )

    assert full.slope_norm < transverse.slope_norm < raw.slope_norm
    assert raw.mean_error < transverse.mean_error < full.mean_error
    assert raw.upper_error < transverse.upper_error < full.upper_error


def test_tangent_risk_is_deterministic_and_uses_transverse_signal_norm() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.8, -0.3),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.08, 0.01), (0.0, 0.01, 0.12)),
        precision=((10.0, 0.0, 0.0), (0.0, 12.63, -1.05), (0.0, -1.05, 8.42)),
        converged=True,
        iterations=1,
    )

    signal = posterior_transverse_signal(posterior)
    first = posterior_transverse_tangent_directional_risk(
        posterior,
        sample_count=512,
        seed=41,
    )
    second = posterior_transverse_tangent_directional_risk(
        posterior,
        sample_count=512,
        seed=41,
    )

    assert first == second
    assert first.slope_norm == signal.debiased_norm


def test_tangent_projection_removes_longitudinal_angular_noise() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 1.0, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.40, 0.0), (0.0, 0.0, 0.01)),
        precision=((10.0, 0.0, 0.0), (0.0, 2.5, 0.0), (0.0, 0.0, 100.0)),
        converged=True,
        iterations=1,
    )

    full_noise = posterior_transverse_debiased_directional_risk(
        posterior,
        sample_count=4096,
        seed=17,
    )
    tangent = posterior_transverse_tangent_directional_risk(
        posterior,
        sample_count=4096,
        seed=17,
    )

    assert tangent.slope_norm == full_noise.slope_norm
    assert tangent.mean_error < full_noise.mean_error
    assert tangent.upper_error < full_noise.upper_error


def test_noise_dominated_radial_signal_refuses_confident_direction() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.2, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, 0.0, 0.1)),
        precision=((10.0, 0.0, 0.0), (0.0, 10.0, 0.0), (0.0, 0.0, 10.0)),
        converged=True,
        iterations=1,
    )

    signal = posterior_radial_signal(posterior)
    risk = posterior_radial_debiased_directional_risk(posterior, sample_count=64, seed=2)

    assert signal.debiased_norm == 0.0
    assert signal.retained_fraction == 0.0
    assert risk.mean_error == 0.5
    assert risk.upper_error == 0.5


def test_noise_dominated_transverse_signal_refuses_confident_direction() -> None:
    posterior = LaplacePosterior(
        mean=(0.0, 0.2, 0.0),
        covariance=((0.1, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, 0.0, 0.1)),
        precision=((10.0, 0.0, 0.0), (0.0, 10.0, 0.0), (0.0, 0.0, 10.0)),
        converged=True,
        iterations=1,
    )

    signal = posterior_transverse_signal(posterior)
    risk = posterior_transverse_debiased_directional_risk(
        posterior,
        sample_count=64,
        seed=2,
    )
    tangent = posterior_transverse_tangent_directional_risk(
        posterior,
        sample_count=64,
        seed=2,
    )

    assert signal.transverse_variance == 0.1
    assert signal.debiased_norm == 0.0
    assert risk.mean_error == 0.5
    assert risk.upper_error == 0.5
    assert tangent.mean_error == 0.5
    assert tangent.upper_error == 0.5
