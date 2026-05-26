import pandas as pd

from app.database import supabase_client
from app.services.project_service import get_active_projects, load_projects, save_projects
from tests.helpers.fake_supabase import FakeSupabase


def test_save_and_load_projects(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_projects.clear()
    df = pd.DataFrame(
        {
            "project_code": ["PRJ-1", "PRJ-2"],
            "project_name": ["Alpha", "Beta"],
            "active_status": [True, False],
        }
    )
    save_projects(df)
    loaded = load_projects()
    assert len(loaded) == 2
    assert loaded.loc[0, "project_code"] == "PRJ-1"


def test_get_active_projects(monkeypatch) -> None:
    fake = FakeSupabase()
    monkeypatch.setattr(supabase_client, "get_supabase", lambda: fake)
    load_projects.clear()
    df = pd.DataFrame(
        {
            "project_code": ["PRJ-1", "PRJ-2"],
            "project_name": ["Alpha", "Beta"],
            "active_status": [True, False],
        }
    )
    save_projects(df)
    active = get_active_projects()
    assert len(active) == 1
    assert active[0].code == "PRJ-1"
