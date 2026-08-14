from datetime import UTC, datetime
from uuid import UUID, uuid5

from mosaic_engine.models import (
    CalibrationNextResponse,
    CalibrationNextStatus,
    CalibrationResponseChoice,
    CalibrationResponseReceipt,
    CalibrationResponseRequest,
    CalibrationStimulus,
    CalibrationStimulusOption,
)
from mosaic_engine.store import (
    CalibrationResponseRecord,
    CalibrationSessionRecord,
    CalibrationStore,
    CalibrationTrialRecord,
)
from mosaic_engine.supabase import SupabaseConflictError
from mosaic_engine.version import MOCK_CALIBRATION_POLICY_VERSION

MOCK_CALIBRATION_INSTRUMENT_KEY = "p4-text-pair"
MOCK_CALIBRATION_INSTRUMENT_VERSION = "p4-text-pair-1.0.0"
MOCK_CALIBRATION_STIMULUS_VERSION = "p4-text-pair-stimulus-1.0.0"
MOCK_CALIBRATION_TARGET_TRIALS = 10

_MOCK_NAMESPACE = UUID("4d1c5223-93c7-4e79-a733-4fd19815fe93")
_TEXT_PAIRS = (
    ("Quiet evening at home", "Spontaneous night out"),
    ("Plan the weekend early", "Decide the weekend as it unfolds"),
    ("Frequent small gatherings", "Occasional large gatherings"),
    ("Save toward a future goal", "Spend on a memorable experience"),
    ("Resolve disagreement promptly", "Take time before revisiting disagreement"),
    ("Share most free time together", "Keep substantial independent free time"),
    ("Prefer predictable routines", "Prefer frequent novelty"),
    ("Talk through feelings immediately", "Process feelings internally first"),
    ("Relocate for a major career opportunity", "Stay close to an established community"),
    ("Plan household responsibilities explicitly", "Divide responsibilities flexibly as needed"),
)


class CalibrationConflictError(RuntimeError):
    pass


class CalibrationNotFoundError(RuntimeError):
    pass


