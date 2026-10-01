"""Tests for the Module 5 steering-plan checker."""

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from steering_check import evaluate  # noqa: E402


class SteeringCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
        cls.structured = json.loads((ROOT / "plans" / "structured.json").read_text(encoding="utf-8"))
        cls.unsafe = json.loads((ROOT / "plans" / "unsafe.json").read_text(encoding="utf-8"))

    def test_structured_plan_is_valid(self) -> None:
        report = evaluate(self.task, self.structured)
        self.assertTrue(report["valid"])
        self.assertEqual(report["phase_count"], 5)

    def test_unsafe_plan_is_rejected(self) -> None:
        report = evaluate(self.task, self.unsafe)
        self.assertFalse(report["valid"])
        self.assertTrue(report["authority_expanded"])

    def test_model_contract_is_required_and_authority_invariant(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["model_contract"]["astra_authority_unchanged"] = False
        report = evaluate(self.task, plan)
        self.assertFalse(report["valid"])
        self.assertFalse(report["model_contract_valid"])

    def test_skipping_plan_is_rejected(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["phases"] = [phase for phase in plan["phases"] if phase["posture"] != "Plan"]
        report = evaluate(self.task, plan)
        self.assertFalse(report["valid"])
        self.assertTrue(any("posture sequence" in issue for issue in report["issues"]))

    def test_scope_expansion_is_rejected(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["phases"][2]["scope"].append("deployment/production.yml")
        self.assertTrue(any("exceeds allowed scope" in issue for issue in evaluate(self.task, plan)["issues"]))

    def test_missing_stop_is_rejected(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["phases"][1]["stopping_condition"] = "continue"
        self.assertFalse(evaluate(self.task, plan)["valid"])

    def test_wrong_exit_evidence_is_rejected(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["phases"][3]["exit_evidence"] = "tests-not-run"
        self.assertFalse(evaluate(self.task, plan)["valid"])

    def test_required_constraints_apply_to_every_phase(self) -> None:
        plan = json.loads(json.dumps(self.structured))
        plan["phases"][4]["constraints"] = []
        self.assertFalse(evaluate(self.task, plan)["valid"])


if __name__ == "__main__":
    unittest.main()
