import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid5

from mosaic_engine.models import CalibrationResponseChoice
from mosaic_engine.supabase import SupabaseConflictError
from mosaic_engine.synthetic_generation import (
    DeterministicSvgGenerator,
    SyntheticGeneratorAdapter,
)
from mosaic_engine.synthetic_models import (
    SyntheticAsset,
    SyntheticCalibrationNextResponse,
    SyntheticCalibrationNextStatus,
    SyntheticCalibrationPair,
    SyntheticCalibrationResponseReceipt,
    SyntheticCalibrationResponseRequest,
    SyntheticStimulusSpecification,
)
from mosaic_engine.synthetic_store import (
    SyntheticAssetRecord,
    SyntheticCalibrationResponseRecord,
    SyntheticCalibrationSessionRecord,
    SyntheticCalibrationStore,
    SyntheticPairRecord,
    SyntheticQcEventRecord,
    SyntheticStimulusSpecRecord,
)
from mosaic_engine.version import MOCK_SYNTHETIC_PAIR_POLICY_VERSION

MOCK_SYNTHETIC_INSTRUMENT_KEY = "p6-synthetic-pair"
MOCK_SYNTHETIC_INSTRUMENT_VERSION = "p6-synthetic-pair-1.0.0"
MOCK_SYNTHETIC_SPEC_VERSION = "p6-synthetic-spec-1.0.0"
MOCK_SYNTHETIC_QC_VERSION = "p6-synthetic-qc-1.0.0"
MOCK_SYNTHETIC_TARGET_TRIALS = 20

_SPEC_NAMESPACE = UUID("a8de2f44-21f0-4d74-9d2c-b213a484f073")
_ASSET_NAMESPACE = UUID("85e79f03-88c7-43ce-b722-2e3f5f3403ab")
_QC_NAMESPACE = UUID("fd0921ca-086d-40fd-a201-d381d1ed98da")
_PAIR_NAMESPACE = UUID("4ab6ef79-40d1-4d9b-b83c-11dcbd96971e")


class SyntheticCalibrationConflictError(RuntimeError):
    pass


class SyntheticCalibrationNotFoundError(RuntimeError):
    pass


