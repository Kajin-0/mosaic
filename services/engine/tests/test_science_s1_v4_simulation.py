from __future__ import annotations

import pytest

from mosaic_engine.science_s1_v4_simulation import run_ground_truth_simulation_v4


def _run(policy: str):
    return run_ground_truth_simulation_v4(
        policy=policy,
        true_alpha=(0.1, 0.8, -0.5),
        candidates=(
            (1.2, 0.1),
            (0.2, 1.1),
            (-1.0, 0.3),
            (0.4, -1.2),
            (0.9, 0.8),
        ),
        decision_features=(
            (1.0, 0.0),
            (0.0, 1.0),
            (0.8, 0.7),
            (-0.8, -0.4),
            (0.3, -1.0),
            (-0.4, 0.9),
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
        "expected_top_k_evsi",
    ),
)
def test_v4_policies_are_reproducible(policy: str) -> None:
    first = _run(policy)
    second = _run(policy)

    assert first.selected_pairs == second.selected_pairs
    assert first.posterior.mean == pytest.approx(second.posterior.mean)
    assert first.metrics.top_k_regret == pytest.approx(second.metrics.top_k_regret)


def test_decision_policy_records_one_evsi_score_per_query() -> None:
    result = _run("expected_top_k_evsi")

    assert len(result.selected_decision_scores) == result.query_count
    assert all(score == pytest.approx(score) for score in result.selected_decision_scores)


def test_information_and_random_baselines_do_not_emit_decision_scores() -> None:
    for policy in ("random", "posterior_fisher_d_optimal", "mutual_information_d_optimal"):
        assert _run(policy).selected_decision_scores == ()
