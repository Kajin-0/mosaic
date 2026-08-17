from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

import pytest

from mosaic_engine.science_s1_continuous_geometry import (
    CONE_ALPHA,
    ParameterBox,
    _certify_cone_side,
    _cone_halfspaces,
    _fraction,
    _log_fraction_upper,
    common_log_likelihood_cutoff_lower,
    certify_continuous_cone_current,
    initial_nuisance_box,
    likelihood_bounds,
)
from mosaic_engine.science_s1_eprocess import PrequentialBinaryObservation, binary_log_probability


def _balanced_observations() -> tuple[PrequentialBinaryObservation, ...]:
    features = ((1.0, 0.0), (0.0, 1.0), (-1.0, -1.0))
    observations: list[PrequentialBinaryObservation] = []
    for feature in features:
        observations.append(
            PrequentialBinaryObservation(
                features=feature,
                accepted=False,
                predictive_probability=0.5,
            )
        )
        observations.append(
            PrequentialBinaryObservation(
                features=feature,
                accepted=True,
                predictive_probability=0.5,
            )
        )
    return tuple(observations)


def test_likelihood_interval_bounds_contain_direct_point_value() -> None:
    observations = (
        PrequentialBinaryObservation((0.6, -0.8), True, 0.55),
        PrequentialBinaryObservation((-0.2, 0.9), False, 0.45),
    )
    alpha = (0.1, 0.7, -0.3)
    point_box = ParameterBox(tuple((Fraction.from_float(value),) * 2 for value in alpha))

    bounds = likelihood_bounds(point_box, observations)
    direct = sum(
        binary_log_probability(alpha, observation.features, observation.accepted)
        for observation in observations
    )
    direct_decimal = Decimal.from_float(direct)

    assert bounds.lower <= direct_decimal <= bounds.upper


def test_common_confidence_cutoff_builds_finite_box_containing_zero_parameter() -> None:
    observations = _balanced_observations()
    cutoff = common_log_likelihood_cutoff_lower(observations)
    box = initial_nuisance_box(observations, common_cutoff_lower=cutoff)

    assert box is not None
    for lower, upper in box.intervals:
        assert lower < 0 < upper


def test_nuisance_box_refuses_unmixed_outcomes() -> None:
    observations = tuple(
        PrequentialBinaryObservation(feature, True, 0.5)
        for feature in ((1.0, 0.0), (0.0, 1.0), (-1.0, -1.0))
    )
    cutoff = common_log_likelihood_cutoff_lower(observations)

    assert initial_nuisance_box(observations, common_cutoff_lower=cutoff) is None


def test_known_outside_survivor_cannot_be_turned_into_certificate() -> None:
    observations = _balanced_observations()
    cutoff = common_log_likelihood_cutoff_lower(observations)
    outside_parameter = (0.0, 0.0, 0.1)
    point_box = ParameterBox(
        tuple((_fraction(value), _fraction(value)) for value in outside_parameter)
    )
    halfspaces = _cone_halfspaces((1.0, 0.0), target_error=0.15)
    violated = next(
        halfspace
        for halfspace in halfspaces
        if halfspace[0] * point_box.intervals[1][0]
        + halfspace[1] * point_box.intervals[2][0]
        < 0
    )

    result = _certify_cone_side(
        point_box,
        observations,
        halfspace=violated,
        common_cutoff_lower=cutoff,
        cone_log_threshold_upper=_log_fraction_upper(1 / CONE_ALPHA),
        max_nodes=10,
        min_width=1e-6,
    )

    assert not result.certified
    assert result.reason == "resolution_limit"


def test_box_entirely_inside_halfspace_certifies_without_numerical_search() -> None:
    observations = _balanced_observations()
    cutoff = common_log_likelihood_cutoff_lower(observations)
    halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[0]
    inside_box = ParameterBox(
        (
            (Fraction(-1), Fraction(1)),
            (Fraction(2), Fraction(3)),
            (Fraction(0), Fraction(0)),
        )
    )

    result = _certify_cone_side(
        inside_box,
        observations,
        halfspace=halfspace,
        common_cutoff_lower=cutoff,
        cone_log_threshold_upper=_log_fraction_upper(1 / CONE_ALPHA),
        max_nodes=10,
        min_width=1e-6,
    )

    assert result.certified
    assert result.nodes_visited == 1


def test_continuous_certificate_rejects_invalid_alpha_split() -> None:
    with pytest.raises(ValueError, match="sum to at most 0.05"):
        certify_continuous_cone_current(
            _balanced_observations(),
            (1.0, 0.0),
            common_alpha=Fraction(1, 25),
            cone_alpha=Fraction(1, 25),
        )
