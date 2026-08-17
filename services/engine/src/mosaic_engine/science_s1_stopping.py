from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import acos, atan2, pi, sqrt
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


@dataclass(frozen=True)
class PosteriorTransverseSignal:
    raw_norm: float
    raw_norm_sq: float
    covariance_trace: float
    parallel_variance: float
    transverse_variance: float
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


def _quadratic_form(vector: Sequence[float], matrix: Sequence[Sequence[float]]) -> float:
    if len(matrix) != len(vector) or any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector dimensions must agree")
    return sum(
        float(vector[row])
        * sum(float(matrix[row][column]) * float(vector[column]) for column in range(len(vector)))
        for row in range(len(vector))
    )


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
    """Estimate how much fitted slope norm remains after full covariance debiasing."""
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


def posterior_transverse_signal(posterior: LaplacePosterior) -> PosteriorTransverseSignal:
    """Debias fitted slope norm using only covariance that can rotate its direction."""
    slope_mean, covariance = _slope_marginal(posterior)
    raw_norm_sq = sum(value * value for value in slope_mean)
    raw_norm = sqrt(raw_norm_sq)
    covariance_trace = sum(covariance[index][index] for index in range(len(covariance)))

    if raw_norm > 1e-15:
        direction = tuple(value / raw_norm for value in slope_mean)
        parallel_variance = _quadratic_form(direction, covariance)
    else:
        parallel_variance = 0.0

    transverse_variance = max(covariance_trace - parallel_variance, 0.0)
    debiased_norm_sq = max(raw_norm_sq - transverse_variance, 0.0)
    debiased_norm = sqrt(debiased_norm_sq)
    retained_fraction = debiased_norm / raw_norm if raw_norm > 1e-15 else 0.0
    return PosteriorTransverseSignal(
        raw_norm=raw_norm,
        raw_norm_sq=raw_norm_sq,
        covariance_trace=covariance_trace,
        parallel_variance=parallel_variance,
        transverse_variance=transverse_variance,
        debiased_norm=debiased_norm,
        debiased_norm_sq=debiased_norm_sq,
        retained_fraction=retained_fraction,
    )


def _validate_risk_arguments(reference_norm: float, quantile: float, sample_count: int) -> None:
    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if quantile <= 0.0 or quantile > 1.0:
        raise ValueError("quantile must lie in (0, 1]")
    if reference_norm < 0.0:
        raise ValueError("reference_norm must be nonnegative")


def _posterior_directional_risk_with_reference_norm(
    posterior: LaplacePosterior,
    *,
    reference_norm: float,
    quantile: float,
    sample_count: int,
    seed: int,
) -> PosteriorDirectionalRisk:
    _validate_risk_arguments(reference_norm, quantile, sample_count)
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


def _posterior_tangent_risk_with_reference_norm(
    posterior: LaplacePosterior,
    *,
    reference_norm: float,
    quantile: float,
    sample_count: int,
    seed: int,
) -> PosteriorDirectionalRisk:
    """Evaluate first-order angular uncertainty from transverse posterior noise only."""
    _validate_risk_arguments(reference_norm, quantile, sample_count)
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
    lower = _cholesky(covariance)
    random = Random(seed)
    errors: list[float] = []

    for _ in range(sample_count):
        standard = [random.gauss(0.0, 1.0) for _ in direction]
        delta = tuple(
            sum(lower[row][column] * standard[column] for column in range(row + 1))
            for row in range(len(direction))
        )
        parallel = _dot(direction, delta)
        transverse = tuple(
            delta[index] - parallel * direction[index] for index in range(len(direction))
        )
        angle = atan2(_norm(transverse), reference_norm)
        errors.append(angle / pi)

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
    """Estimate posterior uncertainty in Gaussian-population ranking direction."""
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
    """Evaluate angular uncertainty after subtracting full slope-covariance energy."""
    radial = posterior_radial_signal(posterior)
    return _posterior_directional_risk_with_reference_norm(
        posterior,
        reference_norm=radial.debiased_norm,
        quantile=quantile,
        sample_count=sample_count,
        seed=seed,
    )


def posterior_transverse_debiased_directional_risk(
    posterior: LaplacePosterior,
    *,
    quantile: float = 0.95,
    sample_count: int = 512,
    seed: int = 0,
) -> PosteriorDirectionalRisk:
    """Evaluate full-noise angular uncertainty after transverse norm debiasing."""
    transverse = posterior_transverse_signal(posterior)
    return _posterior_directional_risk_with_reference_norm(
        posterior,
        reference_norm=transverse.debiased_norm,
        quantile=quantile,
        sample_count=sample_count,
        seed=seed,
    )


def posterior_transverse_tangent_directional_risk(
    posterior: LaplacePosterior,
    *,
    quantile: float = 0.95,
    sample_count: int = 512,
    seed: int = 0,
) -> PosteriorDirectionalRisk:
    """Estimate ranking-direction uncertainty in the local tangent space.

    The reference scale uses transverse-debiased fitted norm from v12d. Posterior
    perturbations are sampled from the full Laplace slope covariance, projected with
    ``I - uu.T``, and converted to angle as ``atan2(||delta_perp||, B_perp_db)``.
    Pure longitudinal perturbations therefore contribute zero first-order angular risk.

    This remains a candidate synthetic stopping statistic, not a calibrated confidence
    bound until its prospective operating characteristics are measured.
    """
    transverse = posterior_transverse_signal(posterior)
    return _posterior_tangent_risk_with_reference_norm(
        posterior,
        reference_norm=transverse.debiased_norm,
        quantile=quantile,
        sample_count=sample_count,
        seed=seed,
    )
