from __future__ import annotations

import math

import pytest

from mosaic_engine.science_s1 import (
    acceptance_probability,
    binary_fisher_information,
    four_option_probabilities,
    minimum_pair_queries_for_local_rank,
    operational_selectivity,
    pair_fisher_information,
    pairwise_preference_probability,
    sigmoid,
)


def test_effective_pair_coefficient_absorbs_noise_scale() -> None:
    preference_direction = (1.2, -0.7)
    inverse_noise_scale = 2.5
    effective_coefficients = tuple(inverse_noise_scale * value for value in preference_direction)
    features_a = (0.2, -0.4)
    features_b = (-0.5, 0.3)

    expected_score = inverse_noise_scale * sum(
        coefficient * (feature_a - feature_b)
        for coefficient, feature_a, feature_b in zip(
            preference_direction,
            features_a,
            features_b,
            strict=True,
        )
    )

    assert pairwise_preference_probability(
        effective_coefficients,
        features_a,
        features_b,
    ) == pytest.approx(sigmoid(expected_score))


def test_forced_pairwise_probability_has_no_acceptance_intercept() -> None:
    coefficients = (0.8, -0.25)
    features_a = (0.4, 0.1)
    features_b = (-0.2, 0.6)

    probability = pairwise_preference_probability(coefficients, features_a, features_b)

    # Any absolute intercept would cancel from s(A) - s(B); the public pairwise
    # function therefore has no intercept argument at all.
    assert probability == pytest.approx(
        sigmoid(
            sum(
                coefficient * (feature_a - feature_b)
                for coefficient, feature_a, feature_b in zip(
                    coefficients,
                    features_a,
                    features_b,
                    strict=True,
                )
            )
        )
    )


def test_four_option_response_is_two_binary_acceptability_observations() -> None:
    alpha = (-0.2, 0.7, -0.5)
    features_a = (0.2, -0.4)
    features_b = (-0.5, 0.3)

    probabilities = four_option_probabilities(alpha, features_a, features_b)
    probability_a = acceptance_probability(alpha, features_a)
    probability_b = acceptance_probability(alpha, features_b)

    assert sum(probabilities.values()) == pytest.approx(1.0)
    assert probabilities["a_only"] == pytest.approx(probability_a * (1.0 - probability_b))
    assert probabilities["b_only"] == pytest.approx((1.0 - probability_a) * probability_b)
    assert probabilities["both"] == pytest.approx(probability_a * probability_b)
    assert probabilities["neither"] == pytest.approx((1.0 - probability_a) * (1.0 - probability_b))


def test_binary_fisher_information_is_symmetric_positive_semidefinite() -> None:
    alpha = (0.1, 0.8, -0.3)
    features = (0.25, -0.6)
    information = binary_fisher_information(alpha, features)

    assert information[0][1] == pytest.approx(information[1][0])
    assert information[0][2] == pytest.approx(information[2][0])
    assert information[1][2] == pytest.approx(information[2][1])

    for vector in ((1.0, 0.0, 0.0), (0.2, -1.0, 0.7), (1.0, 1.0, 1.0)):
        quadratic_form = sum(
            vector[row] * information[row][column] * vector[column]
            for row in range(3)
            for column in range(3)
        )
        assert quadratic_form >= -1e-12


def test_pair_information_is_sum_of_candidate_information() -> None:
    alpha = (-0.1, 0.4, 0.9)
    features_a = (0.3, -0.8)
    features_b = (-0.4, 0.2)

    pair_information = pair_fisher_information(alpha, features_a, features_b)
    information_a = binary_fisher_information(alpha, features_a)
    information_b = binary_fisher_information(alpha, features_b)

    for row in range(3):
        for column in range(3):
            assert pair_information[row][column] == pytest.approx(
                information_a[row][column] + information_b[row][column]
            )


def test_pair_rank_lower_bound_is_only_a_necessary_count() -> None:
    assert minimum_pair_queries_for_local_rank(0) == 1
    assert minimum_pair_queries_for_local_rank(1) == 1
    assert minimum_pair_queries_for_local_rank(2) == 2
    assert minimum_pair_queries_for_local_rank(5) == 3
    assert minimum_pair_queries_for_local_rank(8) == 5

    with pytest.raises(ValueError, match="nonnegative"):
        minimum_pair_queries_for_local_rank(-1)


def test_operational_selectivity_uses_reference_distribution() -> None:
    alpha = (0.0, 1.0)
    symmetric_reference = ((-1.0,), (0.0,), (1.0,))

    assert operational_selectivity(alpha, symmetric_reference) == pytest.approx(0.5)

    with pytest.raises(ValueError, match="must not be empty"):
        operational_selectivity(alpha, ())


def test_sigmoid_remains_stable_for_large_scores() -> None:
    assert math.isclose(sigmoid(1000.0), 1.0)
    assert math.isclose(sigmoid(-1000.0), 0.0, abs_tol=1e-15)
