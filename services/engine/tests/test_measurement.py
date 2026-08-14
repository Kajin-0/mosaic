from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from mosaic_engine.app import create_app
from mosaic_engine.config import Settings
from mosaic_engine.measurement import (
    MOCK_MEASUREMENT_INSTRUMENT_KEY,
    MOCK_MEASUREMENT_INSTRUMENT_VERSION,
    MOCK_MEASUREMENT_TARGET_ITEMS,
    MeasurementService,
)
from mosaic_engine.measurement_models import MeasurementAnswer
from mosaic_engine.measurement_store import (
    MeasurementPresentationRecord,
    MeasurementResponseRecord,
    MeasurementScoreRunRecord,
    MeasurementSessionRecord,
)
from mosaic_engine.supabase import SupabaseAuthenticationError
from mosaic_engine.version import MOCK_MEASUREMENT_SELECTION_POLICY_VERSION

SUBJECT_ID = UUID("22222222-2222-4222-8222-222222222222")
AUTH = {"Authorization": "Bearer measurement-access-token"}


class StaticSubjectResolver:
    async def resolve_subject(self, access_token: str | None) -> UUID:
        if access_token != "measurement-access-token":
            raise SupabaseAuthenticationError("bad token")
        return SUBJECT_ID


class MemoryMeasurementStore:
    def __init__(self) -> None:
        self.sessions: dict[UUID, MeasurementSessionRecord] = {}
        self.presentations: dict[UUID, MeasurementPresentationRecord] = {}
        self.responses: dict[UUID, MeasurementResponseRecord] = {}
        self.score_runs: dict[UUID, MeasurementScoreRunRecord] = {}

    async def get_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
    ) -> MeasurementSessionRecord | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.subject_id == subject_id
                and session.instrument_key == instrument_key
                and session.instrument_version == instrument_version
                and session.selection_policy_version == selection_policy_version
            ),
            None,
        )

    async def get_measurement_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> MeasurementSessionRecord | None:
        session = self.sessions.get(session_id)
        return session if session and session.subject_id == subject_id else None

    async def create_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
        target_item_count: int,
    ) -> MeasurementSessionRecord:
        session = MeasurementSessionRecord(
            id=uuid4(),
            subject_id=subject_id,
            instrument_key=instrument_key,
            instrument_version=instrument_version,
            selection_policy_version=selection_policy_version,
            target_item_count=target_item_count,
            status="active",
            created_at=datetime.now(UTC),
        )
        self.sessions[session.id] = session
        return session

    async def list_measurement_presentations(
        self,
        session_id: UUID,
    ) -> list[MeasurementPresentationRecord]:
        return sorted(
            [item for item in self.presentations.values() if item.session_id == session_id],
            key=lambda item: item.ordinal,
        )

    async def list_measurement_responses(
        self,
        session_id: UUID,
    ) -> list[MeasurementResponseRecord]:
        return sorted(
            [item for item in self.responses.values() if item.session_id == session_id],
            key=lambda item: item.server_timestamp,
        )

    async def create_measurement_presentation(
        self,
        presentation: MeasurementPresentationRecord,
    ) -> MeasurementPresentationRecord:
        self.presentations[presentation.id] = presentation
        return presentation

    async def get_measurement_presentation(
        self,
        presentation_id: UUID,
    ) -> MeasurementPresentationRecord | None:
        return self.presentations.get(presentation_id)

    async def find_measurement_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> MeasurementResponseRecord | None:
        return next(
            (
                response
                for response in self.responses.values()
                if response.client_response_id == client_response_id
            ),
            None,
        )

    async def find_measurement_response_by_presentation_id(
        self,
        presentation_id: UUID,
    ) -> MeasurementResponseRecord | None:
        return self.responses.get(presentation_id)

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
    ) -> MeasurementResponseRecord:
        record = MeasurementResponseRecord(
            id=uuid4(),
            session_id=session_id,
            presentation_id=presentation_id,
            subject_id=subject_id,
            client_response_id=client_response_id,
            answer=answer,
            client_timestamp=client_timestamp,
            server_timestamp=datetime.now(UTC),
            instrument_version=instrument_version,
            selection_policy_version=selection_policy_version,
        )
        self.responses[presentation_id] = record
        return record

    async def complete_measurement_session(
        self,
        session_id: UUID,
    ) -> MeasurementSessionRecord:
        session = self.sessions[session_id].model_copy(
            update={"status": "complete", "completed_at": datetime.now(UTC)},
        )
        self.sessions[session_id] = session
        return session

    async def find_measurement_score_run(
        self,
        session_id: UUID,
        scoring_version: str,
        evidence_fingerprint: str,
    ) -> MeasurementScoreRunRecord | None:
        return next(
            (
                run
                for run in self.score_runs.values()
                if run.session_id == session_id
                and run.scoring_version == scoring_version
                and run.evidence_fingerprint == evidence_fingerprint
            ),
            None,
        )

    async def create_measurement_score_run(
        self,
        *,
        session_id: UUID,
        subject_id: UUID,
        scoring_version: str,
        evidence_fingerprint: str,
        response_count: int,
        scores: dict[str, float],
    ) -> MeasurementScoreRunRecord:
        run = MeasurementScoreRunRecord(
            id=uuid4(),
            session_id=session_id,
            subject_id=subject_id,
            scoring_version=scoring_version,
            evidence_fingerprint=evidence_fingerprint,
            response_count=response_count,
            scores=scores,
            created_at=datetime.now(UTC),
        )
        self.score_runs[run.id] = run
        return run


