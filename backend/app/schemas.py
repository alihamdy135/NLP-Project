# from __future__ import annotations

# from datetime import datetime
# from typing import Any, Literal

# from pydantic import BaseModel, ConfigDict, Field, field_validator


# class TaskAnalysisRequest(BaseModel):
#     model_config = ConfigDict(str_strip_whitespace=True)

#     task_title: str = Field(min_length=1, max_length=500)
#     list_title: str = Field(default='general', max_length=200)
#     description: str = Field(default='', max_length=5000)
#     importance: bool | None = None
#     deadline: datetime | None = None
#     duration_override_minutes: int | None = Field(default=None, ge=1, le=1440)
#     created_at: datetime | None = None

#     @field_validator('task_title')
#     @classmethod
#     def non_blank_task(cls, value: str) -> str:
#         if not value.strip():
#             raise ValueError('task_title must not be blank')
#         return value


# class LabelProbability(BaseModel):
#     label: str
#     probability: float = Field(ge=0.0, le=1.0)


# class ContextPrediction(BaseModel):
#     time_slots: list[LabelProbability]
#     location: LabelProbability
#     input_text: str


# class PriorityPrediction(BaseModel):
#     label: str | None
#     probability: float | None = Field(default=None, ge=0.0, le=1.0)
#     probabilities: list[LabelProbability] = Field(default_factory=list)
#     status: str


# class TemporalOutput(BaseModel):
#     deadline: datetime | None
#     duration_override_minutes: int | None
#     deadline_text: str | None
#     duration_text: str | None
#     deadline_source: str
#     duration_source: str
#     deadline_precision: str | None


# class UrgencyOutput(BaseModel):
#     deadline_proximity: float = Field(ge=0.0, le=1.0)
#     explicit_cue_strength: float = Field(ge=0.0, le=1.0)
#     slot_recency: float = Field(ge=0.0, le=1.0)
#     score: float = Field(ge=0.0, le=1.0)
#     is_urgent: bool


# class ImportanceOutput(BaseModel):
#     important: bool | None
#     source: str
#     model_priority: str | None
#     model_confidence: float | None
#     disagreement: bool


# class AnalysisResponse(BaseModel):
#     request: TaskAnalysisRequest
#     context: ContextPrediction | None
#     priority: PriorityPrediction
#     temporal: TemporalOutput
#     urgency: UrgencyOutput
#     importance: ImportanceOutput
#     quadrant: str
#     effort: dict[str, Any]
#     schedule: list[dict[str, Any]]
#     warnings: list[str]
#     model_versions: dict[str, str]


# class ScheduleRequest(BaseModel):
#     tasks: list[TaskAnalysisRequest] = Field(min_length=1, max_length=100)
#     horizon: Literal['day', 'week', 'month', 'year'] = 'week'
#     available_hours_per_day: float = Field(default=4.0, gt=0, le=24)
#     preferred_start_time: str = Field(default='09:00', pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
#     start_date: datetime | None = None


# class ScheduleSession(BaseModel):
#     task_title: str
#     list_title: str
#     start: datetime
#     end: datetime
#     duration_minutes: int
#     duration_source: str
#     quadrant: str
#     urgent: bool
#     deadline: datetime | None
#     deadline_status: str
#     context_label: str | None


# class ScheduleResponse(BaseModel):
#     horizon: str
#     sessions: list[ScheduleSession]
#     unscheduled: list[dict[str, Any]]
#     warnings: list[str]


from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    task_title: str = Field(
        min_length=1,
        max_length=500
    )

    list_title: str = Field(
        default='general',
        max_length=200
    )

    description: str = Field(
        default='',
        max_length=5000
    )

    importance: bool | None = None

    deadline: datetime | None = None

    start_date: date | None = None

    start_time: str | None = Field(
        default=None,
        pattern=r'^([01]\d|2[0-3]):[0-5]\d$'
    )

    duration_override_minutes: int | None = Field(
        default=None,
        ge=1,
        le=1440
    )

    created_at: datetime | None = None

    @field_validator('task_title')
    @classmethod
    def non_blank_task(
        cls,
        value: str
    ) -> str:
        if not value.strip():
            raise ValueError(
                'task_title must not be blank'
            )

        return value


class LabelProbability(BaseModel):
    label: str

    probability: float = Field(
        ge=0.0,
        le=1.0
    )


class ContextPrediction(BaseModel):
    time_slots: list[LabelProbability]

    location: LabelProbability

    input_text: str


class PriorityPrediction(BaseModel):
    label: str | None

    probability: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0
    )

    probabilities: list[LabelProbability] = Field(
        default_factory=list
    )

    status: str


class TemporalOutput(BaseModel):
    deadline: datetime | None

    duration_override_minutes: int | None

    deadline_text: str | None

    duration_text: str | None

    deadline_source: str

    duration_source: str

    deadline_precision: str | None


class UrgencyOutput(BaseModel):
    deadline_proximity: float = Field(
        ge=0.0,
        le=1.0
    )

    explicit_cue_strength: float = Field(
        ge=0.0,
        le=1.0
    )

    slot_recency: float = Field(
        ge=0.0,
        le=1.0
    )

    score: float = Field(
        ge=0.0,
        le=1.0
    )

    is_urgent: bool


class ImportanceOutput(BaseModel):
    important: bool | None

    source: str

    model_priority: str | None

    model_confidence: float | None

    disagreement: bool


class AnalysisResponse(BaseModel):
    request: TaskAnalysisRequest

    context: ContextPrediction | None

    priority: PriorityPrediction

    temporal: TemporalOutput

    urgency: UrgencyOutput

    importance: ImportanceOutput

    quadrant: str

    effort: dict[str, Any]

    schedule: list[dict[str, Any]]

    warnings: list[str]

    model_versions: dict[str, str]


class ScheduleRequest(BaseModel):
    tasks: list[TaskAnalysisRequest] = Field(
        min_length=1,
        max_length=100
    )

    horizon: Literal[
        'day',
        'week',
        'month',
        'year'
    ] = 'week'

    available_hours_per_day: float = Field(
        default=4.0,
        gt=0,
        le=24
    )

    preferred_start_time: str = Field(
        default='09:00',
        pattern=r'^([01]\d|2[0-3]):[0-5]\d$'
    )

    start_date: date | None = None


class ScheduleSession(BaseModel):
    task_title: str

    list_title: str

    start: datetime

    end: datetime

    duration_minutes: int

    duration_source: str

    quadrant: str

    urgent: bool

    deadline: datetime | None

    deadline_status: str

    context_label: str | None

    start_date: date | None = None


class ScheduleResponse(BaseModel):
    horizon: str

    sessions: list[ScheduleSession]

    unscheduled: list[dict[str, Any]]

    warnings: list[str]