from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

import pandas as pd

from app.config.settings import DECIMAL_PLACES, SESSION_LABELS, TIME_FORMAT, TIMESHEET_COLUMNS
from app.services.time_calculator import compute_session_duration
from app.utils.time_utils import parse_time_str, round_hours


@dataclass(frozen=True)
class ValidationResult:
    cleaned: pd.DataFrame
    errors: list[str]


def _parse_date(value: object) -> tuple[Optional[date], Optional[str]]:
    if value is None or pd.isna(value):
        return None, "Date is required."
    try:
        parsed = pd.to_datetime(value).date()
        return parsed, None
    except (ValueError, TypeError):
        return None, f"Invalid date value: {value}."


def _parse_time(value: object) -> tuple[Optional[str], Optional[str]]:
    if value is None or pd.isna(value):
        return None, None
    text = str(value).strip()
    if not text:
        return None, None
    parsed, error = parse_time_str(text, TIME_FORMAT)
    if error:
        return None, error
    return parsed.strftime(TIME_FORMAT), None


def validate_and_prepare_edits(df: pd.DataFrame) -> ValidationResult:
    errors: list[str] = []
    missing = [col for col in TIMESHEET_COLUMNS if col not in df.columns]
    if missing:
        return ValidationResult(df, ["Missing columns: " + ", ".join(missing)])
    if df.empty:
        return ValidationResult(df[TIMESHEET_COLUMNS].copy(), [])

    working = df[TIMESHEET_COLUMNS].copy()
    working = working.fillna("")

    valid_sessions = set(SESSION_LABELS.values())
    cleaned_dates: list[str] = []
    cleaned_check_in: list[str] = []
    cleaned_check_out: list[str] = []
    computed_durations: list[Optional[Decimal]] = []

    for idx, row in working.iterrows():
        parsed_date, date_error = _parse_date(row["Date"])
        if date_error:
            errors.append(f"Row {idx + 1}: {date_error}")
            cleaned_dates.append("")
        else:
            cleaned_dates.append(parsed_date.isoformat())

        session = str(row["Session"]).strip()
        if session not in valid_sessions:
            errors.append(f"Row {idx + 1}: Invalid session '{row['Session']}'.")
        working.at[idx, "Session"] = session

        project = str(row["Project Number"]).strip()
        if not project:
            errors.append(f"Row {idx + 1}: Project Number is required.")
        working.at[idx, "Project Number"] = project

        check_in, check_in_error = _parse_time(row["Check-in"])
        check_out, check_out_error = _parse_time(row["Check-out"])
        if check_in_error:
            errors.append(f"Row {idx + 1}: {check_in_error}")
        if check_out_error:
            errors.append(f"Row {idx + 1}: {check_out_error}")

        if (check_in and not check_out) or (check_out and not check_in):
            errors.append(f"Row {idx + 1}: Both check-in and check-out are required.")

        if check_in and check_out:
            check_in_time, _ = parse_time_str(check_in, TIME_FORMAT)
            check_out_time, _ = parse_time_str(check_out, TIME_FORMAT)
            if check_in_time and check_out_time and check_out_time <= check_in_time:
                errors.append(f"Row {idx + 1}: Check-out must be after check-in.")

        cleaned_check_in.append(check_in or "")
        cleaned_check_out.append(check_out or "")

        duration = None
        if check_in and check_out and parsed_date:
            check_in_time, _ = parse_time_str(check_in, TIME_FORMAT)
            check_out_time, _ = parse_time_str(check_out, TIME_FORMAT)
            duration = compute_session_duration(check_in_time, check_out_time, DECIMAL_PLACES, parsed_date)
        computed_durations.append(duration)

    working["Date"] = cleaned_dates
    working["Check-in"] = cleaned_check_in
    working["Check-out"] = cleaned_check_out

    working["Allocated Time"] = pd.to_numeric(working["Allocated Time"], errors="coerce")
    if working["Allocated Time"].isna().any():
        errors.append("Allocated Time must be numeric for all rows.")
    if (working["Allocated Time"] < 0).any():
        errors.append("Allocated Time cannot be negative.")

    working["Session Duration"] = pd.to_numeric(working["Session Duration"], errors="coerce")
    for idx, duration in enumerate(computed_durations):
        if duration is not None:
            continue
        if pd.isna(working.at[idx, "Session Duration"]):
            errors.append(f"Row {idx + 1}: Session Duration is required when times are empty.")
    if (working["Session Duration"] < 0).any():
        errors.append("Session Duration cannot be negative.")

    for idx, duration in enumerate(computed_durations):
        if duration is None:
            continue
        working.at[idx, "Session Duration"] = float(duration)

    grouped = working.groupby(["Date", "Session"], dropna=False)
    tolerance = 10 ** -DECIMAL_PLACES
    for (group_date, session), group in grouped:
        if not group_date:
            continue
        session_duration = group["Session Duration"].dropna()
        if session_duration.empty:
            continue
        distinct = session_duration.round(DECIMAL_PLACES).unique()
        if len(distinct) > 1:
            errors.append(
                f"Session Duration mismatch for {group_date} {session}. Ensure all rows share the same duration."
            )
        allocated_sum = group["Allocated Time"].sum()
        if abs(allocated_sum - session_duration.iloc[0]) > tolerance:
            errors.append(
                f"Allocated Time does not match Session Duration for {group_date} {session}."
            )

    daily_totals = (
        working.groupby("Date", as_index=False)["Allocated Time"]
        .sum()
        .rename(columns={"Allocated Time": "Daily Total"})
    )
    working = working.drop(columns=["Daily Total"]).merge(daily_totals, on="Date", how="left")

    working["Session Duration"] = working["Session Duration"].apply(
        lambda value: float(round_hours(Decimal(str(value)), DECIMAL_PLACES))
        if not pd.isna(value)
        else ""
    )
    working["Allocated Time"] = working["Allocated Time"].apply(
        lambda value: float(round_hours(Decimal(str(value)), DECIMAL_PLACES))
        if not pd.isna(value)
        else ""
    )
    working["Daily Total"] = working["Daily Total"].apply(
        lambda value: float(round_hours(Decimal(str(value)), DECIMAL_PLACES))
        if not pd.isna(value)
        else ""
    )

    working = working[TIMESHEET_COLUMNS]
    return ValidationResult(working, errors)
