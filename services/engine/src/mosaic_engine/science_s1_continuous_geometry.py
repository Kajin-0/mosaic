from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from itertools import combinations
from math import cos, hypot, pi, sin

from .science_s1_eprocess import PrequentialBinaryObservation

DECIMAL_PRECISION = 60
COMMON_ALPHA = Fraction(1, 200)
CONE_ALPHA = Fraction(9, 200)
TOTAL_ALPHA = Fraction(1, 20)
CONE_OFFSETS_DEGREES = (-150, -120, -90, -60, -30, 30, 60, 90, 120, 150, 180)


@dataclass(frozen=True)
class ParameterBox:
    intervals: tuple[tuple[Fraction, Fraction], ...]

    def __post_init__(self) -> None:
        if len(self.intervals) != 3:
            raise ValueError("continuous S1 box must contain intercept plus two slopes")
        if any(lower > upper for lower, upper in self.intervals):
            raise ValueError("box interval lower bound exceeds upper bound")


@dataclass(frozen=True)
class LikelihoodBounds:
    lower: Decimal
    upper: Decimal


@dataclass(frozen=True)
class ConeSideCertificate:
    certified: bool
    nodes_visited: int
    unresolved_boxes: int
    reason: str


@dataclass(frozen=True)
class ContinuousConeCertificate:
    certified: bool
    initial_box: ParameterBox | None
    side_certificates: tuple[ConeSideCertificate, ConeSideCertificate] | tuple[()]
    common_cutoff_lower: Decimal | None
    cone_log_threshold_upper: Decimal
    reason: str


def _fraction(value: float) -> Fraction:
    return Fraction.from_float(float(value))


def _decimal_from_fraction(value: Fraction, *, rounding: str) -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = rounding
        return Decimal(value.numerator) / Decimal(value.denominator)


def _log_fraction_lower(value: Fraction) -> Decimal:
    if value <= 0:
        raise ValueError("logarithm argument must be positive")
    decimal_value = _decimal_from_fraction(value, rounding=ROUND_FLOOR)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        result = decimal_value.ln()
        return context.next_minus(result)


def _log_fraction_upper(value: Fraction) -> Decimal:
    if value <= 0:
        raise ValueError("logarithm argument must be positive")
    decimal_value = _decimal_from_fraction(value, rounding=ROUND_CEILING)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        result = decimal_value.ln()
        return context.next_plus(result)


def _log_sigmoid_decimal(score: Decimal) -> Decimal:
    one = Decimal(1)
    if score >= 0:
        return -(one + (-score).exp()).ln()
    return score - (one + score.exp()).ln()


def _log_one_minus_sigmoid_decimal(score: Decimal) -> Decimal:
    one = Decimal(1)
    if score >= 0:
        return -score - (one + (-score).exp()).ln()
    return -(one + score.exp()).ln()


def _log_probability_bounds(
    score_interval: tuple[Fraction, Fraction],
    *,
    accepted: bool,
) -> LikelihoodBounds:
    lower_score, upper_score = score_interval
    lower_decimal = _decimal_from_fraction(lower_score, rounding=ROUND_FLOOR)
    upper_decimal = _decimal_from_fraction(upper_score, rounding=ROUND_CEILING)

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        if accepted:
            lower_value = context.next_minus(_log_sigmoid_decimal(lower_decimal))
            upper_value = context.next_plus(_log_sigmoid_decimal(upper_decimal))
        else:
            lower_value = context.next_minus(_log_one_minus_sigmoid_decimal(upper_decimal))
            upper_value = context.next_plus(_log_one_minus_sigmoid_decimal(lower_decimal))
    return LikelihoodBounds(lower=lower_value, upper=upper_value)


def _directed_sum(values: Sequence[Decimal], *, rounding: str) -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = rounding
        total = Decimal(0)
        for value in values:
            total += value
        return total


