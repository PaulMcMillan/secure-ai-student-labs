# Payments temporary override

## Rules

- test_command: python -m unittest discover -s services/payments/tests -v
- data_boundary: synthetic payment fixtures only
- review_gate: inspect decimal rounding and idempotency changes
