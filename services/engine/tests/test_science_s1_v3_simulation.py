from __future__ import annotations

from mosaic_engine.science_s1_simulation import make_gaussian_scenario
from mosaic_engine.science_s1_v3_simulation import run_ground_truth_simulation_v3


def test_uncertainty_aware_v3_policies_are_reproducible_and_converge() -> None:
    true_alpha, candidates, heldout = make_gaussian_scenario(
        feature_dimension=3,
        candidate_count=10,
        heldout_count=32,
        seed=101,
    )
    common = {
        "true_alpha": true_alpha,
        "candidates": candidates,
        "heldout_features": heldout,
        "prior_mean": (0.0, 0.0, 0.0, 0.0),
        "prior_variances": (4.0, 4.0, 4.0, 4.0),
        "query_count": 5,
        "top_k": 4,
        "seed": 202,
    }

    for policy in (
        "posterior_fisher_d_optimal",
        "mutual_information_d_optimal",
    ):
        first = run_ground_truth_simulation_v3(policy=policy, **common)
        second = run_ground_truth_simulation_v3(policy=policy, **common)

        assert first == second
        assert first.posterior.converged
        assert len(first.selected_pairs) == 5
        assert len(set(first.selected_pairs)) == 5
        assert first.metrics.excess_log_loss >= -1e-12
        assert first.metrics.top_k_regret >= 0.0


def test_v3_reuses_original_random_and_plugin_d_optimal_semantics() -> None:
    true_alpha, candidates, heldout = make_gaussian_scenario(
        feature_dimension=2,
        candidate_count=8,
        heldout_count=24,
        seed=303,
    )
    common = {
        "true_alpha": true_alpha,
        "candidates": candidates,
        "heldout_features": heldout,
        "prior_mean": (0.0, 0.0, 0.0),
        "prior_variances": (4.0, 4.0, 4.0),
        "query_count": 4,
        "top_k": 4,
        "seed": 404,
    }

    random_result = run_ground_truth_simulation_v3(policy="random", **common)
    d_optimal_result = run_ground_truth_simulation_v3(policy="d_optimal", **common)

    assert random_result.posterior.converged
    assert d_optimal_result.posterior.converged
    assert random_result.policy == "random"
    assert d_optimal_result.policy == "d_optimal"
