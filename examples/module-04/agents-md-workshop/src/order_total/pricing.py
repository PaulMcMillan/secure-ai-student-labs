"""Calculate a total using decimal prices and whole-item quantities."""

from decimal import Decimal, ROUND_HALF_UP


def calculate_order_total(lines: list[tuple[Decimal, int]]) -> Decimal:
    """Return the total for (unit_price, quantity) pairs."""
    total = Decimal("0")
    for price, quantity in lines:
        total += price * quantity
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def delivery_fee(subtotal: Decimal) -> Decimal:
    """Return the fee for a nonnegative subtotal already rounded to cents."""
    raise NotImplementedError("Delivery policy has not been supplied")
