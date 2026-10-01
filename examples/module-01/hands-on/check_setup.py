"""Check the single practice edit used by the M01 setup activity."""
from pathlib import Path
import sys


def main() -> int:
    path = Path(__file__).resolve().with_name("practice.txt")
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        print(f"Cannot read practice.txt: {exc}")
        return 2
    if value != "status: ready":
        print("Practice edit pending: change practice.txt to exactly 'status: ready'.")
        return 1
    print("PASS: this checkout contains the practice edit and Python ran the check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
