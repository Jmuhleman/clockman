from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.config.settings import SESSION_LABELS
from app.models.entries import SessionComputed, SessionInput, TimesheetRow
from app.services.allocation_service import allocate_time
from app.services.time_calculator import compute_daily_total, compute_session_duration


def build_timesheet_rows(
    entry_date: date,
    sessions: dict[str, SessionInput],
    decimal_places: int,
) -> tuple[list[TimesheetRow], dict[str, SessionComputed], Decimal]:
    computed_sessions: dict[str, SessionComputed] = {}
    durations: list[Decimal] = []

    for key, label in SESSION_LABELS.items():
        session = sessions.get(key, SessionInput(check_in=None, check_out=None, projects=[]))
        duration = compute_session_duration(session.check_in, session.check_out, decimal_places, entry_date)
        allocations = allocate_time(duration, session.projects, decimal_places) if duration else []
        computed_sessions[key] = SessionComputed(
            session_label=label,
            check_in=session.check_in,
            check_out=session.check_out,
            duration_hours=duration,
            allocations=allocations,
        )
        if duration is not None:
            durations.append(duration)

    daily_total = compute_daily_total(durations, decimal_places)

    rows: list[TimesheetRow] = []
    for computed in computed_sessions.values():
        if not computed.duration_hours or not computed.allocations:
            continue
        for allocation in computed.allocations:
            rows.append(
                TimesheetRow(
                    date=entry_date,
                    session=computed.session_label,
                    check_in=computed.check_in,
                    check_out=computed.check_out,
                    session_duration=computed.duration_hours,
                    project_number=allocation.project_number,
                    allocated_time=allocation.allocated_hours,
                    daily_total=daily_total,
                )
            )

    return rows, computed_sessions, daily_total
