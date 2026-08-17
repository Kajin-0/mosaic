from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from random import Random

from .science_s1 import acceptance_probability
from .science_s1_bayesian_acquisition import choose_uncertainty_aware_pair
from .science_s1_decision_acquisition_fast import choose_expected_top_k_value_pair_approximation
from .science_s1_simulation import (
    BinaryObservation,
    CandidatePair,
    LaplacePosterior,
    SimulationMetrics,
    choose_pair,
    evaluate_ground_truth,
    fit_logistic_laplace,
)

_POLICIES = {
    "random",
    "posterior_fisher_d_optimal",
    "mutual_information_d_optimal",
    "expected_top_k_evsi",
}


@dataclass(frozen=True)
class V4SimulationResult:
    policy: str
    query_count: int
    selected_pairs: tuple[CandidatePair, ...]
    selected_decision_scores: tuple[float, ...]
    posterior: LaplacePosterior
    metrics: SimulationMetrics


def run_ground_truth_simulation_v4(
    *,
    policy: str,
    true_alpha: Sequence[float],
    candidates: Sequence[Sequence[float]],
    decision_features: Sequence[Sequence[float]],
    heldout_features: Sequence[Sequence[float]],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
    query_count: int,
    top_k: int,
    seed: int,
) -> V4SimulationResult:
    """Run an S1 v4 acquisition policy on the unchanged synthetic ground truth."""
    if policy not in _POLICIES:
        raise ValueError(
            "policy must be random, posterior_fisher_d_optimal, "
            "mutual_information_d_optimal, or expected_top_k_evsi"
        )
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")
    if not decision_features:
        raise ValueError("decision_features must not be empty")
    if top_k <= 0 or top_k > len(decision_features) or top_k > len(heldout_features):
        raise ValueError("top_k must be within both decision and held-out banks")

    remaining: list[CandidatePair] = list(combinations(range(len(candidates)), 2))
    if query_count > len(remaining):
        raise ValueError("query_count exceeds number of unique candidate pairs")

    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    selected_pairs: list[CandidatePair] = []
    selected_decision_scores: list[float] = []
    selection_random = Random(seed ^ 0x5DEECE66D)
    response_random = Random(seed ^ 0xC0FFEE)

    for _ in range(query_count):
        if policy == "random":
            pair = choose_pair(
                policy,
                remaining,
                candidates,
                posterior,
                random=selection_random,
            )
        elif policy == "expected_top_k_evsi":
            pair, score = choose_expected_top_k_value_pair_approximation(
                remaining,
                candidates,
                posterior,
                decision_features,
                top_k=top_k,
            )
            selected_decision_scores.append(score)
        else:
            pair = choose_uncertainty_aware_pair(
                policy,
                remaining,
                candidates,
                posterior,
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

    return V4SimulationResult(
        policy=policy,
        query_count=query_count,
        selected_pairs=tuple(selected_pairs),
        selected_decision_scores=tuple(selected_decision_scores),
        posterior=posterior,
        metrics=evaluate_ground_truth(
            true_alpha,
            posterior,
            heldout_features,
            top_k=top_k,
        ),
    )
