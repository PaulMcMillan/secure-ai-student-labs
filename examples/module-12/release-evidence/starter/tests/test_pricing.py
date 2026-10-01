import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pricing import quote_total


class StarterPricingTests(unittest.TestCase):
    def test_standard_total(self):
        self.assertEqual(quote_total(100), 100.0)

    def test_partner_total(self):
        self.assertEqual(quote_total(100, "partner"), 90.0)


if __name__ == "__main__":
    unittest.main()
