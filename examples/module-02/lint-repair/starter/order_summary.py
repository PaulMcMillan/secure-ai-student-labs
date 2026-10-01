"""Render a simple order count for the classroom exercise."""

import math


def summarize_orders(count: int) -> str:
    """Return the singular or plural label for a nonnegative count."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    noun = "order" if count == 1 else "orders"
    return f"{count} {noun}"
