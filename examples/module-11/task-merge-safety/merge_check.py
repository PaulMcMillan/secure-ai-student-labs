"""Validate synthetic multi-agent task graphs and integration evidence."""

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
ALLOWED_AUTHORITY = {"read", "write", "integrate"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def acyclic(tasks: list[dict[str, Any]]) -> bool:
    ids = {task.get("id") for task in tasks}
    dependencies = {task.get("id"): set(task.get("depends_on", [])) for task in tasks}
    if None in ids or any(not deps <= ids for deps in dependencies.values()):
        return False
    remaining = set(ids)
    resolved: set[str] = set()
    while remaining:
        ready = {task_id for task_id in remaining if dependencies[task_id] <= resolved}
        if not ready:
            return False
        resolved.update(ready)
        remaining.difference_update(ready)
    return True


def evaluate(contract: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    if evidence.get("workflow_id") != contract.get("workflow_id"):
        issues.append("workflow_id does not match the contract")
    if evidence.get("authority_expanded") is not False:
        issues.append("authority_expanded must be false")
    if evidence.get("secrets_included") is not False:
        issues.append("secrets_included must be false")

    rag_release = evidence.get("rag_release", {})
    binding = verify_rag_evidence(
        REPO_ROOT,
        contract.get("rag_observed_evidence"),
        rag_release.get("observed_evidence") if isinstance(rag_release, dict) else None,
    )
    source_artifacts = binding.get("artifact", {}).get("source_artifacts", {})
    evaluation_cases_digest = (
        source_artifacts.get("evaluation_cases", {}).get("sha256")
        if isinstance(source_artifacts, dict)
        else None
    )
    expected_digests = {
        **binding.get("release_digests", {}),
        "evaluation_cases": evaluation_cases_digest,
    }
    rag_release_digests = (
        rag_release.get("digests", {}) if isinstance(rag_release.get("digests"), dict) else {}
    ) if isinstance(rag_release, dict) else {}
    rag_release_ready = (
        isinstance(rag_release, dict)
        and binding["valid"]
        and set(rag_release_digests)
        == {"corpus", "index", "configuration", "evaluation_cases"}
        and all(
            SHA256.fullmatch(str(value)) is not None
            for value in rag_release_digests.values()
        )
        and rag_release_digests == expected_digests
    )
    if not rag_release_ready:
        issues.append("shared RAG release must bind full corpus/index/configuration/evaluation digests to the required EV-RAG artifact")

    operations = evidence.get("operations", {})
    operations_ready = (
        isinstance(operations, dict)
        and nonempty(operations.get("runtime_interface"))
        and operations.get("runtime_interface") != "unknown"
        and operations.get("permission_inheritance_verified") is True
        and operations.get("goal_budget_accounted") is True
        and nonempty(operations.get("cancellation_owner"))
        and isinstance(operations.get("max_parallel_observed"), int)
        and operations.get("max_parallel_observed", 0) <= contract.get("max_parallel", -1)
    )
    if not operations_ready:
        issues.append("operations must record the runtime interface, inherited permissions, root goal budget, cancellation owner, and bounded concurrency")

    tasks = evidence.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        issues.append("tasks must be a non-empty list")
        tasks = []
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if len(ids) != len(set(ids)) or any(not nonempty(task_id) for task_id in ids):
        issues.append("task IDs must be unique non-empty strings")
    by_id = {task.get("id"): task for task in tasks if isinstance(task, dict) and nonempty(task.get("id"))}

    dag_valid = acyclic(tasks) if tasks and len(by_id) == len(tasks) else False
    if not dag_valid:
        issues.append("task graph must be acyclic with valid dependencies")

    allowed_paths = set(contract.get("allowed_paths", []))
    scope_ok = True
    bases_ok = True
    outputs: list[str] = []
    writer_ids: list[str] = []
    writer_owners: set[str] = set()
    rag_bindings_consistent = rag_release_ready
    rag_bound_task_ids = set(contract.get("rag_bound_task_ids", []))
    for task in tasks:
        paths = task.get("paths", [])
        write_paths = task.get("write_paths", [])
        if not isinstance(paths, list) or not set(paths) <= allowed_paths:
            scope_ok = False
        if not isinstance(write_paths, list) or not set(write_paths) <= set(paths):
            scope_ok = False
        if task.get("base_commit") != contract.get("base_commit") or not GIT_SHA.fullmatch(str(task.get("base_commit", ""))):
            bases_ok = False
        if task.get("id") in rag_bound_task_ids and (
            task.get("rag_release_ref") != contract.get("rag_observed_evidence", {}).get("id")
            or task.get("rag_release_digests") != expected_digests
        ):
            rag_bindings_consistent = False
        if task.get("authority") not in ALLOWED_AUTHORITY:
            issues.append(f"task {task.get('id')} has unsupported authority")
        if not nonempty(task.get("owner")) or not nonempty(task.get("role")):
            issues.append(f"task {task.get('id')} must name owner and role")
        if task.get("status") != "complete":
            issues.append(f"task {task.get('id')} must be complete")
        budget = task.get("budget", {})
        if not (
            isinstance(budget, dict)
            and isinstance(budget.get("max_minutes"), int)
            and budget.get("max_minutes", 0) > 0
            and isinstance(budget.get("max_attempts"), int)
            and 0 < budget.get("max_attempts", 0) <= 3
            and nonempty(task.get("stop_condition"))
        ):
            issues.append(f"task {task.get('id')} must have finite time/attempt budgets and a stop condition")
        if not nonempty(task.get("output")):
            issues.append(f"task {task.get('id')} must own an output")
        else:
            outputs.append(task["output"])
        if task.get("authority") == "write":
            writer_ids.append(task.get("id"))
            writer_owners.add(task.get("owner"))
            if not write_paths:
                issues.append(f"writer {task.get('id')} must declare write paths")
            if not nonempty(task.get("isolation")) or task.get("isolation") in {"shared", "shared-checkout", "none"}:
                issues.append(f"writer {task.get('id')} must use isolated state")
    if not scope_ok:
        issues.append("task paths and write paths must remain within allowed scope")
    if not bases_ok:
        issues.append("every task must use the contract's immutable base")
    if len(outputs) != len(set(outputs)):
        issues.append("each task must own a distinct output")
    required_roles = set(contract.get("required_roles", []))
    actual_roles = {task.get("role") for task in tasks}
    if not required_roles <= actual_roles:
        issues.append("all required task roles must be present")
    if rag_bound_task_ids != set(by_id):
        rag_bindings_consistent = False
        issues.append("rag_bound_task_ids must name every task exactly once")

    waves = evidence.get("waves", [])
    schedule_valid = isinstance(waves, list) and bool(waves)
    writes_disjoint = True
    scheduled: list[str] = []
    completed_before: set[str] = set()
    max_parallel = contract.get("max_parallel")
    if schedule_valid:
        for wave in waves:
            if not isinstance(wave, list) or not wave or not isinstance(max_parallel, int) or len(wave) > max_parallel:
                schedule_valid = False
                continue
            wave_tasks = [by_id.get(task_id) for task_id in wave]
            if any(task is None for task in wave_tasks):
                schedule_valid = False
                continue
            for task in wave_tasks:
                if not set(task.get("depends_on", [])) <= completed_before:
                    schedule_valid = False
            for left_index, left in enumerate(wave_tasks):
                left_writes = set(left.get("write_paths", []))
                for right in wave_tasks[left_index + 1:]:
                    if left_writes & set(right.get("write_paths", [])):
                        writes_disjoint = False
            scheduled.extend(wave)
            completed_before.update(wave)
        if scheduled != ids or len(scheduled) != len(set(scheduled)):
            schedule_valid = False
    if not schedule_valid:
        issues.append("waves must schedule every task once, after dependencies, within max_parallel")
    if not writes_disjoint:
        issues.append("parallel tasks must have disjoint write sets")

    reviewers = [task for task in tasks if task.get("role") == "reviewer"]
    review_independent = len(reviewers) == 1
    if review_independent:
        reviewer = reviewers[0]
        review_independent = (
            reviewer.get("authority") == "read"
            and reviewer.get("owner") not in writer_owners
            and set(writer_ids) <= set(reviewer.get("depends_on", []))
        )
    if not review_independent:
        issues.append("one read-only independent reviewer must depend on every writer")

    reports = evidence.get("reports", [])
    report_task_ids = set(contract.get("rag_report_task_ids", []))
    reports_ready = (
        isinstance(reports, list)
        and len(reports) == len(report_task_ids)
        and {report.get("task_id") for report in reports if isinstance(report, dict)} == report_task_ids
    )
    if reports_ready:
        for report in reports:
            producer = by_id.get(report.get("task_id"), {})
            if (
                report.get("output") != producer.get("output")
                or report.get("rag_release_ref") != contract.get("rag_observed_evidence", {}).get("id")
                or report.get("rag_release_digests") != expected_digests
            ):
                reports_ready = False
                break
    if not reports_ready:
        rag_bindings_consistent = False
        issues.append("quality and security reports must match their producer and the shared RAG release digests")

    integration = evidence.get("integration", {})
    integrators = [task for task in tasks if task.get("role") == "integrator"]
    required_validation = set(contract.get("required_validation", []))
    integration_binding_ok = (
        isinstance(integration, dict)
        and integration.get("rag_release_ref") == contract.get("rag_observed_evidence", {}).get("id")
        and integration.get("rag_release_digests") == expected_digests
    )
    if not integration_binding_ok:
        rag_bindings_consistent = False
    integration_ready = (
        isinstance(integration, dict)
        and len(integrators) == 1
        and integration.get("task_id") == integrators[0].get("id")
        and integration.get("owner") == integrators[0].get("owner")
        and integration.get("merge_order") == writer_ids
        and nonempty(integration.get("conflict_resolution"))
        and required_validation <= set(integration.get("validation", []))
        and integration_binding_ok
        and integration.get("result") == "pass"
        and isinstance(integration.get("residual_risks"), list)
        and bool(integration.get("residual_risks"))
        and nonempty(integration.get("stop_condition"))
    )
    if not integration_ready:
        issues.append("integration must have one owner, writer merge order, conflict policy, all gates, risk, and stop")
    if not rag_bindings_consistent:
        issues.append("tasks, reports, and integration must use one immutable RAG release")

    valid = not issues
    return {
        "workflow_id": evidence.get("workflow_id"),
        "valid": valid,
        "task_count": len(tasks),
        "dag_valid": dag_valid,
        "schedule_valid": schedule_valid,
        "writes_disjoint": writes_disjoint,
        "bases_ok": bases_ok,
        "scope_ok": scope_ok,
        "review_independent": review_independent,
        "integration_ready": integration_ready,
        "rag_evidence_bound": binding["valid"],
        "rag_release_consistent": rag_bindings_consistent,
        "operations_ready": operations_ready,
        "authority_expanded": evidence.get("authority_expanded"),
        "secrets_in_evidence": evidence.get("secrets_included") is not False,
        "agents_spawned": False,
        "git_operations_run": False,
        "credentials_read": False,
        "network_used": False,
        "issues": issues,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python merge_check.py <task.json> <evidence.json>", file=sys.stderr)
        return 2
    try:
        contract = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        evidence = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "issues": [str(exc)]}, indent=2))
        return 2
    report = evaluate(contract, evidence)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
