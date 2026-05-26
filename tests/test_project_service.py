from pathlib import Path

import pandas as pd

from app.services.project_service import get_active_projects, load_projects, save_projects


def test_save_and_load_projects(tmp_path: Path) -> None:
    path = tmp_path / "projects.csv"
    df = pd.DataFrame(
        {
            "project_code": ["PRJ-1", "PRJ-2"],
            "project_name": ["Alpha", "Beta"],
            "active_status": [True, False],
        }
    )
    save_projects(path, df)
    loaded = load_projects(path)
    assert len(loaded) == 2
    assert loaded.loc[0, "project_code"] == "PRJ-1"


def test_get_active_projects(tmp_path: Path) -> None:
    path = tmp_path / "projects.csv"
    df = pd.DataFrame(
        {
            "project_code": ["PRJ-1", "PRJ-2"],
            "project_name": ["Alpha", "Beta"],
            "active_status": [True, False],
        }
    )
    save_projects(path, df)
    active = get_active_projects(path)
    assert len(active) == 1
    assert active[0].code == "PRJ-1"
