from decimal import Decimal

import pandas as pd

from app.services.allocation_override_service import validate_allocation_overrides


def test_validate_allocation_overrides_matches_session_total() -> None:
    df = pd.DataFrame(
        {
            "Session": ["Morning", "Morning"],
            "Project Number": ["PRJ-1", "PRJ-2"],
            "Allocated Time": [2.0, 2.0],
        }
    )
    session_durations = {"Morning": Decimal("4.00")}
    cleaned, errors = validate_allocation_overrides(df, session_durations, 2)
    assert errors == []
    assert cleaned["Allocated Time"].sum() == 4.0


def test_validate_allocation_overrides_detects_mismatch() -> None:
    df = pd.DataFrame(
        {
            "Session": ["Afternoon"],
            "Project Number": ["PRJ-1"],
            "Allocated Time": [1.0],
        }
    )
    session_durations = {"Afternoon": Decimal("3.00")}
    _, errors = validate_allocation_overrides(df, session_durations, 2)
    assert errors
