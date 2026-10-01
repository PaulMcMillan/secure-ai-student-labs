"""Validate least-privilege security-agent task cards without running agents."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED = {"id", "task", "scope", "tools", "network", "writes", "oracle", "budget", "prohibited", "human_owner", "output", "stop"}


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    cards = data.get("cards", [])
    errors: list[str] = []
    ids: set[str] = set()
    for index, card in enumerate(cards):
        missing = sorted(REQUIRED - set(card))
        if missing:
            errors.append(f"card {index} missing: {', '.join(missing)}")
            continue
        if card["id"] in ids:
            errors.append(f"duplicate id: {card['id']}")
        ids.add(card["id"])
        if card["network"] is not False or card["writes"] is not False:
            errors.append(f"{card['id']} must be offline and read-only")
        budget = card["budget"]
        if not isinstance(budget.get("cases"), int) or budget["cases"] <= 0:
            errors.append(f"{card['id']} needs a positive case budget")
        if not isinstance(budget.get("attempts_per_case"), int) or not 0 < budget["attempts_per_case"] <= 3:
            errors.append(f"{card['id']} attempts_per_case must be 1..3")
        prohibited = " ".join(card["prohibited"]).lower()
        if not any(term in prohibited for term in ["live", "production", "containment", "remediation"]):
            errors.append(f"{card['id']} lacks a material safety prohibition")
        if not card["oracle"] or not card["human_owner"] or not card["stop"]:
            errors.append(f"{card['id']} lacks oracle, owner, or stop condition")
    expected = {"SEC-THREAT", "SEC-PROMPT", "SEC-LOOP", "SEC-TOOL-MCP", "SEC-SUPPLY", "SEC-DETECT", "SEC-RECOVERY"}
    if ids != expected:
        errors.append("card set does not match the seven required security roles")
    return {"valid": not errors, "cards": len(cards), "errors": errors, "agents_started": False, "network_used": False, "files_written": False}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: security_agent_check.py SECURITY_AGENT_CARDS.json")
        return 2
    report = validate(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
