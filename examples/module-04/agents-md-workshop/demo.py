"""An example caller. Run with python demo.py from the repository root."""

from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from order_total.pricing import calculate_order_total


if __name__ == "__main__":
    order = [(Decimal("5.25"), 2), (Decimal("3.00"), 1)]
    print(f"Order total: {calculate_order_total(order)}")
