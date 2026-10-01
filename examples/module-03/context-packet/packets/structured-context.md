# Pricing context packet

## Goal

Implement the approved bulk discount in the order total calculation.

## Context

- `src/pricing.py` - owns the order total calculation and public function.
- `tests/test_pricing.py` - records existing behavior and test conventions.
- `docs/pricing-policy.md` - defines the approved bulk discount threshold and rate.

## Constraints

- Preserve the public API.
- Continue to use `Decimal` for money.
- Add no production dependency.
- Do not access or expose credentials or customer data.

## Deliverable

Provide the implementation, focused tests, and a concise summary of changed behavior.

## Validation

Run `python -m unittest discover -s tests -v` and review the diff for unrelated changes.

## Stopping condition

Stop when the focused suite passes and the diff is scoped. Ask before changing the policy threshold, public API, or dependency set if the sources conflict.
