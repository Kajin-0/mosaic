from decimal import Decimal
from fractions import Fraction

from mosaic_engine.science_s1_benchmark_v14e import (
    BoxEvaluation,
    _dimension_score,
    _split_box_dimension,
)
from mosaic_engine.science_s1_continuous_geometry import ParameterBox


def test_split_box_dimension_splits_only_requested_coordinate() -> None:
    box = ParameterBox(
        (
            (Fraction(-2), Fraction(2)),
            (Fraction(-4), Fraction(8)),
            (Fraction(-6), Fraction(10)),
        )
    )

    left, right = _split_box_dimension(box, 1)

    assert left.intervals == (
        (Fraction(-2), Fraction(2)),
        (Fraction(-4), Fraction(2)),
        (Fraction(-6), Fraction(10)),
    )
    assert right.intervals == (
        (Fraction(-2), Fraction(2)),
        (Fraction(2), Fraction(8)),
        (Fraction(-6), Fraction(10)),
    )


def test_dimension_score_prefers_more_immediate_certified_prunes() -> None:
    box = ParameterBox(
        (
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
        )
    )
    pruned = BoxEvaluation("common_prune", Decimal(-1), None, 1.0)
    unresolved_close = BoxEvaluation("unresolved", Decimal("0.2"), Decimal("0.4"), 1.0)
    unresolved_far = BoxEvaluation("unresolved", Decimal("5"), Decimal("8"), 1.0)

    one_prune = ((box, pruned), (box, unresolved_far))
    no_prunes = ((box, unresolved_close), (box, unresolved_close))

    assert _dimension_score(one_prune, dimension=1) < _dimension_score(
        no_prunes,
        dimension=0,
    )


def test_dimension_score_breaks_equal_pruning_by_worst_survival_distance() -> None:
    box = ParameterBox(
        (
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
            (Fraction(-1), Fraction(1)),
        )
    )
    close = BoxEvaluation("unresolved", Decimal("0.2"), Decimal("0.5"), 1.0)
    far = BoxEvaluation("unresolved", Decimal("4"), Decimal("7"), 1.0)

    close_preview = ((box, close), (box, close))
    far_preview = ((box, far), (box, far))

    assert _dimension_score(close_preview, dimension=2) < _dimension_score(
        far_preview,
        dimension=0,
    )
