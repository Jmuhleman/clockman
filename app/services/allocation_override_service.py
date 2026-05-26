from __future__ import annotations

from decimal import Decimal

import pandas as pd

from app.utils.time_utils import round_hours


def validate_allocation_overrides(
    allocation_df: pd.DataFrame,
    session_durations: dict[str, Decimal | None],
    decimal_places: int,
) -> tuple[pd.DataFrame, list[str]]:
    errors: list[str] = []
    if allocation_df.empty:
        return allocation_df, errors

    required_columns = {"Session", "Project Number", "Allocated Time"}
    missing = required_columns - set(allocation_df.columns)
    if missing:
        return allocation_df, ["Missing columns: " + ", ".join(sorted(missing))]

    working = allocation_df.copy()
    working["Allocated Time"] = pd.to_numeric(working["Allocated Time"], errors="coerce")
    if working["Allocated Time"].isna().any():
        errors.append("Allocated Time must be numeric for all rows.")
    if (working["Allocated Time"] < 0).any():
        errors.append("Allocated Time cannot be negative.")

    working["Project Number"] = working["Project Number"].astype(str).str.strip()
    if working["Project Number"].eq("").any():
        errors.append("Project Number is required for all rows.")

    tolerance = Decimal(10) ** -decimal_places
    for session, session_df in working.groupby("Session"):
        duration = session_durations.get(session)
        if duration is None:
            errors.append(f"{session}: Session duration is missing.")
            continue
        allocated_sum = Decimal(str(session_df["Allocated Time"].sum()))
        if (allocated_sum - duration).copy_abs() > tolerance:
            errors.append(
                f"{session}: Allocated Time total must equal {duration:.{decimal_places}f}."
            )

    daily_total = sum(
        (duration for duration in session_durations.values() if duration is not None),
        Decimal(0),
    )
    if not working.empty:
        allocated_total = Decimal(str(working["Allocated Time"].sum()))
        if (allocated_total - daily_total).copy_abs() > tolerance:
            errors.append(
                f"Daily total allocation must equal {daily_total:.{decimal_places}f}."
            )

    if errors:
        return working, errors

    working["Allocated Time"] = working["Allocated Time"].apply(
        lambda value: float(round_hours(Decimal(str(value)), decimal_places))
    )
    return working, errors
