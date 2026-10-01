"""Reference pricing change for the Module 12 capstone."""

RATES = {"standard": 0.0, "partner": 0.10}
REASONS = {"standard": "standard rate", "partner": "partner discount"}


def quote_total(subtotal: float, segment: str = "standard") -> float:
    if isinstance(subtotal, bool) or not isinstance(subtotal, (int, float)) or subtotal < 0:
        raise ValueError("subtotal must be a non-negative number")
    if segment not in RATES:
        raise ValueError("unknown segment")
    return round(float(subtotal) * (1 - RATES[segment]), 2)


def explain_quote(subtotal: float, segment: str = "standard") -> dict[str, object]:
    total = quote_total(subtotal, segment)
    return {
        "subtotal": round(float(subtotal), 2),
        "discount_rate": RATES[segment],
        "total": total,
        "reason": REASONS[segment],
    }
