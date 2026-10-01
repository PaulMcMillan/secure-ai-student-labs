# MCP 2026-07-28 Security Practicum Fixture

This dependency-free, offline fixture powers Module 8 security Labs 8.2-8.6. It evaluates synthetic policy evidence; it does not scan, install, start, exploit, or configure a real MCP server.

Run this block from `examples/module-08/mcp-security`.

```powershell
python security_check.py profiles/hardened.json --section all
python security_check.py profiles/unsafe.json --section all
python event_check.py events/normal.jsonl
python event_check.py events/incident.jsonl
python -m unittest discover -s tests -v
```

Valid inputs exit 0. Intentionally unsafe profiles/events exit 1 with control IDs or alerts. The current baseline evaluates stateless per-request protocol/capability validation, required server discovery support, pinned tools, issuer/audience validation, side-effect approval, credential/grant revocation, and model-invariant authorization. Reports never include credential values. The high-assurance thresholds are an explicit course baseline dated 2026-09-18 and must be reconciled with current official MCP requirements and organizational policy before production use.
