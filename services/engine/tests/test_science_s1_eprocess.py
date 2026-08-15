from __future__ import annotations

from math import isfinite, log

import pytest

from mosaic_engine.science_s1_eprocess import (
    PrequentialBinaryObservation,
    anytime_log_threshold,
    binary_log_probability,
    composite_null_log_e_lower_bound,
    confidence_log_likelihood_threshold,
    one_step_e_expectation,
    prequential_log_e_increment,
    prequential_log_e_value,
    reject_composite_null,
    reject_fixed_parameter,
)


def test_binary_log_probability_is_stable_for_extreme_scores() -> None:
    alpha = (0.0, 1000.0)

    assert binary_log_probability(alpha, (1.0,), True) == pytest.approx(0.0, abs=1e-12)
    assert binary_log_probability(alpha, (1.0,), False) == pytest.approx(-1000.0)
    assert binary_log_probability(alpha, (-1.0,), False) == pytest.approx(0.0, abs=1e-12)
    assert binary_log_probability(alpha, (-1.0,), True) == pytest.approx(-1000.0)


def test_one_step_e_increment_has_conditional_expectation_one() -> None:
    alpha = (-0.4, 0.8, -0.3)
    features = (0.25, -0.7)

    for predictive_probability in (0.05, 0.2, 0.5, 0.83, 0.97):
        assert one_step_e_expectation(
            alpha,
            features,
            predictive_probability=predictive_probability,
        ) == pytest.approx(1.0, abs=1e-12)


def test_cumulative_log_e_value_is_sum_of_predictable_increments() -> None:
    alpha = (0.1, 0.6)
    observations = (
        PrequentialBinaryObservation((0.3,), True, 0.7),
        PrequentialBinaryObservation((-0.8,), False, 0.4),
        PrequentialBinaryObservation((0.1,), True, 0.55),
    )

    expected = sum(
        prequential_log_e_increment(
            alpha,
            observation.features,
            observation.accepted,
            predictive_probability=observation.predictive_probability,
        )
        for observation in observations
    )

    assert prequential_log_e_value(alpha, observations) == pytest.approx(expected)
    assert isfinite(expected)


def test_confidence_likelihood_cutoff_matches_e_threshold() -> None:
    alpha_level = 0.05
    log_predictive_joint = -12.0
    threshold = confidence_log_likelihood_threshold(
        log_predictive_joint,
        alpha_level=alpha_level,
    )

    assert threshold == pytest.approx(log_predictive_joint + log(alpha_level))
    boundary_log_e = log_predictive_joint - threshold
    assert boundary_log_e == pytest.approx(anytime_log_threshold(alpha_level))
    assert reject_fixed_parameter(boundary_log_e, alpha_level=alpha_level)


def test_composite_null_uses_upper_likelihood_bound_conservatively() -> None:
    log_predictive_joint = -8.0
    tight_upper = -12.0
    loose_upper = -10.0

    tight_log_e = composite_null_log_e_lower_bound(log_predictive_joint, tight_upper)
    loose_log_e = composite_null_log_e_lower_bound(log_predictive_joint, loose_upper)

    assert tight_log_e > loose_log_e
    assert reject_composite_null(
        log_predictive_joint,
        tight_upper,
        alpha_level=0.05,
    )
    assert not reject_composite_null(
        log_predictive_joint,
        loose_upper,
        alpha_level=0.05,
    )


def test_invalid_probabilities_and_levels_are_rejected() -> None:
    alpha = (0.0, 1.0)

    for prediction in (0.0, 1.0, -0.1, 1.1):
        with pytest.raises(ValueError, match="predictive_probability"):
            prequential_log_e_increment(
                alpha,
                (0.0,),
                True,
                predictive_probability=prediction,
            )

    for level in (0.0, 1.0, -0.1, 1.1):
        with pytest.raises(ValueError, match="alpha_level"):
            anytime_log_threshold(level)
