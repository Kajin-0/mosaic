from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from mosaic_engine.measurement_models import MeasurementAnswer, MeasurementItem


class MeasurementStoreRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MeasurementSessionRecord(MeasurementStoreRecord):
    id: UUID
    subject_id: UUID
    instrument_key: str
    instrument_version: str
    selection_policy_version: str
    target_item_count: int
    status: Literal["active", "complete"]
    created_at: datetime
    completed_at: datetime | None = None


class MeasurementPresentationRecord(MeasurementStoreRecord):
    id: UUID
    session_id: UUID
    subject_id: UUID
    ordinal: int
    item_id: str
    item_version: str
    item_kind: str
    selection_policy_version: str
    item: MeasurementItem
    created_at: datetime


class MeasurementResponseRecord(MeasurementStoreRecord):
    id: UUID
    session_id: UUID
    presentation_id: UUID
    subject_id: UUID
    client_response_id: UUID
    answer: MeasurementAnswer
    client_timestamp: datetime | None = None
    server_timestamp: datetime
    instrument_version: str
    selection_policy_version: str


class MeasurementScoreRunRecord(MeasurementStoreRecord):
    id: UUID
    session_id: UUID
    subject_id: UUID
    scoring_version: str
    evidence_fingerprint: str
    response_count: int
    scores: dict[str, float]
    created_at: datetime


class MeasurementStore(Protocol):
    async def get_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
    ) -> MeasurementSessionRecord | None: ...

    async def get_measurement_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> MeasurementSessionRecord | None: ...

    async def create_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
        target_item_count: int,
    ) -> MeasurementSessionRecord: ...

    async def list_measurement_presentations(
        self,
        session_id: UUID,
    ) -> list[MeasurementPresentationRecord]: ...

    async def list_measurement_responses(
        self,
        session_id: UUID,
    ) -> list[MeasurementResponseRecord]: ...

    async def create_measurement_presentation(
        self,
        presentation: MeasurementPresentationRecord,
    ) -> MeasurementPresentationRecord: ...

    async def get_measurement_presentation(
        self,
        presentation_id: UUID,
    ) -> MeasurementPresentationRecord | None: ...

    async def find_measurement_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> MeasurementResponseRecord | None: ...

    async def find_measurement_response_by_presentation_id(
        self,
        presentation_id: UUID,
    ) -> MeasurementResponseRecord | None: ...

    async def create_measurement_response(
        self,
        *,
        subject_id: UUID,
        session_id: UUID,
        presentation_id: UUID,
        client_response_id: UUID,
        answer: MeasurementAnswer,
        client_timestamp: datetime | None,
        instrument_version: str,
        selection_policy_version: str,
    ) -> MeasurementResponseRecord: ...

    async def complete_measurement_session(
        self,
        session_id: UUID,
    ) -> MeasurementSessionRecord: ...

    async def find_measurement_score_run(
        self,
        session_id: UUID,
        scoring_version: str,
        evidence_fingerprint: str,
    ) -> MeasurementScoreRunRecord | None: ...

    async def create_measurement_score_run(
        self,
        *,
        session_id: UUID,
        subject_id: UUID,
        scoring_version: str,
        evidence_fingerprint: str,
        response_count: int,
        scores: dict[str, float],
    ) -> MeasurementScoreRunRecord: ...
