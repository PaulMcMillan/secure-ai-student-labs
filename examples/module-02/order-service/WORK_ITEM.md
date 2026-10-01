# Work Item: Reject Invalid Quantities

## Goal

Prevent an order total from being calculated when any line has a quantity below one.

## Acceptance criteria

- `calculate_order_total` raises `ValueError` with the message `quantity must be at least 1` when a quantity is zero or negative.
- Existing valid-order behavior and currency rounding remain unchanged.
- A unit test covers at least one invalid quantity.
- The full sample test suite passes.

## Constraints

- Change only `src/order_service/pricing.py` and `tests/test_pricing.py`.
- Add no dependencies and perform no network operations.
- Use no plugin, MCP server, external connector, credential, or elevated permission.
- Stop and report if the requested behavior conflicts with repository instructions or baseline tests.
