from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations
from random import Random

from .science_s1 import acceptance_probability
from .science_s1_bayesian_acquisition import choose_uncertainty_aware_pair
from .science_s1_simulation import (
    BinaryObservation,
    CandidatePair,
    SimulationResult,
    evaluate_ground_truth,
    fit_logistic_laplace,
    choose_pair,
)

_BASE_POLICIES = {"random", "d_optimal"}
_UNCERTAINTY_AWARE_POLICIES = {
    "posterior_fisher_d_optimal",
    "mutual_information_d_optimal",
}


def run_ground_truth_simulation_v3(
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
    """Run an S1 v3 policy on the unchanged linear-logistic synthetic ground truth."""
    if policy not in _BASE_POLICIES | _UNCERTAINTY_AWARE_POLICIES:
        raise ValueError(
            "policy must be random, d_optimal, posterior_fisher_d_optimal, "
            "or mutual_information_d_optimal"
        )
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")

    remaining: list[CandidatePair] = list(combinations(range(len(candidates)), 2))
    if query_count > len(remaining):
        raise ValueError("query_count exceeds number of unique candidate pairs")

    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    selected_pairs: list[CandidatePair] = []
    selection_random = Random(seed ^ 0x5DEECE66D)
    response_random = Random(seed ^ 0xC0FFEE)

    for _ in range(query_count):
        if policy in _BASE_POLICIES:
            pair = choose_pair(
                policy,
                remaining,
                candidates,
                posterior,
                random=selection_random,
            )
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
