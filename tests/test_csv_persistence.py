from datetime import date, time
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.csv_persistence import append_timesheet_rows, load_timesheets, write_timesheets
from app.models.entries import TimesheetRow


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


def test_append_timesheet_rows_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "timesheets.csv"
    append_timesheet_rows(path, [_sample_row()])
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Date,Session,Check-in" in content


def test_append_timesheet_rows_schema_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "timesheets.csv"
    path.write_text("Bad,Header\n", encoding="utf-8")
    with pytest.raises(ValueError):
        append_timesheet_rows(path, [_sample_row()])


def test_load_timesheets_empty(tmp_path: Path) -> None:
    path = tmp_path / "timesheets.csv"
    append_timesheet_rows(path, [_sample_row()])
    df = load_timesheets(path)
    assert not df.empty


def test_write_timesheets_creates_backup(tmp_path: Path) -> None:
    path = tmp_path / "timesheets.csv"
    append_timesheet_rows(path, [_sample_row()])
    df = load_timesheets(path)
    write_timesheets(path, df, backup=True)
    backups = list(tmp_path.glob("timesheets.bak.*"))
    assert backups


def test_write_timesheets_allows_empty(tmp_path: Path) -> None:
    path = tmp_path / "timesheets.csv"
    df = load_timesheets(path)
    write_timesheets(path, df, backup=False)
    content = path.read_text(encoding="utf-8")
    assert "Date,Session,Check-in" in content
