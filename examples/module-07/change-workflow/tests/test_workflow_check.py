import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from workflow_check import evaluate  # noqa: E402


class WorkflowCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
        cls.complete = json.loads(
            (ROOT / "evidence" / "complete.json").read_text(encoding="utf-8")
        )

    def changed(self):
        return copy.deepcopy(self.complete)

    def test_complete_evidence_is_valid(self):
        self.assertTrue(evaluate(self.task, self.changed())["valid"])

    def test_task_id_must_match(self):
        evidence = self.changed()
        evidence["task_id"] = "OTHER"
        self.assertIn("task_id_mismatch", evaluate(self.task, evidence)["issues"])

    def test_model_contract_is_required_and_authority_invariant(self):
        evidence = self.changed()
        evidence["model_contract"]["astra_authority_unchanged"] = False
        self.assertIn("model_contract_invalid", evaluate(self.task, evidence)["issues"])

    def test_stage_order_is_required(self):
        evidence = self.changed()
        evidence["stages"] = list(reversed(evidence["stages"]))
        self.assertIn("stage_order_incomplete", evaluate(self.task, evidence)["issues"])

    def test_changed_files_must_stay_in_scope(self):
        evidence = self.changed()
        evidence["changed_files"].append("../secrets.txt")
        self.assertIn("changed_scope_invalid", evaluate(self.task, evidence)["issues"])

    def test_required_command_must_be_recorded(self):
        evidence = self.changed()
        evidence["commands"] = []
        report = evaluate(self.task, evidence)
        self.assertIn("required_check_missing", report["issues"])
        self.assertIn("check_failed_or_unrecorded", report["issues"])

    def test_failed_check_blocks_completion(self):
        evidence = self.changed()
        evidence["commands"][0]["exit_code"] = 1
        self.assertIn("check_failed_or_unrecorded", evaluate(self.task, evidence)["issues"])

    def test_acceptance_must_be_complete(self):
        evidence = self.changed()
        evidence["acceptance"][0]["satisfied"] = False
        self.assertIn("acceptance_incomplete", evaluate(self.task, evidence)["issues"])

    def test_diff_and_secret_review_are_required(self):
        evidence = self.changed()
        evidence["diff_review"] = {"completed": False, "secret_scan": False}
        report = evaluate(self.task, evidence)
        self.assertIn("diff_review_missing", report["issues"])
        self.assertIn("secret_review_missing", report["issues"])

    def test_authority_cannot_expand(self):
        evidence = self.changed()
        evidence["authority_expanded"] = True
        self.assertIn("authority_expanded", evaluate(self.task, evidence)["issues"])


if __name__ == "__main__":
    unittest.main()
