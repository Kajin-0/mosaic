from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import cos, pi, sqrt

Vector = tuple[float, ...]


@dataclass(frozen=True)
class ControlledDesignDiagnostics:
    candidate_count: int
    feature_dimension: int
    maximum_absolute_feature_mean: float
    maximum_absolute_gram_error: float
    minimum_row_norm: float
    maximum_row_norm: float


def centered_dct_candidate_bank(
    *,
    candidate_count: int,
    feature_dimension: int,
) -> tuple[Vector, ...]:
    """Construct a deterministic centered orthogonal synthetic query bank.

    Columns are the first ``feature_dimension`` nonconstant DCT-II basis vectors,
    scaled so that X.T X / n = I.  The omitted constant basis vector is exactly
    the intercept direction, so 1.T X = 0 and the augmented design satisfies
    Z.T Z / n = I in exact arithmetic.
    """
    if candidate_count < 2:
        raise ValueError("candidate_count must be at least two")
    if feature_dimension <= 0:
        raise ValueError("feature_dimension must be positive")
    if feature_dimension >= candidate_count:
        raise ValueError("feature_dimension must be smaller than candidate_count")

    scale = sqrt(2.0)
    return tuple(
        tuple(
            scale * cos(pi * (row_index + 0.5) * (feature_index + 1) / candidate_count)
            for feature_index in range(feature_dimension)
        )
        for row_index in range(candidate_count)
    )


def centered_orthogonalized_candidate_bank(
    candidates: Sequence[Sequence[float]],
) -> tuple[Vector, ...]:
    """Center and orthogonalize a full-rank stochastic candidate bank.

    Modified Gram-Schmidt is applied to the centered feature columns, with a
    second re-orthogonalization pass for numerical stability.  Each resulting
    column is rescaled to norm sqrt(n), so X.T X / n = I while the columns
    remain orthogonal to the intercept direction.
    """
    if not candidates:
        raise ValueError("candidates must not be empty")
    feature_dimension = len(candidates[0])
    candidate_count = len(candidates)
    if feature_dimension <= 0 or any(len(row) != feature_dimension for row in candidates):
        raise ValueError("candidate rows must have one common positive dimension")
    if feature_dimension >= candidate_count:
        raise ValueError("feature_dimension must be smaller than candidate_count")

    means = tuple(
        sum(float(row[column]) for row in candidates) / candidate_count
        for column in range(feature_dimension)
    )
    centered_columns = [
        [float(row[column]) - means[column] for row in candidates]
        for column in range(feature_dimension)
    ]

    orthonormal_columns: list[list[float]] = []
    tolerance = 1e-12 * sqrt(candidate_count)
    for centered_column in centered_columns:
        vector = list(centered_column)
        for _ in range(2):
            for basis in orthonormal_columns:
                projection = sum(
                    value * basis_value for value, basis_value in zip(vector, basis, strict=True)
                )
                vector = [
                    value - projection * basis_value
                    for value, basis_value in zip(vector, basis, strict=True)
                ]
        norm = sqrt(sum(value * value for value in vector))
        if norm <= tolerance:
            raise ValueError("candidate feature columns are not full rank after centering")
        orthonormal_columns.append([value / norm for value in vector])

    scale = sqrt(candidate_count)
    return tuple(
        tuple(scale * orthonormal_columns[column][row] for column in range(feature_dimension))
        for row in range(candidate_count)
    )


def controlled_design_diagnostics(
    candidates: Sequence[Sequence[float]],
) -> ControlledDesignDiagnostics:
    if not candidates:
        raise ValueError("candidates must not be empty")
    feature_dimension = len(candidates[0])
    if feature_dimension <= 0 or any(len(row) != feature_dimension for row in candidates):
        raise ValueError("candidate rows must have one common positive dimension")

    candidate_count = len(candidates)
    feature_means = tuple(
        sum(float(row[column]) for row in candidates) / candidate_count
        for column in range(feature_dimension)
    )
    maximum_absolute_gram_error = 0.0
    for row_index in range(feature_dimension):
        for column_index in range(feature_dimension):
            empirical = (
                sum(float(row[row_index]) * float(row[column_index]) for row in candidates)
                / candidate_count
            )
            target = 1.0 if row_index == column_index else 0.0
            maximum_absolute_gram_error = max(
                maximum_absolute_gram_error,
                abs(empirical - target),
            )

    row_norms = tuple(sqrt(sum(float(value) * float(value) for value in row)) for row in candidates)
    return ControlledDesignDiagnostics(
        candidate_count=candidate_count,
        feature_dimension=feature_dimension,
        maximum_absolute_feature_mean=max(abs(value) for value in feature_means),
        maximum_absolute_gram_error=maximum_absolute_gram_error,
        minimum_row_norm=min(row_norms),
        maximum_row_norm=max(row_norms),
    )
