from __future__ import annotations

import json
from math import comb
from typing import cast

from .science_s1_benchmark_v13d import run_benchmark_v13d

BENCHMARK_VERSION = "s1-numerator-validation-benchmark-v13e"
SEEDS = tuple(range(192, 320))
PRIMARY_HORIZON = 240
CONTROL = "mixture_all"
CANDIDATES = ("mle_face", "snml")
MIN_ABSOLUTE_STOP_LIFT = 0.10
MAX_PAIRED_P_VALUE = 0.01


def _stopped_by(path: dict[str, object], predictor: str, horizon: int) -> bool:
    stops = cast(dict[str, object], path["first_stop"])
    stop = stops[predictor]
    if stop is None:
        return False
    return cast(int, cast(dict[str, object], stop)["observation_count"]) <= horizon


def _geometry_violation(path: dict[str, object], predictor: str, horizon: int) -> bool:
    stops = cast(dict[str, object], path["first_stop"])
    stop = stops[predictor]
    if stop is None:
        return False
    record = cast(dict[str, object], stop)
    return (
        cast(int, record["observation_count"]) <= horizon
        and bool(record["false_stop"])
        and bool(record["true_in_confidence_set"])
    )


def _paired_exact_p_value(candidate_only: int, control_only: int) -> float:
    discordant = candidate_only + control_only
    if discordant == 0:
        return 1.0
    smaller = min(candidate_only, control_only)
    lower_tail = sum(comb(discordant, k) for k in range(smaller + 1)) / (2**discordant)
    return min(1.0, 2.0 * lower_tail)


def _summary_by_predictor(result: dict[str, object], horizon: int) -> dict[str, dict[str, object]]:
    summaries = cast(list[dict[str, object]], result["predictor_summaries"])
    return {
        cast(str, summary["predictor"]): summary
        for summary in summaries
        if cast(int, summary["horizon"]) == horizon
    }


def _prospective_validation(result: dict[str, object]) -> dict[str, object]:
    paths = cast(list[dict[str, object]], result["paths"])
    by_predictor = _summary_by_predictor(result, PRIMARY_HORIZON)
    control_stop_rate = float(by_predictor[CONTROL]["stop_rate"])

    candidate_results: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        candidate_stop_rate = float(by_predictor[candidate]["stop_rate"])
        candidate_only = sum(
            _stopped_by(path, candidate, PRIMARY_HORIZON)
            and not _stopped_by(path, CONTROL, PRIMARY_HORIZON)
            for path in paths
        )
        control_only = sum(
            _stopped_by(path, CONTROL, PRIMARY_HORIZON)
            and not _stopped_by(path, candidate, PRIMARY_HORIZON)
            for path in paths
        )
        paired_p = _paired_exact_p_value(candidate_only, control_only)
        lift = candidate_stop_rate - control_stop_rate
        geometry_violations = sum(
            _geometry_violation(path, candidate, PRIMARY_HORIZON) for path in paths
        )
        candidate_results.append(
            {
                "predictor": candidate,
                "stop_rate": candidate_stop_rate,
                "absolute_stop_lift_vs_control": lift,
                "candidate_only_stops": candidate_only,
                "control_only_stops": control_only,
                "paired_exact_p_value": paired_p,
                "geometry_violations": geometry_violations,
                "passes_replication_gate": (
                    lift >= MIN_ABSOLUTE_STOP_LIFT
                    and paired_p <= MAX_PAIRED_P_VALUE
                    and geometry_violations == 0
                ),
            }
        )

    left, right = CANDIDATES
    left_only = sum(
        _stopped_by(path, left, PRIMARY_HORIZON)
        and not _stopped_by(path, right, PRIMARY_HORIZON)
        for path in paths
    )
    right_only = sum(
        _stopped_by(path, right, PRIMARY_HORIZON)
        and not _stopped_by(path, left, PRIMARY_HORIZON)
        for path in paths
    )
    head_to_head_p = _paired_exact_p_value(left_only, right_only)

    return {
        "prespecified_primary_horizon": PRIMARY_HORIZON,
        "control": CONTROL,
        "candidate_predictors": CANDIDATES,
        "replication_gate": {
            "minimum_absolute_stop_lift": MIN_ABSOLUTE_STOP_LIFT,
            "maximum_paired_exact_p_value": MAX_PAIRED_P_VALUE,
            "required_geometry_violations": 0,
        },
        "control_stop_rate": control_stop_rate,
        "candidate_results": candidate_results,
        "candidate_head_to_head": {
            "left": left,
            "right": right,
            "left_only_stops": left_only,
            "right_only_stops": right_only,
            "paired_exact_p_value": head_to_head_p,
            "ranking_established_at_0_05": head_to_head_p <= 0.05,
        },
    }


def run_benchmark_v13e() -> dict[str, object]:
    result = run_benchmark_v13d(seeds=SEEDS)
    result["benchmark_version"] = BENCHMARK_VERSION
    result["scientific_scope"] = (
        "Fresh-seed prospective validation of the v13d numerator-efficiency result. Seeds "
        "192..319 are disjoint from v13c and v13d. The 5-degree finite model, true directions, "
        "target, alpha, candidate bank, disagreement query controller, common-path semantics, "
        "and predictor definitions are frozen. mixture_all is the control; mle_face and snml "
        "are the prespecified adaptive candidates. Oracle truth remains diagnostic only."
    )
    result["prospective_validation"] = _prospective_validation(result)
    return result


def main() -> None:
    print(json.dumps(run_benchmark_v13e(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
