import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("security_range", ROOT / "security_range.py")
security_range = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(security_range)


class SecurityRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = security_range.load_catalog()

    def test_catalog_has_thirteen_linked_episodes(self):
        self.assertEqual(13, len(self.catalog))
        self.assertEqual("M01", next(iter(self.catalog)))
        self.assertEqual("M12.5", list(self.catalog)[-1])

    def test_every_episode_has_unique_evidence(self):
        evidence = [item["evidence_id"] for item in self.catalog.values()]
        self.assertEqual(len(evidence), len(set(evidence)))

    def test_vulnerable_profiles_are_compromised(self):
        for episode in self.catalog.values():
            with self.subTest(episode=episode["id"]):
                report = security_range.evaluate(episode, set(), "vulnerable")
                self.assertEqual("COMPROMISED", report["status"])

    def test_hardened_profiles_are_blocked(self):
        for episode in self.catalog.values():
            with self.subTest(episode=episode["id"]):
                controls = set(episode["required_controls"])
                report = security_range.evaluate(episode, controls, "hardened")
                self.assertEqual("BLOCKED", report["status"])
                self.assertEqual([], report["missing_controls"])

    def test_partial_controls_do_not_pass(self):
        for episode in self.catalog.values():
            with self.subTest(episode=episode["id"]):
                controls = set(episode["required_controls"][:-1])
                report = security_range.evaluate(episode, controls, "custom")
                self.assertEqual("COMPROMISED", report["status"])

    def test_reports_assert_no_external_behavior(self):
        episode = self.catalog["M08"]
        report = security_range.evaluate(episode, set(), "vulnerable")
        self.assertTrue(report["simulation_only"])
        self.assertFalse(report["external_actions"])
        self.assertFalse(report["network_used"])
        self.assertFalse(report["credentials_read"])
        self.assertFalse(report["commands_executed"])

    def test_every_episode_has_monitoring_and_response(self):
        for episode in self.catalog.values():
            self.assertGreaterEqual(len(episode["signals"]), 2)
            self.assertTrue(episode["first_response"])

    def test_episode_chain_is_contiguous(self):
        ids = list(self.catalog)
        for current, following in zip(ids, ids[1:]):
            self.assertEqual(following, self.catalog[current]["next_episode"])
        self.assertEqual("COURSE-CLOSE", self.catalog[ids[-1]]["next_episode"])


if __name__ == "__main__":
    unittest.main()
