#!/usr/bin/env python3
"""Validate a synthetic Module 12 capstone evidence bundle without side effects."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


EXAMPLES_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = EXAMPLES_ROOT.parent
if str(EXAMPLES_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_ROOT))
from rag_evidence_binding import SHA256, verify_rag_evidence  # noqa: E402

REQUIRED_STATES = ["intake", "context", "plan", "implement", "test", "review", "release", "stop"]
REQUIRED_GATES = ["scope", "implementation", "validation", "review", "release"]
REQUIRED_POSTURES = ["Explore", "Plan", "Implement", "Test", "Review", "Release"]
SAFE_TOOLS = {"filesystem", "shell"}
GIT_SHA = re.compile(r"^[0-9a-f]{7,40}$")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def safe_relative(path: str) -> bool:
    candidate = PurePosixPath(path.replace("\\", "/"))
    return bool(path) and not candidate.is_absolute() and ".." not in candidate.parts


def validate(task: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []

    capstone_id = task.get("capstone_id")
    id_ok = bool(capstone_id) and record.get("capstone_id") == capstone_id
    if not id_ok:
        issues.append("capstone_id must match the task contract")

    scope = record.get("scope", {})
    allowed_paths = set(task.get("allowed_paths", []))
    changed_paths = scope.get("changed_paths", [])
    scope_ok = (
        isinstance(changed_paths, list)
        and bool(changed_paths)
        and all(isinstance(path, str) and safe_relative(path) and path in allowed_paths for path in changed_paths)
        and scope.get("goal") == task.get("goal")
        and GIT_SHA.fullmatch(str(scope.get("start_ref", ""))) is not None
        and scope.get("branch") not in {None, "", "main", "master"}
        and bool(scope.get("stop_condition"))
    )
    if not scope_ok:
        issues.append("scope must preserve the goal, immutable start, feature branch, allowed paths, and stop")

    instructions = record.get("instructions", {})
    instruction_trace = (
        {"AGENTS.md", "task.json"}.issubset(set(instructions.get("sources", [])))
        and instructions.get("conflicts_resolved") is True
        and {"standard-library-only", "synthetic-data", "no-network", "run-tests"}.issubset(
            set(instructions.get("trace", []))
        )
    )
    if not instruction_trace:
        issues.append("instruction sources, conflict resolution, and effective-rule trace are required")

    context = record.get("context", {})
    context_ready = (
        {"pricing.py", "tests/test_pricing.py", "task.json"}.issubset(set(context.get("included", [])))
        and {"credentials", "production-data"}.issubset(set(context.get("excluded", [])))
        and bool(context.get("assumptions"))
        and context.get("acceptance_linked") is True
        and context.get("synthetic_only") is True
    )
    if not context_ready:
        issues.append("context must be sufficient, acceptance-linked, synthetic, and privacy bounded")

    decision = record.get("decision", {})
    decision_recorded = (
        bool(decision.get("surface"))
        and bool(decision.get("rationale"))
        and decision.get("posture_sequence") == REQUIRED_POSTURES
        and decision.get("execution_shape") in {"single-agent", "sequential-delegation", "parallel-delegation"}
        and bool(decision.get("execution_reason"))
    )
    if not decision_recorded:
        issues.append("surface, posture sequence, execution shape, and rationale must be explicit")

    cost = record.get("cost", {})
    budget = cost.get("budget", {})
    actual = cost.get("actual", {})
    cost_bounded = (
        cost.get("risk") == task.get("risk")
        and cost.get("complexity") in {"bounded", "moderate", "complex"}
        and isinstance(budget.get("time_minutes"), int)
        and budget.get("time_minutes", 0) > 0
        and isinstance(budget.get("max_iterations"), int)
        and 0 < budget.get("max_iterations", 0) <= 3
        and isinstance(actual.get("time_minutes"), int)
        and actual.get("time_minutes", 0) <= budget.get("time_minutes", -1)
        and isinstance(actual.get("iterations"), int)
        and actual.get("iterations", 0) <= budget.get("max_iterations", -1)
        and bool(cost.get("escalation_trigger"))
    )
    if not cost_bounded:
        issues.append("cost evidence must match risk and stay within time, iteration, and escalation bounds")

    tools = record.get("tools", {})
    tool_controls = (
        bool(tools.get("allowed"))
        and set(tools.get("allowed", [])).issubset(SAFE_TOOLS)
        and tools.get("external_tools") == []
        and tools.get("network_allowed") is False
        and tools.get("authority_expanded") is False
        and bool(tools.get("approval_boundary"))
    )
    if not tool_controls:
        issues.append("tools must remain local, least-authority, network-off, and approval bounded")

    workflow = record.get("workflow", {})
    gates = workflow.get("gates", {})
    workflow_complete = workflow.get("states") == REQUIRED_STATES and all(
        gates.get(gate) == "pass" for gate in REQUIRED_GATES
    )
    if not workflow_complete:
        issues.append("workflow states must be ordered and every required gate must pass")

    security = record.get("security", {})
    security_ready = (
        security.get("synthetic_data") is True
        and security.get("secrets_included") is False
        and security.get("production_data_used") is False
        and security.get("input_validation") is True
        and security.get("least_privilege") is True
        and security.get("dependency_change") is False
    )
    if not security_ready:
        issues.append("security evidence must prove synthetic data, no secrets, validation, and least privilege")

    rag = record.get("rag", {})
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
    rag_ready = (
        isinstance(rag, dict)
        and binding["valid"]
        and rag.get("reference_path") == task.get("rag_reference")
        and isinstance(rag.get("commands"), list)
        and len(rag.get("commands", [])) >= 3
        and all(isinstance(command, str) and command.strip() for command in rag.get("commands", []))
        and set(digests) == {"corpus", "index", "configuration"}
        and all(SHA256.fullmatch(str(digests[name])) for name in ["corpus", "index", "configuration"])
        and digests == binding.get("release_digests")
        and rag.get("ingestion_status") == "completed"
        and ingestion == binding.get("ingestion")
        and category_results == binding.get("category_results")
        and metric_results == binding.get("metric_results")
        and bool(monitoring.get("owner"))
        and isinstance(monitoring.get("freshness_slo_minutes"), (int, float))
        and monitoring.get("freshness_slo_minutes", 0) > 0
        and bool(monitoring.get("alert_route"))
        and bool(monitoring.get("canary_metrics"))
        and set(monitoring.get("canary_metrics", [])) <= set(metric_results)
        and bool(rag.get("rollback_or_reindex"))
        and rag.get("verified_during_integration") is True
    )
    if not rag_ready:
        issues.append(
            "RAG evidence must bind the required EV-RAG artifact and full digests to the observed "
            "ingestion, 8 categories, 10 metrics, owned monitoring, and rollback/reindex"
        )

    validation = record.get("validation", [])
    required_checks = set(task.get("required_checks", []))
    check_ids = [item.get("id") for item in validation if isinstance(item, dict)]
    tests_passed = (
        isinstance(validation, list)
        and len(check_ids) == len(set(check_ids))
        and required_checks.issubset(set(check_ids))
        and all(
            item.get("status") == "pass"
            and bool(item.get("command"))
            and bool(item.get("output_ref"))
            and item.get("fabricated") is False
            for item in validation
            if isinstance(item, dict)
        )
        and len(check_ids) == len(validation)
    )
    if not tests_passed:
        issues.append("validation must contain unique passing required checks with commands and real output references")

    review = record.get("review", {})
    findings = review.get("findings", [])
    review_independent = (
        bool(review.get("author"))
        and bool(review.get("reviewer"))
        and review.get("author") != review.get("reviewer")
        and review.get("read_only") is True
        and bool(review.get("target_ref"))
        and {"acceptance", "correctness", "security", "tests", "scope"}.issubset(
            set(review.get("coverage", []))
        )
        and isinstance(findings, list)
        and all(
            isinstance(item, dict)
            and bool(item.get("id"))
            and item.get("decision") in {"accepted", "rejected", "deferred", "remediated"}
            and bool(item.get("evidence"))
            for item in findings
        )
        and review.get("adjudicated") is True
    )
    if not review_independent:
        issues.append("review must be independent, read-only, target-pinned, complete, and adjudicated")

    release = record.get("release", {})
    release_ready = (
        bool(release.get("owner"))
        and release.get("all_gates_passed") is True
        and release.get("rollback_ready") is True
        and bool(release.get("rollback_path"))
        and bool(release.get("residual_risks"))
        and release.get("stop_condition_met") is True
    )
    if not release_ready:
        issues.append("release needs an owner, passing gates, rollback, residual risk, and stop evidence")

    evidence_index = record.get("evidence_index", {})
    required_domains = set(task.get("required_domains", []))
    index_values = list(evidence_index.values()) if isinstance(evidence_index, dict) else []
    evidence_traceable = (
        isinstance(evidence_index, dict)
        and required_domains.issubset(set(evidence_index))
        and all(isinstance(value, str) and value.startswith("EV-") for value in index_values)
        and len(index_values) == len(set(index_values))
    )
    if not evidence_traceable:
        issues.append("every required evidence domain needs a unique EV-prefixed index entry")

    critical_safety_failure = bool(record.get("critical_safety_failures"))
    if critical_safety_failure:
        issues.append("critical safety failures require remediation regardless of score")

    runtime = record.get("runtime", {})
    external_actions = any(
        runtime.get(field) is not False
        for field in ["commands_executed", "model_called", "network_used", "credentials_read", "git_operations_run"]
    )
    if external_actions:
        issues.append("the checker evidence must report no external actions")

    report = {
        "capstone_id": capstone_id,
        "valid": not issues,
        "scope_ok": scope_ok,
        "instruction_trace": instruction_trace,
        "context_ready": context_ready,
        "decision_recorded": decision_recorded,
        "cost_bounded": cost_bounded,
        "tool_controls": tool_controls,
        "workflow_complete": workflow_complete,
        "security_ready": security_ready,
        "rag_evidence_bound": binding["valid"],
        "rag_ready": rag_ready,
        "tests_passed": tests_passed,
        "review_independent": review_independent,
        "release_ready": release_ready,
        "evidence_traceable": evidence_traceable,
        "critical_safety_failure": critical_safety_failure,
        "evidence_domain_count": len(evidence_index) if isinstance(evidence_index, dict) else 0,
        "commands_executed": False,
        "model_called": False,
        "network_used": False,
        "credentials_read": False,
        "git_operations_run": False,
        "issues": issues,
    }
    return report


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: evidence_check.py TASK_JSON EVIDENCE_JSON", file=sys.stderr)
        return 2
    try:
        report = validate(load_json(Path(argv[1])), load_json(Path(argv[2])))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
