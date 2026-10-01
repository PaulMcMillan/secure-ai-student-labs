"""Tests for the deterministic Module 3 context-packet evaluator."""

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packet_check import evaluate_packet  # noqa: E402


class PacketCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = json.loads((ROOT / "task.json").read_text(encoding="utf-8"))
        cls.structured = (ROOT / "packets" / "structured-context.md").read_text(encoding="utf-8")
        cls.weak = (ROOT / "packets" / "weak-context.md").read_text(encoding="utf-8")

    def evaluate(self, packet: str) -> dict[str, object]:
        return evaluate_packet(self.task, packet, ROOT)

    def test_structured_packet_is_valid_and_complete(self) -> None:
        report = self.evaluate(self.structured)
        self.assertTrue(report["valid"])
        self.assertEqual(report["score"], 10)
        self.assertEqual(report["context_precision"], 1.0)

    def test_weak_packet_is_rejected(self) -> None:
        report = self.evaluate(self.weak)
        self.assertFalse(report["valid"])
        self.assertIn("missing required sections", report["issues"][0])

    def test_missing_required_context_is_rejected(self) -> None:
        packet = self.structured.replace(
            "- `docs/pricing-policy.md` - defines the approved bulk discount threshold and rate.\n",
            "",
        )
        report = self.evaluate(packet)
        self.assertFalse(report["valid"])
        self.assertTrue(any("missing required context" in issue for issue in report["issues"]))

    def test_unknown_context_path_is_rejected(self) -> None:
        packet = self.structured.replace(
            "## Constraints",
            "- `docs/unknown.md` - appears relevant but does not exist.\n\n## Constraints",
        )
        report = self.evaluate(packet)
        self.assertFalse(report["valid"])
        self.assertTrue(any("unrecognized context paths" in issue for issue in report["issues"]))

    def test_irrelevant_context_reduces_precision_and_is_rejected(self) -> None:
        packet = self.structured.replace(
            "## Constraints",
            "- `docs/mobile-roadmap.md` - describes unrelated future work.\n\n## Constraints",
        )
        report = self.evaluate(packet)
        self.assertFalse(report["valid"])
        self.assertLess(report["context_precision"], 1.0)

    def test_secret_like_content_is_rejected_without_echo(self) -> None:
        marker = "example-sensitive-value"
        packet = self.structured + f"\napi_key = {marker}\n"
        report = self.evaluate(packet)
        self.assertFalse(report["valid"])
        self.assertFalse(report["secret_values_echoed"])
        self.assertNotIn(marker, json.dumps(report))

    def test_wrong_validation_command_is_rejected(self) -> None:
        packet = self.structured.replace(
            "python -m unittest discover -s tests -v",
            "run the tests",
        )
        report = self.evaluate(packet)
        self.assertFalse(report["valid"])
        self.assertTrue(any("exact validation command" in issue for issue in report["issues"]))


if __name__ == "__main__":
    unittest.main()
