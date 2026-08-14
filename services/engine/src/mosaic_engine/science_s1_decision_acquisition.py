from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import atan2, cos, pi, sin, sqrt

from .science_s1 import sigmoid
from .science_s1_bayesian_acquisition import posterior_mean_acceptance
from .science_s1_simulation import CandidatePair, LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]
Matrix2 = tuple[tuple[float, float], tuple[float, float]]

# Nine-point Gauss-Hermite rule, matching the numerical order used by the S1
# one-dimensional posterior-predictive calculations.  The v4 update derives
# all score/response moments from one joint quadrature so its covariance block
# is internally coherent rather than mixing independently approximated moments.
_GH9_NODES = (
    -3.1909932017815277,
    -2.266580584531843,
    -1.468553289216668,
    -0.7235510187528376,
    0.0,
    0.7235510187528376,
    1.468553289216668,
    2.266580584531843,
    3.1909932017815277,
)
_GH9_WEIGHTS = (
    3.9606977263264365e-05,
    0.004943624275536941,
    0.08847452739437664,
    0.43265155900255564,
    0.720235215606051,
    0.43265155900255564,
    0.08847452739437664,
    0.004943624275536941,
    3.9606977263264365e-05,
)
_SQRT_TWO = sqrt(2.0)


@dataclass(frozen=True)
class PairPredictiveMoments:
    probability_a: float
    probability_b: float
    probability_both: float
    covariance: Matrix2
    score_covariance: Matrix2
    score_response_covariance: Matrix2


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


