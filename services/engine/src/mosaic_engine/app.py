import logging
import time
from collections.abc import Awaitable, Callable
from typing import Annotated, Protocol
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mosaic_engine.calibration import (
    CalibrationConflictError,
    CalibrationNotFoundError,
    CalibrationService,
)
from mosaic_engine.config import Settings, get_settings
from mosaic_engine.logging import configure_logging
from mosaic_engine.measurement import (
    MeasurementConflictError,
    MeasurementNotFoundError,
    MeasurementService,
)
from mosaic_engine.measurement_models import (
    MeasurementNextRequest,
    MeasurementNextResponse,
    MeasurementResponseReceipt,
    MeasurementResponseRequest,
    MeasurementScoreRequest,
    MeasurementScoreResponse,
)
from mosaic_engine.mock import rank_candidates
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
from mosaic_engine.supabase import (
    SupabaseAuthenticationError,
    SupabaseConfigurationError,
    SupabaseGateway,
    SupabasePersistenceError,
)
from mosaic_engine.version import (
    API_VERSION,
    CONTRACT_VERSION,
    ENGINE_VERSION,
    MOCK_CALIBRATION_POLICY_VERSION,
    MOCK_RANKER_MODEL_VERSION,
)

RequestHandler = Callable[[Request], Awaitable[Response]]


class SubjectResolver(Protocol):
    async def resolve_subject(self, access_token: str | None) -> UUID: ...


class SupabaseSubjectResolver:
    def __init__(self, gateway: SupabaseGateway) -> None:
        self._gateway = gateway

    async def resolve_subject(self, access_token: str | None) -> UUID:
        user_id = await self._gateway.authenticate_user(access_token)
        return await self._gateway.get_or_create_subject(user_id)


def create_app(
    settings: Settings | None = None,
    *,
    subject_resolver: SubjectResolver | None = None,
    calibration_service: CalibrationService | None = None,
    measurement_service: MeasurementService | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)

    gateway: SupabaseGateway | None = None
    if subject_resolver is None or calibration_service is None or measurement_service is None:
        try:
            gateway = SupabaseGateway(resolved)
        except SupabaseConfigurationError:
            gateway = None

    if subject_resolver is None and gateway is not None:
        subject_resolver = SupabaseSubjectResolver(gateway)
    if calibration_service is None and gateway is not None:
        calibration_service = CalibrationService(gateway)
    if measurement_service is None and gateway is not None:
        measurement_service = MeasurementService(gateway)

    app = FastAPI(
        title="Mosaic Engine API",
        version=CONTRACT_VERSION,
        description=(
            "Server-authoritative Mosaic API boundary. Phase 4 calibration and Phase 5 "
            "measurement behavior are deterministic persisted infrastructure protocols, not "
            "validated relationship-science inference."
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
        event = {
            "event": "http_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
        subject_id = getattr(request.state, "subject_id", None)
        if subject_id is not None:
            event["subject_id"] = str(subject_id)
        logging.getLogger("mosaic.http").info("request_complete", extra=event)
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

    bearer = HTTPBearer(auto_error=False)

    async def require_subject(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> UUID:
        if subject_resolver is None:
            raise HTTPException(
                status_code=503,
                detail="Authenticated science persistence is not configured.",
            )
        token = (
            credentials.credentials
            if credentials and credentials.scheme.lower() == "bearer"
            else None
        )
        try:
            subject_id = await subject_resolver.resolve_subject(token)
        except SupabaseAuthenticationError as exc:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing access token.",
            ) from exc
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Science persistence is unavailable.",
            ) from exc
        request.state.subject_id = subject_id
        return subject_id

    v1 = APIRouter(prefix="/v1")

    @v1.post(
        "/calibration/next",
        response_model=CalibrationNextResponse,
        operation_id="getNextCalibrationTrial",
    )
    async def calibration_next(
        payload: CalibrationNextRequest,
        subject_id: Annotated[UUID, Depends(require_subject)],
    ) -> CalibrationNextResponse:
        del payload
        if calibration_service is None:
            raise HTTPException(
                status_code=503,
                detail="Calibration persistence is not configured.",
            )
        try:
            return await calibration_service.next_trial(subject_id)
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Calibration persistence is unavailable.",
            ) from exc

    @v1.post(
        "/calibration/response",
        response_model=CalibrationResponseReceipt,
        operation_id="submitCalibrationResponse",
    )
    async def calibration_response(
        payload: CalibrationResponseRequest,
        subject_id: Annotated[UUID, Depends(require_subject)],
    ) -> CalibrationResponseReceipt:
        if calibration_service is None:
            raise HTTPException(
                status_code=503,
                detail="Calibration persistence is not configured.",
            )
        try:
            return await calibration_service.submit_response(subject_id, payload)
        except CalibrationNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except CalibrationConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Calibration persistence is unavailable.",
            ) from exc

    @v1.post(
        "/measurement/next",
        response_model=MeasurementNextResponse,
        operation_id="getNextMeasurementItem",
    )
    async def measurement_next(
        payload: MeasurementNextRequest,
        subject_id: Annotated[UUID, Depends(require_subject)],
    ) -> MeasurementNextResponse:
        del payload
        if measurement_service is None:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is not configured.",
            )
        try:
            return await measurement_service.next_item(subject_id)
        except MeasurementConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is unavailable.",
            ) from exc

    @v1.post(
        "/measurement/response",
        response_model=MeasurementResponseReceipt,
        operation_id="submitMeasurementResponse",
    )
    async def measurement_response(
        payload: MeasurementResponseRequest,
        subject_id: Annotated[UUID, Depends(require_subject)],
    ) -> MeasurementResponseReceipt:
        if measurement_service is None:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is not configured.",
            )
        try:
            return await measurement_service.submit_response(subject_id, payload)
        except MeasurementNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except MeasurementConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is unavailable.",
            ) from exc

    @v1.post(
        "/measurement/score",
        response_model=MeasurementScoreResponse,
        operation_id="scoreMeasurementSession",
    )
    async def measurement_score(
        payload: MeasurementScoreRequest,
        subject_id: Annotated[UUID, Depends(require_subject)],
    ) -> MeasurementScoreResponse:
        if measurement_service is None:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is not configured.",
            )
        try:
            return await measurement_service.score(subject_id, payload)
        except MeasurementNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except MeasurementConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except SupabasePersistenceError as exc:
            raise HTTPException(
                status_code=503,
                detail="Measurement persistence is unavailable.",
            ) from exc

    @v1.post(
        "/matches/rank",
        response_model=MatchRankResponse,
        operation_id="rankMatches",
    )
    def matches_rank(payload: MatchRankRequest) -> MatchRankResponse:
        return rank_candidates(payload)

    app.include_router(v1)
    return app
