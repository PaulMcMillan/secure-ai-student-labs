"""Pricing behavior for the synthetic Module 3 repository."""

from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")


def order_total(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    """Return a tax-inclusive total rounded to cents."""
    return (subtotal * (Decimal("1") + tax_rate)).quantize(CENT, rounding=ROUND_HALF_UP)
