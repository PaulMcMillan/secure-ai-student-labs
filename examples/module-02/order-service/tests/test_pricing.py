"""Baseline tests for the synthetic order service."""

from decimal import Decimal
from pathlib import Path
import sys
import unittest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from order_service.pricing import calculate_order_total


class CalculateOrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self) -> None:
        self.assertEqual(calculate_order_total([]), Decimal("0.00"))

    def test_single_line_includes_tax(self) -> None:
        total = calculate_order_total([(Decimal("10.00"), 2)])
        self.assertEqual(total, Decimal("21.60"))

    def test_multiple_lines_are_summed(self) -> None:
        total = calculate_order_total(
            [(Decimal("5.25"), 2), (Decimal("3.00"), 1)]
        )
        self.assertEqual(total, Decimal("14.58"))

    def test_rounds_half_up_to_cents(self) -> None:
        total = calculate_order_total(
            [(Decimal("0.05"), 1)], tax_rate=Decimal("0.10")
        )
        self.assertEqual(total, Decimal("0.06"))


if __name__ == "__main__":
    unittest.main()
