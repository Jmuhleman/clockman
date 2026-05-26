from __future__ import annotations

import logging
from typing import Any

from app.config.settings import PROJECTS_TABLE
from app.database import supabase_client


def _execute(query, error_message: str) -> list[dict[str, Any]]:
    try:
        response = query.execute()
    except Exception as exc:
        logging.exception(error_message)
        raise ValueError(error_message) from exc
    if getattr(response, "error", None):
        logging.error("%s: %s", error_message, response.error)
        raise ValueError(error_message)
    return response.data or []


def get_active_projects() -> list[dict[str, Any]]:
    return [row for row in get_projects() if row.get("active_status")]


def get_projects() -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(PROJECTS_TABLE)
        .select("project_code,project_name,active_status")
        .order("project_code"),
        "Failed to load projects from Supabase.",
    )


def create_project(project: dict[str, Any]) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(PROJECTS_TABLE).insert([project]),
        "Failed to create project in Supabase.",
    )


def update_project(project_code: str, updates: dict[str, Any]) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(PROJECTS_TABLE).update(updates).eq("project_code", project_code),
        "Failed to update project in Supabase.",
    )


def delete_project(project_code: str) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(PROJECTS_TABLE).delete().eq("project_code", project_code),
        "Failed to delete project from Supabase.",
    )


def upsert_projects(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    if not payload:
        return []
    return _execute(
        supabase.table(PROJECTS_TABLE).upsert(payload, on_conflict="project_code"),
        "Failed to save projects to Supabase.",
    )


def delete_projects_by_code(codes: list[str]) -> list[dict[str, Any]]:
    if not codes:
        return []
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(PROJECTS_TABLE).delete().in_("project_code", codes),
        "Failed to delete removed projects from Supabase.",
    )
