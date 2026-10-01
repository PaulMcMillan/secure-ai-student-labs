"""Validate the four required MCP control decisions in an integration dossier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_CONTROLS = {
    "per_request_protocol_and_capability_validation",
    "pinned_tool_inventory",
    "issuer_and_token_audience_validation",
    "side_effect_approval",
}


def evaluate(dossier: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if dossier.get("protocol_version") != "2026-07-28":
        issues.append("protocol_not_pinned")
    if dossier.get("transport") not in {"stdio", "streamable_http"}:
        issues.append("transport_invalid")
    controls = dossier.get("controls")
    if not isinstance(controls, dict):
        controls = {}
    for control in sorted(REQUIRED_CONTROLS):
        if not isinstance(controls.get(control), str) or not controls[control].strip():
            issues.append(f"missing_{control}")
    tools = dossier.get("pinned_tools")
    if not isinstance(tools, list) or not tools or len(tools) != len(set(tools)):
        issues.append("pinned_tool_inventory_invalid")
    if dossier.get("secrets_in_source") is not False:
        issues.append("secrets_not_excluded")
    for field in ("owner", "identity_boundary", "audit", "disablement", "removal"):
        if not isinstance(dossier.get(field), str) or not dossier[field].strip():
            issues.append(f"missing_{field}")
    return {"valid": not issues, "issues": issues, "control_count": len(controls), "tool_count": len(tools or [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    args = parser.parse_args()
    dossier = json.loads(args.dossier.read_text(encoding="utf-8"))
    report = evaluate(dossier)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
