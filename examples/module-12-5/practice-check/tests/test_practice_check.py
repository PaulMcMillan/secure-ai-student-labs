from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from practice_check import check, load


class PracticeCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = load(ROOT / "task.json")
        cls.complete = load(ROOT / "records" / "complete.json")

    def report(self, mutate=None):
        record = deepcopy(self.complete)
        if mutate:
            mutate(record)
        return check(self.task, record)

    def test_complete_record_passes(self):
        report = self.report()
        self.assertTrue(report["valid"], report["issues"])
        self.assertEqual(report["practice_count"], 12)

    def test_starter_record_fails(self):
        self.assertFalse(check(self.task, load(ROOT / "records" / "starter.json"))["valid"])

    def test_unsafe_record_is_critical(self):
        report = check(self.task, load(ROOT / "records" / "unsafe.json"))
        self.assertFalse(report["valid"])
        self.assertTrue(report["critical_safety_failure"])

    def test_contract_is_bounded(self):
        report = self.report(lambda record: record["contract"].update({"start_ref": "latest"}))
        self.assertFalse(report["contract_ready"])

    def test_context_is_curated(self):
        report = self.report(lambda record: record["context"].update({"acceptance_linked": False}))
        self.assertFalse(report["context_curated"])

    def test_guidance_uses_effective_scope(self):
        report = self.report(lambda record: record["guidance"].update({"conflicts_resolved": False}))
        self.assertFalse(report["guidance_scoped"])

    def test_plan_has_validated_deliverables(self):
        report = self.report(lambda record: record["plan"]["steps"][0].update({"validation": ""}))
        self.assertFalse(report["plan_risk_aligned"])

    def test_permissions_and_tools_remain_minimal(self):
        record = deepcopy(self.complete)
        record["permissions"]["network_allowed"] = True
        record["tools"]["external"] = ["live-system"]
        report = check(self.task, record)
        self.assertFalse(report["permissions_least"])
        self.assertFalse(report["tools_minimal"])

    def test_plugin_inventory_and_hot_refresh_need_governance(self):
        record = deepcopy(self.complete)
        record["tools"]["plugin_inventory"] = [{
            "artifact_kind": "synthetic-training-fixture",
            "id": "synthetic-rag-eval-plugin",
            "version": "1.0.0",
            "digest": "short",
            "permissions": ["read-rag-evidence"],
        }]
        record["tools"]["hot_refresh_reapproval_required"] = False
        self.assertFalse(check(self.task, record)["tools_minimal"])

    def test_budget_has_an_escalation_boundary(self):
        report = self.report(lambda record: record["budget"].update({"actual_iterations": 4}))
        self.assertFalse(report["budget_bounded"])

    def test_validation_and_review_are_evidence_backed(self):
        record = deepcopy(self.complete)
        record["validation"][0]["fabricated"] = True
        record["review"]["reviewer"] = record["review"]["author"]
        report = check(self.task, record)
        self.assertFalse(report["validation_layered"])
        self.assertFalse(report["review_ready"])

    def test_rag_operating_loop_requires_bound_metrics_and_owner(self):
        record = deepcopy(self.complete)
        record["rag_operations"]["observed_evidence"]["sha256"] = "0" * 64
        record["rag_operations"]["metric_results"]["cross_tenant_block_rate"] = 0.0
        record["rag_operations"]["owner"] = ""
        report = check(self.task, record)
        self.assertFalse(report["rag_evidence_bound"])
        self.assertFalse(report["rag_operations_ready"])

    def test_reuse_and_retrospective_require_evidence(self):
        record = deepcopy(self.complete)
        record["reuse"].update({"automated": True, "repeat_count": 1})
        record["retrospective"]["measure"] = ""
        report = check(self.task, record)
        self.assertFalse(report["reuse_evidence_based"])
        self.assertFalse(report["retrospective_measurable"])

    def test_checker_performs_no_external_actions(self):
        source = (ROOT / "practice_check.py").read_text(encoding="utf-8")
        for forbidden in ["subprocess", "requests", "urlopen", "socket", "os.system"]:
            self.assertNotIn(forbidden, source)
        report = self.report()
        for field in ["commands_executed", "model_called", "network_used", "credentials_read", "git_operations_run"]:
            self.assertFalse(report[field])


if __name__ == "__main__":
    unittest.main()
