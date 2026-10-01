# Module 12 Release-Evidence Capstone

This offline fixture combines a working pricing change with a machine-checkable enterprise evidence bundle and a release record for the pre-staged functional [`examples/rag-reference`](../../rag-reference/README.md) workload. The RAG record references the checked-in redacted `EV-RAG-01` observation by path and full SHA-256. The checker independently hashes the observation, manifest, evaluation cases, and implementation and requires matching full corpus/index/configuration digests, exact ingest counts, eight category results, and ten metric results.

## Student activity

Follow the [M12 workbook directions](../../../WORKBOOK_GUIDE.md#m12--release-evidence-capstone) for preparation, implementation, evidence, and independent review. From the lab collection root, run:

```sh
python scripts/prepare_coding_lab.py m12 ../m12-work
```

Open the printed folder as your working project. It includes the [function contract](starter/WORK_ITEM.md), [project instructions](starter/AGENTS.md), `task.json`, baseline code/tests, and `evidence/capstone.json`. Run `python -m unittest discover -s tests -v` **inside m12-work**, before and after your change. The helper creates a Git baseline and exercise branch when Git is installed; the final evidence gate needs that real baseline.

Keep a second terminal at the lab collection root for M03 and the evidence checker. Create `student-results` there, then validate your own record from that terminal:

```sh
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json ../m12-work/evidence/capstone.json > student-results/m12-check.json
```

Open the report and address its `issues`. The starter exits `1`; a complete record exits `0`. Substitute your folder name if you used a different destination. Keep actual outputs and incomplete gates honest.

## Reference checks after your attempt

Run these from the lab collection root. They check the supplied fixtures; your implementation is tested inside `m12-work`.

```powershell
python -m unittest discover -s examples/module-12/release-evidence/starter/tests -v
python -m unittest discover -s examples/module-12/release-evidence/solution/tests -v
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/complete.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/unsafe.json
python -m unittest discover -s examples/module-12/release-evidence/tests -v
```

The starter has two passing baseline tests. The solution has five passing tests. The complete evidence exits `0`; starter and unsafe evidence exit `1`; the checker suite runs thirteen tests. Only the repository-wide `scripts/validate_course.py` reruns ingest, query, and evaluation behavior and compares that observed output with `EV-RAG-01`.

`evidence_check.py` is read-only and does not execute recorded commands, call a model, read credentials, use the network, or perform Git operations. It proves only the structure, checked-in file bindings, and internal consistency of recorded evidence. It does not prove that a production model, review, approval, release, or rollback occurred.
