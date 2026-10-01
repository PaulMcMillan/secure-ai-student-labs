"""Baseline tests for the synthetic pricing service."""

from decimal import Decimal
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pricing import order_total  # noqa: E402


class OrderTotalTests(unittest.TestCase):
    def test_applies_tax_and_rounds_to_cents(self) -> None:
        self.assertEqual(order_total(Decimal("19.99"), Decimal("0.0825")), Decimal("21.64"))

    def test_zero_subtotal_remains_zero(self) -> None:
        self.assertEqual(order_total(Decimal("0"), Decimal("0.10")), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
