from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from mosaic_engine.models import CalibrationResponseChoice, CalibrationStimulus


class StoreRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")


class CalibrationSessionRecord(StoreRecord):
    id: UUID
    subject_id: UUID
    instrument_key: str
    instrument_version: str
    policy_version: str
    target_trial_count: int
    status: Literal["active", "complete"]
    created_at: datetime
    completed_at: datetime | None = None


class CalibrationTrialRecord(StoreRecord):
    id: UUID
    session_id: UUID
    subject_id: UUID
    ordinal: int
    stimulus_id: str
    stimulus_version: str
    policy_version: str
    stimulus: CalibrationStimulus
    response_options: list[CalibrationResponseChoice]
    created_at: datetime


class CalibrationResponseRecord(StoreRecord):
    id: UUID
    session_id: UUID
    experiment_id: UUID
    subject_id: UUID
    client_response_id: UUID
    response: CalibrationResponseChoice
    client_timestamp: datetime | None = None
    server_timestamp: datetime
    policy_version: str


class CalibrationStore(Protocol):
    async def get_or_create_subject(self, user_id: UUID) -> UUID: ...

    async def get_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
    ) -> CalibrationSessionRecord | None: ...

    async def get_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> CalibrationSessionRecord | None: ...

    async def create_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
        target_trial_count: int,
    ) -> CalibrationSessionRecord: ...

    async def list_trials(self, session_id: UUID) -> list[CalibrationTrialRecord]: ...

    async def list_responses(self, session_id: UUID) -> list[CalibrationResponseRecord]: ...

    async def create_trial(
        self,
        trial: CalibrationTrialRecord,
    ) -> CalibrationTrialRecord: ...

    async def get_trial(self, experiment_id: UUID) -> CalibrationTrialRecord | None: ...

    async def find_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> CalibrationResponseRecord | None: ...

    async def find_response_by_experiment_id(
        self,
        experiment_id: UUID,
    ) -> CalibrationResponseRecord | None: ...

    async def create_response(
        self,
        subject_id: UUID,
        session_id: UUID,
        experiment_id: UUID,
        client_response_id: UUID,
        response: CalibrationResponseChoice,
        client_timestamp: datetime | None,
        policy_version: str,
    ) -> CalibrationResponseRecord: ...

    async def complete_session(self, session_id: UUID) -> CalibrationSessionRecord: ...
