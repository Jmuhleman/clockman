from app.database import supabase_client
from app.database.repositories.projects_repository import (
    create_project,
    delete_project,
    get_projects,
    update_project,
)
from tests.helpers.fake_supabase import FakeSupabase


def test_projects_repository_crud(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)

    create_project({"project_code": "PRJ-1", "project_name": "Alpha", "active_status": True})
    projects = get_projects()
    assert projects

    update_project("PRJ-1", {"project_name": "Updated"})
    updated = get_projects()
    assert updated[0]["project_name"] == "Updated"

    delete_project("PRJ-1")
    remaining = get_projects()
    assert remaining == []
