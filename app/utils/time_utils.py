from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def parse_time_str(value: Optional[str], time_format: str) -> tuple[Optional[time], Optional[str]]:
    if value is None:
        return None, None
    raw = value.strip()
    if not raw:
        return None, None
    try:
        return datetime.strptime(raw, time_format).time(), None
    except ValueError:
        return None, f"Invalid time format: '{value}'. Use HH:MM (24h)."


def round_hours(value: Decimal, decimal_places: int) -> Decimal:
    quant = Decimal(10) ** -decimal_places
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def duration_to_hours(minutes: int, decimal_places: int) -> Decimal:
    hours = Decimal(minutes) / Decimal(60)
    return round_hours(hours, decimal_places)


def format_time(value: Optional[time], time_format: str) -> str:
    if value is None:
        return ""
    return value.strftime(time_format)


def format_decimal(value: Optional[Decimal], decimal_places: int) -> str:
    if value is None:
        return ""
    return f"{value:.{decimal_places}f}"
