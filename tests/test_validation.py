from datetime import date

from app.config.settings import TIME_FORMAT
from app.validators.timesheet_validator import validate_daily_inputs, validate_session


def test_validate_session_missing_checkout() -> None:
    validation = validate_session(
        "Morning session", "08:00", "", ["PRJ-100"], TIME_FORMAT
    )
    assert any("Both check-in and check-out" in error for error in validation.errors)


def test_validate_session_duplicate_projects() -> None:
    validation = validate_session(
        "Morning session", "08:00", "12:00", ["PRJ-1", "prj-1"], TIME_FORMAT
    )
    assert any("Duplicate project numbers" in error for error in validation.errors)


def test_validate_daily_ordering() -> None:
    validation = validate_daily_inputs(
        date(2025, 1, 1),
        "08:00",
        "12:00",
        ["PRJ-1"],
        "11:00",
        "16:00",
        ["PRJ-2"],
        TIME_FORMAT,
    )
    assert any("Morning session must finish" in error for error in validation.errors)


def test_validate_daily_valid_input() -> None:
    validation = validate_daily_inputs(
        date(2025, 1, 1),
        "08:00",
        "12:00",
        ["PRJ-1"],
        "13:00",
        "17:30",
        ["PRJ-2"],
        TIME_FORMAT,
    )
    assert validation.errors == []
