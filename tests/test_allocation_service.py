from decimal import Decimal

from app.services.allocation_service import allocate_time


def test_allocate_time_even_split() -> None:
    allocations = allocate_time(Decimal("4.00"), ["PRJ-1", "PRJ-2"], 2)
    assert allocations[0].allocated_hours == Decimal("2.00")
    assert allocations[1].allocated_hours == Decimal("2.00")


def test_allocate_time_rounding_adjustment() -> None:
    allocations = allocate_time(Decimal("1.00"), ["A", "B", "C"], 2)
    total = sum(allocation.allocated_hours for allocation in allocations)
    assert total == Decimal("1.00")
