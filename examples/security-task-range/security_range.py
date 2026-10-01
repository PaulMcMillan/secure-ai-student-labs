"""Offline policy simulator for the linked AI security course activities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "scenarios.json"


def load_catalog() -> dict[str, dict]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    catalog = {item["id"]: item for item in episodes}
    if len(catalog) != 13:
        raise ValueError("scenario catalog must contain 13 unique episodes")
    return catalog


def evaluate(episode: dict, controls: set[str], profile: str) -> dict:
    missing = [name for name in episode["required_controls"] if name not in controls]
    status = "BLOCKED" if not missing else "COMPROMISED"
    blocked_at = episode["attack_steps"][0]["id"] if status == "BLOCKED" else None
    return {
        "incident_id": "NB-AI-2026-001",
        "episode": episode["id"],
        "evidence_id": episode["evidence_id"],
        "simulation_only": True,
        "profile": profile,
        "status": status,
        "attack_objective": episode["attack_objective"],
        "attack_path": [step["id"] for step in episode["attack_steps"]],
        "controls_present": sorted(controls),
        "missing_controls": missing,
        "blocked_at": blocked_at,
        "signals": episode["signals"],
        "first_response": episode["first_response"],
        "next_episode": episode["next_episode"],
        "external_actions": False,
        "network_used": False,
        "credentials_read": False,
        "commands_executed": False,
    }


def controls_for(episode: dict, profile: str, custom: str | None) -> set[str]:
    if custom is not None:
        return {item.strip() for item in custom.split(",") if item.strip()}
    if profile == "hardened":
        return set(episode["required_controls"])
    return set()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list linked security episodes")
    sub.add_parser("self-test", help="verify catalog and safety invariants")
    run = sub.add_parser("run", help="evaluate one synthetic episode")
    run.add_argument("episode")
    run.add_argument("--profile", choices=["vulnerable", "hardened"], default="vulnerable")
    run.add_argument("--controls", help="comma-separated custom controls")
    summary = sub.add_parser("summary", help="evaluate all episodes")
    summary.add_argument("--profile", choices=["vulnerable", "hardened"], default="hardened")
    args = parser.parse_args(argv)
    catalog = load_catalog()

    if args.command == "list":
        for episode in catalog.values():
            print(f"{episode['id']}: {episode['title']} -> {episode['evidence_id']}")
        return 0

    if args.command == "self-test":
        expected = [f"M{i:02d}" for i in range(1, 13)] + ["M12.5"]
        if list(catalog) != expected:
            raise ValueError(f"unexpected episode order: {list(catalog)}")
        if any(not item["required_controls"] for item in catalog.values()):
            raise ValueError("every episode requires at least one control")
        print(json.dumps({"valid": True, "episodes": 13, "simulation_only": True}))
        return 0

    if args.command == "run":
        episode_id = args.episode.upper()
        if episode_id not in catalog:
            parser.error(f"unknown episode {args.episode}")
        episode = catalog[episode_id]
        controls = controls_for(episode, args.profile, args.controls)
        print(json.dumps(evaluate(episode, controls, args.profile), indent=2))
        return 0


    reports = []
    for episode in catalog.values():
        controls = controls_for(episode, args.profile, None)
        reports.append(evaluate(episode, controls, args.profile))
    compromised = sum(item["status"] == "COMPROMISED" for item in reports)
    print(json.dumps({
        "incident_id": "NB-AI-2026-001",
        "profile": args.profile,
        "episodes": len(reports),
        "blocked": len(reports) - compromised,
        "compromised": compromised,
        "simulation_only": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
