from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
import shutil

import pandas as pd

from app.config.settings import CSV_COLUMNS, DECIMAL_PLACES, TIME_FORMAT
from app.models.entries import TimesheetRow
from app.utils.time_utils import format_decimal, format_time


def ensure_csv_exists(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def validate_csv_schema(path: Path) -> None:
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader, None)
    if header is None:
        raise ValueError("CSV file is empty. Expected a header row.")
    if header != CSV_COLUMNS:
        raise ValueError(
            "CSV schema mismatch. Expected columns: " + ", ".join(CSV_COLUMNS)
        )


def _row_to_dict(row: TimesheetRow) -> dict[str, str]:
    return {
        "Date": row.date.isoformat(),
        "Session": row.session,
        "Check-in": format_time(row.check_in, TIME_FORMAT),
        "Check-out": format_time(row.check_out, TIME_FORMAT),
        "Session Duration": format_decimal(row.session_duration, DECIMAL_PLACES),
        "Project Number": row.project_number,
        "Allocated Time": format_decimal(row.allocated_time, DECIMAL_PLACES),
        "Daily Total": format_decimal(row.daily_total, DECIMAL_PLACES),
    }


def append_timesheet_rows(path: Path, rows: list[TimesheetRow]) -> None:
    if not rows:
        raise ValueError("No rows to write. Please enter at least one valid session.")
    ensure_csv_exists(path)
    validate_csv_schema(path)
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        for row in rows:
            writer.writerow(_row_to_dict(row))


def load_timesheets(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=CSV_COLUMNS)
    validate_csv_schema(path)
    return pd.read_csv(path)


def write_timesheets(path: Path, df: pd.DataFrame, backup: bool = True) -> None:
    if df.empty:
        raise ValueError("Cannot write an empty timesheet dataset.")
    missing = [col for col in CSV_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    df = df[CSV_COLUMNS].copy()

    if backup and path.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = path.with_suffix(f".bak.{timestamp}")
        shutil.copy2(path, backup_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, float_format=f"%.{DECIMAL_PLACES}f")
