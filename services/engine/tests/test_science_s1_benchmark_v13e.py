from __future__ import annotations

import pytest

from mosaic_engine.science_s1_benchmark_v13e import (
    CANDIDATES,
    CONTROL,
    MAX_PAIRED_P_VALUE,
    MIN_ABSOLUTE_STOP_LIFT,
    PRIMARY_HORIZON,
    SEEDS,
    _paired_exact_p_value,
    _prospective_validation,
)


def test_v13e_seed_block_is_fresh() -> None:
    assert min(SEEDS) == 192
    assert max(SEEDS) == 319
    assert len(SEEDS) == 128


def test_paired_exact_p_value_handles_symmetric_and_extreme_discordance() -> None:
    assert _paired_exact_p_value(0, 0) == pytest.approx(1.0)
    assert _paired_exact_p_value(10, 10) == pytest.approx(1.0)
    assert _paired_exact_p_value(20, 0) < 0.01


def test_prospective_validation_applies_prespecified_gate() -> None:
    paths = []
    for index in range(20):
        control_stop = index < 2
        mle_stop = index < 15
        snml_stop = index < 14
        paths.append(
            {
                "first_stop": {
                    CONTROL: (
                        {
                            "observation_count": 220,
                            "false_stop": False,
                            "true_in_confidence_set": True,
                        }
                        if control_stop
                        else None
                    ),
                    "mle_face": (
                        {
                            "observation_count": 210,
                            "false_stop": False,
                            "true_in_confidence_set": True,
                        }
                        if mle_stop
                        else None
                    ),
                    "snml": (
                        {
                            "observation_count": 215,
                            "false_stop": False,
                            "true_in_confidence_set": True,
                        }
                        if snml_stop
                        else None
                    ),
                }
            }
        )

    result = {
        "paths": paths,
        "predictor_summaries": [
            {"predictor": CONTROL, "horizon": PRIMARY_HORIZON, "stop_rate": 2 / 20},
            {"predictor": "mle_face", "horizon": PRIMARY_HORIZON, "stop_rate": 15 / 20},
            {"predictor": "snml", "horizon": PRIMARY_HORIZON, "stop_rate": 14 / 20},
        ],
    }
    validation = _prospective_validation(result)

    assert validation["control"] == CONTROL
    assert validation["candidate_predictors"] == CANDIDATES
    assert validation["replication_gate"] == {
        "minimum_absolute_stop_lift": MIN_ABSOLUTE_STOP_LIFT,
        "maximum_paired_exact_p_value": MAX_PAIRED_P_VALUE,
        "required_geometry_violations": 0,
    }
    for candidate in validation["candidate_results"]:
        assert candidate["passes_replication_gate"] is True
        assert candidate["geometry_violations"] == 0
