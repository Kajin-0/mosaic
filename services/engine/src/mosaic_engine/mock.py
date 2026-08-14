import hashlib
from uuid import UUID, uuid5

from mosaic_engine.models import (
    CalibrationNextRequest,
    CalibrationNextResponse,
    CalibrationResponseChoice,
    CalibrationResponseReceipt,
    CalibrationResponseRequest,
    CalibrationStimulus,
    CalibrationStimulusOption,
    MatchRankRequest,
    MatchRankResponse,
    RankedCandidate,
)
from mosaic_engine.version import MOCK_CALIBRATION_POLICY_VERSION, MOCK_RANKER_MODEL_VERSION

_MOCK_NAMESPACE = UUID("4d1c5223-93c7-4e79-a733-4fd19815fe93")
_TEXT_PAIRS = (
    ("Quiet evening at home", "Spontaneous night out"),
    ("Plan the weekend early", "Decide the weekend as it unfolds"),
    ("Frequent small gatherings", "Occasional large gatherings"),
    ("Save toward a future goal", "Spend on a memorable experience"),
    ("Resolve disagreement promptly", "Take time before revisiting disagreement"),
)


def next_calibration_trial(request: CalibrationNextRequest) -> CalibrationNextResponse:
    ordinal = request.completed_trial_count + 1
    experiment_id = uuid5(
        _MOCK_NAMESPACE,
        f"{MOCK_CALIBRATION_POLICY_VERSION}:{request.session_id}:{ordinal}",
    )
    left_label, right_label = _TEXT_PAIRS[request.completed_trial_count % len(_TEXT_PAIRS)]

    return CalibrationNextResponse(
        session_id=request.session_id,
        experiment_id=experiment_id,
        ordinal=ordinal,
        policy_version=MOCK_CALIBRATION_POLICY_VERSION,
        stimulus=CalibrationStimulus(
            left=CalibrationStimulusOption(id="left", label=left_label),
            right=CalibrationStimulusOption(id="right", label=right_label),
        ),
        response_options=list(CalibrationResponseChoice),
    )


def accept_calibration_response(
    request: CalibrationResponseRequest,
) -> CalibrationResponseReceipt:
    return CalibrationResponseReceipt(
        session_id=request.session_id,
        experiment_id=request.experiment_id,
        client_response_id=request.client_response_id,
        policy_version=MOCK_CALIBRATION_POLICY_VERSION,
    )


def _candidate_score(candidate_id: UUID) -> float:
    digest = hashlib.sha256(
        f"{MOCK_RANKER_MODEL_VERSION}:{candidate_id}".encode(),
    ).digest()
    numerator = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return numerator / ((1 << 64) - 1)


def rank_candidates(request: MatchRankRequest) -> MatchRankResponse:
    scored = sorted(
        ((candidate_id, _candidate_score(candidate_id)) for candidate_id in request.candidate_ids),
        key=lambda item: (-item[1], str(item[0])),
    )[: request.limit]

    return MatchRankResponse(
        model_version=MOCK_RANKER_MODEL_VERSION,
        ranked_candidates=[
            RankedCandidate(candidate_id=candidate_id, rank=index, rank_score=round(score, 8))
            for index, (candidate_id, score) in enumerate(scored, start=1)
        ],
    )