def _design_vector(
    features: Sequence[float],
    *,
    rotation_degrees: float = 0.0,
) -> tuple[Fraction, Fraction, Fraction]:
    if len(features) != 2:
        raise ValueError("continuous v14 certificate currently requires two slope features")
    x_value = float(features[0])
    y_value = float(features[1])
    if rotation_degrees == 0.0:
        rotated_x = x_value
        rotated_y = y_value
    else:
        angle = rotation_degrees * pi / 180.0
        cosine = cos(angle)
        sine = sin(angle)
        # Rotating the candidate slope by +angle is equivalent to rotating the
        # observation feature by -angle before taking the dot product.
        rotated_x = cosine * x_value + sine * y_value
        rotated_y = -sine * x_value + cosine * y_value
    return (Fraction(1), _fraction(rotated_x), _fraction(rotated_y))


def _score_interval(
    box: ParameterBox,
    design: Sequence[Fraction],
) -> tuple[Fraction, Fraction]:
    if len(design) != 3:
        raise ValueError("design vector must contain intercept plus two features")
    lower = Fraction(0)
    upper = Fraction(0)
    for coefficient, (interval_lower, interval_upper) in zip(
        design,
        box.intervals,
        strict=True,
    ):
        if coefficient >= 0:
            lower += coefficient * interval_lower
            upper += coefficient * interval_upper
        else:
            lower += coefficient * interval_upper
            upper += coefficient * interval_lower
    return lower, upper


def likelihood_bounds(
    box: ParameterBox,
    observations: Sequence[PrequentialBinaryObservation],
    *,
    rotation_degrees: float = 0.0,
) -> LikelihoodBounds:
    lower_terms: list[Decimal] = []
    upper_terms: list[Decimal] = []
    for observation in observations:
        design = _design_vector(
            observation.features,
            rotation_degrees=rotation_degrees,
        )
        term = _log_probability_bounds(
            _score_interval(box, design),
            accepted=observation.accepted,
        )
        lower_terms.append(term.lower)
        upper_terms.append(term.upper)
    return LikelihoodBounds(
        lower=_directed_sum(lower_terms, rounding=ROUND_FLOOR),
        upper=_directed_sum(upper_terms, rounding=ROUND_CEILING),
    )


def common_log_likelihood_cutoff_lower(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    alpha_level: Fraction = COMMON_ALPHA,
) -> Decimal:
    if not observations:
        raise ValueError("observations must not be empty")
    if not 0 < alpha_level < 1:
        raise ValueError("alpha_level must lie strictly between zero and one")

    terms: list[Decimal] = []
    for observation in observations:
        probability = (
            observation.predictive_probability
            if observation.accepted
            else 1.0 - observation.predictive_probability
        )
        probability_fraction = _fraction(probability)
        if probability_fraction <= 0 or probability_fraction >= 1:
            raise ValueError("predictive outcome probability must lie strictly between zero and one")
        terms.append(_log_fraction_lower(probability_fraction))
    log_joint_lower = _directed_sum(terms, rounding=ROUND_FLOOR)
    log_alpha_lower = _log_fraction_lower(alpha_level)
    return _directed_sum((log_joint_lower, log_alpha_lower), rounding=ROUND_FLOOR)


