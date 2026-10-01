"""Validate a synthetic Secure AI evidence packet without touching a host.

The checker distinguishes platform-enforcement evidence from AI-system controls
and from performance/capability observations.  It never probes hardware, opens
a network connection, starts a model, or changes external state.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED_MODALITIES = {
    "llm_gpt",
    "computer_vision",
    "natural_language_processing",
    "reinforcement_learning",
    "speech_recognition",
    "gan_generative_media",
    "embeddings_foundation_models",
}

REQUIRED_PLATFORM_EVIDENCE = {
    "secure_boot",
    "kernel_lockdown",
    "tpm2",
    "disk_encryption",
    "mok",
    "ima",
    "lkrg",
    "gpu_capability",
}

REQUIRED_CONTROL_SPINE = {
    "workload_identity",
    "data_and_object_authorization",
    "model_data_supply_chain",
    "input_provenance_and_normalization",
    "sandbox_and_network_isolation",
    "adversarial_evaluation",
    "monitoring_and_response",
    "human_consequence_gate",
}

EVIDENCE_CLASSES = {
    "preventive_enforcement",
    "measurement",
    "attestation_enabler",
    "runtime_detection",
    "encryption",
    "performance_capability",
}

REQUIRED_EVIDENCE_FIELDS = {
    "id",
    "assertion",
    "evidence_class",
    "status",
    "observed_at",
    "scope",
    "evidence_refs",
    "owner",
    "limitations",
}

REQUIRED_MODALITY_FIELDS = {
    "id",
    "untrusted_inputs",
    "attack_paths",
    "prevent",
    "detect",
    "respond",
    "test_oracles",
}


def _nonempty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _evidence_by_id(data: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    platform_evidence = data.get("platform_evidence", [])
    if not isinstance(platform_evidence, list):
        return result
    for item in platform_evidence:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def validate(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "errors": [f"cannot read evidence packet: {exc}"],
            "modalities": 0,
            "platform_evidence": 0,
            "external_actions": False,
            "host_probed": False,
            "performance_claims_satisfy_security_controls": False,
        }

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["evidence packet root must be an object"],
            "modalities": 0,
            "platform_evidence": 0,
            "external_actions": False,
            "host_probed": False,
            "performance_claims_satisfy_security_controls": False,
        }

    errors: list[str] = []

    safety = data.get("safety", {})
    if not isinstance(safety, dict):
        errors.append("safety must be an object")
        safety = {}
    for field in ("offline_synthetic", "network_used", "host_probed", "models_started", "files_written"):
        if field not in safety:
            errors.append(f"safety missing {field}")
    if safety.get("offline_synthetic") is not True:
        errors.append("packet must declare an offline synthetic exercise")
    for field in ("network_used", "host_probed", "models_started", "files_written"):
        if safety.get(field) is not False:
            errors.append(f"safety.{field} must be false")

    modalities = data.get("modality_controls", [])
    if not isinstance(modalities, list):
        errors.append("modality_controls must be an array")
        modalities = []
    modality_ids = {
        item.get("id") for item in modalities if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    missing_modalities = sorted(REQUIRED_MODALITIES - modality_ids)
    extra_modalities = sorted(modality_ids - REQUIRED_MODALITIES)
    if missing_modalities:
        errors.append("missing modalities: " + ", ".join(missing_modalities))
    if extra_modalities:
        errors.append("unknown modalities: " + ", ".join(extra_modalities))
    for item in modalities:
        if not isinstance(item, dict):
            errors.append("modality entry must be an object")
            continue
        identifier = item.get("id", "unknown")
        missing = sorted(REQUIRED_MODALITY_FIELDS - set(item))
        if missing:
            errors.append(f"{identifier} missing: {', '.join(missing)}")
            continue
        for field in REQUIRED_MODALITY_FIELDS - {"id"}:
            if not _nonempty_list(item.get(field)):
                errors.append(f"{identifier}.{field} must be a nonempty list of strings")

    platform = data.get("platform_evidence", [])
    if not isinstance(platform, list):
        errors.append("platform_evidence must be an array")
        platform = []
    platform_by_id = _evidence_by_id(data)
    missing_platform = sorted(REQUIRED_PLATFORM_EVIDENCE - set(platform_by_id))
    if missing_platform:
        errors.append("missing platform evidence: " + ", ".join(missing_platform))
    for item in platform:
        if not isinstance(item, dict):
            errors.append("platform evidence entry must be an object")
            continue
        identifier = item.get("id", "unknown")
        missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(item))
        if missing:
            errors.append(f"{identifier} missing evidence fields: {', '.join(missing)}")
            continue
        if not isinstance(item["evidence_class"], str) or item["evidence_class"] not in EVIDENCE_CLASSES:
            errors.append(f"{identifier} has unknown evidence_class")
        if not isinstance(item["status"], str) or item["status"] not in {"pass", "fail", "gap"}:
            errors.append(f"{identifier} status must be pass, fail, or gap")
        if item["status"] != "pass":
            errors.append(f"{identifier} is not evidenced as pass")
        if not isinstance(item["observed_at"], str) or "T" not in item["observed_at"]:
            errors.append(f"{identifier} lacks a timestamped observation")
        for field in ("scope", "owner", "limitations"):
            if not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"{identifier}.{field} must be nonempty")
        if not _nonempty_list(item["evidence_refs"]):
            errors.append(f"{identifier}.evidence_refs must contain reviewable evidence")

    raw_control_spine = data.get("control_spine", [])
    if not isinstance(raw_control_spine, list) or any(
        not isinstance(item, str) for item in raw_control_spine
    ):
        errors.append("control_spine must be an array of strings")
        control_spine: set[str] = set()
    else:
        control_spine = set(raw_control_spine)
    if control_spine != REQUIRED_CONTROL_SPINE:
        errors.append("control_spine must contain the eight required AI-system controls")

    gpu = platform_by_id.get("gpu_capability", {})
    if gpu.get("evidence_class") != "performance_capability":
        errors.append("gpu_capability must be classified as performance_capability")
    if gpu.get("counts_as_ai_security_control") is not False:
        errors.append("GPU API/benchmark success cannot satisfy an AI security control")

    ima = platform_by_id.get("ima", {})
    if ima.get("hash_algorithm") != "sha256" or ima.get("pcr") != 10:
        errors.append("IMA evidence must bind the claimed SHA-256 policy to PCR 10")
    if ima.get("measurement_count_interpretation") != "point-in-time-observation-not-threshold":
        errors.append("IMA measurement count must not be treated as a pass threshold")
    if not _nonempty_list(ima.get("verification", [])) or "replay-and-quote" not in ima.get("verification", []):
        errors.append("IMA requires log validation plus a replay-and-quote check")

    disk = platform_by_id.get("disk_encryption", {})
    devices = disk.get("covered_devices", [])
    if not isinstance(devices, list) or not devices:
        errors.append("disk_encryption must list every covered data-bearing device")
    elif any(not isinstance(device, dict) or device.get("encrypted") is not True for device in devices):
        errors.append("every listed data-bearing device must be evidenced as encrypted")
    if disk.get("key_protection_verified") is not True or disk.get("recovery_tested") is not True:
        errors.append("disk encryption requires key protection and tested recovery evidence")

    mok = platform_by_id.get("mok", {})
    if mok.get("enrolled") is not True or mok.get("private_key_protected") is not True:
        errors.append("MOK evidence requires enrollment and protected signing-key custody")
    if not _nonempty_list(mok.get("verified_modules", [])):
        errors.append("MOK enrollment alone does not prove required modules are signed and trusted")

    lkrg = platform_by_id.get("lkrg", {})
    if lkrg.get("installed") is not True or lkrg.get("loaded_at_observation") is not True:
        errors.append("LKRG must be both installed and loaded at the observation time")
    if lkrg.get("integrity_scan") != "passed" or not _nonempty_list(lkrg.get("alert_destinations", [])):
        errors.append("LKRG requires a reviewed scan result and an alert destination")

    tpm = platform_by_id.get("tpm2", {})
    if tpm.get("version") != "2.0" or tpm.get("fresh_quote_verified") is not True:
        errors.append("TPM presence alone is insufficient; require a verified fresh TPM 2.0 quote")

    secure_boot = platform_by_id.get("secure_boot", {})
    if secure_boot.get("enabled") is not True or secure_boot.get("enforcement_verified") is not True:
        errors.append("Secure Boot must be enabled and its enforcement path verified")

    lockdown = platform_by_id.get("kernel_lockdown", {})
    if lockdown.get("mode") not in {"integrity", "confidentiality"}:
        errors.append("kernel lockdown must be active in integrity or confidentiality mode")

    report = {
        "valid": not errors,
        "errors": errors,
        "modalities": len(modality_ids),
        "platform_evidence": len(platform_by_id),
        "external_actions": False,
        "host_probed": False,
        "performance_claims_satisfy_security_controls": False,
    }
    return report


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: secure_ai_check.py EVIDENCE_PACKET.json")
        return 2
    report = validate(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
