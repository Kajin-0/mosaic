from __future__ import annotations

from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14a import (
    _box_grid,
    _random_boxes,
    _reference_cone_log_e,
    _reference_log_likelihood,
    _synthetic_observations,
)
from mosaic_engine.science_s1_continuous_geometry import likelihood_bounds
from mosaic_engine.science_s1_continuous_geometry_grouped import (
    group_binary_observations,
    grouped_cone_log_e_lower_bound,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from mosaic_engine.science_s1_eprocess import PrequentialBinaryObservation


def test_group_binary_observations_preserves_feature_outcome_counts() -> None:
    observations = (
        PrequentialBinaryObservation((1.0, 0.0), True, 0.5),
        PrequentialBinaryObservation((1.0, 0.0), False, 0.5),
        PrequentialBinaryObservation((1.0, 0.0), True, 0.5),
        PrequentialBinaryObservation((0.0, 1.0), False, 0.5),
    )

    groups = group_binary_observations(observations)

    assert len(groups) == 2
    by_feature = {group.features: group for group in groups}
    assert by_feature[(1.0, 0.0)].accept_count == 2
    assert by_feature[(1.0, 0.0)].reject_count == 1
    assert by_feature[(0.0, 1.0)].accept_count == 0
    assert by_feature[(0.0, 1.0)].reject_count == 1


def test_grouped_likelihood_bounds_contain_high_precision_reference_grid() -> None:
    observations = _synthetic_observations(
        alpha=(0.2, 0.9, -0.35),
        repeats=3,
        seed=14_201,
    )
    prepared = prepare_grouped_likelihood(observations, rotations_degrees=(0.0, 30.0))
    box = _random_boxes(count=1, seed=14_202)[0]

    for rotation in (0.0, 30.0):
        bounds = grouped_likelihood_bounds(box, prepared, rotation_degrees=rotation)
        for theta in _box_grid(box, grid_size=3):
            direct = _reference_log_likelihood(
                theta,
                observations,
                rotation_degrees=rotation,
            )
            assert bounds.lower <= direct <= bounds.upper


def test_grouped_cone_lower_bound_is_one_sided_on_dense_box_grid() -> None:
    observations = _synthetic_observations(
        alpha=(0.1, 1.0, 0.25),
        repeats=3,
        seed=14_203,
    )
    prepared = prepare_grouped_likelihood(observations)
    box = _random_boxes(count=1, seed=14_204)[0]
    lower = grouped_cone_log_e_lower_bound(box, prepared)

    for theta in _box_grid(box, grid_size=3):
        assert lower <= _reference_cone_log_e(theta, observations)


def test_grouped_and_raw_bounds_both_enclose_same_point_likelihood() -> None:
    observations = _synthetic_observations(
        alpha=(0.0, 0.8, -0.2),
        repeats=4,
        seed=14_205,
    )
    prepared = prepare_grouped_likelihood(observations, rotations_degrees=(0.0,))
    theta = (Fraction(1, 10), Fraction(9, 10), Fraction(-1, 5))
    point_box = _random_boxes(count=1, seed=14_206)[0]
    point_box = type(point_box)(tuple((value, value) for value in theta))
    direct = _reference_log_likelihood(theta, observations)

    grouped = grouped_likelihood_bounds(point_box, prepared)
    raw = likelihood_bounds(point_box, observations)

    assert grouped.lower <= direct <= grouped.upper
    assert raw.lower <= direct <= raw.upper


def test_prepared_grouped_likelihood_reduces_repeated_path_to_unique_features() -> None:
    observations = _synthetic_observations(
        alpha=(0.0, 0.9, 0.0),
        repeats=20,
        seed=14_207,
    )

    prepared = prepare_grouped_likelihood(observations)

    assert prepared.observation_count == 240
    assert len(prepared.groups) == 12
    assert sum(group.accept_count + group.reject_count for group in prepared.groups) == 240
