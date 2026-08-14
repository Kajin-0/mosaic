from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import Field

from mosaic_engine.models import ApiModel, CalibrationResponseChoice


class SyntheticCalibrationNextStatus(StrEnum):
    PAIR = "pair"
    COMPLETE = "complete"


class SyntheticStimulusSpecification(ApiModel):
    spec_version: str
    candidate_key: str
    seed: int = Field(ge=0)
    control_vector: dict[str, float]
    prompt_template: str


class SyntheticGenerationProvenance(ApiModel):
    adapter_key: str
    adapter_version: str
    provider: str
    model: str
    model_revision: str
    seed: int = Field(ge=0)
    prompt: str
    parameters: dict[str, str | int | float | bool]


class SyntheticAsset(ApiModel):
    asset_id: UUID
    specification_id: UUID
    media_type: str
    content_sha256: str = Field(min_length=64, max_length=64)
    asset_uri: str
    provenance: SyntheticGenerationProvenance


class SyntheticCalibrationPair(ApiModel):
    pair_id: UUID
    ordinal: int = Field(ge=1)
    left: SyntheticAsset
    right: SyntheticAsset
    randomization_seed: int = Field(ge=0)
    pair_policy_version: str


class SyntheticCalibrationNextRequest(ApiModel):
    pass


class SyntheticCalibrationNextResponse(ApiModel):
    session_id: UUID
    status: SyntheticCalibrationNextStatus
    completed_trial_count: int = Field(ge=0)
    target_trial_count: int = Field(ge=1)
    instrument_version: str
    pair_policy_version: str
    generator_adapter_version: str
    pair: SyntheticCalibrationPair | None = None
    response_options: list[CalibrationResponseChoice] = Field(default_factory=list)
    cache_ready: bool
    is_mock: Literal[True] = True


class SyntheticCalibrationResponseRequest(ApiModel):
    session_id: UUID
    pair_id: UUID
    client_response_id: UUID
    response: CalibrationResponseChoice
    client_timestamp: datetime | None = None


class SyntheticCalibrationResponseReceipt(ApiModel):
    accepted: Literal[True] = True
    duplicate: bool
    session_id: UUID
    pair_id: UUID
    client_response_id: UUID
    pair_policy_version: str
    completed_trial_count: int = Field(ge=1)
    target_trial_count: int = Field(ge=1)
    session_complete: bool
    server_timestamp: datetime
    is_mock: Literal[True] = True
