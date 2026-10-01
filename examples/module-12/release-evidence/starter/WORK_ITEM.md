# Add a quote explanation

Read `AGENTS.md`, `task.json`, `pricing.py`, and `tests/test_pricing.py` in your prepared M12 project.

## Function contract

Add `explain_quote(subtotal: float, segment: str = "standard") -> dict[str, object]`.
Preserve the existing `quote_total` signature, validation, rates, and rounding.
The explanation must be deterministic and return exactly these four fields:

| Field | Required value |
| --- | --- |
| `subtotal` | The input converted to `float` and rounded to two decimal places with Python's existing `round` behavior. |
| `discount_rate` | `0.0` for `standard`; `0.10` for `partner`. |
| `total` | Exactly the result of `quote_total(subtotal, segment)`. |
| `reason` | `standard rate` for `standard`; `partner discount` for `partner`. |

Examples:

```python
explain_quote(100)
# {"subtotal": 100.0, "discount_rate": 0.0, "total": 100.0, "reason": "standard rate"}
explain_quote(100, "partner")
# {"subtotal": 100.0, "discount_rate": 0.10, "total": 90.0, "reason": "partner discount"}
```

For both functions, a negative subtotal, a boolean, or a non-numeric subtotal raises
`ValueError("subtotal must be a non-negative number")`. An unknown string segment
raises `ValueError("unknown segment")`. Preserve the starter's other input behavior;
this task does not broaden the public API or change currency representation.

## Acceptance and evidence

1. Run the two baseline tests from this project root: `python -m unittest discover -s tests -v`.
2. Add tests for both explanation examples, consistency with `quote_total` for a fractional subtotal, and the invalid inputs above. Cover both public functions when checking validation. Keep the existing valid-total tests.
3. Run the new tests before implementing the function and retain their failure. Implement the smallest change, then rerun the full suite.
4. Review the changed files against the four allowed paths in `task.json`. Test count depends on how you group cases; passing behavior matters more than matching the reference's five methods.
5. Complete `evidence/capstone.json` using your actual baseline, branch, checks, and independent review. The workbook guide explains the separate RAG run, `evidence/rag-report.json`, and final checker command.

Keep the reference solution closed until after your attempt. A passing reference suite is not evidence that your implementation passed.
