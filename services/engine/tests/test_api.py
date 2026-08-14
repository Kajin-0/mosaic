from uuid import UUID

from fastapi.testclient import TestClient

from mosaic_engine.app import create_app
from mosaic_engine.config import Settings
from mosaic_engine.version import CONTRACT_VERSION, ENGINE_VERSION

client = TestClient(create_app(Settings(environment="test", log_level="CRITICAL")))
SESSION_ID = "11111111-1111-4111-8111-111111111111"


def test_health_and_version() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "mosaic-engine"}

    version = client.get("/version")
    assert version.status_code == 200
    assert version.json()["engine_version"] == ENGINE_VERSION
    assert version.json()["contract_version"] == CONTRACT_VERSION


def test_calibration_next_is_deterministic() -> None:
    payload = {"session_id": SESSION_ID, "completed_trial_count": 3}
    first = client.post("/v1/calibration/next", json=payload)
    second = client.post("/v1/calibration/next", json=payload)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["ordinal"] == 4
    assert first.json()["is_mock"] is True
    UUID(first.json()["experiment_id"])


def test_calibration_response_returns_mock_receipt() -> None:
    next_trial = client.post(
        "/v1/calibration/next",
        json={"session_id": SESSION_ID, "completed_trial_count": 0},
    ).json()
    payload = {
        "session_id": SESSION_ID,
        "experiment_id": next_trial["experiment_id"],
        "client_response_id": "22222222-2222-4222-8222-222222222222",
        "response": "both",
    }

    response = client.post("/v1/calibration/response", json=payload)
    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["duplicate"] is False
    assert response.json()["is_mock"] is True


def test_match_rank_is_deterministic_and_limited() -> None:
    payload = {
        "candidate_ids": [
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        ],
        "limit": 2,
    }

    first = client.post("/v1/matches/rank", json=payload)
    second = client.post("/v1/matches/rank", json=payload)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["is_mock"] is True
    assert len(first.json()["ranked_candidates"]) == 2
    assert [item["rank"] for item in first.json()["ranked_candidates"]] == [1, 2]


def test_duplicate_candidate_ids_are_rejected() -> None:
    candidate = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    response = client.post(
        "/v1/matches/rank",
        json={"candidate_ids": [candidate, candidate], "limit": 2},
    )
    assert response.status_code == 422
