from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from math import cos, pi, sin
from random import Random
from typing import cast

from .science_s1 import acceptance_probability
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    CONE_ALPHA,
    CONE_OFFSETS_DEGREES,
    ParameterBox,
    _cone_halfspaces,
    _cone_log_e_lower_bound,
    _fraction,
    certify_continuous_cone_current,
    likelihood_bounds,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-continuous-bound-validation-v14a"
METHOD_VERSION = "continuous-split-alpha-interval-bnb-v1"
VALIDATION_SEED = 14_001
REFERENCE_PRECISION = 120
DEFAULT_BOX_COUNT = 8
DEFAULT_GRID_SIZE = 3
DEFAULT_CERTIFICATE_MAX_NODES = 250
ROTATIONS_DEGREES = (0.0, 30.0, -60.0, 120.0)


def _decimal_fraction(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        return Decimal(value.numerator) / Decimal(value.denominator)


def _reference_log_probability(score: Decimal, *, accepted: bool) -> Decimal:
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        one = Decimal(1)
        if accepted:
            return -(one + (-score).exp()).ln()
        return -(one + score.exp()).ln()


def _rotated_design(
    features: Sequence[float],
    *,
    rotation_degrees: float,
) -> tuple[float, float]:
    x_value = float(features[0])
    y_value = float(features[1])
    if rotation_degrees == 0.0:
        return x_value, y_value
    angle = rotation_degrees * pi / 180.0
    cosine = cos(angle)
    sine = sin(angle)
    return (
        cosine * x_value + sine * y_value,
        -sine * x_value + cosine * y_value,
    )


def _reference_log_likelihood(
    theta: Sequence[Fraction],
    observations: Sequence[PrequentialBinaryObservation],
    *,
    rotation_degrees: float = 0.0,
) -> Decimal:
    if len(theta) != 3:
        raise ValueError("theta must contain intercept plus two slopes")
    theta_decimal = tuple(_decimal_fraction(value) for value in theta)
    terms: list[Decimal] = []
    for observation in observations:
        x_value, y_value = _rotated_design(
            observation.features,
            rotation_degrees=rotation_degrees,
        )
        with localcontext() as context:
            context.prec = REFERENCE_PRECISION
            score = theta_decimal[0]
            score += theta_decimal[1] * Decimal.from_float(x_value)
            score += theta_decimal[2] * Decimal.from_float(y_value)
        terms.append(_reference_log_probability(score, accepted=observation.accepted))
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        return sum(terms, Decimal(0))


def _reference_cone_log_e(
    theta: Sequence[Fraction],
    observations: Sequence[PrequentialBinaryObservation],
) -> Decimal:
    null_log_likelihood = _reference_log_likelihood(theta, observations)
    alternatives = [
        _reference_log_likelihood(
            theta,
            observations,
            rotation_degrees=float(offset),
        )
        for offset in CONE_OFFSETS_DEGREES
    ]
    maximum = max(alternatives)
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        total = sum(((value - maximum).exp() for value in alternatives), Decimal(0))
        log_mixture = maximum + total.ln() - Decimal(len(alternatives)).ln()
        return log_mixture - null_log_likelihood


def _unit_candidate_bank(count: int = 12) -> tuple[tuple[float, float], ...]:
    return tuple(
        (
            cos(2.0 * pi * index / count),
            sin(2.0 * pi * index / count),
        )
        for index in range(count)
    )


def _synthetic_observations(
    *,
    alpha: Sequence[float],
    repeats: int,
    seed: int,
) -> tuple[PrequentialBinaryObservation, ...]:
    random = Random(seed)
    observations: list[PrequentialBinaryObservation] = []
    candidates = _unit_candidate_bank()
    for _ in range(repeats):
        for features in candidates:
            probability = acceptance_probability(alpha, features)
            observations.append(
                PrequentialBinaryObservation(
                    features=features,
                    accepted=random.random() < probability,
                    predictive_probability=0.5,
                )
            )
    return tuple(observations)


def _random_boxes(*, count: int, seed: int) -> tuple[ParameterBox, ...]:
    random = Random(seed)
    boxes: list[ParameterBox] = []
    for _ in range(count):
        centers = (
            random.uniform(-1.5, 1.5),
            random.uniform(-2.0, 2.0),
            random.uniform(-2.0, 2.0),
        )
        widths = (
            random.uniform(0.02, 1.0),
            random.uniform(0.02, 1.2),
            random.uniform(0.02, 1.2),
        )
        intervals = tuple(
            (
                _fraction(center - width / 2.0),
                _fraction(center + width / 2.0),
            )
            for center, width in zip(centers, widths, strict=True)
        )
        boxes.append(ParameterBox(intervals))
    return tuple(boxes)


def _grid_values(
    interval: tuple[Fraction, Fraction],
    *,
    count: int,
) -> tuple[Fraction, ...]:
    if count < 2:
        raise ValueError("grid count must be at least two")
    lower, upper = interval
    return tuple(lower + (upper - lower) * Fraction(index, count - 1) for index in range(count))


def _box_grid(box: ParameterBox, *, grid_size: int) -> Iterable[tuple[Fraction, ...]]:
    axes = tuple(_grid_values(interval, count=grid_size) for interval in box.intervals)
    return product(*axes)


def _common_exact_cutoff(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    alpha_level: Fraction = COMMON_ALPHA,
) -> Decimal:
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        log_joint = sum(
            Decimal.from_float(
                observation.predictive_probability
                if observation.accepted
                else 1.0 - observation.predictive_probability
            ).ln()
            for observation in observations
        )
        return log_joint + _decimal_fraction(alpha_level).ln()


def _cone_exact_threshold(*, alpha_level: Fraction = CONE_ALPHA) -> Decimal:
    with localcontext() as context:
        context.prec = REFERENCE_PRECISION
        return (Decimal(1) / _decimal_fraction(alpha_level)).ln()


def _halfspace_value(
    theta: Sequence[Fraction],
    coefficients: Sequence[Fraction],
) -> Fraction:
    return coefficients[0] * theta[1] + coefficients[1] * theta[2]


def _validate_box_bounds(
    boxes: Sequence[ParameterBox],
    observations: Sequence[PrequentialBinaryObservation],
    *,
    grid_size: int,
) -> dict[str, object]:
    likelihood_violations = 0
    cone_lower_violations = 0
    point_evaluations = 0
    minimum_cone_slack: Decimal | None = None

    for box in boxes:
        likelihood_enclosures = {
            rotation: likelihood_bounds(
                box,
                observations,
                rotation_degrees=rotation,
            )
            for rotation in ROTATIONS_DEGREES
        }
        cone_lower = _cone_log_e_lower_bound(box, observations)
        for theta in _box_grid(box, grid_size=grid_size):
            point_evaluations += 1
            for rotation, enclosure in likelihood_enclosures.items():
                direct = _reference_log_likelihood(
                    theta,
                    observations,
                    rotation_degrees=rotation,
                )
                if not enclosure.lower <= direct <= enclosure.upper:
                    likelihood_violations += 1
            direct_cone = _reference_cone_log_e(theta, observations)
            slack = direct_cone - cone_lower
            if slack < 0:
                cone_lower_violations += 1
            if minimum_cone_slack is None or slack < minimum_cone_slack:
                minimum_cone_slack = slack

    return {
        "boxes": len(boxes),
        "grid_size": grid_size,
        "point_evaluations": point_evaluations,
        "rotations_per_point": len(ROTATIONS_DEGREES),
        "likelihood_enclosure_violations": likelihood_violations,
        "cone_lower_bound_violations": cone_lower_violations,
        "minimum_cone_lower_slack": str(minimum_cone_slack),
    }


def _dense_outside_survivors(
    certificate_box: ParameterBox,
    observations: Sequence[PrequentialBinaryObservation],
    *,
    center_slope: Sequence[float],
    grid_size: int,
) -> int:
    common_cutoff = _common_exact_cutoff(observations)
    cone_threshold = _cone_exact_threshold()
    halfspaces = _cone_halfspaces(center_slope, target_error=0.15)
    survivors = 0

    for theta in _box_grid(certificate_box, grid_size=grid_size):
        outside = any(_halfspace_value(theta, halfspace) < 0 for halfspace in halfspaces)
        if not outside:
            continue
        common_survives = _reference_log_likelihood(theta, observations) > common_cutoff
        cone_survives = _reference_cone_log_e(theta, observations) < cone_threshold
        survivors += int(common_survives and cone_survives)
    return survivors


def _validate_full_certificates(
    *,
    grid_size: int,
    max_nodes: int,
) -> list[dict[str, object]]:
    scenarios = (
        ("aligned_240", (0.15, 1.2, 0.0), 20, 14_101, (1.0, 0.0)),
        ("aligned_480", (0.15, 1.2, 0.0), 40, 14_102, (1.0, 0.0)),
        ("off_axis_240", (0.0, 0.9, 0.75), 20, 14_103, (1.0, 0.0)),
        ("weak_240", (0.0, 0.25, 0.0), 20, 14_104, (1.0, 0.0)),
    )
    results: list[dict[str, object]] = []

    for name, alpha, repeats, seed, center in scenarios:
        observations = _synthetic_observations(alpha=alpha, repeats=repeats, seed=seed)
        certificate = certify_continuous_cone_current(
            observations,
            center,
            max_nodes=max_nodes,
            min_width=0.05,
        )
        dense_outside_survivors = None
        if certificate.initial_box is not None:
            dense_outside_survivors = _dense_outside_survivors(
                certificate.initial_box,
                observations,
                center_slope=center,
                grid_size=grid_size,
            )
        if certificate.certified and dense_outside_survivors:
            raise AssertionError("certificate contradicted by dense outside survivor diagnostic")
        results.append(
            {
                "scenario": name,
                "observation_count": len(observations),
                "certified": certificate.certified,
                "reason": certificate.reason,
                "dense_outside_survivors": dense_outside_survivors,
                "side_certificates": [
                    {
                        "certified": side.certified,
                        "nodes_visited": side.nodes_visited,
                        "unresolved_boxes": side.unresolved_boxes,
                        "reason": side.reason,
                    }
                    for side in certificate.side_certificates
                ],
            }
        )
    return results


def run_benchmark_v14a(
    *,
    box_count: int = DEFAULT_BOX_COUNT,
    grid_size: int = DEFAULT_GRID_SIZE,
    include_full_certificates: bool = True,
    certificate_max_nodes: int = DEFAULT_CERTIFICATE_MAX_NODES,
) -> dict[str, object]:
    if box_count <= 0:
        raise ValueError("box_count must be positive")
    if grid_size < 2:
        raise ValueError("grid_size must be at least two")
    if certificate_max_nodes <= 0:
        raise ValueError("certificate_max_nodes must be positive")

    observations = _synthetic_observations(
        alpha=(0.2, 0.9, -0.35),
        repeats=8,
        seed=VALIDATION_SEED,
    )
    boxes = _random_boxes(count=box_count, seed=VALIDATION_SEED + 1)
    box_validation = _validate_box_bounds(
        boxes,
        observations,
        grid_size=grid_size,
    )
    if cast(int, box_validation["likelihood_enclosure_violations"]) != 0:
        raise AssertionError("likelihood interval enclosure violation")
    if cast(int, box_validation["cone_lower_bound_violations"]) != 0:
        raise AssertionError("cone e-value lower-bound violation")

    full_certificates = (
        _validate_full_certificates(
            grid_size=max(3, grid_size),
            max_nodes=certificate_max_nodes,
        )
        if include_full_certificates
        else []
    )
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Deterministic adversarial method validation of continuous v14 interval likelihood "
            "bounds, cone-cover e-value lower bounds, and branch-and-bound certificate outputs. "
            "This is numerical-method validation, not a sequential operating-characteristic study."
        ),
        "config": {
            "validation_seed": VALIDATION_SEED,
            "reference_precision": REFERENCE_PRECISION,
            "box_count": box_count,
            "grid_size": grid_size,
            "rotations_degrees": ROTATIONS_DEGREES,
            "common_alpha": float(COMMON_ALPHA),
            "cone_alpha": float(CONE_ALPHA),
            "include_full_certificates": include_full_certificates,
            "certificate_max_nodes": certificate_max_nodes,
        },
        "box_validation": box_validation,
        "full_certificate_scenarios": full_certificates,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
