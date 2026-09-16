from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from math import inf

from .schemas import ScheduleRequest, ScheduleResponse, ScheduleSession
from .service import AnalysisService
from .rules import parse_temporal_info


class Scheduler:
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    @staticmethod
    def _next_working_day(value: datetime) -> datetime:
        value = value + timedelta(days=1)
        while value.weekday() >= 5:
            value += timedelta(days=1)
        return value

    def schedule(self, request: ScheduleRequest) -> ScheduleResponse:
        start_date = request.start_date or datetime.now(timezone.utc)
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        start_clock = datetime.strptime(request.preferred_start_time, '%H:%M').time()
        horizon_days = {'day': 1, 'week': 5, 'month': 22, 'year': 260}[request.horizon]
        daily_budget = int(request.available_hours_per_day * 60)

        analyzed = []
        warnings = [
            'Duration precedence is user override, then explicit task duration, then calibrated effort model, then a labelled 30-minute planning block.',
            'Jira priority and effort are transfer/proxy signals and do not establish personal importance.',
        ]
        for item in request.tasks:
            result = self.analysis_service.analyze(item)
            deadline = result.temporal.deadline
            deadline_key = deadline.timestamp() if deadline else inf
            analyzed.append((result, item, deadline_key))
            warnings.extend(result.warnings)

        analyzed.sort(key=lambda triple: (
            not triple[0].urgency.is_urgent,
            triple[0].importance.important is not True,
            triple[2],
        ))

        sessions: list[ScheduleSession] = []
        unscheduled: list[dict] = []
        current_day = start_date.replace(hour=start_clock.hour, minute=start_clock.minute, second=0, microsecond=0)
        day_index = 0
        used_today = 0

        for result, item, _ in analyzed:
            duration = result.temporal.duration_override_minutes
            source = result.temporal.duration_source
            if not duration:
                duration = 30
                source = 'planning_block_default'

            remaining = int(duration)
            while remaining > 0:
                if day_index >= horizon_days:
                    unscheduled.append({
                        'task_title': item.task_title,
                        'reason': f'{request.horizon} horizon is full',
                        'remaining_minutes': remaining,
                    })
                    break
                if used_today >= daily_budget:
                    current_day = self._next_working_day(current_day)
                    day_index += 1
                    used_today = 0
                    continue

                chunk = min(remaining, daily_budget - used_today)
                session_start = current_day + timedelta(minutes=used_today)
                session_end = session_start + timedelta(minutes=chunk)
                deadline = result.temporal.deadline
                if deadline is None:
                    deadline_status = 'no deadline'
                elif session_end <= deadline:
                    deadline_status = 'within deadline'
                else:
                    deadline_status = 'after deadline'
                context_label = result.context.location.label if result.context else None
                sessions.append(ScheduleSession(
                    task_title=item.task_title,
                    list_title=item.list_title,
                    start=session_start,
                    end=session_end,
                    duration_minutes=chunk,
                    duration_source=source,
                    quadrant=result.quadrant,
                    urgent=result.urgency.is_urgent,
                    deadline=deadline,
                    deadline_status=deadline_status,
                    context_label=context_label,
                ))
                remaining -= chunk
                used_today += chunk
                if remaining > 0:
                    current_day = self._next_working_day(current_day)
                    day_index += 1
                    used_today = 0

        return ScheduleResponse(
            horizon=request.horizon,
            sessions=sessions,
            unscheduled=unscheduled,
            warnings=list(dict.fromkeys(warnings)),
        )
