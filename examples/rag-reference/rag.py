#!/usr/bin/env python3
"""Dependency-free, security-focused offline RAG reference.

The generator is intentionally extractive. It demonstrates grounding and citations
without requiring a model, network access, credentials, or a third-party index.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import secrets
import sys
import time
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
DEFAULT_AS_OF = date(2026, 9, 10)
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "should", "the", "to", "was", "what",
    "when", "where", "which", "who", "why", "with",
}
ALLOWED_SUFFIXES = {".md", ".txt"}
MAX_SOURCE_BYTES = 64 * 1024
MAX_QUERY_TOKENS = 24
MAX_RESULTS = 4
MAX_SCORED_CHUNKS = 100
MIN_SCORE = 0.25
REQUIRED_EVAL_CATEGORIES = {"answerable", "abstain", "classification", "cross_tenant", "poison", "freshness", "deletion", "budget"}
POISON_PATTERNS = {
    "instruction_override": re.compile(r"\bignore (all |any )?(previous|prior|system|developer) instructions?\b", re.I),
    "secret_request": re.compile(r"\b(reveal|print|send|exfiltrate).{0,40}\b(secret|token|password|system prompt)\b", re.I),
    "authority_claim": re.compile(r"\b(system|developer) message\s*:", re.I),
}


class RagError(ValueError):
    """Expected validation or policy failure."""


def _json_load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RagError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RagError(f"expected a JSON object in {path}")
    return value


def _json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def tokenize(value: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(value)]


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RagError(f"{field} must be YYYY-MM-DD") from exc


def _validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise RagError(f"manifest schema_version must be {SCHEMA_VERSION}")
    for field in ("corpus_id", "corpus_version"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise RagError(f"manifest {field} must be a non-empty string")
    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise RagError("manifest documents must be a non-empty list")
    seen: set[str] = set()
    for document in documents:
        if not isinstance(document, dict):
            raise RagError("each manifest document must be an object")
        for field in ("source_id", "path", "title", "owner", "document_version", "deletion_status", "tenant", "classification", "effective_date", "expires_at"):
            if not isinstance(document.get(field), str) or not document[field].strip():
                raise RagError(f"document {field} must be a non-empty string")
        if document["source_id"] in seen:
            raise RagError(f"duplicate source_id: {document['source_id']}")
        seen.add(document["source_id"])
        if document["deletion_status"] not in {"active", "deletion_pending", "legal_hold"}:
            raise RagError(f"{document['source_id']} deletion_status is not recognized")
        if document["classification"] not in {"public", "internal", "confidential", "restricted", "untrusted"}:
            raise RagError(f"{document['source_id']} classification is not recognized")
        roles = document.get("allowed_roles")
        if not isinstance(roles, list) or not roles or not all(isinstance(role, str) and role for role in roles):
            raise RagError(f"{document['source_id']} allowed_roles must be a non-empty string list")
        effective = _parse_date(document["effective_date"], "effective_date")
        expires = _parse_date(document["expires_at"], "expires_at")
        if expires < effective:
            raise RagError(f"{document['source_id']} expires before it becomes effective")
        if "sha256" in document and not re.fullmatch(r"[0-9a-f]{64}", str(document["sha256"])):
            raise RagError(f"{document['source_id']} sha256 must be 64 lowercase hex characters")
    return documents


def _resolve_source(manifest_path: Path, relative: str) -> Path:
    base = manifest_path.parent.resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise RagError(f"source path escapes corpus directory: {relative}") from exc
    if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
        raise RagError(f"unsupported source suffix: {candidate.suffix}")
    return candidate


def _quarantine_reasons(document: dict[str, Any], text: str) -> list[str]:
    reasons: list[str] = []
    if document.get("quarantine") is True:
        reasons.append("manifest_marked")
    for name, pattern in POISON_PATTERNS.items():
        if pattern.search(text):
            reasons.append(name)
    return sorted(set(reasons))


def _chunks(text: str, max_chars: int = 700) -> Iterable[str]:
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", text)]
    current = ""
    for paragraph in (part for part in paragraphs if part):
        sentences = SENTENCE_RE.split(paragraph) if len(paragraph) > max_chars else [paragraph]
        for sentence in sentences:
            proposed = f"{current} {sentence}".strip()
            if current and len(proposed) > max_chars:
                yield current
                current = sentence[:max_chars]
            else:
                current = proposed[:max_chars]
    if current:
        yield current


def build_index(manifest_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest = _json_load(manifest_path)
    documents = _validate_manifest(manifest)
    indexed_documents: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    for document in documents:
        source_path = _resolve_source(manifest_path, document["path"])
        try:
            raw = source_path.read_bytes()
        except OSError as exc:
            raise RagError(f"cannot read source {document['source_id']}: {exc}") from exc
        if len(raw) > MAX_SOURCE_BYTES:
            raise RagError(f"source exceeds {MAX_SOURCE_BYTES} bytes: {document['source_id']}")
        digest = _sha256_bytes(raw)
        if document.get("sha256") and digest != document["sha256"]:
            raise RagError(f"integrity check failed: {document['source_id']}")
        text = raw.decode("utf-8")
        quarantine_reasons = _quarantine_reasons(document, text)
        record = {**document, "content_sha256": digest, "quarantined": bool(quarantine_reasons), "quarantine_reasons": quarantine_reasons}
        indexed_documents.append(record)
        if quarantine_reasons or document["deletion_status"] == "deletion_pending":
            continue
        for position, chunk_text in enumerate(_chunks(text), start=1):
            tokens = tokenize(chunk_text)
            if tokens:
                chunks.append({
                    "chunk_id": f"{document['source_id']}:{position}",
                    "source_id": document["source_id"],
                    "text": chunk_text,
                    "term_frequency": dict(Counter(tokens)),
                    "token_count": len(tokens),
                })
    document_frequency: Counter[str] = Counter()
    for chunk in chunks:
        document_frequency.update(chunk["term_frequency"].keys())
    value = {
        "schema_version": SCHEMA_VERSION,
        "corpus_id": manifest["corpus_id"],
        "corpus_version": manifest["corpus_version"],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "documents": indexed_documents,
        "chunks": chunks,
        "statistics": {
            "document_count": len(indexed_documents),
            "indexed_document_count": sum(not doc["quarantined"] and doc["deletion_status"] != "deletion_pending" for doc in indexed_documents),
            "quarantined_document_count": sum(doc["quarantined"] for doc in indexed_documents),
            "deletion_pending_document_count": sum(doc["deletion_status"] == "deletion_pending" for doc in indexed_documents),
            "chunk_count": len(chunks),
            "average_chunk_tokens": (sum(chunk["token_count"] for chunk in chunks) / len(chunks)) if chunks else 0.0,
            "document_frequency": dict(document_frequency),
        },
    }
    integrity_sha256 = _index_integrity(value)
    value["integrity_sha256"] = integrity_sha256
    value["index_version"] = integrity_sha256[:16]
    return value


def _index_integrity(index: dict[str, Any]) -> str:
    """Digest policy metadata, content-derived chunks, and retrieval statistics.

    The build timestamp and digest labels are excluded so identical inputs produce
    identical evidence. This is tamper evidence, not publisher authenticity.
    """
    payload = {
        key: index[key]
        for key in ("schema_version", "corpus_id", "corpus_version", "documents", "chunks", "statistics")
        if key in index
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(canonical)


def load_index(path: Path) -> dict[str, Any]:
    index = _json_load(path)
    if index.get("schema_version") != SCHEMA_VERSION or not isinstance(index.get("chunks"), list) or not isinstance(index.get("documents"), list):
        raise RagError("unsupported or malformed index")
    expected = _index_integrity(index)
    if index.get("integrity_sha256") != expected or index.get("index_version") != expected[:16]:
        raise RagError("index integrity check failed")
    return index


def _eligible_documents(index: dict[str, Any], tenant: str, roles: set[str], clearances: set[str], as_of: date) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    eligible: dict[str, dict[str, Any]] = {}
    filtered = Counter()
    for document in index["documents"]:
        if document.get("quarantined"):
            filtered["quarantined"] += 1
        elif document["deletion_status"] == "deletion_pending":
            filtered["deletion_pending"] += 1
        elif document["tenant"] != tenant:
            filtered["tenant"] += 1
        elif not roles.intersection(document["allowed_roles"]):
            filtered["role"] += 1
        elif document["classification"] not in clearances:
            filtered["classification"] += 1
        elif _parse_date(document["effective_date"], "effective_date") > as_of:
            filtered["not_yet_effective"] += 1
        elif _parse_date(document["expires_at"], "expires_at") < as_of:
            filtered["expired"] += 1
        else:
            eligible[document["source_id"]] = document
    return eligible, dict(filtered)


def _bm25_score(query_terms: list[str], chunk: dict[str, Any], stats: dict[str, Any]) -> float:
    total_chunks = max(1, int(stats["chunk_count"]))
    average_length = max(1.0, float(stats["average_chunk_tokens"]))
    score = 0.0
    for term in set(query_terms):
        frequency = int(chunk["term_frequency"].get(term, 0))
        if not frequency:
            continue
        df = int(stats["document_frequency"].get(term, 0))
        inverse_document_frequency = math.log(1 + ((total_chunks - df + 0.5) / (df + 0.5)))
        denominator = frequency + 1.5 * (0.25 + 0.75 * int(chunk["token_count"]) / average_length)
        score += inverse_document_frequency * ((frequency * 2.5) / denominator)
    return score


def _sentence_for_query(text: str, query_terms: list[str]) -> str:
    terms = set(query_terms)
    sentences = [part.strip() for part in SENTENCE_RE.split(text) if part.strip()]
    return max(sentences, key=lambda sentence: (len(terms.intersection(tokenize(sentence))), -len(sentence))) if sentences else text.strip()


def _telemetry_event(
    result: dict[str, Any],
    roles: list[str],
    clearances: list[str],
    elapsed_ms: float,
    policy_filter_counts: dict[str, int],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": result["trace_id"],
        "role_count": len(set(roles)),
        "clearance_count": len(set(clearances)),
        "corpus_version": result["corpus_version"],
        "index_version": result["index_version"],
        "integrity_sha256": result["integrity_sha256"],
        "status": result["status"],
        "reason": result["reason"],
        "policy_decision": result["policy_decision"],
        "retrieved_source_ids": [item["source_id"] for item in result["retrieved"]],
        "retrieved_count": len(result["retrieved"]),
        "citation_count": len(result["citations"]),
        # Reason-specific denial counts are operator evidence. They are kept out
        # of the caller response so a denied caller cannot probe corpus makeup.
        "policy_filter_counts": policy_filter_counts,
        "budget": result["budget"],
        "elapsed_ms": round(elapsed_ms, 3),
        "content_logged": False,
    }


def _append_telemetry(path: Path | None, event: dict[str, Any]) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def answer_query(
    index: dict[str, Any],
    *,
    principal: str,
    tenant: str,
    roles: list[str],
    clearances: list[str],
    question: str,
    as_of: date = DEFAULT_AS_OF,
    top_k: int = 3,
    telemetry_path: Path | None = None,
    operator_event_out: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    query_terms = tokenize(question)
    ranking_terms = [term for term in query_terms if term not in STOPWORDS] or query_terms
    budget = {
        "query_tokens": len(query_terms), "max_query_tokens": MAX_QUERY_TOKENS,
        "requested_results": int(top_k), "max_results": MAX_RESULTS, "max_scored_chunks": MAX_SCORED_CHUNKS,
    }
    base = {
        "trace_id": secrets.token_hex(16),
        "corpus_version": index["corpus_version"], "index_version": index["index_version"], "integrity_sha256": index["integrity_sha256"],
        "budget": budget, "answer": "", "citations": [], "retrieved": [],
    }
    policy_filter_counts: dict[str, int] = {}
    if not principal.strip() or not tenant.strip() or not roles or not clearances:
        result = {**base, "status": "blocked", "reason": "invalid_principal_context", "policy_decision": "deny_identity"}
    elif not query_terms:
        result = {**base, "status": "blocked", "reason": "empty_question", "policy_decision": "deny_input"}
    elif len(query_terms) > MAX_QUERY_TOKENS or top_k < 1 or top_k > MAX_RESULTS:
        result = {**base, "status": "blocked", "reason": "budget_exceeded", "policy_decision": "deny_budget"}
    else:
        eligible_documents, policy_filter_counts = _eligible_documents(index, tenant, set(roles), set(clearances), as_of)
        eligible_chunks = [chunk for chunk in index["chunks"] if chunk["source_id"] in eligible_documents]
        budget["scored_chunks"] = len(eligible_chunks)
        if len(eligible_chunks) > MAX_SCORED_CHUNKS:
            result = {**base, "status": "blocked", "reason": "ranking_budget_exceeded", "policy_decision": "deny_budget"}
        else:
            ranked = [(_bm25_score(ranking_terms, chunk, index["statistics"]), chunk) for chunk in eligible_chunks]
            ranked = [item for item in ranked if item[0] > 0]
            ranked.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
            selected = ranked[:top_k]
            base["retrieved"] = [
                {"source_id": chunk["source_id"], "chunk_id": chunk["chunk_id"], "score": round(score, 6), "content_sha256": eligible_documents[chunk["source_id"]]["content_sha256"]}
                for score, chunk in selected
            ]
            evidence_coverage = 0.0
            if selected:
                evidence_coverage = len(set(ranking_terms).intersection(selected[0][1]["term_frequency"])) / len(set(ranking_terms))
            budget["evidence_term_coverage"] = round(evidence_coverage, 4)
            if not selected or selected[0][0] < MIN_SCORE or evidence_coverage < 0.6:
                result = {**base, "status": "abstained", "reason": "no_authorized_evidence", "policy_decision": "allow_retrieval_abstain"}
            else:
                answer_parts: list[str] = []
                citations: list[dict[str, str]] = []
                # The offline composer uses the single best authorized chunk. A
                # hosted adapter may synthesize across several chunks, but must
                # preserve sentence-level support and citation checks.
                for _, chunk in selected[:1]:
                    sentence = _sentence_for_query(chunk["text"], ranking_terms)
                    if sentence:
                        document = eligible_documents[chunk["source_id"]]
                        answer_parts.append(f"{sentence} [{chunk['chunk_id']}]")
                        citations.append({
                            "source_id": chunk["source_id"], "chunk_id": chunk["chunk_id"], "quote": sentence[:240],
                            "title": document["title"], "owner": document["owner"], "document_version": document["document_version"],
                            "classification": document["classification"], "effective_date": document["effective_date"],
                            "deletion_status": document["deletion_status"], "content_sha256": document["content_sha256"],
                        })
                if answer_parts:
                    result = {**base, "status": "answered", "reason": "grounded_evidence_found", "policy_decision": "allow_grounded_answer", "answer": " ".join(answer_parts), "citations": citations}
                else:
                    result = {**base, "status": "abstained", "reason": "no_groundable_sentence", "policy_decision": "allow_retrieval_abstain"}
    elapsed_ms = (time.perf_counter() - started) * 1000
    event = _telemetry_event(result, roles, clearances, elapsed_ms, policy_filter_counts)
    if operator_event_out is not None:
        operator_event_out.clear()
        operator_event_out.update(event)
    _append_telemetry(telemetry_path, event)
    return result


def evaluate(index: dict[str, Any], cases_path: Path, telemetry_path: Path | None = None) -> dict[str, Any]:
    cases = _json_load(cases_path).get("cases")
    if not isinstance(cases, list) or not cases:
        raise RagError("eval cases must be a non-empty list")
    categories = {case.get("category") for case in cases if isinstance(case, dict)}
    missing_categories = REQUIRED_EVAL_CATEGORIES - categories
    if missing_categories:
        raise RagError(f"eval cases missing required categories: {', '.join(sorted(missing_categories))}")
    rows: list[dict[str, Any]] = []
    totals = Counter()
    passes = Counter()
    citation_correct = citation_total = recall_hits = recall_total = 0
    for case in cases:
        principal = case["principal"]
        result = answer_query(
            index, principal=principal["id"], tenant=principal["tenant"], roles=principal["roles"], clearances=principal["clearances"],
            question=case["question"], as_of=_parse_date(case.get("as_of", DEFAULT_AS_OF.isoformat()), "as_of"),
            top_k=case.get("top_k", 3), telemetry_path=telemetry_path,
        )
        expected = set(case.get("expected_sources", []))
        cited = {item["source_id"] for item in result["citations"]}
        retrieved = {item["source_id"] for item in result["retrieved"]}
        forbidden = set(case.get("forbidden_sources", []))
        passed = (
            result["status"] == case["expected_status"]
            and (not expected or expected.issubset(cited))
            and all(value.lower() in result["answer"].lower() for value in case.get("answer_contains", []))
            and not forbidden.intersection(cited | retrieved)
        )
        category = case["category"]
        totals[category] += 1
        passes[category] += int(passed)
        if expected:
            recall_total += 1
            recall_hits += int(bool(expected.intersection(retrieved)))
        for source_id in cited:
            citation_total += 1
            citation_correct += int(not expected or source_id in expected)
        rows.append({"id": case["id"], "category": category, "passed": passed, "status": result["status"], "reason": result["reason"], "cited_sources": sorted(cited), "retrieved_sources": sorted(retrieved), "trace_id": result["trace_id"]})
    rate = lambda name: round(passes[name] / totals[name], 4)
    passed_count = sum(row["passed"] for row in rows)
    return {
        "schema_version": SCHEMA_VERSION, "corpus_version": index["corpus_version"], "index_version": index["index_version"], "integrity_sha256": index["integrity_sha256"],
        "total": len(rows), "passed": passed_count, "all_passed": passed_count == len(rows),
        "metrics": {
            "retrieval_recall_at_k": round(recall_hits / recall_total, 4) if recall_total else 1.0,
            "citation_precision": round(citation_correct / citation_total, 4) if citation_total else 1.0,
            "answerable_pass_rate": rate("answerable"), "abstain_pass_rate": rate("abstain"),
            "classification_block_rate": rate("classification"),
            "cross_tenant_block_rate": rate("cross_tenant"), "poison_block_rate": rate("poison"),
            "freshness_pass_rate": rate("freshness"), "deletion_block_rate": rate("deletion"), "budget_pass_rate": rate("budget"),
        },
        "cases": rows,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("--manifest", type=Path, required=True)
    ingest.add_argument("--index", type=Path, required=True)
    query = commands.add_parser("query")
    query.add_argument("--index", type=Path, required=True)
    query.add_argument("--principal", required=True)
    query.add_argument("--tenant", required=True)
    query.add_argument("--roles", nargs="+", required=True)
    query.add_argument("--clearances", nargs="+", required=True)
    query.add_argument("--question", required=True)
    query.add_argument("--as-of", type=date.fromisoformat, default=DEFAULT_AS_OF)
    query.add_argument("--top-k", type=int, default=3)
    query.add_argument("--telemetry", type=Path)
    eval_parser = commands.add_parser("eval")
    eval_parser.add_argument("--index", type=Path, required=True)
    eval_parser.add_argument("--cases", type=Path, required=True)
    eval_parser.add_argument("--telemetry", type=Path)
    eval_parser.add_argument("--report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "ingest":
            value = build_index(args.manifest)
            _json_write(args.index, value)
            output = {"status": "indexed", "index": str(args.index), **value["statistics"], "index_version": value["index_version"], "integrity_sha256": value["integrity_sha256"]}
        elif args.command == "query":
            output = answer_query(load_index(args.index), principal=args.principal, tenant=args.tenant, roles=args.roles, clearances=args.clearances,
                                  question=args.question, as_of=args.as_of, top_k=args.top_k, telemetry_path=args.telemetry)
        else:
            output = evaluate(load_index(args.index), args.cases, args.telemetry)
            if args.report:
                _json_write(args.report, output)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0 if output.get("all_passed", True) else 1
    except (RagError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
