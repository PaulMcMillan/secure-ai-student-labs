"""Starter pricing behavior for the Module 12 capstone."""

RATES = {"standard": 0.0, "partner": 0.10}


def quote_total(subtotal: float, segment: str = "standard") -> float:
    if isinstance(subtotal, bool) or not isinstance(subtotal, (int, float)) or subtotal < 0:
        raise ValueError("subtotal must be a non-negative number")
    if segment not in RATES:
        raise ValueError("unknown segment")
    return round(float(subtotal) * (1 - RATES[segment]), 2)
