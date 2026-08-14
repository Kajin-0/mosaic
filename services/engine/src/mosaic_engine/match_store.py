from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from mosaic_engine.models import RankedCandidate


class MatchRankRunRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    subject_id: UUID
    model_version: str
    request_fingerprint: str
    candidate_ids: list[UUID]
    requested_limit: int
    ranked_candidates: list[RankedCandidate]
    created_at: datetime


class MatchRankStore(Protocol):
    async def find_match_rank_run(
        self,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
    ) -> MatchRankRunRecord | None: ...

    async def create_match_rank_run(
        self,
        *,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
        candidate_ids: list[UUID],
        requested_limit: int,
        ranked_candidates: list[RankedCandidate],
    ) -> MatchRankRunRecord: ...
