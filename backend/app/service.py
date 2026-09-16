# from __future__ import annotations

# import re
# from datetime import datetime, timezone
# from typing import Any

# from .config import load_manifest, load_policy
# from .models import ModelNotReady, ModelRuntime
# from .rules import (
#     assign_eisenhower_quadrant,
#     calculate_deadline_proximity,
#     calculate_explicit_cue_strength,
#     calculate_slot_recency,
#     calculate_urgency_score,
#     determine_importance,
#     parse_temporal_info,
# )
# from .schemas import (
#     AnalysisResponse,
#     ContextPrediction,
#     ImportanceOutput,
#     LabelProbability,
#     PriorityPrediction,
#     TaskAnalysisRequest,
#     TemporalOutput,
#     UrgencyOutput,
# )

# URL_PATTERN = re.compile(r'https?://\S+')
# CODE_PATTERN = re.compile(r'\{code[^}]*\}.*?\{code\}|<code>.*?</code>', re.I | re.S)
# LEAKAGE_PATTERN = re.compile(r'\b(blocker|critical|major|minor|trivial|urgent|asap)\b', re.I)


# def clean_priority_text(task_title: str, description: str = '') -> str:
#     # M4 Model B was trained on cleaned Jira summary/description text; list context
#     # belongs only to Model A and is intentionally excluded here.
#     text = f'{task_title or ""} {description or ""}'
#     text = CODE_PATTERN.sub(' ', text)
#     text = URL_PATTERN.sub(' ', text)
#     text = LEAKAGE_PATTERN.sub('[MASK]', text)
#     return re.sub(r'\s+', ' ', text).strip()


# class AnalysisService:
#     def __init__(self, runtime: ModelRuntime | None = None):
#         self.runtime = runtime or ModelRuntime()
#         self.policy = load_policy()
#         self.manifest = load_manifest()

#     def analyze(self, request: TaskAnalysisRequest) -> AnalysisResponse:
#         now = request.created_at or datetime.now(timezone.utc)
#         warnings: list[str] = []

#         temporal = parse_temporal_info(request.task_title, now)
#         if request.deadline is not None:
#             temporal['deadline'] = request.deadline
#             temporal['deadline_text'] = request.deadline.isoformat()
#             temporal['deadline_source'] = 'user'
#             temporal['deadline_precision'] = 'timestamp'
#         if request.duration_override_minutes is not None:
#             temporal['duration_override_minutes'] = request.duration_override_minutes
#             temporal['duration_source'] = 'user_override'
#         context_data: dict[str, Any] | None = None
#         try:
#             context_data = self.runtime.predict_context(request.task_title, request.list_title)
#         except ModelNotReady as exc:
#             warnings.append(f'Context model unavailable: {exc}')

#         priority_data: dict[str, Any] | None = None
#         try:
#             priority_data = self.runtime.predict_priority(clean_priority_text(request.task_title, request.description))
#         except ModelNotReady as exc:
#             warnings.append(f'Priority model unavailable: {exc}')

#         effort_data: dict[str, Any] | None = None
#         predict_effort = getattr(self.runtime, 'predict_effort', None)
#         if callable(predict_effort):
#             try:
#                 effort_data = predict_effort(clean_priority_text(request.task_title, request.description))
#             except ModelNotReady as exc:
#                 warnings.append(f'Effort model unavailable: {exc}')

#         # Duration precedence: user override > explicit text > calibrated effort model > planning block.
#         if (
#             effort_data
#             and request.duration_override_minutes is None
#             and temporal.get('duration_override_minutes') is None
#         ):
#             temporal['duration_override_minutes'] = effort_data['estimated_minutes']
#             temporal['duration_source'] = 'effort_model'
#             temporal['duration_text'] = f"calibrated {effort_data['estimated_minutes']} minute estimate"

#         predicted_slot = context_data['time_slots'][0]['label'] if context_data else None
#         deadline_proximity = calculate_deadline_proximity(temporal['deadline'], now, self.policy)
#         cue_strength = calculate_explicit_cue_strength(request.task_title, self.policy)
#         slot_recency = calculate_slot_recency(predicted_slot, now, self.policy)
#         urgency_score, is_urgent = calculate_urgency_score(deadline_proximity, cue_strength, slot_recency, self.policy)

