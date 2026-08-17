from __future__ import annotations

import json
from collections.abc import Sequence
from fractions import Fraction
from math import prod

from .science_s1_benchmark_v14a import (
    _box_grid,
    _common_exact_cutoff,
    _reference_log_likelihood,
    _synthetic_observations,
)
from .science_s1_benchmark_v14g import _run_fair_best_first_side
from .science_s1_common_polytope import certified_common_polytope_outer_box
from .science_s1_continuous_geometry import (
    COMMON_ALPHA,
    ParameterBox,
    _cone_halfspaces,
    common_log_likelihood_cutoff_lower,
)
from .science_s1_eprocess import PrequentialBinaryObservation

BENCHMARK_VERSION = "s1-exact-common-polytope-v14h"
METHOD_VERSION = "all-score-halfspace-exact-vertex-box-v1"

SCENARIOS = (
    ("aligned_240", (0.15, 1.2, 0.0), 20, 14_601),
    ("aligned_480", (0.15, 1.2, 0.0), 40, 14_602),
)

DIRECTIONAL_CASES = (
    ("aligned_240_side0_negative_control", "aligned_240", 0),
    ("aligned_480_side0", "aligned_480", 0),
    ("aligned_480_side1", "aligned_480", 1),
)

REFERENCE_V14G = {
    "aligned_240_side0_negative_control": {
        "evaluations": 249,
        "unresolved_boxes": 2,
        "certified": False,
        "elapsed_seconds": 44.929193590000005,
    },
    "aligned_480_side0": {
        "evaluations": 249,
        "unresolved_boxes": 5,
        "certified": False,
        "elapsed_seconds": 51.13619508999999,
    },
    "aligned_480_side1": {
        "evaluations": 249,
        "unresolved_boxes": 4,
        "certified": False,
        "elapsed_seconds": 51.15366469100001,
    },
}

KNOWN_240_SURVIVOR = (
    0.6758436374323773,
    1.253551105895155,
    -0.6918084477654259,
)


def _inside_box(box: ParameterBox, theta: Sequence[Fraction]) -> bool:
    return all(
        lower <= value <= upper
        for value, (lower, upper) in zip(theta, box.intervals, strict=True)
    )


def _float_intervals(box: ParameterBox) -> list[list[float]]:
    return [[float(lower), float(upper)] for lower, upper in box.intervals]


def _widths(box: ParameterBox) -> tuple[float, float, float]:
    values = tuple(float(upper - lower) for lower, upper in box.intervals)
    return values[0], values[1], values[2]


def _box_summary(coarse: ParameterBox, tightened: ParameterBox) -> dict[str, object]:
    coarse_widths = _widths(coarse)
    tight_widths = _widths(tightened)
    coarse_volume = prod(coarse_widths)
    tight_volume = prod(tight_widths)
    return {
        "coarse_intervals": _float_intervals(coarse),
        "tightened_intervals": _float_intervals(tightened),
        "coarse_widths": list(coarse_widths),
        "tightened_widths": list(tight_widths),
        "axis_width_ratios": [
            tight / coarse_width
            for tight, coarse_width in zip(
                tight_widths,
                coarse_widths,
                strict=True,
            )
        ],
        "coarse_volume": coarse_volume,
        "tightened_volume": tight_volume,
        "volume_ratio": tight_volume / coarse_volume,
    }


