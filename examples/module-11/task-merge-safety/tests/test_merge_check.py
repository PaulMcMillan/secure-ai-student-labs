import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from merge_check import evaluate  # noqa: E402


CONTRACT = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
COMPLETE = json.loads((ROOT / "evidence" / "complete.json").read_text(encoding="utf-8"))
UNSAFE = json.loads((ROOT / "evidence" / "unsafe.json").read_text(encoding="utf-8"))


class MergeCheckTests(unittest.TestCase):
    def test_complete_record_passes(self):
        report = evaluate(CONTRACT, COMPLETE)
        self.assertTrue(report["valid"])
        self.assertEqual(report["task_count"], 6)

    def test_unsafe_record_fails(self):
        report = evaluate(CONTRACT, UNSAFE)
        self.assertFalse(report["valid"])
        self.assertGreaterEqual(len(report["issues"]), 6)

    def test_cycle_is_rejected(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][0]["depends_on"] = ["implement-code"]
        self.assertFalse(evaluate(CONTRACT, evidence)["dag_valid"])

    def test_dependency_must_be_in_earlier_wave(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["waves"][0], evidence["waves"][1] = evidence["waves"][1], evidence["waves"][0]
        self.assertFalse(evaluate(CONTRACT, evidence)["schedule_valid"])

    def test_parallel_writes_must_be_disjoint(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][3]["paths"] = ["evidence/retrieval-quality.json"]
        evidence["tasks"][3]["write_paths"] = ["evidence/retrieval-quality.json"]
        self.assertFalse(evaluate(CONTRACT, evidence)["writes_disjoint"])

    def test_every_task_uses_pinned_base(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][2]["base_commit"] = "latest"
        self.assertFalse(evaluate(CONTRACT, evidence)["bases_ok"])

    def test_paths_remain_in_scope(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][2]["paths"].append("release.yml")
        self.assertFalse(evaluate(CONTRACT, evidence)["scope_ok"])

    def test_agent_operations_require_inheritance_budget_and_cancel_owner(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["operations"]["permission_inheritance_verified"] = False
        evidence["operations"]["goal_budget_accounted"] = False
        evidence["operations"]["cancellation_owner"] = ""
        self.assertFalse(evaluate(CONTRACT, evidence)["operations_ready"])

    def test_each_task_needs_finite_budget_and_stop(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][2]["budget"]["max_attempts"] = 99
        evidence["tasks"][2]["stop_condition"] = ""
        self.assertFalse(evaluate(CONTRACT, evidence)["valid"])

    def test_reviewer_must_be_independent_and_read_only(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["tasks"][4]["owner"] = evidence["tasks"][2]["owner"]
        self.assertFalse(evaluate(CONTRACT, evidence)["review_independent"])

    def test_integration_requires_all_validation(self):
        evidence = copy.deepcopy(COMPLETE)
        evidence["integration"]["validation"].remove("authorization-tests")
        self.assertFalse(evaluate(CONTRACT, evidence)["integration_ready"])

        evidence = copy.deepcopy(COMPLETE)
        evidence["reports"][0]["rag_release_digests"]["index"] = "0" * 64
        report = evaluate(CONTRACT, evidence)
        self.assertFalse(report["rag_release_consistent"])

    def test_checker_performs_no_external_actions(self):
        report = evaluate(CONTRACT, COMPLETE)
        self.assertFalse(report["agents_spawned"])
        self.assertFalse(report["git_operations_run"])
        self.assertFalse(report["credentials_read"])
        self.assertFalse(report["network_used"])
        self.assertFalse(report["secrets_in_evidence"])


if __name__ == "__main__":
    unittest.main()
