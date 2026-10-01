"""Run a deterministic MCP STDIO exchange against the training server."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL_VERSION = "2025-11-25"


def messages() -> list[dict[str, Any]]:
    return [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "aitrainer-client", "version": "1.0.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "lookup_policy", "arguments": {"policy_id": "SEC-02"}},
        },
    ]


def run_exchange() -> tuple[list[dict[str, Any]], str]:
    wire_input = "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in messages())
    completed = subprocess.run(
        [sys.executable, str(ROOT / "server.py")],
        input=wire_input,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"server exited {completed.returncode}: {completed.stderr}")
    responses = [json.loads(line) for line in completed.stdout.splitlines() if line]
    return responses, completed.stderr


def summarize(responses: list[dict[str, Any]], stderr: str) -> dict[str, Any]:
    if len(responses) != 3:
        raise ValueError(f"expected 3 responses, found {len(responses)}")
    initialize, tool_list, tool_result = responses
    tools = tool_list.get("result", {}).get("tools", [])
    structured = tool_result.get("result", {}).get("structuredContent", {})
    return {
        "protocol_version": initialize.get("result", {}).get("protocolVersion"),
        "response_count": len(responses),
        "tool_names": [tool.get("name") for tool in tools],
        "result_is_error": tool_result.get("result", {}).get("isError"),
        "result_classification": structured.get("classification"),
        "stderr_empty": stderr == "",
        "credentials_used": False,
        "network_used": False,
    }


def main() -> int:
    responses, stderr = run_exchange()
    print(json.dumps(summarize(responses, stderr), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
