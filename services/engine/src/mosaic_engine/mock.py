import hashlib
from uuid import UUID

from mosaic_engine.models import MatchRankRequest, MatchRankResponse, RankedCandidate
from mosaic_engine.version import MOCK_RANKER_MODEL_VERSION


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
