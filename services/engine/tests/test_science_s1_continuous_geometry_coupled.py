from __future__ import annotations

from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import (
    _reference_cone_log_e,
    _reference_log_likelihood,
    _synthetic_observations,
)
from mosaic_engine.science_s1_continuous_geometry import ParameterBox
from mosaic_engine.science_s1_continuous_geometry_coupled import (
    grouped_coupled_cone_log_e_lower_bound,
    grouped_log_likelihood_ratio_lower_bound,
)
from mosaic_engine.science_s1_continuous_geometry_grouped import prepare_grouped_likelihood


def _box_around(
    theta: tuple[float, float, float],
    widths: tuple[float, float, float],
) -> ParameterBox:
    return ParameterBox(
        tuple(
            (
                Fraction.from_float(center - width / 2.0),
                Fraction.from_float(center + width / 2.0),
            )
            for center, width in zip(theta, widths, strict=True)
        )
    )


def test_coupled_ratio_lower_bound_is_below_direct_points() -> None:
    observations = _synthetic_observations(
        alpha=(0.15, 1.0, -0.3),
        repeats=3,
        seed=14_501,
    )
    prepared = prepare_grouped_likelihood(observations)
    box = _box_around((0.1, 0.8, -0.2), (0.3, 0.4, 0.4))
    lower = grouped_log_likelihood_ratio_lower_bound(
        box,
        prepared,
        rotation_degrees=60.0,
    )

    for theta in (
        tuple(interval[0] for interval in box.intervals),
        tuple(interval[1] for interval in box.intervals),
        tuple((lower_value + upper_value) / 2 for lower_value, upper_value in box.intervals),
    ):
        direct = _reference_log_likelihood(
            theta,
            observations,
            rotation_degrees=60.0,
        ) - _reference_log_likelihood(theta, observations)
        assert lower <= direct


def test_coupled_cone_lower_bound_is_below_direct_points() -> None:
    observations = _synthetic_observations(
        alpha=(0.0, 0.9, 0.4),
        repeats=3,
        seed=14_502,
    )
    prepared = prepare_grouped_likelihood(observations)
    box = _box_around((0.0, 0.7, 0.2), (0.2, 0.5, 0.5))
    lower = grouped_coupled_cone_log_e_lower_bound(box, prepared)

    for theta in (
        tuple(interval[0] for interval in box.intervals),
        tuple(interval[1] for interval in box.intervals),
        tuple((lower_value + upper_value) / 2 for lower_value, upper_value in box.intervals),
    ):
        assert lower <= _reference_cone_log_e(theta, observations)
