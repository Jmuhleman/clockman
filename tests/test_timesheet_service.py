from datetime import date, time
from decimal import Decimal

from app.models.entries import SessionInput
import pandas as pd

from app.services.timesheet_service import build_timesheet_rows, build_timesheet_rows_from_allocations


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


def test_build_timesheet_rows_from_allocations() -> None:
    sessions = {
        "morning": SessionInput(
            check_in=time(8, 0),
            check_out=time(12, 0),
            projects=["PRJ-1"],
        ),
        "afternoon": SessionInput(
            check_in=None,
            check_out=None,
            projects=[],
        ),
    }
    allocations = pd.DataFrame(
        {
            "Session": ["Morning"],
            "Project Number": ["PRJ-1"],
            "Allocated Time": [4.0],
        }
    )
    rows = build_timesheet_rows_from_allocations(
        date(2025, 1, 1),
        allocations,
        sessions,
        {"Morning": Decimal("4.00")},
        Decimal("4.00"),
    )
    assert len(rows) == 1
