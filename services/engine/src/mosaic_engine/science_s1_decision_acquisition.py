from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import pi, sqrt

from .science_s1 import sigmoid
from .science_s1_bayesian_acquisition import (
    posterior_expected_fisher_weight,
    posterior_mean_acceptance,
)
from .science_s1_simulation import CandidatePair, LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]

# Five-point Gauss-Hermite rule for the bivariate predictive integral.
_GH5_NODES = (
    -2.0201828704560856,
    -0.9585724646138185,
    0.0,
    0.9585724646138185,
    2.0201828704560856,
)
_GH5_WEIGHTS = (
    0.01995324205904591,
    0.3936193231522412,
    0.9453087204829419,
    0.3936193231522412,
    0.01995324205904591,
)
_SQRT_TWO = sqrt(2.0)


@dataclass(frozen=True)
class PairPredictiveMoments:
    probability_a: float
    probability_b: float
    probability_both: float
    covariance: tuple[tuple[float, float], tuple[float, float]]


@dataclass(frozen=True)
class LinearBayesOutcome:
    response_a: bool
    response_b: bool
    probability: float
    mean: Vector
    covariance: Matrix


def _augment(features: Sequence[float]) -> Vector:
    return (1.0, *(float(value) for value in features))


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions must agree")
    return sum(float(a) * float(b) for a, b in zip(left, right, strict=True))


