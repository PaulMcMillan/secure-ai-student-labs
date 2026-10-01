"""Detect synthetic MCP security events without echoing sensitive fields."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REQUIRED_FIELDS = {
    "timestamp", "request_id", "server_id", "server_version", "subject_id",
    "client_id", "transport", "tool", "risk_tier", "approval", "policy",
    "duration_ms", "result", "error_category", "bytes_in", "bytes_out",
    "tool_hash", "expected_tool_hash", "profile", "origin_valid",
    "audience_valid", "sensitive_output_detected",
}
FORBIDDEN_FIELDS = {"authorization", "access_token", "refresh_token", "cookie", "session_id", "secret"}


def evaluate(events: list[dict[str, Any]]) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        missing = sorted(REQUIRED_FIELDS - event.keys())
        if missing:
            alerts.append({"line": index, "severity": "high", "type": "event-schema-incomplete"})
        if FORBIDDEN_FIELDS.intersection(event):
            alerts.append({"line": index, "severity": "critical", "type": "forbidden-sensitive-field"})
        if event.get("tool_hash") != event.get("expected_tool_hash"):
            alerts.append({"line": index, "severity": "critical", "type": "tool-inventory-drift"})
        if event.get("profile") == "read-only" and event.get("result") == "write-succeeded":
            alerts.append({"line": index, "severity": "critical", "type": "write-in-read-only-profile"})
        if event.get("risk_tier") in {2, 3} and event.get("approval") != "approved":
            alerts.append({"line": index, "severity": "critical", "type": "sensitive-action-without-approval"})
        if event.get("origin_valid") is False:
            alerts.append({"line": index, "severity": "high", "type": "invalid-origin"})
        if event.get("audience_valid") is False:
            alerts.append({"line": index, "severity": "critical", "type": "wrong-token-audience"})
        if event.get("sensitive_output_detected") is True:
            alerts.append({"line": index, "severity": "critical", "type": "sensitive-output-detected"})
    return {
        "valid": not alerts,
        "events_checked": len(events),
        "alert_count": len(alerts),
        "alerts": alerts,
        "sensitive_values_echoed": False,
    }


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        events.append(value)
    return events


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python event_check.py <events.jsonl>", file=sys.stderr)
        return 2
    try:
        events = load_events(Path(argv[1]))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 2
    report = evaluate(events)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
