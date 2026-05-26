from __future__ import annotations

import pandas as pd


def _ensure_allocated_numeric(df: pd.DataFrame) -> pd.DataFrame:
    if "Allocated Time" not in df.columns:
        raise ValueError("Allocated Time column is missing.")
    df = df.copy()
    df["Allocated Time"] = pd.to_numeric(df["Allocated Time"], errors="raise")
    return df


def aggregate_by_project(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Project Number", "Total Allocated Hours"])
    if "Project Number" not in df.columns:
        raise ValueError("Project Number column is missing.")
    df = _ensure_allocated_numeric(df)
    result = (
        df.groupby("Project Number", as_index=False)["Allocated Time"]
        .sum()
        .rename(columns={"Allocated Time": "Total Allocated Hours"})
        .sort_values("Project Number")
    )
    return result


def aggregate_by_date_project(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Date", "Project Number", "Total Allocated Hours"])
    df = _ensure_allocated_numeric(df)
    if "Date" not in df.columns or "Project Number" not in df.columns:
        raise ValueError("Date or Project Number column is missing.")
    result = (
        df.groupby(["Date", "Project Number"], as_index=False)["Allocated Time"]
        .sum()
        .rename(columns={"Allocated Time": "Total Allocated Hours"})
        .sort_values(["Date", "Project Number"])
    )
    return result
