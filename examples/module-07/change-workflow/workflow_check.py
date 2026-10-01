"""Validate the evidence record for a bounded repository change."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any


def normalized_path(value: str) -> str:
    """Return a stable repository-relative path, rejecting traversal and roots."""
    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        return ""
    return candidate.as_posix()


def evaluate(task: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []

    if evidence.get("task_id") != task.get("task_id"):
        issues.append("task_id_mismatch")

    required_model = task.get("model_contract", {})
    model = evidence.get("model_contract", {})
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
        issues.append("model_contract_invalid")

    required_stages = task.get("required_stages", [])
    actual_stages = [item.get("name") for item in evidence.get("stages", []) if isinstance(item, dict)]
    if actual_stages != required_stages:
        issues.append("stage_order_incomplete")
    for item in evidence.get("stages", []):
        if not isinstance(item, dict) or not item.get("deliverable") or not item.get("exit_evidence"):
            issues.append("stage_evidence_missing")
            break

    allowed = {normalized_path(item) for item in task.get("allowed_paths", [])}
    changed = [normalized_path(item) for item in evidence.get("changed_files", [])]
    if not changed or any(not item or item not in allowed for item in changed):
        issues.append("changed_scope_invalid")

    commands = evidence.get("commands", [])
    command_results = {
        item.get("command"): item.get("exit_code")
        for item in commands
        if isinstance(item, dict)
    }
    if any(command not in command_results for command in task.get("required_commands", [])):
        issues.append("required_check_missing")
    if not commands or any(
        not isinstance(item, dict) or item.get("exit_code") != 0 for item in commands
    ):
        issues.append("check_failed_or_unrecorded")

    acceptance = {
        item.get("id"): item.get("satisfied")
        for item in evidence.get("acceptance", [])
        if isinstance(item, dict)
    }
    if any(acceptance.get(item) is not True for item in task.get("acceptance_ids", [])):
        issues.append("acceptance_incomplete")

    review = evidence.get("diff_review", {})
    if not isinstance(review, dict) or review.get("completed") is not True:
        issues.append("diff_review_missing")
    if not isinstance(review, dict) or review.get("secret_scan") is not True:
        issues.append("secret_review_missing")

    if evidence.get("authority_expanded") is not False:
        issues.append("authority_expanded")
    if not isinstance(evidence.get("skipped_checks"), list):
        issues.append("skipped_checks_missing")
    if not isinstance(evidence.get("residual_risks"), list):
        issues.append("residual_risks_missing")
    if not isinstance(evidence.get("base"), str) or not evidence.get("base", "").strip():
        issues.append("base_missing")
    if not isinstance(evidence.get("stop_reason"), str) or not evidence.get("stop_reason", "").strip():
        issues.append("stop_reason_missing")

    unique_issues = list(dict.fromkeys(issues))
    return {
        "valid": not unique_issues,
        "issues": unique_issues,
        "changed_file_count": len(changed),
        "check_count": len(commands),
        "review_complete": isinstance(review, dict) and review.get("completed") is True,
        "authority_expanded": evidence.get("authority_expanded") is not False,
        "model_contract_valid": model_valid,
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    report = evaluate(load_json(args.task), load_json(args.evidence))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
