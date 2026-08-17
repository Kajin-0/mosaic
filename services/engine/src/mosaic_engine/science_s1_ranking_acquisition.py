from __future__ import annotations

from collections.abc import Sequence
from math import erfc, exp, pi, sqrt

from .science_s1_decision_acquisition import linear_bayes_pair_outcomes
from .science_s1_simulation import CandidatePair, LaplacePosterior

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]
_SQRT_TWO = sqrt(2.0)
_INV_SQRT_TWO_PI = 1.0 / sqrt(2.0 * pi)


def _augment_difference(feature_difference: Sequence[float]) -> Vector:
    # Intercept cancels in every pairwise ordering comparison.
    return (0.0, *(float(value) for value in feature_difference))


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


def normal_cdf_negative_nonnegative(value: float) -> float:
    """Return Phi(-value) for value >= 0 without a scipy dependency."""
    if value < 0.0:
        raise ValueError("value must be nonnegative")
    return 0.5 * erfc(value / _SQRT_TWO)


def normal_pdf(value: float) -> float:
    return _INV_SQRT_TWO_PI * exp(-0.5 * value * value)


def pairwise_misorder_probability(mean_difference: float, variance_difference: float) -> float:
    """Posterior probability that the sign of the mean score difference is wrong."""
    if variance_difference < -1e-10:
        raise ValueError("variance must be nonnegative")
    variance_difference = max(float(variance_difference), 0.0)
    if variance_difference <= 1e-14:
        return 0.0
    standardized = abs(float(mean_difference)) / sqrt(variance_difference)
    return normal_cdf_negative_nonnegative(standardized)


def pairwise_linear_score_regret(mean_difference: float, variance_difference: float) -> float:
    """Expected regret from committing to the sign of the posterior mean score.

    If Delta ~ Normal(mu, sigma^2), the Bayes action under linear score utility
    chooses the sign of mu.  The statewise loss is the magnitude of Delta only
    when that chosen ordering is wrong.  The posterior expected loss is

        sigma * phi(|mu|/sigma) - |mu| * Phi(-|mu|/sigma).
    """
    if variance_difference < -1e-10:
        raise ValueError("variance must be nonnegative")
    variance_difference = max(float(variance_difference), 0.0)
    if variance_difference <= 1e-14:
        return 0.0
    standard_deviation = sqrt(variance_difference)
    absolute_mean = abs(float(mean_difference))
    standardized = absolute_mean / standard_deviation
    return max(
        standard_deviation * normal_pdf(standardized)
        - absolute_mean * normal_cdf_negative_nonnegative(standardized),
        0.0,
    )


def reference_pair_risks(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    reference_differences: Sequence[Sequence[float]],
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if not reference_differences:
        raise ValueError("reference_differences must not be empty")

    misorder_probabilities: list[float] = []
    score_regrets: list[float] = []
    for feature_difference in reference_differences:
        augmented = _augment_difference(feature_difference)
        if len(augmented) != len(mean):
            raise ValueError("reference difference dimension does not match posterior state")
        mean_difference = _dot(mean, augmented)
        variance_difference = _quadratic_form(covariance, augmented)
        misorder_probabilities.append(
            pairwise_misorder_probability(mean_difference, variance_difference)
        )
        score_regrets.append(pairwise_linear_score_regret(mean_difference, variance_difference))
    return tuple(misorder_probabilities), tuple(score_regrets)


def population_ranking_risk(
    mean: Sequence[float],
    covariance: Sequence[Sequence[float]],
    reference_differences: Sequence[Sequence[float]],
) -> tuple[float, float]:
    misorder_probabilities, score_regrets = reference_pair_risks(
        mean,
        covariance,
        reference_differences,
    )
    count = len(score_regrets)
    return (
        sum(misorder_probabilities) / count,
        sum(score_regrets) / count,
    )


def expected_population_score_regret_reduction(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
    reference_differences: Sequence[Sequence[float]],
    *,
    current_score_regret: float | None = None,
) -> float:
    if current_score_regret is None:
        _, current_score_regret = population_ranking_risk(
            posterior.mean,
            posterior.covariance,
            reference_differences,
        )

    expected_updated_regret = 0.0
    for outcome in linear_bayes_pair_outcomes(posterior, features_a, features_b):
        _, outcome_regret = population_ranking_risk(
            outcome.mean,
            outcome.covariance,
            reference_differences,
        )
        expected_updated_regret += outcome.probability * outcome_regret
    return current_score_regret - expected_updated_regret


def choose_population_score_regret_pair(
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
    reference_differences: Sequence[Sequence[float]],
) -> tuple[CandidatePair, float]:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")

    _, current_score_regret = population_ranking_risk(
        posterior.mean,
        posterior.covariance,
        reference_differences,
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
        score = expected_population_score_regret_reduction(
            posterior,
            features_a,
            features_b,
            reference_differences,
            current_score_regret=current_score_regret,
        )
        if score > best_score or (score == best_score and pair < best_pair):
            best_pair = pair
            best_score = score
    return best_pair, best_score
