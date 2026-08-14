from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from mosaic_engine.app import create_app
from mosaic_engine.calibration import (
    MOCK_CALIBRATION_INSTRUMENT_KEY,
    MOCK_CALIBRATION_INSTRUMENT_VERSION,
    MOCK_CALIBRATION_TARGET_TRIALS,
    CalibrationService,
)
from mosaic_engine.config import Settings
from mosaic_engine.match_service import MatchRankingService
from mosaic_engine.match_store import MatchRankRunRecord
from mosaic_engine.models import CalibrationResponseChoice, RankedCandidate
from mosaic_engine.store import (
    CalibrationResponseRecord,
    CalibrationSessionRecord,
    CalibrationTrialRecord,
)
from mosaic_engine.version import (
    CONTRACT_VERSION,
    ENGINE_VERSION,
    MOCK_CALIBRATION_POLICY_VERSION,
)

SUBJECT_ID = UUID("11111111-1111-4111-8111-111111111111")


class StaticSubjectResolver:
    async def resolve_subject(self, access_token: str | None) -> UUID:
        if access_token != "test-access-token":
            from mosaic_engine.supabase import SupabaseAuthenticationError

            raise SupabaseAuthenticationError("bad token")
        return SUBJECT_ID


class MemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[UUID, CalibrationSessionRecord] = {}
        self.trials: dict[UUID, CalibrationTrialRecord] = {}
        self.responses: dict[UUID, CalibrationResponseRecord] = {}

    async def get_or_create_subject(self, user_id: UUID) -> UUID:
        del user_id
        return SUBJECT_ID

    async def get_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
    ) -> CalibrationSessionRecord | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.subject_id == subject_id
                and session.instrument_key == instrument_key
                and session.instrument_version == instrument_version
                and session.policy_version == policy_version
            ),
            None,
        )

    async def get_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> CalibrationSessionRecord | None:
        session = self.sessions.get(session_id)
        return session if session and session.subject_id == subject_id else None

    async def create_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
        target_trial_count: int,
    ) -> CalibrationSessionRecord:
        session = CalibrationSessionRecord(
            id=uuid4(),
            subject_id=subject_id,
            instrument_key=instrument_key,
            instrument_version=instrument_version,
            policy_version=policy_version,
            target_trial_count=target_trial_count,
            status="active",
            created_at=datetime.now(UTC),
        )
        self.sessions[session.id] = session
        return session

    async def list_trials(self, session_id: UUID) -> list[CalibrationTrialRecord]:
        return sorted(
            [trial for trial in self.trials.values() if trial.session_id == session_id],
            key=lambda trial: trial.ordinal,
        )

    async def list_responses(self, session_id: UUID) -> list[CalibrationResponseRecord]:
        return sorted(
            [response for response in self.responses.values() if response.session_id == session_id],
            key=lambda response: response.server_timestamp,
        )

    async def create_trial(self, trial: CalibrationTrialRecord) -> CalibrationTrialRecord:
        self.trials[trial.id] = trial
        return trial

    async def get_trial(self, experiment_id: UUID) -> CalibrationTrialRecord | None:
        return self.trials.get(experiment_id)

    async def find_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> CalibrationResponseRecord | None:
        return next(
            (
                response
                for response in self.responses.values()
                if response.client_response_id == client_response_id
            ),
            None,
        )

    async def find_response_by_experiment_id(
        self,
        experiment_id: UUID,
    ) -> CalibrationResponseRecord | None:
        return self.responses.get(experiment_id)

    async def create_response(
        self,
        subject_id: UUID,
        session_id: UUID,
        experiment_id: UUID,
        client_response_id: UUID,
        response: CalibrationResponseChoice,
        client_timestamp: datetime | None,
        policy_version: str,
    ) -> CalibrationResponseRecord:
        record = CalibrationResponseRecord(
            id=uuid4(),
            session_id=session_id,
            experiment_id=experiment_id,
            subject_id=subject_id,
            client_response_id=client_response_id,
            response=response,
            client_timestamp=client_timestamp,
            server_timestamp=datetime.now(UTC),
            policy_version=policy_version,
        )
        self.responses[experiment_id] = record
        return record

    async def complete_session(self, session_id: UUID) -> CalibrationSessionRecord:
        session = self.sessions[session_id].model_copy(
            update={"status": "complete", "completed_at": datetime.now(UTC)},
        )
        self.sessions[session_id] = session
        return session


