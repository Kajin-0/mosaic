from __future__ import annotations

from collections.abc import Sequence
from random import Random

from .science_s1 import acceptance_probability
from .science_s1_ranking_evaluation import evaluate_pairwise_ranking
from .science_s1_simulation import (
    BinaryObservation,
    CandidatePair,
    evaluate_ground_truth,
    fit_logistic_laplace,
)
from .science_s1_v6_simulation import V6SimulationResult


def balanced_round_robin_pair_schedule(
    candidate_count: int,
    *,
    seed: int,
) -> tuple[CandidatePair, ...]:
    """Return a randomized 1-factorization schedule for an even candidate bank.

    Every block of ``candidate_count / 2`` pairs is a perfect matching: every
    candidate appears exactly once. Across ``candidate_count - 1`` rounds every
    unordered candidate pair appears exactly once. Randomization only relabels
    candidates and orders rounds/pairs; it never depends on experimental responses.
    """
    if candidate_count < 2 or candidate_count % 2 != 0:
        raise ValueError("candidate_count must be an even integer of at least two")

    random = Random(seed)
    labels = list(range(candidate_count))
    random.shuffle(labels)
    fixed = labels[-1]
    rotating = labels[:-1]
    rounds: list[list[CandidatePair]] = []

    for _ in range(candidate_count - 1):
        round_pairs: list[CandidatePair] = [tuple(sorted((fixed, rotating[-1])))]
        for index in range((candidate_count - 2) // 2):
            round_pairs.append(tuple(sorted((rotating[index], rotating[-2 - index]))))
        random.shuffle(round_pairs)
        rounds.append(round_pairs)
        rotating = [rotating[-1], *rotating[:-1]]

    random.shuffle(rounds)
    return tuple(pair for round_pairs in rounds for pair in round_pairs)


def run_scheduled_ground_truth_simulation(
    *,
    true_alpha: Sequence[float],
    candidates: Sequence[Sequence[float]],
    heldout_features: Sequence[Sequence[float]],
    prior_mean: Sequence[float],
    prior_variances: Sequence[float],
    pair_schedule: Sequence[CandidatePair],
    query_count: int,
    top_k: int,
    response_seed: int,
    policy_name: str = "balanced_round_robin_passive",
) -> V6SimulationResult:
    """Run the S1 synthetic likelihood on a response-independent pair schedule."""
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")
    if query_count > len(pair_schedule):
        raise ValueError("query_count exceeds pair schedule length")
    if top_k <= 0 or top_k > len(heldout_features):
        raise ValueError("top_k must be within the held-out bank")

    selected_pairs = tuple(pair_schedule[:query_count])
    if len(set(selected_pairs)) != len(selected_pairs):
        raise ValueError("selected pair schedule must not repeat candidate pairs")
    for first, second in selected_pairs:
        if first == second or first < 0 or second < 0:
            raise ValueError("candidate pair indices must be distinct and nonnegative")
        if first >= len(candidates) or second >= len(candidates):
            raise ValueError("candidate pair index is out of range")

    posterior = fit_logistic_laplace((), prior_mean, prior_variances)
    observations: list[BinaryObservation] = []
    response_random = Random(response_seed ^ 0xC0FFEE)

    for first, second in selected_pairs:
        for candidate_index in (first, second):
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
        policy=policy_name,
        query_count=query_count,
        selected_pairs=selected_pairs,
        selected_acquisition_scores=(),
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
