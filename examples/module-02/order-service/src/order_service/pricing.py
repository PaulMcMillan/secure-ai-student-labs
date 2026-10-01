"""Deterministic order-total calculation for the Module 2 lab."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

CENT = Decimal("0.01")


def calculate_order_total(
    lines: Iterable[tuple[Decimal, int]],
    tax_rate: Decimal = Decimal("0.08"),
) -> Decimal:
    """Return the tax-inclusive total for ``(unit_price, quantity)`` lines."""
    subtotal = sum((unit_price * quantity for unit_price, quantity in lines), Decimal("0"))
    tax = (subtotal * tax_rate).quantize(CENT, rounding=ROUND_HALF_UP)
    return (subtotal + tax).quantize(CENT, rounding=ROUND_HALF_UP)