def make_client(store: MemoryMeasurementStore) -> TestClient:
    return TestClient(
        create_app(
            Settings(environment="test", log_level="CRITICAL"),
            subject_resolver=StaticSubjectResolver(),
            measurement_service=MeasurementService(store),
        ),
    )


def answer_for(body: dict[str, object], ordinal: int) -> dict[str, object]:
    item = body["item"]
    assert isinstance(item, dict)
    kind = item["kind"]
    if kind == "rating":
        return {"kind": "rating", "value": ((ordinal - 1) % 5) + 1}
    if kind == "forced_choice":
        side = "left" if ordinal % 2 else "right"
        option = item[side]
        assert isinstance(option, dict)
        return {"kind": "choice", "option_id": option["id"]}
    options = item["options"]
    assert isinstance(options, list)
    option = options[(ordinal - 1) % len(options)]
    assert isinstance(option, dict)
    return {"kind": "choice", "option_id": option["id"]}


def test_measurement_requires_authentication() -> None:
    store = MemoryMeasurementStore()
    client = make_client(store)
    response = client.post("/v1/measurement/next", json={})
    assert response.status_code == 401


def test_measurement_is_resumable_idempotent_and_rescorable() -> None:
    store = MemoryMeasurementStore()
    client = make_client(store)
    kinds: list[str] = []
    session_id: str | None = None

    for ordinal in range(1, MOCK_MEASUREMENT_TARGET_ITEMS + 1):
        next_item = client.post("/v1/measurement/next", headers=AUTH, json={})
        assert next_item.status_code == 200
        body = next_item.json()
        assert body["status"] == "item"
        assert body["ordinal"] == ordinal
        assert body["completed_item_count"] == ordinal - 1
        assert body["target_item_count"] == MOCK_MEASUREMENT_TARGET_ITEMS
        assert body["instrument_key"] == MOCK_MEASUREMENT_INSTRUMENT_KEY
        assert body["instrument_version"] == MOCK_MEASUREMENT_INSTRUMENT_VERSION
        assert body["selection_policy_version"] == MOCK_MEASUREMENT_SELECTION_POLICY_VERSION
        session_id = session_id or body["session_id"]
        assert body["session_id"] == session_id
        kinds.append(body["item"]["kind"])

        repeated = client.post("/v1/measurement/next", headers=AUTH, json={})
        assert repeated.status_code == 200
        assert repeated.json()["presentation_id"] == body["presentation_id"]

        request = {
            "session_id": session_id,
            "presentation_id": body["presentation_id"],
            "client_response_id": str(uuid4()),
            "answer": answer_for(body, ordinal),
            "client_timestamp": datetime.now(UTC).isoformat(),
        }
        accepted = client.post("/v1/measurement/response", headers=AUTH, json=request)
        assert accepted.status_code == 200
        assert accepted.json()["duplicate"] is False
        assert accepted.json()["completed_item_count"] == ordinal

        duplicate = client.post("/v1/measurement/response", headers=AUTH, json=request)
        assert duplicate.status_code == 200
        assert duplicate.json()["duplicate"] is True

        if ordinal == 10:
            client = make_client(store)
            resumed = client.post("/v1/measurement/next", headers=AUTH, json={})
            assert resumed.status_code == 200
            assert resumed.json()["session_id"] == session_id
            assert resumed.json()["ordinal"] == 11
            assert resumed.json()["completed_item_count"] == 10

    assert set(kinds) == {"hard_constraint", "rating", "scenario", "forced_choice"}
    assert {kind: kinds.count(kind) for kind in set(kinds)} == {
        "hard_constraint": 5,
        "rating": 5,
        "scenario": 5,
        "forced_choice": 5,
    }

    complete = client.post("/v1/measurement/next", headers=AUTH, json={})
    assert complete.status_code == 200
    assert complete.json()["status"] == "complete"
    assert complete.json()["completed_item_count"] == 20
    assert complete.json()["presentation_id"] is None
    assert complete.json()["item"] is None

    raw_before = [
        response.model_dump(mode="json")
        for response in awaitable_result(store.list_measurement_responses(UUID(session_id)))
    ]

    v1 = client.post(
        "/v1/measurement/score",
        headers=AUTH,
        json={"session_id": session_id, "scoring_version": "mock-measurement-p5-score-1.0.0"},
    )
    v2 = client.post(
        "/v1/measurement/score",
        headers=AUTH,
        json={"session_id": session_id, "scoring_version": "mock-measurement-p5-score-2.0.0"},
    )
    assert v1.status_code == 200
    assert v2.status_code == 200
    assert v1.json()["response_count"] == 20
    assert v2.json()["response_count"] == 20
    assert v1.json()["evidence_fingerprint"] == v2.json()["evidence_fingerprint"]
    assert v1.json()["score_run_id"] != v2.json()["score_run_id"]
    assert v1.json()["scores"] != v2.json()["scores"]

    raw_after = [
        response.model_dump(mode="json")
        for response in awaitable_result(store.list_measurement_responses(UUID(session_id)))
    ]
    assert raw_after == raw_before
    assert len(store.score_runs) == 2


def awaitable_result(awaitable):
    import asyncio

    return asyncio.run(awaitable)
