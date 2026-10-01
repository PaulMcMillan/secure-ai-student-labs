from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cost_trace import TraceError, evaluate_trace


class CostTraceTests(unittest.TestCase):
    def fixture(self):
        return {
            "catalog_accessed": "2026-09-18",
            "comparison_contract": {
                "prompt_version": "review-v1",
                "evaluation_set": "five-cases-v1",
                "authority_profile": "read-only-review-v1",
            },
            "reviewer_hourly_usd": 60,
            "candidates": [
                {"model": "a", "role": "balanced", "reasoning_effort": "medium", "rates_per_million": {"input": 1, "cached_input": 0.1, "output": 5}, "runs": [
                    {"accepted": False, "input_tokens": 1000, "output_tokens": 100, "reviewer_minutes": 2},
                    {"accepted": True, "input_tokens": 1000, "output_tokens": 100, "reviewer_minutes": 1}
                ]},
                {"model": "b", "role": "quality", "reasoning_effort": "medium", "rates_per_million": {"input": 2, "cached_input": 0.2, "output": 10}, "runs": [
                    {"accepted": True, "input_tokens": 1000, "output_tokens": 100, "reviewer_minutes": 1}
                ]}
            ]
        }

    def test_rejected_runs_contribute_to_cost_per_accepted_task(self):
        report = evaluate_trace(self.fixture())
        row = next(item for item in report["candidates"] if item["model"] == "a")
        self.assertEqual(2, row["runs"])
        self.assertEqual(1, row["accepted"])
        self.assertGreater(row["cost_per_accepted_task_usd"], row["human_review_cost_usd"] / row["accepted"])

    def test_winner_uses_total_observed_cost_not_unit_price(self):
        report = evaluate_trace(self.fixture())
        self.assertEqual("b", report["winner_on_observed_cost_per_accepted_task"])

    def test_missing_access_date_fails(self):
        data = self.fixture()
        data.pop("catalog_accessed")
        with self.assertRaises(TraceError):
            evaluate_trace(data)

    def test_comparison_contract_is_required(self):
        data = self.fixture()
        data.pop("comparison_contract")
        with self.assertRaises(TraceError):
            evaluate_trace(data)

    def test_candidate_without_accepted_run_fails(self):
        data = self.fixture()
        data["candidates"][0]["runs"] = [{"accepted": False}]
        with self.assertRaises(TraceError):
            evaluate_trace(data)


if __name__ == "__main__":
    unittest.main()
