from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any


def _localize(value: datetime, reference: datetime) -> datetime:
    if reference.tzinfo is not None and value.tzinfo is None:
        return value.replace(tzinfo=reference.tzinfo)
    return value


def _next_weekday(reference: datetime, target: int) -> datetime:
    delta = (target - reference.weekday()) % 7
    if delta == 0:
        delta = 7
    return (reference + timedelta(days=delta)).replace(hour=23, minute=59, second=59, microsecond=0)


def parse_temporal_info(task_text: str, task_datetime: datetime) -> dict[str, Any]:
    """Extract only explicit dates and durations; never infer missing values."""
    text = str(task_text or '').lower().strip()
    result: dict[str, Any] = {
        'deadline': None,
        'duration_override_minutes': None,
        'deadline_text': None,
        'duration_text': None,
        'deadline_source': 'none',
        'duration_source': 'none',
        'deadline_precision': None,
    }

    duration_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|days?)\b', text)
    if duration_match:
        value = float(duration_match.group(1))
        unit = duration_match.group(2)
        multiplier = 1 if unit.startswith(('minute', 'min')) else 60 if unit.startswith(('hour', 'hr')) else 1440
        result['duration_override_minutes'] = int(value * multiplier)
        result['duration_text'] = duration_match.group(0)
        result['duration_source'] = 'explicit_duration'

    iso = re.search(r'\b\d{4}-\d{1,2}-\d{1,2}\b', text)
    if iso:
        parsed = datetime.fromisoformat(iso.group(0))
        result.update(deadline=_localize(parsed, task_datetime), deadline_text=iso.group(0),
                      deadline_source='explicit_temporal_cue', deadline_precision='day')
        return result

    if re.search(r'\bby\s+end\s+of\s+(?:the\s+)?week\b', text):
        days_until_sunday = 6 - task_datetime.weekday()
        parsed = task_datetime + timedelta(days=days_until_sunday)
        result.update(deadline=parsed.replace(hour=23, minute=59, second=59, microsecond=0),
                      deadline_text='by end of week', deadline_source='explicit_temporal_cue', deadline_precision='week')
        return result

    if re.search(r'\bnext\s+week\b', text):
        parsed = task_datetime + timedelta(days=7 - task_datetime.weekday())
        result.update(deadline=parsed.replace(hour=23, minute=59, second=59, microsecond=0),
                      deadline_text='next week', deadline_source='explicit_temporal_cue', deadline_precision='week')
        return result

    relative = [('today', 0), ('tonight', 0), ('tomorrow', 1)]
    for cue, days in relative:
        if re.search(rf'\b{cue}\b', text):
            parsed = task_datetime + timedelta(days=days)
            if cue == 'tonight':
                parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=0)
            result.update(deadline=parsed, deadline_text=cue, deadline_source='explicit_temporal_cue', deadline_precision='day')
            return result

    weekdays = {name: index for index, name in enumerate(
        ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
    )}
    weekday_match = re.search(r'\b(?:next\s+)?(?:on\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text)
    if weekday_match:
        parsed = _next_weekday(task_datetime, weekdays[weekday_match.group(1)])
        result.update(deadline=parsed, deadline_text=weekday_match.group(0), deadline_source='explicit_temporal_cue', deadline_precision='day')
    return result


def calculate_deadline_proximity(deadline: datetime | None, current_datetime: datetime, policy: dict) -> float:
    if deadline is None:
        return 0.0
    if deadline.tzinfo is None and current_datetime.tzinfo is not None:
        deadline = deadline.replace(tzinfo=current_datetime.tzinfo)
    hours_remaining = (deadline - current_datetime).total_seconds() / 3600
    config = policy['deadline_proximity']
    if hours_remaining <= 24:
        return float(config['overdue_or_within_24h'])
    decay_hours = float(config['decay_days']) * 24
    if hours_remaining >= decay_hours:
        return 0.0
    return max(0.0, min(1.0, 1 - ((hours_remaining - 24) / (decay_hours - 24))))


def calculate_explicit_cue_strength(task_text: str, policy: dict) -> float:
    text = str(task_text or '').lower()
    high = policy['explicit_cue_strength']['high']
    if any(re.search(rf'\b{re.escape(cue)}\b', text) for cue in high['cues']):
        return float(high['score'])
    medium = policy['explicit_cue_strength']['medium']
    if any(cue in text for cue in medium['cues']):
        return float(medium['score'])
    return float(policy['explicit_cue_strength']['none']['score'])


def calculate_urgency_score(deadline_proximity: float, explicit_cue_strength: float, slot_recency: float, policy: dict) -> tuple[float, bool]:
    weights = policy['weights']
    score = (
        weights['deadline_proximity'] * deadline_proximity
        + weights['explicit_cue_strength'] * explicit_cue_strength
        + weights['slot_recency'] * slot_recency
    )
    return float(score), bool(score >= policy['urgent_threshold'])


def determine_importance(user_importance: bool | None, model_b_priority: str | None = None, model_b_confidence: float | None = None) -> dict[str, Any]:
    suggestion = True if model_b_priority in ('Blocker', 'Critical') else False if model_b_priority in ('Minor', 'Trivial') else None
    disagreement = suggestion is not None and user_importance is not None and suggestion != user_importance
    if user_importance is not None:
        return {'important': user_importance, 'importance_source': 'user', 'model_b_priority': model_b_priority,
                'model_b_confidence': model_b_confidence, 'disagreement': disagreement}
    return {'important': suggestion, 'importance_source': 'model_b' if suggestion is not None else 'neutral',
            'model_b_priority': model_b_priority, 'model_b_confidence': model_b_confidence, 'disagreement': False}


def assign_eisenhower_quadrant(urgent: bool, important: bool) -> str:
    if urgent and important:
        return 'Q1 - Do now'
    if important:
        return 'Q2 - Schedule'
    if urgent:
        return 'Q3 - Delegate/Batch'
    return 'Q4 - Defer/Drop'


def current_horizon(current_datetime: datetime) -> list[str]:
    prefix = 'WD' if current_datetime.weekday() < 5 else 'WE'
    period = 'morning' if current_datetime.hour < 12 else 'afternoon' if current_datetime.hour < 17 else 'evening' if current_datetime.hour < 21 else 'night'
    periods = ['morning', 'afternoon', 'evening', 'night', 'anytime']
    return [f'{prefix}-{item}' for item in periods[periods.index(period):]]


def calculate_slot_recency(predicted_slot: str | None, current_datetime: datetime, policy: dict) -> float:
    if predicted_slot and predicted_slot in current_horizon(current_datetime):
        return float(policy['slot_recency']['top_slot_current_horizon'])
    return float(policy['slot_recency']['outside_horizon'])


def normalize_task_title(title: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', '', str(title).lower())).strip()
