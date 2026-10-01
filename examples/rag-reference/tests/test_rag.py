from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rag_reference", ROOT / "rag.py")
assert SPEC and SPEC.loader
rag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rag)


class RagReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = rag.build_index(ROOT / "corpus" / "manifest.json")

    def test_poisoned_document_is_quarantined_and_not_chunked(self) -> None:
        poisoned = next(doc for doc in self.index["documents"] if doc["source_id"] == "vendor-note-quarantined")
        self.assertTrue(poisoned["quarantined"])
        self.assertIn("instruction_override", poisoned["quarantine_reasons"])
        self.assertIn("secret_request", poisoned["quarantine_reasons"])
        self.assertNotIn("manifest_marked", poisoned["quarantine_reasons"])
        self.assertNotIn("vendor-note-quarantined", {chunk["source_id"] for chunk in self.index["chunks"]})

    def test_load_rejects_policy_or_chunk_tampering(self) -> None:
        for target in ("policy", "chunk"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                changed = json.loads(json.dumps(self.index))
                if target == "policy":
                    changed["documents"][0]["classification"] = "public"
                else:
                    changed["chunks"][0]["text"] = "tampered text"
                path = Path(directory) / "index.json"
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaisesRegex(rag.RagError, "index integrity"):
                    rag.load_index(path)

    def test_authorized_answer_has_grounded_citation(self) -> None:
        result = rag.answer_query(
            self.index,
            principal="learner-alpha",
            tenant="northstar",
            roles=["employee"],
            clearances=["internal"],
            question="What is the travel approval threshold?",
        )
        self.assertEqual("answered", result["status"])
        self.assertIn("$500", result["answer"])
        self.assertEqual("northstar-travel-2026", result["citations"][0]["source_id"])
        self.assertIn(result["citations"][0]["quote"], result["answer"])
        self.assertRegex(result["citations"][0]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(result["citations"][0]["content_sha256"], result["retrieved"][0]["content_sha256"])

    def test_cross_tenant_source_is_filtered_before_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            telemetry = Path(directory) / "telemetry.jsonl"
            result = rag.answer_query(
                self.index,
                principal="learner-alpha",
                tenant="northstar",
                roles=["employee"],
                clearances=["internal"],
                question="What is the Southstar acquisition project codename?",
                telemetry_path=telemetry,
            )
            classification_denied = rag.answer_query(
                self.index,
                principal="learner-alpha",
                tenant="northstar",
                roles=["employee"],
                clearances=["internal"],
                question="What must happen before a consequential production action?",
                telemetry_path=telemetry,
            )
            events = [json.loads(line) for line in telemetry.read_text(encoding="utf-8").splitlines()]
        self.assertEqual("abstained", result["status"])
        self.assertNotIn("southstar-acquisition-private", {item["source_id"] for item in result["retrieved"]})
        self.assertNotIn("filtered_documents", result["budget"])
        self.assertGreaterEqual(events[0]["policy_filter_counts"]["tenant"], 1)
        self.assertEqual("abstained", classification_denied["status"])
        self.assertNotIn("northstar-ai-security-2026", {item["source_id"] for item in classification_denied["retrieved"]})
        self.assertNotIn("filtered_documents", classification_denied["budget"])
        self.assertGreaterEqual(events[1]["policy_filter_counts"]["classification"], 1)
        legal_hold_authorized = rag.answer_query(
            self.index,
            principal="security-alpha",
            tenant="northstar",
            roles=["employee"],
            clearances=["restricted"],
            question="What do consequential actions require?",
        )
        self.assertEqual("answered", legal_hold_authorized["status"])
        self.assertEqual("legal_hold", legal_hold_authorized["citations"][0]["deletion_status"])

    def test_expired_and_deletion_pending_sources_are_filtered(self) -> None:
        expired = rag.answer_query(
            self.index,
            principal="learner-alpha",
            tenant="northstar",
            roles=["employee"],
            clearances=["internal"],
            question="What was the retired daily meal cap?",
        )
        deletion_pending = rag.answer_query(
            self.index,
            principal="learner-alpha",
            tenant="northstar",
            roles=["employee"],
            clearances=["internal"],
            question="What proposed travel threshold begins in 2027?",
            as_of=rag.date(2027, 6, 1),
        )
        self.assertEqual("abstained", expired["status"])
        self.assertEqual("abstained", deletion_pending["status"])
        self.assertNotIn("filtered_documents", deletion_pending["budget"])
        self.assertNotIn("northstar-travel-2027-draft", {chunk["source_id"] for chunk in self.index["chunks"]})

    def test_budget_is_enforced(self) -> None:
        result = rag.answer_query(
            self.index,
            principal="learner-alpha",
            tenant="northstar",
            roles=["employee"],
            clearances=["internal"],
            question=" ".join(f"token{number}" for number in range(30)),
        )
        self.assertEqual("blocked", result["status"])
        self.assertEqual("deny_budget", result["policy_decision"])

    def test_telemetry_excludes_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.jsonl"
            secret_question = "What is the travel approval threshold?"
            result = rag.answer_query(
                self.index,
                principal="learner-alpha",
                tenant="northstar",
                roles=["employee"],
                clearances=["internal"],
                question=secret_question,
                telemetry_path=path,
            )
            raw = path.read_text(encoding="utf-8")
            event = json.loads(raw)
            self.assertNotIn(secret_question, raw)
            self.assertTrue(result["answer"])
            self.assertNotIn(result["answer"], raw)
            self.assertNotIn("employee", raw)
            self.assertNotIn("internal", raw)
            for forbidden_field in ("principal_hash", "tenant_hash", "query_hash"):
                self.assertNotIn(forbidden_field, event)
            self.assertFalse(event["content_logged"])
            self.assertEqual(result["trace_id"], event["trace_id"])
            self.assertIn("policy_filter_counts", event)

    def test_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps({
                "schema_version": "1.0",
                "corpus_id": "bad",
                "corpus_version": "1",
                "documents": [{
                    "source_id": "escape", "path": "../outside.md", "title": "Escape",
                    "tenant": "northstar", "allowed_roles": ["employee"], "classification": "internal",
                    "effective_date": "2026-01-01", "expires_at": "2026-12-31"
                }]
            }), encoding="utf-8")
            with self.assertRaises(rag.RagError):
                rag.build_index(path)
        bad_manifest = json.loads(json.dumps(self.index["documents"][0]))
        bad_manifest.pop("content_sha256")
        bad_manifest.pop("quarantined")
        bad_manifest.pop("quarantine_reasons")
        bad_manifest["path"] = "documents/travel-policy.md"
        bad_manifest["classification"] = "invented-by-caller"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "documents").mkdir()
            (root / "documents" / "travel-policy.md").write_text("training", encoding="utf-8")
            bad_manifest.pop("sha256", None)
            path = root / "manifest.json"
            path.write_text(json.dumps({"schema_version": "1.0", "corpus_id": "bad", "corpus_version": "1", "documents": [bad_manifest]}), encoding="utf-8")
            with self.assertRaisesRegex(rag.RagError, "classification"):
                rag.build_index(path)

    def test_all_quality_and_security_evals_pass(self) -> None:
        report = rag.evaluate(self.index, ROOT / "evals" / "cases.json")
        self.assertTrue(report["all_passed"], report)
        for value in report["metrics"].values():
            self.assertEqual(1.0, value)


if __name__ == "__main__":
    unittest.main()
