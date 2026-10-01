# RAG Reference Runbook

## Scope and owner

This runbook covers the local, synthetic training fixture in `examples/rag-reference`. The lab operator owns the process. It has no network listener, identity provider, model API, production corpus, or automatic write action.

## Preflight

1. Use Python 3.10 or newer and run from the repository root.
2. Confirm `git status --short` does not show an API key, generated index, or telemetry file.
3. Inspect `corpus/manifest.json`; source paths, owner, document version, deletion status, tenant, roles, classification, dates, and quarantine state are security controls.
4. Do not replace the synthetic files with private or regulated data.

## Build and verify

```powershell
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/index.json
python -m unittest discover -s examples/rag-reference/tests -v
```

Expected ingestion evidence: seven manifest documents, five searchable documents/chunks, one scanner-quarantined document, one deletion-pending document omitted from chunks, and non-empty `index_version`/`integrity_sha256`. Loading recomputes the full index digest over policy metadata, chunks, and retrieval statistics. A source-hash mismatch, path escape, unsupported suffix, malformed metadata, oversized file, or changed index must fail closed. A bare digest is tamper evidence, not publisher authentication; production requires a trusted signed release binding.

## Query and observe

Run the query command in `README.md`. An authorized answer must cite `northstar-travel-2026`. The caller receives only a coarse policy outcome and budget; it must not receive reason-specific forbidden-corpus counts. Inspect the access-controlled operator file `build/telemetry.jsonl`: it may contain version/integrity hashes, role/clearance counts, source IDs, per-reason policy-filter counts, budgets, timing, and trace IDs, but never principal/tenant/query hashes, role names, clearance names, the question, answer, chunk text, or citation quote. Production identity correlation requires a vault-backed keyed HMAC or approved opaque ID—not an unsalted deterministic digest.

## Evaluate

```powershell
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl --report examples/rag-reference/build/eval-report.json
```

Pass requires all eight cases and all reported rates to equal `1.0`. Do not average away a classification, cross-tenant, poison, freshness, or budget failure; each is a release blocker for this fixture.

## Incident response

1. Disable the affected corpus/index version and stop answering from it.
2. Preserve the manifest, content hashes, index version, trace IDs, policy decisions, and redacted telemetry.
3. Identify every trace that retrieved the affected source ID. Do not copy sensitive chunks into the incident channel.
4. Quarantine the source, verify owner and provenance, rebuild into a new index version, and rerun all evals.
5. Restore only after the security owner approves the evidence. Retain the prior index only according to approved retention policy.

## Cleanup

Delete `examples/rag-reference/build/index.json`, `telemetry.jsonl`, and `eval-report.json`. The checked-in `.gitignore` prevents accidental staging, but verify `git status --short` before committing.
