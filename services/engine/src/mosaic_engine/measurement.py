import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid5

from mosaic_engine.measurement_models import (
    ForcedChoiceItem,
    HardConstraintItem,
    MeasurementAnswer,
    MeasurementChoiceAnswer,
    MeasurementChoiceOption,
    MeasurementItem,
    MeasurementNextResponse,
    MeasurementNextStatus,
    MeasurementRatingAnswer,
    MeasurementResponseReceipt,
    MeasurementResponseRequest,
    MeasurementScoreRequest,
    MeasurementScoreResponse,
    MeasurementScoringVersion,
    RatingItem,
    ScenarioItem,
)
from mosaic_engine.measurement_store import (
    MeasurementPresentationRecord,
    MeasurementResponseRecord,
    MeasurementScoreRunRecord,
    MeasurementSessionRecord,
    MeasurementStore,
)
from mosaic_engine.supabase import SupabaseConflictError
from mosaic_engine.version import MOCK_MEASUREMENT_SELECTION_POLICY_VERSION

MOCK_MEASUREMENT_INSTRUMENT_KEY = "p5-onboarding-measurement"
MOCK_MEASUREMENT_INSTRUMENT_VERSION = "p5-onboarding-measurement-1.0.0"
MOCK_MEASUREMENT_TARGET_ITEMS = 20
MOCK_MEASUREMENT_ITEM_VERSION = "p5-mock-item-1.0.0"

_MEASUREMENT_NAMESPACE = UUID("40f0e633-676e-4e0f-89f5-33b69faed2a2")


@dataclass(frozen=True)
class MockInstrumentItem:
    item_id: str
    item: MeasurementItem


def _option(option_id: str, label: str) -> MeasurementChoiceOption:
    return MeasurementChoiceOption(id=option_id, label=label)


