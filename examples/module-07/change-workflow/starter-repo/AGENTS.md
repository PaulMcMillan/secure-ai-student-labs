# Repository Guidance

- Work only in `src/inventory.py` and `tests/test_inventory.py`.
- Preserve the public `reserve(available, requested)` signature.
- Use only the Python standard library.
- Run `python -m unittest discover -s tests -v`.
- Do not use network access, credentials, or destructive Git commands.
- Done means all four acceptance behaviors are tested, the diff is reviewed, and residual risk is recorded.
