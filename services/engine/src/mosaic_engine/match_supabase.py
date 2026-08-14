from uuid import UUID

from mosaic_engine.match_store import MatchRankRunRecord
from mosaic_engine.models import RankedCandidate
from mosaic_engine.supabase import SupabaseGateway


class MatchSupabaseStore:
    def __init__(self, gateway: SupabaseGateway) -> None:
        self._gateway = gateway

    async def find_match_rank_run(
        self,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
    ) -> MatchRankRunRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/match_rank_runs",
            params={
                "select": "*",
                "subject_id": f"eq.{subject_id}",
                "model_version": f"eq.{model_version}",
                "request_fingerprint": f"eq.{request_fingerprint}",
                "limit": "1",
            },
        )
        return MatchRankRunRecord.model_validate(rows[0]) if rows else None

    async def create_match_rank_run(
        self,
        *,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
        candidate_ids: list[UUID],
        requested_limit: int,
        ranked_candidates: list[RankedCandidate],
    ) -> MatchRankRunRecord:
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/match_rank_runs",
            json={
                "subject_id": str(subject_id),
                "model_version": model_version,
                "request_fingerprint": request_fingerprint,
                "candidate_ids": [str(candidate_id) for candidate_id in candidate_ids],
                "requested_limit": requested_limit,
                "ranked_candidates": [
                    candidate.model_dump(mode="json") for candidate in ranked_candidates
                ],
            },
            prefer="return=representation",
            expected={201},
        )
        return MatchRankRunRecord.model_validate(rows[0])
