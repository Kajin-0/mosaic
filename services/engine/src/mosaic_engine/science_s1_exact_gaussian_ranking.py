from __future__ import annotations

from collections.abc import Sequence
from math import exp, gamma, log, pi, sqrt

from .science_s1_decision_acquisition import linear_bayes_pair_outcomes
from .science_s1_simulation import CandidatePair, LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]

# 24-point Gauss-Legendre rule mapped to [0, 1].  The exact Gaussian-reference
# expected norm is one-dimensional regardless of slope dimension.
_GL24_NODES = (
    0.0024063900014893447,
    0.012635722014345263,
    0.030862723998633601,
    0.056792236497799464,
    0.089999007013048526,
    0.12993790421072282,
    0.17595317403151223,
    0.22728926430558022,
    0.28310324618697746,
    0.3424786601519183,
    0.40444056626319186,
    0.46797155356869719,
    0.53202844643130276,
    0.5955594337368082,
    0.6575213398480817,
    0.71689675381302254,
    0.77271073569441984,
    0.82404682596848777,
    0.87006209578927718,
    0.91000099298695147,
    0.94320776350220048,
    0.96913727600136634,
    0.98736427798565474,
    0.99759360999851066,
)
_GL24_WEIGHTS = (
    0.0061706148999943452,
    0.01426569431446678,
    0.022138719408709706,
    0.02964929245771818,
    0.036673240705540081,
    0.043095080765976602,
    0.048809326052056963,
    0.053722135057982782,
    0.057752834026862758,
    0.060835236463901647,
    0.062918728173414123,
    0.06396909767337601,
    0.06396909767337601,
    0.062918728173414123,
    0.060835236463901647,
    0.057752834026862758,
    0.053722135057982782,
    0.048809326052056963,
    0.043095080765976602,
    0.036673240705540081,
    0.02964929245771818,
    0.022138719408709706,
    0.01426569431446678,
    0.0061706148999943452,
)
_SQRT_PI = sqrt(pi)


def _euclidean_norm(vector: Sequence[float]) -> float:
    return sqrt(sum(float(value) * float(value) for value in vector))


def _validate_covariance(covariance: Sequence[Sequence[float]], dimension: int) -> None:
    if len(covariance) != dimension or any(len(row) != dimension for row in covariance):
        raise ValueError("covariance dimension does not match mean")
    for row in range(dimension):
        for column in range(dimension):
            if abs(float(covariance[row][column]) - float(covariance[column][row])) > 1e-9:
                raise ValueError("covariance must be symmetric")


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


def _solve_cholesky(lower: Sequence[Sequence[float]], right: Sequence[float]) -> Vector:
    dimension = len(lower)
    if len(right) != dimension:
        raise ValueError("right-hand side dimension does not match factor")

    forward = [0.0] * dimension
    for row in range(dimension):
        previous = sum(float(lower[row][column]) * forward[column] for column in range(row))
        forward[row] = (float(right[row]) - previous) / float(lower[row][row])

    solution = [0.0] * dimension
    for row in range(dimension - 1, -1, -1):
        previous = sum(
            float(lower[column][row]) * solution[column] for column in range(row + 1, dimension)
        )
        solution[row] = (forward[row] - previous) / float(lower[row][row])
    return tuple(solution)


