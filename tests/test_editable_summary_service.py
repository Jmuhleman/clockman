import pandas as pd

from app.services.editable_summary_service import validate_and_prepare_edits


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2026-05-20", "2026-05-20"],
            "Session": ["Morning", "Morning"],
            "Check-in": ["08:00", "08:00"],
            "Check-out": ["12:00", "12:00"],
            "Session Duration": [4.0, 4.0],
            "Project Number": ["PRJ-1", "PRJ-2"],
            "Allocated Time": [2.0, 2.0],
            "Daily Total": [4.0, 4.0],
        }
    )


def test_validate_and_prepare_edits_recalculates_daily_total() -> None:
    result = validate_and_prepare_edits(_sample_df())
    assert result.errors == []
    assert result.cleaned["Daily Total"].iloc[0] == 4.0


def test_validate_and_prepare_edits_invalid_time() -> None:
    df = _sample_df()
    df.loc[0, "Check-in"] = "99:99"
    result = validate_and_prepare_edits(df)
    assert result.errors
