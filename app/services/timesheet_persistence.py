from __future__ import annotations

from decimal import Decimal
from typing import Any

import pandas as pd
import streamlit as st

from app.config.settings import DECIMAL_PLACES, TIME_FORMAT, TIMESHEET_COLUMNS
from app.database.repositories.timesheet_repository import (
    get_timesheet_entries,
    insert_timesheet_entries,
    replace_timesheet_entries,
)
from app.models.entries import TimesheetRow
from app.utils.time_utils import format_time, parse_time_str, round_hours


def _row_to_record(row: TimesheetRow) -> dict[str, Any]:
    return {
        "work_date": row.date.isoformat(),
        "session": row.session,
        "check_in": format_time(row.check_in, TIME_FORMAT) or None,
        "check_out": format_time(row.check_out, TIME_FORMAT) or None,
        "session_duration": float(round_hours(row.session_duration, DECIMAL_PLACES))
        if row.session_duration is not None
        else None,
        "project_code": row.project_number,
        "allocated_time": float(round_hours(row.allocated_time, DECIMAL_PLACES))
        if row.allocated_time is not None
        else None,
        "daily_total": float(round_hours(row.daily_total, DECIMAL_PLACES))
        if row.daily_total is not None
        else None,
    }


def _format_time_value(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    parsed, error = parse_time_str(text[:5], TIME_FORMAT)
    if error:
        return text
    return parsed.strftime(TIME_FORMAT)


def _records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=TIMESHEET_COLUMNS)
    df = pd.DataFrame(records)
    df = df.rename(
        columns={
            "work_date": "Date",
            "session": "Session",
            "check_in": "Check-in",
            "check_out": "Check-out",
            "session_duration": "Session Duration",
            "project_code": "Project Number",
            "allocated_time": "Allocated Time",
            "daily_total": "Daily Total",
        }
    )
    df["Check-in"] = df["Check-in"].apply(_format_time_value)
    df["Check-out"] = df["Check-out"].apply(_format_time_value)
    return df[TIMESHEET_COLUMNS]


@st.cache_data(ttl=30)
def load_timesheets() -> pd.DataFrame:
    data = get_timesheet_entries()
    return _records_to_dataframe(data)


def append_timesheet_rows(rows: list[TimesheetRow]) -> None:
    if not rows:
        raise ValueError("No rows to write. Please enter at least one valid session.")
    payload = [_row_to_record(row) for row in rows]
    insert_timesheet_entries(payload)
    load_timesheets.clear()


def write_timesheets(df: pd.DataFrame, backup: bool = True) -> None:
    missing = [col for col in TIMESHEET_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    payload: list[dict[str, Any]] = []
    if not df.empty:
        prepared = df[TIMESHEET_COLUMNS].copy()
        prepared["Date"] = prepared["Date"].astype(str)
        prepared["Check-in"] = prepared["Check-in"].astype(str)
        prepared["Check-out"] = prepared["Check-out"].astype(str)
        prepared["Session Duration"] = pd.to_numeric(prepared["Session Duration"], errors="coerce")
        prepared["Allocated Time"] = pd.to_numeric(prepared["Allocated Time"], errors="coerce")
        prepared["Daily Total"] = pd.to_numeric(prepared["Daily Total"], errors="coerce")
        payload = []
        for _, row in prepared.iterrows():
            session_duration = (
                float(round_hours(Decimal(str(row["Session Duration"])), DECIMAL_PLACES))
                if not pd.isna(row["Session Duration"])
                else None
            )
            allocated_time = (
                float(round_hours(Decimal(str(row["Allocated Time"])), DECIMAL_PLACES))
                if not pd.isna(row["Allocated Time"])
                else None
            )
            daily_total = (
                float(round_hours(Decimal(str(row["Daily Total"])), DECIMAL_PLACES))
                if not pd.isna(row["Daily Total"])
                else None
            )
            payload.append(
                {
                    "work_date": row["Date"],
                    "session": row["Session"],
                    "check_in": _format_time_value(row["Check-in"]) or None,
                    "check_out": _format_time_value(row["Check-out"]) or None,
                    "session_duration": session_duration,
                    "project_code": row["Project Number"],
                    "allocated_time": allocated_time,
                    "daily_total": daily_total,
                }
            )

    replace_timesheet_entries(payload, backup=backup)
    load_timesheets.clear()
