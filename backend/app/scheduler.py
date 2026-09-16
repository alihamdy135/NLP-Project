# from __future__ import annotations

# from datetime import datetime, time, timedelta, timezone
# from math import inf

# from .schemas import ScheduleRequest, ScheduleResponse, ScheduleSession
# from .service import AnalysisService
# from .rules import parse_temporal_info


# class Scheduler:
#     def __init__(self, analysis_service: AnalysisService):
#         self.analysis_service = analysis_service

#     @staticmethod
#     def _next_working_day(value: datetime) -> datetime:
#         value = value + timedelta(days=1)
#         while value.weekday() >= 5:
#             value += timedelta(days=1)
#         return value

#     def schedule(self, request: ScheduleRequest) -> ScheduleResponse:
#         start_date = request.start_date or datetime.now(timezone.utc)
#         if start_date.tzinfo is None:
#             start_date = start_date.replace(tzinfo=timezone.utc)
#         start_clock = datetime.strptime(request.preferred_start_time, '%H:%M').time()
#         horizon_days = {'day': 1, 'week': 5, 'month': 22, 'year': 260}[request.horizon]
#         daily_budget = int(request.available_hours_per_day * 60)

#         analyzed = []
#         warnings = [
#             'Duration precedence is user override, then explicit task duration, then calibrated effort model, then a labelled 30-minute planning block.',
#             'Jira priority and effort are transfer/proxy signals and do not establish personal importance.',
#         ]
#         for item in request.tasks:
#             result = self.analysis_service.analyze(item)
#             deadline = result.temporal.deadline
#             deadline_key = deadline.timestamp() if deadline else inf
#             analyzed.append((result, item, deadline_key))
#             warnings.extend(result.warnings)

#         analyzed.sort(key=lambda triple: (
#             not triple[0].urgency.is_urgent,
#             triple[0].importance.important is not True,
#             triple[2],
#         ))

#         sessions: list[ScheduleSession] = []
#         unscheduled: list[dict] = []
#         current_day = start_date.replace(hour=start_clock.hour, minute=start_clock.minute, second=0, microsecond=0)
#         day_index = 0
#         used_today = 0

#         for result, item, _ in analyzed:
#             duration = result.temporal.duration_override_minutes
#             source = result.temporal.duration_source
#             if not duration:
#                 duration = 30
#                 source = 'planning_block_default'

#             remaining = int(duration)
#             while remaining > 0:
#                 if day_index >= horizon_days:
#                     unscheduled.append({
#                         'task_title': item.task_title,
#                         'reason': f'{request.horizon} horizon is full',
#                         'remaining_minutes': remaining,
#                     })
#                     break
#                 if used_today >= daily_budget:
#                     current_day = self._next_working_day(current_day)
#                     day_index += 1
#                     used_today = 0
#                     continue

#                 chunk = min(remaining, daily_budget - used_today)
#                 session_start = current_day + timedelta(minutes=used_today)
#                 session_end = session_start + timedelta(minutes=chunk)
#                 deadline = result.temporal.deadline
#                 if deadline is None:
#                     deadline_status = 'no deadline'
#                 elif session_end <= deadline:
#                     deadline_status = 'within deadline'
#                 else:
#                     deadline_status = 'after deadline'
#                 context_label = result.context.location.label if result.context else None
#                 sessions.append(ScheduleSession(
#                     task_title=item.task_title,
#                     list_title=item.list_title,
#                     start=session_start,
#                     end=session_end,
#                     duration_minutes=chunk,
#                     duration_source=source,
#                     quadrant=result.quadrant,
#                     urgent=result.urgency.is_urgent,
#                     deadline=deadline,
#                     deadline_status=deadline_status,
#                     context_label=context_label,
#                 ))
#                 remaining -= chunk
#                 used_today += chunk
#                 if remaining > 0:
#                     current_day = self._next_working_day(current_day)
#                     day_index += 1
#                     used_today = 0

