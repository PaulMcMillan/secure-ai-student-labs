"""Tests for sanitized setup evidence helpers."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from setup_check import collect_evidence, first_line, summarize_auth


class SetupCheckTests(unittest.TestCase):
    def test_chatgpt_auth_is_reduced_to_category(self) -> None:
        self.assertEqual(summarize_auth("Signed in with ChatGPT as learner@example.invalid"), "chatgpt")

    def test_api_key_auth_is_reduced_to_category(self) -> None:
        self.assertEqual(summarize_auth("Authenticated using API key"), "api-key")

    def test_version_evidence_is_bounded_to_first_line(self) -> None:
        self.assertEqual(first_line("codex 1.2.3\nextra diagnostic"), "codex 1.2.3")

    def test_identity_and_mfa_evidence_do_not_read_secrets(self) -> None:
        report = collect_evidence()
        self.assertEqual(report["human_mfa_evidence"], "external-policy-required")
        self.assertEqual(report["credential_store_category"], "not-inspected")
        self.assertFalse(report["identity_token_contents_read"])
        self.assertFalse(report["credential_contents_read"])


if __name__ == "__main__":
    unittest.main()
