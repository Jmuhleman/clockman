from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from app.models.entries import SessionInput
from app.utils.time_utils import parse_time_str


@dataclass(frozen=True)
class SessionValidation:
    data: SessionInput
    errors: list[str]
    time_valid: bool


@dataclass(frozen=True)
class DailyValidation:
    date: date
    sessions: dict[str, SessionValidation]
    errors: list[str]


def _clean_projects(projects: list[str]) -> list[str]:
    cleaned: list[str] = []
    for project in projects:
        if project is None:
            continue
        trimmed = project.strip()
        if trimmed:
            cleaned.append(trimmed)
    return cleaned


def _find_duplicate_projects(projects: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for project in projects:
        normalized = project.lower()
        if normalized in seen and project not in duplicates:
            duplicates.append(project)
        else:
            seen.add(normalized)
    return duplicates


def validate_session(
    session_label: str,
    check_in_str: Optional[str],
    check_out_str: Optional[str],
    projects: list[str],
    time_format: str,
) -> SessionValidation:
    errors: list[str] = []
    time_errors: list[str] = []

    check_in, check_in_error = parse_time_str(check_in_str, time_format)
    if check_in_error:
        time_errors.append(check_in_error)

    check_out, check_out_error = parse_time_str(check_out_str, time_format)
    if check_out_error:
        time_errors.append(check_out_error)

    if time_errors:
        errors.extend(time_errors)

    if (check_in and not check_out) or (check_out and not check_in):
        errors.append("Both check-in and check-out are required.")

    if check_in and check_out:
        if check_out <= check_in:
            errors.append("Check-out must be after check-in (overnight sessions not supported).")

    cleaned_projects = _clean_projects(projects)
    duplicates = _find_duplicate_projects(cleaned_projects)
    if duplicates:
        errors.append(f"Duplicate project numbers: {', '.join(sorted(duplicates))}.")

    if check_in and check_out and not cleaned_projects:
        errors.append("At least one project number is required.")

    time_valid = not time_errors and not (
        check_in and check_out and check_out <= check_in
    )

    return SessionValidation(
        data=SessionInput(check_in=check_in, check_out=check_out, projects=cleaned_projects),
        errors=errors,
        time_valid=time_valid,
    )


def validate_daily_inputs(
    entry_date: date,
    morning_in: Optional[str],
    morning_out: Optional[str],
    morning_projects: list[str],
    afternoon_in: Optional[str],
    afternoon_out: Optional[str],
    afternoon_projects: list[str],
    time_format: str,
) -> DailyValidation:
    morning = validate_session("Morning", morning_in, morning_out, morning_projects, time_format)
    afternoon = validate_session("Afternoon", afternoon_in, afternoon_out, afternoon_projects, time_format)

    errors: list[str] = []
    errors.extend(morning.errors)
    errors.extend(afternoon.errors)

    if morning.data.check_out and afternoon.data.check_in:
        if morning.data.check_out >= afternoon.data.check_in:
            errors.append("Morning session must finish before afternoon session starts.")

    return DailyValidation(
        date=entry_date,
        sessions={"morning": morning, "afternoon": afternoon},
        errors=errors,
    )
