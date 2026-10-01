# Optional OpenAI File Search Adapter

<!-- UPDATE-SENSITIVE: OpenAI API behavior, model availability, limits, and pricing. Baseline 2026-09-10; verify before delivery. -->

The required lab stays offline. This optional production-oriented extension maps the same controls to the OpenAI Responses API and File Search. Official documentation accessed 2026-09-10 describes File Search as a hosted Responses API tool that searches vector stores with semantic and keyword search. Current vector-store search supports file-attribute filters and returns file IDs, filenames, scores, attributes, and content chunks.

## Control-preserving mapping

| Offline reference | Hosted adapter requirement |
|---|---|
| Manifest and local files | Upload only allowlisted files; record returned file IDs and local source hashes |
| Tenant/role/date filter before BM25 | Attach bounded file attributes and send the authorization/freshness filter with every search or File Search call |
| Quarantine before indexing | Scan, classify, and approve before upload; never upload quarantined content |
| Cited extractive answer | Request File Search through Responses, include search results for audit, and validate file-citation annotations against authorized returned files |
| Index version | Record vector-store ID, file IDs, attributes, corpus version, and ingestion completion/failure state |
| Redacted JSONL | Record request/response IDs, file IDs, usage, latency, decision, and hashes; omit prompts and chunks unless approved |
| Cleanup | Delete or expire test files/vector stores and verify deletion |

## Safe implementation sequence

1. Obtain credentials through the approved workload identity or secret-injection path. Never put a key in this repository, a prompt, a notebook, a shell history example, or a telemetry event.
2. Create a test-only vector store with an expiry policy where supported.
3. Upload the allowlisted corpus, attach attributes such as `tenant`, `role_scope`, `effective_date`, `expires_at`, and `source_id`, and poll each file to `completed`; stop on `failed` or `cancelled`.
4. Derive the server-side filter from authenticated principal claims. The model or user must not supply or broaden the tenant/role filter.
5. Use the Responses API with the File Search tool. Include `file_search_call.results` only in the protected diagnostic record needed for evaluation.
6. Validate every citation against the authorized results for that request. Abstain when evidence is missing, unauthorized, stale, or below the local quality threshold.
7. Run all eight required categories before enabling traffic: `answerable`, `abstain`, `classification`, `cross_tenant`, `poison`, `freshness`, `deletion`, and `budget`.
8. Delete or expire the test vector store, then verify that it can no longer be searched.

Do not paste a copy-paste SDK snippet into the core lab: SDK signatures and model IDs are volatile. Generate the adapter from the current official reference during delivery and pin the tested SDK version in the AI BOM.

## Official sources

- OpenAI, “File search,” https://developers.openai.com/api/docs/guides/tools-file-search — accessed 2026-09-10.
- OpenAI, “Retrieval,” https://developers.openai.com/api/docs/guides/retrieval — accessed 2026-09-10.
- OpenAI, “Search vector store,” https://developers.openai.com/api/reference/typescript/resources/vector_stores/methods/search — accessed 2026-09-10.
- OpenAI, “Working with evals,” https://developers.openai.com/api/docs/guides/evals — accessed 2026-09-10.
