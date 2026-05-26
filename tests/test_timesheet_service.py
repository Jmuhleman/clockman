from datetime import date, time
from decimal import Decimal

from app.models.entries import SessionInput
from app.services.timesheet_service import build_timesheet_rows


def test_build_timesheet_rows_allocates_per_project() -> None:
    sessions = {
        "morning": SessionInput(
            check_in=time(8, 0),
            check_out=time(12, 0),
            projects=["PRJ-1", "PRJ-2"],
        ),
        "afternoon": SessionInput(
            check_in=None,
            check_out=None,
            projects=[],
        ),
    }
    rows, _, daily_total = build_timesheet_rows(date(2025, 1, 1), sessions, 2)
    assert len(rows) == 2
    assert daily_total == Decimal("4.00")
