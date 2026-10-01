from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from order_total.pricing import calculate_order_total


class OrderTotalTests(unittest.TestCase):
    def test_empty_order(self):
        self.assertEqual(calculate_order_total([]), Decimal("0.00"))

    def test_multiple_items(self):
        lines = [(Decimal("5.25"), 2), (Decimal("3.00"), 1)]
        self.assertEqual(calculate_order_total(lines), Decimal("13.50"))

    def test_decimal_arithmetic(self):
        result = calculate_order_total([(Decimal("0.10"), 3)])
        self.assertIsInstance(result, Decimal)
        self.assertEqual(result, Decimal("0.30"))

    def test_rounds_half_up(self):
        self.assertEqual(
            calculate_order_total([(Decimal("1.005"), 1)]),
            Decimal("1.01"),
        )


if __name__ == "__main__":
    unittest.main()
