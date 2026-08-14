import base64
import hashlib
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from mosaic_engine.app import create_app
from mosaic_engine.config import Settings
from mosaic_engine.models import CalibrationResponseChoice
from mosaic_engine.supabase import SupabaseAuthenticationError
from mosaic_engine.synthetic_calibration import (
    MOCK_SYNTHETIC_TARGET_TRIALS,
    SyntheticCalibrationService,
)
from mosaic_engine.synthetic_models import SyntheticCalibrationResponseRequest
from mosaic_engine.synthetic_store import (
    SyntheticAssetRecord,
    SyntheticCalibrationResponseRecord,
    SyntheticCalibrationSessionRecord,
    SyntheticPairRecord,
    SyntheticQcEventRecord,
    SyntheticStimulusSpecRecord,
)

SUBJECT_ID = UUID("88888888-8888-4888-8888-888888888888")
AUTH = {"Authorization": "Bearer synthetic-access-token"}


class StaticSubjectResolver:
    async def resolve_subject(self, access_token: str | None) -> UUID:
        if access_token != "synthetic-access-token":
            raise SupabaseAuthenticationError("bad token")
        return SUBJECT_ID


class MemorySyntheticStore:
    def __init__(self) -> None:
        self.sessions: dict[UUID, SyntheticCalibrationSessionRecord] = {}
        self.specs: dict[UUID, SyntheticStimulusSpecRecord] = {}
        self.assets: dict[UUID, SyntheticAssetRecord] = {}
        self.qc_events: dict[UUID, SyntheticQcEventRecord] = {}
        self.pairs: dict[UUID, SyntheticPairRecord] = {}
        self.responses: dict[UUID, SyntheticCalibrationResponseRecord] = {}

    async def get_synthetic_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        pair_policy_version: str,
        generator_adapter_version: str,
    ) -> SyntheticCalibrationSessionRecord | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.subject_id == subject_id
                and session.instrument_key == instrument_key
                and session.instrument_version == instrument_version
                and session.pair_policy_version == pair_policy_version
                and session.generator_adapter_version == generator_adapter_version
            ),
            None,
        )

    async def get_synthetic_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord | None:
        session = self.sessions.get(session_id)
        return session if session and session.subject_id == subject_id else None

    async def create_synthetic_session(
        self,
        *,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        pair_policy_version: str,
        generator_adapter_version: str,
        target_trial_count: int,
    ) -> SyntheticCalibrationSessionRecord:
        session = SyntheticCalibrationSessionRecord(
            id=uuid4(),
            subject_id=subject_id,
            instrument_key=instrument_key,
            instrument_version=instrument_version,
            pair_policy_version=pair_policy_version,
            generator_adapter_version=generator_adapter_version,
            target_trial_count=target_trial_count,
            status="active",
            created_at=datetime.now(UTC),
        )
        self.sessions[session.id] = session
        return session

    async def complete_synthetic_session(
        self,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord:
        session = self.sessions[session_id].model_copy(
            update={"status": "complete", "completed_at": datetime.now(UTC)},
        )
        self.sessions[session_id] = session
        return session

    async def list_synthetic_pairs(self, session_id: UUID) -> list[SyntheticPairRecord]:
        return sorted(
            [pair for pair in self.pairs.values() if pair.session_id == session_id],
            key=lambda pair: pair.ordinal,
        )

    async def create_synthetic_spec(
        self,
        record: SyntheticStimulusSpecRecord,
    ) -> SyntheticStimulusSpecRecord:
        self.specs[record.id] = record
        return record

    async def create_synthetic_asset(
        self,
        record: SyntheticAssetRecord,
    ) -> SyntheticAssetRecord:
        self.assets[record.id] = record
        return record

    async def create_synthetic_qc_event(
        self,
        record: SyntheticQcEventRecord,
    ) -> SyntheticQcEventRecord:
        self.qc_events[record.id] = record
        return record

    async def create_synthetic_pair(
        self,
        record: SyntheticPairRecord,
    ) -> SyntheticPairRecord:
        self.pairs[record.id] = record
        return record

    async def get_synthetic_pair(self, pair_id: UUID) -> SyntheticPairRecord | None:
        return self.pairs.get(pair_id)

    async def get_synthetic_asset(self, asset_id: UUID) -> SyntheticAssetRecord | None:
        return self.assets.get(asset_id)

    async def list_synthetic_responses(
        self,
        session_id: UUID,
    ) -> list[SyntheticCalibrationResponseRecord]:
        return sorted(
            [response for response in self.responses.values() if response.session_id == session_id],
            key=lambda response: response.server_timestamp,
        )

    async def find_synthetic_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None:
        return next(
            (
                response
                for response in self.responses.values()
                if response.client_response_id == client_response_id
            ),
            None,
        )

    async def find_synthetic_response_by_pair_id(
        self,
        pair_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None:
        return self.responses.get(pair_id)

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
    ) -> SyntheticCalibrationResponseRecord:
        record = SyntheticCalibrationResponseRecord(
            id=uuid4(),
            session_id=session_id,
            pair_id=pair_id,
            subject_id=subject_id,
            client_response_id=client_response_id,
            response=response,
            client_timestamp=client_timestamp,
            server_timestamp=datetime.now(UTC),
            pair_policy_version=pair_policy_version,
        )
        self.responses[pair_id] = record
        return record


def test_synthetic_cache_is_replayable_and_complete() -> None:
    store = MemorySyntheticStore()
    service = SyntheticCalibrationService(store)

    first = __import__("asyncio").run(service.next_pair(SUBJECT_ID))
    repeated = __import__("asyncio").run(service.next_pair(SUBJECT_ID))

    assert first.status == "pair"
    assert first.cache_ready is True
    assert first.pair is not None
    assert repeated.pair is not None
    assert repeated.pair.pair_id == first.pair.pair_id
    assert len(store.pairs) == MOCK_SYNTHETIC_TARGET_TRIALS
    assert len(store.specs) == MOCK_SYNTHETIC_TARGET_TRIALS * 2
    assert len(store.assets) == MOCK_SYNTHETIC_TARGET_TRIALS * 2
    assert len(store.qc_events) == MOCK_SYNTHETIC_TARGET_TRIALS * 2
    assert {event.decision for event in store.qc_events.values()} == {"accepted"}

    uri = first.pair.left.asset_uri
    prefix = "data:image/svg+xml;base64,"
    assert uri.startswith(prefix)
    raw = base64.b64decode(uri.removeprefix(prefix))
    assert hashlib.sha256(raw).hexdigest() == first.pair.left.content_sha256
    assert first.pair.left.provenance.provider == "mosaic-local-mock"


def test_synthetic_session_completes_with_idempotent_evidence() -> None:
    store = MemorySyntheticStore()
    service = SyntheticCalibrationService(store)
    asyncio = __import__("asyncio")

    first = asyncio.run(service.next_pair(SUBJECT_ID))
    assert first.pair is not None
    client_response_id = uuid4()
    timestamp = datetime(2026, 8, 14, 13, 0, tzinfo=UTC)
    request = SyntheticCalibrationResponseRequest(
        session_id=first.session_id,
        pair_id=first.pair.pair_id,
        client_response_id=client_response_id,
        response=CalibrationResponseChoice.LEFT,
        client_timestamp=timestamp,
    )
    accepted = asyncio.run(service.submit_response(SUBJECT_ID, request))
    duplicate = asyncio.run(service.submit_response(SUBJECT_ID, request))
    assert accepted.duplicate is False
    assert duplicate.duplicate is True
    assert len(store.responses) == 1

    for _ in range(1, MOCK_SYNTHETIC_TARGET_TRIALS):
        next_pair = asyncio.run(service.next_pair(SUBJECT_ID))
        assert next_pair.pair is not None
        asyncio.run(
            service.submit_response(
                SUBJECT_ID,
                SyntheticCalibrationResponseRequest(
                    session_id=next_pair.session_id,
                    pair_id=next_pair.pair.pair_id,
                    client_response_id=uuid4(),
                    response=CalibrationResponseChoice.BOTH,
                    client_timestamp=datetime.now(UTC),
                ),
            ),
        )

    complete = asyncio.run(service.next_pair(SUBJECT_ID))
    assert complete.status == "complete"
    assert complete.completed_trial_count == MOCK_SYNTHETIC_TARGET_TRIALS
    assert len(store.responses) == MOCK_SYNTHETIC_TARGET_TRIALS


def test_synthetic_api_requires_authentication_and_returns_pair() -> None:
    store = MemorySyntheticStore()
    app = create_app(
        Settings(environment="test"),
        subject_resolver=StaticSubjectResolver(),
        synthetic_calibration_service=SyntheticCalibrationService(store),
    )
    client = TestClient(app)

    unauthorized = client.post("/v1/synthetic-calibration/next", json={})
    assert unauthorized.status_code == 401

    response = client.post("/v1/synthetic-calibration/next", json={}, headers=AUTH)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pair"
    assert payload["cache_ready"] is True
    assert payload["target_trial_count"] == MOCK_SYNTHETIC_TARGET_TRIALS
    assert payload["pair"]["left"]["content_sha256"]
    assert payload["pair"]["right"]["provenance"]["adapter_key"] == "deterministic-svg"
