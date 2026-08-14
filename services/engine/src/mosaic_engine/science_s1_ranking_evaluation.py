from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

from .science_s1 import acceptance_probability


@dataclass(frozen=True)
class PairwiseRankingMetrics:
    pair_count: int
    ordering_error_rate: float
    probability_regret: float


def _score(alpha: Sequence[float], features: Sequence[float]) -> float:
    if len(alpha) != len(features) + 1:
        raise ValueError("alpha must contain an intercept plus one coefficient per feature")
    return float(alpha[0]) + sum(
        float(coefficient) * float(value)
        for coefficient, value in zip(alpha[1:], features, strict=True)
    )


def evaluate_pairwise_ranking(
    true_alpha: Sequence[float],
    inferred_alpha: Sequence[float],
    heldout_features: Sequence[Sequence[float]],
) -> PairwiseRankingMetrics:
    """Evaluate inferred ordering against the true synthetic preference state.

    Probability regret is the true acceptance-probability gap paid only when
    the inferred mean-score ordering is wrong.  An exact inferred tie receives
    half error / half regret unless the true pair is also tied.
    """
    if len(heldout_features) < 2:
        raise ValueError("at least two held-out candidates are required")
    if len(true_alpha) != len(inferred_alpha):
        raise ValueError("true and inferred alpha dimensions must agree")

    true_scores = tuple(_score(true_alpha, features) for features in heldout_features)
    inferred_scores = tuple(_score(inferred_alpha, features) for features in heldout_features)
    true_probabilities = tuple(
        acceptance_probability(true_alpha, features) for features in heldout_features
    )

    error_mass = 0.0
    regret_mass = 0.0
    pair_count = 0
    for first, second in combinations(range(len(heldout_features)), 2):
        pair_count += 1
        true_difference = true_scores[first] - true_scores[second]
        inferred_difference = inferred_scores[first] - inferred_scores[second]
        probability_gap = abs(true_probabilities[first] - true_probabilities[second])

        if true_difference == 0.0:
            continue
        if inferred_difference == 0.0:
            error_mass += 0.5
            regret_mass += 0.5 * probability_gap
        elif true_difference * inferred_difference < 0.0:
            error_mass += 1.0
            regret_mass += probability_gap

    return PairwiseRankingMetrics(
        pair_count=pair_count,
        ordering_error_rate=error_mass / pair_count,
        probability_regret=regret_mass / pair_count,
    )
