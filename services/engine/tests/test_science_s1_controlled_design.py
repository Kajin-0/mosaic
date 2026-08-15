from __future__ import annotations

import pytest

from mosaic_engine.science_s1_controlled_design import (
    centered_dct_candidate_bank,
    controlled_design_diagnostics,
)


def test_centered_dct_bank_has_identity_empirical_geometry() -> None:
    for feature_dimension in (2, 4, 8, 12):
        candidates = centered_dct_candidate_bank(
            candidate_count=18,
            feature_dimension=feature_dimension,
        )
        diagnostics = controlled_design_diagnostics(candidates)

        assert len(candidates) == 18
        assert all(len(row) == feature_dimension for row in candidates)
        assert diagnostics.maximum_absolute_feature_mean < 1e-12
        assert diagnostics.maximum_absolute_gram_error < 1e-12
        assert diagnostics.minimum_row_norm > 0.0
        assert diagnostics.maximum_row_norm >= diagnostics.minimum_row_norm


def test_centered_dct_bank_rejects_unidentifiable_shape() -> None:
    with pytest.raises(ValueError):
        centered_dct_candidate_bank(candidate_count=1, feature_dimension=1)
    with pytest.raises(ValueError):
        centered_dct_candidate_bank(candidate_count=6, feature_dimension=0)
    with pytest.raises(ValueError):
        centered_dct_candidate_bank(candidate_count=6, feature_dimension=6)


def test_controlled_design_diagnostics_rejects_ragged_rows() -> None:
    with pytest.raises(ValueError):
        controlled_design_diagnostics(())
    with pytest.raises(ValueError):
        controlled_design_diagnostics(((1.0, 2.0), (3.0,)))