#         return ScheduleResponse(
#             horizon=request.horizon,
#             sessions=sessions,
#             unscheduled=unscheduled,
#             warnings=list(dict.fromkeys(warnings)),
#         )


from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from math import inf

from .schemas import ScheduleRequest, ScheduleResponse, ScheduleSession
from .service import AnalysisService

EGYPT_TZ = timezone(timedelta(hours=3))


class Scheduler:
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    @staticmethod
    def _make_datetime(
        value: date,
        start_time: time
    ) -> datetime:
        return datetime.combine(
            value,
            start_time,
            tzinfo=EGYPT_TZ
        )

    @staticmethod
    def _parse_time(
        value: str | None,
        fallback: time
    ) -> time:
        if not value:
            return fallback

        try:
            return datetime.strptime(
                value,
                "%H:%M"
            ).time()
        except ValueError:
            return fallback

    @staticmethod
    def _next_working_day(
        current: datetime,
        start_time: time
    ) -> datetime:
        next_day = current + timedelta(days=1)

        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)

        return next_day.replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0
        )

    @staticmethod
    def _move_to_working_day(
        current: datetime,
        start_time: time
    ) -> datetime:
        while current.weekday() >= 5:
            current += timedelta(days=1)

        return current.replace(
            hour=current.hour,
            minute=current.minute,
            second=0,
            microsecond=0
        )

    @staticmethod
    def _working_days_between(
        start: date,
        end: date
    ) -> int:
        if end <= start:
            return 0

        count = 0
        current = start

        while current < end:
            current += timedelta(days=1)

            if current.weekday() < 5:
                count += 1

        return count

    @staticmethod
    def _normalize_datetime(
        value: datetime | None
    ) -> datetime | None:
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(
                tzinfo=EGYPT_TZ
            )

        return value.astimezone(
            EGYPT_TZ
        )

    def schedule(
        self,
        request: ScheduleRequest
    ) -> ScheduleResponse:

        # ---------------------------------------------------------
        # 1. GLOBAL PLANNING SETTINGS
        # ---------------------------------------------------------

        if request.start_date is not None:
            planning_start_date = request.start_date
        else:
            planning_start_date = datetime.now(
                EGYPT_TZ
            ).date()

        global_start_time = datetime.strptime(
            request.preferred_start_time,
            "%H:%M"
        ).time()

        horizon_days = {
            "day": 1,
            "week": 5,
            "month": 22,
            "year": 260
        }[request.horizon]

        daily_budget = int(
            request.available_hours_per_day * 60
        )

        warnings = [
            "Duration precedence is user override, then explicit task duration, then calibrated effort model, then a labelled 30-minute planning block.",
            "Each task start time is treated as the earliest time that task can begin.",
            "Task deadlines are treated as completion cutoffs.",
            "Jira priority and effort are transfer/proxy signals and do not establish personal importance."
        ]

        # ---------------------------------------------------------
        # 2. ANALYZE ALL TASKS
        # ---------------------------------------------------------

        analyzed = []

        for task in request.tasks:

            result = self.analysis_service.analyze(
                task
            )

            deadline = self._normalize_datetime(
                result.temporal.deadline
            )

            deadline_key = (
                deadline.timestamp()
                if deadline is not None
                else inf
            )

            analyzed.append(
                {
                    "result": result,
                    "task": task,
                    "deadline_key": deadline_key
                }
            )

        # ---------------------------------------------------------
        # 3. SORT TASKS
        # ---------------------------------------------------------

        analyzed.sort(
            key=lambda item: (
                not item["result"].urgency.is_urgent,
                item["result"].importance.important is not True,
                item["deadline_key"]
            )
        )

        sessions: list[ScheduleSession] = []
        unscheduled: list[dict] = []

        # ---------------------------------------------------------
        # 4. INITIAL PLANNER POSITION
        # ---------------------------------------------------------

        current = self._make_datetime(
            planning_start_date,
            global_start_time
        )

        current = self._move_to_working_day(
            current,
            global_start_time
        )

        # ---------------------------------------------------------
        # 5. SCHEDULE TASKS
        # ---------------------------------------------------------

        for entry in analyzed:

            result = entry["result"]
            task = entry["task"]

            # -----------------------------------------------------
            # DURATION
            # -----------------------------------------------------

            duration = (
                result.temporal.duration_override_minutes
            )

            duration_source = (
                result.temporal.duration_source
            )

            if not duration:
                duration = 30
                duration_source = "planning_block_default"

            duration = int(duration)

            remaining = duration

            # -----------------------------------------------------
            # TASK START DATE
            # -----------------------------------------------------

            if task.start_date is not None:
                task_start_date = max(
                    planning_start_date,
                    task.start_date
                )
            else:
                task_start_date = planning_start_date

            # -----------------------------------------------------
            # TASK START TIME
            #
            # THIS IS THE IMPORTANT FIX.
            #
            # If the task says 12:00, it cannot be scheduled
            # before 12:00.
            # -----------------------------------------------------

            task_start_time = self._parse_time(
                getattr(
                    task,
                    "start_time",
                    None
                ),
                global_start_time
            )

            requested_task_start = self._make_datetime(
                task_start_date,
                task_start_time
            )

            # -----------------------------------------------------
            # MOVE WEEKEND TASKS TO MONDAY
            # -----------------------------------------------------

            if requested_task_start.weekday() >= 5:

                requested_task_start = (
                    self._move_to_working_day(
                        requested_task_start,
                        task_start_time
                    )
                )

            # -----------------------------------------------------
            # NEVER SCHEDULE BEFORE TASK START
            #
            # Example:
            #
            # Fajr -> 03:00
            # Gym  -> 12:00
            #
            # Gym will not be allowed at 03:30.
            # -----------------------------------------------------

            if current < requested_task_start:
                current = requested_task_start

            # -----------------------------------------------------
            # DEADLINE
            # -----------------------------------------------------

            deadline = self._normalize_datetime(
                result.temporal.deadline
            )

            # -----------------------------------------------------
            # SCHEDULE THE TASK
            # -----------------------------------------------------

            while remaining > 0:

                # -------------------------------------------------
                # HORIZON CHECK
                # -------------------------------------------------

                days_from_start = (
                    self._working_days_between(
                        planning_start_date,
                        current.date()
                    )
                )

                if days_from_start >= horizon_days:

                    unscheduled.append(
                        {
                            "task_title": task.task_title,
                            "reason": (
                                f"{request.horizon} "
                                "horizon is full"
                            ),
                            "remaining_minutes": remaining
                        }
                    )

                    break

                # -------------------------------------------------
                # MAKE SURE CURRENT DATE IS A WORKING DAY
                # -------------------------------------------------

                if current.weekday() >= 5:

                    current = self._next_working_day(
                        current,
                        global_start_time
                    )

                    continue

                # -------------------------------------------------
                # DAILY WORKING WINDOW
                #
                # Global planning start defines the beginning of
                # each normal working day.
                # -------------------------------------------------

                day_start = self._make_datetime(
                    current.date(),
                    global_start_time
                )

                day_end = (
                    day_start
                    + timedelta(
                        minutes=daily_budget
                    )
                )

                # -------------------------------------------------
                # IF CURRENT IS BEFORE TODAY'S WORK WINDOW
                # -------------------------------------------------

                if current < day_start:
                    current = day_start

                # -------------------------------------------------
                # IF CURRENT IS AFTER TODAY'S WORK WINDOW
                # -------------------------------------------------

                if current >= day_end:

                    current = self._next_working_day(
                        current,
                        global_start_time
                    )

                    continue

                # -------------------------------------------------
                # FIRST DAY TASK START TIME
                #
                # If Gym starts at 12:00, current becomes 12:00.
                #
                # We only need this protection when the current
                # position is still before the requested start.
                # -------------------------------------------------

                if (
                    current.date()
                    == requested_task_start.date()
                    and current < requested_task_start
                ):
                    current = requested_task_start

                    if current >= day_end:

                        current = self._next_working_day(
                            current,
                            global_start_time
                        )

                        continue

                # -------------------------------------------------
                # AVAILABLE TIME TODAY
                # -------------------------------------------------

                available_today = int(
                    (
                        day_end - current
                    ).total_seconds() // 60
                )

                if available_today <= 0:

                    current = self._next_working_day(
                        current,
                        global_start_time
                    )

                    continue

                # -------------------------------------------------
                # CHUNK SIZE
                # -------------------------------------------------

                chunk = min(
                    remaining,
                    available_today
                )

                session_start = current

                session_end = (
                    session_start
                    + timedelta(
                        minutes=chunk
                    )
                )

                # -------------------------------------------------
                # DEADLINE CHECK
                # -------------------------------------------------

                if deadline is not None:

                    if session_start >= deadline:

                        unscheduled.append(
                            {
                                "task_title": task.task_title,
                                "reason": "deadline passed",
                                "remaining_minutes": remaining,
                                "deadline": deadline.isoformat()
                            }
                        )

                        break

                    if session_end > deadline:

                        minutes_until_deadline = int(
                            (
                                deadline
                                - session_start
                            ).total_seconds()
                            // 60
                        )

                        if minutes_until_deadline <= 0:

                            unscheduled.append(
                                {
                                    "task_title": task.task_title,
                                    "reason": (
                                        "no available time "
                                        "before deadline"
                                    ),
                                    "remaining_minutes": remaining,
                                    "deadline": deadline.isoformat()
                                }
                            )

                            break

                        chunk = min(
                            chunk,
                            minutes_until_deadline
                        )

                        session_end = (
                            session_start
                            + timedelta(
                                minutes=chunk
                            )
                        )

                # -------------------------------------------------
                # DEADLINE STATUS
                # -------------------------------------------------

                if deadline is None:

                    deadline_status = "no deadline"

                elif session_end <= deadline:

                    deadline_status = "within deadline"

                else:

                    deadline_status = "after deadline"

                # -------------------------------------------------
                # CONTEXT LABEL
                # -------------------------------------------------

                context_label = None

                if result.context is not None:

                    context_label = (
                        result.context
                        .location
                        .label
                    )

                # -------------------------------------------------
                # CREATE SESSION
                # -------------------------------------------------

                session = ScheduleSession(
                    task_title=task.task_title,
                    list_title=task.list_title,
                    start=session_start,
                    end=session_end,
                    duration_minutes=chunk,
                    duration_source=duration_source,
                    quadrant=result.quadrant,
                    urgent=result.urgency.is_urgent,
                    deadline=deadline,
                    deadline_status=deadline_status,
                    context_label=context_label,
                    start_date=task.start_date
                )

                sessions.append(
                    session
                )

                # -------------------------------------------------
                # UPDATE REMAINING TIME
                # -------------------------------------------------

                remaining -= chunk

                current = session_end

                # -------------------------------------------------
                # IF TASK IS FINISHED
                # -------------------------------------------------

                if remaining <= 0:
                    break

                # -------------------------------------------------
                # TASK CONTINUES TO ANOTHER DAY
                # -------------------------------------------------

                current = self._next_working_day(
                    current,
                    global_start_time
                )

            # -----------------------------------------------------
            # NEXT TASK
            #
            # current remains at the end of the previous session.
            # The next task's own start_time is checked again at
            # the beginning of the next iteration.
            # -----------------------------------------------------

        # ---------------------------------------------------------
        # 6. RETURN RESULT
        # ---------------------------------------------------------

        return ScheduleResponse(
            horizon=request.horizon,
            sessions=sessions,
            unscheduled=unscheduled,
            warnings=list(
                dict.fromkeys(warnings)
            )
        )