class MemoryMatchStore:
    def __init__(self) -> None:
        self.runs: dict[tuple[UUID, str, str], MatchRankRunRecord] = {}

    async def find_match_rank_run(
        self,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
    ) -> MatchRankRunRecord | None:
        return self.runs.get((subject_id, model_version, request_fingerprint))

    async def create_match_rank_run(
        self,
        *,
        subject_id: UUID,
        model_version: str,
        request_fingerprint: str,
        candidate_ids: list[UUID],
        requested_limit: int,
        ranked_candidates: list[RankedCandidate],
    ) -> MatchRankRunRecord:
        record = MatchRankRunRecord(
            id=uuid4(),
            subject_id=subject_id,
            model_version=model_version,
            request_fingerprint=request_fingerprint,
            candidate_ids=candidate_ids,
            requested_limit=requested_limit,
            ranked_candidates=ranked_candidates,
            created_at=datetime.now(UTC),
        )
        self.runs[(subject_id, model_version, request_fingerprint)] = record
        return record


store = MemoryStore()
match_store = MemoryMatchStore()
client = TestClient(
    create_app(
        Settings(environment="test", log_level="CRITICAL"),
        subject_resolver=StaticSubjectResolver(),
        calibration_service=CalibrationService(store),
        match_ranking_service=MatchRankingService(match_store),
    ),
)
AUTH = {"Authorization": "Bearer test-access-token"}


def test_health_and_version() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "mosaic-engine"}

    version = client.get("/version")
    assert version.status_code == 200
    assert version.json()["engine_version"] == ENGINE_VERSION
    assert version.json()["contract_version"] == CONTRACT_VERSION


def test_calibration_requires_authentication() -> None:
    response = client.post("/v1/calibration/next", json={})
    assert response.status_code == 401


def test_pending_trial_is_server_authoritative_and_stable() -> None:
    first = client.post("/v1/calibration/next", headers=AUTH, json={})
    second = client.post("/v1/calibration/next", headers=AUTH, json={})

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["status"] == "trial"
    assert first.json()["ordinal"] == 1
    assert first.json()["completed_trial_count"] == 0
    assert first.json()["target_trial_count"] == MOCK_CALIBRATION_TARGET_TRIALS
    assert first.json()["policy_version"] == MOCK_CALIBRATION_POLICY_VERSION
    UUID(first.json()["experiment_id"])


def test_ten_trials_are_idempotent_and_complete() -> None:
    for expected_ordinal in range(1, MOCK_CALIBRATION_TARGET_TRIALS + 1):
        next_trial = client.post("/v1/calibration/next", headers=AUTH, json={})
        assert next_trial.status_code == 200
        body = next_trial.json()
        assert body["ordinal"] == expected_ordinal
        assert body["completed_trial_count"] == expected_ordinal - 1

        client_response_id = str(uuid4())
        payload = {
            "session_id": body["session_id"],
            "experiment_id": body["experiment_id"],
            "client_response_id": client_response_id,
            "response": "both",
        }
        accepted = client.post("/v1/calibration/response", headers=AUTH, json=payload)
        assert accepted.status_code == 200
        assert accepted.json()["duplicate"] is False
        assert accepted.json()["completed_trial_count"] == expected_ordinal

        duplicate = client.post("/v1/calibration/response", headers=AUTH, json=payload)
        assert duplicate.status_code == 200
        assert duplicate.json()["duplicate"] is True
        assert duplicate.json()["completed_trial_count"] == expected_ordinal

    complete = client.post("/v1/calibration/next", headers=AUTH, json={})
    assert complete.status_code == 200
    assert complete.json()["status"] == "complete"
    assert complete.json()["completed_trial_count"] == MOCK_CALIBRATION_TARGET_TRIALS
    assert complete.json()["experiment_id"] is None
    assert complete.json()["stimulus"] is None

    session = next(iter(store.sessions.values()))
    assert session.instrument_key == MOCK_CALIBRATION_INSTRUMENT_KEY
    assert session.instrument_version == MOCK_CALIBRATION_INSTRUMENT_VERSION
    assert session.status == "complete"
    assert len(store.trials) == MOCK_CALIBRATION_TARGET_TRIALS
    assert len(store.responses) == MOCK_CALIBRATION_TARGET_TRIALS


def test_match_rank_requires_authentication_and_reuses_persisted_run() -> None:
    payload = {
        "candidate_ids": [
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        ],
        "limit": 2,
    }

    unauthenticated = client.post("/v1/matches/rank", json=payload)
    assert unauthenticated.status_code == 401

    first = client.post("/v1/matches/rank", headers=AUTH, json=payload)
    second = client.post("/v1/matches/rank", headers=AUTH, json=payload)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["persisted"] is True
    assert len(first.json()["request_fingerprint"]) == 64
    UUID(first.json()["run_id"])
    assert len(first.json()["ranked_candidates"]) == 2
    assert len(match_store.runs) == 1
