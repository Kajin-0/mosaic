from __future__ import annotations

from collections.abc import Callable, Sequence
from math import expm1, log, pi, sqrt

from .science_s1 import sigmoid
from .science_s1_simulation import LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]
CandidatePair = tuple[int, int]

# Nine-point Gauss-Hermite rule for integrals with weight exp(-x^2).
# Standard-normal expectations use x -> mu + sqrt(2 * variance) * node
# and divide the weighted sum by sqrt(pi).
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
_SQRT_PI = sqrt(pi)
_LOG_TWO = log(2.0)


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


def _normal_expectation(
    mean: float,
    variance: float,
    function: Callable[[float], float],
) -> float:
    if variance < -1e-12:
        raise ValueError("variance must be nonnegative")
    if variance <= 1e-14:
        return function(mean)

    scale = sqrt(2.0 * max(variance, 0.0))
    return (
        sum(
            weight * function(mean + scale * node)
            for node, weight in zip(_GH9_NODES, _GH9_WEIGHTS, strict=True)
        )
        / _SQRT_PI
    )


def posterior_score_moments(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> tuple[float, float]:
    augmented = _augment(features)
    if len(augmented) != len(posterior.mean):
        raise ValueError("feature dimension does not match posterior")
    mean = _dot(posterior.mean, augmented)
    variance = _quadratic_form(posterior.covariance, augmented)
    if variance < -1e-10:
        raise ValueError("posterior covariance produced a negative score variance")
    return mean, max(variance, 0.0)


def bernoulli_entropy(probability: float) -> float:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie within [0, 1]")
    if probability == 0.0 or probability == 1.0:
        return 0.0
    return -probability * log(probability) - (1.0 - probability) * log(1.0 - probability)


def posterior_mean_acceptance(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> float:
    mean, variance = posterior_score_moments(posterior, features)
    return _normal_expectation(mean, variance, sigmoid)


def posterior_expected_fisher_weight(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> float:
    mean, variance = posterior_score_moments(posterior, features)
    return _normal_expectation(
        mean,
        variance,
        lambda score: sigmoid(score) * (1.0 - sigmoid(score)),
    )


def _rank_one_information(weight: float, features: Sequence[float]) -> Matrix:
    if weight < 0.0:
        raise ValueError("information weight must be nonnegative")
    augmented = _augment(features)
    return tuple(
        tuple(weight * row_value * column_value for column_value in augmented)
        for row_value in augmented
    )


def posterior_expected_fisher_information(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> Matrix:
    return _rank_one_information(
        posterior_expected_fisher_weight(posterior, features),
        features,
    )


def binary_parameter_mutual_information(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> float:
    """Approximate I(alpha; Y | x, D) in nats under the Laplace posterior.

    For Y|alpha,x ~ Bernoulli(sigmoid(alpha^T z)), the exact Bayesian identity is

        I(alpha;Y) = H(E[p]) - E[H(p)].

    Only the one-dimensional Gaussian score alpha^T z must be integrated.
    """
    mean, variance = posterior_score_moments(posterior, features)
    predictive_probability = _normal_expectation(mean, variance, sigmoid)
    expected_conditional_entropy = _normal_expectation(
        mean,
        variance,
        lambda score: bernoulli_entropy(sigmoid(score)),
    )
    information = bernoulli_entropy(predictive_probability) - expected_conditional_entropy
    return min(max(information, 0.0), _LOG_TWO)


def mutual_information_equivalent_information(
    posterior: LaplacePosterior,
    features: Sequence[float],
) -> Matrix:
    """Map exact binary mutual information to a rank-one Gaussian-equivalent matrix.

    Let v = z^T Sigma z and choose lambda so that a rank-one Gaussian precision
    update lambda z z^T has the same entropy reduction as the binary mutual
    information for this candidate:

        0.5 log(1 + lambda v) = I(alpha;Y|x,D).

    Therefore lambda = expm1(2 I) / v.  As v -> 0, this tends to the local
    Bernoulli Fisher weight, while for broad posteriors the one-response gain is
    bounded by log(2) nats.
    """
    _, variance = posterior_score_moments(posterior, features)
    if variance <= 1e-12:
        return posterior_expected_fisher_information(posterior, features)

    information = binary_parameter_mutual_information(posterior, features)
    equivalent_weight = expm1(2.0 * information) / variance
    return _rank_one_information(equivalent_weight, features)


def _cholesky(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    dimension = len(matrix)
    if dimension == 0 or any(len(row) != dimension for row in matrix):
        raise ValueError("matrix must be nonempty and square")
    lower = [[0.0] * dimension for _ in range(dimension)]
    for row in range(dimension):
        for column in range(row + 1):
            previous = sum(lower[row][index] * lower[column][index] for index in range(column))
            if row == column:
                diagonal = float(matrix[row][row]) - previous
                if diagonal <= 0.0:
                    raise ValueError("matrix must be positive definite")
                lower[row][column] = sqrt(diagonal)
            else:
                lower[row][column] = (float(matrix[row][column]) - previous) / lower[column][column]
    return lower


def _log_determinant_spd(matrix: Sequence[Sequence[float]]) -> float:
    lower = _cholesky(matrix)
    return 2.0 * sum(log(lower[index][index]) for index in range(len(lower)))


def _add_information(
    precision: Sequence[Sequence[float]],
    information_a: Sequence[Sequence[float]],
    information_b: Sequence[Sequence[float]],
) -> Matrix:
    dimension = len(precision)
    if (
        dimension == 0
        or len(information_a) != dimension
        or len(information_b) != dimension
        or any(
            len(precision[row]) != dimension
            or len(information_a[row]) != dimension
            or len(information_b[row]) != dimension
            for row in range(dimension)
        )
    ):
        raise ValueError("precision and information matrices must have equal square dimensions")
    return tuple(
        tuple(
            float(precision[row][column])
            + float(information_a[row][column])
            + float(information_b[row][column])
            for column in range(dimension)
        )
        for row in range(dimension)
    )


def choose_uncertainty_aware_pair(
    policy: str,
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
) -> CandidatePair:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")
    if policy == "posterior_fisher_d_optimal":
        information_function = posterior_expected_fisher_information
    elif policy == "mutual_information_d_optimal":
        information_function = mutual_information_equivalent_information
    else:
        raise ValueError(
            "policy must be posterior_fisher_d_optimal or mutual_information_d_optimal"
        )

    candidate_information = tuple(
        information_function(posterior, features) for features in candidates
    )
    baseline_log_determinant = _log_determinant_spd(posterior.precision)

    best_pair = remaining_pairs[0]
    best_score = float("-inf")
    for pair in remaining_pairs:
        first, second = pair
        if first == second or first < 0 or second < 0:
            raise ValueError("candidate pair indices must be distinct and nonnegative")
        try:
            information_a = candidate_information[first]
            information_b = candidate_information[second]
        except IndexError as error:
            raise ValueError("candidate pair index is out of range") from error
        updated_precision = _add_information(
            posterior.precision,
            information_a,
            information_b,
        )
        score = 0.5 * (_log_determinant_spd(updated_precision) - baseline_log_determinant)
        if score > best_score or (score == best_score and pair < best_pair):
            best_score = score
            best_pair = pair
    return best_pair
