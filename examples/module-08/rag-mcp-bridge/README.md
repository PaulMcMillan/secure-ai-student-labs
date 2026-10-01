# Read-only Stateless RAG MCP Bridge

This dependency-free training bridge exposes the shared offline RAG reference through one pinned read-only MCP tool, `search_knowledge`. It speaks the `2026-07-28` stateless request shape and implements the required `server/discover` RPC; invoking discovery is optional for clients.

Security boundary:

- every request validates protocol version and client-capability metadata;
- the tool inventory is pinned and deterministic;
- verified principal, tenant, roles, clearances, issuer, and audience arrive from the runtime auth context, never tool arguments or `clientInfo`;
- the expected synthetic issuer and token audience are validated before retrieval;
- the only admitted tool has `side_effect: none`; future write tools require a separate preview/approval/idempotency design;
- RAG authorization and classification filters run before ranking; answers cite or abstain;
- the fixture injects the frozen trusted policy time `2026-09-10` outside tool arguments for deterministic results. Production must use trusted server/policy time; a caller or model must never choose authorization/freshness time;
- optional trace context must be a bounded, nonzero W3C version-00 `traceparent` before it is reflected or logged;
- the tool handler is externally read-only. It emits a content-redacted operator event to the host's stderr logging plane; the host, not the tool, owns any durable audit write. Per-reason filter counts stay in that protected operator event and never appear in the caller response.

Build the shared index first, then run:

```powershell
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/index.json
python examples/module-08/rag-mcp-bridge/client.py
python -m unittest discover -s examples/module-08/rag-mcp-bridge/tests -v
```

The STDIO client passes a synthetic, non-secret verified-claims object in `AITRAINER_AUTH_CONTEXT`. A production gateway must derive these claims from validated credentials; never accept them from the model or tool arguments. Configure the host to collect stderr operator events into an access-controlled, encrypted, retention-bounded sink. Use a current Tier 1 MCP SDK and established OAuth/OIDC libraries in production.

Protocol/schema errors use standard JSON-RPC codes; unsupported protocol version uses MCP-defined `-32022` with both requested and supported versions. The teaching bridge uses application-defined `-30001` for authorization rejection and `-30003` for missing side-effect approval, outside JSON-RPC and MCP reserved ranges.
