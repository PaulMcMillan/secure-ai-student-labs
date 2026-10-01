# Module 12 Release-Evidence Capstone

This offline fixture combines a working pricing change with a machine-checkable enterprise evidence bundle and a release record for the pre-staged functional [`examples/rag-reference`](../../rag-reference/README.md) workload. The RAG record references the checked-in redacted `EV-RAG-01` observation by path and full SHA-256. The checker independently hashes the observation, manifest, evaluation cases, and implementation and requires matching full corpus/index/configuration digests, exact ingest counts, eight category results, and ten metric results.

## Run

```powershell
python -m unittest discover -s examples/module-12/release-evidence/starter/tests -v
python -m unittest discover -s examples/module-12/release-evidence/solution/tests -v
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/complete.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/unsafe.json
python -m unittest discover -s examples/module-12/release-evidence/tests -v
```

The starter has two passing baseline tests. The solution has five passing tests. The complete evidence exits `0`; starter and unsafe evidence exit `1`; the checker suite runs thirteen tests. Only the repository-wide `scripts/validate_course.py` reruns ingest, query, and evaluation behavior and compares that observed output with `EV-RAG-01`.

`evidence_check.py` is read-only and does not execute recorded commands, call a model, read credentials, use the network, or perform Git operations. It proves only the structure, checked-in file bindings, and internal consistency of recorded evidence. It does not prove that a production model, review, approval, release, or rollback occurred.
