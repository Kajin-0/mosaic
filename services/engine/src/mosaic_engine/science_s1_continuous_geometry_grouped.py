from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
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
    _certify_cone_side,
    _cone_halfspaces,
    _design_vector,
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
from .science_s1_eprocess import PrequentialBinaryObservation


@dataclass(frozen=True)
class GroupedFeatureCounts:
    features: tuple[float, float]
    accept_count: int
    reject_count: int

    def __post_init__(self) -> None:
        if self.accept_count < 0 or self.reject_count < 0:
            raise ValueError("grouped outcome counts must be nonnegative")
        if self.accept_count + self.reject_count <= 0:
            raise ValueError("grouped feature must contain at least one observation")


@dataclass(frozen=True)
class PreparedRotationDesign:
    rotation_degrees: float
    designs: tuple[tuple[Fraction, Fraction, Fraction], ...]


@dataclass(frozen=True)
class PreparedGroupedLikelihood:
    groups: tuple[GroupedFeatureCounts, ...]
    rotations: tuple[PreparedRotationDesign, ...]
    observation_count: int


def group_binary_observations(
    observations: Sequence[PrequentialBinaryObservation],
) -> tuple[GroupedFeatureCounts, ...]:
    if not observations:
        raise ValueError("observations must not be empty")

    counts: dict[tuple[float, float], list[int]] = defaultdict(lambda: [0, 0])
    for observation in observations:
        if len(observation.features) != 2:
            raise ValueError("continuous v14 grouped bounds require two slope features")
        key = (float(observation.features[0]), float(observation.features[1]))
        if observation.accepted:
            counts[key][0] += 1
        else:
            counts[key][1] += 1

    return tuple(
        GroupedFeatureCounts(
            features=features,
            accept_count=outcome_counts[0],
            reject_count=outcome_counts[1],
        )
        for features, outcome_counts in sorted(counts.items())
    )


def prepare_grouped_likelihood(
    observations: Sequence[PrequentialBinaryObservation],
    *,
    rotations_degrees: Sequence[float] = (0.0, *CONE_OFFSETS_DEGREES),
) -> PreparedGroupedLikelihood:
    groups = group_binary_observations(observations)
    rotations = tuple(float(value) for value in rotations_degrees)
    if len(set(rotations)) != len(rotations):
        raise ValueError("rotations_degrees must not contain duplicates")

    prepared_rotations = tuple(
        PreparedRotationDesign(
            rotation_degrees=rotation,
            designs=tuple(
                _design_vector(group.features, rotation_degrees=rotation) for group in groups
            ),
        )
        for rotation in rotations
    )
    return PreparedGroupedLikelihood(
        groups=groups,
        rotations=prepared_rotations,
        observation_count=sum(group.accept_count + group.reject_count for group in groups),
    )


def _directed_integer_multiply(value: Decimal, count: int, *, rounding: str) -> Decimal:
    if count < 0:
        raise ValueError("count must be nonnegative")
    if count == 0:
        return Decimal(0)
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        context.rounding = rounding
        return value * Decimal(count)


def _designs_for_rotation(
    prepared: PreparedGroupedLikelihood,
    rotation_degrees: float,
) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
    target = float(rotation_degrees)
    for prepared_rotation in prepared.rotations:
        if prepared_rotation.rotation_degrees == target:
            return prepared_rotation.designs
    raise ValueError(f"rotation {target} was not prepared")


def grouped_likelihood_bounds(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
    *,
    rotation_degrees: float = 0.0,
) -> LikelihoodBounds:
    designs = _designs_for_rotation(prepared, rotation_degrees)
    lower_terms: list[Decimal] = []
    upper_terms: list[Decimal] = []

    for group, design in zip(prepared.groups, designs, strict=True):
        score_interval = _score_interval(box, design)
        if group.accept_count:
            accepted = _log_probability_bounds(score_interval, accepted=True)
            lower_terms.append(
                _directed_integer_multiply(
                    accepted.lower,
                    group.accept_count,
                    rounding=ROUND_FLOOR,
                )
            )
            upper_terms.append(
                _directed_integer_multiply(
                    accepted.upper,
                    group.accept_count,
                    rounding=ROUND_CEILING,
                )
            )
        if group.reject_count:
            rejected = _log_probability_bounds(score_interval, accepted=False)
            lower_terms.append(
                _directed_integer_multiply(
                    rejected.lower,
                    group.reject_count,
                    rounding=ROUND_FLOOR,
                )
            )
            upper_terms.append(
                _directed_integer_multiply(
                    rejected.upper,
                    group.reject_count,
                    rounding=ROUND_CEILING,
                )
            )

    return LikelihoodBounds(
        lower=_directed_sum(lower_terms, rounding=ROUND_FLOOR),
        upper=_directed_sum(upper_terms, rounding=ROUND_CEILING),
    )


def grouped_cone_log_e_lower_bound(
    box: ParameterBox,
    prepared: PreparedGroupedLikelihood,
) -> Decimal:
    null_upper = grouped_likelihood_bounds(box, prepared).upper
    alternative_lowers = [
        grouped_likelihood_bounds(
            box,
            prepared,
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


def _certify_cone_side_grouped(
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

        if grouped_cone_log_e_lower_bound(box, prepared) >= cone_log_threshold_upper:
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


def certify_continuous_cone_current_grouped(
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
        _certify_cone_side_grouped(
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
