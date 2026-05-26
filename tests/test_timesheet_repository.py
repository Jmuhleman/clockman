from app.database import supabase_client
from app.database.repositories.timesheet_repository import (
    delete_timesheet_entry,
    get_entries_by_project,
    get_timesheet_entries,
    insert_timesheet_entries,
    update_timesheet_entry,
)
from tests.helpers.fake_supabase import FakeSupabase


def test_timesheet_repository_crud(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)

    payload = [
        {
            "work_date": "2026-05-20",
            "session": "Morning",
            "check_in": "08:00",
            "check_out": "12:00",
            "session_duration": 4.0,
            "project_code": "PRJ-1",
            "allocated_time": 4.0,
            "daily_total": 4.0,
        }
    ]
    inserted = insert_timesheet_entries(payload)
    assert len(inserted) == 1

    entries = get_timesheet_entries()
    assert entries

    entry_id = inserted[0]["id"]
    update_timesheet_entry(entry_id, {"allocated_time": 3.5})
    by_project = get_entries_by_project("PRJ-1")
    assert by_project[0]["allocated_time"] == 3.5

    delete_timesheet_entry(entry_id)
    remaining = get_timesheet_entries()
    assert remaining == []
