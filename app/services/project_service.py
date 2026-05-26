from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from app.config.settings import PROJECT_COLUMNS
from app.database.repositories.projects_repository import (
    delete_projects_by_code,
    get_projects,
    upsert_projects,
)


@dataclass(frozen=True)
class Project:
    code: str
    name: str
    active: bool


def validate_projects_df(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    missing = [col for col in PROJECT_COLUMNS if col not in df.columns]
    if missing:
        errors.append("Missing project columns: " + ", ".join(missing))
        return errors

    if df.empty:
        return errors

    df = df.copy()
    df["project_code"] = df["project_code"].astype(str).str.strip()
    df["project_name"] = df["project_name"].astype(str).str.strip()

    if df["project_code"].eq("").any():
        errors.append("Project code cannot be empty.")
    if df["project_name"].eq("").any():
        errors.append("Project name cannot be empty.")

    duplicates = df["project_code"].str.lower().duplicated()
    if duplicates.any():
        dupes = df.loc[duplicates, "project_code"].tolist()
        errors.append("Duplicate project codes: " + ", ".join(sorted(set(dupes))))

    if "active_status" in df.columns:
        invalid = df["active_status"].apply(
            lambda x: not (pd.isna(x) or isinstance(x, (bool, int)))
        )
        if invalid.any():
            errors.append("Active status must be a boolean value.")

    return errors


@st.cache_data(ttl=30)
def load_projects() -> pd.DataFrame:
    records = get_projects()
    df = pd.DataFrame(records or [])
    if df.empty:
        return pd.DataFrame(columns=PROJECT_COLUMNS)
    df = df[PROJECT_COLUMNS].copy()
    df["project_code"] = df["project_code"].astype(str).str.strip()
    df["project_name"] = df["project_name"].astype(str).str.strip()
    df["active_status"] = df["active_status"].fillna(True).astype(bool)
    return df


def save_projects(df: pd.DataFrame) -> None:
    errors = validate_projects_df(df)
    if errors:
        raise ValueError(" ".join(errors))
    df = df.copy()
    df["project_code"] = df["project_code"].astype(str).str.strip()
    df["project_name"] = df["project_name"].astype(str).str.strip()
    df["active_status"] = df["active_status"].fillna(True).astype(bool)

    existing_records = get_projects()
    existing_codes = {row["project_code"] for row in existing_records or []}
    new_codes = set(df["project_code"])

    to_delete = sorted(existing_codes - new_codes)
    if to_delete:
        delete_projects_by_code(to_delete)

    payload = df.to_dict(orient="records")
    if payload:
        upsert_projects(payload)

    load_projects.clear()


def get_active_projects() -> list[Project]:
    df = load_projects()
    if df.empty:
        return []
    active_df = df[df["active_status"] == True]
    return [
        Project(code=row["project_code"], name=row["project_name"], active=bool(row["active_status"]))
        for _, row in active_df.iterrows()
    ]
