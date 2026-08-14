from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MeasurementApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MeasurementNextStatus(StrEnum):
    ITEM = "item"
    COMPLETE = "complete"


class MeasurementChoiceOption(MeasurementApiModel):
    id: str
    label: str


class HardConstraintItem(MeasurementApiModel):
    kind: Literal["hard_constraint"] = "hard_constraint"
    prompt: str
    dimension_key: str
    options: list[MeasurementChoiceOption] = Field(min_length=2, max_length=6)


class RatingItem(MeasurementApiModel):
    kind: Literal["rating"] = "rating"
    prompt: str
    dimension_key: str
    scale_min: int = Field(default=1, ge=1)
    scale_max: int = Field(default=5, ge=2)
    min_label: str
    max_label: str


class ScenarioItem(MeasurementApiModel):
    kind: Literal["scenario"] = "scenario"
    prompt: str
    dimension_key: str
    options: list[MeasurementChoiceOption] = Field(min_length=2, max_length=6)


class ForcedChoiceItem(MeasurementApiModel):
    kind: Literal["forced_choice"] = "forced_choice"
    prompt: str
    dimension_key: str
    left: MeasurementChoiceOption
    right: MeasurementChoiceOption


MeasurementItem = Annotated[
    HardConstraintItem | RatingItem | ScenarioItem | ForcedChoiceItem,
    Field(discriminator="kind"),
]


class MeasurementChoiceAnswer(MeasurementApiModel):
    kind: Literal["choice"] = "choice"
    option_id: str


class MeasurementRatingAnswer(MeasurementApiModel):
    kind: Literal["rating"] = "rating"
    value: int = Field(ge=1, le=5)


MeasurementAnswer = Annotated[
    MeasurementChoiceAnswer | MeasurementRatingAnswer,
    Field(discriminator="kind"),
]


class MeasurementNextRequest(MeasurementApiModel):
    pass


class MeasurementNextResponse(MeasurementApiModel):
    session_id: UUID
    status: MeasurementNextStatus
    completed_item_count: int = Field(ge=0)
    target_item_count: int = Field(ge=1)
    instrument_key: str
    instrument_version: str
    selection_policy_version: str
    presentation_id: UUID | None = None
    ordinal: int | None = Field(default=None, ge=1)
    item_id: str | None = None
    item_version: str | None = None
    item: MeasurementItem | None = None
    is_mock: Literal[True] = True


class MeasurementResponseRequest(MeasurementApiModel):
    session_id: UUID
    presentation_id: UUID
    client_response_id: UUID
    answer: MeasurementAnswer
    client_timestamp: datetime | None = None


class MeasurementResponseReceipt(MeasurementApiModel):
    accepted: Literal[True] = True
    duplicate: bool
    session_id: UUID
    presentation_id: UUID
    client_response_id: UUID
    instrument_version: str
    selection_policy_version: str
    completed_item_count: int = Field(ge=1)
    target_item_count: int = Field(ge=1)
    session_complete: bool
    server_timestamp: datetime
    is_mock: Literal[True] = True


class MeasurementScoringVersion(StrEnum):
    V1 = "mock-measurement-p5-score-1.0.0"
    V2 = "mock-measurement-p5-score-2.0.0"


class MeasurementScoreRequest(MeasurementApiModel):
    session_id: UUID
    scoring_version: MeasurementScoringVersion


class MeasurementScoreResponse(MeasurementApiModel):
    score_run_id: UUID
    session_id: UUID
    scoring_version: MeasurementScoringVersion
    evidence_fingerprint: str = Field(min_length=64, max_length=64)
    response_count: int = Field(ge=0)
    scores: dict[str, float]
    created_at: datetime
    is_mock: Literal[True] = True
