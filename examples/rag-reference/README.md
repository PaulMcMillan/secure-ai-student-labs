# Secure Offline RAG Reference

This dependency-free Python example is the shared retrieval-augmented generation (RAG) reference for the course. It is deliberately small enough to audit in class while still exercising the production invariants that matter: manifest-controlled ingestion, integrity evidence, quarantine, authorization and freshness filtering **before** ranking, BM25-style lexical retrieval, grounded cited answers, abstention, redacted telemetry, evaluation, and cleanup.

The offline answer composer is deterministic and extractive; it never calls a model. That makes the required lab reproducible without credentials or network access. `OPENAI_FILE_SEARCH_ADAPTER.md` describes an optional hosted semantic-plus-keyword path, but it is not required and is UPDATE-SENSITIVE.

## Quick start

Run from the repository root with Python 3.10 or newer:

```powershell
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/index.json
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What is the travel approval threshold?" --telemetry examples/rag-reference/build/telemetry.jsonl
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl
python -m unittest discover -s examples/rag-reference/tests -v
```

Expected query fields include `status`, `reason`, `answer`, `citations`, `retrieved`, `trace_id`, `corpus_version`, `index_version`, `policy_decision`, and a coarse `budget`. The caller response never exposes per-reason counts for documents filtered by tenant, role, classification, freshness, deletion, or quarantine. Those counts are protected operator evidence in redacted telemetry, which never records the question, answer, retrieved text, citation quote, or reversible/dictionary-testable identity/query hashes. Production correlation should use a vault-backed keyed HMAC or an approved opaque identifier with bounded retention.

## Security invariants

1. The manifest path is the ingestion allowlist; paths cannot escape its directory.
2. Content hashes are verified when `sha256` is present.
3. The included poison sample is scanner-detected (not manifest-marked), recorded with named reasons, and never indexed. Operators may also mark a source for quarantine.
4. Tenant, role, explicit document-classification clearance, deletion-pending, effective-date, and expiry checks run before term frequencies are scored. Deletion-pending sources produce no chunks after rebuild. `legal_hold` preserves a source and does not itself confer authorization; otherwise-authorized callers may retrieve it.
5. Empty, over-budget, unauthorized, stale, poisoned, or weak evidence produces `blocked` or `abstained`, never an invented answer.
6. Every answer sentence comes from a returned chunk and has a stable source/chunk citation carrying the verified source-content digest and provenance fields.
7. Logs contain trace metadata, version/integrity hashes, and role/clearance counts—not identity/query hashes, role names, clearance names, prompts, or content.
8. `integrity_sha256` covers document policy metadata, content-derived chunks, and retrieval statistics; `load_index` verifies it before use. The digest is tamper evidence, not publisher authenticity—production release provenance requires a signature or equivalent trusted binding.

`--principal`, `--tenant`, `--roles`, and `--clearances` simulate verified identity claims supplied by the trusted lab harness. They must never be populated from user/model text in production. Classification access is an explicit set match; the fixture does not invent a clearance hierarchy. Citations carry source owner, document version, classification, effective date, and deletion status from the manifest.

`DEFAULT_AS_OF = 2026-09-10` is a frozen deterministic lab evaluation clock, not “current time.” The CLI's optional `--as-of` exists for controlled freshness/deletion tests. A production service must inject trusted server or policy time outside model/user/tool arguments and protect time synchronization; never let a caller choose the instant used for authorization or freshness.

This is a teaching reference, not a drop-in production service. See `THREAT_MODEL.md`, `RUNBOOK.md`, and `AI_BOM.json` before adapting it.
