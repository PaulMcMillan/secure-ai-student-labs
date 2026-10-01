"""Deterministically evaluate a synthetic engineering context packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


REQUIRED_SECTIONS = (
    "goal",
    "context",
    "constraints",
    "deliverable",
    "validation",
    "stopping condition",
)
SECRET_PATTERN = re.compile(
    r"(?i)(?:api[_ -]?key|password|access[_ -]?token|secret)\s*[:=]\s*\S+|\bsk-[a-z0-9_-]{8,}"
)
PATH_PATTERN = re.compile(r"`([^`]+)`")
RATIONALE_PATTERN = re.compile(r"(?m)^\s*-\s*`([^`]+)`\s*(?:-|:|—)\s*\S+")


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def parse_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    active: str | None = None
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            active = normalize(heading.group(1))
            sections.setdefault(active, [])
        elif active is not None:
            sections[active].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def all_terms(text: str, terms: list[str]) -> bool:
    normalized = normalize(text)
    return all(normalize(term) in normalized for term in terms)


def evaluate_packet(task: dict[str, Any], packet: str, base_dir: Path) -> dict[str, Any]:
    sections = parse_sections(packet)
    issues: list[str] = []
    fatal = False
    score = 0

    missing_sections = [name for name in REQUIRED_SECTIONS if name not in sections]
    if missing_sections:
        issues.append("missing required sections: " + ", ".join(missing_sections))
        fatal = True

    if SECRET_PATTERN.search(packet):
        issues.append("secret-like assignment or token found")
        fatal = True

    goal = sections.get("goal", "")
    if all_terms(goal, task["required_goal_terms"]):
        score += 1
    else:
        issues.append("goal does not state the required behavior")

    context_text = sections.get("context", "")
    selected = sorted(set(PATH_PATTERN.findall(context_text)))
    required = set(task["required_context"])
    useful = set(task.get("useful_context", []))
    irrelevant = set(task.get("irrelevant_context", []))
    selected_set = set(selected)
    missing_context = sorted(required - selected_set)
    if not missing_context:
        score += 2
    else:
        issues.append("missing required context: " + ", ".join(missing_context))
        fatal = True

    relevant_selected = selected_set & (required | useful)
    precision = len(relevant_selected) / len(selected_set) if selected_set else 0.0
    unknown = selected_set - required - useful - irrelevant
    selected_irrelevant = selected_set & irrelevant
    if selected_set and not unknown and not selected_irrelevant:
        score += 1
    else:
        if unknown:
            issues.append("unrecognized context paths: " + ", ".join(sorted(unknown)))
        if selected_irrelevant:
            issues.append("declared irrelevant context selected: " + ", ".join(sorted(selected_irrelevant)))
        fatal = True

    repo_root = (base_dir / task["repository_root"]).resolve()
    nonexistent = sorted(path for path in selected if not (repo_root / path).is_file())
    rationalized = set(RATIONALE_PATTERN.findall(context_text))
    missing_rationales = sorted(selected_set - rationalized)
    if selected and not nonexistent and not missing_rationales:
        score += 1
    else:
        if nonexistent:
            issues.append("context paths do not exist: " + ", ".join(nonexistent))
        if missing_rationales:
            issues.append("context paths lack rationales: " + ", ".join(missing_rationales))
        fatal = True

    if all_terms(sections.get("constraints", ""), task["required_constraint_terms"]):
        score += 1
    else:
        issues.append("material constraints are incomplete")

    if all_terms(sections.get("deliverable", ""), task["required_deliverable_terms"]):
        score += 1
    else:
        issues.append("deliverable is incomplete")

    if task["validation_command"] in sections.get("validation", ""):
        score += 1
    else:
        issues.append("exact validation command is missing")
        fatal = True

    if all_terms(sections.get("stopping condition", ""), task["required_stop_terms"]):
        score += 1
    else:
        issues.append("stopping condition must say when to stop and ask")

    if all_terms(sections.get("constraints", ""), task["required_privacy_terms"]):
        score += 1
    else:
        issues.append("privacy boundary is incomplete")

    return {
        "task_id": task["task_id"],
        "score": score,
        "max_score": 10,
        "valid": score >= 8 and not fatal,
        "context_precision": round(precision, 2),
        "selected_context": selected,
        "issues": issues,
        "secret_values_echoed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()

    task = json.loads(args.task.read_text(encoding="utf-8"))
    packet = args.packet.read_text(encoding="utf-8")
    report = evaluate_packet(task, packet, args.task.parent)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
