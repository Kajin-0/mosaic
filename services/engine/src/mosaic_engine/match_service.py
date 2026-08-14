import hashlib
import json
from uuid import UUID

from mosaic_engine.match_store import MatchRankRunRecord, MatchRankStore
from mosaic_engine.mock import rank_candidates
from mosaic_engine.models import MatchRankRequest, PersistedMatchRankResponse, RankedCandidate
from mosaic_engine.supabase import SupabaseConflictError
from mosaic_engine.version import MOCK_RANKER_MODEL_VERSION


class MatchRankingConflictError(RuntimeError):
    pass


class MatchRankingService:
    def __init__(self, store: MatchRankStore) -> None:
        self._store = store

    async def rank(
        self,
        subject_id: UUID,
        request: MatchRankRequest,
    ) -> PersistedMatchRankResponse:
        candidate_ids = sorted(request.candidate_ids, key=str)
        request_fingerprint = self._request_fingerprint(candidate_ids, request.limit)
        ranked = rank_candidates(request).ranked_candidates

        existing = await self._store.find_match_rank_run(
            subject_id,
            MOCK_RANKER_MODEL_VERSION,
            request_fingerprint,
        )
        if existing is not None:
            self._assert_same_run(existing, candidate_ids, request.limit, ranked)
            return self._response(existing)

        try:
            stored = await self._store.create_match_rank_run(
                subject_id=subject_id,
                model_version=MOCK_RANKER_MODEL_VERSION,
                request_fingerprint=request_fingerprint,
                candidate_ids=candidate_ids,
                requested_limit=request.limit,
                ranked_candidates=ranked,
            )
        except SupabaseConflictError as exc:
            raced = await self._store.find_match_rank_run(
                subject_id,
                MOCK_RANKER_MODEL_VERSION,
                request_fingerprint,
            )
            if raced is None:
                raise MatchRankingConflictError(
                    "Match-ranking run conflicted without a reconstructable persisted result.",
                ) from exc
            self._assert_same_run(raced, candidate_ids, request.limit, ranked)
            stored = raced

        return self._response(stored)

    def _request_fingerprint(self, candidate_ids: list[UUID], requested_limit: int) -> str:
        payload = {
            "candidate_ids": [str(candidate_id) for candidate_id in candidate_ids],
            "limit": requested_limit,
            "model_version": MOCK_RANKER_MODEL_VERSION,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def _assert_same_run(
        self,
        stored: MatchRankRunRecord,
        candidate_ids: list[UUID],
        requested_limit: int,
        ranked_candidates: list[RankedCandidate],
    ) -> None:
        if (
            stored.model_version != MOCK_RANKER_MODEL_VERSION
            or stored.candidate_ids != candidate_ids
            or stored.requested_limit != requested_limit
            or stored.ranked_candidates != ranked_candidates
        ):
            raise MatchRankingConflictError(
                "Persisted ranking fingerprint resolved to different immutable model output.",
            )

    def _response(self, record: MatchRankRunRecord) -> PersistedMatchRankResponse:
        return PersistedMatchRankResponse(
            run_id=record.id,
            model_version=record.model_version,
            request_fingerprint=record.request_fingerprint,
            ranked_candidates=record.ranked_candidates,
            created_at=record.created_at,
        )
