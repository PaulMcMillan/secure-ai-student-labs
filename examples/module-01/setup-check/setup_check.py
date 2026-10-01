"""Collect sanitized, read-only Codex setup evidence for Module 1."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence


def run(command: Sequence[str]) -> tuple[int, str]:
    """Run a short diagnostic and return its code and combined text."""
    try:
        result = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return result.returncode, (result.stdout + "\n" + result.stderr).strip()


def summarize_auth(output: str) -> str:
    """Reduce login output to a non-secret category."""
    lowered = output.lower()
    if "not logged" in lowered or "not authenticated" in lowered:
        return "not-authenticated"
    if "chatgpt" in lowered:
        return "chatgpt"
    if "api key" in lowered or "api-key" in lowered:
        return "api-key"
    if output.strip():
        return "configured-or-unknown"
    return "unavailable"


def first_line(output: str) -> str:
    """Return one trimmed, bounded line for version evidence."""
    return output.splitlines()[0][:120] if output.splitlines() else "unavailable"


def collect_evidence() -> dict[str, object]:
    """Collect facts without reading credential or configuration contents."""
    git_code, git_root_output = run(["git", "rev-parse", "--show-toplevel"])
    git_root = Path(git_root_output.splitlines()[0]) if git_code == 0 and git_root_output else None

    branch_code, branch_output = run(["git", "branch", "--show-current"])
    status_code, status_output = run(["git", "status", "--porcelain"])

    codex_available = shutil.which("codex") is not None
    version_code, version_output = run(["codex", "--version"]) if codex_available else (127, "")
    auth_code, auth_output = run(["codex", "login", "status"]) if codex_available else (127, "")

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    project_config = git_root / ".codex" / "config.toml" if git_root else None
    federation_rule_present = bool(os.environ.get("OPENAI_FEDERATION_RULE_ID"))
    identity_token_path = os.environ.get("OPENAI_IDENTITY_TOKEN_FILE")

    return {
        "python_version": ".".join(str(item) for item in sys.version_info[:3]),
        "platform": sys.platform,
        "current_directory_name": Path.cwd().name,
        "git_available": git_code == 0,
        "git_root_name": git_root.name if git_root else "unavailable",
        "branch": first_line(branch_output) if branch_code == 0 else "unavailable",
        "worktree_clean": status_code == 0 and not status_output,
        "codex_available": codex_available and version_code == 0,
        "codex_version": first_line(version_output) if version_code == 0 else "unavailable",
        "auth_category": summarize_auth(auth_output) if auth_code in {0, 1} else "unavailable",
        "human_mfa_evidence": "external-policy-required",
        "credential_store_category": "not-inspected",
        "wif_requested": federation_rule_present and bool(identity_token_path),
        "identity_token_file_present": bool(identity_token_path and Path(identity_token_path).is_file()),
        "identity_token_contents_read": False,
        "user_config_present": (codex_home / "config.toml").is_file(),
        "project_config_present": bool(project_config and project_config.is_file()),
        "credential_contents_read": False,
    }


if __name__ == "__main__":
    print(json.dumps(collect_evidence(), indent=2, sort_keys=True))
