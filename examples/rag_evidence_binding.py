"""Read-only verification for the shared redacted RAG observation artifact.

Module fixtures call this helper to verify structure and file bindings.  It never
executes a recorded command.  Only ``scripts/validate_course.py`` reruns the RAG
behavior that produced the checked-in observation.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SOURCE_ARTIFACTS = {
    "manifest": "examples/rag-reference/corpus/manifest.json",
    "evaluation_cases": "examples/rag-reference/evals/cases.json",
    "implementation": "examples/rag-reference/rag.py",
}
EXPECTED_CATEGORIES = {
    "answerable",
    "abstain",
    "classification",
    "cross_tenant",
    "poison",
    "freshness",
    "deletion",
    "budget",
}
EXPECTED_METRICS = {
    "retrieval_recall_at_k",
    "citation_precision",
    "answerable_pass_rate",
    "abstain_pass_rate",
    "classification_block_rate",
    "cross_tenant_block_rate",
    "poison_block_rate",
    "freshness_pass_rate",
    "deletion_block_rate",
    "budget_pass_rate",
}
FORBIDDEN_RAW_KEYS = {
    "answer",
    "citations",
    "clearances",
    "content",
    "principal",
    "question",
    "retrieved_sources",
    "roles",
    "tenant",
    "trace_id",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _repo_file(repo_root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    relative = PurePosixPath(value.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        return None
    root = repo_root.resolve()
    candidate = root.joinpath(*relative.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        if any(str(key).lower() in FORBIDDEN_RAW_KEYS for key in value):
            return True
        return any(_contains_forbidden_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def verify_rag_evidence(
    repo_root: Path,
    required_reference: Any,
    supplied_reference: Any,
) -> dict[str, Any]:
    """Verify one EV-RAG reference and every checked-in file digest it claims."""

    issues: list[str] = []
    artifact: dict[str, Any] = {}

    required_ok = (
        isinstance(required_reference, dict)
        and isinstance(required_reference.get("id"), str)
        and required_reference.get("id", "").startswith("EV-RAG-")
        and _repo_file(repo_root, required_reference.get("path")) is not None
    )
    if not required_ok:
        issues.append("task contract must name a safe EV-RAG id and repository-relative artifact path")

    supplied_ok = (
        required_ok
        and isinstance(supplied_reference, dict)
        and supplied_reference.get("id") == required_reference.get("id")
        and supplied_reference.get("path") == required_reference.get("path")
        and SHA256.fullmatch(str(supplied_reference.get("sha256", ""))) is not None
    )
    if not supplied_ok:
        issues.append("record must reference the contract-required EV-RAG artifact with a full SHA-256")
        return {"valid": False, "issues": issues, "artifact": artifact}

    evidence_path = _repo_file(repo_root, supplied_reference["path"])
    if evidence_path is None or not evidence_path.is_file():
        issues.append("referenced EV-RAG artifact does not exist inside the repository")
        return {"valid": False, "issues": issues, "artifact": artifact}
    if _sha256(evidence_path) != supplied_reference["sha256"]:
        issues.append("referenced EV-RAG artifact digest does not match its file bytes")

    try:
        artifact = _json_object(evidence_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        issues.append(f"referenced EV-RAG artifact is not a JSON object: {exc}")
        return {"valid": False, "issues": issues, "artifact": {}}

    if artifact.get("evidence_id") != required_reference.get("id"):
        issues.append("EV-RAG evidence_id does not match the task contract")
    if artifact.get("schema_version") != "1.0":
        issues.append("EV-RAG schema_version must be 1.0")

    sources = artifact.get("source_artifacts", {})
    source_values: dict[str, dict[str, Any]] = {}
    if not isinstance(sources, dict) or set(sources) != set(EXPECTED_SOURCE_ARTIFACTS):
        issues.append("EV-RAG source_artifacts must name manifest, evaluation_cases, and implementation")
    else:
        for name, expected_path in EXPECTED_SOURCE_ARTIFACTS.items():
            source = sources.get(name, {})
            source_values[name] = source if isinstance(source, dict) else {}
            path = source_values[name].get("path")
            digest = str(source_values[name].get("sha256", ""))
            target = _repo_file(repo_root, path)
            if path != expected_path or target is None or not target.is_file():
                issues.append(f"EV-RAG {name} must reference {expected_path}")
            elif SHA256.fullmatch(digest) is None or _sha256(target) != digest:
                issues.append(f"EV-RAG {name} digest does not match the referenced file")

    release_digests = artifact.get("release_digests", {})
    manifest_digest = source_values.get("manifest", {}).get("sha256")
    implementation_digest = source_values.get("implementation", {}).get("sha256")
    index = artifact.get("index", {})
    index_digest = index.get("integrity_sha256") if isinstance(index, dict) else None
    release_digest_ok = (
        isinstance(release_digests, dict)
        and set(release_digests) == {"corpus", "index", "configuration"}
        and all(SHA256.fullmatch(str(release_digests.get(name, ""))) for name in release_digests)
        and release_digests.get("corpus") == manifest_digest
        and release_digests.get("configuration") == implementation_digest
        and release_digests.get("index") == index_digest
    )
    if not release_digest_ok:
        issues.append("EV-RAG release digests must bind manifest, index integrity, and implementation")

    index_ok = (
        isinstance(index, dict)
        and SHA256.fullmatch(str(index.get("integrity_sha256", ""))) is not None
        and index.get("index_version") == str(index.get("integrity_sha256", ""))[:16]
        and index.get("integrity_verified_on_load") is True
    )
    if not index_ok:
        issues.append("EV-RAG index needs a full integrity digest, matching version prefix, and load verification")

    manifest: dict[str, Any] = {}
    case_file: dict[str, Any] = {}
    try:
        manifest = _json_object(repo_root / EXPECTED_SOURCE_ARTIFACTS["manifest"])
        case_file = _json_object(repo_root / EXPECTED_SOURCE_ARTIFACTS["evaluation_cases"])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        issues.append(f"RAG source artifact cannot be parsed: {exc}")

    document_value = manifest.get("documents", []) if isinstance(manifest, dict) else []
    documents = document_value if isinstance(document_value, list) else []
    case_value = case_file.get("cases", []) if isinstance(case_file, dict) else []
    cases = case_value if isinstance(case_value, list) else []
    category_counts = Counter(
        case.get("category") for case in cases if isinstance(case, dict) and case.get("category")
    )

    ingestion = artifact.get("ingestion", {})
    count_fields = {
        "document_count",
        "indexed_document_count",
        "chunk_count",
        "scanner_quarantined_document_count",
        "deletion_pending_document_count",
    }
    counts_are_integers = (
        isinstance(ingestion, dict)
        and all(type(ingestion.get(field)) is int for field in count_fields)
    )
    ingestion_ok = (
        counts_are_integers
        and ingestion.get("document_count") == len(documents) == 7
        and ingestion.get("indexed_document_count") == 5
        and ingestion.get("chunk_count") == 5
        and ingestion.get("scanner_quarantined_document_count") == 1
        and ingestion.get("deletion_pending_document_count") == 1
        and ingestion.get("indexed_document_count")
        + ingestion.get("scanner_quarantined_document_count")
        + ingestion.get("deletion_pending_document_count")
        == ingestion.get("document_count")
    )
    if not ingestion_ok:
        issues.append("EV-RAG ingestion counts must match the seven-document observed run")

    evaluation = artifact.get("evaluation", {})
    category_results = evaluation.get("category_results", {}) if isinstance(evaluation, dict) else {}
    metric_results = evaluation.get("metric_results", {}) if isinstance(evaluation, dict) else {}
    category_ok = (
        len(cases) == 8
        and set(category_counts) == EXPECTED_CATEGORIES
        and all(count == 1 for count in category_counts.values())
        and isinstance(category_results, dict)
        and set(category_results) == EXPECTED_CATEGORIES
        and all(category_results[name] == "pass" for name in EXPECTED_CATEGORIES)
    )
    metrics_ok = (
        isinstance(metric_results, dict)
        and set(metric_results) == EXPECTED_METRICS
        and all(metric_results[name] == 1.0 for name in EXPECTED_METRICS)
    )
    evaluation_ok = (
        isinstance(evaluation, dict)
        and evaluation.get("case_count") == len(cases) == 8
        and evaluation.get("passed_count") == 8
        and evaluation.get("all_passed") is True
        and category_ok
        and metrics_ok
    )
    if not evaluation_ok:
        issues.append("EV-RAG must contain 8 passing category results and the exact 10 passing metrics")

    redaction = artifact.get("redaction", {})
    redaction_ok = (
        isinstance(redaction, dict)
        and redaction.get("redacted") is True
        and redaction.get("raw_questions_included") is False
        and redaction.get("raw_answers_included") is False
        and redaction.get("identity_attributes_included") is False
        and redaction.get("document_content_included") is False
        and not _contains_forbidden_key(artifact)
    )
    if not redaction_ok:
        issues.append("EV-RAG artifact must be redacted and omit raw content and identity attributes")

    verification = artifact.get("verification", {})
    verification_ok = (
        isinstance(verification, dict)
        and verification.get("repository_behavior_validator") == "scripts/validate_course.py"
        and verification.get("structure_checkers_execute_commands") is False
    )
    if not verification_ok:
        issues.append("EV-RAG must identify the repository behavior validator and read-only structure checkers")

    return {
        "valid": not issues,
        "issues": issues,
        "artifact": artifact,
        "release_digests": release_digests if isinstance(release_digests, dict) else {},
        "ingestion": ingestion if isinstance(ingestion, dict) else {},
        "category_results": category_results if isinstance(category_results, dict) else {},
        "metric_results": metric_results if isinstance(metric_results, dict) else {},
    }
