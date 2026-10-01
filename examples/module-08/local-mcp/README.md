# LEGACY Module 8 Local MCP Fixture — Migration Comparison Only

> **Legacy, non-normative fixture.** This directory preserves the MCP `2025-11-25` handshake solely for migration comparison. Do not use it to teach or implement the current protocol. The canonical MCP `2026-07-28` course fixture is [`../stateless-mcp`](../stateless-mcp/README.md).

This dependency-free training fixture implements a deliberately small subset of MCP version `2025-11-25` over STDIO: initialization, the initialized notification, `tools/list`, and `tools/call`. It exposes one read-only tool backed by two static synthetic records.

It makes no model or network call, reads no environment variable or credential, performs no write, and changes no Codex configuration. It is a legacy comparison fixture, not a general MCP SDK or production server.

## Run

Run this block from `examples/module-08/local-mcp`.

```powershell
python client.py
python dossier_check.py risk-dossier.json
python -m unittest discover -s tests -v
```

Expected: the client reports three responses and one successful tool; the dossier is valid; twelve tests pass. `transcript.jsonl` provides a readable fallback. Refresh the protocol and Codex configuration sources before reuse.
