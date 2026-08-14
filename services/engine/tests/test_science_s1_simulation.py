from __future__ import annotations

from random import Random

import pytest

from mosaic_engine.science_s1_simulation import (
    LaplacePosterior,
    boundary_pair_score,
    choose_pair,
    d_optimal_pair_score,
    evaluate_ground_truth,
    fit_logistic_laplace,
    make_gaussian_scenario,
    run_ground_truth_simulation,
)


def test_prior_only_laplace_state_reproduces_diagonal_gaussian_prior() -> None:
    posterior = fit_logistic_laplace((), (0.2, -0.4), (4.0, 0.25))

    assert posterior.converged
    assert posterior.mean == pytest.approx((0.2, -0.4))
    assert posterior.covariance[0] == pytest.approx((4.0, 0.0))
    assert posterior.covariance[1] == pytest.approx((0.0, 0.25))
    assert posterior.precision[0] == pytest.approx((0.25, 0.0))
    assert posterior.precision[1] == pytest.approx((0.0, 4.0))


def test_boundary_score_prefers_candidates_near_current_acceptance_boundary() -> None:
    posterior_mean = (0.0, 1.0)

    near_boundary = boundary_pair_score(posterior_mean, (0.0,), (0.1,))
    far_from_boundary = boundary_pair_score(posterior_mean, (5.0,), (6.0,))

    assert near_boundary > far_from_boundary


def test_d_optimal_score_prefers_probe_along_more_uncertain_direction() -> None:
    posterior = fit_logistic_laplace(
        (),
        (0.0, 0.0, 0.0),
        (1.0, 100.0, 0.01),
    )

    uncertain_direction = d_optimal_pair_score(posterior, (1.0, 0.0), (-1.0, 0.0))
    known_direction = d_optimal_pair_score(posterior, (0.0, 1.0), (0.0, -1.0))

    assert uncertain_direction > known_direction


def test_boundary_policy_uses_pair_score_not_candidate_order() -> None:
    posterior = fit_logistic_laplace((), (0.0, 1.0), (1.0, 1.0))
    candidates = ((5.0,), (0.0,), (6.0,), (0.1,))
    remaining = ((0, 2), (1, 3))

    selected = choose_pair(
        "boundary",
        remaining,
        candidates,
        posterior,
        random=Random(1),
    )

    assert selected == (1, 3)


def test_ground_truth_metrics_are_exact_when_posterior_mean_equals_truth() -> None:
    posterior = LaplacePosterior(
        mean=(0.2, 0.7),
        covariance=((1.0, 0.0), (0.0, 1.0)),
        precision=((1.0, 0.0), (0.0, 1.0)),
        converged=True,
        iterations=1,
    )
    heldout = ((-2.0,), (-1.0,), (0.0,), (1.0,), (2.0,))

    metrics = evaluate_ground_truth((0.2, 0.7), posterior, heldout, top_k=2)

    assert metrics.coefficient_rmse == pytest.approx(0.0)
    assert metrics.probability_mse == pytest.approx(0.0)
    assert metrics.top_k_regret == pytest.approx(0.0)
    assert metrics.top_k_overlap == pytest.approx(1.0)
    assert metrics.interval_coverage == pytest.approx(1.0)
    assert metrics.oracle_log_loss > 0.0
    assert metrics.expected_log_loss == pytest.approx(metrics.oracle_log_loss)
    assert metrics.excess_log_loss == pytest.approx(0.0)


def test_ground_truth_simulation_is_reproducible_and_keeps_pairs_unique() -> None:
    true_alpha, candidates, heldout = make_gaussian_scenario(
        feature_dimension=3,
        candidate_count=12,
        heldout_count=40,
        seed=11,
    )
    arguments = {
        "policy": "d_optimal",
        "true_alpha": true_alpha,
        "candidates": candidates,
        "heldout_features": heldout,
        "prior_mean": (0.0, 0.0, 0.0, 0.0),
        "prior_variances": (4.0, 4.0, 4.0, 4.0),
        "query_count": 6,
        "top_k": 5,
        "seed": 23,
    }

    first = run_ground_truth_simulation(**arguments)
    second = run_ground_truth_simulation(**arguments)

    assert first == second
    assert first.posterior.converged
    assert len(first.selected_pairs) == 6
    assert len(set(first.selected_pairs)) == 6
    assert first.metrics.excess_log_loss >= -1e-12
    assert first.metrics.top_k_regret >= 0.0
    assert 0.0 <= first.metrics.top_k_overlap <= 1.0
    assert 0.0 <= first.metrics.interval_coverage <= 1.0
