from datetime import date, time
from decimal import Decimal

import pandas as pd

from app.config.settings import TIMESHEET_COLUMNS
from app.database import supabase_client
from app.models.entries import TimesheetRow
from app.services.timesheet_persistence import append_timesheet_rows, load_timesheets, write_timesheets
from tests.helpers.fake_supabase import FakeSupabase


def _sample_row() -> TimesheetRow:
    return TimesheetRow(
        date=date(2025, 1, 1),
        session="Morning",
        check_in=time(8, 0),
        check_out=time(12, 0),
        session_duration=Decimal("4.00"),
        project_number="PRJ-100",
        allocated_time=Decimal("4.00"),
        daily_total=Decimal("4.00"),
    )


def test_append_timesheet_rows_inserts(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_timesheets.clear()
    append_timesheet_rows([_sample_row()])
    df = load_timesheets()
    assert len(df) == 1


def test_load_timesheets_empty(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_timesheets.clear()
    df = load_timesheets()
    assert df.empty


def test_write_timesheets_replaces(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_timesheets.clear()
    append_timesheet_rows([_sample_row()])
    df = load_timesheets()
    df["Project Number"] = ["PRJ-200"]
    write_timesheets(df, backup=True)
    updated = load_timesheets()
    assert updated["Project Number"].iloc[0] == "PRJ-200"


def test_write_timesheets_allows_empty(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_timesheets.clear()
    empty_df = pd.DataFrame(columns=TIMESHEET_COLUMNS)
    write_timesheets(empty_df, backup=False)
    df = load_timesheets()
    assert df.empty
