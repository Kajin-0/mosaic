from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from math import exp, log, log1p, sqrt
from random import Random

from .science_s1 import acceptance_probability, pair_fisher_information, sigmoid

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]
CandidatePair = tuple[int, int]


@dataclass(frozen=True)
class BinaryObservation:
    features: Vector
    accepted: bool


@dataclass(frozen=True)
class LaplacePosterior:
    mean: Vector
    covariance: Matrix
    precision: Matrix
    converged: bool
    iterations: int


@dataclass(frozen=True)
class SimulationMetrics:
    coefficient_rmse: float
    expected_log_loss: float
    probability_mse: float
    top_k_regret: float
    top_k_overlap: float
    interval_coverage: float


@dataclass(frozen=True)
class SimulationResult:
    policy: str
    query_count: int
    selected_pairs: tuple[CandidatePair, ...]
    posterior: LaplacePosterior
    metrics: SimulationMetrics


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions must agree")
    return sum(float(a) * float(b) for a, b in zip(left, right, strict=True))


def _augment(features: Sequence[float]) -> Vector:
    return (1.0, *(float(value) for value in features))


def _softplus(value: float) -> float:
    if value >= 0.0:
        return value + log1p(exp(-value))
    return log1p(exp(value))


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


def _solve_spd(matrix: Sequence[Sequence[float]], right: Sequence[float]) -> Vector:
    lower = _cholesky(matrix)
    dimension = len(lower)
    if len(right) != dimension:
        raise ValueError("right-hand vector dimension must match matrix")

    forward = [0.0] * dimension
    for row in range(dimension):
        forward[row] = (
            float(right[row]) - sum(lower[row][column] * forward[column] for column in range(row))
        ) / lower[row][row]

    solution = [0.0] * dimension
    for row in range(dimension - 1, -1, -1):
        solution[row] = (
            forward[row]
            - sum(lower[column][row] * solution[column] for column in range(row + 1, dimension))
        ) / lower[row][row]
    return tuple(solution)


def _inverse_spd(matrix: Sequence[Sequence[float]]) -> Matrix:
    dimension = len(matrix)
    columns: list[Vector] = []
    for column in range(dimension):
        basis = [0.0] * dimension
        basis[column] = 1.0
        columns.append(_solve_spd(matrix, basis))

    return tuple(
        tuple(columns[column][row] for column in range(dimension)) for row in range(dimension)
    )


def _log_determinant_spd(matrix: Sequence[Sequence[float]]) -> float:
    lower = _cholesky(matrix)
    return 2.0 * sum(log(lower[index][index]) for index in range(len(lower)))


def _add_matrices(
    left: Sequence[Sequence[float]],
    right: Sequence[Sequence[float]],
) -> Matrix:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row) for left_row, right_row in zip(left, right, strict=True)
    ):
        raise ValueError("matrix dimensions must agree")
    return tuple(
        tuple(float(a) + float(b) for a, b in zip(left_row, right_row, strict=True))
        for left_row, right_row in zip(left, right, strict=True)
    )


def _negative_log_posterior(
    alpha: Sequence[float],
    observations: Sequence[BinaryObservation],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
) -> float:
    if len(alpha) != len(prior_mean) or len(alpha) != len(prior_variances):
        raise ValueError("prior and parameter dimensions must agree")

    value = 0.0
    for coefficient, mean, variance in zip(alpha, prior_mean, prior_variances, strict=True):
        if variance <= 0.0:
            raise ValueError("prior variances must be positive")
        value += 0.5 * (float(coefficient) - float(mean)) ** 2 / float(variance)

    for observation in observations:
        augmented = _augment(observation.features)
        if len(augmented) != len(alpha):
            raise ValueError("observation feature dimension does not match parameter dimension")
        score = _dot(alpha, augmented)
        target = 1.0 if observation.accepted else 0.0
        value += _softplus(score) - target * score
    return value


def _gradient_and_hessian(
    alpha: Sequence[float],
    observations: Sequence[BinaryObservation],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
) -> tuple[Vector, Matrix]:
    dimension = len(alpha)
    if dimension == 0 or len(prior_mean) != dimension or len(prior_variances) != dimension:
        raise ValueError("prior and parameter dimensions must agree")

    gradient = [0.0] * dimension
    hessian = [[0.0] * dimension for _ in range(dimension)]
    for index, (coefficient, mean, variance) in enumerate(
        zip(alpha, prior_mean, prior_variances, strict=True)
    ):
        if variance <= 0.0:
            raise ValueError("prior variances must be positive")
        gradient[index] = (float(coefficient) - float(mean)) / float(variance)
        hessian[index][index] = 1.0 / float(variance)

    for observation in observations:
        augmented = _augment(observation.features)
        if len(augmented) != dimension:
            raise ValueError("observation feature dimension does not match parameter dimension")
        probability = sigmoid(_dot(alpha, augmented))
        target = 1.0 if observation.accepted else 0.0
        weight = probability * (1.0 - probability)
        for row in range(dimension):
            gradient[row] += (probability - target) * augmented[row]
            for column in range(dimension):
                hessian[row][column] += weight * augmented[row] * augmented[column]

    return tuple(gradient), tuple(tuple(row) for row in hessian)


