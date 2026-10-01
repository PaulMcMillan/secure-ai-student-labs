"""Run a synthetic authenticated query through the read-only RAG MCP bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
RAG_ROOT = ROOT.parents[1] / "rag-reference"
AUTH_CONTEXT = {
    "principal": "learner-alpha",
    "tenant": "northstar",
    "roles": ["employee"],
    "clearances": ["internal"],
    "issuer": "https://idp.northstar.example",
    "audience": "rag-mcp-training",
}


def request() -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_knowledge",
            "arguments": {"question": "What is the travel approval threshold?", "top_k": 3},
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                "io.modelcontextprotocol/clientCapabilities": {},
                "io.modelcontextprotocol/clientInfo": {"name": "aitrainer-bridge-client", "version": "1.0.0"},
                "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
            },
        },
    }


def main() -> int:
    index = RAG_ROOT / "build" / "index.json"
    if not index.exists():
        print("Build examples/rag-reference/build/index.json first.", file=sys.stderr)
        return 2
    env = dict(os.environ)
    env.update({
        "AITRAINER_AUTH_CONTEXT": json.dumps(AUTH_CONTEXT),
        "AITRAINER_RAG_INDEX": str(index),
    })
    notification = {"jsonrpc": "2.0", "method": "notifications/unknown", "params": {"_meta": request()["params"]["_meta"]}}
    completed = subprocess.run(
        [sys.executable, str(ROOT / "server.py")],
        input=json.dumps(notification) + "\n" + json.dumps(request()) + "\n",
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        env=env,
    )
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)
        return completed.returncode
    result = json.loads(completed.stdout)["result"]
    summary = {
        "result_type": result["resultType"],
        "status": result["structuredContent"]["status"],
        "answer": result["structuredContent"]["answer"],
        "citations": result["structuredContent"]["citations"],
        "policy_decision": result["structuredContent"]["policy_decision"],
        "traceparent": result["_meta"]["traceparent"],
        "tool": "search_knowledge",
        "side_effect": "none",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