def _invert_three_by_three(
    rows: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...] | None:
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("matrix must be 3 x 3")
    matrix = [
        list(row) + [Fraction(int(row_index == column)) for column in range(3)]
        for row_index, row in enumerate(rows)
    ]
    for column in range(3):
        pivot = next(
            (row for row in range(column, 3) if matrix[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        pivot_value = matrix[column][column]
        matrix[column] = [value / pivot_value for value in matrix[column]]
        for row in range(3):
            if row == column:
                continue
            factor = matrix[row][column]
            if factor == 0:
                continue
            matrix[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[column], strict=True)
            ]
    return tuple(tuple(matrix[row][3:]) for row in range(3))


def _linear_interval_transform(
    matrix: Sequence[Sequence[Fraction]],
    intervals: Sequence[tuple[Fraction, Fraction]],
) -> tuple[tuple[Fraction, Fraction], ...]:
    transformed: list[tuple[Fraction, Fraction]] = []
    for row in matrix:
        lower = Fraction(0)
        upper = Fraction(0)
        for coefficient, (interval_lower, interval_upper) in zip(row, intervals, strict=True):
            if coefficient >= 0:
                lower += coefficient * interval_lower
                upper += coefficient * interval_upper
            else:
                lower += coefficient * interval_upper
                upper += coefficient * interval_lower
        transformed.append((lower, upper))
    return tuple(transformed)


def initial_nuisance_box(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    common_cutoff_lower: Decimal,
) -> ParameterBox | None:
    if not observations:
        raise ValueError("observations must not be empty")
    cutoff = Fraction(common_cutoff_lower)
    if cutoff >= 0:
        return None

    counts: dict[tuple[float, float], list[int]] = defaultdict(lambda: [0, 0])
    for observation in observations:
        if len(observation.features) != 2:
            raise ValueError("continuous v14 certificate currently requires two features")
        key = (float(observation.features[0]), float(observation.features[1]))
        counts[key][1 if observation.accepted else 0] += 1

    mixed_features = [
        features
        for features, (reject_count, accept_count) in counts.items()
        if reject_count > 0 and accept_count > 0
    ]
    best_box: ParameterBox | None = None
    best_log_volume: float | None = None

    for feature_triplet in combinations(mixed_features, 3):
        design_rows = tuple(_design_vector(features) for features in feature_triplet)
        inverse = _invert_three_by_three(design_rows)
        if inverse is None:
            continue

        score_intervals: list[tuple[Fraction, Fraction]] = []
        for features in feature_triplet:
            reject_count, accept_count = counts[features]
            score_intervals.append(
                (
                    cutoff / accept_count,
                    -cutoff / reject_count,
                )
            )
        parameter_intervals = _linear_interval_transform(inverse, score_intervals)
        box = ParameterBox(parameter_intervals)
        widths = [float(upper - lower) for lower, upper in box.intervals]
        if any(width <= 0.0 for width in widths):
            continue
        # Product comparison without constructing enormous exact rational products.
        log_volume = sum(__import__("math").log(width) for width in widths)
        if best_log_volume is None or log_volume < best_log_volume:
            best_log_volume = log_volume
            best_box = box
    return best_box


def _cone_halfspaces(
    center_slope: Sequence[float],
    *,
    target_error: float,
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    if len(center_slope) != 2:
        raise ValueError("center_slope must have two coordinates")
    center_x = float(center_slope[0])
    center_y = float(center_slope[1])
    norm = hypot(center_x, center_y)
    if norm <= 1e-15:
        raise ValueError("center_slope must be nonzero")
    if not 0.0 < target_error < 0.5:
        raise ValueError("target_error must lie strictly between zero and one half")

    unit_x = center_x / norm
    unit_y = center_y / norm
    perpendicular_x = -unit_y
    perpendicular_y = unit_x
    delta = target_error * pi
    sine = sin(delta)
    cosine = cos(delta)
    return (
        (
            _fraction(sine * unit_x + cosine * perpendicular_x),
            _fraction(sine * unit_y + cosine * perpendicular_y),
        ),
        (
            _fraction(sine * unit_x - cosine * perpendicular_x),
            _fraction(sine * unit_y - cosine * perpendicular_y),
        ),
    )


def _minimum_halfspace_value(
    box: ParameterBox,
    coefficients: Sequence[Fraction],
) -> Fraction:
    if len(coefficients) != 2:
        raise ValueError("halfspace must act on the two slope coordinates")
    value = Fraction(0)
    for coefficient, (lower, upper) in zip(
        coefficients,
        box.intervals[1:],
        strict=True,
    ):
        value += coefficient * (lower if coefficient >= 0 else upper)
    return value


def _cone_log_e_lower_bound(
    box: ParameterBox,
    observations: Sequence[PrequentialBinaryObservation],
) -> Decimal:
    null_upper = likelihood_bounds(box, observations).upper
    alternative_lowers = [
        likelihood_bounds(
            box,
            observations,
            rotation_degrees=float(offset),
        ).lower
        for offset in CONE_OFFSETS_DEGREES
    ]
    best_alternative_lower = max(alternative_lowers)
    log_support_upper = _log_fraction_upper(Fraction(len(CONE_OFFSETS_DEGREES)))
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = ROUND_FLOOR
        return best_alternative_lower - log_support_upper - null_upper


def _largest_width_dimension(box: ParameterBox) -> int:
    return max(
        range(3),
        key=lambda index: float(box.intervals[index][1] - box.intervals[index][0]),
    )


def _split_box(box: ParameterBox) -> tuple[ParameterBox, ParameterBox]:
    dimension = _largest_width_dimension(box)
    lower, upper = box.intervals[dimension]
    midpoint = (lower + upper) / 2
    left = list(box.intervals)
    right = list(box.intervals)
    left[dimension] = (lower, midpoint)
    right[dimension] = (midpoint, upper)
    return ParameterBox(tuple(left)), ParameterBox(tuple(right))


def _certify_cone_side(
    initial_box: ParameterBox,
    observations: Sequence[PrequentialBinaryObservation],
    *,
    halfspace: Sequence[Fraction],
    common_cutoff_lower: Decimal,
    cone_log_threshold_upper: Decimal,
    max_nodes: int,
    min_width: float,
) -> ConeSideCertificate:
    stack = [initial_box]
    nodes_visited = 0

    while stack:
        if nodes_visited >= max_nodes:
            return ConeSideCertificate(
                certified=False,
                nodes_visited=nodes_visited,
                unresolved_boxes=len(stack),
                reason="node_limit",
            )
        box = stack.pop()
        nodes_visited += 1

        if _minimum_halfspace_value(box, halfspace) >= 0:
            continue

        null_bounds = likelihood_bounds(box, observations)
        if null_bounds.upper <= common_cutoff_lower:
            continue

        if _cone_log_e_lower_bound(box, observations) >= cone_log_threshold_upper:
            continue

        widths = [float(upper - lower) for lower, upper in box.intervals]
        if max(widths) <= min_width:
            return ConeSideCertificate(
                certified=False,
                nodes_visited=nodes_visited,
                unresolved_boxes=len(stack) + 1,
                reason="resolution_limit",
            )
        stack.extend(_split_box(box))

    return ConeSideCertificate(
        certified=True,
        nodes_visited=nodes_visited,
        unresolved_boxes=0,
        reason="all_violating_boxes_pruned",
    )


def certify_continuous_cone_current(
    observations: Sequence[PrequentialBinaryObservation],
    center_slope: Sequence[float],
    *,
    target_error: float = 0.15,
    common_alpha: Fraction = COMMON_ALPHA,
    cone_alpha: Fraction = CONE_ALPHA,
    max_nodes: int = 20_000,
    min_width: float = 1e-5,
) -> ContinuousConeCertificate:
    if not observations:
        raise ValueError("observations must not be empty")
    if common_alpha <= 0 or cone_alpha <= 0 or common_alpha + cone_alpha > TOTAL_ALPHA:
        raise ValueError("split alpha levels must be positive and sum to at most 0.05")
    if max_nodes <= 0:
        raise ValueError("max_nodes must be positive")
    if min_width <= 0.0:
        raise ValueError("min_width must be positive")

    cone_log_threshold_upper = _log_fraction_upper(1 / cone_alpha)
    common_cutoff_lower = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=common_alpha,
    )
    initial_box = initial_nuisance_box(
        observations,
        common_cutoff_lower=common_cutoff_lower,
    )
    if initial_box is None:
        return ContinuousConeCertificate(
            certified=False,
            initial_box=None,
            side_certificates=(),
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            reason="no_finite_nuisance_box",
        )

    try:
        halfspaces = _cone_halfspaces(center_slope, target_error=target_error)
    except ValueError as error:
        return ContinuousConeCertificate(
            certified=False,
            initial_box=initial_box,
            side_certificates=(),
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            reason=str(error),
        )

    side_certificates = tuple(
        _certify_cone_side(
            initial_box,
            observations,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            max_nodes=max_nodes,
            min_width=min_width,
        )
        for halfspace in halfspaces
    )
    return ContinuousConeCertificate(
        certified=all(side.certified for side in side_certificates),
        initial_box=initial_box,
        side_certificates=side_certificates,
        common_cutoff_lower=common_cutoff_lower,
        cone_log_threshold_upper=cone_log_threshold_upper,
        reason=(
            "both_cone_sides_certified"
            if all(side.certified for side in side_certificates)
            else "at_least_one_cone_side_unresolved"
        ),
    )
