from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from mosaic_engine.measurement import MeasurementService
from mosaic_engine.measurement_models import MeasurementRatingAnswer, RatingItem
from mosaic_engine.measurement_store import (
    MeasurementPresentationRecord,
    MeasurementResponseRecord,
    MeasurementStore,
)

SESSION_ID = UUID("33333333-3333-4333-8333-333333333333")
SUBJECT_ID = UUID("44444444-4444-4444-8444-444444444444")
PRESENTATION_ID = UUID("55555555-5555-4555-8555-555555555555")
RESPONSE_ID = UUID("66666666-6666-4666-8666-666666666666")
CLIENT_RESPONSE_ID = UUID("77777777-7777-4777-8777-777777777777")


class UnusedStore:
    pass


def make_evidence(
    *,
    prompt: str = "Baseline prompt",
    instrument_version: str = "instrument-1",
    selection_policy_version: str = "selector-1",
) -> tuple[MeasurementPresentationRecord, MeasurementResponseRecord]:
    item = RatingItem(
        prompt=prompt,
        dimension_key="test_dimension",
        min_label="Low",
        max_label="High",
    )
    presentation = MeasurementPresentationRecord(
        id=PRESENTATION_ID,
        session_id=SESSION_ID,
        subject_id=SUBJECT_ID,
        ordinal=1,
        item_id="item-1",
        item_version="item-version-1",
        item_kind="rating",
        selection_policy_version=selection_policy_version,
        item=item,
        created_at=datetime(2026, 8, 14, tzinfo=UTC),
    )
    response = MeasurementResponseRecord(
        id=RESPONSE_ID,
        session_id=SESSION_ID,
        presentation_id=PRESENTATION_ID,
        subject_id=SUBJECT_ID,
        client_response_id=CLIENT_RESPONSE_ID,
        answer=MeasurementRatingAnswer(value=4),
        client_timestamp=datetime(2026, 8, 14, 12, 0, tzinfo=UTC),
        server_timestamp=datetime(2026, 8, 14, 12, 0, 1, tzinfo=UTC),
        instrument_version=instrument_version,
        selection_policy_version=selection_policy_version,
    )
    return presentation, response


def fingerprint(
    service: MeasurementService,
    evidence: tuple[MeasurementPresentationRecord, MeasurementResponseRecord],
) -> str:
    return service._evidence_fingerprint([evidence])


def test_evidence_fingerprint_binds_exact_item_and_provenance() -> None:
    service = MeasurementService(cast(MeasurementStore, UnusedStore()))
    baseline = fingerprint(service, make_evidence())

    changed_prompt = fingerprint(service, make_evidence(prompt="Different authored prompt"))
    changed_instrument = fingerprint(
        service,
        make_evidence(instrument_version="instrument-2"),
    )
    changed_selector = fingerprint(
        service,
        make_evidence(selection_policy_version="selector-2"),
    )

    assert changed_prompt != baseline
    assert changed_instrument != baseline
    assert changed_selector != baseline
