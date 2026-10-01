# Capstone project guidance

- Use Python 3.11+ and the standard library only.
- Use synthetic data. Do not access the network, credentials, plugins, or production systems.
- Follow `WORK_ITEM.md` and the copied `task.json`. Allowed paths are relative to this working project: `pricing.py`, `tests/test_pricing.py`, `evidence/capstone.json`, and `evidence/rag-report.json`.
- Preserve `quote_total` and its existing behavior. Keep the change focused on the explanation function and its tests.
- From this project root, run `python -m unittest discover -s tests -v` before and after the change. Review the diff and report the actual results and remaining risks.
- The learner runs the shared RAG activity and evidence checker from the separate lab collection. Reference those results honestly in the evidence record.
- Stop on a failing baseline, an instruction conflict, or required work outside the allowed paths. Do not claim approval, independent review, or a release that did not occur.