class SyntheticCalibrationService:
    def __init__(
        self,
        store: SyntheticCalibrationStore,
        generator: SyntheticGeneratorAdapter | None = None,
    ) -> None:
        self._store = store
        self._generator = generator or DeterministicSvgGenerator()

    async def next_pair(self, subject_id: UUID) -> SyntheticCalibrationNextResponse:
        session = await self._get_or_create_session(subject_id)
        responses = await self._store.list_synthetic_responses(session.id)
        completed = len(responses)

        if completed >= session.target_trial_count:
            if session.status != "complete":
                session = await self._store.complete_synthetic_session(session.id)
            return self._complete_response(session, completed)

        pairs = await self._ensure_cache(session)
        answered = {response.pair_id for response in responses}
        pending = next((pair for pair in pairs if pair.id not in answered), None)
        if pending is None:
            raise SyntheticCalibrationConflictError(
                "Synthetic pair cache does not contain the next unanswered trial.",
            )
        return await self._pair_response(session, pending, completed, len(pairs))

    async def submit_response(
        self,
        subject_id: UUID,
        request: SyntheticCalibrationResponseRequest,
    ) -> SyntheticCalibrationResponseReceipt:
        existing_idempotent = await self._store.find_synthetic_response_by_client_id(
            request.client_response_id,
        )
        if existing_idempotent is not None:
            self._assert_same_idempotent_request(subject_id, request, existing_idempotent)
            return await self._receipt(existing_idempotent, duplicate=True)

        session = await self._store.get_synthetic_session_by_id(subject_id, request.session_id)
        if session is None:
            raise SyntheticCalibrationNotFoundError(
                "Synthetic calibration session was not found for this subject.",
            )
        if session.pair_policy_version != MOCK_SYNTHETIC_PAIR_POLICY_VERSION:
            raise SyntheticCalibrationConflictError(
                "Synthetic calibration pair-policy version is not active.",
            )
        if session.status == "complete":
            raise SyntheticCalibrationConflictError(
                "Synthetic calibration session is already complete.",
            )

        pair = await self._store.get_synthetic_pair(request.pair_id)
        if pair is None:
            raise SyntheticCalibrationNotFoundError("Synthetic calibration pair was not found.")
        if pair.session_id != session.id or pair.subject_id != subject_id:
            raise SyntheticCalibrationConflictError(
                "Synthetic pair does not belong to the authenticated session.",
            )

        existing_pair = await self._store.find_synthetic_response_by_pair_id(request.pair_id)
        if existing_pair is not None:
            raise SyntheticCalibrationConflictError(
                "Synthetic pair already has immutable evidence under a different idempotency key.",
            )

        responses = await self._store.list_synthetic_responses(session.id)
        expected_ordinal = len(responses) + 1
        if pair.ordinal != expected_ordinal:
            raise SyntheticCalibrationConflictError(
                f"Out-of-order response: expected ordinal {expected_ordinal}, got {pair.ordinal}.",
            )

        try:
            record = await self._store.create_synthetic_response(
                subject_id=subject_id,
                session_id=session.id,
                pair_id=pair.id,
                client_response_id=request.client_response_id,
                response=request.response,
                client_timestamp=request.client_timestamp,
                pair_policy_version=session.pair_policy_version,
            )
        except SupabaseConflictError as exc:
            raced = await self._store.find_synthetic_response_by_client_id(
                request.client_response_id,
            )
            if raced is None:
                raise SyntheticCalibrationConflictError(
                    "Synthetic calibration response conflicted with immutable evidence.",
                ) from exc
            self._assert_same_idempotent_request(subject_id, request, raced)
            return await self._receipt(raced, duplicate=True)

        completed = len(responses) + 1
        if completed >= session.target_trial_count:
            await self._store.complete_synthetic_session(session.id)

        return SyntheticCalibrationResponseReceipt(
            duplicate=False,
            session_id=session.id,
            pair_id=pair.id,
            client_response_id=request.client_response_id,
            pair_policy_version=session.pair_policy_version,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            session_complete=completed >= session.target_trial_count,
            server_timestamp=record.server_timestamp,
        )

    async def _get_or_create_session(
        self,
        subject_id: UUID,
    ) -> SyntheticCalibrationSessionRecord:
        session = await self._store.get_synthetic_session(
            subject_id,
            MOCK_SYNTHETIC_INSTRUMENT_KEY,
            MOCK_SYNTHETIC_INSTRUMENT_VERSION,
            MOCK_SYNTHETIC_PAIR_POLICY_VERSION,
            self._generator.version,
        )
        if session is not None:
            return session

        try:
            return await self._store.create_synthetic_session(
                subject_id=subject_id,
                instrument_key=MOCK_SYNTHETIC_INSTRUMENT_KEY,
                instrument_version=MOCK_SYNTHETIC_INSTRUMENT_VERSION,
                pair_policy_version=MOCK_SYNTHETIC_PAIR_POLICY_VERSION,
                generator_adapter_version=self._generator.version,
                target_trial_count=MOCK_SYNTHETIC_TARGET_TRIALS,
            )
        except SupabaseConflictError:
            raced = await self._store.get_synthetic_session(
                subject_id,
                MOCK_SYNTHETIC_INSTRUMENT_KEY,
                MOCK_SYNTHETIC_INSTRUMENT_VERSION,
                MOCK_SYNTHETIC_PAIR_POLICY_VERSION,
                self._generator.version,
            )
            if raced is None:
                raise
            return raced

    async def _ensure_cache(
        self,
        session: SyntheticCalibrationSessionRecord,
    ) -> list[SyntheticPairRecord]:
        pairs = await self._store.list_synthetic_pairs(session.id)
        existing_ordinals = {pair.ordinal for pair in pairs}
        for ordinal in range(1, session.target_trial_count + 1):
            if ordinal in existing_ordinals:
                continue
            await self._ensure_pair_artifacts(session, ordinal)
        return await self._store.list_synthetic_pairs(session.id)

    async def _ensure_pair_artifacts(
        self,
        session: SyntheticCalibrationSessionRecord,
        ordinal: int,
    ) -> None:
        assets: list[SyntheticAssetRecord] = []
        for variant in (0, 1):
            specification = self._build_specification(session, ordinal, variant)
            spec_id = uuid5(
                _SPEC_NAMESPACE,
                f"{session.id}:{specification.candidate_key}:{specification.spec_version}",
            )
            specification_sha256 = self._sha256_json(specification.model_dump(mode="json"))
            spec_record = SyntheticStimulusSpecRecord(
                id=spec_id,
                session_id=session.id,
                subject_id=session.subject_id,
                stimulus_key=specification.candidate_key,
                spec_version=specification.spec_version,
                specification_sha256=specification_sha256,
                specification=specification,
                created_at=datetime.now(UTC),
            )
            try:
                await self._store.create_synthetic_spec(spec_record)
            except SupabaseConflictError:
                pass

            generated = self._generator.generate(specification)
            asset_id = uuid5(
                _ASSET_NAMESPACE,
                f"{session.id}:{spec_id}:{generated.content_sha256}",
            )
            asset_record = SyntheticAssetRecord(
                id=asset_id,
                spec_id=spec_id,
                session_id=session.id,
                subject_id=session.subject_id,
                media_type=generated.media_type,
                content_sha256=generated.content_sha256,
                asset_uri=generated.asset_uri,
                generation_provenance=generated.provenance,
                created_at=datetime.now(UTC),
            )
            try:
                asset_record = await self._store.create_synthetic_asset(asset_record)
            except SupabaseConflictError:
                existing_asset = await self._store.get_synthetic_asset(asset_id)
                if existing_asset is None:
                    raise
                asset_record = existing_asset

            decision = (
                "accepted"
                if asset_record.media_type == "image/svg+xml"
                and len(asset_record.content_sha256) == 64
                else "rejected"
            )
            reasons = [] if decision == "accepted" else ["mock_generator_integrity_failure"]
            qc_record = SyntheticQcEventRecord(
                id=uuid5(_QC_NAMESPACE, f"{asset_id}:{MOCK_SYNTHETIC_QC_VERSION}"),
                asset_id=asset_id,
                session_id=session.id,
                subject_id=session.subject_id,
                qc_version=MOCK_SYNTHETIC_QC_VERSION,
                decision=decision,
                reasons=reasons,
                created_at=datetime.now(UTC),
            )
            try:
                await self._store.create_synthetic_qc_event(qc_record)
            except SupabaseConflictError:
                pass
            if decision != "accepted":
                raise SyntheticCalibrationConflictError(
                    "Synthetic mock generator produced an asset that failed deterministic QC.",
                )
            assets.append(asset_record)

        randomization_seed = self._seed(f"pair:{session.id}:{ordinal}")
        left, right = assets if randomization_seed % 2 == 0 else list(reversed(assets))
        pair_record = SyntheticPairRecord(
            id=uuid5(
                _PAIR_NAMESPACE,
                f"{session.id}:{ordinal}:{MOCK_SYNTHETIC_PAIR_POLICY_VERSION}",
            ),
            session_id=session.id,
            subject_id=session.subject_id,
            ordinal=ordinal,
            left_asset_id=left.id,
            right_asset_id=right.id,
            randomization_seed=randomization_seed,
            pair_policy_version=MOCK_SYNTHETIC_PAIR_POLICY_VERSION,
            created_at=datetime.now(UTC),
        )
        try:
            await self._store.create_synthetic_pair(pair_record)
        except SupabaseConflictError:
            pass

    def _build_specification(
        self,
        session: SyntheticCalibrationSessionRecord,
        ordinal: int,
        variant: int,
    ) -> SyntheticStimulusSpecification:
        candidate_key = f"p6-{ordinal:02d}-{chr(ord('a') + variant)}"
        return SyntheticStimulusSpecification(
            spec_version=MOCK_SYNTHETIC_SPEC_VERSION,
            candidate_key=candidate_key,
            seed=self._seed(f"candidate:{session.id}:{ordinal}:{variant}"),
            control_vector={
                "face_width": ((ordinal * 7 + variant * 3) % 11) / 10,
                "eye_spacing": ((ordinal * 5 + variant * 7 + 2) % 11) / 10,
                "smile": ((ordinal * 3 + variant * 5 + 4) % 11) / 10,
                "contrast": ((ordinal * 2 + variant * 9 + 1) % 11) / 10,
                "hair_height": ((ordinal * 11 + variant * 4 + 3) % 13) / 12,
            },
            prompt_template=(
                "Controlled synthetic calibration candidate {candidate_key}; "
                "deterministic seed {seed}."
            ),
        )

    async def _pair_response(
        self,
        session: SyntheticCalibrationSessionRecord,
        pair: SyntheticPairRecord,
        completed: int,
        cache_size: int,
    ) -> SyntheticCalibrationNextResponse:
        left = await self._store.get_synthetic_asset(pair.left_asset_id)
        right = await self._store.get_synthetic_asset(pair.right_asset_id)
        if left is None or right is None:
            raise SyntheticCalibrationNotFoundError(
                "Synthetic pair references an asset that cannot be reconstructed.",
            )
        return SyntheticCalibrationNextResponse(
            session_id=session.id,
            status=SyntheticCalibrationNextStatus.PAIR,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            instrument_version=session.instrument_version,
            pair_policy_version=session.pair_policy_version,
            generator_adapter_version=session.generator_adapter_version,
            pair=SyntheticCalibrationPair(
                pair_id=pair.id,
                ordinal=pair.ordinal,
                left=self._asset_view(left),
                right=self._asset_view(right),
                randomization_seed=pair.randomization_seed,
                pair_policy_version=pair.pair_policy_version,
            ),
            response_options=list(CalibrationResponseChoice),
            cache_ready=cache_size >= session.target_trial_count,
        )

    def _complete_response(
        self,
        session: SyntheticCalibrationSessionRecord,
        completed: int,
    ) -> SyntheticCalibrationNextResponse:
        return SyntheticCalibrationNextResponse(
            session_id=session.id,
            status=SyntheticCalibrationNextStatus.COMPLETE,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            instrument_version=session.instrument_version,
            pair_policy_version=session.pair_policy_version,
            generator_adapter_version=session.generator_adapter_version,
            cache_ready=True,
        )

    async def _receipt(
        self,
        response: SyntheticCalibrationResponseRecord,
        *,
        duplicate: bool,
    ) -> SyntheticCalibrationResponseReceipt:
        session = await self._store.get_synthetic_session_by_id(
            response.subject_id,
            response.session_id,
        )
        if session is None:
            raise SyntheticCalibrationNotFoundError(
                "Synthetic calibration session disappeared after response storage.",
            )
        completed = len(await self._store.list_synthetic_responses(session.id))
        return SyntheticCalibrationResponseReceipt(
            duplicate=duplicate,
            session_id=response.session_id,
            pair_id=response.pair_id,
            client_response_id=response.client_response_id,
            pair_policy_version=response.pair_policy_version,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            session_complete=completed >= session.target_trial_count,
            server_timestamp=response.server_timestamp,
        )

    def _assert_same_idempotent_request(
        self,
        subject_id: UUID,
        request: SyntheticCalibrationResponseRequest,
        stored: SyntheticCalibrationResponseRecord,
    ) -> None:
        if (
            stored.subject_id != subject_id
            or stored.session_id != request.session_id
            or stored.pair_id != request.pair_id
            or stored.response != request.response
            or stored.client_timestamp != request.client_timestamp
        ):
            raise SyntheticCalibrationConflictError(
                "client_response_id was reused with a different immutable synthetic payload.",
            )

    def _asset_view(self, record: SyntheticAssetRecord) -> SyntheticAsset:
        return SyntheticAsset(
            asset_id=record.id,
            specification_id=record.spec_id,
            media_type=record.media_type,
            content_sha256=record.content_sha256,
            asset_uri=record.asset_uri,
            provenance=record.generation_provenance,
        )

    def _seed(self, value: str) -> int:
        return int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big") & ((1 << 63) - 1)

    def _sha256_json(self, value: dict[str, object]) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(payload).hexdigest()
