"""Inventory reservation behavior for the Module 7 lab."""


def reserve(available: int, requested: int) -> int:
    """Return remaining units after validating a positive reservation."""
    if requested <= 0:
        raise ValueError("requested quantity must be positive")
    if requested > available:
        raise ValueError("insufficient stock")
    return available - requested
