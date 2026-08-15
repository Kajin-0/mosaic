from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import exp, log, log1p


@dataclass(frozen=True)
class PrequentialBinaryObservation:
    features: tuple[float, ...]
    accepted: bool
    predictive_probability: float


def _linear_score(alpha: Sequence[float], features: Sequence[float]) -> float:
    if len(alpha) != len(features) + 1:
        raise ValueError("alpha must contain one intercept plus one coefficient per feature")
    return float(alpha[0]) + sum(
        float(coefficient) * float(feature)
        for coefficient, feature in zip(alpha[1:], features, strict=True)
    )


def _log_sigmoid(score: float) -> float:
    if score >= 0.0:
        return -log1p(exp(-score))
    return score - log1p(exp(score))


def _log_one_minus_sigmoid(score: float) -> float:
    if score >= 0.0:
        return -score - log1p(exp(-score))
    return -log1p(exp(score))


def binary_log_probability(
    alpha: Sequence[float],
    features: Sequence[float],
    accepted: bool,
) -> float:
    """Stable Bernoulli-logistic log probability for one S1 binary observation."""
    score = _linear_score(alpha, features)
    return _log_sigmoid(score) if accepted else _log_one_minus_sigmoid(score)


def _validate_predictive_probability(probability: float) -> float:
    value = float(probability)
    if value <= 0.0 or value >= 1.0:
        raise ValueError("predictive_probability must lie strictly between zero and one")
    return value


def prequential_log_e_increment(
    alpha: Sequence[float],
    features: Sequence[float],
    accepted: bool,
    *,
    predictive_probability: float,
) -> float:
    """Return log q_t(Y_t) - log p_alpha(Y_t | x_t).

    ``predictive_probability`` must be chosen using only information available before
    the current outcome is observed. Under a correctly specified fixed ``alpha`` and
    predictable design, exponentiating this increment gives a one-step likelihood
    ratio with conditional expectation one.
    """
    prediction = _validate_predictive_probability(predictive_probability)
    log_predictive = log(prediction if accepted else 1.0 - prediction)
    return log_predictive - binary_log_probability(alpha, features, accepted)


def prequential_log_e_value(
    alpha: Sequence[float],
    observations: Sequence[PrequentialBinaryObservation],
) -> float:
    """Return the cumulative log e-process against one fixed candidate parameter."""
    return sum(
        prequential_log_e_increment(
            alpha,
            observation.features,
            observation.accepted,
            predictive_probability=observation.predictive_probability,
        )
        for observation in observations
    )


def one_step_e_expectation(
    alpha: Sequence[float],
    features: Sequence[float],
    *,
    predictive_probability: float,
) -> float:
    """Evaluate the exact two-outcome conditional normalization identity numerically."""
    prediction = _validate_predictive_probability(predictive_probability)
    log_true_accept = binary_log_probability(alpha, features, True)
    log_true_reject = binary_log_probability(alpha, features, False)
    accept_term = exp(log_true_accept) * exp(log(prediction) - log_true_accept)
    reject_term = exp(log_true_reject) * exp(log(1.0 - prediction) - log_true_reject)
    return accept_term + reject_term


def anytime_log_threshold(alpha_level: float) -> float:
    """Return log(1 / alpha) for an e-process rejection threshold."""
    level = float(alpha_level)
    if level <= 0.0 or level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")
    return -log(level)


def reject_fixed_parameter(log_e_value: float, *, alpha_level: float = 0.05) -> bool:
    """Return whether a fixed parameter is rejected by the anytime-valid e-process."""
    return float(log_e_value) >= anytime_log_threshold(alpha_level)


def confidence_log_likelihood_threshold(
    log_predictive_joint: float,
    *,
    alpha_level: float = 0.05,
) -> float:
    """Return the equivalent log-likelihood cutoff for the e-process confidence set.

    A parameter remains in the confidence sequence when

        log L_t(alpha) > log Q_t + log(alpha_level),

    with the boundary convention left to the caller.
    """
    level = float(alpha_level)
    if level <= 0.0 or level >= 1.0:
        raise ValueError("alpha_level must lie strictly between zero and one")
    return float(log_predictive_joint) + log(level)


def composite_null_log_e_lower_bound(
    log_predictive_joint: float,
    upper_log_likelihood_null: float,
) -> float:
    """Return a conservative log e-value for a composite null.

    If ``upper_log_likelihood_null`` is a genuine upper bound on
    ``sup_{theta in H0} log L_t(theta)``, then

        Q_t / exp(upper_log_likelihood_null)

    is no larger than the fixed-parameter likelihood ratio for every theta in H0.
    Crossing the e-threshold is therefore a safe certificate for rejecting the whole
    null. Numerical angular certification must preserve the upper-bound direction;
    an underestimated null supremum would invalidate the guarantee.
    """
    return float(log_predictive_joint) - float(upper_log_likelihood_null)


def reject_composite_null(
    log_predictive_joint: float,
    upper_log_likelihood_null: float,
    *,
    alpha_level: float = 0.05,
) -> bool:
    """Return whether the conservative composite-null e-value crosses its threshold."""
    return composite_null_log_e_lower_bound(
        log_predictive_joint,
        upper_log_likelihood_null,
    ) >= anytime_log_threshold(alpha_level)
