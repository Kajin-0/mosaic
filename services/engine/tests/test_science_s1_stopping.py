from mosaic_engine.science_s1_simulation import LaplacePosterior
from mosaic_engine.science_s1_stopping import posterior_directional_risk


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
