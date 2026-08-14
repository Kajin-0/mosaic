from __future__ import annotations

import pytest

from mosaic_engine.science_s1_ranking_evaluation import evaluate_pairwise_ranking


def test_perfect_inferred_order_has_zero_pairwise_regret() -> None:
    features = ((-1.0,), (0.0,), (1.0,), (2.0,))

    metrics = evaluate_pairwise_ranking((0.0, 1.0), (4.0, 0.3), features)

    assert metrics.pair_count == 6
    assert metrics.ordering_error_rate == 0.0
    assert metrics.probability_regret == 0.0


def test_reversed_order_misorders_every_nontied_pair() -> None:
    features = ((-1.0,), (0.0,), (1.0,))

    metrics = evaluate_pairwise_ranking((0.0, 1.0), (0.0, -1.0), features)

    assert metrics.pair_count == 3
    assert metrics.ordering_error_rate == 1.0
    assert metrics.probability_regret > 0.0


def test_exact_inferred_tie_receives_half_error_mass() -> None:
    features = ((-1.0,), (1.0,))

    metrics = evaluate_pairwise_ranking((0.0, 1.0), (0.0, 0.0), features)

    assert metrics.pair_count == 1
    assert metrics.ordering_error_rate == pytest.approx(0.5)
    assert 0.0 < metrics.probability_regret < 0.5


def test_probability_regret_is_bounded_by_one() -> None:
    features = ((-10.0,), (10.0,), (5.0,), (-5.0,))

    metrics = evaluate_pairwise_ranking((0.0, 2.0), (0.0, -1.0), features)

    assert 0.0 <= metrics.probability_regret <= 1.0
