from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable


def generate_time_options(interval_minutes: int) -> list[str]:
    if interval_minutes <= 0:
        raise ValueError("Interval minutes must be greater than zero.")
    options: list[str] = []
    current = datetime(2000, 1, 1, 0, 0)
    end = datetime(2000, 1, 1, 23, 59)
    step = timedelta(minutes=interval_minutes)
    while current <= end:
        options.append(current.strftime("%H:%M"))
        current += step
    return options


def with_empty_option(options: Iterable[str]) -> list[str]:
    return [""] + list(options)
