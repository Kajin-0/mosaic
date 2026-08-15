from __future__ import annotations

from collections import Counter

import pytest

from mosaic_engine.science_s1_passive_design import balanced_round_robin_pair_schedule


def test_balanced_round_robin_schedule_factorizes_complete_even_graph() -> None:
    candidate_count = 18
    schedule = balanced_round_robin_pair_schedule(candidate_count, seed=20260815)

    assert len(schedule) == candidate_count * (candidate_count - 1) // 2
    assert len(set(schedule)) == len(schedule)

    pairs_per_round = candidate_count // 2
    for start in range(0, len(schedule), pairs_per_round):
        round_pairs = schedule[start : start + pairs_per_round]
        endpoints = [candidate for pair in round_pairs for candidate in pair]
        assert sorted(endpoints) == list(range(candidate_count))

    endpoint_counts = Counter(candidate for pair in schedule for candidate in pair)
    assert set(endpoint_counts.values()) == {candidate_count - 1}


def test_balanced_round_robin_schedule_is_seeded_but_preserves_invariants() -> None:
    first = balanced_round_robin_pair_schedule(6, seed=1)
    second = balanced_round_robin_pair_schedule(6, seed=2)
    assert first != second
    assert set(first) == set(second)


def test_balanced_round_robin_schedule_rejects_odd_candidate_count() -> None:
    with pytest.raises(ValueError):
        balanced_round_robin_pair_schedule(5, seed=0)