def _matrix_vector(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> Vector:
    if len(matrix) != len(vector) or any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector dimensions must agree")
    return tuple(_dot(row, vector) for row in matrix)


def _score_covariance(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[float, float, float, float, float]:
    augmented_a = _augment(features_a)
    augmented_b = _augment(features_b)
    if len(augmented_a) != len(posterior.mean) or len(augmented_b) != len(posterior.mean):
        raise ValueError("feature dimension does not match posterior")

    sigma_a = _matrix_vector(posterior.covariance, augmented_a)
    sigma_b = _matrix_vector(posterior.covariance, augmented_b)
    mean_a = _dot(posterior.mean, augmented_a)
    mean_b = _dot(posterior.mean, augmented_b)
    variance_a = max(_dot(augmented_a, sigma_a), 0.0)
    variance_b = max(_dot(augmented_b, sigma_b), 0.0)
    covariance_ab = _dot(augmented_a, sigma_b)
    return mean_a, mean_b, variance_a, variance_b, covariance_ab


def _bivariate_probability_both(
    mean_a: float,
    mean_b: float,
    variance_a: float,
    variance_b: float,
    covariance_ab: float,
) -> float:
    if variance_a <= 1e-14 and variance_b <= 1e-14:
        return sigmoid(mean_a) * sigmoid(mean_b)

    diagonal_a = sqrt(max(variance_a, 0.0))
    if diagonal_a <= 1e-12:
        probability_a = sigmoid(mean_a)
        # With a deterministic first score, cross covariance must vanish in a
        # valid covariance matrix up to numerical error.
        expectation_b = 0.0
        scale_b = sqrt(2.0 * max(variance_b, 0.0))
        for node_b, weight_b in zip(_GH5_NODES, _GH5_WEIGHTS, strict=True):
            expectation_b += weight_b * sigmoid(mean_b + scale_b * node_b)
        return probability_a * expectation_b / sqrt(pi)

    lower_11 = diagonal_a
    lower_21 = covariance_ab / lower_11
    residual_b = max(variance_b - lower_21 * lower_21, 0.0)
    lower_22 = sqrt(residual_b)

    expectation = 0.0
    for node_a, weight_a in zip(_GH5_NODES, _GH5_WEIGHTS, strict=True):
        standard_a = _SQRT_TWO * node_a
        score_a = mean_a + lower_11 * standard_a
        probability_a = sigmoid(score_a)
        for node_b, weight_b in zip(_GH5_NODES, _GH5_WEIGHTS, strict=True):
            standard_b = _SQRT_TWO * node_b
            score_b = mean_b + lower_21 * standard_a + lower_22 * standard_b
            expectation += weight_a * weight_b * probability_a * sigmoid(score_b)
    return expectation / pi


def pair_predictive_moments(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> PairPredictiveMoments:
    probability_a = posterior_mean_acceptance(posterior, features_a)
    probability_b = posterior_mean_acceptance(posterior, features_b)
    mean_a, mean_b, variance_a, variance_b, covariance_ab = _score_covariance(
        posterior,
        features_a,
        features_b,
    )
    probability_both = _bivariate_probability_both(
        mean_a,
        mean_b,
        variance_a,
        variance_b,
        covariance_ab,
    )
    lower = max(0.0, probability_a + probability_b - 1.0)
    upper = min(probability_a, probability_b)
    probability_both = min(max(probability_both, lower), upper)
    binary_covariance = probability_both - probability_a * probability_b
    variance_y_a = probability_a * (1.0 - probability_a)
    variance_y_b = probability_b * (1.0 - probability_b)
    return PairPredictiveMoments(
        probability_a=probability_a,
        probability_b=probability_b,
        probability_both=probability_both,
        covariance=((variance_y_a, binary_covariance), (binary_covariance, variance_y_b)),
    )


def _inverse_2x2(
    matrix: tuple[tuple[float, float], tuple[float, float]],
) -> tuple[tuple[float, float], tuple[float, float]]:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    if determinant <= 1e-12:
        jitter = 1e-8
        a += jitter
        d += jitter
        determinant = a * d - b * c
    if determinant <= 0.0:
        raise ValueError("predictive response covariance must be positive definite")
    inverse_scale = 1.0 / determinant
    return (
        (d * inverse_scale, -b * inverse_scale),
        (-c * inverse_scale, a * inverse_scale),
    )


def _linear_bayes_columns(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[Vector, Vector]:
    augmented_a = _augment(features_a)
    augmented_b = _augment(features_b)
    sigma_a = _matrix_vector(posterior.covariance, augmented_a)
    sigma_b = _matrix_vector(posterior.covariance, augmented_b)
    weight_a = posterior_expected_fisher_weight(posterior, features_a)
    weight_b = posterior_expected_fisher_weight(posterior, features_b)
    return (
        tuple(value * weight_a for value in sigma_a),
        tuple(value * weight_b for value in sigma_b),
    )


def linear_bayes_pair_outcomes(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[LinearBayesOutcome, ...]:
    moments = pair_predictive_moments(posterior, features_a, features_b)
    response_inverse = _inverse_2x2(moments.covariance)
    covariance_a, covariance_b = _linear_bayes_columns(posterior, features_a, features_b)
    dimension = len(posterior.mean)

    gain_a = tuple(
        covariance_a[index] * response_inverse[0][0]
        + covariance_b[index] * response_inverse[1][0]
        for index in range(dimension)
    )
    gain_b = tuple(
        covariance_a[index] * response_inverse[0][1]
        + covariance_b[index] * response_inverse[1][1]
        for index in range(dimension)
    )

    updated_covariance = tuple(
        tuple(
            posterior.covariance[row][column]
            - gain_a[row] * covariance_a[column]
            - gain_b[row] * covariance_b[column]
            for column in range(dimension)
        )
        for row in range(dimension)
    )

    p_a = moments.probability_a
    p_b = moments.probability_b
    p_11 = moments.probability_both
    outcome_probabilities = (
        (False, False, 1.0 - p_a - p_b + p_11),
        (False, True, p_b - p_11),
        (True, False, p_a - p_11),
        (True, True, p_11),
    )

    outcomes: list[LinearBayesOutcome] = []
    for response_a, response_b, probability in outcome_probabilities:
        residual_a = (1.0 if response_a else 0.0) - p_a
        residual_b = (1.0 if response_b else 0.0) - p_b
        updated_mean = tuple(
            posterior.mean[index] + gain_a[index] * residual_a + gain_b[index] * residual_b
            for index in range(dimension)
        )
        outcomes.append(
            LinearBayesOutcome(
                response_a=response_a,
                response_b=response_b,
                probability=max(probability, 0.0),
                mean=updated_mean,
                covariance=updated_covariance,
            )
        )

    total_probability = sum(outcome.probability for outcome in outcomes)
    if total_probability <= 0.0:
        raise ValueError("predictive outcome probabilities must have positive mass")
    return tuple(
        LinearBayesOutcome(
            response_a=outcome.response_a,
            response_b=outcome.response_b,
            probability=outcome.probability / total_probability,
            mean=outcome.mean,
            covariance=outcome.covariance,
        )
        for outcome in outcomes
    )


def _predictive_acceptance_from_state(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    features: Sequence[float],
) -> float:
    posterior = LaplacePosterior(
        mean=tuple(float(value) for value in mean),
        covariance=tuple(tuple(float(value) for value in row) for row in covariance),
        precision=tuple(tuple() for _ in mean),
        converged=True,
        iterations=0,
    )
    return posterior_mean_acceptance(posterior, features)


def top_k_posterior_value(
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
        _predictive_acceptance_from_state(mean, covariance, features)
        for features in decision_features
    ]
    return sum(sorted(probabilities, reverse=True)[:top_k]) / top_k


def expected_top_k_value_of_information(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
    decision_features: Sequence[Sequence[float]],
    *,
    top_k: int,
) -> float:
    current_value = top_k_posterior_value(
        posterior.mean,
        posterior.covariance,
        decision_features,
        top_k=top_k,
    )
    expected_updated_value = 0.0
    for outcome in linear_bayes_pair_outcomes(posterior, features_a, features_b):
        expected_updated_value += outcome.probability * top_k_posterior_value(
            outcome.mean,
            outcome.covariance,
            decision_features,
            top_k=top_k,
        )
    return expected_updated_value - current_value


def choose_expected_top_k_value_pair(
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
    decision_features: Sequence[Sequence[float]],
    *,
    top_k: int,
) -> CandidatePair:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")

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
        score = expected_top_k_value_of_information(
            posterior,
            features_a,
            features_b,
            decision_features,
            top_k=top_k,
        )
        if score > best_score or (score == best_score and pair < best_pair):
            best_pair = pair
            best_score = score
    return best_pair
