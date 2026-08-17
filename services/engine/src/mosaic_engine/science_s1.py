from __future__ import annotations

from collections.abc import Sequence
from math import ceil, exp

FOUR_OPTION_RESPONSES = ("a_only", "b_only", "both", "neither")


def sigmoid(value: float) -> float:
    """Numerically stable logistic function."""
    if value >= 0.0:
        exponential = exp(-value)
        return 1.0 / (1.0 + exponential)

    exponential = exp(value)
    return exponential / (1.0 + exponential)


def acceptance_probability(alpha: Sequence[float], features: Sequence[float]) -> float:
    """Return P(willing-to-meet) for the S1 effective linear-logistic state."""
    if len(alpha) != len(features) + 1:
        raise ValueError("alpha must contain one intercept plus one coefficient per feature")

    score = float(alpha[0]) + sum(
        float(coefficient) * float(feature)
        for coefficient, feature in zip(alpha[1:], features, strict=True)
    )
    return sigmoid(score)


def pairwise_preference_probability(
    effective_coefficients: Sequence[float],
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> float:
    """Return P(A preferred to B) using only the identifiable effective coefficients.

    An absolute acceptance intercept is intentionally absent: it cancels from forced
    pairwise utility differences.
    """
    if len(effective_coefficients) != len(features_a) or len(features_a) != len(features_b):
        raise ValueError("coefficient and feature dimensions must agree")

    difference_score = sum(
        float(coefficient) * (float(feature_a) - float(feature_b))
        for coefficient, feature_a, feature_b in zip(
            effective_coefficients,
            features_a,
            features_b,
            strict=True,
        )
    )
    return sigmoid(difference_score)


def four_option_probabilities(
    alpha: Sequence[float],
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> dict[str, float]:
    """Return the provisional independent-threshold four-option response probabilities."""
    probability_a = acceptance_probability(alpha, features_a)
    probability_b = acceptance_probability(alpha, features_b)

    return {
        "a_only": probability_a * (1.0 - probability_b),
        "b_only": (1.0 - probability_a) * probability_b,
        "both": probability_a * probability_b,
        "neither": (1.0 - probability_a) * (1.0 - probability_b),
    }


def binary_fisher_information(
    alpha: Sequence[float],
    features: Sequence[float],
) -> tuple[tuple[float, ...], ...]:
    """Return local Fisher information for one binary acceptability observation."""
    probability = acceptance_probability(alpha, features)
    weight = probability * (1.0 - probability)
    augmented_features = (1.0, *(float(feature) for feature in features))

    return tuple(
        tuple(weight * row_feature * column_feature for column_feature in augmented_features)
        for row_feature in augmented_features
    )


def pair_fisher_information(
    alpha: Sequence[float],
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[tuple[float, ...], ...]:
    """Return local information for one four-option pair under conditional independence."""
    information_a = binary_fisher_information(alpha, features_a)
    information_b = binary_fisher_information(alpha, features_b)

    return tuple(
        tuple(value_a + value_b for value_a, value_b in zip(row_a, row_b, strict=True))
        for row_a, row_b in zip(information_a, information_b, strict=True)
    )


def minimum_pair_queries_for_local_rank(feature_dimension: int) -> int:
    """Necessary rank lower bound for a d-feature model plus intercept.

    One four-option pair yields at most two rank-one binary-information terms. This
    bound says nothing about useful precision and must not be used as a query budget.
    """
    if feature_dimension < 0:
        raise ValueError("feature_dimension must be nonnegative")
    return ceil((feature_dimension + 1) / 2)


def operational_selectivity(
    alpha: Sequence[float],
    reference_features: Sequence[Sequence[float]],
) -> float:
    """Return 1 - mean predicted acceptance over a versioned reference distribution."""
    if not reference_features:
        raise ValueError("reference_features must not be empty")

    mean_acceptance = sum(
        acceptance_probability(alpha, features) for features in reference_features
    ) / len(reference_features)
    return 1.0 - mean_acceptance
