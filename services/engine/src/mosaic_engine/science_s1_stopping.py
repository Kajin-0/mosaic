from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import acos, pi, sqrt
from random import Random

from .science_s1_simulation import LaplacePosterior


@dataclass(frozen=True)
class PosteriorDirectionalRisk:
    mean_error: float
    upper_error: float
    slope_norm: float
    sample_count: int
    quantile: float


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions must agree")
    return sum(float(a) * float(b) for a, b in zip(left, right, strict=True))


def _norm(values: Sequence[float]) -> float:
    return sqrt(sum(float(value) ** 2 for value in values))


def _cholesky(matrix: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
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
    return tuple(tuple(row) for row in lower)


def _nearest_rank_quantile(values: Sequence[float], quantile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if quantile <= 0.0 or quantile > 1.0:
        raise ValueError("quantile must lie in (0, 1]")
    ordered = sorted(float(value) for value in values)
    rank = max(1, int((quantile * len(ordered)) + 0.999999999999))
    return ordered[min(rank - 1, len(ordered) - 1)]


def _angle_error(reference: Sequence[float], candidate: Sequence[float]) -> float:
    reference_norm = _norm(reference)
    candidate_norm = _norm(candidate)
    if reference_norm <= 1e-15 or candidate_norm <= 1e-15:
        return 0.5
    cosine = _dot(reference, candidate) / (reference_norm * candidate_norm)
    cosine = min(1.0, max(-1.0, cosine))
    return acos(cosine) / pi


def posterior_directional_risk(
    posterior: LaplacePosterior,
    *,
    quantile: float = 0.95,
    sample_count: int = 512,
    seed: int = 0,
) -> PosteriorDirectionalRisk:
    """Estimate posterior uncertainty in Gaussian-population ranking direction.

    The fitted slope mean is the operational ranking direction. Draws are taken
    from the Laplace slope marginal and converted to angular wrong-order error
    relative to that fitted direction. The result uses posterior quantities only;
    it never accesses a synthetic ground-truth coefficient vector.

    ``upper_error`` is a nearest-rank posterior quantile. It is a candidate
    stopping statistic whose frequentist false-stop behavior must be measured by
    synthetic benchmarks before any product use.
    """
    if len(posterior.mean) < 2:
        raise ValueError("posterior must contain an intercept and at least one slope")
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if quantile <= 0.0 or quantile > 1.0:
        raise ValueError("quantile must lie in (0, 1]")

    slope_mean = tuple(float(value) for value in posterior.mean[1:])
    slope_norm = _norm(slope_mean)
    if slope_norm <= 1e-15:
        return PosteriorDirectionalRisk(
            mean_error=0.5,
            upper_error=0.5,
            slope_norm=slope_norm,
            sample_count=sample_count,
            quantile=quantile,
        )

    covariance = tuple(
        tuple(float(value) for value in row[1:]) for row in posterior.covariance[1:]
    )
    lower = _cholesky(covariance)
    random = Random(seed)
    errors: list[float] = []

    for _ in range(sample_count):
        standard = [random.gauss(0.0, 1.0) for _ in slope_mean]
        draw = tuple(
            slope_mean[row]
            + sum(lower[row][column] * standard[column] for column in range(row + 1))
            for row in range(len(slope_mean))
        )
        errors.append(_angle_error(slope_mean, draw))

    return PosteriorDirectionalRisk(
        mean_error=sum(errors) / len(errors),
        upper_error=_nearest_rank_quantile(errors, quantile),
        slope_norm=slope_norm,
        sample_count=sample_count,
        quantile=quantile,
    )