def _direct_retained_grid_validation(
    observations: Sequence[PrequentialBinaryObservation],
    tightened_box: ParameterBox,
) -> dict[str, int]:
    validation_box = ParameterBox(
        (
            (Fraction(-3, 4), Fraction(3, 4)),
            (Fraction(1, 5), Fraction(11, 5)),
            (Fraction(-1), Fraction(1)),
        )
    )
    exact_cutoff = _common_exact_cutoff(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    retained = 0
    excluded_retained = 0
    for theta in _box_grid(validation_box, grid_size=5):
        if _reference_log_likelihood(theta, observations) > exact_cutoff:
            retained += 1
            excluded_retained += int(not _inside_box(tightened_box, theta))
    return {
        "grid_points": 125,
        "direct_retained_points": retained,
        "retained_points_excluded_by_tightened_box": excluded_retained,
    }


def _scenario_result(
    name: str,
    alpha: Sequence[float],
    repeats: int,
    seed: int,
) -> dict[str, object]:
    observations = _synthetic_observations(
        alpha=alpha,
        repeats=repeats,
        seed=seed,
    )
    cutoff = common_log_likelihood_cutoff_lower(
        observations,
        alpha_level=COMMON_ALPHA,
    )
    outer = certified_common_polytope_outer_box(
        observations,
        common_cutoff_lower=cutoff,
    )
    if outer is None:
        raise AssertionError(f"{name} did not produce a finite common outer box")

    validation = _direct_retained_grid_validation(
        observations,
        outer.tightened_box,
    )
    if validation["retained_points_excluded_by_tightened_box"] != 0:
        raise AssertionError("tightened common polytope excluded a direct retained grid point")

    result: dict[str, object] = {
        "scenario": name,
        "observation_count": len(observations),
        "halfspace_count": outer.halfspace_count,
        "feasible_vertex_count": outer.feasible_vertex_count,
        "box": _box_summary(outer.coarse_box, outer.tightened_box),
        "direct_grid_validation": validation,
    }

    if name == "aligned_240":
        survivor = tuple(Fraction.from_float(value) for value in KNOWN_240_SURVIVOR)
        exact_cutoff = _common_exact_cutoff(
            observations,
            alpha_level=COMMON_ALPHA,
        )
        direct_margin = _reference_log_likelihood(survivor, observations) - exact_cutoff
        contained = _inside_box(outer.tightened_box, survivor)
        if direct_margin <= 0:
            raise AssertionError("v14d negative-control point no longer survives common confidence")
        if not contained:
            raise AssertionError("tightened common polytope excluded v14d retained survivor")
        result["known_240_survivor"] = {
            "theta": list(KNOWN_240_SURVIVOR),
            "direct_common_survival_margin": str(direct_margin),
            "contained_in_tightened_box": contained,
        }

    return result


def run_benchmark_v14h() -> dict[str, object]:
    scenario_results = {
        name: _scenario_result(name, alpha, repeats, seed)
        for name, alpha, repeats, seed in SCENARIOS
    }

    directional_results: list[dict[str, object]] = []
    for case_name, scenario_name, side_index in DIRECTIONAL_CASES:
        alpha, repeats, seed = next(
            (alpha, repeats, seed)
            for name, alpha, repeats, seed in SCENARIOS
            if name == scenario_name
        )
        observations = _synthetic_observations(
            alpha=alpha,
            repeats=repeats,
            seed=seed,
        )
        cutoff = common_log_likelihood_cutoff_lower(
            observations,
            alpha_level=COMMON_ALPHA,
        )
        outer = certified_common_polytope_outer_box(
            observations,
            common_cutoff_lower=cutoff,
        )
        if outer is None:
            raise AssertionError(f"{case_name} did not produce a finite common outer box")
        halfspace = _cone_halfspaces((1.0, 0.0), target_error=0.15)[side_index]
        candidate = _run_fair_best_first_side(
            observations,
            outer.tightened_box,
            halfspace=halfspace,
        )
        if case_name == "aligned_240_side0_negative_control" and bool(
            candidate["certified"]
        ):
            raise AssertionError(
                "v14h common-box tightening certified the known retained "
                "outside-cone negative control"
            )
        directional_results.append(
            {
                "case": case_name,
                "reference_v14g": REFERENCE_V14G[case_name],
                "tightened_common_box": candidate,
            }
        )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "method_version": METHOD_VERSION,
        "scientific_scope": (
            "Common-confidence outer-geometry change only. The common e-process cutoff, alpha "
            "split, directional cone-cover e-process, rational cone, coupled bound, sensitivity "
            "split, fair best-first order, precision, and 250-evaluation budget are unchanged. "
            "The new outer box is the exact coordinate bounding box of all necessary per-feature "
            "score halfspaces intersected with the already-certified coarse nuisance box."
        ),
        "scenarios": list(scenario_results.values()),
        "directional_replay": directional_results,
    }


def main() -> None:
    print(json.dumps(run_benchmark_v14h(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
