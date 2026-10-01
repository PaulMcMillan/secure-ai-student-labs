# Order Service Sample Repository

This synthetic repository supports the Day 1 M02 coding demonstration and lab. It calculates order totals with `Decimal`, uses only the Python standard library, and does not access the network or external data.

## Layout

```text
order-service/
├── AGENTS.md
├── WORK_ITEM.md
├── src/order_service/pricing.py
└── tests/test_pricing.py
```

## Baseline validation

From the student repository root:

```powershell
python -m unittest discover -s examples/module-02/order-service/tests -v
```

Expected: four tests pass before the exercise.

## Exercise boundary

Read `AGENTS.md` and `WORK_ITEM.md` before editing. Record the acting surface and permission/tool inventory. Do not add packages, enable a plugin/MCP server, use network or credentials, elevate access, or change rounding behavior. The learner adds input validation and one negative-case test, then reviews the diff and test output.
