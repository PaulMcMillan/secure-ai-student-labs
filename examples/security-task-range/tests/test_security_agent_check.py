import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("security_agent_check", ROOT / "security_agent_check.py")
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


class SecurityAgentCardTests(unittest.TestCase):
    def test_reference_cards_pass(self):
        report = checker.validate(ROOT / "security-agent-cards.json")
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(7, report["cards"])
        self.assertFalse(report["agents_started"])
        self.assertFalse(report["network_used"])

    def test_network_enabled_card_fails(self):
        data = json.loads((ROOT / "security-agent-cards.json").read_text(encoding="utf-8"))
        data["cards"][0]["network"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cards.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            report = checker.validate(path)
        self.assertFalse(report["valid"])

    def test_unbounded_attempts_fail(self):
        data = json.loads((ROOT / "security-agent-cards.json").read_text(encoding="utf-8"))
        data["cards"][1]["budget"]["attempts_per_case"] = 99
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cards.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            report = checker.validate(path)
        self.assertFalse(report["valid"])


if __name__ == "__main__":
    unittest.main()
