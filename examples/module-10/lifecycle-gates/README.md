# Module 10 RAG Lifecycle-Gates Fixture

This offline fixture validates a synthetic RAG ingestion/release workflow against `task.json`. The complete record references the checked-in, redacted `EV-RAG-01` observation by path and full SHA-256. The checker independently hashes the referenced observation, manifest, evaluation-case file, and implementation; then it requires the same full corpus/index/configuration digests, observed ingest counts, eight category results, and ten metric results. It also checks owned monitoring, rollback, and ordinary lifecycle evidence.

Run this block from `examples/module-10/lifecycle-gates`.

```powershell
python workflow_check.py task.json evidence/complete.json
python workflow_check.py task.json evidence/unsafe.json
python -m unittest discover -s tests -v
```

The complete record exits 0. The unsafe and starter records exit 1 with actionable issues; twelve tests exercise the contract. `workflow_check.py` is read-only and never executes a recorded command, calls a model, reads credentials, uses the network, modifies code, or releases software. Only the repository-wide `scripts/validate_course.py` reruns the functional [`examples/rag-reference`](../../rag-reference/README.md) behavior. Neither validator attests to production behavior.
