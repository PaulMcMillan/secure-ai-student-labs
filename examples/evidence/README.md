# Shared RAG observation

`EV-RAG-01.json` is the supplied redacted course observation dated 2026-09-10. It records source SHA-256 digests, index integrity and version, ingestion counts, and aggregate evaluation results for the synthetic offline RAG fixture.

Run `python scripts/validate_course.py` from the repository root to rebuild the index in a temporary directory, execute a cited query and evaluation, and compare the fresh counts, categories, metrics, and index digests with this observation. The script also runs the M02 and M03 unit tests.

The observation describes synthetic local behavior. It does not attest to a live model, production deployment, or real approval.
