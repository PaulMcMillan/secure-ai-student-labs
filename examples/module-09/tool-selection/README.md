# Module 9 Tool-Selection Fixture

This dependency-free fixture validates workflow evidence; it does not rank model quality or emulate Codex or Claude Code. All product-independent rules are explicit: a declared recommendation, immutable base, non-overlapping outputs, at most one writer, complete role contracts, and rationale tied to task evidence. Claude Code scenarios also record a dated 2026-09-10 review of restricted mode, fail-closed sandbox configuration, managed policy, plugin inventory, and loop-usage monitoring; the record does not prove those controls are active.

Run this block from `examples/module-09/tool-selection`.

```powershell
python decision.py scenarios/local-implementation.json
python decision.py scenarios/architecture-review.json
python decision.py scenarios/bounded-sequence.json
python decision.py scenarios/unsafe-dual-edit.json
python -m unittest discover -s tests -v
```

Valid scenarios exit 0 and print JSON. Invalid scenarios exit 1 with actionable issues; ten tests cover durable selection and the dated control review. No command invokes a model, reads credentials, accesses the network, writes files, or changes product configuration.
