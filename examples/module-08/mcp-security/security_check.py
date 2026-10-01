"""Evaluate synthetic MCP high-assurance policy evidence without touching a server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


Check = tuple[str, str, Callable[[Any], bool]]


def present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def true(value: Any) -> bool:
    return value is True


def false(value: Any) -> bool:
    return value is False


def bounded_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and "*" not in value and "**" not in value


def exact(value: Any, expected: Any) -> bool:
    return value == expected


CHECKS: dict[str, list[Check]] = {
    "admission": [
        ("ADM-01", "source.owner", present),
        ("ADM-02", "source.version_pinned", true),
        ("ADM-03", "source.digest_verified", true),
        ("ADM-04", "source.dependency_lock_reviewed", true),
        ("ADM-05", "source.startup_command_reviewed", true),
        ("ADM-06", "source.capability_baseline_recorded", true),
        ("ADM-07", "source.change_requires_reapproval", true),
        ("ADM-08", "least_privilege.default_deny", true),
        ("ADM-09", "least_privilege.non_elevated", true),
        ("ADM-10", "least_privilege.filesystem_roots", bounded_list),
        ("ADM-11", "least_privilege.environment_allowlist", bounded_list),
        ("ADM-12", "least_privilege.egress_allowlist", bounded_list),
    ],
    "identity": [
        ("ID-01", "identity.protected_resource_metadata", true),
        ("ID-02", "identity.resource_parameter_on_both_requests", true),
        ("ID-03", "identity.issuer_validation", true),
        ("ID-04", "identity.audience_validation", true),
        ("ID-05", "identity.pkce_method", lambda v: exact(v, "S256")),
        ("ID-06", "identity.exact_redirect_match", true),
        ("ID-07", "identity.single_use_state", true),
        ("ID-08", "identity.read_write_scopes_split", true),
        ("ID-09", "identity.object_and_tenant_authorization", true),
        ("ID-10", "identity.token_passthrough", false),
        ("ID-11", "identity.downstream_token_separate", true),
        ("ID-12", "identity.access_token_ttl_seconds", lambda v: isinstance(v, int) and 0 < v <= 900),
        ("ID-13", "identity.refresh_token_rotation", true),
        ("ID-14", "identity.protocol_version", lambda v: exact(v, "2026-07-28")),
        ("ID-15", "identity.per_request_protocol_and_capability_validation", true),
        ("ID-16", "identity.every_request_authorized", true),
        ("ID-17", "identity.server_discover_implemented", true),
        ("ID-18", "identity.client_info_used_as_authentication", false),
        ("ID-19", "identity.issuer_and_token_audience_validation", true),
    ],
    "runtime": [
        ("RUN-01", "runtime.local_transport", lambda v: exact(v, "stdio")),
        ("RUN-02", "runtime.shell_wrapper", false),
        ("RUN-03", "runtime.local_http_bind", lambda v: v in {"disabled", "127.0.0.1", "::1"}),
        ("RUN-04", "runtime.origin_validation", true),
        ("RUN-05", "runtime.https_required_for_remote", true),
        ("RUN-06", "runtime.authenticate_every_remote_request", true),
        ("RUN-07", "runtime.ssrf_address_filtering", true),
        ("RUN-08", "runtime.redirect_revalidation", true),
        ("RUN-09", "runtime.dns_rebinding_defense", true),
        ("RUN-10", "least_privilege.egress_allowlist", bounded_list),
        ("RUN-11", "least_privilege.filesystem_roots", bounded_list),
        ("RUN-12", "least_privilege.environment_allowlist", bounded_list),
        ("RUN-13", "runtime.secret_storage", lambda v: exact(v, "external-reference")),
        ("RUN-14", "runtime.literal_secrets_in_config", false),
        ("RUN-15", "runtime.sandboxed", true),
        ("RUN-16", "runtime.resource_limits", true),
        ("RUN-17", "runtime.startup_and_call_timeouts", true),
        ("RUN-18", "runtime.stdout_protocol_only", true),
    ],
    "tools": [
        ("TOOL-01", "tools.default_deny", true),
        ("TOOL-02", "tools.approved_tools", bounded_list),
        ("TOOL-03", "tools.schema_hash_baseline", true),
        ("TOOL-04", "tools.strict_input_schema", true),
        ("TOOL-05", "tools.additional_properties_rejected", true),
        ("TOOL-06", "tools.semantic_validation", true),
        ("TOOL-07", "tools.object_and_tenant_authorization", true),
        ("TOOL-08", "tools.raw_shell_interpolation", false),
        ("TOOL-09", "tools.risk_tiers_assigned", true),
        ("TOOL-10", "tools.sensitive_actions_require_approval", true),
        ("TOOL-11", "tools.idempotency_and_deduplication", true),
        ("TOOL-12", "tools.unknown_outcomes_not_retried", true),
        ("TOOL-13", "tools.output_treated_as_untrusted", true),
        ("TOOL-14", "tools.output_redaction_and_size_limit", true),
        ("TOOL-15", "tools.annotations_used_as_authorization", false),
        ("TOOL-16", "tools.pinned_tool_inventory", true),
        ("TOOL-17", "tools.side_effect_approval", true),
    ],
    "operations": [
        ("OPS-01", "operations.security_event_schema", true),
        ("OPS-02", "operations.sensitive_value_redaction_tested", true),
        ("OPS-03", "operations.inventory_and_config_hash_monitored", true),
        ("OPS-04", "operations.read_write_and_approval_metrics", true),
        ("OPS-05", "operations.auth_policy_origin_alerts", true),
        ("OPS-06", "operations.sensitive_output_alert", true),
        ("OPS-07", "operations.synthetic_read_canary", true),
        ("OPS-08", "operations.disable_and_absence_tested", true),
        ("OPS-09", "operations.credential_and_grant_revocation", true),
        ("OPS-10", "operations.incident_runbook", true),
        ("OPS-11", "operations.recovery_requires_reapproval", true),
        ("OPS-12", "operations.evidence_retention_defined", true),
    ],
}


def get_path(profile: dict[str, Any], dotted: str) -> Any:
    value: Any = profile
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def evaluate(profile: dict[str, Any], section: str) -> dict[str, Any]:
    selected = list(CHECKS) if section == "all" else [section]
    results: list[dict[str, Any]] = []
    for selected_section in selected:
        for control_id, path, predicate in CHECKS[selected_section]:
            passed = False
            try:
                passed = bool(predicate(get_path(profile, path)))
            except (TypeError, ValueError):
                passed = False
            results.append(
                {"control_id": control_id, "section": selected_section, "path": path, "passed": passed}
            )
    failed = [item["control_id"] for item in results if not item["passed"]]
    return {
        "profile_id": profile.get("profile_id"),
        "section": section,
        "valid": not failed,
        "checks_run": len(results),
        "checks_passed": len(results) - len(failed),
        "failed_control_ids": failed,
        "credentials_read": False,
        "network_used": False,
        "server_started": False,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    parser.add_argument("--section", choices=["all", *CHECKS], default="all")
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 2
    report = evaluate(profile, args.section)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
