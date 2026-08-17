from __future__ import annotations

from collections.abc import Sequence
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction

from .science_s1_continuous_geometry import (
    CERTIFIED_TARGET_ERROR,
    COMMON_ALPHA,
    CONE_ALPHA,
    CONE_OFFSETS_DEGREES,
    DECIMAL_PRECISION,
    TOTAL_ALPHA,
    ConeSideCertificate,
    ContinuousConeCertificate,
    LikelihoodBounds,
    ParameterBox,
    _cone_halfspaces,
    _decimal_from_fraction,
    _directed_sum,
    _largest_width_dimension,
    _log_fraction_upper,
    _log_probability_bounds,
    _minimum_halfspace_value,
    _score_interval,
    _split_box,
    common_log_likelihood_cutoff_lower,
    initial_nuisance_box,
)
from .science_s1_continuous_geometry_grouped import (
    PreparedGroupedLikelihood,
    _designs_for_rotation,
    grouped_likelihood_bounds,
    prepare_grouped_likelihood,
)
from .science_s1_eprocess import PrequentialBinaryObservation


def _directed_subtract(left: Decimal, right: Decimal, *, rounding: str) -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = rounding
        return left - right


def _directed_multiply(left: Decimal, right: Decimal, *, rounding: str) -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = rounding
        return left * right


def _decimal_interval_from_fraction(value: Fraction) -> tuple[Decimal, Decimal]:
    return (
        _decimal_from_fraction(value, rounding=ROUND_FLOOR),
        _decimal_from_fraction(value, rounding=ROUND_CEILING),
    )


def _interval_multiply(
    left: tuple[Decimal, Decimal],
    right: tuple[Decimal, Decimal],
) -> tuple[Decimal, Decimal]:
    floor_products = tuple(
        _directed_multiply(a, b, rounding=ROUND_FLOOR)
        for a in left
        for b in right
    )
    ceiling_products = tuple(
        _directed_multiply(a, b, rounding=ROUND_CEILING)
        for a in left
        for b in right
    )
    return min(floor_products), max(ceiling_products)


def _interval_scale_nonnegative_integer(
    interval: tuple[Decimal, Decimal],
    count: int,
) -> tuple[Decimal, Decimal]:
    if count < 0:
        raise ValueError("count must be nonnegative")
    multiplier = Decimal(count)
    return (
        _directed_multiply(interval[0], multiplier, rounding=ROUND_FLOOR),
        _directed_multiply(interval[1], multiplier, rounding=ROUND_CEILING),
    )


def _sigmoid_bounds(score_interval: tuple[Fraction, Fraction]) -> tuple[Decimal, Decimal]:
    log_probability = _log_probability_bounds(score_interval, accepted=True)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        lower_midpoint = log_probability.lower.exp()
        upper_midpoint = log_probability.upper.exp()
        return context.next_minus(lower_midpoint), context.next_plus(upper_midpoint)


def _residual_bounds(
    score_interval: tuple[Fraction, Fraction],
    *,
    accepted: bool,
) -> tuple[Decimal, Decimal]:
    sigmoid_lower, sigmoid_upper = _sigmoid_bounds(score_interval)
    outcome = Decimal(1 if accepted else 0)
    return (
        _directed_subtract(outcome, sigmoid_upper, rounding=ROUND_FLOOR),
        _directed_subtract(outcome, sigmoid_lower, rounding=ROUND_CEILING),
    )


def _gradient_term_bounds(
    residual: tuple[Decimal, Decimal],
    coefficient: Fraction,
) -> tuple[Decimal, Decimal]:
    return _interval_multiply(residual, _decimal_interval_from_fraction(coefficient))


def _difference_interval(
    left: tuple[Decimal, Decimal],
    right: tuple[Decimal, Decimal],
) -> tuple[Decimal, Decimal]:
    return (
        _directed_subtract(left[0], right[1], rounding=ROUND_FLOOR),
        _directed_subtract(left[1], right[0], rounding=ROUND_CEILING),
    )


def _box_center(box: ParameterBox) -> tuple[Fraction, Fraction, Fraction]:
    return tuple((lower + upper) / 2 for lower, upper in box.intervals)  # type: ignore[return-value]


def _point_box(theta: Sequence[Fraction]) -> ParameterBox:
    if len(theta) != 3:
        raise ValueError("theta must contain intercept plus two slopes")
    return ParameterBox(tuple((value, value) for value in theta))


def _half_widths(box: ParameterBox) -> tuple[Fraction, Fraction, Fraction]:
    return tuple((upper - lower) / 2 for lower, upper in box.intervals)  # type: ignore[return-value]


