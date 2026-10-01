"""Validate a teaching Codex project config without activating it."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tomllib
from typing import Any


SENSITIVE_FRAGMENTS = ("password", "secret", "token", "api_key", "apikey")
COURSE_MODELS = {"gpt-5.6", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-6-astra"}
# This guard checks the current Codex config.toml schema, not the broader
# per-model effort capabilities exposed by the OpenAI API model pages.
CODEX_GPT56_CONFIG_EFFORTS = {"low", "medium", "high", "xhigh"}
CODEX_ASTRA_CONFIG_EFFORTS = {"low", "medium", "high", "xhigh"}
PROJECT_FORBIDDEN_KEYS = {
    "openai_base_url",
    "chatgpt_base_url",
    "apps_mcp_product_sku",
    "model_provider",
    "model_providers",
    "notify",
    "profile",
    "profiles",
    "experimental_realtime_ws_base_url",
    "otel",
}


def walk_keys(value: Any, prefix: str = "") -> list[str]:
    """Return dotted keys from nested dictionaries."""
    if not isinstance(value, dict):
        return []
    keys: list[str] = []
    for key, child in value.items():
        dotted = f"{prefix}.{key}" if prefix else str(key)
        keys.append(dotted)
        keys.extend(walk_keys(child, dotted))
    return keys


def validate_config(path: Path) -> dict[str, object]:
    """Return a safe validation report for a project-scoped teaching config."""
    with path.open("rb") as handle:
        config = tomllib.load(handle)

    keys = walk_keys(config)
    problems: list[str] = []

    for key in keys:
        lowered = key.lower()
        if any(fragment in lowered for fragment in SENSITIVE_FRAGMENTS):
            problems.append(f"sensitive key is not allowed in project config: {key}")
        if key.split(".", 1)[0] in PROJECT_FORBIDDEN_KEYS:
            problems.append(f"project-ignored key is not allowed in this project example: {key}")

    if config.get("sandbox_mode") == "danger-full-access":
        problems.append("danger-full-access exceeds the course workspace boundary")
    if config.get("approval_policy") == "never":
        problems.append("approval_policy never removes the interactive course baseline")

    model = config.get("model")
    effort = config.get("model_reasoning_effort")
    if model is not None and model not in COURSE_MODELS:
        problems.append("model is outside the GPT-5.6/Astra course routing profile")
    if model == "gpt-6-astra" and effort not in CODEX_ASTRA_CONFIG_EFFORTS:
        problems.append("gpt-6-astra requires low, medium, high, or xhigh in this Codex TOML course profile")
    if isinstance(model, str) and model.startswith("gpt-5.6") and effort not in CODEX_GPT56_CONFIG_EFFORTS:
        problems.append("this Codex TOML profile permits GPT-5.6 effort low, medium, high, or xhigh")

    uses_permission_profiles = "default_permissions" in config or isinstance(config.get("permissions"), dict)
    uses_legacy_sandbox = "sandbox_mode" in config or "sandbox_workspace_write" in config
    if uses_permission_profiles and uses_legacy_sandbox:
        problems.append("permission profiles do not compose with legacy sandbox settings")

    permissions = config.get("permissions", {})
    profile_network_enabled = any(
        isinstance(profile, dict)
        and isinstance(profile.get("network"), dict)
        and profile["network"].get("enabled") is True
        for profile in permissions.values()
    ) if isinstance(permissions, dict) else False
    features = config.get("features", {})
    network_proxy_enabled = isinstance(features, dict) and features.get("network_proxy") is True
    if profile_network_enabled and not network_proxy_enabled:
        problems.append("network.enabled requires features.network_proxy for domain enforcement")

    return {
        "valid": not problems,
        "keys": sorted(keys),
        "model_route": {"model": model, "reasoning_effort": effort},
        "problems": sorted(set(problems)),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: config_guard.py PATH_TO_TOML", file=sys.stderr)
        return 2
    report = validate_config(Path(sys.argv[1]))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
