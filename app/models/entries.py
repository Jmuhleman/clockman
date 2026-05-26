from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class SessionInput:
    check_in: Optional[time]
    check_out: Optional[time]
    projects: list[str]


@dataclass(frozen=True)
class ProjectAllocation:
    project_number: str
    allocated_hours: Decimal


@dataclass(frozen=True)
class SessionComputed:
    session_label: str
    check_in: Optional[time]
    check_out: Optional[time]
    duration_hours: Optional[Decimal]
    allocations: list[ProjectAllocation]


@dataclass(frozen=True)
class TimesheetRow:
    date: date
    session: str
    check_in: Optional[time]
    check_out: Optional[time]
    session_duration: Optional[Decimal]
    project_number: str
    allocated_time: Optional[Decimal]
    daily_total: Optional[Decimal]
