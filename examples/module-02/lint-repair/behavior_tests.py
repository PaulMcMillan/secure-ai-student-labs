"""Run fixed behavior tests against the explicitly selected classroom file."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import unittest


def run_tests(source: Path) -> unittest.result.TestResult:
    spec = importlib.util.spec_from_file_location("classroom_order_summary", source)
    if spec is None or spec.loader is None:
        raise ValueError("source must be an importable Python file")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class OrderSummaryTests(unittest.TestCase):
        def test_zero_orders(self):
            self.assertEqual(module.summarize_orders(0), "0 orders")

        def test_one_order(self):
            self.assertEqual(module.summarize_orders(1), "1 order")

        def test_multiple_orders(self):
            self.assertEqual(module.summarize_orders(3), "3 orders")

        def test_negative_count(self):
            with self.assertRaisesRegex(ValueError, "^count must be nonnegative$"):
                module.summarize_orders(-1)

    return unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(OrderSummaryTests))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    return 0 if run_tests(args.source).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
