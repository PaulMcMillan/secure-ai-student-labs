"""Inventory reservation behavior for the Module 7 lab."""


def reserve(available: int, requested: int) -> int:
    """Return remaining units or reject a request larger than availability."""
    if requested > available:
        raise ValueError("insufficient stock")
    return available - requested
