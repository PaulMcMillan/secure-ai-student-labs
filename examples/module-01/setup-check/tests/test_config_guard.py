"""Tests for the teaching config guard."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config_guard import validate_config


class ConfigGuardTests(unittest.TestCase):
    def test_safe_course_baseline_is_accepted(self) -> None:
        report = validate_config(ROOT / "configs" / "safe-project.toml")
        self.assertTrue(report["valid"])
        self.assertEqual(report["problems"], [])

    def test_unsafe_course_baseline_is_rejected(self) -> None:
        report = validate_config(ROOT / "configs" / "unsafe-project.toml")
        self.assertFalse(report["valid"])
        self.assertEqual(len(report["problems"]), 2)

    def test_sensitive_key_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text('service_token = "example-not-a-real-secret"\n', encoding="utf-8")
            report = validate_config(path)
            ignored_keys = (
                'apps_mcp_product_sku = "example"\n',
                'profile = "example"\n',
                'profiles = {}\n',
                'experimental_realtime_ws_base_url = "wss://example.invalid"\n',
            )
            for content in ignored_keys:
                path.write_text(content, encoding="utf-8")
                ignored_report = validate_config(path)
                self.assertFalse(ignored_report["valid"])
                self.assertIn("project-ignored key", str(ignored_report["problems"]))
        self.assertFalse(report["valid"])
        self.assertIn("sensitive key", str(report["problems"]))

    def test_permission_profile_is_accepted_when_proxy_is_explicit(self) -> None:
        report = validate_config(ROOT / "configs" / "safe-permission-profile.toml")
        self.assertTrue(report["valid"])
        self.assertEqual(report["problems"], [])

    def test_daily_model_route_is_reported(self) -> None:
        report = validate_config(ROOT / "configs" / "safe-project.toml")
        self.assertTrue(report["valid"], report)
        self.assertEqual(
            report["model_route"],
            {"model": "gpt-5.6", "reasoning_effort": "medium"},
        )

    def test_astra_rejects_none_reasoning(self) -> None:
        report = validate_config(ROOT / "configs" / "unsafe-astra-none.toml")
        self.assertFalse(report["valid"])
        self.assertIn("gpt-6-astra requires low", str(report["problems"]))

    def test_mixed_permission_models_and_missing_proxy_are_rejected(self) -> None:
        report = validate_config(ROOT / "configs" / "unsafe-mixed-permissions.toml")
        self.assertFalse(report["valid"])
        self.assertIn("permission profiles do not compose", str(report["problems"]))
        self.assertIn("network.enabled requires", str(report["problems"]))


if __name__ == "__main__":
    unittest.main()
