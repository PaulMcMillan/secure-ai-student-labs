from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidence_check import load_json, validate


class EvidenceCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = load_json(ROOT / "task.json")
        cls.complete = load_json(ROOT / "evidence" / "complete.json")

    def report(self, mutate=None):
        record = deepcopy(self.complete)
        if mutate:
            mutate(record)
        return validate(self.task, record)

    def test_complete_bundle_passes(self):
        report = self.report()
        self.assertTrue(report["valid"], report["issues"])
        self.assertEqual(report["evidence_domain_count"], 11)

    def test_starter_bundle_fails(self):
        report = validate(self.task, load_json(ROOT / "evidence" / "starter.json"))
        self.assertFalse(report["valid"])

    def test_unsafe_bundle_fails_critically(self):
        report = validate(self.task, load_json(ROOT / "evidence" / "unsafe.json"))
        self.assertFalse(report["valid"])
        self.assertTrue(report["critical_safety_failure"])

    def test_scope_is_bounded(self):
        report = self.report(lambda record: record["scope"]["changed_paths"].append("../outside.txt"))
        self.assertFalse(report["scope_ok"])

    def test_instruction_trace_is_required(self):
        report = self.report(lambda record: record["instructions"].update({"conflicts_resolved": False}))
        self.assertFalse(report["instruction_trace"])

    def test_context_excludes_restricted_data(self):
        report = self.report(lambda record: record["context"].update({"synthetic_only": False}))
        self.assertFalse(report["context_ready"])

    def test_cost_stays_within_budget(self):
        report = self.report(lambda record: record["cost"]["actual"].update({"iterations": 4}))
        self.assertFalse(report["cost_bounded"])

    def test_tools_do_not_expand_authority(self):
        report = self.report(lambda record: record["tools"].update({"network_allowed": True}))
        self.assertFalse(report["tool_controls"])

    def test_workflow_and_security_gates_are_required(self):
        record = deepcopy(self.complete)
        record["workflow"]["gates"]["review"] = "skip"
        record["security"]["input_validation"] = False
        report = validate(self.task, record)
        self.assertFalse(report["workflow_complete"])
        self.assertFalse(report["security_ready"])

    def test_rag_requires_bound_observation_exact_metrics_and_monitoring(self):
        record = deepcopy(self.complete)
        record["rag"]["observed_evidence"]["sha256"] = "0" * 64
        record["rag"]["metric_results"]["poison_block_rate"] = 0.0
        record["rag"]["monitoring"]["owner"] = ""
        report = validate(self.task, record)
        self.assertFalse(report["rag_evidence_bound"])
        self.assertFalse(report["rag_ready"])

    def test_validation_cannot_be_fabricated(self):
        report = self.report(lambda record: record["validation"][0].update({"fabricated": True}))
        self.assertFalse(report["tests_passed"])

    def test_review_and_release_are_owned(self):
        record = deepcopy(self.complete)
        record["review"]["reviewer"] = record["review"]["author"]
        record["release"]["rollback_ready"] = False
        report = validate(self.task, record)
        self.assertFalse(report["review_independent"])
        self.assertFalse(report["release_ready"])

    def test_checker_performs_no_external_actions(self):
        source = (ROOT / "evidence_check.py").read_text(encoding="utf-8")
        for forbidden in ["subprocess", "requests", "urlopen", "socket", "os.system"]:
            self.assertNotIn(forbidden, source)
        report = self.report()
        for field in ["commands_executed", "model_called", "network_used", "credentials_read", "git_operations_run"]:
            self.assertFalse(report[field])


if __name__ == "__main__":
    unittest.main()
