import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from event_check import evaluate as evaluate_events, load_events  # noqa: E402
from security_check import CHECKS, evaluate as evaluate_profile  # noqa: E402


HARDENED = json.loads((ROOT / "profiles" / "hardened.json").read_text(encoding="utf-8"))
UNSAFE = json.loads((ROOT / "profiles" / "unsafe.json").read_text(encoding="utf-8"))


class ProfileTests(unittest.TestCase):
    def test_every_section_has_at_least_ten_controls(self):
        for checks in CHECKS.values():
            self.assertGreaterEqual(len(checks), 10)

    def test_hardened_all_passes(self):
        report = evaluate_profile(HARDENED, "all")
        self.assertTrue(report["valid"])
        self.assertEqual(report["checks_run"], report["checks_passed"])

    def test_unsafe_all_fails_without_runtime_actions(self):
        report = evaluate_profile(UNSAFE, "all")
        self.assertFalse(report["valid"])
        self.assertFalse(report["credentials_read"])
        self.assertFalse(report["network_used"])
        self.assertFalse(report["server_started"])

    def test_hardened_admission_passes(self):
        self.assertTrue(evaluate_profile(HARDENED, "admission")["valid"])

    def test_unsafe_admission_fails(self):
        self.assertFalse(evaluate_profile(UNSAFE, "admission")["valid"])

    def test_hardened_identity_passes(self):
        self.assertTrue(evaluate_profile(HARDENED, "identity")["valid"])

    def test_unsafe_identity_fails(self):
        self.assertFalse(evaluate_profile(UNSAFE, "identity")["valid"])

    def test_hardened_runtime_passes(self):
        self.assertTrue(evaluate_profile(HARDENED, "runtime")["valid"])

    def test_unsafe_runtime_fails(self):
        self.assertFalse(evaluate_profile(UNSAFE, "runtime")["valid"])

    def test_hardened_tools_passes(self):
        self.assertTrue(evaluate_profile(HARDENED, "tools")["valid"])

    def test_unsafe_tools_fails(self):
        self.assertFalse(evaluate_profile(UNSAFE, "tools")["valid"])

    def test_hardened_operations_passes(self):
        self.assertTrue(evaluate_profile(HARDENED, "operations")["valid"])

    def test_unsafe_operations_fails(self):
        self.assertFalse(evaluate_profile(UNSAFE, "operations")["valid"])


class EventTests(unittest.TestCase):
    def test_normal_events_pass(self):
        report = evaluate_events(load_events(ROOT / "events" / "normal.jsonl"))
        self.assertTrue(report["valid"])
        self.assertEqual(report["alert_count"], 0)

    def test_incident_events_trigger_required_alerts(self):
        report = evaluate_events(load_events(ROOT / "events" / "incident.jsonl"))
        types = {alert["type"] for alert in report["alerts"]}
        self.assertFalse(report["valid"])
        self.assertTrue({
            "tool-inventory-drift", "write-in-read-only-profile",
            "sensitive-action-without-approval", "invalid-origin",
            "wrong-token-audience", "sensitive-output-detected",
        }.issubset(types))

    def test_sensitive_field_is_detected_without_echo(self):
        event = load_events(ROOT / "events" / "normal.jsonl")[0]
        event["authorization"] = "synthetic-value-not-a-credential"
        report = evaluate_events([event])
        self.assertFalse(report["valid"])
        self.assertFalse(report["sensitive_values_echoed"])
        self.assertNotIn("synthetic-value-not-a-credential", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