def _score_moments(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[float, float, Matrix2]:
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
    covariance = (
        (variance_a, covariance_ab),
        (covariance_ab, variance_b),
    )
    return mean_a, mean_b, covariance


def _joint_score_response_moments(
    mean_a: float,
    mean_b: float,
    score_covariance: Matrix2,
) -> tuple[float, float, float, Matrix2]:
    variance_a = max(score_covariance[0][0], 0.0)
    variance_b = max(score_covariance[1][1], 0.0)
    covariance_ab = score_covariance[0][1]

    if variance_a <= 1e-14 and variance_b <= 1e-14:
        probability_a = sigmoid(mean_a)
        probability_b = sigmoid(mean_b)
        return (
            probability_a,
            probability_b,
            probability_a * probability_b,
            ((0.0, 0.0), (0.0, 0.0)),
        )

    if variance_a <= 1e-14:
        probability_a = sigmoid(mean_a)
        scale_b = sqrt(2.0 * variance_b)
        total_probability_b = 0.0
        total_score_b_probability_b = 0.0
        for node_b, weight_b in zip(_GH9_NODES, _GH9_WEIGHTS, strict=True):
            score_b = mean_b + scale_b * node_b
            probability_b = sigmoid(score_b)
            total_probability_b += weight_b * probability_b
            total_score_b_probability_b += weight_b * (score_b - mean_b) * probability_b
        normalization = sqrt(pi)
        probability_b = total_probability_b / normalization
        covariance_score_b_y_b = total_score_b_probability_b / normalization
        return (
            probability_a,
            probability_b,
            probability_a * probability_b,
            ((0.0, 0.0), (0.0, covariance_score_b_y_b)),
        )

    lower_11 = sqrt(variance_a)
    lower_21 = covariance_ab / lower_11
    residual_b = max(variance_b - lower_21 * lower_21, 0.0)
    lower_22 = sqrt(residual_b)

    probability_a_total = 0.0
    probability_b_total = 0.0
    probability_both_total = 0.0
    score_a_y_a_total = 0.0
    score_a_y_b_total = 0.0
    score_b_y_a_total = 0.0
    score_b_y_b_total = 0.0

    for node_a, weight_a in zip(_GH9_NODES, _GH9_WEIGHTS, strict=True):
        standard_a = _SQRT_TWO * node_a
        score_a = mean_a + lower_11 * standard_a
        probability_a = sigmoid(score_a)
        for node_b, weight_b in zip(_GH9_NODES, _GH9_WEIGHTS, strict=True):
            standard_b = _SQRT_TWO * node_b
            score_b = mean_b + lower_21 * standard_a + lower_22 * standard_b
            probability_b = sigmoid(score_b)
            weight = weight_a * weight_b
            probability_a_total += weight * probability_a
            probability_b_total += weight * probability_b
            probability_both_total += weight * probability_a * probability_b
            score_a_y_a_total += weight * (score_a - mean_a) * probability_a
            score_a_y_b_total += weight * (score_a - mean_a) * probability_b
            score_b_y_a_total += weight * (score_b - mean_b) * probability_a
            score_b_y_b_total += weight * (score_b - mean_b) * probability_b

    normalization = pi
    return (
        probability_a_total / normalization,
        probability_b_total / normalization,
        probability_both_total / normalization,
        (
            (score_a_y_a_total / normalization, score_a_y_b_total / normalization),
            (score_b_y_a_total / normalization, score_b_y_b_total / normalization),
        ),
    )


def pair_predictive_moments(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> PairPredictiveMoments:
    mean_a, mean_b, score_covariance = _score_moments(
        posterior,
        features_a,
        features_b,
    )
    probability_a, probability_b, probability_both, score_response_covariance = (
        _joint_score_response_moments(mean_a, mean_b, score_covariance)
    )

    lower = max(0.0, probability_a + probability_b - 1.0)
    upper = min(probability_a, probability_b)
    tolerance = 1e-10
    if probability_both < lower - tolerance or probability_both > upper + tolerance:
        raise ValueError("joint quadrature violated binary probability bounds")

    binary_covariance = probability_both - probability_a * probability_b
    variance_y_a = probability_a * (1.0 - probability_a)
    variance_y_b = probability_b * (1.0 - probability_b)
    return PairPredictiveMoments(
        probability_a=probability_a,
        probability_b=probability_b,
        probability_both=probability_both,
        covariance=((variance_y_a, binary_covariance), (binary_covariance, variance_y_b)),
        score_covariance=score_covariance,
        score_response_covariance=score_response_covariance,
    )


def _inverse_2x2(matrix: Matrix2) -> Matrix2:
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


def _symmetric_pseudoinverse_2x2(matrix: Matrix2) -> Matrix2:
    a = matrix[0][0]
    b = 0.5 * (matrix[0][1] + matrix[1][0])
    d = matrix[1][1]
    scale = max(abs(a), abs(b), abs(d), 1.0)
    tolerance = 1e-12 * scale
    if a < -tolerance or d < -tolerance:
        raise ValueError("score covariance must be positive semidefinite")

    trace = a + d
    discriminant = sqrt(max((a - d) * (a - d) + 4.0 * b * b, 0.0))
    eigenvalue_high = 0.5 * (trace + discriminant)
    eigenvalue_low = 0.5 * (trace - discriminant)
    if eigenvalue_low < -tolerance:
        raise ValueError("score covariance must be positive semidefinite")

    angle = 0.5 * atan2(2.0 * b, a - d)
    cosine = cos(angle)
    sine = sin(angle)
    inverse_high = 1.0 / eigenvalue_high if eigenvalue_high > tolerance else 0.0
    inverse_low = 1.0 / eigenvalue_low if eigenvalue_low > tolerance else 0.0

    return (
        (
            inverse_high * cosine * cosine + inverse_low * sine * sine,
            (inverse_high - inverse_low) * cosine * sine,
        ),
        (
            (inverse_high - inverse_low) * cosine * sine,
            inverse_high * sine * sine + inverse_low * cosine * cosine,
        ),
    )


def _linear_bayes_columns(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
    moments: PairPredictiveMoments,
) -> tuple[Vector, Vector]:
    augmented_a = _augment(features_a)
    augmented_b = _augment(features_b)
    sigma_a = _matrix_vector(posterior.covariance, augmented_a)
    sigma_b = _matrix_vector(posterior.covariance, augmented_b)
    score_inverse = _symmetric_pseudoinverse_2x2(moments.score_covariance)
    score_response = moments.score_response_covariance

    covariance_a: list[float] = []
    covariance_b: list[float] = []
    for sigma_a_value, sigma_b_value in zip(sigma_a, sigma_b, strict=True):
        projection_a = (
            sigma_a_value * score_inverse[0][0] + sigma_b_value * score_inverse[1][0]
        )
        projection_b = (
            sigma_a_value * score_inverse[0][1] + sigma_b_value * score_inverse[1][1]
        )
        covariance_a.append(
            projection_a * score_response[0][0] + projection_b * score_response[1][0]
        )
        covariance_b.append(
            projection_a * score_response[0][1] + projection_b * score_response[1][1]
        )
    return tuple(covariance_a), tuple(covariance_b)


def linear_bayes_pair_outcomes(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> tuple[LinearBayesOutcome, ...]:
    moments = pair_predictive_moments(posterior, features_a, features_b)
    response_inverse = _inverse_2x2(moments.covariance)
    covariance_a, covariance_b = _linear_bayes_columns(
        posterior,
        features_a,
        features_b,
        moments,
    )
    dimension = len(posterior.mean)

    gain_a = tuple(
        covariance_a[index] * response_inverse[0][0] + covariance_b[index] * response_inverse[1][0]
        for index in range(dimension)
    )
    gain_b = tuple(
        covariance_a[index] * response_inverse[0][1] + covariance_b[index] * response_inverse[1][1]
        for index in range(dimension)
    )

    raw_covariance = tuple(
        tuple(
            posterior.covariance[row][column]
            - gain_a[row] * covariance_a[column]
            - gain_b[row] * covariance_b[column]
            for column in range(dimension)
        )
        for row in range(dimension)
    )
    updated_covariance = tuple(
        tuple(
            0.5 * (raw_covariance[row][column] + raw_covariance[column][row])
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
        if probability < -1e-10:
            raise ValueError("joint quadrature produced negative outcome probability")
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
