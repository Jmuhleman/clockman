import pandas as pd

from app.services.summary_aggregation_service import (
    aggregate_by_date,
    aggregate_by_date_project,
    aggregate_by_project,
)


def test_aggregate_by_date_sums_all_activities() -> None:
    df = pd.DataFrame(
        {
            "Date": ["2026-05-20", "2026-05-20", "2026-05-21"],
            "Allocated Time": [2.0, 1.5, 3.0],
        }
    )
    result = aggregate_by_date(df)
    assert result.loc[result["Date"] == "2026-05-20", "Total Hours Worked"].iloc[0] == 3.5
    assert result.loc[result["Date"] == "2026-05-21", "Total Hours Worked"].iloc[0] == 3.0


def test_aggregate_by_project_sums() -> None:
    df = pd.DataFrame(
        {
            "Project Number": ["PRJ-1", "PRJ-1", "PRJ-2"],
            "Allocated Time": [2.0, 1.5, 3.0],
        }
    )
    result = aggregate_by_project(df)
    total_prj1 = result.loc[result["Project Number"] == "PRJ-1", "Total Allocated Hours"].iloc[0]
    assert total_prj1 == 3.5


def test_aggregate_by_date_project_sums() -> None:
    df = pd.DataFrame(
        {
            "Date": ["2026-05-20", "2026-05-20", "2026-05-21"],
            "Project Number": ["PRJ-1", "PRJ-1", "PRJ-1"],
            "Allocated Time": [2.0, 1.5, 3.0],
        }
    )
    result = aggregate_by_date_project(df)
    total = result.loc[
        (result["Date"] == "2026-05-20") & (result["Project Number"] == "PRJ-1"),
        "Total Allocated Hours",
    ].iloc[0]
    assert total == 3.5
