import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pricing import explain_quote, quote_total


class PricingTests(unittest.TestCase):
    def test_standard_total_is_preserved(self):
        self.assertEqual(quote_total(100), 100.0)

    def test_partner_total_is_preserved(self):
        self.assertEqual(quote_total(100, "partner"), 90.0)

    def test_explanation(self):
        self.assertEqual(
            explain_quote(100, "partner"),
            {"subtotal": 100.0, "discount_rate": 0.10, "total": 90.0, "reason": "partner discount"},
        )

    def test_negative_subtotal_is_rejected(self):
        with self.assertRaises(ValueError):
            quote_total(-1)

    def test_unknown_segment_is_rejected(self):
        with self.assertRaises(ValueError):
            quote_total(10, "private")


if __name__ == "__main__":
    unittest.main()
