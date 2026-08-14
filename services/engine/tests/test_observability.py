import json
import logging
from io import StringIO
from uuid import UUID

from fastapi.testclient import TestClient

from mosaic_engine.app import create_app
from mosaic_engine.config import Settings
from mosaic_engine.logging import JsonFormatter
from mosaic_engine.observability import (
    pseudonymous_subject_ref,
    request_version_context,
    resolve_request_id,
)
from mosaic_engine.supabase import SupabaseAuthenticationError
from mosaic_engine.version import (
    API_VERSION,
    CONTRACT_VERSION,
    ENGINE_VERSION,
    MOCK_CALIBRATION_POLICY_VERSION,
    MOCK_RANKER_MODEL_VERSION,
)

SUBJECT_ID = UUID("22222222-2222-4222-8222-222222222222")


class StaticSubjectResolver:
    async def resolve_subject(self, access_token: str | None) -> UUID:
        if access_token != "test-access-token":
            raise SupabaseAuthenticationError("bad token")
        return SUBJECT_ID


def _captured_client(*, raise_server_exceptions: bool = True) -> tuple[TestClient, StringIO]:
    app = create_app(
        Settings(environment="test", log_level="INFO"),
        subject_resolver=StaticSubjectResolver(),
    )
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("mosaic")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return TestClient(app, raise_server_exceptions=raise_server_exceptions), stream


def _last_event(stream: StringIO) -> dict[str, object]:
    lines = [line for line in stream.getvalue().splitlines() if line]
    assert lines
    return json.loads(lines[-1])


def test_subject_reference_is_stable_and_does_not_expose_uuid() -> None:
    reference = pseudonymous_subject_ref(SUBJECT_ID)
    assert reference == pseudonymous_subject_ref(SUBJECT_ID)
    assert reference.startswith("subject_")
    assert str(SUBJECT_ID) not in reference
    assert len(reference) == len("subject_") + 16


def test_request_ids_accept_safe_values_and_replace_unsafe_values() -> None:
    assert resolve_request_id("mobile-request_17") == "mobile-request_17"
    replacement = resolve_request_id("contains spaces")
    UUID(replacement)


def test_route_context_includes_global_and_science_versions() -> None:
    calibration = request_version_context("/v1/calibration/next")
    assert calibration == {
        "engine_version": ENGINE_VERSION,
        "api_version": API_VERSION,
        "contract_version": CONTRACT_VERSION,
        "policy_version": MOCK_CALIBRATION_POLICY_VERSION,
    }

    ranking = request_version_context("/v1/matches/rank")
    assert ranking["model_version"] == MOCK_RANKER_MODEL_VERSION
    assert ranking["api_version"] == API_VERSION


def test_authenticated_science_log_is_pseudonymous_and_versioned() -> None:
    client, stream = _captured_client()
    response = client.post(
        "/v1/calibration/next",
        headers={
            "Authorization": "Bearer test-access-token",
            "x-request-id": "calibration-observability-test",
        },
        json={},
    )
    assert response.status_code == 503
    assert response.headers["x-request-id"] == "calibration-observability-test"

    event = _last_event(stream)
    assert event["event"] == "http_request"
    assert event["message"] == "request_complete"
    assert event["request_id"] == "calibration-observability-test"
    assert event["status_code"] == 503
    assert event["subject_ref"] == pseudonymous_subject_ref(SUBJECT_ID)
    assert "subject_id" not in event
    assert event["engine_version"] == ENGINE_VERSION
    assert event["api_version"] == API_VERSION
    assert event["contract_version"] == CONTRACT_VERSION
    assert event["policy_version"] == MOCK_CALIBRATION_POLICY_VERSION
    assert isinstance(event["duration_ms"], int | float)


def test_unhandled_exception_emits_failure_event_before_propagation() -> None:
    app = create_app(Settings(environment="test", log_level="INFO"))

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("synthetic failure")

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("mosaic")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")
    assert response.status_code == 500

    event = _last_event(stream)
    assert event["message"] == "request_failed"
    assert event["status_code"] == 500
    assert event["error_type"] == "RuntimeError"
    assert event["engine_version"] == ENGINE_VERSION
    assert "exception" in event