#         importance = determine_importance(
#             request.importance,
#             priority_data['label'] if priority_data else None,
#             priority_data['probability'] if priority_data else None,
#         )
#         quadrant = 'Unresolved' if importance['important'] is None else assign_eisenhower_quadrant(is_urgent, importance['important'])

#         if context_data is None:
#             context = None
#         else:
#             context = ContextPrediction(
#                 input_text=context_data['input_text'],
#                 time_slots=[LabelProbability(**item) for item in context_data['time_slots']],
#                 location=LabelProbability(**context_data['location']),
#             )

#         if priority_data is None:
#             priority = PriorityPrediction(label=None, probability=None, probabilities=[], status='unavailable')
#         else:
#             priority = PriorityPrediction(
#                 label=priority_data['label'], probability=priority_data['probability'],
#                 probabilities=[LabelProbability(**item) for item in priority_data['probabilities']], status='ready',
#             )

#         if effort_data is None:
#             warnings.append('Effort model unavailable; scheduling falls back to explicit duration or a labelled 30-minute planning block.')
#             effort = {
#                 'status': 'not_available',
#                 'reason': 'No deployable effort candidate is registered in the manifest.',
#             }
#         else:
#             effort = dict(effort_data)
#             effort['effective_duration_minutes'] = temporal.get('duration_override_minutes')
#             if temporal.get('duration_source') == 'user_override':
#                 effort['source'] = 'user_override'
#                 effort['user_override_minutes'] = request.duration_override_minutes
#             elif temporal.get('duration_source') == 'explicit_duration':
#                 effort['source'] = 'explicit_duration'
#             else:
#                 effort['source'] = 'effort_model'
#             effort['disclaimer'] = 'Jira proxy estimate; review the range when planning personal tasks.'

#         return AnalysisResponse(
#             request=request,
#             context=context,
#             priority=priority,
#             temporal=TemporalOutput(**temporal),
#             urgency=UrgencyOutput(
#                 deadline_proximity=deadline_proximity,
#                 explicit_cue_strength=cue_strength,
#                 slot_recency=slot_recency,
#                 score=urgency_score,
#                 is_urgent=is_urgent,
#             ),
#             importance=ImportanceOutput(
#                 important=importance['important'], source=importance['importance_source'],
#                 model_priority=importance['model_b_priority'], model_confidence=importance['model_b_confidence'],
#                 disagreement=importance['disagreement'],
#             ),
#             quadrant=quadrant,
#             effort=effort,
#             schedule=[],
#             warnings=list(dict.fromkeys(warnings)),
#             model_versions={
#                 'context': self.manifest['models']['context']['base_model'],
#                 'priority': self.manifest['models']['priority']['base_model'],
#                 'effort': self.manifest['models']['effort']['base_model'],
#             },
#         )


from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .config import load_manifest, load_policy
from .models import ModelNotReady, ModelRuntime
from .rules import (
    assign_eisenhower_quadrant,
    calculate_deadline_proximity,
    calculate_explicit_cue_strength,
    calculate_slot_recency,
    calculate_urgency_score,
    determine_importance,
    parse_temporal_info,
)
from .schemas import (
    AnalysisResponse,
    ContextPrediction,
    ImportanceOutput,
    LabelProbability,
    PriorityPrediction,
    TaskAnalysisRequest,
    TemporalOutput,
    UrgencyOutput,
)


URL_PATTERN = re.compile(r'https?://\S+')

CODE_PATTERN = re.compile(
    r'\{\{code[^}]*\}\}.*?\{\{code\}\}|<code>.*?</code>',
    re.I | re.S,
)

LEAKAGE_PATTERN = re.compile(
    r'\b(blocker|critical|major|minor|trivial|urgent|asap)\b',
    re.I,
)


def clean_priority_text(
    task_title: str,
    description: str = '',
) -> str:
    """
    Clean task text before sending it to the priority/effort models.

    Model B was trained on cleaned Jira summary/description text.
    List context belongs only to Model A.
    """

    text = f'{task_title or ""} {description or ""}'

    text = CODE_PATTERN.sub(' ', text)

    text = URL_PATTERN.sub(' ', text)

    text = LEAKAGE_PATTERN.sub('[MASK]', text)

    return re.sub(r'\s+', ' ', text).strip()


