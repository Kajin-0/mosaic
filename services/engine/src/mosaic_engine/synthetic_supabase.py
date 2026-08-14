from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from mosaic_engine.models import CalibrationResponseChoice
from mosaic_engine.supabase import SupabaseGateway, SupabasePersistenceError
from mosaic_engine.synthetic_store import (
    SyntheticAssetRecord,
    SyntheticCalibrationResponseRecord,
    SyntheticCalibrationSessionRecord,
    SyntheticPairRecord,
    SyntheticQcEventRecord,
    SyntheticStimulusSpecRecord,
)


class SyntheticSupabaseStore:
    def __init__(self, gateway: SupabaseGateway) -> None:
        self._gateway = gateway

    async def get_synthetic_session(
        self,
        subject_id: UUID,
        instrument_key: str,
        instrument_version: str,
        pair_policy_version: str,
        generator_adapter_version: str,
    ) -> SyntheticCalibrationSessionRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_calibration_sessions",
            params={
                "select": "*",
                "subject_id": f"eq.{subject_id}",
                "instrument_key": f"eq.{instrument_key}",
                "instrument_version": f"eq.{instrument_version}",
                "pair_policy_version": f"eq.{pair_policy_version}",
                "generator_adapter_version": f"eq.{generator_adapter_version}",
                "limit": "1",
            },
        )
        return SyntheticCalibrationSessionRecord.model_validate(rows[0]) if rows else None

    async def get_synthetic_session_by_id(
        self,
        subject_id: UUID,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_calibration_sessions",
            params={
                "select": "*",
                "id": f"eq.{session_id}",
                "subject_id": f"eq.{subject_id}",
                "limit": "1",
            },
        )
        return SyntheticCalibrationSessionRecord.model_validate(rows[0]) if rows else None

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
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_calibration_sessions",
            json={
                "subject_id": str(subject_id),
                "instrument_key": instrument_key,
                "instrument_version": instrument_version,
                "pair_policy_version": pair_policy_version,
                "generator_adapter_version": generator_adapter_version,
                "target_trial_count": target_trial_count,
            },
            prefer="return=representation",
            expected={201},
        )
        return SyntheticCalibrationSessionRecord.model_validate(rows[0])

    async def complete_synthetic_session(
        self,
        session_id: UUID,
    ) -> SyntheticCalibrationSessionRecord:
        rows = await self._gateway._service_request(
            "PATCH",
            "/rest/v1/synthetic_calibration_sessions",
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
                "Synthetic calibration session disappeared during completion.",
            )
        return SyntheticCalibrationSessionRecord.model_validate(rows[0])

    async def list_synthetic_pairs(self, session_id: UUID) -> list[SyntheticPairRecord]:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_pairs",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "ordinal.asc",
            },
        )
        return [SyntheticPairRecord.model_validate(row) for row in rows]

    async def create_synthetic_spec(
        self,
        record: SyntheticStimulusSpecRecord,
    ) -> SyntheticStimulusSpecRecord:
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_stimulus_specs",
            json={
                "id": str(record.id),
                "session_id": str(record.session_id),
                "subject_id": str(record.subject_id),
                "stimulus_key": record.stimulus_key,
                "spec_version": record.spec_version,
                "specification_sha256": record.specification_sha256,
                "specification": record.specification.model_dump(mode="json"),
            },
            prefer="return=representation",
            expected={201},
        )
        return SyntheticStimulusSpecRecord.model_validate(rows[0])

    async def get_synthetic_spec(self, spec_id: UUID) -> SyntheticStimulusSpecRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_stimulus_specs",
            params={"select": "*", "id": f"eq.{spec_id}", "limit": "1"},
        )
        return SyntheticStimulusSpecRecord.model_validate(rows[0]) if rows else None

    async def create_synthetic_asset(
        self,
        record: SyntheticAssetRecord,
    ) -> SyntheticAssetRecord:
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_assets",
            json={
                "id": str(record.id),
                "spec_id": str(record.spec_id),
                "session_id": str(record.session_id),
                "subject_id": str(record.subject_id),
                "media_type": record.media_type,
                "content_sha256": record.content_sha256,
                "asset_uri": record.asset_uri,
                "generation_provenance": record.generation_provenance.model_dump(mode="json"),
            },
            prefer="return=representation",
            expected={201},
        )
        return SyntheticAssetRecord.model_validate(rows[0])

    async def get_synthetic_asset(self, asset_id: UUID) -> SyntheticAssetRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_assets",
            params={"select": "*", "id": f"eq.{asset_id}", "limit": "1"},
        )
        return SyntheticAssetRecord.model_validate(rows[0]) if rows else None

    async def create_synthetic_qc_event(
        self,
        record: SyntheticQcEventRecord,
    ) -> SyntheticQcEventRecord:
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_qc_events",
            json={
                "id": str(record.id),
                "asset_id": str(record.asset_id),
                "session_id": str(record.session_id),
                "subject_id": str(record.subject_id),
                "qc_version": record.qc_version,
                "decision": record.decision,
                "reasons": record.reasons,
            },
            prefer="return=representation",
            expected={201},
        )
        return SyntheticQcEventRecord.model_validate(rows[0])

    async def get_synthetic_qc_event(
        self,
        qc_event_id: UUID,
    ) -> SyntheticQcEventRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_qc_events",
            params={"select": "*", "id": f"eq.{qc_event_id}", "limit": "1"},
        )
        return SyntheticQcEventRecord.model_validate(rows[0]) if rows else None

    async def create_synthetic_pair(
        self,
        record: SyntheticPairRecord,
    ) -> SyntheticPairRecord:
        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_pairs",
            json={
                "id": str(record.id),
                "session_id": str(record.session_id),
                "subject_id": str(record.subject_id),
                "ordinal": record.ordinal,
                "left_asset_id": str(record.left_asset_id),
                "right_asset_id": str(record.right_asset_id),
                "randomization_seed": record.randomization_seed,
                "pair_policy_version": record.pair_policy_version,
            },
            prefer="return=representation",
            expected={201},
        )
        return SyntheticPairRecord.model_validate(rows[0])

    async def get_synthetic_pair(self, pair_id: UUID) -> SyntheticPairRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_pairs",
            params={"select": "*", "id": f"eq.{pair_id}", "limit": "1"},
        )
        return SyntheticPairRecord.model_validate(rows[0]) if rows else None

    async def list_synthetic_responses(
        self,
        session_id: UUID,
    ) -> list[SyntheticCalibrationResponseRecord]:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_calibration_responses",
            params={
                "select": "*",
                "session_id": f"eq.{session_id}",
                "order": "server_timestamp.asc",
            },
        )
        return [SyntheticCalibrationResponseRecord.model_validate(row) for row in rows]

    async def find_synthetic_response_by_client_id(
        self,
        client_response_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None:
        return await self._find_response("client_response_id", client_response_id)

    async def find_synthetic_response_by_pair_id(
        self,
        pair_id: UUID,
    ) -> SyntheticCalibrationResponseRecord | None:
        return await self._find_response("pair_id", pair_id)

    async def _find_response(
        self,
        field: str,
        value: UUID,
    ) -> SyntheticCalibrationResponseRecord | None:
        rows = await self._gateway._service_request(
            "GET",
            "/rest/v1/synthetic_calibration_responses",
            params={"select": "*", field: f"eq.{value}", "limit": "1"},
        )
        return SyntheticCalibrationResponseRecord.model_validate(rows[0]) if rows else None

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
        body: dict[str, Any] = {
            "subject_id": str(subject_id),
            "session_id": str(session_id),
            "pair_id": str(pair_id),
            "client_response_id": str(client_response_id),
            "response": response.value,
            "pair_policy_version": pair_policy_version,
        }
        if client_timestamp is not None:
            body["client_timestamp"] = client_timestamp.isoformat()

        rows = await self._gateway._service_request(
            "POST",
            "/rest/v1/synthetic_calibration_responses",
            json=body,
            prefer="return=representation",
            expected={201},
        )
        return SyntheticCalibrationResponseRecord.model_validate(rows[0])
