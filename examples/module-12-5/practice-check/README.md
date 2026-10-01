# Module 12.5 Best-Practice Packet Checker

This standard-library-only fixture checks twelve durable engineering practices in a synthetic RAG operating packet. It includes optional synthetic-plugin admission rules, hot-refresh reapproval, functional/security RAG evaluation, monitoring, alerting, rollback/reindex, and promotion evidence. No plugin is required by the complete record. Its RAG section references the checked-in redacted `EV-RAG-01` observation by path and full SHA-256; the checker independently hashes that artifact and its manifest, evaluation cases, and implementation.

```powershell
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/complete.json
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/unsafe.json
python -m unittest discover -s examples/module-12-5/practice-check/tests -v
```

The complete record exits `0`; starter and unsafe records exit `1`; the suite runs fourteen tests. `practice_check.py` is read-only and never executes recorded commands, calls a model, uses the network, reads credentials, or performs Git operations. Only the repository-wide `scripts/validate_course.py` reruns the functional [`examples/rag-reference`](../../rag-reference/README.md) behavior. Passing proves checked-in bindings and internal structure, not that any production engineering activity occurred.
