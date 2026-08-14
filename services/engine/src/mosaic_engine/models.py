from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(ApiModel):
    status: Literal["ok"] = "ok"
    service: str


class VersionResponse(ApiModel):
    service: str
    engine_version: str
    api_version: str
    contract_version: str
    calibration_policy_version: str
    ranker_model_version: str


class CalibrationResponseChoice(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"
    NEITHER = "neither"


class CalibrationNextStatus(StrEnum):
    TRIAL = "trial"
    COMPLETE = "complete"


class CalibrationStimulusOption(ApiModel):
    id: str
    label: str


class CalibrationStimulus(ApiModel):
    kind: Literal["text_pair"] = "text_pair"
    left: CalibrationStimulusOption
    right: CalibrationStimulusOption


class CalibrationNextRequest(ApiModel):
    pass


class CalibrationNextResponse(ApiModel):
    session_id: UUID
    status: CalibrationNextStatus
    completed_trial_count: int = Field(ge=0)
    target_trial_count: int = Field(ge=1)
    policy_version: str
    instrument_version: str
    experiment_id: UUID | None = None
    ordinal: int | None = Field(default=None, ge=1)
    stimulus_id: str | None = None
    stimulus_version: str | None = None
    stimulus: CalibrationStimulus | None = None
    response_options: list[CalibrationResponseChoice] = Field(default_factory=list)
    is_mock: Literal[True] = True


class CalibrationResponseRequest(ApiModel):
    session_id: UUID
    experiment_id: UUID
    client_response_id: UUID
    response: CalibrationResponseChoice
    client_timestamp: datetime | None = None


class CalibrationResponseReceipt(ApiModel):
    accepted: Literal[True] = True
    duplicate: bool
    session_id: UUID
    experiment_id: UUID
    client_response_id: UUID
    policy_version: str
    completed_trial_count: int = Field(ge=1)
    target_trial_count: int = Field(ge=1)
    session_complete: bool
    server_timestamp: datetime
    is_mock: Literal[True] = True


class MatchRankRequest(ApiModel):
    candidate_ids: list[UUID] = Field(min_length=1, max_length=50)
    limit: int = Field(default=10, ge=1, le=50)

    @field_validator("candidate_ids")
    @classmethod
    def candidate_ids_are_unique(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("candidate_ids must be unique")
        return value


class RankedCandidate(ApiModel):
    candidate_id: UUID
    rank: int = Field(ge=1)
    rank_score: float = Field(ge=0.0, le=1.0)


class MatchRankResponse(ApiModel):
    model_version: str
    ranked_candidates: list[RankedCandidate]
    is_mock: Literal[True] = True


class PersistedMatchRankResponse(MatchRankResponse):
    run_id: UUID
    request_fingerprint: str = Field(min_length=64, max_length=64)
    created_at: datetime
    persisted: Literal[True] = True
