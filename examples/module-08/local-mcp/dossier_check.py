"""Validate an MCP integration risk dossier without reading credentials."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_TEXT = (
    "server_name",
    "owner",
    "purpose",
    "source_date",
    "protocol_version",
    "transport",
    "identity_boundary",
    "credential_handling",
    "audit",
    "monitoring",
    "disablement",
    "rollback",
    "removal",
)
REQUIRED_TOOL_FIELDS = (
    "name",
    "side_effect",
    "approval",
    "input_fields",
    "output_fields",
    "idempotent",
)


def evaluate(dossier: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    for field in REQUIRED_TEXT:
        if not isinstance(dossier.get(field), str) or not dossier[field].strip():
            issues.append(f"missing_{field}")

    if dossier.get("transport") not in {"stdio", "streamable_http"}:
        issues.append("transport_invalid")
    if dossier.get("secrets_in_source") is not False:
        issues.append("secrets_not_excluded")

    exposure = dossier.get("data_exposure")
    if not isinstance(exposure, dict) or not all(
        key in exposure for key in ("input", "output", "downstream_systems")
    ):
        issues.append("data_exposure_incomplete")

    tools = dossier.get("tools")
    if not isinstance(tools, list) or not tools:
        issues.append("tool_inventory_missing")
        tools = []
    names: list[str] = []
    for tool in tools:
        if not isinstance(tool, dict) or any(field not in tool for field in REQUIRED_TOOL_FIELDS):
            issues.append("tool_contract_incomplete")
            continue
        name = tool.get("name")
        if not isinstance(name, str) or not name:
            issues.append("tool_name_invalid")
        else:
            names.append(name)
        if tool.get("side_effect") != "none" and tool.get("approval") in {"auto", "approve"}:
            issues.append("write_tool_needs_prompt")
        if not isinstance(tool.get("input_fields"), list) or not isinstance(
            tool.get("output_fields"), list
        ):
            issues.append("tool_fields_invalid")
        if not isinstance(tool.get("idempotent"), bool):
            issues.append("idempotency_missing")
    if len(names) != len(set(names)):
        issues.append("duplicate_tool_name")

    timeouts = dossier.get("timeouts")
    if not isinstance(timeouts, dict) or any(
        not isinstance(timeouts.get(key), int) or timeouts[key] <= 0
        for key in ("startup_seconds", "tool_seconds")
    ):
        issues.append("timeouts_invalid")
    for field in ("failure_modes", "residual_risks"):
        if not isinstance(dossier.get(field), list) or not dossier[field]:
            issues.append(f"{field}_missing")

    unique_issues = list(dict.fromkeys(issues))
    return {
        "valid": not unique_issues,
        "issues": unique_issues,
        "tool_count": len(tools),
        "transport": dossier.get("transport"),
        "secrets_in_source": dossier.get("secrets_in_source") is not False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    args = parser.parse_args()
    dossier = json.loads(args.dossier.read_text(encoding="utf-8"))
    if not isinstance(dossier, dict):
        raise ValueError("dossier must be a JSON object")
    report = evaluate(dossier)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
