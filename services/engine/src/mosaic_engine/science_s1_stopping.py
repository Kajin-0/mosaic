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


@dataclass(frozen=True)
class PosteriorRadialSignal:
    raw_norm: float
    raw_norm_sq: float
    covariance_trace: float
    debiased_norm: float
    debiased_norm_sq: float
    retained_fraction: float


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions must agree")
    return sum(float(a) * float(b) for a, b in zip(left, right, strict=True))


def _norm(values: Sequence[float]) -> float:
    return sqrt(sum(float(value) ** 2 for value in values))


def _slope_marginal(
    posterior: LaplacePosterior,
) -> tuple[tuple[float, ...], tuple[tuple[float, ...], ...]]:
    if len(posterior.mean) < 2:
        raise ValueError("posterior must contain an intercept and at least one slope")
    slope_mean = tuple(float(value) for value in posterior.mean[1:])
    covariance = tuple(tuple(float(value) for value in row[1:]) for row in posterior.covariance[1:])
    if len(covariance) != len(slope_mean) or any(len(row) != len(slope_mean) for row in covariance):
        raise ValueError("posterior slope covariance dimensions must agree")
    return slope_mean, covariance


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


def posterior_radial_signal(posterior: LaplacePosterior) -> PosteriorRadialSignal:
    """Estimate how much fitted slope norm remains after first-order noise debiasing.

    If an approximately Gaussian estimator has mean ``beta`` and covariance ``V``, then
    ``E[||m||^2] = ||beta||^2 + tr(V)``. The Laplace slope covariance is used here as a
    posterior-observable proxy for that noise term. This is a diagnostic approximation,
    not a finite-sample unbiasedness claim or a confidence bound.
    """
    slope_mean, covariance = _slope_marginal(posterior)
    raw_norm_sq = sum(value * value for value in slope_mean)
    raw_norm = sqrt(raw_norm_sq)
    covariance_trace = sum(covariance[index][index] for index in range(len(covariance)))
    debiased_norm_sq = max(raw_norm_sq - covariance_trace, 0.0)
    debiased_norm = sqrt(debiased_norm_sq)
    retained_fraction = debiased_norm / raw_norm if raw_norm > 1e-15 else 0.0
    return PosteriorRadialSignal(
        raw_norm=raw_norm,
        raw_norm_sq=raw_norm_sq,
        covariance_trace=covariance_trace,
        debiased_norm=debiased_norm,
        debiased_norm_sq=debiased_norm_sq,
        retained_fraction=retained_fraction,
    )


def _posterior_directional_risk_with_reference_norm(
    posterior: LaplacePosterior,
    *,
    reference_norm: float,
    quantile: float,
    sample_count: int,
    seed: int,
) -> PosteriorDirectionalRisk:
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if quantile <= 0.0 or quantile > 1.0:
        raise ValueError("quantile must lie in (0, 1]")
    if reference_norm < 0.0:
        raise ValueError("reference_norm must be nonnegative")

    slope_mean, covariance = _slope_marginal(posterior)
    raw_norm = _norm(slope_mean)
    if raw_norm <= 1e-15 or reference_norm <= 1e-15:
        return PosteriorDirectionalRisk(
            mean_error=0.5,
            upper_error=0.5,
            slope_norm=reference_norm,
            sample_count=sample_count,
            quantile=quantile,
        )

    direction = tuple(value / raw_norm for value in slope_mean)
    reference = tuple(reference_norm * value for value in direction)
    lower = _cholesky(covariance)
    random = Random(seed)
    errors: list[float] = []

    for _ in range(sample_count):
        standard = [random.gauss(0.0, 1.0) for _ in reference]
        draw = tuple(
            reference[row] + sum(lower[row][column] * standard[column] for column in range(row + 1))
            for row in range(len(reference))
        )
        errors.append(_angle_error(reference, draw))

    return PosteriorDirectionalRisk(
        mean_error=sum(errors) / len(errors),
        upper_error=_nearest_rank_quantile(errors, quantile),
        slope_norm=reference_norm,
        sample_count=sample_count,
        quantile=quantile,
    )


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
    slope_mean, _ = _slope_marginal(posterior)
    return _posterior_directional_risk_with_reference_norm(
        posterior,
        reference_norm=_norm(slope_mean),
        quantile=quantile,
        sample_count=sample_count,
        seed=seed,
    )


def posterior_radial_debiased_directional_risk(
    posterior: LaplacePosterior,
    *,
    quantile: float = 0.95,
    sample_count: int = 512,
    seed: int = 0,
) -> PosteriorDirectionalRisk:
    """Inflate directional uncertainty by removing first-order radial noise energy.

    The fitted slope direction is retained, but its reference norm is replaced by
    ``sqrt(max(||m||^2 - tr(Sigma_beta), 0))`` before angular posterior-noise draws
    are evaluated. A zero debiased norm returns random-ordering uncertainty (0.5),
    preventing a noise-dominated fitted vector from satisfying ordinary S1 targets.

    This is a theory-motivated synthetic diagnostic. Its operating characteristics
    must be validated prospectively before any use as a calibration stopping rule.
    """
    radial = posterior_radial_signal(posterior)
    return _posterior_directional_risk_with_reference_norm(
        posterior,
        reference_norm=radial.debiased_norm,
        quantile=quantile,
        sample_count=sample_count,
        seed=seed,
    )