class CalibrationService:
    def __init__(self, store: CalibrationStore) -> None:
        self._store = store

    async def next_trial(self, subject_id: UUID) -> CalibrationNextResponse:
        session = await self._get_or_create_session(subject_id)
        trials = await self._store.list_trials(session.id)
        responses = await self._store.list_responses(session.id)
        completed = len(responses)

        if completed >= session.target_trial_count:
            if session.status != "complete":
                session = await self._store.complete_session(session.id)
            return self._complete_response(session, completed)

        answered = {response.experiment_id for response in responses}
        pending = next((trial for trial in trials if trial.id not in answered), None)
        if pending is not None:
            return self._trial_response(session, pending, completed)

        ordinal = completed + 1
        trial = self._build_trial(session, ordinal)
        try:
            trial = await self._store.create_trial(trial)
        except SupabaseConflictError:
            trials = await self._store.list_trials(session.id)
            raced = next((item for item in trials if item.ordinal == ordinal), None)
            if raced is None:
                raise
            trial = raced

        return self._trial_response(session, trial, completed)

    async def submit_response(
        self,
        subject_id: UUID,
        request: CalibrationResponseRequest,
    ) -> CalibrationResponseReceipt:
        existing_idempotent = await self._store.find_response_by_client_id(
            request.client_response_id,
        )
        if existing_idempotent is not None:
            self._assert_same_idempotent_request(subject_id, request, existing_idempotent)
            return await self._receipt(existing_idempotent, duplicate=True)

        session = await self._store.get_session_by_id(subject_id, request.session_id)
        if session is None:
            raise CalibrationNotFoundError("Calibration session was not found for this subject.")
        if session.policy_version != MOCK_CALIBRATION_POLICY_VERSION:
            raise CalibrationConflictError("Calibration session policy version is not active.")
        if session.status == "complete":
            raise CalibrationConflictError("Calibration session is already complete.")

        trial = await self._store.get_trial(request.experiment_id)
        if trial is None:
            raise CalibrationNotFoundError("Calibration experiment was not found.")
        if trial.session_id != session.id or trial.subject_id != subject_id:
            raise CalibrationConflictError(
                "Experiment does not belong to the authenticated session.",
            )

        existing_experiment = await self._store.find_response_by_experiment_id(
            request.experiment_id,
        )
        if existing_experiment is not None:
            raise CalibrationConflictError(
                "Experiment already has immutable evidence under a different idempotency key.",
            )

        responses = await self._store.list_responses(session.id)
        expected_ordinal = len(responses) + 1
        if trial.ordinal != expected_ordinal:
            raise CalibrationConflictError(
                f"Out-of-order response: expected ordinal {expected_ordinal}, got {trial.ordinal}.",
            )

        try:
            record = await self._store.create_response(
                subject_id=subject_id,
                session_id=session.id,
                experiment_id=trial.id,
                client_response_id=request.client_response_id,
                response=request.response,
                client_timestamp=request.client_timestamp,
                policy_version=MOCK_CALIBRATION_POLICY_VERSION,
            )
        except SupabaseConflictError as exc:
            raced = await self._store.find_response_by_client_id(request.client_response_id)
            if raced is None:
                raise CalibrationConflictError(
                    "Calibration response conflicted with immutable evidence.",
                ) from exc
            self._assert_same_idempotent_request(subject_id, request, raced)
            return await self._receipt(raced, duplicate=True)

        completed = len(responses) + 1
        if completed >= session.target_trial_count:
            await self._store.complete_session(session.id)

        return CalibrationResponseReceipt(
            duplicate=False,
            session_id=session.id,
            experiment_id=trial.id,
            client_response_id=request.client_response_id,
            policy_version=MOCK_CALIBRATION_POLICY_VERSION,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            session_complete=completed >= session.target_trial_count,
            server_timestamp=record.server_timestamp,
        )

    async def _get_or_create_session(self, subject_id: UUID) -> CalibrationSessionRecord:
        session = await self._store.get_session(
            subject_id,
            MOCK_CALIBRATION_INSTRUMENT_KEY,
            MOCK_CALIBRATION_INSTRUMENT_VERSION,
            MOCK_CALIBRATION_POLICY_VERSION,
        )
        if session is not None:
            return session

        try:
            return await self._store.create_session(
                subject_id,
                MOCK_CALIBRATION_INSTRUMENT_KEY,
                MOCK_CALIBRATION_INSTRUMENT_VERSION,
                MOCK_CALIBRATION_POLICY_VERSION,
                MOCK_CALIBRATION_TARGET_TRIALS,
            )
        except SupabaseConflictError:
            raced = await self._store.get_session(
                subject_id,
                MOCK_CALIBRATION_INSTRUMENT_KEY,
                MOCK_CALIBRATION_INSTRUMENT_VERSION,
                MOCK_CALIBRATION_POLICY_VERSION,
            )
            if raced is None:
                raise
            return raced

    def _build_trial(
        self,
        session: CalibrationSessionRecord,
        ordinal: int,
    ) -> CalibrationTrialRecord:
        experiment_id = uuid5(
            _MOCK_NAMESPACE,
            f"{MOCK_CALIBRATION_POLICY_VERSION}:{session.id}:{ordinal}",
        )
        left_label, right_label = _TEXT_PAIRS[(ordinal - 1) % len(_TEXT_PAIRS)]
        stimulus_id = f"p4-text-pair-{ordinal:02d}"
        stimulus = CalibrationStimulus(
            left=CalibrationStimulusOption(id=f"{stimulus_id}:left", label=left_label),
            right=CalibrationStimulusOption(id=f"{stimulus_id}:right", label=right_label),
        )
        return CalibrationTrialRecord(
            id=experiment_id,
            session_id=session.id,
            subject_id=session.subject_id,
            ordinal=ordinal,
            stimulus_id=stimulus_id,
            stimulus_version=MOCK_CALIBRATION_STIMULUS_VERSION,
            policy_version=MOCK_CALIBRATION_POLICY_VERSION,
            stimulus=stimulus,
            response_options=list(CalibrationResponseChoice),
            created_at=datetime.now(UTC),
        )

    def _trial_response(
        self,
        session: CalibrationSessionRecord,
        trial: CalibrationTrialRecord,
        completed: int,
    ) -> CalibrationNextResponse:
        return CalibrationNextResponse(
            session_id=session.id,
            status=CalibrationNextStatus.TRIAL,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            policy_version=session.policy_version,
            instrument_version=session.instrument_version,
            experiment_id=trial.id,
            ordinal=trial.ordinal,
            stimulus_id=trial.stimulus_id,
            stimulus_version=trial.stimulus_version,
            stimulus=trial.stimulus,
            response_options=trial.response_options,
        )

    def _complete_response(
        self,
        session: CalibrationSessionRecord,
        completed: int,
    ) -> CalibrationNextResponse:
        return CalibrationNextResponse(
            session_id=session.id,
            status=CalibrationNextStatus.COMPLETE,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            policy_version=session.policy_version,
            instrument_version=session.instrument_version,
        )

    async def _receipt(
        self,
        response: CalibrationResponseRecord,
        *,
        duplicate: bool,
    ) -> CalibrationResponseReceipt:
        session = await self._store.get_session_by_id(
            response.subject_id,
            response.session_id,
        )
        if session is None:
            raise CalibrationNotFoundError(
                "Calibration session disappeared after response storage.",
            )
        completed = len(await self._store.list_responses(session.id))
        return CalibrationResponseReceipt(
            duplicate=duplicate,
            session_id=response.session_id,
            experiment_id=response.experiment_id,
            client_response_id=response.client_response_id,
            policy_version=response.policy_version,
            completed_trial_count=completed,
            target_trial_count=session.target_trial_count,
            session_complete=completed >= session.target_trial_count,
            server_timestamp=response.server_timestamp,
        )

    def _assert_same_idempotent_request(
        self,
        subject_id: UUID,
        request: CalibrationResponseRequest,
        stored: CalibrationResponseRecord,
    ) -> None:
        if (
            stored.subject_id != subject_id
            or stored.session_id != request.session_id
            or stored.experiment_id != request.experiment_id
            or stored.response != request.response
            or stored.client_timestamp != request.client_timestamp
        ):
            raise CalibrationConflictError(
                "client_response_id was reused with a different immutable response payload.",
            )