def fit_logistic_laplace(
    observations: Sequence[BinaryObservation],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
    *,
    initial_mean: Sequence[float] | None = None,
    tolerance: float = 1e-9,
    max_iterations: int = 50,
) -> LaplacePosterior:
    """Fit Gaussian-prior logistic regression by Newton MAP plus Laplace covariance."""
    if not prior_mean or len(prior_mean) != len(prior_variances):
        raise ValueError("prior vectors must be nonempty and have equal dimension")
    if tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("tolerance and max_iterations must be positive")

    alpha = [float(value) for value in (prior_mean if initial_mean is None else initial_mean)]
    if len(alpha) != len(prior_mean):
        raise ValueError("initial_mean dimension must match prior")

    converged = False
    iterations = 0
    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        gradient, hessian = _gradient_and_hessian(
            alpha,
            observations,
            prior_mean,
            prior_variances,
        )
        newton_step = _solve_spd(hessian, gradient)
        if max(abs(value) for value in newton_step) <= tolerance:
            converged = True
            break

        current_value = _negative_log_posterior(
            alpha,
            observations,
            prior_mean,
            prior_variances,
        )
        directional_derivative = _dot(gradient, newton_step)
        step_scale = 1.0
        accepted_step = False
        for _ in range(30):
            candidate = [
                value - step_scale * step for value, step in zip(alpha, newton_step, strict=True)
            ]
            candidate_value = _negative_log_posterior(
                candidate,
                observations,
                prior_mean,
                prior_variances,
            )
            if candidate_value <= (current_value - 1e-4 * step_scale * directional_derivative):
                alpha = candidate
                accepted_step = True
                break
            step_scale *= 0.5

        if not accepted_step:
            break

    gradient, precision = _gradient_and_hessian(
        alpha,
        observations,
        prior_mean,
        prior_variances,
    )
    if max(abs(value) for value in gradient) <= max(tolerance, 1e-7):
        converged = True
    covariance = _inverse_spd(precision)
    return LaplacePosterior(
        mean=tuple(alpha),
        covariance=covariance,
        precision=precision,
        converged=converged,
        iterations=iterations,
    )


