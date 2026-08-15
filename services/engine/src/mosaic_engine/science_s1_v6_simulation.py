from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from random import Random

from .science_s1 import acceptance_probability
from .science_s1_bayesian_acquisition import choose_uncertainty_aware_pair
from .science_s1_exact_gaussian_ranking import choose_exact_gaussian_ranking_pair
from .science_s1_ranking_acquisition import choose_population_score_regret_pair
from .science_s1_ranking_evaluation import PairwiseRankingMetrics, evaluate_pairwise_ranking
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
    "population_score_regret",
    "exact_gaussian_score_regret",
}


@dataclass(frozen=True)
class V6SimulationResult:
    policy: str
    query_count: int
    selected_pairs: tuple[CandidatePair, ...]
    selected_acquisition_scores: tuple[float, ...]
    posterior: LaplacePosterior
    metrics: SimulationMetrics
    ranking_metrics: PairwiseRankingMetrics


def run_ground_truth_simulation_v6(
    *,
    policy: str,
    true_alpha: Sequence[float],
    candidates: Sequence[Sequence[float]],
    reference_differences: Sequence[Sequence[float]],
    heldout_features: Sequence[Sequence[float]],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
    query_count: int,
    top_k: int,
    seed: int,
) -> V6SimulationResult:
    """Run v6 with Monte-Carlo or exact Gaussian-reference ranking acquisition."""
    if policy not in _POLICIES:
        raise ValueError(
            "policy must be random, posterior_fisher_d_optimal, "
            "mutual_information_d_optimal, population_score_regret, "
            "or exact_gaussian_score_regret"
        )
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")
    if not reference_differences:
        raise ValueError("reference_differences must not be empty")
    if top_k <= 0 or top_k > len(heldout_features):
        raise ValueError("top_k must be within the held-out bank")

    remaining: list[CandidatePair] = list(combinations(range(len(candidates)), 2))
    if query_count > len(remaining):
        raise ValueError("query_count exceeds number of unique candidate pairs")

    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    selected_pairs: list[CandidatePair] = []
    selected_acquisition_scores: list[float] = []
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
        elif policy == "population_score_regret":
            pair, score = choose_population_score_regret_pair(
                remaining,
                candidates,
                posterior,
                reference_differences,
            )
            selected_acquisition_scores.append(score)
        elif policy == "exact_gaussian_score_regret":
            pair, score = choose_exact_gaussian_ranking_pair(
                remaining,
                candidates,
                posterior,
            )
            selected_acquisition_scores.append(score)
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

    return V6SimulationResult(
        policy=policy,
        query_count=query_count,
        selected_pairs=tuple(selected_pairs),
        selected_acquisition_scores=tuple(selected_acquisition_scores),
        posterior=posterior,
        metrics=evaluate_ground_truth(
            true_alpha,
            posterior,
            heldout_features,
            top_k=top_k,
        ),
        ranking_metrics=evaluate_pairwise_ranking(
            true_alpha,
            posterior.mean,
            heldout_features,
        ),
    )