class AnalysisService:
    def __init__(
        self,
        runtime: ModelRuntime | None = None,
    ):
        self.runtime = runtime or ModelRuntime()

        self.policy = load_policy()

        self.manifest = load_manifest()

    def analyze(
        self,
        request: TaskAnalysisRequest,
    ) -> AnalysisResponse:

        # ============================================================
        # CURRENT TIME
        # ============================================================
        #
        # This is used for urgency calculations and temporal parsing.
        #
        # IMPORTANT:
        # This does NOT determine the scheduler's start time.
        #
        now = (
            request.created_at
            or datetime.now(timezone.utc)
        )

        warnings: list[str] = []

        # ============================================================
        # TEMPORAL ANALYSIS
        # ============================================================
        #
        # This extracts things such as:
        #
        # - deadlines
        # - explicit durations
        # - temporal phrases
        #
        # It does NOT determine when the scheduler should start
        # the task.
        #

        temporal = parse_temporal_info(
            request.task_title,
            now,
        )

        # ============================================================
        # USER-PROVIDED DEADLINE
        # ============================================================
        #
        # A deadline entered by the user always overrides NLP
        # temporal extraction.
        #

        if request.deadline is not None:

            temporal['deadline'] = request.deadline

            temporal['deadline_text'] = (
                request.deadline.isoformat()
            )

            temporal['deadline_source'] = 'user'

            temporal['deadline_precision'] = 'timestamp'

        # ============================================================
        # USER-PROVIDED DURATION
        # ============================================================
        #
        # User duration has the highest precedence.
        #

        if request.duration_override_minutes is not None:

            temporal['duration_override_minutes'] = (
                request.duration_override_minutes
            )

            temporal['duration_source'] = (
                'user_override'
            )

            temporal['duration_text'] = (
                f'{request.duration_override_minutes} '
                'minute user override'
            )

        # ============================================================
        # CONTEXT MODEL
        # ============================================================

        context_data: dict[str, Any] | None = None

        try:

            context_data = (
                self.runtime.predict_context(
                    request.task_title,
                    request.list_title,
                )
            )

        except ModelNotReady as exc:

            warnings.append(
                f'Context model unavailable: {exc}'
            )

        # ============================================================
        # PRIORITY MODEL
        # ============================================================

        priority_data: dict[str, Any] | None = None

        try:

            priority_data = (
                self.runtime.predict_priority(
                    clean_priority_text(
                        request.task_title,
                        request.description,
                    )
                )
            )

        except ModelNotReady as exc:

            warnings.append(
                f'Priority model unavailable: {exc}'
            )

        # ============================================================
        # EFFORT MODEL
        # ============================================================

        effort_data: dict[str, Any] | None = None

        predict_effort = getattr(
            self.runtime,
            'predict_effort',
            None,
        )

        if callable(predict_effort):

            try:

                effort_data = predict_effort(
                    clean_priority_text(
                        request.task_title,
                        request.description,
                    )
                )

            except ModelNotReady as exc:

                warnings.append(
                    f'Effort model unavailable: {exc}'
                )

        # ============================================================
        # DURATION PRECEDENCE
        # ============================================================
        #
        # 1. User override
        # 2. Explicit duration extracted from text
        # 3. Effort model
        # 4. Scheduler fallback of 30 minutes
        #

        if (
            effort_data
            and request.duration_override_minutes is None
            and temporal.get(
                'duration_override_minutes'
            ) is None
        ):

            estimated_minutes = int(
                effort_data['estimated_minutes']
            )

            temporal[
                'duration_override_minutes'
            ] = estimated_minutes

            temporal[
                'duration_source'
            ] = 'effort_model'

            temporal[
                'duration_text'
            ] = (
                f'calibrated '
                f'{estimated_minutes} minute estimate'
            )

        # ============================================================
        # PREDICTED TIME SLOT
        # ============================================================

        predicted_slot = None

        if context_data:

            time_slots = context_data.get(
                'time_slots',
                [],
            )

            if time_slots:

                predicted_slot = (
                    time_slots[0]['label']
                )

        # ============================================================
        # URGENCY
        # ============================================================

        deadline_proximity = (
            calculate_deadline_proximity(
                temporal.get('deadline'),
                now,
                self.policy,
            )
        )

        cue_strength = (
            calculate_explicit_cue_strength(
                request.task_title,
                self.policy,
            )
        )

        slot_recency = (
            calculate_slot_recency(
                predicted_slot,
                now,
                self.policy,
            )
        )

        urgency_score, is_urgent = (
            calculate_urgency_score(
                deadline_proximity,
                cue_strength,
                slot_recency,
                self.policy,
            )
        )

        # ============================================================
        # IMPORTANCE
        # ============================================================

        importance = determine_importance(
            request.importance,
            (
                priority_data['label']
                if priority_data
                else None
            ),
            (
                priority_data['probability']
                if priority_data
                else None
            ),
        )

        # ============================================================
        # EISENHOWER QUADRANT
        # ============================================================

        quadrant = (
            'Unresolved'
            if importance['important'] is None
            else assign_eisenhower_quadrant(
                is_urgent,
                importance['important'],
            )
        )

        # ============================================================
        # CONTEXT RESPONSE
        # ============================================================

        if context_data is None:

            context = None

        else:

            context = ContextPrediction(
                input_text=context_data['input_text'],

                time_slots=[
                    LabelProbability(**item)
                    for item in context_data[
                        'time_slots'
                    ]
                ],

                location=LabelProbability(
                    **context_data['location']
                ),
            )

        # ============================================================
        # PRIORITY RESPONSE
        # ============================================================

        if priority_data is None:

            priority = PriorityPrediction(
                label=None,
                probability=None,
                probabilities=[],
                status='unavailable',
            )

        else:

            priority = PriorityPrediction(
                label=priority_data['label'],

                probability=(
                    priority_data['probability']
                ),

                probabilities=[
                    LabelProbability(**item)
                    for item in priority_data[
                        'probabilities'
                    ]
                ],

                status='ready',
            )

        # ============================================================
        # EFFORT RESPONSE
        # ============================================================

        if effort_data is None:

            warnings.append(
                'Effort model unavailable; scheduling '
                'falls back to explicit duration or a '
                'labelled 30-minute planning block.'
            )

            effort = {
                'status': 'not_available',

                'reason': (
                    'No deployable effort candidate '
                    'is registered in the manifest.'
                ),
            }

        else:

            effort = dict(effort_data)

            effort[
                'effective_duration_minutes'
            ] = temporal.get(
                'duration_override_minutes'
            )

            # --------------------------------------------
            # Identify actual duration source
            # --------------------------------------------

            if (
                request.duration_override_minutes
                is not None
            ):

                effort['source'] = (
                    'user_override'
                )

                effort[
                    'user_override_minutes'
                ] = (
                    request.duration_override_minutes
                )

            elif (
                temporal.get(
                    'duration_source'
                )
                == 'explicit_duration'
            ):

                effort['source'] = (
                    'explicit_duration'
                )

            else:

                effort['source'] = (
                    'effort_model'
                )

            effort['disclaimer'] = (
                'Jira proxy estimate; review the '
                'range when planning personal tasks.'
            )

        # ============================================================
        # FINAL ANALYSIS RESPONSE
        # ============================================================
        #
        # Notice:
        #
        # request.start_date is preserved inside request.
        #
        # The scheduler is responsible for deciding the actual
        # session start datetime.
        #
        # This service does NOT convert a deadline such as 05:00
        # into a scheduling start time.
        #

        return AnalysisResponse(
            request=request,

            context=context,

            priority=priority,

            temporal=TemporalOutput(
                **temporal
            ),

            urgency=UrgencyOutput(
                deadline_proximity=(
                    deadline_proximity
                ),

                explicit_cue_strength=(
                    cue_strength
                ),

                slot_recency=(
                    slot_recency
                ),

                score=urgency_score,

                is_urgent=is_urgent,
            ),

            importance=ImportanceOutput(
                important=importance[
                    'important'
                ],

                source=importance[
                    'importance_source'
                ],

                model_priority=importance[
                    'model_b_priority'
                ],

                model_confidence=importance[
                    'model_b_confidence'
                ],

                disagreement=importance[
                    'disagreement'
                ],
            ),

            quadrant=quadrant,

            effort=effort,

            # Analysis itself does not create sessions.
            # Scheduler creates them later.
            schedule=[],

            warnings=list(
                dict.fromkeys(warnings)
            ),

            model_versions={
                'context': (
                    self.manifest[
                        'models'
                    ]['context'][
                        'base_model'
                    ]
                ),

                'priority': (
                    self.manifest[
                        'models'
                    ]['priority'][
                        'base_model'
                    ]
                ),

                'effort': (
                    self.manifest[
                        'models'
                    ]['effort'][
                        'base_model'
                    ]
                ),
            },
        )