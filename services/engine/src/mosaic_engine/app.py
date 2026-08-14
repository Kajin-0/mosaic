import logging
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request, Response

from mosaic_engine.config import Settings, get_settings
from mosaic_engine.logging import configure_logging
from mosaic_engine.mock import accept_calibration_response, next_calibration_trial, rank_candidates
from mosaic_engine.models import (
    CalibrationNextRequest,
    CalibrationNextResponse,
    CalibrationResponseReceipt,
    CalibrationResponseRequest,
    HealthResponse,
    MatchRankRequest,
    MatchRankResponse,
    VersionResponse,
)
from mosaic_engine.version import (
    API_VERSION,
    CONTRACT_VERSION,
    ENGINE_VERSION,
    MOCK_CALIBRATION_POLICY_VERSION,
    MOCK_RANKER_MODEL_VERSION,
)

RequestHandler = Callable[[Request], Awaitable[Response]]


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)

    app = FastAPI(
        title="Mosaic Engine API",
        version=CONTRACT_VERSION,
        description=(
            "Server-authoritative Mosaic API boundary. Phase 3 calibration and ranking behavior "
            "is deterministic mock infrastructure, not relationship-science inference."
        ),
        docs_url=None if resolved.environment == "production" else "/docs",
        redoc_url=None if resolved.environment == "production" else "/redoc",
    )
    app.state.settings = resolved

    @app.middleware("http")
    async def request_context(request: Request, call_next: RequestHandler) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        response.headers["x-request-id"] = request_id
        logging.getLogger("mosaic.http").info(
            "request_complete",
            extra={
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.get("/health", response_model=HealthResponse, operation_id="getHealth")
    def health() -> HealthResponse:
        return HealthResponse(service=resolved.service_name)

    @app.get("/version", response_model=VersionResponse, operation_id="getVersion")
    def version() -> VersionResponse:
        return VersionResponse(
            service=resolved.service_name,
            engine_version=ENGINE_VERSION,
            api_version=API_VERSION,
            contract_version=CONTRACT_VERSION,
            calibration_policy_version=MOCK_CALIBRATION_POLICY_VERSION,
            ranker_model_version=MOCK_RANKER_MODEL_VERSION,
        )

    v1 = APIRouter(prefix="/v1")

    @v1.post(
        "/calibration/next",
        response_model=CalibrationNextResponse,
        operation_id="getNextCalibrationTrial",
    )
    def calibration_next(payload: CalibrationNextRequest) -> CalibrationNextResponse:
        return next_calibration_trial(payload)

    @v1.post(
        "/calibration/response",
        response_model=CalibrationResponseReceipt,
        operation_id="submitCalibrationResponse",
    )
    def calibration_response(payload: CalibrationResponseRequest) -> CalibrationResponseReceipt:
        return accept_calibration_response(payload)

    @v1.post(
        "/matches/rank",
        response_model=MatchRankResponse,
        operation_id="rankMatches",
    )
    def matches_rank(payload: MatchRankRequest) -> MatchRankResponse:
        return rank_candidates(payload)

    app.include_router(v1)
    return app