def boundary_pair_score(
    posterior_mean: Sequence[float],
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> float:
    probability_a = acceptance_probability(posterior_mean, features_a)
    probability_b = acceptance_probability(posterior_mean, features_b)
    return probability_a * (1.0 - probability_a) + probability_b * (1.0 - probability_b)


def d_optimal_pair_score(
    posterior: LaplacePosterior,
    features_a: Sequence[float],
    features_b: Sequence[float],
) -> float:
    information = pair_fisher_information(posterior.mean, features_a, features_b)
    updated_precision = _add_matrices(posterior.precision, information)
    return 0.5 * (
        _log_determinant_spd(updated_precision) - _log_determinant_spd(posterior.precision)
    )


def choose_pair(
    policy: str,
    remaining_pairs: Sequence[CandidatePair],
    candidates: Sequence[Sequence[float]],
    posterior: LaplacePosterior,
    *,
    random: Random,
) -> CandidatePair:
    if not remaining_pairs:
        raise ValueError("remaining_pairs must not be empty")
    if policy == "random":
        return random.choice(tuple(remaining_pairs))
    if policy not in {"boundary", "d_optimal"}:
        raise ValueError("policy must be random, boundary, or d_optimal")

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
        if policy == "boundary":
            score = boundary_pair_score(posterior.mean, features_a, features_b)
        else:
            score = d_optimal_pair_score(posterior, features_a, features_b)
        if score > best_score or (score == best_score and pair < best_pair):
            best_score = score
            best_pair = pair
    return best_pair


def evaluate_ground_truth(
    true_alpha: Sequence[float],
    posterior: LaplacePosterior,
    heldout_features: Sequence[Sequence[float]],
    *,
    top_k: int,
) -> SimulationMetrics:
    if not heldout_features:
        raise ValueError("heldout_features must not be empty")
    if top_k <= 0 or top_k > len(heldout_features):
        raise ValueError("top_k must be within the held-out bank")
    if len(true_alpha) != len(posterior.mean):
        raise ValueError("true and posterior parameter dimensions must agree")

    true_probabilities = [
        acceptance_probability(true_alpha, features) for features in heldout_features
    ]
    predicted_probabilities = [
        acceptance_probability(posterior.mean, features) for features in heldout_features
    ]

    expected_log_loss = 0.0
    probability_mse = 0.0
    for truth, prediction in zip(
        true_probabilities,
        predicted_probabilities,
        strict=True,
    ):
        clipped = min(max(prediction, 1e-15), 1.0 - 1e-15)
        expected_log_loss += -truth * log(clipped) - (1.0 - truth) * log(1.0 - clipped)
        probability_mse += (truth - prediction) ** 2
    expected_log_loss /= len(heldout_features)
    probability_mse /= len(heldout_features)

    true_ranking = sorted(
        range(len(heldout_features)),
        key=true_probabilities.__getitem__,
        reverse=True,
    )
    predicted_ranking = sorted(
        range(len(heldout_features)),
        key=predicted_probabilities.__getitem__,
        reverse=True,
    )
    true_top = true_ranking[:top_k]
    predicted_top = predicted_ranking[:top_k]
    optimal_value = sum(true_probabilities[index] for index in true_top) / top_k
    predicted_value = sum(true_probabilities[index] for index in predicted_top) / top_k
    top_k_regret = optimal_value - predicted_value
    top_k_overlap = len(set(true_top).intersection(predicted_top)) / top_k

    coefficient_rmse = sqrt(
        sum(
            (float(truth) - float(estimate)) ** 2
            for truth, estimate in zip(true_alpha, posterior.mean, strict=True)
        )
        / len(true_alpha)
    )
    interval_coverage = sum(
        abs(float(truth) - posterior.mean[index]) <= 1.96 * sqrt(posterior.covariance[index][index])
        for index, truth in enumerate(true_alpha)
    ) / len(true_alpha)

    return SimulationMetrics(
        coefficient_rmse=coefficient_rmse,
        expected_log_loss=expected_log_loss,
        probability_mse=probability_mse,
        top_k_regret=top_k_regret,
        top_k_overlap=top_k_overlap,
        interval_coverage=interval_coverage,
    )


def run_ground_truth_simulation(
    *,
    policy: str,
    true_alpha: Sequence[float],
    candidates: Sequence[Sequence[float]],
    heldout_features: Sequence[Sequence[float]],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
    query_count: int,
    top_k: int,
    seed: int,
) -> SimulationResult:
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")

    remaining = list(combinations(range(len(candidates)), 2))
    if query_count > len(remaining):
        raise ValueError("query_count exceeds number of unique candidate pairs")

    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    selected_pairs: list[CandidatePair] = []
    selection_random = Random(seed ^ 0x5DEECE66D)
    response_random = Random(seed ^ 0xC0FFEE)

    for _ in range(query_count):
        pair = choose_pair(
            policy,
            remaining,
            candidates,
            posterior,
            random=selection_random,
        )
        remaining.remove(pair)
        selected_pairs.append(pair)
        for candidate_index in pair:
            features = tuple(float(value) for value in candidates[candidate_index])
            probability = acceptance_probability(true_alpha, features)
            observations.append(
                BinaryObservation(
                    features=features,
                    accepted=response_random.random() < probability,
                )
            )
        posterior = fit_logistic_laplace(
            observations,
            prior_mean,
            prior_variances,
            initial_mean=posterior.mean,
        )

    return SimulationResult(
        policy=policy,
        query_count=query_count,
        selected_pairs=tuple(selected_pairs),
        posterior=posterior,
        metrics=evaluate_ground_truth(
            true_alpha,
            posterior,
            heldout_features,
            top_k=top_k,
        ),
    )


def make_gaussian_scenario(
    *,
    feature_dimension: int,
    candidate_count: int,
    heldout_count: int,
    seed: int,
    slope_scale: float = 0.9,
    intercept: float = 0.0,
) -> tuple[Vector, tuple[Vector, ...], tuple[Vector, ...]]:
    if feature_dimension <= 0 or candidate_count < 2 or heldout_count <= 0:
        raise ValueError("scenario dimensions and counts must be positive")
    if slope_scale < 0.0:
        raise ValueError("slope_scale must be nonnegative")

    random = Random(seed)
    coefficient_scale = slope_scale / sqrt(feature_dimension)
    true_alpha = (
        float(intercept),
        *(random.gauss(0.0, coefficient_scale) for _ in range(feature_dimension)),
    )
    candidates = tuple(
        tuple(random.gauss(0.0, 1.0) for _ in range(feature_dimension))
        for _ in range(candidate_count)
    )
    heldout = tuple(
        tuple(random.gauss(0.0, 1.0) for _ in range(feature_dimension))
        for _ in range(heldout_count)
    )
    return true_alpha, candidates, heldout
