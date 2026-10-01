import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workflow_check import evaluate  # noqa: E402


TASK = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
COMPLETE = json.loads((ROOT / "evidence" / "complete.json").read_text(encoding="utf-8"))
UNSAFE = json.loads((ROOT / "evidence" / "unsafe.json").read_text(encoding="utf-8"))


class WorkflowCheckTests(unittest.TestCase):
    def test_complete_evidence_passes(self):
        report = evaluate(TASK, COMPLETE)
        self.assertTrue(report["valid"])
        self.assertEqual(report["state_count"], 10)

    def test_unsafe_evidence_fails(self):
        report = evaluate(TASK, UNSAFE)
        self.assertFalse(report["valid"])
        self.assertGreaterEqual(len(report["issues"]), 5)

    def test_state_order_is_required(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["events"][1], evidence["events"][2] = evidence["events"][2], evidence["events"][1]
        self.assertFalse(evaluate(TASK, evidence)["valid"])

    def test_required_evidence_is_required(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["events"][4]["evidence"].remove("retrieval-eval")
        self.assertFalse(evaluate(TASK, evidence)["gates_passed"])

    def test_changed_paths_must_remain_in_scope(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["changed_paths"].append("release/production.yml")
        self.assertFalse(evaluate(TASK, evidence)["scope_ok"])

    def test_authority_must_match_state_contract(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["events"][5]["authority"] = "write"
        self.assertFalse(evaluate(TASK, evidence)["valid"])

    def test_failed_gate_blocks_completion(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["events"][4]["result"] = "fail"
        self.assertFalse(evaluate(TASK, evidence)["gates_passed"])

    def test_implementer_cannot_self_approve(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["events"][6]["owner"] = evidence["events"][3]["owner"]
        self.assertFalse(evaluate(TASK, evidence)["separation_of_duties"])

    def test_rollback_must_be_validated(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["rollback"]["validation_result"] = "not-run"
        self.assertFalse(evaluate(TASK, evidence)["rollback_ready"])

        evidence = copy.deepcopy(COMPLETE)
        evidence["rollback"]["validation_command"] = "python -m unittest discover -s tests -v"
        self.assertFalse(evaluate(TASK, evidence)["rollback_ready"])

    def test_rag_release_requires_the_pinned_observation_and_digests(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["rag_release"]["observed_evidence"]["path"] = "examples/evidence/not-the-contract.json"
        report = evaluate(TASK, evidence)
        self.assertFalse(report["rag_evidence_bound"])
        self.assertFalse(report["rag_release_ready"])

        evidence = copy.deepcopy(COMPLETE)
        evidence["rag_release"]["digests"]["index"] = "0" * 64
        self.assertFalse(evaluate(TASK, evidence)["rag_release_ready"])

    def test_rag_release_requires_exact_metrics_and_owned_monitoring(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["rag_release"]["metric_results"]["cross_tenant_block_rate"] = 0.0
        evidence["rag_release"]["monitoring"]["owner"] = ""
        self.assertFalse(evaluate(TASK, evidence)["rag_release_ready"])

    def test_checker_performs_no_external_actions(self):
        report = evaluate(TASK, COMPLETE)
        self.assertFalse(report["commands_executed"])
        self.assertFalse(report["credentials_read"])
        self.assertFalse(report["network_used"])
        self.assertFalse(report["secrets_in_evidence"])


if __name__ == "__main__":
    unittest.main()
