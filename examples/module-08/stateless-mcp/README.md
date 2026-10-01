# Module 8 Stateless MCP 2026-07-28 Fixture

This dependency-free, offline fixture implements a deliberately small MCP `2026-07-28` STDIO path: the server implements the required `server/discover` RPC (clients may choose whether to invoke it), plus `tools/list` and `tools/call`. It validates string/integer request IDs, omits an unknown ID from parse/invalid-request errors, silently ignores notifications, validates required per-request metadata and optional W3C trace fields, and returns complete version-error data. There is no `initialize`, `notifications/initialized`, session ID, model call, network call, credential, filesystem write, or production data.

Every request carries `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities` in `params._meta`; `clientInfo` is optional and self-reported. Every successful result has `resultType: complete` and server identity in result `_meta`. The deterministic list has conservative cache hints. This hand-written subset teaches the wire boundary; use a current Tier 1 SDK for production.

```powershell
python examples/module-08/stateless-mcp/client.py
python examples/module-08/stateless-mcp/dossier_check.py examples/module-08/stateless-mcp/risk-dossier.json
python -m unittest discover -s examples/module-08/stateless-mcp/tests -v
```

Expected: three independent responses, one pinned `lookup_policy` tool, valid dossier, and twelve passing tests.

The sibling `local-mcp` directory is explicitly retained as a **legacy 2025-11-25 migration fixture**. It is not the normative core lab.
