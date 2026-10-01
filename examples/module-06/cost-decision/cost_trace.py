"""Calculate cost per accepted task from a source-dated evaluation trace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class TraceError(ValueError):
    pass


def evaluate_trace(data: dict[str, Any]) -> dict[str, Any]:
    accessed = data.get("catalog_accessed")
    comparison = data.get("comparison_contract")
    candidates = data.get("candidates")
    if not isinstance(accessed, str) or not accessed:
        raise TraceError("catalog_accessed is required")
    if not isinstance(candidates, list) or not candidates:
        raise TraceError("candidates must be a non-empty list")
    if not isinstance(comparison, dict):
        raise TraceError("comparison_contract is required")
    for field in ("prompt_version", "evaluation_set", "authority_profile"):
        if not isinstance(comparison.get(field), str) or not comparison[field].strip():
            raise TraceError(f"comparison_contract.{field} is required")
    reviewer_hourly = float(data.get("reviewer_hourly_usd", 0))
    rows = []
    for candidate in candidates:
        rates = candidate.get("rates_per_million", {})
        runs = candidate.get("runs", [])
        effort = candidate.get("reasoning_effort")
        if not isinstance(effort, str) or not effort.strip():
            raise TraceError(f"{candidate.get('model', 'candidate')} reasoning_effort is required")
        for field in ("input", "cached_input", "output"):
            if not isinstance(rates.get(field), (int, float)) or rates[field] < 0:
                raise TraceError(f"{candidate.get('model', 'candidate')} has invalid {field} rate")
        if not isinstance(runs, list) or not runs:
            raise TraceError(f"{candidate.get('model', 'candidate')} runs must be non-empty")
        api_cost = human_cost = tool_cost = 0.0
        accepted = 0
        for run in runs:
            accepted += int(run.get("accepted") is True)
            api_cost += (
                float(run.get("input_tokens", 0)) * rates["input"]
                + float(run.get("cached_input_tokens", 0)) * rates["cached_input"]
                + float(run.get("output_tokens", 0)) * rates["output"]
            ) / 1_000_000
            tool_cost += float(run.get("tool_cost_usd", 0))
            human_cost += float(run.get("reviewer_minutes", 0)) * reviewer_hourly / 60
        if accepted == 0:
            raise TraceError(f"{candidate.get('model', 'candidate')} has no accepted run")
        total = api_cost + tool_cost + human_cost
        rows.append({
            "model": candidate["model"],
            "role": candidate["role"],
            "reasoning_effort": effort,
            "runs": len(runs),
            "accepted": accepted,
            "acceptance_rate": round(accepted / len(runs), 4),
            "api_cost_usd": round(api_cost, 6),
            "tool_cost_usd": round(tool_cost, 6),
            "human_review_cost_usd": round(human_cost, 6),
            "total_observed_cost_usd": round(total, 6),
            "cost_per_accepted_task_usd": round(total / accepted, 6),
        })
    rows.sort(key=lambda row: (row["cost_per_accepted_task_usd"], -row["acceptance_rate"], row["model"]))
    return {
        "valid": True,
        "catalog_accessed": accessed,
        "scenario": data.get("scenario"),
        "comparison_contract": comparison,
        "winner_on_observed_cost_per_accepted_task": rows[0]["model"],
        "candidates": rows,
        "warning": "A small synthetic trace is not a production routing policy; rerun representative evals and refresh catalog facts.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate_trace(json.loads(args.trace.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, TraceError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
