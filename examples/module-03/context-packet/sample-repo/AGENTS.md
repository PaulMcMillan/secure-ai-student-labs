# Repository guidance

- Preserve the public `order_total` function signature.
- Use `Decimal` for all money calculations.
- Add no production dependencies.
- Run `python -m unittest discover -s tests -v` after changing pricing behavior.
