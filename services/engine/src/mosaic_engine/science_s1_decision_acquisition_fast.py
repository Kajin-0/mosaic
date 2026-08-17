from __future__ import annotations

from collections.abc import Sequence
from math import pi, sqrt

from .science_s1 import sigmoid
from .science_s1_decision_acquisition import linear_bayes_pair_outcomes
from .science_s1_simulation import CandidatePair, LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]


def _augment(features: Sequence[float]) -> Vector:
    return (1.0, *(float(value) for value in features))


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions must agree")
    return sum(float(a) * float(b) for a, b in zip(left, right, strict=True))


def _quadratic_form(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> float:
    dimension = len(vector)
    if len(matrix) != dimension or any(len(row) != dimension for row in matrix):
        raise ValueError("matrix and vector dimensions must agree")
    return sum(
        float(vector[row]) * float(matrix[row][column]) * float(vector[column])
        for row in range(dimension)
        for column in range(dimension)
    )


def logistic_normal_mean_approximation(mean: float, variance: float) -> float:
    """Approximate E[sigmoid(S)] for S ~ Normal(mean, variance).

    This is used only inside the v4 acquisition objective.  Posterior fitting and
    held-out benchmark evaluation continue to use the existing Gauss-Hermite
    calculations.
    """
    if variance < -1e-10:
        raise ValueError("variance must be nonnegative")
    variance = max(float(variance), 0.0)
    adjusted_mean = float(mean) / sqrt(1.0 + pi * variance / 8.0)
    return sigmoid(adjusted_mean)


def predictive_acceptance_approximation(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    features: Sequence[float],
) -> float:
    augmented = _augment(features)
    if len(augmented) != len(mean):
        raise ValueError("feature dimension does not match posterior state")
    score_mean = _dot(mean, augmented)
    score_variance = _quadratic_form(covariance, augmented)
    return logistic_normal_mean_approximation(score_mean, score_variance)


def top_k_posterior_value_approximation(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    decision_features: Sequence[Sequence[float]],
    *,
    top_k: int,
) -> float:
    if not decision_features:
        raise ValueError("decision_features must not be empty")
    if top_k <= 0 or top_k > len(decision_features):
        raise ValueError("top_k must be within the decision bank")
    probabilities = [
        predictive_acceptance_approximation(mean, covariance, features)
        for features in decision_features
    ]
    return sum(sorted(probabilities, reverse=True)[:top_k]) / top_k


def expected_top_k_value_of_information_approximation(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
    decision_features: Sequence[Sequence[float]],
    *,
    top_k: int,
    current_value: float | None = None,
) -> float:
    if current_value is None:
        current_value = top_k_posterior_value_approximation(
            posterior.mean,
            posterior.covariance,
            decision_features,
            top_k=top_k,
        )

    expected_updated_value = 0.0
    for outcome in linear_bayes_pair_outcomes(posterior, features_a, features_b):
        expected_updated_value += outcome.probability * top_k_posterior_value_approximation(
            outcome.mean,
            outcome.covariance,
            decision_features,
            top_k=top_k,
        )
    return expected_updated_value - current_value


def choose_expected_top_k_value_pair_approximation(
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
    decision_features: Sequence[Sequence[float]],
    *,
    top_k: int,
) -> tuple[CandidatePair, float]:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")

    current_value = top_k_posterior_value_approximation(
        posterior.mean,
        posterior.covariance,
        decision_features,
        top_k=top_k,
    )
    best_pair = remaining_pairs[0]
    best_score = float("-inf")
    for pair in remaining_pairs:
        first, second = pair
        if first == second or first < 0 or second < 0:
            raise ValueError("candidate pair indices must be distinct and nonnegative")
        try:
            features_a = candidates[first]
            features_b = candidates[second]
        except IndexError as error:
            raise ValueError("candidate pair index is out of range") from error
        score = expected_top_k_value_of_information_approximation(
            posterior,
            features_a,
            features_b,
            decision_features,
            top_k=top_k,
            current_value=current_value,
        )
        if score > best_score or (score == best_score and pair < best_pair):
            best_pair = pair
            best_score = score
    return best_pair, best_score
