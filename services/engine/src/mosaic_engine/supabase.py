from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from mosaic_engine.config import Settings
from mosaic_engine.measurement_models import MeasurementAnswer
from mosaic_engine.measurement_store import (
    MeasurementPresentationRecord,
    MeasurementResponseRecord,
    MeasurementScoreRunRecord,
    MeasurementSessionRecord,
)
from mosaic_engine.models import CalibrationResponseChoice
from mosaic_engine.store import (
    CalibrationResponseRecord,
    CalibrationSessionRecord,
    CalibrationTrialRecord,
)


class SupabaseConfigurationError(RuntimeError):
    pass


class SupabaseAuthenticationError(RuntimeError):
    pass


class SupabasePersistenceError(RuntimeError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class SupabaseConflictError(SupabasePersistenceError):
    pass


class SupabaseGateway:
    def __init__(self, settings: Settings) -> None:
        if not settings.supabase_url:
            raise SupabaseConfigurationError("MOSAIC_ENGINE_SUPABASE_URL is required.")
        if not settings.supabase_public_key:
            raise SupabaseConfigurationError("MOSAIC_ENGINE_SUPABASE_PUBLIC_KEY is required.")
        if not settings.supabase_server_key:
            raise SupabaseConfigurationError("MOSAIC_ENGINE_SUPABASE_SERVER_KEY is required.")

        self._url = settings.supabase_url.rstrip("/")
        self._public_key = settings.supabase_public_key.get_secret_value()
        self._server_key = settings.supabase_server_key.get_secret_value()
        self._timeout = settings.supabase_timeout_seconds

    async def authenticate_user(self, access_token: str | None) -> UUID:
        if not access_token:
            raise SupabaseAuthenticationError("Missing bearer token.")

        async with httpx.AsyncClient(base_url=self._url, timeout=self._timeout) as client:
            response = await client.get(
                "/auth/v1/user",
                headers={
                    "apikey": self._public_key,
                    "Authorization": f"Bearer {access_token}",
                },
            )

        if response.status_code != 200:
            raise SupabaseAuthenticationError("Invalid or expired Supabase access token.")

        try:
            return UUID(response.json()["id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SupabaseAuthenticationError(
                "Supabase user payload did not contain a valid id.",
            ) from exc

    def _service_headers(self, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self._server_key,
            "Authorization": f"Bearer {self._server_key}",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    async def _service_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        prefer: str | None = None,
        expected: set[int] | None = None,
    ) -> Any:
        expected_statuses = expected or {200}
        async with httpx.AsyncClient(base_url=self._url, timeout=self._timeout) as client:
            response = await client.request(
                method,
                path,
                params=params,
                json=json,
                headers=self._service_headers(prefer),
            )

        if response.status_code not in expected_statuses:
            message = response.text or (
                f"Supabase request failed with HTTP {response.status_code}."
            )
            error_type = (
                SupabaseConflictError if response.status_code == 409 else SupabasePersistenceError
            )
            raise error_type(response.status_code, message)

        if not response.content:
            return None
        return response.json()

    async def get_or_create_subject(self, user_id: UUID) -> UUID:
        subject = await self._find_subject(user_id)
        if subject:
            return UUID(subject["subject_id"])

        try:
            rows = await self._service_request(
                "POST",
                "/rest/v1/science_subjects",
                json={"user_id": str(user_id)},
                prefer="return=representation",
                expected={201},
            )
            return UUID(rows[0]["subject_id"])
        except SupabaseConflictError:
            raced = await self._find_subject(user_id)
            if not raced:
                raise
            return UUID(raced["subject_id"])

    async def _find_subject(self, user_id: UUID) -> dict[str, Any] | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/science_subjects",
            params={
                "select": "subject_id,user_id",
                "user_id": f"eq.{user_id}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    async def get_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
    ) -> CalibrationSessionRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_sessions",
            params={
                "select": "*",
                "subject_id": f"eq.{subject_id}",
                "instrument_key": f"eq.{instrument_key}",
                "instrument_version": f"eq.{instrument_version}",
                "policy_version": f"eq.{policy_version}",
                "limit": "1",
            },
        )
        return CalibrationSessionRecord.model_validate(rows[0]) if rows else None

    async def get_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> CalibrationSessionRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_sessions",
            params={
                "select": "*",
                "id": f"eq.{session_id}",
                "subject_id": f"eq.{subject_id}",
                "limit": "1",
            },
        )
        return CalibrationSessionRecord.model_validate(rows[0]) if rows else None

    async def create_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        policy_version: str,
        target_trial_count: int,
    ) -> CalibrationSessionRecord:
        rows = await self._service_request(
            "POST",
            "/rest/v1/calibration_sessions",
            json={
                "subject_id": str(subject_id),
                "instrument_key": instrument_key,
                "instrument_version": instrument_version,
                "policy_version": policy_version,
                "target_trial_count": target_trial_count,
            },
            prefer="return=representation",
            expected={201},
        )
        return CalibrationSessionRecord.model_validate(rows[0])

    async def list_trials(self, session_id: UUID) -> list[CalibrationTrialRecord]:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_trials",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "ordinal.asc",
            },
        )
        return [CalibrationTrialRecord.model_validate(row) for row in rows]

    async def list_responses(self, session_id: UUID) -> list[CalibrationResponseRecord]:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_responses",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "server_timestamp.asc",
            },
        )
        return [CalibrationResponseRecord.model_validate(row) for row in rows]

    async def create_trial(self, trial: CalibrationTrialRecord) -> CalibrationTrialRecord:
        rows = await self._service_request(
            "POST",
            "/rest/v1/calibration_trials",
            json={
                "id": str(trial.id),
                "session_id": str(trial.session_id),
                "subject_id": str(trial.subject_id),
                "ordinal": trial.ordinal,
                "stimulus_id": trial.stimulus_id,
                "stimulus_version": trial.stimulus_version,
                "policy_version": trial.policy_version,
                "stimulus": trial.stimulus.model_dump(mode="json"),
                "response_options": [choice.value for choice in trial.response_options],
            },
            prefer="return=representation",
            expected={201},
        )
        return CalibrationTrialRecord.model_validate(rows[0])

    async def get_trial(self, experiment_id: UUID) -> CalibrationTrialRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_trials",
            params={"select": "*", "id": f"eq.{experiment_id}", "limit": "1"},
        )
        return CalibrationTrialRecord.model_validate(rows[0]) if rows else None

    async def find_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> CalibrationResponseRecord | None:
        return await self._find_response("client_response_id", client_response_id)

    async def find_response_by_experiment_id(
        self,
        experiment_id: UUID,
    ) -> CalibrationResponseRecord | None:
        return await self._find_response("experiment_id", experiment_id)

    async def _find_response(
        self,
        field: str,
        value: UUID,
    ) -> CalibrationResponseRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/calibration_responses",
            params={"select": "*", field: f"eq.{value}", "limit": "1"},
        )
        return CalibrationResponseRecord.model_validate(rows[0]) if rows else None

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
        body: dict[str, Any] = {
            "subject_id": str(subject_id),
            "session_id": str(session_id),
            "experiment_id": str(experiment_id),
            "client_response_id": str(client_response_id),
            "response": response.value,
            "policy_version": policy_version,
        }
        if client_timestamp is not None:
            body["client_timestamp"] = client_timestamp.isoformat()

        rows = await self._service_request(
            "POST",
            "/rest/v1/calibration_responses",
            json=body,
            prefer="return=representation",
            expected={201},
        )
        return CalibrationResponseRecord.model_validate(rows[0])

    async def complete_session(self, session_id: UUID) -> CalibrationSessionRecord:
        rows = await self._service_request(
            "PATCH",
            "/rest/v1/calibration_sessions",
            params={"id": f"eq.{session_id}"},
            json={
                "status": "complete",
                "completed_at": datetime.now(UTC).isoformat(),
            },
            prefer="return=representation",
        )
        if not rows:
            raise SupabasePersistenceError(
                404,
                "Calibration session disappeared during completion.",
            )
        return CalibrationSessionRecord.model_validate(rows[0])

    async def get_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
    ) -> MeasurementSessionRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_sessions",
            params={
                "select": "*",
                "subject_id": f"eq.{subject_id}",
                "instrument_key": f"eq.{instrument_key}",
                "instrument_version": f"eq.{instrument_version}",
                "selection_policy_version": f"eq.{selection_policy_version}",
                "limit": "1",
            },
        )
        return MeasurementSessionRecord.model_validate(rows[0]) if rows else None

    async def get_measurement_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> MeasurementSessionRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_sessions",
            params={
                "select": "*",
                "id": f"eq.{session_id}",
                "subject_id": f"eq.{subject_id}",
                "limit": "1",
            },
        )
        return MeasurementSessionRecord.model_validate(rows[0]) if rows else None

    async def create_measurement_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        selection_policy_version: str,
        target_item_count: int,
    ) -> MeasurementSessionRecord:
        rows = await self._service_request(
            "POST",
            "/rest/v1/measurement_sessions",
            json={
                "subject_id": str(subject_id),
                "instrument_key": instrument_key,
                "instrument_version": instrument_version,
                "selection_policy_version": selection_policy_version,
                "target_item_count": target_item_count,
            },
            prefer="return=representation",
            expected={201},
        )
        return MeasurementSessionRecord.model_validate(rows[0])

    async def list_measurement_presentations(
        self,
        session_id: UUID,
    ) -> list[MeasurementPresentationRecord]:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_presentations",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "ordinal.asc",
            },
        )
        return [MeasurementPresentationRecord.model_validate(row) for row in rows]

    async def list_measurement_responses(
        self,
        session_id: UUID,
    ) -> list[MeasurementResponseRecord]:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_responses",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "server_timestamp.asc",
            },
        )
        return [MeasurementResponseRecord.model_validate(row) for row in rows]

    async def create_measurement_presentation(
        self,
        presentation: MeasurementPresentationRecord,
    ) -> MeasurementPresentationRecord:
        rows = await self._service_request(
            "POST",
            "/rest/v1/measurement_presentations",
            json={
                "id": str(presentation.id),
                "session_id": str(presentation.session_id),
                "subject_id": str(presentation.subject_id),
                "ordinal": presentation.ordinal,
                "item_id": presentation.item_id,
                "item_version": presentation.item_version,
                "item_kind": presentation.item_kind,
                "selection_policy_version": presentation.selection_policy_version,
                "item": presentation.item.model_dump(mode="json"),
            },
            prefer="return=representation",
            expected={201},
        )
        return MeasurementPresentationRecord.model_validate(rows[0])

    async def get_measurement_presentation(
        self,
        presentation_id: UUID,
    ) -> MeasurementPresentationRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_presentations",
            params={"select": "*", "id": f"eq.{presentation_id}", "limit": "1"},
        )
        return MeasurementPresentationRecord.model_validate(rows[0]) if rows else None

    async def find_measurement_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> MeasurementResponseRecord | None:
        return await self._find_measurement_response("client_response_id", client_response_id)

    async def find_measurement_response_by_presentation_id(
        self,
        presentation_id: UUID,
    ) -> MeasurementResponseRecord | None:
        return await self._find_measurement_response("presentation_id", presentation_id)

    async def _find_measurement_response(
        self,
        field: str,
        value: UUID,
    ) -> MeasurementResponseRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_responses",
            params={"select": "*", field: f"eq.{value}", "limit": "1"},
        )
        return MeasurementResponseRecord.model_validate(rows[0]) if rows else None

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
        body: dict[str, Any] = {
            "subject_id": str(subject_id),
            "session_id": str(session_id),
            "presentation_id": str(presentation_id),
            "client_response_id": str(client_response_id),
            "answer": answer.model_dump(mode="json"),
            "instrument_version": instrument_version,
            "selection_policy_version": selection_policy_version,
        }
        if client_timestamp is not None:
            body["client_timestamp"] = client_timestamp.isoformat()

        rows = await self._service_request(
            "POST",
            "/rest/v1/measurement_responses",
            json=body,
            prefer="return=representation",
            expected={201},
        )
        return MeasurementResponseRecord.model_validate(rows[0])

    async def complete_measurement_session(
        self,
        session_id: UUID,
    ) -> MeasurementSessionRecord:
        rows = await self._service_request(
            "PATCH",
            "/rest/v1/measurement_sessions",
            params={"id": f"eq.{session_id}"},
            json={
                "status": "complete",
                "completed_at": datetime.now(UTC).isoformat(),
            },
            prefer="return=representation",
        )
        if not rows:
            raise SupabasePersistenceError(
                404,
                "Measurement session disappeared during completion.",
            )
        return MeasurementSessionRecord.model_validate(rows[0])

    async def find_measurement_score_run(
        self,
        session_id: UUID,
        scoring_version: str,
        evidence_fingerprint: str,
    ) -> MeasurementScoreRunRecord | None:
        rows = await self._service_request(
            "GET",
            "/rest/v1/measurement_score_runs",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "scoring_version": f"eq.{scoring_version}",
                "evidence_fingerprint": f"eq.{evidence_fingerprint}",
                "limit": "1",
            },
        )
        return MeasurementScoreRunRecord.model_validate(rows[0]) if rows else None

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
        rows = await self._service_request(
            "POST",
            "/rest/v1/measurement_score_runs",
            json={
                "session_id": str(session_id),
                "subject_id": str(subject_id),
                "scoring_version": scoring_version,
                "evidence_fingerprint": evidence_fingerprint,
                "response_count": response_count,
                "scores": scores,
            },
            prefer="return=representation",
            expected={201},
        )
        return MeasurementScoreRunRecord.model_validate(rows[0])
