from __future__ import annotations

from collections.abc import Sequence
from math import acos, atan, exp, pi, sqrt, tan

Vector = tuple[float, ...]
_SQRT_TWO_PI = sqrt(2.0 * pi)


def gaussian_population_ordering_error_from_cosine(cosine: float) -> float:
    """Return exact wrong-order probability for isotropic Gaussian candidate differences.

    For nonzero true and fitted slope vectors with cosine ``rho``, independent
    isotropic Gaussian candidates give jointly Gaussian score differences whose
    sign-disagreement probability is ``acos(rho) / pi``. Logistic monotonicity
    preserves the ordering, and the intercept cancels from candidate differences.
    """
    value = float(cosine)
    if value < -1.0 or value > 1.0:
        raise ValueError("cosine must be within [-1, 1]")
    return acos(value) / pi


def _logistic_fisher_weight(score: float) -> float:
    if score >= 0.0:
        exponential = exp(-score)
    else:
        exponential = exp(score)
    return exponential / (1.0 + exponential) ** 2


def gaussian_logistic_transverse_fisher_weight(
    slope_norm: float,
    *,
    integration_limit: float = 8.0,
    intervals: int = 2048,
) -> float:
    """Evaluate a(B)=E[sigma(BZ)(1-sigma(BZ))] for Z~N(0,1).

    For an isotropic Gaussian candidate population and a slope vector with norm
    ``B``, this is the per-observation Fisher eigenvalue in every direction
    orthogonal to the true slope. The integral is evaluated by deterministic
    Simpson quadrature; the default +/-8 standard-deviation truncation makes the
    omitted Gaussian mass negligible for S1 benchmark purposes.
    """
    if slope_norm < 0.0:
        raise ValueError("slope_norm must be nonnegative")
    if integration_limit <= 0.0:
        raise ValueError("integration_limit must be positive")
    if intervals <= 0 or intervals % 2 != 0:
        raise ValueError("intervals must be a positive even integer")

    lower = -float(integration_limit)
    upper = float(integration_limit)
    step = (upper - lower) / intervals

    def integrand(z_value: float) -> float:
        normal_density = exp(-0.5 * z_value * z_value) / _SQRT_TWO_PI
        return normal_density * _logistic_fisher_weight(float(slope_norm) * z_value)

    total = integrand(lower) + integrand(upper)
    for index in range(1, intervals):
        coefficient = 4.0 if index % 2 == 1 else 2.0
        total += coefficient * integrand(lower + index * step)
    return total * step / 3.0


def boundary_directional_information_coordinate(*, kappa: float, slope_norm: float) -> float:
    """Return eta_0 = B^2 kappa / 4 for the ideal p=0.5 boundary limit."""
    if kappa <= 0.0:
        raise ValueError("kappa must be positive")
    if slope_norm <= 0.0:
        raise ValueError("slope_norm must be positive")
    return float(slope_norm) ** 2 * float(kappa) / 4.0


def gaussian_logistic_directional_information_coordinate(
    *,
    kappa: float,
    slope_norm: float,
) -> float:
    """Return eta_F = B^2 kappa a(B) for isotropic Gaussian logistic sampling."""
    if kappa <= 0.0:
        raise ValueError("kappa must be positive")
    if slope_norm <= 0.0:
        raise ValueError("slope_norm must be positive")
    fisher_weight = gaussian_logistic_transverse_fisher_weight(slope_norm)
    return float(slope_norm) ** 2 * float(kappa) * fisher_weight


def asymptotic_isotropic_slope_cosine(*, kappa: float, slope_norm: float) -> float:
    """Approximate slope cosine under the locally balanced p=0.5 information limit."""
    eta = boundary_directional_information_coordinate(kappa=kappa, slope_norm=slope_norm)
    return sqrt(eta / (1.0 + eta))


def asymptotic_isotropic_ordering_error(*, kappa: float, slope_norm: float) -> float:
    """Approximate ordering error under the locally balanced p=0.5 information limit."""
    eta = boundary_directional_information_coordinate(kappa=kappa, slope_norm=slope_norm)
    return atan(1.0 / sqrt(eta)) / pi


def asymptotic_gaussian_logistic_ordering_error(*, kappa: float, slope_norm: float) -> float:
    """Approximate ordering error using the Gaussian-logistic transverse Fisher weight.

    In the large-d controlled-geometry approximation, total transverse slope-error
    energy approaches ``1 / (kappa * a(B))``. Combining that with the exact
    Gaussian-population angle/order identity gives ``atan(eta_F^-1/2) / pi``.
    This remains a synthetic asymptotic benchmark, not a production stopping rule.
    """
    eta = gaussian_logistic_directional_information_coordinate(
        kappa=kappa,
        slope_norm=slope_norm,
    )
    return atan(1.0 / sqrt(eta)) / pi


def asymptotic_kappa_for_ordering_error(*, target_error: float, slope_norm: float) -> float:
    """Invert the p=0.5 boundary-limit ordering law for a target below random ordering."""
    if target_error <= 0.0 or target_error >= 0.5:
        raise ValueError("target_error must lie strictly between 0 and 0.5")
    if slope_norm <= 0.0:
        raise ValueError("slope_norm must be positive")
    tangent = tan(pi * float(target_error))
    return 4.0 / (float(slope_norm) ** 2 * tangent * tangent)


def normalize_effective_slope(
    alpha: Sequence[float],
    *,
    target_norm: float,
) -> Vector:
    """Normalize an effective linear-logistic slope while preserving the intercept.

    The resulting norm is meaningful only relative to the fixed standardized
    feature basis used by the experiment. It is not a separately identified
    psychological preference-strength parameter.
    """
    if len(alpha) < 2:
        raise ValueError("alpha must contain an intercept and at least one slope coefficient")
    if target_norm <= 0.0:
        raise ValueError("target_norm must be positive")

    intercept = float(alpha[0])
    slope = tuple(float(value) for value in alpha[1:])
    norm = sqrt(sum(value * value for value in slope))
    if norm <= 0.0:
        raise ValueError("cannot normalize a zero slope")
    scale = float(target_norm) / norm
    return (intercept, *(value * scale for value in slope))
