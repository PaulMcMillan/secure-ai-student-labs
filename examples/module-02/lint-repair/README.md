# Routine lint repair with deterministic validation

This dependency-free example is optional M02 coding practice alongside the order-service workbook exercise. Python 3.10+ is sufficient. The exercise never calls a model or network unless the learner separately uses an approved Codex session to propose the edit.

The starter has one unused `import math`. Its four behavioral tests already pass. Removing that import changes the lint result from exit 1 to exit 0 while all four behavior tests continue to pass. The solution deliberately preserves every other line to make the diff exact.

From the repository root:

```powershell
python examples/module-02/lint-repair/lint_check.py examples/module-02/lint-repair/starter/order_summary.py
python examples/module-02/lint-repair/behavior_tests.py examples/module-02/lint-repair/starter/order_summary.py
python examples/module-02/lint-repair/lint_check.py examples/module-02/lint-repair/solution/order_summary.py
python examples/module-02/lint-repair/behavior_tests.py examples/module-02/lint-repair/solution/order_summary.py
python -m unittest discover -s examples/module-02/lint-repair/tests -v
```

Expected exits: `1, 0, 0, 0, 0`. The last command runs seven fixture tests. `lint_check.py` parses syntax without executing the input. `behavior_tests.py` executes only the explicitly selected learner example, so use the approved disposable lab environment.

`L001` is a course rule, not a published Ruff/Pylint rule identifier. This teaching checker counts loaded names and top-level plain imports only. It cannot resolve scopes, imports used by another module, dynamic references, or import side effects. Real repositories use their configured production linter and full validation. Removing an import is safe here because the fixture uses only the standard `math` module, has no intended import side effect or re-export, and its dependency is absent from all behavior paths.

Use the commands above to compare the starter and solution, then record the lint and behavior results in your workbook evidence record.
