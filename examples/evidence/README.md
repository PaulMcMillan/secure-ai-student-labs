# Shared Observed Evidence

`EV-RAG-01.json` is the redacted aggregate from the offline secure-RAG reference run dated 2026-09-10. It binds the manifest, evaluation-case file, and implementation by full SHA-256; records the index integrity/version and ingest counts; and preserves only aggregate category and metric results. It intentionally excludes questions, answers, document content, identity attributes, citations, and traces.

Module 10, 11, 12, and 12.5 checkers read this file and independently hash every checked-in source it references. Those structure checkers never execute the recorded RAG commands. `scripts/validate_course.py` is the repository-wide behavioral validator: it rebuilds the index in a temporary directory, reruns the evaluation, and compares the fresh counts, category results, metric results, index integrity, and index version with `EV-RAG-01`.

Any change to `rag.py`, `corpus/manifest.json`, or `evals/cases.json` invalidates this observation. Rerun repository validation, review the new output, replace the observation only when the change is intended, and then update every pinned observation SHA-256 in the complete module records.
