#!/usr/bin/env python3
"""Validate a synthetic Codex best-practice packet without external actions."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any


EXAMPLES_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = EXAMPLES_ROOT.parent
if str(EXAMPLES_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_ROOT))
from rag_evidence_binding import SHA256, verify_rag_evidence  # noqa: E402

POSTURES = ["Explore", "Plan", "Implement", "Test", "Review"]
REVIEW_CRITERIA = {"acceptance", "correctness", "security", "tests", "scope"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def relative_path(value: str) -> bool:
    path = PurePosixPath(value.replace("\\", "/"))
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def check(task: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []

    if not task.get("practice_id") or record.get("practice_id") != task.get("practice_id"):
        issues.append("practice_id must match the task contract")

    contract = record.get("contract", {})
    contract_ready = (
        bool(contract.get("goal"))
        and bool(contract.get("context_refs"))
        and bool(contract.get("constraints"))
        and len(contract.get("done_when", [])) >= 3
        and bool(contract.get("allowed_paths"))
        and all(relative_path(path) for path in contract.get("allowed_paths", []))
        and bool(contract.get("excluded_paths"))
        and contract.get("start_ref") not in {None, "", "latest"}
    )
    if not contract_ready:
        issues.append("contract needs goal, context, constraints, done evidence, bounded paths, exclusions, and immutable start")

    context = record.get("context", {})
    context_curated = (
        {"examples/rag-reference/README.md", "rag-config.json", "corpus-manifest.json", "AGENTS.md"}.issubset(set(context.get("included", [])))
        and {"credentials", "production-data"}.issubset(set(context.get("excluded", [])))
        and bool(context.get("assumptions"))
        and bool(context.get("unknowns"))
        and context.get("acceptance_linked") is True
    )
    if not context_curated:
        issues.append("context must be acceptance-linked, relevant, explicit about unknowns, and exclude restricted data")

    guidance = record.get("guidance", {})
    guidance_scoped = (
        bool(guidance.get("one_off"))
        and "AGENTS.md" in guidance.get("repo_sources", [])
        and guidance.get("project_config_reviewed") is True
        and guidance.get("nearest_scope_wins") is True
        and guidance.get("conflicts_resolved") is True
        and guidance.get("concise_and_actionable") is True
    )
    if not guidance_scoped:
        issues.append("guidance must use the smallest durable scope and resolve effective instruction precedence")

    plan = record.get("plan", {})
    steps = plan.get("steps", [])
    plan_risk_aligned = (
        plan.get("postures") == POSTURES
        and plan.get("risk") in {"low", "medium", "high"}
        and len(steps) >= 3
        and all(
            isinstance(step, dict)
            and bool(step.get("id"))
            and bool(step.get("deliverable"))
            and bool(step.get("validation"))
            for step in steps
        )
        and len(plan.get("decision_points", [])) >= 2
    )
    if not plan_risk_aligned:
        issues.append("plan must declare ordered postures, risk, validated deliverables, and decision points")

    permissions = record.get("permissions", {})
    permissions_least = (
        permissions.get("workspace_only") is True
        and permissions.get("network_allowed") is False
        and permissions.get("authority_expanded") is False
        and bool(permissions.get("approval_boundary"))
        and permissions.get("synthetic_data_only") is True
        and permissions.get("secrets_included") is False
    )
    if not permissions_least:
        issues.append("permissions must remain workspace-only, network-off, synthetic, secret-free, and approval bounded")

    tools = record.get("tools", {})
    plugin_inventory = tools.get("plugin_inventory", [])
    tools_minimal = (
        bool(tools.get("selected"))
        and set(tools.get("selected", [])).issubset(set(task.get("allowed_tools", [])))
        and tools.get("external") == []
        and bool(tools.get("selection_reason"))
        and set(tools.get("side_effects", [])).issubset({"workspace-write", "local-test-process", "local-index-write"})
        and tools.get("mcp_needed") is False
        and isinstance(plugin_inventory, list)
        and all(
            isinstance(plugin, dict)
            and plugin.get("artifact_kind") == "synthetic-training-fixture"
            and str(plugin.get("id", "")).startswith("synthetic-")
            and bool(plugin.get("version"))
            and SHA256.fullmatch(str(plugin.get("digest", ""))) is not None
            and isinstance(plugin.get("permissions"), list)
            for plugin in plugin_inventory
        )
        and tools.get("plugin_results_treated_as_untrusted") is True
        and tools.get("hot_refresh_reapproval_required") is True
    )
    if not tools_minimal:
        issues.append("tool/plugin selection must be justified, versioned, permission-reviewed, local, result-untrusted, side-effect bounded, and avoid unnecessary MCP")

    budget = record.get("budget", {})
    budget_bounded = (
        isinstance(budget.get("time_minutes"), int)
        and budget.get("time_minutes", 0) > 0
        and isinstance(budget.get("max_iterations"), int)
        and 0 < budget.get("max_iterations", 0) <= 3
        and isinstance(budget.get("actual_minutes"), int)
        and 0 <= budget.get("actual_minutes", -1) <= budget.get("time_minutes", -1)
        and isinstance(budget.get("actual_iterations"), int)
        and 0 <= budget.get("actual_iterations", -1) <= budget.get("max_iterations", -1)
        and bool(budget.get("escalation_trigger"))
    )
    if not budget_bounded:
        issues.append("time and iteration use must stay within a declared budget with an escalation trigger")

    validation = record.get("validation", [])
    check_ids = [item.get("id") for item in validation if isinstance(item, dict)]
    validation_layered = (
        isinstance(validation, list)
        and len(check_ids) == len(validation) == len(set(check_ids))
        and set(task.get("required_checks", [])).issubset(set(check_ids))
        and all(
            item.get("status") == "pass"
            and bool(item.get("command"))
            and bool(item.get("output_ref"))
            and item.get("fabricated") is False
            for item in validation
        )
    )
    if not validation_layered:
        issues.append("validation needs unique software, functional RAG, RAG security, operations, diff, and review evidence without fabrication")

    rag_operations = record.get("rag_operations", {})
    digests = rag_operations.get("digests", {}) if isinstance(rag_operations, dict) else {}
    ingestion = rag_operations.get("ingestion", {}) if isinstance(rag_operations, dict) else {}
    category_results = rag_operations.get("category_results", {}) if isinstance(rag_operations, dict) else {}
    metric_results = rag_operations.get("metric_results", {}) if isinstance(rag_operations, dict) else {}
    binding = verify_rag_evidence(
        REPO_ROOT,
        task.get("rag_observed_evidence"),
        rag_operations.get("observed_evidence") if isinstance(rag_operations, dict) else None,
    )
    rag_operations_ready = (
        isinstance(rag_operations, dict)
        and binding["valid"]
        and bool(rag_operations.get("owner"))
        and set(digests) == {"corpus", "index", "configuration"}
        and all(SHA256.fullmatch(str(digests.get(name, ""))) for name in digests)
        and digests == binding.get("release_digests")
        and ingestion == binding.get("ingestion")
        and category_results == binding.get("category_results")
        and metric_results == binding.get("metric_results")
        and rag_operations.get("functional_eval") == "pass"
        and rag_operations.get("security_eval") == "pass"
        and bool(rag_operations.get("alert_route"))
        and bool(rag_operations.get("canary_metrics"))
        and set(rag_operations.get("canary_metrics", [])) <= set(metric_results)
        and bool(rag_operations.get("rollback_or_reindex"))
    )
    if not rag_operations_ready:
        issues.append(
            "RAG operations must bind the required EV-RAG artifact and full digests to the "
            "observed ingestion, 8 categories, 10 metrics, alerting, and rollback/reindex"
        )

    review = record.get("review", {})
    review_ready = (
        bool(review.get("target_ref"))
        and REVIEW_CRITERIA.issubset(set(review.get("criteria", [])))
        and bool(review.get("reviewer"))
        and review.get("reviewer") != review.get("author")
        and review.get("read_only") is True
        and review.get("findings_adjudicated") is True
        and bool(review.get("residual_risk"))
    )
    if not review_ready:
        issues.append("review must be target-pinned, independent, read-only, complete, adjudicated, and risk aware")

    reuse = record.get("reuse", {})
    reuse_evidence_based = (
        isinstance(reuse.get("repeat_count"), int)
        and reuse.get("repeat_count", -1) >= 0
        and reuse.get("current_surface") in {"task-prompt", "AGENTS.md", "skill", "plugin", "automation"}
        and bool(reuse.get("promotion_rule"))
        and not (reuse.get("automated") is True and reuse.get("repeat_count", 0) < 3)
        and bool(reuse.get("plugin_admission_rule"))
        and bool(reuse.get("removal_owner"))
        and reuse.get("event_triggered") is False
    )
    if not reuse_evidence_based:
        issues.append("reuse must progress from prompt to guidance, skill, or automation only after repeated stable evidence")

    retrospective = record.get("retrospective", {})
    retrospective_measurable = all(
        bool(retrospective.get(field))
        for field in ["observed_friction", "root_cause", "improvement", "measure", "owner"]
    )
    if not retrospective_measurable:
        issues.append("retrospective needs observed friction, root cause, improvement, measure, and owner")

    stop = record.get("stop", {})
    evidence_index = record.get("evidence_index", {})
    required_evidence = set(task.get("required_evidence", []))
    values = list(evidence_index.values()) if isinstance(evidence_index, dict) else []
    stop_ready = (
        bool(stop.get("condition"))
        and stop.get("met") is True
        and isinstance(stop.get("unresolved"), list)
        and bool(stop.get("next_owner"))
        and isinstance(evidence_index, dict)
        and required_evidence == set(evidence_index)
        and len(values) == len(set(values))
        and all(isinstance(value, str) and value.startswith("EV-") for value in values)
    )
    if not stop_ready:
        issues.append("stop must be explicit, owned, honest about unresolved work, and indexed across twelve practices")

    critical_safety_failure = bool(record.get("critical_safety_failures"))
    if critical_safety_failure:
        issues.append("critical safety failures require remediation")

    runtime = record.get("runtime", {})
    external_actions = any(
        runtime.get(field) is not False
        for field in ["commands_executed", "model_called", "network_used", "credentials_read", "git_operations_run"]
    )
    if external_actions:
        issues.append("the offline checker must report no external actions")

    fields = {
        "contract_ready": contract_ready,
        "context_curated": context_curated,
        "guidance_scoped": guidance_scoped,
        "plan_risk_aligned": plan_risk_aligned,
        "permissions_least": permissions_least,
        "tools_minimal": tools_minimal,
        "budget_bounded": budget_bounded,
        "validation_layered": validation_layered,
        "review_ready": review_ready,
        "reuse_evidence_based": reuse_evidence_based,
        "retrospective_measurable": retrospective_measurable,
        "stop_ready": stop_ready,
    }
    return {
        "practice_id": task.get("practice_id"),
        "valid": not issues,
        **fields,
        "rag_evidence_bound": binding["valid"],
        "rag_operations_ready": rag_operations_ready,
        "practice_count": len(fields),
        "critical_safety_failure": critical_safety_failure,
        "commands_executed": False,
        "model_called": False,
        "network_used": False,
        "credentials_read": False,
        "git_operations_run": False,
        "issues": issues,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: practice_check.py TASK_JSON RECORD_JSON", file=sys.stderr)
        return 2
    try:
        report = check(load(Path(argv[1])), load(Path(argv[2])))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
