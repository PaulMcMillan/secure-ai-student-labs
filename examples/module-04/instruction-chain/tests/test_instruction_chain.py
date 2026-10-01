"""Tests for the synthetic Module 4 instruction tools."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from guidance_lint import lint  # noqa: E402
from instruction_trace import trace  # noqa: E402


class InstructionTraceTests(unittest.TestCase):
    def test_payments_chain_is_broad_to_specific(self) -> None:
        report = trace(ROOT / "scenarios" / "payments.json")
        self.assertEqual(
            report["selected_sources"],
            [
                "fixture/codex-home/AGENTS.md",
                "fixture/repo/AGENTS.md",
                "fixture/repo/services/AGENTS.md",
                "fixture/repo/services/payments/AGENTS.override.md",
            ],
        )

    def test_same_directory_override_replaces_standard_and_fallback(self) -> None:
        report = trace(ROOT / "scenarios" / "payments.json")
        sources = report["selected_sources"]
        self.assertNotIn("fixture/repo/services/payments/AGENTS.md", sources)
        self.assertNotIn("fixture/repo/services/payments/TEAM_GUIDE.md", sources)

    def test_closer_rule_wins(self) -> None:
        report = trace(ROOT / "scenarios" / "payments.json")
        self.assertEqual(
            report["effective_rules"]["test_command"],
            "python -m unittest discover -s services/payments/tests -v",
        )
        self.assertEqual(report["effective_rules"]["response_style"], "concise")

    def test_catalog_uses_configured_fallback(self) -> None:
        report = trace(ROOT / "scenarios" / "catalog.json")
        self.assertEqual(
            report["selected_sources"][-1],
            "fixture/repo/services/catalog/TEAM_GUIDE.md",
        )

    def test_normal_fixture_is_not_truncated(self) -> None:
        report = trace(ROOT / "scenarios" / "payments.json")
        self.assertFalse(report["truncated"])
        self.assertLess(report["bytes_loaded"], report["max_bytes"])

    def test_untrusted_project_skips_project_guidance(self) -> None:
        report = trace(ROOT / "scenarios" / "untrusted-payments.json")
        self.assertFalse(report["project_trusted"])
        self.assertEqual(report["selected_sources"], ["fixture/codex-home/AGENTS.md"])
        self.assertIn("untrusted", report["skipped_project_guidance_reason"])

    def test_primary_folder_governs_multi_folder_discovery(self) -> None:
        report = trace(ROOT / "scenarios" / "multi-folder.json")
        self.assertEqual(report["automatic_guidance_root"], "fixture/repo")
        self.assertEqual(report["secondary_folders"], ["fixture/secondary"])
        self.assertNotIn("fixture/secondary/AGENTS.md", report["selected_sources"])


class GuidanceLintTests(unittest.TestCase):
    def test_root_guidance_passes_course_structure(self) -> None:
        text = (ROOT / "fixture" / "repo" / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(lint(text), [])

    def test_vague_or_incomplete_guidance_is_rejected(self) -> None:
        issues = lint("# Guidance\n\n## Scope\nAlways do the right thing.\n")
        self.assertTrue(any("missing heading" in issue for issue in issues))
        self.assertTrue(any("vague instruction" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
