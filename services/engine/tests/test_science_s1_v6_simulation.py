from __future__ import annotations

import pytest

from mosaic_engine.science_s1_v6_simulation import run_ground_truth_simulation_v6


def _run(policy: str):
    return run_ground_truth_simulation_v6(
        policy=policy,
        true_alpha=(0.1, 0.8, -0.5),
        candidates=(
            (1.2, 0.1),
            (0.2, 1.1),
            (-1.0, 0.3),
            (0.4, -1.2),
            (0.9, 0.8),
        ),
        reference_differences=(
            (1.0, 0.0),
            (0.0, 1.0),
            (0.8, -0.8),
            (-1.2, 0.4),
            (0.5, 1.1),
        ),
        heldout_features=(
            (1.1, 0.1),
            (0.1, 1.2),
            (0.7, 0.8),
            (-0.9, -0.5),
            (0.4, -0.9),
            (-0.5, 1.0),
            (1.3, -0.2),
            (-0.7, 0.6),
        ),
        prior_mean=(0.0, 0.0, 0.0),
        prior_variances=(4.0, 4.0, 4.0),
        query_count=2,
        top_k=2,
        seed=12345,
    )


@pytest.mark.parametrize(
    "policy",
    (
        "random",
        "posterior_fisher_d_optimal",
        "mutual_information_d_optimal",
        "population_score_regret",
        "exact_gaussian_score_regret",
    ),
)
def test_v6_policies_are_reproducible(policy: str) -> None:
    first = _run(policy)
    second = _run(policy)

    assert first.selected_pairs == second.selected_pairs
    assert first.posterior.mean == pytest.approx(second.posterior.mean)
    assert first.metrics.top_k_regret == pytest.approx(second.metrics.top_k_regret)
    assert first.ranking_metrics == second.ranking_metrics


def test_ranking_policies_record_one_score_per_query() -> None:
    for policy in ("population_score_regret", "exact_gaussian_score_regret"):
        result = _run(policy)
        assert len(result.selected_acquisition_scores) == result.query_count
        assert all(score == pytest.approx(score) for score in result.selected_acquisition_scores)


def test_information_and_random_baselines_do_not_emit_acquisition_scores() -> None:
    for policy in ("random", "posterior_fisher_d_optimal", "mutual_information_d_optimal"):
        assert _run(policy).selected_acquisition_scores == ()
