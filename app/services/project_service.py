from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.config.settings import PROJECT_COLUMNS


@dataclass(frozen=True)
class Project:
    code: str
    name: str
    active: bool


def ensure_projects_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        pd.DataFrame(columns=PROJECT_COLUMNS).to_csv(path, index=False)


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


def load_projects(path: Path) -> pd.DataFrame:
    ensure_projects_csv(path)
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=PROJECT_COLUMNS)
    missing = [col for col in PROJECT_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError("Project CSV schema mismatch. Missing: " + ", ".join(missing))
    df = df[PROJECT_COLUMNS].copy()
    df["project_code"] = df["project_code"].astype(str).str.strip()
    df["project_name"] = df["project_name"].astype(str).str.strip()
    df["active_status"] = df["active_status"].fillna(True).astype(bool)
    return df


def save_projects(path: Path, df: pd.DataFrame) -> None:
    errors = validate_projects_df(df)
    if errors:
        raise ValueError(" ".join(errors))
    df = df.copy()
    df["project_code"] = df["project_code"].astype(str).str.strip()
    df["project_name"] = df["project_name"].astype(str).str.strip()
    df["active_status"] = df["active_status"].fillna(True).astype(bool)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def get_active_projects(path: Path) -> list[Project]:
    df = load_projects(path)
    if df.empty:
        return []
    active_df = df[df["active_status"] == True]
    return [
        Project(code=row["project_code"], name=row["project_name"], active=bool(row["active_status"]))
        for _, row in active_df.iterrows()
    ]
