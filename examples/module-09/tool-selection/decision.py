"""Validate a deterministic, product-independent coding-agent workflow record."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ALLOWED_RECOMMENDATIONS = {"codex", "claude_code", "codex_then_claude_code"}
ALLOWED_TOOLS = {"codex", "claude_code"}
SHA_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")
REQUIRED_ROLE_FIELDS = {
    "tool", "purpose", "authority", "allowed_paths", "inputs", "output",
    "validation", "stop_condition", "receiving_owner",
}
CLAUDE_CONTROL_FIELDS = {
    "restricted_mode_considered", "sandbox_fail_closed", "managed_policy_reviewed",
    "plugin_inventory_reviewed", "loop_usage_monitoring",
}


def evaluate(record: dict) -> dict:
    issues: list[str] = []
    recommendation = record.get("recommendation")
    if recommendation not in ALLOWED_RECOMMENDATIONS:
        issues.append("recommendation must name an allowed workflow")

    base = record.get("base_commit", "")
    if not isinstance(base, str) or not SHA_PATTERN.fullmatch(base):
        issues.append("base_commit must be an immutable 7-40 character hexadecimal SHA")

    rationale = record.get("rationale", [])
    if not isinstance(rationale, list) or len(rationale) < 2 or not all(
        isinstance(item, str) and item.strip() for item in rationale
    ):
        issues.append("rationale must contain at least two task-evidence statements")

    roles = record.get("roles", [])
    if not isinstance(roles, list) or not roles:
        issues.append("roles must contain at least one role")
        roles = []

    writers = 0
    outputs: list[str] = []
    tools: list[str] = []
    for index, role in enumerate(roles, start=1):
        if not isinstance(role, dict):
            issues.append(f"role {index} must be an object")
            continue
        missing = sorted(REQUIRED_ROLE_FIELDS - role.keys())
        if missing:
            issues.append(f"role {index} missing fields: {', '.join(missing)}")
        tool = role.get("tool")
        if tool not in ALLOWED_TOOLS:
            issues.append(f"role {index} has an unsupported tool")
        else:
            tools.append(tool)
        authority = role.get("authority")
        if authority == "write":
            writers += 1
        elif authority != "read":
            issues.append(f"role {index} authority must be read or write")
        for field in ("purpose", "output", "stop_condition", "receiving_owner"):
            if not isinstance(role.get(field), str) or not role.get(field, "").strip():
                issues.append(f"role {index} {field} must be non-empty")
        for field in ("allowed_paths", "inputs", "validation"):
            value = role.get(field)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                issues.append(f"role {index} {field} must be a non-empty string list")
        if isinstance(role.get("output"), str) and role["output"].strip():
            outputs.append(role["output"])

    if writers > 1:
        issues.append("concurrent or multiple writers are not allowed")
    if len(outputs) != len(set(outputs)):
        issues.append("roles must own distinct outputs")

    expected_tools = {
        "codex": ["codex"],
        "claude_code": ["claude_code"],
        "codex_then_claude_code": ["codex", "claude_code"],
    }.get(recommendation)
    if expected_tools is not None and tools != expected_tools:
        issues.append("role order does not match recommendation")
    if recommendation == "codex" and writers != 1:
        issues.append("Codex implementation workflow requires exactly one writer")
    if recommendation == "claude_code" and writers != 0:
        issues.append("standalone Claude Code complementary workflow must be read-only")
    if recommendation == "codex_then_claude_code":
        if writers != 1:
            issues.append("bounded sequence requires exactly one writer")
        if len(roles) == 2 and roles[1].get("authority") != "read":
            issues.append("second role in bounded sequence must be read-only")

    claude_controls_current = True
    if "claude_code" in tools:
        baseline = record.get("product_baseline", {})
        controls = baseline.get("claude_code_controls", {}) if isinstance(baseline, dict) else {}
        claude_controls_current = (
            baseline.get("as_of") == "2026-09-10"
            and isinstance(controls, dict)
            and CLAUDE_CONTROL_FIELDS <= set(controls)
            and all(controls[field] is True for field in CLAUDE_CONTROL_FIELDS)
        )
        if not claude_controls_current:
            issues.append("Claude Code roles require the 2026-09-10 restricted-mode, fail-closed sandbox, managed-policy, plugin, and loop-usage control review")

    valid = not issues
    return {
        "scenario_id": record.get("scenario_id"),
        "valid": valid,
        "recommendation": recommendation,
        "single_writer": writers <= 1,
        "writer_count": writers,
        "role_count": len(roles),
        "claude_controls_current": claude_controls_current,
        "credentials_used": False,
        "network_used": False,
        "issues": issues,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python decision.py <scenario.json>", file=sys.stderr)
        return 2
    try:
        record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "issues": [str(exc)]}, indent=2))
        return 2
    report = evaluate(record)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
