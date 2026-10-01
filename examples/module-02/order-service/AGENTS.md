# Order Service Agent Instructions

## Scope

- Keep changes inside this sample repository.
- Use Python 3.10+ and the standard library only.
- Preserve `Decimal` arithmetic and `ROUND_HALF_UP` currency rounding.
- Make the smallest change that satisfies `WORK_ITEM.md`.
- Do not use network access, credentials, generated files, or destructive commands.
- Do not load or install a plugin, skill, hook, or MCP server for this task; local repository tools are sufficient.

## Validation

From the student repository root, run:

```powershell
python -m unittest discover -s examples/module-02/order-service/tests -v
```

Review the final diff and report the changed files, test result, selected surface/permission posture, capability inventory, and any residual risk.
