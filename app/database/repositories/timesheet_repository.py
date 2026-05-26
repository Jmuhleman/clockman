from __future__ import annotations

import logging
from typing import Any

from app.config.settings import TIMESHEETS_TABLE
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


def get_timesheet_entries() -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE)
        .select(
            "work_date,session,check_in,check_out,session_duration,project_code,allocated_time,daily_total,created_at"
        )
        .order("created_at"),
        "Failed to load timesheet entries from Supabase.",
    )


def get_entries_by_date(work_date: str) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE)
        .select(
            "work_date,session,check_in,check_out,session_duration,project_code,allocated_time,daily_total,created_at"
        )
        .eq("work_date", work_date),
        "Failed to load timesheet entries by date.",
    )


def get_entries_by_project(project_code: str) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE)
        .select(
            "work_date,session,check_in,check_out,session_duration,project_code,allocated_time,daily_total,created_at"
        )
        .eq("project_code", project_code),
        "Failed to load timesheet entries by project.",
    )


def get_summary_entries() -> list[dict[str, Any]]:
    return get_timesheet_entries()


def insert_timesheet_entries(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not payload:
        return []
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE).insert(payload),
        "Failed to append timesheet entries to Supabase.",
    )


def update_timesheet_entry(entry_id: int, updates: dict[str, Any]) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE).update(updates).eq("id", entry_id),
        "Failed to update timesheet entry.",
    )


def delete_timesheet_entry(entry_id: int) -> list[dict[str, Any]]:
    supabase = supabase_client.get_supabase()
    return _execute(
        supabase.table(TIMESHEETS_TABLE).delete().eq("id", entry_id),
        "Failed to delete timesheet entry.",
    )


def replace_timesheet_entries(payload: list[dict[str, Any]], backup: bool = True) -> None:
    supabase = supabase_client.get_supabase()
    backup_rows: list[dict[str, Any]] = []
    if backup:
        backup_rows = _execute(
            supabase.table(TIMESHEETS_TABLE)
            .select(
                "work_date,session,check_in,check_out,session_duration,project_code,allocated_time,daily_total,created_at"
            ),
            "Failed to read existing timesheet entries for backup.",
        )

    _execute(
        supabase.table(TIMESHEETS_TABLE).delete().neq("id", 0),
        "Failed to clear existing timesheet entries.",
    )

    if payload:
        try:
            insert_timesheet_entries(payload)
        except ValueError as exc:
            if backup_rows:
                insert_timesheet_entries(backup_rows)
            raise exc
