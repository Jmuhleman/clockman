from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.models.entries import ProjectAllocation
from app.utils.time_utils import round_hours


def allocate_time(
    duration_hours: Decimal, projects: list[str], decimal_places: int
) -> list[ProjectAllocation]:
    if not projects:
        return []
    rounded_total = round_hours(duration_hours, decimal_places)
    count = len(projects)
    quant = Decimal(10) ** -decimal_places
    base = (rounded_total / count).quantize(quant, rounding=ROUND_HALF_UP)
    allocations = [base] * count
    remainder = rounded_total - (base * count)
    allocations[-1] = (base + remainder).quantize(quant, rounding=ROUND_HALF_UP)

    return [
        ProjectAllocation(project_number=project, allocated_hours=amount)
        for project, amount in zip(projects, allocations)
    ]
