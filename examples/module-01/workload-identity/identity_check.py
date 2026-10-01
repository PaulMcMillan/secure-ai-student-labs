"""Validate a synthetic workload identity and isolation profile offline."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_nonempty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(is_nonempty_string(item) for item in value)
    )


def as_object(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def contains_forbidden(values: list[str], forbidden: set[str]) -> bool:
    return any(value.lower() in forbidden for value in values)


def evaluate(contract: dict, profile: dict) -> dict:
    if not isinstance(profile, dict):
        profile = {}
    identity = as_object(profile.get("workload_identity"))
    mutual = as_object(profile.get("mutual_verification"))
    runtime = as_object(profile.get("runtime_attestation"))
    authorization = as_object(profile.get("authorization"))
    secrets = as_object(profile.get("secrets"))
    network = as_object(profile.get("network"))
    execution = as_object(profile.get("execution"))
    approval = as_object(profile.get("human_approval"))

    forbidden = {value.lower() for value in contract["forbidden_wildcards"]}
    resource_classes = contract["required_resource_classes"]
    resource_lists_present = all(
        is_nonempty_string_list(authorization.get(name)) for name in resource_classes
    )
    no_resource_wildcards = resource_lists_present and all(
        not contains_forbidden(authorization[name], forbidden)
        for name in resource_classes
    )

    zones = as_object(network.get("zones"))
    required_zones = contract["required_network_zones"]
    zone_values = [zones.get(name) for name in required_zones]
    actions = (
        authorization["actions"]
        if is_nonempty_string_list(authorization.get("actions"))
        else []
    )
    allowed_environments = (
        runtime["allowed_execution_environments"]
        if is_nonempty_string_list(runtime.get("allowed_execution_environments"))
        else []
    )
    vault_references = (
        secrets["vault_references"]
        if is_nonempty_string_list(secrets.get("vault_references"))
        else []
    )
    authorized_egress = (
        network["authorized_egress"]
        if is_nonempty_string_list(network.get("authorized_egress"))
        else []
    )
    approval_classes = (
        approval["required_for"]
        if is_nonempty_string_list(approval.get("required_for"))
        else []
    )

    schema_errors: list[str] = []

    def require(condition: bool, field: str) -> None:
        if not condition:
            schema_errors.append(field)

    require(is_nonempty_string(profile.get("profile")), "profile")
    for name in [
        "workload_identity",
        "mutual_verification",
        "runtime_attestation",
        "authorization",
        "secrets",
        "network",
        "execution",
        "human_approval",
    ]:
        require(isinstance(profile.get(name), dict), name)
    require(is_nonempty_string(identity.get("id")), "workload_identity.id")
    require(is_nonempty_string(identity.get("proof_type")), "workload_identity.proof_type")
    require(
        type(identity.get("credential_lifetime_minutes")) is int,
        "workload_identity.credential_lifetime_minutes",
    )
    for field in ["dedicated", "shared_service_account", "automatic_rotation"]:
        require(type(identity.get(field)) is bool, f"workload_identity.{field}")
    for field in [
        "client_verifies_server",
        "server_verifies_workload",
        "audience_bound",
        "issuer_and_trust_domain_validated",
    ]:
        require(type(mutual.get(field)) is bool, f"mutual_verification.{field}")
    for field in ["node_attested", "workload_attested", "image_digest_verified"]:
        require(type(runtime.get(field)) is bool, f"runtime_attestation.{field}")
    require(
        is_nonempty_string_list(runtime.get("allowed_execution_environments")),
        "runtime_attestation.allowed_execution_environments",
    )
    require(
        is_nonempty_string(runtime.get("current_execution_environment")),
        "runtime_attestation.current_execution_environment",
    )
    for name in resource_classes:
        require(
            is_nonempty_string_list(authorization.get(name)),
            f"authorization.{name}",
        )
    require(is_nonempty_string_list(authorization.get("actions")), "authorization.actions")
    for field in ["tenant_bound", "object_authorization"]:
        require(type(authorization.get(field)) is bool, f"authorization.{field}")
    require(is_nonempty_string_list(secrets.get("vault_references")), "secrets.vault_references")
    for field in [
        "inline_secrets",
        "prompt_secrets",
        "container_baked_secrets",
        "model_file_secrets",
    ]:
        require(type(secrets.get(field)) is bool, f"secrets.{field}")
    require(type(network.get("default_deny")) is bool, "network.default_deny")
    require(isinstance(network.get("zones"), dict), "network.zones")
    for name, value in zip(required_zones, zone_values):
        require(is_nonempty_string(value), f"network.zones.{name}")
    require(is_nonempty_string_list(network.get("authorized_egress")), "network.authorized_egress")
    for field in ["sandboxed", "non_elevated", "workspace_scoped", "generated_code_network"]:
        require(type(execution.get(field)) is bool, f"execution.{field}")
    require(is_nonempty_string_list(approval.get("required_for")), "human_approval.required_for")
    require(
        type(approval.get("approver_must_be_independent")) is bool,
        "human_approval.approver_must_be_independent",
    )

    controls = {
        "dedicated_workload_identity": (
            is_nonempty_string(identity.get("id"))
            and identity.get("dedicated") is True
            and identity.get("shared_service_account") is False
        ),
        "short_lived_verifiable_identity": (
            identity.get("proof_type") in contract["allowed_proof_types"]
            and type(identity.get("credential_lifetime_minutes")) is int
            and 0 < identity["credential_lifetime_minutes"]
            <= contract["maximum_credential_lifetime_minutes"]
            and identity.get("automatic_rotation") is True
        ),
        "mutual_peer_verification": all(
            mutual.get(name) is True
            for name in [
                "client_verifies_server",
                "server_verifies_workload",
                "audience_bound",
                "issuer_and_trust_domain_validated",
            ]
        ),
        "attested_execution_location": (
            runtime.get("node_attested") is True
            and runtime.get("workload_attested") is True
            and runtime.get("image_digest_verified") is True
            and runtime.get("current_execution_environment")
            in allowed_environments
            and not contains_forbidden(allowed_environments, forbidden)
        ),
        "least_privilege_resources": (
            no_resource_wildcards
            and authorization.get("tenant_bound") is True
            and authorization.get("object_authorization") is True
            and bool(actions)
            and not contains_forbidden(actions, forbidden)
            and "admin" not in actions
        ),
        "vault_only_secrets": (
            bool(vault_references)
            and all(
                secrets.get(name) is False
                for name in [
                    "inline_secrets",
                    "prompt_secrets",
                    "container_baked_secrets",
                    "model_file_secrets",
                ]
            )
        ),
        "segmented_default_deny_network": (
            network.get("default_deny") is True
            and all(is_nonempty_string(value) for value in zone_values)
            and len(set(zone_values)) == len(required_zones)
            and bool(authorized_egress)
            and not contains_forbidden(authorized_egress, forbidden)
        ),
        "sandboxed_execution": all(
            execution.get(name) is expected
            for name, expected in [
                ("sandboxed", True),
                ("non_elevated", True),
                ("workspace_scoped", True),
                ("generated_code_network", False),
            ]
        ),
        "consequential_human_approval": (
            set(contract["required_approval_classes"])
            <= set(approval_classes)
            and approval.get("approver_must_be_independent") is True
        ),
    }

    failed = [name for name, passed in controls.items() if not passed]
    return {
        "valid": not failed and not schema_errors,
        "profile": profile.get("profile"),
        "controls": controls,
        "passed_controls": len(controls) - len(failed),
        "control_count": len(controls),
        "failed_controls": failed,
        "schema_errors": sorted(set(schema_errors)),
        "model_called": False,
        "network_used": False,
        "credentials_read": False,
        "certificates_issued": False,
        "external_actions": False,
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: identity_check.py IDENTITY_CONTRACT.json PROFILE.json")
        return 2
    report = evaluate(load(Path(sys.argv[1])), load(Path(sys.argv[2])))
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
