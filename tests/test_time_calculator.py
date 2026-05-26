from datetime import date, time
from decimal import Decimal

from app.services.time_calculator import compute_daily_total, compute_session_duration


def test_compute_session_duration_rounds_hours() -> None:
    duration = compute_session_duration(time(8, 0), time(12, 0), 2, date(2025, 1, 1))
    assert duration == Decimal("4.00")


def test_compute_daily_total_sums() -> None:
    total = compute_daily_total([Decimal("4.00"), Decimal("3.50")], 2)
    assert total == Decimal("7.50")
