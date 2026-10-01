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
        self.assertEqual(explain_quote(100), {
            "subtotal": 100.0, "discount_rate": 0.0, "total": 100.0, "reason": "standard rate",
        })
        for segment, rate, reason in (("standard", 0.0, "standard rate"), ("partner", 0.10, "partner discount")):
            for subtotal in (100, 12.345):
                with self.subTest(segment=segment, subtotal=subtotal):
                    self.assertEqual(explain_quote(subtotal, segment), {
                        "subtotal": round(float(subtotal), 2),
                        "discount_rate": rate,
                        "total": quote_total(subtotal, segment),
                        "reason": reason,
                    })

    def test_invalid_subtotals_are_rejected(self):
        for function in (quote_total, explain_quote):
            for subtotal in (-1, True, "100", None):
                with self.subTest(function=function.__name__, subtotal=subtotal):
                    with self.assertRaises(ValueError) as raised:
                        function(subtotal)
                    self.assertEqual(str(raised.exception), "subtotal must be a non-negative number")

    def test_unknown_segment_is_rejected(self):
        for function in (quote_total, explain_quote):
            with self.subTest(function=function.__name__):
                with self.assertRaises(ValueError) as raised:
                    function(10, "private")
                self.assertEqual(str(raised.exception), "unknown segment")


if __name__ == "__main__":
    unittest.main()
