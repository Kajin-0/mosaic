from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from mosaic_engine.models import CalibrationResponseChoice
from mosaic_engine.synthetic_models import (
    SyntheticGenerationProvenance,
    SyntheticStimulusSpecification,
)


class SyntheticStoreRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")


class SyntheticCalibrationSessionRecord(SyntheticStoreRecord):
    id: UUID
    subject_id: UUID
    instrument_key: str
    instrument_version: str
    pair_policy_version: str
    generator_adapter_version: str
    target_trial_count: int
    status: Literal["active", "complete"]
    created_at: datetime
    completed_at: datetime | None = None


class SyntheticStimulusSpecRecord(SyntheticStoreRecord):
    id: UUID
    session_id: UUID
    subject_id: UUID
    stimulus_key: str
    spec_version: str
    specification_sha256: str
    specification: SyntheticStimulusSpecification
    created_at: datetime


class SyntheticAssetRecord(SyntheticStoreRecord):
    id: UUID
    spec_id: UUID
    session_id: UUID
    subject_id: UUID
    media_type: str
    content_sha256: str
    asset_uri: str
    generation_provenance: SyntheticGenerationProvenance
    created_at: datetime


class SyntheticQcEventRecord(SyntheticStoreRecord):
    id: UUID
    asset_id: UUID
    session_id: UUID
    subject_id: UUID
    qc_version: str
    decision: Literal["accepted", "rejected"]
    reasons: list[str]
    created_at: datetime


class SyntheticPairRecord(SyntheticStoreRecord):
    id: UUID
    session_id: UUID
    subject_id: UUID
    ordinal: int
    left_asset_id: UUID
    right_asset_id: UUID
    randomization_seed: int
    pair_policy_version: str
    created_at: datetime


class SyntheticCalibrationResponseRecord(SyntheticStoreRecord):
    id: UUID
    session_id: UUID
    pair_id: UUID
    subject_id: UUID
    client_response_id: UUID
    response: CalibrationResponseChoice
    client_timestamp: datetime | None = None
    server_timestamp: datetime
    pair_policy_version: str


class SyntheticCalibrationStore(Protocol):
    async def get_synthetic_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        pair_policy_version: str,
        generator_adapter_version: str,
    ) -> SyntheticCalibrationSessionRecord | None: ...

    async def get_synthetic_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord | None: ...

    async def create_synthetic_session(
        self,
        *,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        pair_policy_version: str,
        generator_adapter_version: str,
        target_trial_count: int,
    ) -> SyntheticCalibrationSessionRecord: ...

    async def complete_synthetic_session(
        self,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord: ...

    async def list_synthetic_pairs(self, session_id: UUID) -> list[SyntheticPairRecord]: ...

    async def create_synthetic_spec(
        self,
        record: SyntheticStimulusSpecRecord,
    ) -> SyntheticStimulusSpecRecord: ...

    async def get_synthetic_spec(self, spec_id: UUID) -> SyntheticStimulusSpecRecord | None: ...

    async def create_synthetic_asset(
        self,
        record: SyntheticAssetRecord,
    ) -> SyntheticAssetRecord: ...

    async def get_synthetic_asset(self, asset_id: UUID) -> SyntheticAssetRecord | None: ...

    async def create_synthetic_qc_event(
        self,
        record: SyntheticQcEventRecord,
    ) -> SyntheticQcEventRecord: ...

    async def get_synthetic_qc_event(
        self,
        qc_event_id: UUID,
    ) -> SyntheticQcEventRecord | None: ...

    async def create_synthetic_pair(
        self,
        record: SyntheticPairRecord,
    ) -> SyntheticPairRecord: ...

    async def get_synthetic_pair(self, pair_id: UUID) -> SyntheticPairRecord | None: ...

    async def list_synthetic_responses(
        self,
        session_id: UUID,
    ) -> list[SyntheticCalibrationResponseRecord]: ...

    async def find_synthetic_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None: ...

    async def find_synthetic_response_by_pair_id(
        self,
        pair_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None: ...

    async def create_synthetic_response(
        self,
        *,
        subject_id: UUID,
        session_id: UUID,
        pair_id: UUID,
        client_response_id: UUID,
        response: CalibrationResponseChoice,
        client_timestamp: datetime | None,
        pair_policy_version: str,
    ) -> SyntheticCalibrationResponseRecord: ...