_ITEM_BANK: tuple[MockInstrumentItem, ...] = (
    MockInstrumentItem(
        "p5-hard-children",
        HardConstraintItem(
            prompt="Which statement is closest to your requirement about having children?",
            dimension_key="family_plan",
            options=[
                _option("want_children", "I want children"),
                _option("no_children", "I do not want children"),
                _option("unsure_children", "I am genuinely unsure"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-hard-marriage",
        HardConstraintItem(
            prompt="Which long-term commitment structure fits your plans best?",
            dimension_key="commitment_structure",
            options=[
                _option("marriage_expected", "Marriage is important to me"),
                _option("marriage_optional", "Marriage is optional"),
                _option("marriage_avoid", "I do not want marriage"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-hard-location",
        HardConstraintItem(
            prompt="How fixed is your long-term geographic location?",
            dimension_key="location_flexibility",
            options=[
                _option("location_fixed", "I need to remain in my current region"),
                _option("location_some", "I could relocate for the right circumstances"),
                _option("location_open", "I am broadly open to relocation"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-hard-exclusivity",
        HardConstraintItem(
            prompt="Which relationship structure are you seeking?",
            dimension_key="relationship_structure",
            options=[
                _option("exclusive", "Exclusive / monogamous"),
                _option("open_to_discussion", "Open to discussing structure"),
                _option("nonexclusive", "Non-exclusive"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-hard-cohabitation",
        HardConstraintItem(
            prompt="What is your long-term preference about living with a partner?",
            dimension_key="cohabitation",
            options=[
                _option("cohabit_expected", "Eventually living together is important"),
                _option("cohabit_optional", "Either arrangement could work"),
                _option("separate_homes", "I prefer maintaining separate homes"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-rating-routine",
        RatingItem(
            prompt="How much do you prefer predictable routines in everyday life?",
            dimension_key="routine_preference",
            min_label="Strongly prefer spontaneity",
            max_label="Strongly prefer routine",
        ),
    ),
    MockInstrumentItem(
        "p5-rating-social",
        RatingItem(
            prompt="How socially active would you ideally be in a typical week?",
            dimension_key="social_intensity",
            min_label="Mostly private / quiet",
            max_label="Very socially active",
        ),
    ),
    MockInstrumentItem(
        "p5-rating-autonomy",
        RatingItem(
            prompt="How important is substantial independent time within a relationship?",
            dimension_key="autonomy",
            min_label="Prefer most free time together",
            max_label="Independent time is essential",
        ),
    ),
    MockInstrumentItem(
        "p5-rating-affection",
        RatingItem(
            prompt="How important is frequent verbal or physical affection in daily life?",
            dimension_key="affection",
            min_label="Low importance",
            max_label="Very high importance",
        ),
    ),
    MockInstrumentItem(
        "p5-rating-conflict",
        RatingItem(
            prompt="When a disagreement happens, how strongly do you prefer addressing it quickly?",
            dimension_key="conflict_timing",
            min_label="Prefer substantial time first",
            max_label="Prefer addressing it immediately",
        ),
    ),
    MockInstrumentItem(
        "p5-scenario-stress",
        ScenarioItem(
            prompt=(
                "Your partner comes home after a difficult day and becomes unusually quiet. "
                "What response feels most natural to you?"
            ),
            dimension_key="support_style",
            options=[
                _option("ask_now", "Ask directly what happened"),
                _option("offer_space", "Offer support and give them space"),
                _option("distract", "Suggest doing something enjoyable together"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-scenario-purchase",
        ScenarioItem(
            prompt=(
                "You disagree about a major discretionary purchase. What would you prefer "
                "to do first?"
            ),
            dimension_key="financial_coordination",
            options=[
                _option("budget_review", "Review goals and numbers together"),
                _option("cool_off", "Pause and revisit the decision later"),
                _option("individual_discretion", "Treat it mainly as individual discretion"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-scenario-family",
        ScenarioItem(
            prompt="Both families want you for the same holiday. What approach feels most natural?",
            dimension_key="family_coordination",
            options=[
                _option("alternate", "Create an explicit alternating plan"),
                _option("case_by_case", "Decide case by case each year"),
                _option("separate", "Sometimes attend family events separately"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-scenario-career",
        ScenarioItem(
            prompt=(
                "Your partner receives an exceptional career opportunity in another region. "
                "What is your first instinct?"
            ),
            dimension_key="career_coordination",
            options=[
                _option("explore_move", "Seriously explore moving together"),
                _option("compare_costs", "Compare both careers and life costs before deciding"),
                _option("stay_priority", "Prioritize remaining near the current community"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-scenario-reassurance",
        ScenarioItem(
            prompt=(
                "Communication has been lighter than usual for two days. What would you most "
                "likely do?"
            ),
            dimension_key="reassurance_style",
            options=[
                _option("check_in", "Check in directly about the change"),
                _option("wait", "Give it time unless the pattern continues"),
                _option("increase_contact", "Increase contact and warmth first"),
            ],
        ),
    ),
    MockInstrumentItem(
        "p5-forced-evening",
        ForcedChoiceItem(
            prompt="If you had to choose the more appealing default evening:",
            dimension_key="novelty_preference",
            left=_option("quiet_home", "Quiet evening at home"),
            right=_option("spontaneous_out", "Spontaneous night out"),
        ),
    ),
    MockInstrumentItem(
        "p5-forced-weekend",
        ForcedChoiceItem(
            prompt="If you had to choose the more comfortable weekend style:",
            dimension_key="planning_style",
            left=_option("plan_early", "Plan the weekend early"),
            right=_option("decide_later", "Decide as the weekend unfolds"),
        ),
    ),
    MockInstrumentItem(
        "p5-forced-money",
        ForcedChoiceItem(
            prompt="If both options were reasonable, which would you lean toward?",
            dimension_key="resource_style",
            left=_option("save_goal", "Save toward a future goal"),
            right=_option("buy_experience", "Spend on a memorable experience"),
        ),
    ),
    MockInstrumentItem(
        "p5-forced-time",
        ForcedChoiceItem(
            prompt="Which relationship rhythm sounds closer to your ideal?",
            dimension_key="togetherness",
            left=_option("shared_time", "Share most free time together"),
            right=_option("independent_time", "Keep substantial independent free time"),
        ),
    ),
    MockInstrumentItem(
        "p5-forced-repair",
        ForcedChoiceItem(
            prompt="After a tense disagreement, which default would you rather have?",
            dimension_key="repair_timing",
            left=_option("talk_promptly", "Talk through it promptly"),
            right=_option("revisit_later", "Take time and revisit it later"),
        ),
    ),
)


class MeasurementConflictError(RuntimeError):
    pass


class MeasurementNotFoundError(RuntimeError):
    pass


class MeasurementService:
    def __init__(self, store: MeasurementStore) -> None:
        self._store = store

    async def next_item(self, subject_id: UUID) -> MeasurementNextResponse:
        session = await self._get_or_create_session(subject_id)
        presentations = await self._store.list_measurement_presentations(session.id)
        responses = await self._store.list_measurement_responses(session.id)
        completed = len(responses)

        if completed >= session.target_item_count:
            if session.status != "complete":
                session = await self._store.complete_measurement_session(session.id)
            return self._complete_response(session, completed)

        answered = {response.presentation_id for response in responses}
        pending = next(
            (presentation for presentation in presentations if presentation.id not in answered),
            None,
        )
        if pending is not None:
            return self._item_response(session, pending, completed)

        item_spec = self._select_item(presentations)
        ordinal = completed + 1
        presentation = self._build_presentation(session, item_spec, ordinal)
        try:
            presentation = await self._store.create_measurement_presentation(presentation)
        except SupabaseConflictError:
            presentations = await self._store.list_measurement_presentations(session.id)
            raced = next((item for item in presentations if item.ordinal == ordinal), None)
            if raced is None:
                raise
            presentation = raced

        return self._item_response(session, presentation, completed)

    async def submit_response(
        self,
        subject_id: UUID,
        request: MeasurementResponseRequest,
    ) -> MeasurementResponseReceipt:
        existing_idempotent = await self._store.find_measurement_response_by_client_id(
            request.client_response_id,
        )
        if existing_idempotent is not None:
            self._assert_same_idempotent_request(subject_id, request, existing_idempotent)
            return await self._receipt(existing_idempotent, duplicate=True)

        session = await self._store.get_measurement_session_by_id(subject_id, request.session_id)
        if session is None:
            raise MeasurementNotFoundError("Measurement session was not found for this subject.")
        if session.selection_policy_version != MOCK_MEASUREMENT_SELECTION_POLICY_VERSION:
            raise MeasurementConflictError("Measurement selection policy version is not active.")
        if session.status == "complete":
            raise MeasurementConflictError("Measurement session is already complete.")

        presentation = await self._store.get_measurement_presentation(request.presentation_id)
        if presentation is None:
            raise MeasurementNotFoundError("Measurement presentation was not found.")
        if presentation.session_id != session.id or presentation.subject_id != subject_id:
            raise MeasurementConflictError(
                "Presentation does not belong to the authenticated measurement session.",
            )

        existing_presentation = await self._store.find_measurement_response_by_presentation_id(
            request.presentation_id,
        )
        if existing_presentation is not None:
            raise MeasurementConflictError(
                "Presentation already has immutable evidence under a different idempotency key.",
            )

        responses = await self._store.list_measurement_responses(session.id)
        expected_ordinal = len(responses) + 1
        if presentation.ordinal != expected_ordinal:
            raise MeasurementConflictError(
                "Out-of-order response: expected ordinal "
                f"{expected_ordinal}, got {presentation.ordinal}.",
            )

        self._validate_answer(presentation.item, request.answer)

        try:
            record = await self._store.create_measurement_response(
                subject_id=subject_id,
                session_id=session.id,
                presentation_id=presentation.id,
                client_response_id=request.client_response_id,
                answer=request.answer,
                client_timestamp=request.client_timestamp,
                instrument_version=session.instrument_version,
                selection_policy_version=session.selection_policy_version,
            )
        except SupabaseConflictError as exc:
            raced = await self._store.find_measurement_response_by_client_id(
                request.client_response_id,
            )
            if raced is None:
                raise MeasurementConflictError(
                    "Measurement response conflicted with immutable evidence.",
                ) from exc
            self._assert_same_idempotent_request(subject_id, request, raced)
            return await self._receipt(raced, duplicate=True)

        completed = len(responses) + 1
        if completed >= session.target_item_count:
            await self._store.complete_measurement_session(session.id)

        return MeasurementResponseReceipt(
            duplicate=False,
            session_id=session.id,
            presentation_id=presentation.id,
            client_response_id=request.client_response_id,
            instrument_version=session.instrument_version,
            selection_policy_version=session.selection_policy_version,
            completed_item_count=completed,
            target_item_count=session.target_item_count,
            session_complete=completed >= session.target_item_count,
            server_timestamp=record.server_timestamp,
        )

    async def score(
        self,
        subject_id: UUID,
        request: MeasurementScoreRequest,
    ) -> MeasurementScoreResponse:
        session = await self._store.get_measurement_session_by_id(subject_id, request.session_id)
        if session is None:
            raise MeasurementNotFoundError("Measurement session was not found for this subject.")

        presentations = await self._store.list_measurement_presentations(session.id)
        responses = await self._store.list_measurement_responses(session.id)
        evidence = self._joined_evidence(presentations, responses)
        fingerprint = self._evidence_fingerprint(evidence)
        scoring_version = request.scoring_version.value

        existing = await self._store.find_measurement_score_run(
            session.id,
            scoring_version,
            fingerprint,
        )
        if existing is not None:
            return self._score_response(existing)

        scores = self._compute_scores(evidence, request.scoring_version)
        try:
            run = await self._store.create_measurement_score_run(
                session_id=session.id,
                subject_id=subject_id,
                scoring_version=scoring_version,
                evidence_fingerprint=fingerprint,
                response_count=len(evidence),
                scores=scores,
            )
        except SupabaseConflictError:
            raced = await self._store.find_measurement_score_run(
                session.id,
                scoring_version,
                fingerprint,
            )
            if raced is None:
                raise
            run = raced
        return self._score_response(run)

    async def _get_or_create_session(self, subject_id: UUID) -> MeasurementSessionRecord:
        session = await self._store.get_measurement_session(
            subject_id,
            MOCK_MEASUREMENT_INSTRUMENT_KEY,
            MOCK_MEASUREMENT_INSTRUMENT_VERSION,
            MOCK_MEASUREMENT_SELECTION_POLICY_VERSION,
        )
        if session is not None:
            return session

        try:
            return await self._store.create_measurement_session(
                subject_id,
                MOCK_MEASUREMENT_INSTRUMENT_KEY,
                MOCK_MEASUREMENT_INSTRUMENT_VERSION,
                MOCK_MEASUREMENT_SELECTION_POLICY_VERSION,
                MOCK_MEASUREMENT_TARGET_ITEMS,
            )
        except SupabaseConflictError:
            raced = await self._store.get_measurement_session(
                subject_id,
                MOCK_MEASUREMENT_INSTRUMENT_KEY,
                MOCK_MEASUREMENT_INSTRUMENT_VERSION,
                MOCK_MEASUREMENT_SELECTION_POLICY_VERSION,
            )
            if raced is None:
                raise
            return raced

    def _select_item(
        self,
        presentations: list[MeasurementPresentationRecord],
    ) -> MockInstrumentItem:
        presented_ids = {presentation.item_id for presentation in presentations}
        for item in _ITEM_BANK:
            if item.item_id not in presented_ids:
                return item
        raise MeasurementConflictError("No unpresented item remains in the active instrument.")

    def _build_presentation(
        self,
        session: MeasurementSessionRecord,
        item_spec: MockInstrumentItem,
        ordinal: int,
    ) -> MeasurementPresentationRecord:
        presentation_id = uuid5(
            _MEASUREMENT_NAMESPACE,
            (f"{session.selection_policy_version}:{session.id}:{ordinal}:{item_spec.item_id}"),
        )
        return MeasurementPresentationRecord(
            id=presentation_id,
            session_id=session.id,
            subject_id=session.subject_id,
            ordinal=ordinal,
            item_id=item_spec.item_id,
            item_version=MOCK_MEASUREMENT_ITEM_VERSION,
            item_kind=item_spec.item.kind,
            selection_policy_version=session.selection_policy_version,
            item=item_spec.item,
            created_at=datetime.now(UTC),
        )

    def _item_response(
        self,
        session: MeasurementSessionRecord,
        presentation: MeasurementPresentationRecord,
        completed: int,
    ) -> MeasurementNextResponse:
        return MeasurementNextResponse(
            session_id=session.id,
            status=MeasurementNextStatus.ITEM,
            completed_item_count=completed,
            target_item_count=session.target_item_count,
            instrument_key=session.instrument_key,
            instrument_version=session.instrument_version,
            selection_policy_version=session.selection_policy_version,
            presentation_id=presentation.id,
            ordinal=presentation.ordinal,
            item_id=presentation.item_id,
            item_version=presentation.item_version,
            item=presentation.item,
        )

    def _complete_response(
        self,
        session: MeasurementSessionRecord,
        completed: int,
    ) -> MeasurementNextResponse:
        return MeasurementNextResponse(
            session_id=session.id,
            status=MeasurementNextStatus.COMPLETE,
            completed_item_count=completed,
            target_item_count=session.target_item_count,
            instrument_key=session.instrument_key,
            instrument_version=session.instrument_version,
            selection_policy_version=session.selection_policy_version,
        )

    async def _receipt(
        self,
        response: MeasurementResponseRecord,
        *,
        duplicate: bool,
    ) -> MeasurementResponseReceipt:
        session = await self._store.get_measurement_session_by_id(
            response.subject_id,
            response.session_id,
        )
        if session is None:
            raise MeasurementNotFoundError(
                "Measurement session disappeared after response storage.",
            )
        completed = len(await self._store.list_measurement_responses(session.id))
        return MeasurementResponseReceipt(
            duplicate=duplicate,
            session_id=response.session_id,
            presentation_id=response.presentation_id,
            client_response_id=response.client_response_id,
            instrument_version=response.instrument_version,
            selection_policy_version=response.selection_policy_version,
            completed_item_count=completed,
            target_item_count=session.target_item_count,
            session_complete=completed >= session.target_item_count,
            server_timestamp=response.server_timestamp,
        )

    def _assert_same_idempotent_request(
        self,
        subject_id: UUID,
        request: MeasurementResponseRequest,
        stored: MeasurementResponseRecord,
    ) -> None:
        if (
            stored.subject_id != subject_id
            or stored.session_id != request.session_id
            or stored.presentation_id != request.presentation_id
            or stored.answer.model_dump(mode="json") != request.answer.model_dump(mode="json")
            or stored.client_timestamp != request.client_timestamp
        ):
            raise MeasurementConflictError(
                "client_response_id was reused with a different immutable measurement payload.",
            )

    def _validate_answer(self, item: MeasurementItem, answer: MeasurementAnswer) -> None:
        if isinstance(item, RatingItem):
            if not isinstance(answer, MeasurementRatingAnswer):
                raise MeasurementConflictError("Rating item requires a rating answer.")
            if not item.scale_min <= answer.value <= item.scale_max:
                raise MeasurementConflictError("Rating answer is outside the authored scale.")
            return

        if not isinstance(answer, MeasurementChoiceAnswer):
            raise MeasurementConflictError("Choice item requires a choice answer.")

        if isinstance(item, ForcedChoiceItem):
            valid = {item.left.id, item.right.id}
        elif isinstance(item, (HardConstraintItem, ScenarioItem)):
            valid = {option.id for option in item.options}
        else:
            raise MeasurementConflictError("Unsupported measurement item kind.")
        if answer.option_id not in valid:
            raise MeasurementConflictError("Choice answer does not belong to the authored item.")

    def _joined_evidence(
        self,
        presentations: list[MeasurementPresentationRecord],
        responses: list[MeasurementResponseRecord],
    ) -> list[tuple[MeasurementPresentationRecord, MeasurementResponseRecord]]:
        response_by_presentation = {response.presentation_id: response for response in responses}
        return [
            (presentation, response_by_presentation[presentation.id])
            for presentation in sorted(presentations, key=lambda value: value.ordinal)
            if presentation.id in response_by_presentation
        ]

    def _evidence_fingerprint(
        self,
        evidence: list[tuple[MeasurementPresentationRecord, MeasurementResponseRecord]],
    ) -> str:
        canonical = [
            {
                "ordinal": presentation.ordinal,
                "presentation_id": str(presentation.id),
                "item_id": presentation.item_id,
                "item_version": presentation.item_version,
                "selection_policy_version": presentation.selection_policy_version,
                "item": presentation.item.model_dump(mode="json"),
                "instrument_version": response.instrument_version,
                "response_selection_policy_version": response.selection_policy_version,
                "answer": response.answer.model_dump(mode="json"),
            }
            for presentation, response in evidence
        ]
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(payload).hexdigest()

    def _compute_scores(
        self,
        evidence: list[tuple[MeasurementPresentationRecord, MeasurementResponseRecord]],
        scoring_version: MeasurementScoringVersion,
    ) -> dict[str, float]:
        values: dict[str, list[float]] = {}
        for presentation, response in evidence:
            value = self._numeric_answer(presentation.item, response.answer)
            if scoring_version == MeasurementScoringVersion.V2:
                value = 0.1 + 0.8 * (value**1.25)
            values.setdefault(presentation.item.dimension_key, []).append(value)

        scores = {
            dimension: round(sum(items) / len(items), 6)
            for dimension, items in sorted(values.items())
        }
        scores["completion"] = round(len(evidence) / MOCK_MEASUREMENT_TARGET_ITEMS, 6)
        return scores

    def _numeric_answer(self, item: MeasurementItem, answer: MeasurementAnswer) -> float:
        if isinstance(item, RatingItem) and isinstance(answer, MeasurementRatingAnswer):
            return (answer.value - item.scale_min) / (item.scale_max - item.scale_min)

        if not isinstance(answer, MeasurementChoiceAnswer):
            raise MeasurementConflictError("Stored answer does not match its item type.")

        if isinstance(item, ForcedChoiceItem):
            options = [item.left.id, item.right.id]
        elif isinstance(item, (HardConstraintItem, ScenarioItem)):
            options = [option.id for option in item.options]
        else:
            raise MeasurementConflictError("Stored item kind is unsupported for scoring.")
        try:
            index = options.index(answer.option_id)
        except ValueError as exc:
            raise MeasurementConflictError("Stored answer is not valid for its item.") from exc
        return index / max(1, len(options) - 1)

    def _score_response(self, run: MeasurementScoreRunRecord) -> MeasurementScoreResponse:
        return MeasurementScoreResponse(
            score_run_id=run.id,
            session_id=run.session_id,
            scoring_version=MeasurementScoringVersion(run.scoring_version),
            evidence_fingerprint=run.evidence_fingerprint,
            response_count=run.response_count,
            scores=run.scores,
            created_at=run.created_at,
        )
