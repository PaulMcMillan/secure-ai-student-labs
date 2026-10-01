"""Check a student's M04 project against the workbook's acceptance criteria.

Keep this checker in the lab collection, outside the agent's working project.
It runs the student's Python code in a separate process with a time limit.
"""

import argparse
from pathlib import Path
import subprocess
import sys


RUNNER = r'''
from decimal import Decimal
import importlib
from pathlib import Path
import sys

project = Path(sys.argv[1])
sys.path.insert(0, str(project / "src"))
try:
    pricing = importlib.import_module("order_total.pricing")
except Exception as exc:
    print(f"FAIL importing the calculator: {type(exc).__name__}: {exc}")
    raise SystemExit(1)

checks = [
    ("Existing empty order", "calculate_order_total", [], Decimal("0.00")),
    ("Existing multiple-item order", "calculate_order_total",
     [(Decimal("5.25"), 2), (Decimal("3.00"), 1)], Decimal("13.50")),
    ("Existing decimal arithmetic", "calculate_order_total",
     [(Decimal("0.10"), 3)], Decimal("0.30")),
    ("Existing half-up rounding", "calculate_order_total",
     [(Decimal("1.005"), 1)], Decimal("1.01")),
    ("Fee below the threshold: 49.99", "delivery_fee", Decimal("49.99"), Decimal("5.00")),
    ("Fee exactly at the threshold: 50.00", "delivery_fee", Decimal("50.00"), Decimal("0.00")),
    ("Fee above the threshold: 50.01", "delivery_fee", Decimal("50.01"), Decimal("0.00")),
]
passed = 0
for label, function, value, expected in checks:
    try:
        actual = getattr(pricing, function)(value)
        if not isinstance(actual, Decimal):
            print(f"FAIL {label}: expected Decimal, got {type(actual).__name__}")
        elif actual != expected:
            print(f"FAIL {label}: expected {expected}, got {actual}")
        else:
            print(f"PASS {label}")
            passed += 1
    except Exception as exc:
        print(f"FAIL {label}: {type(exc).__name__}: {exc}")
print(f"{passed}/{len(checks)} acceptance checks passed.")
raise SystemExit(0 if passed == len(checks) else 1)
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Student working folder, such as ../m04-work")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not (project / "src/order_total/pricing.py").is_file():
        parser.error("That folder does not contain src/order_total/pricing.py")
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-c", RUNNER, str(project)],
            cwd=project, capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: the acceptance check exceeded 20 seconds.", file=sys.stderr)
        return 1
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return int(result.returncode != 0)


if __name__ == "__main__":
    raise SystemExit(main())
