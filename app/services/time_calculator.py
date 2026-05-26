from __future__ import annotations

from datetime import datetime, date, time
from decimal import Decimal
from typing import Iterable, Optional

from app.utils.time_utils import duration_to_hours, round_hours


def compute_session_duration(
    check_in: Optional[time],
    check_out: Optional[time],
    decimal_places: int,
    entry_date: Optional[date] = None,
) -> Optional[Decimal]:
    if not check_in or not check_out:
        return None
    day = entry_date or date.today()
    start = datetime.combine(day, check_in)
    end = datetime.combine(day, check_out)
    minutes = int((end - start).total_seconds() // 60)
    return duration_to_hours(minutes, decimal_places)


def compute_daily_total(durations: Iterable[Optional[Decimal]], decimal_places: int) -> Decimal:
    total = sum((duration for duration in durations if duration is not None), Decimal(0))
    return round_hours(total, decimal_places)
