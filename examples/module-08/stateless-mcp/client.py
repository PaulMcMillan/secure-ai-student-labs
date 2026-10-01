"""Drive three independent MCP 2026-07-28 requests over STDIO."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL_VERSION = "2026-07-28"


def meta() -> dict[str, Any]:
    return {
        "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
        "io.modelcontextprotocol/clientCapabilities": {},
        "io.modelcontextprotocol/clientInfo": {"name": "aitrainer-client", "version": "2.0.0"},
    }


def messages() -> list[dict[str, Any]]:
    return [
        {"jsonrpc": "2.0", "method": "notifications/unknown", "params": {"_meta": meta()}},
        {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": meta()}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": meta()}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "lookup_policy", "arguments": {"policy_id": "SEC-02"}, "_meta": meta()},
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
    return [json.loads(line) for line in completed.stdout.splitlines() if line], completed.stderr


def summarize(responses: list[dict[str, Any]], stderr: str) -> dict[str, Any]:
    if len(responses) != 3:
        raise ValueError(f"expected 3 responses, found {len(responses)}")
    discover, tool_list, tool_result = (item["result"] for item in responses)
    return {
        "protocol_version": discover["supportedVersions"][0],
        "response_count": len(responses),
        "result_types": [item["result"]["resultType"] for item in responses],
        "tool_names": [tool["name"] for tool in tool_list["tools"]],
        "cache": {"ttlMs": tool_list["ttlMs"], "cacheScope": tool_list["cacheScope"]},
        "result_is_error": tool_result["isError"],
        "result_classification": tool_result["structuredContent"]["classification"],
        "session_used": False,
        "credentials_used": False,
        "network_used": False,
        "stderr_empty": stderr == "",
    }


def main() -> int:
    responses, stderr = run_exchange()
    print(json.dumps(summarize(responses, stderr), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
