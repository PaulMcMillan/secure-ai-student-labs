import unittest

from src.inventory import reserve


class InventoryTests(unittest.TestCase):
    def test_positive_reservation_returns_remaining_units(self):
        self.assertEqual(reserve(8, 3), 5)

    def test_insufficient_stock_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "insufficient stock"):
            reserve(2, 3)


if __name__ == "__main__":
    unittest.main()