def gaussian_expected_norms(
    means: Sequence[Sequence[float]],
    covariance: Sequence[Sequence[float]],
) -> tuple[float, ...]:
    """Return E||B|| for Gaussian vectors sharing one covariance.

    For B ~ N(m, Sigma),

        E||B|| = 1/(2 sqrt(pi)) int_0^inf [1-L(t)] t^(-3/2) dt,

    where

        L(t) = det(I + 2 t Sigma)^(-1/2)
               exp[-t m^T (I + 2 t Sigma)^(-1) m].

    With t = [u/(1-u)]^2 this becomes a smooth integral on (0,1),
    evaluated here by a fixed 24-point Gauss-Legendre rule.
    """
    if not means:
        raise ValueError("means must not be empty")
    dimension = len(means[0])
    if dimension == 0 or any(len(mean) != dimension for mean in means):
        raise ValueError("all means must have the same positive dimension")
    _validate_covariance(covariance, dimension)

    # A degenerate exact posterior needs no quadrature and avoids accumulating
    # tiny numerical Jensen gaps.
    if all(
        abs(float(covariance[row][column])) <= 1e-15
        for row in range(dimension)
        for column in range(dimension)
    ):
        return tuple(_euclidean_norm(mean) for mean in means)

    totals = [0.0] * len(means)
    for u, weight in zip(_GL24_NODES, _GL24_WEIGHTS, strict=True):
        ratio = u / (1.0 - u)
        t = ratio * ratio
        matrix = tuple(
            tuple(
                (1.0 if row == column else 0.0) + 2.0 * t * float(covariance[row][column])
                for column in range(dimension)
            )
            for row in range(dimension)
        )
        lower = _cholesky(matrix)
        log_determinant = 2.0 * sum(log(lower[index][index]) for index in range(dimension))
        determinant_factor = exp(-0.5 * log_determinant)

        for mean_index, mean in enumerate(means):
            solution = _solve_cholesky(lower, mean)
            quadratic = sum(float(mean[index]) * solution[index] for index in range(dimension))
            laplace_transform = determinant_factor * exp(-t * quadratic)
            totals[mean_index] += weight * (1.0 - laplace_transform) / (u * u)

    return tuple(total / _SQRT_PI for total in totals)


def gaussian_expected_norm(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
) -> float:
    return gaussian_expected_norms((mean,), covariance)[0]


def exact_gaussian_reference_ranking_risk(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
) -> float:
    """Exact-reference linear ranking regret for iid N(0,I) future candidates.

    `mean` and `covariance` are slope-only quantities: the acceptance intercept
    cancels in every future-candidate ordering comparison.

        R = [E||B|| - ||E B||] / sqrt(pi),  B ~ N(mean, covariance).
    """
    expected_norm = gaussian_expected_norm(mean, covariance)
    return max((expected_norm - _euclidean_norm(mean)) / _SQRT_PI, 0.0)


def _slope_state(posterior: LaplacePosterior) -> tuple[Vector, Matrix]:
    if len(posterior.mean) < 2:
        raise ValueError("posterior must contain intercept plus at least one slope")
    mean = tuple(float(value) for value in posterior.mean[1:])
    covariance = tuple(tuple(float(value) for value in row[1:]) for row in posterior.covariance[1:])
    return mean, covariance


def expected_exact_gaussian_ranking_regret_reduction(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
    *,
    current_risk: float | None = None,
) -> float:
    if current_risk is None:
        current_mean, current_covariance = _slope_state(posterior)
        current_risk = exact_gaussian_reference_ranking_risk(current_mean, current_covariance)

    outcomes = linear_bayes_pair_outcomes(posterior, features_a, features_b)
    slope_covariance = tuple(
        tuple(float(value) for value in row[1:]) for row in outcomes[0].covariance[1:]
    )
    slope_means = tuple(tuple(float(value) for value in outcome.mean[1:]) for outcome in outcomes)
    expected_norms = gaussian_expected_norms(slope_means, slope_covariance)

    expected_updated_risk = 0.0
    for outcome, expected_norm, slope_mean in zip(
        outcomes,
        expected_norms,
        slope_means,
        strict=True,
    ):
        outcome_risk = max((expected_norm - _euclidean_norm(slope_mean)) / _SQRT_PI, 0.0)
        expected_updated_risk += outcome.probability * outcome_risk
    return current_risk - expected_updated_risk


def choose_exact_gaussian_ranking_pair(
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
) -> tuple[CandidatePair, float]:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")

    current_mean, current_covariance = _slope_state(posterior)
    current_risk = exact_gaussian_reference_ranking_risk(current_mean, current_covariance)
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
        score = expected_exact_gaussian_ranking_regret_reduction(
            posterior,
            features_a,
            features_b,
            current_risk=current_risk,
        )
        if score > best_score or (score == best_score and pair < best_pair):
            best_pair = pair
            best_score = score
    return best_pair, best_score


def isotropic_zero_mean_expected_norm(*, dimension: int, standard_deviation: float) -> float:
    """Closed-form reference used by tests for a centered isotropic Gaussian."""
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    if standard_deviation < 0.0:
        raise ValueError("standard_deviation must be nonnegative")
    return standard_deviation * sqrt(2.0) * gamma(0.5 * (dimension + 1)) / gamma(0.5 * dimension)
