"""Trace a synthetic Codex project-guidance chain, trust gate, and primary root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


RULE = re.compile(r"(?m)^-\s+([a-z][a-z0-9_]*)\s*:\s*(.+?)\s*$")


def first_nonempty(directory: Path, names: list[str]) -> Path | None:
    for name in names:
        candidate = directory / name
        if candidate.is_file() and candidate.read_text(encoding="utf-8").strip():
            return candidate
    return None


def trace(scenario_path: Path) -> dict[str, Any]:
    scenario_path = scenario_path.resolve()
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    base = scenario_path.parent.parent
    home = (base / scenario["codex_home"]).resolve()
    root = (base / scenario.get("primary_project_root", scenario["project_root"])).resolve()
    cwd = (base / scenario["cwd"]).resolve()
    cwd.relative_to(root)
    project_trusted = bool(scenario.get("project_trusted", True))
    workspace_folders = [
        (base / item).resolve()
        for item in scenario.get("workspace_folders", [scenario.get("primary_project_root", scenario["project_root"])])
    ]
    secondary_folders = [path for path in workspace_folders if path != root]

    selected: list[Path] = []
    global_file = first_nonempty(home, ["AGENTS.override.md", "AGENTS.md"])
    if global_file:
        selected.append(global_file)

    if project_trusted:
        names = ["AGENTS.override.md", "AGENTS.md", *scenario.get("fallback_filenames", [])]
        relative = cwd.relative_to(root)
        directories = [root]
        current = root
        for part in relative.parts:
            current = current / part
            directories.append(current)
        for directory in directories:
            chosen = first_nonempty(directory, names)
            if chosen:
                selected.append(chosen)

    byte_limit = int(scenario["max_bytes"])
    included: list[Path] = []
    total = 0
    truncated = False
    for path in selected:
        size = len(path.read_bytes())
        if total + size > byte_limit:
            truncated = True
            break
        included.append(path)
        total += size

    effective: dict[str, str] = {}
    for path in included:
        effective.update(dict(RULE.findall(path.read_text(encoding="utf-8"))))

    return {
        "project_trusted": project_trusted,
        "automatic_guidance_root": str(root.relative_to(base)).replace("\\", "/"),
        "secondary_folders": [
            str(path.relative_to(base)).replace("\\", "/") for path in secondary_folders
        ],
        "skipped_project_guidance_reason": None
        if project_trusted
        else "project is untrusted; project-level guidance is not loaded",
        "selected_sources": [str(path.relative_to(base)).replace("\\", "/") for path in included],
        "effective_rules": effective,
        "bytes_loaded": total,
        "max_bytes": byte_limit,
        "truncated": truncated,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    args = parser.parse_args()
    print(json.dumps(trace(args.scenario), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
