import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from decision import evaluate  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ROOT / "scenarios" / name).read_text(encoding="utf-8"))


class DecisionTests(unittest.TestCase):
    def test_local_implementation_is_valid_codex_workflow(self):
        report = evaluate(load("local-implementation.json"))
        self.assertTrue(report["valid"])
        self.assertEqual(report["recommendation"], "codex")

    def test_architecture_review_is_valid_read_only_workflow(self):
        report = evaluate(load("architecture-review.json"))
        self.assertTrue(report["valid"])
        self.assertEqual(report["writer_count"], 0)

    def test_bounded_sequence_has_one_writer(self):
        report = evaluate(load("bounded-sequence.json"))
        self.assertTrue(report["valid"])
        self.assertTrue(report["single_writer"])
        self.assertEqual(report["role_count"], 2)
        self.assertTrue(report["claude_controls_current"])

    def test_unsafe_dual_edit_is_rejected(self):
        report = evaluate(load("unsafe-dual-edit.json"))
        self.assertFalse(report["valid"])
        self.assertFalse(report["single_writer"])

    def test_mutable_base_is_rejected(self):
        record = load("local-implementation.json")
        record["base_commit"] = "main"
        self.assertFalse(evaluate(record)["valid"])

    def test_duplicate_outputs_are_rejected(self):
        record = load("bounded-sequence.json")
        record["roles"][1]["output"] = record["roles"][0]["output"]
        self.assertFalse(evaluate(record)["valid"])

    def test_missing_validation_is_rejected(self):
        record = load("architecture-review.json")
        record["roles"][0]["validation"] = []
        self.assertFalse(evaluate(record)["valid"])

    def test_claude_role_requires_current_control_review(self):
        record = load("architecture-review.json")
        record["product_baseline"]["as_of"] = "2026-07-20"
        self.assertFalse(evaluate(record)["claude_controls_current"])

    def test_claude_sandbox_review_must_be_fail_closed(self):
        record = load("bounded-sequence.json")
        record["product_baseline"]["claude_code_controls"]["sandbox_fail_closed"] = False
        self.assertFalse(evaluate(record)["valid"])

    def test_report_never_claims_credentials_or_network(self):
        report = evaluate(load("bounded-sequence.json"))
        self.assertFalse(report["credentials_used"])
        self.assertFalse(report["network_used"])


if __name__ == "__main__":
    unittest.main()
