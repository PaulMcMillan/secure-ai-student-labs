"""Validate a course-authored evidence-gated steering plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FIELDS = ("posture", "deliverable", "scope", "constraints", "validation", "stopping_condition", "exit_evidence")


def evaluate(task: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    required_model = task.get("model_contract", {})
    model = plan.get("model_contract", {})
    required_text = (
        "selected",
        "reasoning_effort",
        "selection_reason",
        "authority_profile",
        "evaluation_set",
        "escalation_trigger",
    )
    model_valid = isinstance(model, dict) and all(
        isinstance(model.get(field), str) and model[field].strip()
        for field in required_text
    )
    if model_valid:
        model_valid = (
            model["selected"] in required_model.get("allowed_models", [])
            and model["authority_profile"] == required_model.get("required_authority_profile")
            and model["evaluation_set"] == required_model.get("required_evaluation_set")
            and model.get("astra_authority_unchanged") is True
            and required_model.get("astra_authority_unchanged") is True
        )
    if not model_valid:
        issues.append("model contract is missing, mismatched, or expands Astra authority")
    phases = plan.get("phases", [])
    postures = [phase.get("posture") for phase in phases]
    if postures != task["required_postures"]:
        issues.append("posture sequence must be Explore, Plan, Implement, Test, Review")
    allowed = set(task["allowed_paths"])
    required_constraints = {item.casefold() for item in task["required_constraints"]}
    for index, phase in enumerate(phases):
        posture = phase.get("posture", f"phase-{index + 1}")
        missing = [field for field in FIELDS if not phase.get(field)]
        if missing:
            issues.append(f"{posture} missing fields: {', '.join(missing)}")
        extra = set(phase.get("scope", [])) - allowed
        if extra:
            issues.append(f"{posture} exceeds allowed scope: {', '.join(sorted(extra))}")
        constraints = {str(item).casefold() for item in phase.get("constraints", [])}
        if not required_constraints.issubset(constraints):
            issues.append(f"{posture} omits required constraints")
        expected = task["required_exit_evidence"].get(posture)
        if expected and phase.get("exit_evidence") != expected:
            issues.append(f"{posture} has wrong exit evidence")
        stop = str(phase.get("stopping_condition", "")).casefold()
        if not any(word in stop for word in ("stop", "complete", "ask")):
            issues.append(f"{posture} has no operational stopping condition")
    return {
        "task_id": task["task_id"],
        "valid": not issues,
        "phase_count": len(phases),
        "postures": postures,
        "issues": issues,
        "authority_expanded": any("exceeds allowed scope" in issue for issue in issues),
        "model_contract_valid": model_valid,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    report = evaluate(
        json.loads(args.task.read_text(encoding="utf-8")),
        json.loads(args.plan.read_text(encoding="utf-8")),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