def grouped_log_likelihood_ratio_lower_bound(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    *,
    rotation_degrees: float,
) -> Decimal:
    """Rigorous lower bound on log L_rot(theta)-log L_0(theta) over ``box``.

    Unlike the v14a/v14b bound, this keeps the null and rotated alternative coupled.
    It evaluates a directed lower bound at the exact rational box center and then uses
    interval bounds on every gradient component plus the mean-value theorem.
    """

    if float(rotation_degrees) == 0.0:
        return Decimal(0)

    center = _box_center(box)
    center_box = _point_box(center)
    null_center = grouped_likelihood_bounds(center_box, prepared)
    rotated_center = grouped_likelihood_bounds(
        center_box,
        prepared,
        rotation_degrees=rotation_degrees,
    )
    center_ratio_lower = _directed_subtract(
        rotated_center.lower,
        null_center.upper,
        rounding=ROUND_FLOOR,
    )

    null_designs = _designs_for_rotation(prepared, 0.0)
    rotated_designs = _designs_for_rotation(prepared, rotation_degrees)
    gradient_lower_terms: list[list[Decimal]] = [[], [], []]
    gradient_upper_terms: list[list[Decimal]] = [[], [], []]

    for group, null_design, rotated_design in zip(
        prepared.groups,
        null_designs,
        rotated_designs,
        strict=True,
    ):
        null_score = _score_interval(box, null_design)
        rotated_score = _score_interval(box, rotated_design)
        for accepted, count in (
            (True, group.accept_count),
            (False, group.reject_count),
        ):
            if count == 0:
                continue
            null_residual = _residual_bounds(null_score, accepted=accepted)
            rotated_residual = _residual_bounds(rotated_score, accepted=accepted)
            for axis in range(3):
                rotated_term = _gradient_term_bounds(
                    rotated_residual,
                    rotated_design[axis],
                )
                null_term = _gradient_term_bounds(null_residual, null_design[axis])
                difference = _difference_interval(rotated_term, null_term)
                scaled = _interval_scale_nonnegative_integer(difference, count)
                gradient_lower_terms[axis].append(scaled[0])
                gradient_upper_terms[axis].append(scaled[1])

    gradient_bounds: list[tuple[Decimal, Decimal]] = []
    for axis in range(3):
        gradient_bounds.append(
            (
                _directed_sum(gradient_lower_terms[axis], rounding=ROUND_FLOOR),
                _directed_sum(gradient_upper_terms[axis], rounding=ROUND_CEILING),
            )
        )

    penalties: list[Decimal] = []
    for width, (gradient_lower, gradient_upper) in zip(
        _half_widths(box),
        gradient_bounds,
        strict=True,
    ):
        width_upper = _decimal_from_fraction(width, rounding=ROUND_CEILING)
        gradient_abs_upper = max(abs(gradient_lower), abs(gradient_upper))
        penalties.append(
            _directed_multiply(
                width_upper,
                gradient_abs_upper,
                rounding=ROUND_CEILING,
            )
        )
    total_penalty = _directed_sum(penalties, rounding=ROUND_CEILING)
    return _directed_subtract(
        center_ratio_lower,
        total_penalty,
        rounding=ROUND_FLOOR,
    )


def grouped_coupled_cone_log_e_lower_bound(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
) -> Decimal:
    ratio_lowers = tuple(
        grouped_log_likelihood_ratio_lower_bound(
            box,
            prepared,
            rotation_degrees=float(offset),
        )
        for offset in CONE_OFFSETS_DEGREES
    )
    best_ratio_lower = max(ratio_lowers)
    log_support_upper = _log_fraction_upper(Fraction(len(CONE_OFFSETS_DEGREES)))
    return _directed_subtract(
        best_ratio_lower,
        log_support_upper,
        rounding=ROUND_FLOOR,
    )


def _certify_cone_side_coupled(
    initial_box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
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

        null_bounds = grouped_likelihood_bounds(box, prepared)
        if null_bounds.upper <= common_cutoff_lower:
            continue

        if grouped_coupled_cone_log_e_lower_bound(box, prepared) >= cone_log_threshold_upper:
            continue

        widths = [float(upper - lower) for lower, upper in box.intervals]
        if max(widths) <= min_width:
            return ConeSideCertificate(
                certified=False,
                nodes_visited=nodes_visited,
                unresolved_boxes=len(stack) + 1,
                reason="resolution_limit",
            )
        dimension = _largest_width_dimension(box)
        if box.intervals[dimension][0] == box.intervals[dimension][1]:
            return ConeSideCertificate(
                certified=False,
                nodes_visited=nodes_visited,
                unresolved_boxes=len(stack) + 1,
                reason="degenerate_unresolved_box",
            )
        stack.extend(_split_box(box))

    return ConeSideCertificate(
        certified=True,
        nodes_visited=nodes_visited,
        unresolved_boxes=0,
        reason="all_violating_boxes_pruned",
    )


def certify_continuous_cone_current_coupled(
    observations: Sequence[PrequentialBinaryObservation],
    center_slope: Sequence[float],
    *,
    target_error: float = CERTIFIED_TARGET_ERROR,
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

    prepared = prepare_grouped_likelihood(observations)
    side_certificates = tuple(
        _certify_cone_side_coupled(
            initial_box,
            prepared,
            halfspace=halfspace,
            common_cutoff_lower=common_cutoff_lower,
            cone_log_threshold_upper=cone_log_threshold_upper,
            max_nodes=max_nodes,
            min_width=min_width,
        )
        for halfspace in halfspaces
    )
    certified = all(side.certified for side in side_certificates)
    return ContinuousConeCertificate(
        certified=certified,
        initial_box=initial_box,
        side_certificates=side_certificates,
        common_cutoff_lower=common_cutoff_lower,
        cone_log_threshold_upper=cone_log_threshold_upper,
        reason=(
            "both_cone_sides_certified"
            if certified
            else "at_least_one_cone_side_unresolved"
        ),
    )
