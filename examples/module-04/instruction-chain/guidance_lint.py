"""Lint the course's recommended AGENTS.md teaching structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


REQUIRED_HEADINGS = ("scope", "repository map", "commands", "constraints", "done when")


def lint(text: str) -> list[str]:
    headings = {match.casefold() for match in re.findall(r"(?m)^##\s+(.+?)\s*$", text)}
    issues = [f"missing heading: {name}" for name in REQUIRED_HEADINGS if name not in headings]
    if "always do the right thing" in text.casefold():
        issues.append("vague instruction has no observable behavior")
    if re.search(r"(?i)(password|api[_ -]?key|token|secret)\s*[:=]\s*\S+", text):
        issues.append("secret-like assignment found")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    issues = lint(args.path.read_text(encoding="utf-8"))
    print(json.dumps({"valid": not issues, "issues": issues, "secret_values_echoed": False}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
