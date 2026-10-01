"""Protect the baseline failure, one-line solution, and behavior checks."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lint_check import lint


class LintTeachingTests(unittest.TestCase):
    def call(self, script, path):
        return subprocess.run([sys.executable, str(ROOT / script), str(path)],
                              capture_output=True, text=True, check=False)

    def test_starter_has_exact_unused_import(self):
        result = self.call("lint_check.py", ROOT / "starter/order_summary.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("3: L001 unused import 'math'", result.stdout)

    def test_solution_has_no_lint_findings(self):
        result = self.call("lint_check.py", ROOT / "solution/order_summary.py")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Lint: PASS (0 issues)", result.stdout)

    def test_solution_only_removes_unused_import(self):
        before = (ROOT / "starter/order_summary.py").read_text(encoding="utf-8")
        after = (ROOT / "solution/order_summary.py").read_text(encoding="utf-8")
        self.assertEqual(before.replace("import math\n", ""), after)

    def test_starter_and_solution_both_pass_behavior(self):
        for state in ("starter", "solution"):
            with self.subTest(state=state):
                result = self.call("behavior_tests.py", ROOT / state / "order_summary.py")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Ran 4 tests", result.stderr)

    def test_used_import_is_retained(self):
        self.assertEqual(lint("import math\nresult = math.sqrt(4)\n"), [])

    def test_invalid_python_returns_check_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "broken.py"
            source.write_text("def broken(\n", encoding="utf-8")
            result = self.call("lint_check.py", source)
            self.assertEqual(result.returncode, 2)
            self.assertIn("CHECK_ERROR: SyntaxError", result.stdout)

    def test_behavior_regression_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "wrong.py"
            source.write_text("def summarize_orders(count):\n    return '0 orders'\n", encoding="utf-8")
            result = self.call("behavior_tests.py", source)
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAILED", result.stderr)


if __name__ == "__main__":
    unittest.main()
