"""Validate the student bundle using Python 3.11+ and the standard library."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True,
        text=True, timeout=60, check=True,
    )
    return json.loads(result.stdout)


def validate_rag() -> None:
    """Rebuild and compare actual behavior with the supplied course observation."""
    observed = json.loads((ROOT / "examples/evidence/EV-RAG-01.json").read_text())
    script = "examples/rag-reference/rag.py"
    with tempfile.TemporaryDirectory(prefix="student-rag-") as temporary:
        index = str(Path(temporary) / "index.json")
        ingest = run_json(script, "ingest", "--manifest",
                          "examples/rag-reference/corpus/manifest.json", "--index", index)
        query = run_json(script, "query", "--index", index, "--principal", "learner-alpha",
                         "--tenant", "northstar", "--roles", "employee", "--clearances",
                         "internal", "--question", "What is the travel approval threshold?")
        report = run_json(script, "eval", "--index", index,
                          "--cases", "examples/rag-reference/evals/cases.json")
        failures = []
        for key, expected in observed["ingestion"].items():
            actual_key = "quarantined_document_count" if key == "scanner_quarantined_document_count" else key
            if ingest.get(actual_key) != expected:
                failures.append(f"ingestion mismatch: {key}")
        for key in ("integrity_sha256", "index_version"):
            if ingest.get(key) != observed["index"][key] or report.get(key) != observed["index"][key]:
                failures.append(f"index mismatch: {key}")
        if query.get("status") != "answered" or not query.get("citations"):
            failures.append("authorized query did not return a cited answer")
        categories = {row["category"]: "pass" if row["passed"] else "fail" for row in report["cases"]}
        expected_eval = observed["evaluation"]
        if (report["total"] != expected_eval["case_count"]
                or report["passed"] != expected_eval["passed_count"]
                or report["all_passed"] is not True
                or categories != expected_eval["category_results"]
                or report["metrics"] != expected_eval["metric_results"]):
            failures.append("evaluation differs from EV-RAG-01")
        if failures:
            raise ValueError("; ".join(failures))
    print("PASS RAG ingestion, cited query, 8 evaluation cases, and observed digests", flush=True)


def main() -> int:
    if sys.version_info < (3, 11):
        print("Python 3.11 or newer is required.", file=sys.stderr)
        return 1
    failures = []
    count = 0
    suites = sorted((ROOT / "examples").rglob("tests"))
    for suite in suites:
        if not suite.is_dir() or not list(suite.glob("test_*.py")):
            continue
        # Separate processes prevent identically named training modules colliding.
        # Running in each fixture root also supports the nested inventory imports.
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                cwd=suite.parent, capture_output=True, text=True, timeout=120,
            )
            output = result.stdout + result.stderr
            match = re.search(r"Ran (\d+) tests?", output)
            if match:
                count += int(match.group(1))
            if result.returncode or not match or int(match.group(1)) == 0:
                failures.append(str(suite.relative_to(ROOT)))
                print(output, flush=True)
            else:
                print(f"PASS {suite.relative_to(ROOT)} ({match.group(1)} tests)", flush=True)
        except subprocess.TimeoutExpired:
            failures.append(str(suite.relative_to(ROOT)) + " timed out")
    try:
        validate_rag()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        failures.append(f"RAG behavior: {exc}")
    print(f"\n{count} tests; {len(failures)} failed checks.", flush=True)
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
