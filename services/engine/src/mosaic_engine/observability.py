import hashlib
import re
from uuid import UUID, uuid4

from mosaic_engine.version import (
    API_VERSION,
    CONTRACT_VERSION,
    ENGINE_VERSION,
    MOCK_CALIBRATION_POLICY_VERSION,
    MOCK_MEASUREMENT_SELECTION_POLICY_VERSION,
    MOCK_RANKER_MODEL_VERSION,
    MOCK_SYNTHETIC_PAIR_POLICY_VERSION,
)

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def resolve_request_id(value: str | None) -> str:
    if value is not None and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return str(uuid4())


def pseudonymous_subject_ref(subject_id: UUID) -> str:
    digest = hashlib.sha256(subject_id.bytes).hexdigest()[:16]
    return f"subject_{digest}"


def request_version_context(path: str) -> dict[str, str]:
    context = {
        "engine_version": ENGINE_VERSION,
        "api_version": API_VERSION,
        "contract_version": CONTRACT_VERSION,
    }
    if path.startswith("/v1/calibration/"):
        context["policy_version"] = MOCK_CALIBRATION_POLICY_VERSION
    elif path.startswith("/v1/measurement/"):
        context["policy_version"] = MOCK_MEASUREMENT_SELECTION_POLICY_VERSION
    elif path.startswith("/v1/synthetic-calibration/"):
        context["policy_version"] = MOCK_SYNTHETIC_PAIR_POLICY_VERSION
    elif path == "/v1/matches/rank":
        context["model_version"] = MOCK_RANKER_MODEL_VERSION
    return context
