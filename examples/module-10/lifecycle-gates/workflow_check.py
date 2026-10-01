"""Validate synthetic AI delivery lifecycle evidence without executing it."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any


EXAMPLES_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = EXAMPLES_ROOT.parent
if str(EXAMPLES_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_ROOT))
from rag_evidence_binding import SHA256, verify_rag_evidence  # noqa: E402

GIT_SHA = re.compile(r"^[0-9a-f]{7,40}$")
ROLLBACK_FIELDS = {"trigger", "owner", "steps", "validation_command", "validation_result"}
RAG_DIGEST_FIELDS = {"corpus", "index", "configuration"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate(task: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if evidence.get("workflow_id") != task.get("workflow_id"):
        issues.append("workflow_id does not match the task contract")

    base = evidence.get("base_commit", "")
    if not isinstance(base, str) or not GIT_SHA.fullmatch(base):
        issues.append("base_commit must be an immutable hexadecimal SHA")

    allowed_paths = set(task.get("allowed_paths", []))
    changed_paths = evidence.get("changed_paths", [])
    scope_ok = isinstance(changed_paths, list) and bool(changed_paths) and set(changed_paths) <= allowed_paths
    if not scope_ok:
        issues.append("changed_paths must be non-empty and remain within allowed_paths")

    if evidence.get("authority_expanded") is not False:
        issues.append("authority_expanded must be false")
    if evidence.get("secrets_included") is not False:
        issues.append("secrets_included must be false")
    skipped = evidence.get("skipped_checks")
    if skipped != []:
        issues.append("skipped_checks must be an empty list")

    states = task.get("required_states", [])
    expected_ids = [state.get("id") for state in states]
    events = evidence.get("events", [])
    actual_ids = [event.get("state") for event in events] if isinstance(events, list) else []
    if actual_ids != expected_ids:
        issues.append("events must contain every required state exactly once and in order")

    gates_passed = True
    for index, state in enumerate(states):
        if index >= len(events) or not isinstance(events[index], dict):
            gates_passed = False
            continue
        event = events[index]
        if event.get("state") != state.get("id"):
            gates_passed = False
            continue
        if not nonempty(event.get("owner")):
            issues.append(f"state {state.get('id')} must name an owner")
        if event.get("owner_role") != state.get("owner_role"):
            issues.append(f"state {state.get('id')} owner_role violates the contract")
        if event.get("authority") != state.get("authority"):
            issues.append(f"state {state.get('id')} authority violates the contract")
        if event.get("result") != "pass":
            issues.append(f"state {state.get('id')} gate must pass")
            gates_passed = False
        required = set(state.get("required_evidence", []))
        supplied = event.get("evidence", [])
        if not isinstance(supplied, list) or not required.issubset(set(supplied)):
            issues.append(f"state {state.get('id')} is missing required evidence")
            gates_passed = False

    by_state = {event.get("state"): event for event in events if isinstance(event, dict)}
    implementation_owner = by_state.get("implement", {}).get("owner")
    approval_owner = by_state.get("approve", {}).get("owner")
    separation_of_duties = bool(
        implementation_owner and approval_owner and implementation_owner != approval_owner
    )
    if not separation_of_duties:
        issues.append("implementation and approval must have different owners")

    rollback = evidence.get("rollback", {})
    rollback_ready = isinstance(rollback, dict) and ROLLBACK_FIELDS <= rollback.keys()
    if rollback_ready:
        rollback_ready = (
            nonempty(rollback.get("trigger"))
            and nonempty(rollback.get("owner"))
            and isinstance(rollback.get("steps"), list)
            and len(rollback["steps"]) >= 3
            and all(nonempty(step) for step in rollback["steps"])
            and rollback.get("validation_command")
            == task.get("required_rollback_validation_command")
            and rollback.get("validation_result") == "pass"
        )
    if not rollback_ready:
        issues.append(
            "rollback must have a trigger, owner, at least three steps, the contract-required "
            "validation command, and a passing result"
        )

    rag = evidence.get("rag_release", {})
    digests = rag.get("digests", {}) if isinstance(rag, dict) else {}
    ingestion = rag.get("ingestion", {}) if isinstance(rag, dict) else {}
    category_results = rag.get("category_results", {}) if isinstance(rag, dict) else {}
    metric_results = rag.get("metric_results", {}) if isinstance(rag, dict) else {}
    monitoring = rag.get("monitoring", {}) if isinstance(rag, dict) else {}
    binding = verify_rag_evidence(
        REPO_ROOT,
        task.get("rag_observed_evidence"),
        rag.get("observed_evidence") if isinstance(rag, dict) else None,
    )
    rag_release_ready = (
        isinstance(rag, dict)
        and binding["valid"]
        and isinstance(digests, dict)
        and set(digests) == RAG_DIGEST_FIELDS
        and all(SHA256.fullmatch(str(digests[field])) for field in RAG_DIGEST_FIELDS)
        and digests == binding.get("release_digests")
        and rag.get("ingestion_status") == "completed"
        and ingestion == binding.get("ingestion")
        and category_results == binding.get("category_results")
        and metric_results == binding.get("metric_results")
        and nonempty(monitoring.get("owner"))
        and nonempty(monitoring.get("freshness_slo"))
        and nonempty(monitoring.get("alert_route"))
        and set(monitoring.get("canary_metrics", [])) <= set(metric_results)
        and bool(monitoring.get("canary_metrics"))
    )
    if not rag_release_ready:
        issues.append(
            "RAG release must bind the required EV-RAG artifact, full corpus/index/configuration "
            "digests, observed ingestion, 8 category results, 10 metrics, and owned monitoring"
        )

    metrics = evidence.get("metrics", {})
    required_metrics = set(task.get("required_metrics", []))
    metrics_complete = (
        isinstance(metrics, dict)
        and required_metrics <= metrics.keys()
        and all(isinstance(metrics[key], (int, float)) and metrics[key] >= 0 for key in required_metrics)
    )
    if not metrics_complete:
        issues.append("metrics must contain every required non-negative measure")

    valid = not issues
    return {
        "workflow_id": evidence.get("workflow_id"),
        "valid": valid,
        "state_count": len(events) if isinstance(events, list) else 0,
        "scope_ok": scope_ok,
        "authority_expanded": evidence.get("authority_expanded"),
        "gates_passed": gates_passed,
        "separation_of_duties": separation_of_duties,
        "rollback_ready": rollback_ready,
        "rag_evidence_bound": binding["valid"],
        "rag_release_ready": rag_release_ready,
        "metrics_complete": metrics_complete,
        "secrets_in_evidence": evidence.get("secrets_included") is not False,
        "commands_executed": False,
        "credentials_read": False,
        "network_used": False,
        "issues": issues,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python workflow_check.py <task.json> <evidence.json>", file=sys.stderr)
        return 2
    try:
        task = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        evidence = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "issues": [str(exc)]}, indent=2))
        return 2
    report = evaluate(task, evidence)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
