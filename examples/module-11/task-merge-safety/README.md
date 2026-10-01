# Module 11 Parallel RAG Evidence and Merge-Safety Fixture

This dependency-free fixture evaluates a synthetic multi-agent RAG evidence workflow. Parallel roles inventory immutable corpus/evaluation inputs, produce separate retrieval-quality and security reports, undergo independent review, and enter one owned integration decision. Every task, report, and integration record must reference the same checked-in redacted `EV-RAG-01` artifact and match its full corpus/index/configuration/evaluation-case digests. The checker independently hashes the observation and its checked-in source files.

Run this block from `examples/module-11/task-merge-safety`.

```powershell
python merge_check.py task.json evidence/complete.json
python merge_check.py task.json evidence/unsafe.json
python -m unittest discover -s tests -v
```

The complete record exits 0. Starter and unsafe records exit 1; twelve tests cover graph, schedule, write isolation, scope, bases, role authority, operational controls, independent review, integration order, RAG release consistency, and explicit stopping. `merge_check.py` is read-only: it does not spawn agents, execute recorded commands, call a model, create a worktree, inspect credentials, access the network, run Git, or merge code. Only the repository-wide `scripts/validate_course.py` reruns the functional [`examples/rag-reference`](../../rag-reference/README.md) behavior. Real agent, review, and integration claims still require production evidence.
