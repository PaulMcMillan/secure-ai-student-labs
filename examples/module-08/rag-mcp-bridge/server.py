"""Read-only MCP 2026-07-28 bridge for the shared offline RAG reference."""

from __future__ import annotations

import importlib.util
import json
import os
import re
from datetime import date
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
EXAMPLES_ROOT = ROOT.parents[1]
RAG_ROOT = EXAMPLES_ROOT / "rag-reference"
SPEC = importlib.util.spec_from_file_location("aitrainer_rag", RAG_ROOT / "rag.py")
if not SPEC or not SPEC.loader:
    raise RuntimeError("cannot load shared RAG reference")
rag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rag)

PROTOCOL_VERSION = "2026-07-28"
PROTOCOL_KEY = "io.modelcontextprotocol/protocolVersion"
CAPABILITIES_KEY = "io.modelcontextprotocol/clientCapabilities"
CLIENT_INFO_KEY = "io.modelcontextprotocol/clientInfo"
SERVER_INFO_KEY = "io.modelcontextprotocol/serverInfo"
SERVER_INFO = {"name": "aitrainer-rag-bridge", "version": "1.0.0"}
EXPECTED_ISSUER = "https://idp.northstar.example"
EXPECTED_AUDIENCE = "rag-mcp-training"
TRACEPARENT_RE = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")
TRACESTATE_KEY_RE = re.compile(r"^(?:[a-z0-9][_0-9a-z*/-]{0,255}|[a-z0-9][_0-9a-z*/-]{0,240}@[a-z0-9][_0-9a-z*/-]{0,13})$")
BAGGAGE_TOKEN_RE = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
AUTHORIZATION_ERROR = -30001
SIDE_EFFECT_APPROVAL_ERROR = -30003

SEARCH_TOOL = {
    "name": "search_knowledge",
    "title": "Search Authorized Training Knowledge",
    "description": "Search only sources authorized by verified runtime claims; returns a cited extract or abstention.",
    "inputSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "question": {"type": "string", "minLength": 1, "maxLength": 500},
            "top_k": {"type": "integer", "minimum": 1, "maximum": rag.MAX_RESULTS},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False},
}
PINNED_TOOLS = {SEARCH_TOOL["name"]: {"definition": SEARCH_TOOL, "side_effect": "none"}}


def valid_request_id(value: Any) -> bool:
    return type(value) in {str, int}


def is_notification(message: Any) -> bool:
    return (
        isinstance(message, dict)
        and message.get("jsonrpc") == "2.0"
        and isinstance(message.get("method"), str)
        and "id" not in message
    )


def error(request_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    detail: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        detail["data"] = data
    envelope: dict[str, Any] = {"jsonrpc": "2.0", "error": detail}
    if valid_request_id(request_id):
        envelope["id"] = request_id
    return envelope


def response(request_id: Any, result: dict[str, Any], traceparent: str | None = None) -> dict[str, Any]:
    enriched = dict(result)
    enriched.setdefault("resultType", "complete")
    meta = dict(enriched.get("_meta", {}))
    meta[SERVER_INFO_KEY] = SERVER_INFO
    if traceparent:
        meta["traceparent"] = traceparent
    enriched["_meta"] = meta
    return {"jsonrpc": "2.0", "id": request_id, "result": enriched}


def _valid_tracestate(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 512:
        return False
    members = value.split(",")
    if len(members) > 32:
        return False
    keys: set[str] = set()
    for raw_member in members:
        member = raw_member.strip(" ")
        if "=" not in member:
            return False
        key, item_value = member.split("=", 1)
        if not TRACESTATE_KEY_RE.fullmatch(key) or key in keys or not item_value or len(item_value) > 256:
            return False
        if item_value != item_value.strip(" ") or any(not (0x20 <= ord(char) <= 0x7E) or char in {",", "="} for char in item_value):
            return False
        keys.add(key)
    return True


def _valid_baggage_octets(value: str) -> bool:
    return all(
        code == 0x21
        or 0x23 <= code <= 0x2B
        or 0x2D <= code <= 0x3A
        or 0x3C <= code <= 0x5B
        or 0x5D <= code <= 0x7E
        for code in map(ord, value)
    )


def _valid_baggage(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 8192:
        return False
    members = value.split(",")
    if len(members) > 64:
        return False
    for raw_member in members:
        sections = [section.strip(" ") for section in raw_member.split(";")]
        if not sections[0] or "=" not in sections[0]:
            return False
        key, item_value = sections[0].split("=", 1)
        if not BAGGAGE_TOKEN_RE.fullmatch(key) or not _valid_baggage_octets(item_value):
            return False
        for prop in sections[1:]:
            prop_key, separator, prop_value = prop.partition("=")
            if not BAGGAGE_TOKEN_RE.fullmatch(prop_key):
                return False
            if separator and not _valid_baggage_octets(prop_value):
                return False
    return True


def _validate_request(message: Any) -> tuple[Any, dict[str, Any] | None, dict[str, Any] | None]:
    if (
        not isinstance(message, dict)
        or message.get("jsonrpc") != "2.0"
        or not isinstance(message.get("method"), str)
        or "id" not in message
        or not valid_request_id(message.get("id"))
    ):
        return None, None, error(None, -32600, "Invalid Request")
    request_id = message.get("id")
    params = message.get("params")
    if not isinstance(params, dict) or not isinstance(params.get("_meta"), dict):
        return request_id, None, error(request_id, -32602, "Invalid per-request metadata")
    meta = params["_meta"]
    requested_version = meta.get(PROTOCOL_KEY)
    if not isinstance(requested_version, str):
        return request_id, None, error(request_id, -32602, "Invalid per-request metadata")
    if requested_version != PROTOCOL_VERSION:
        return request_id, None, error(
            request_id,
            -32022,
            "Unsupported protocol version",
            {"supported": [PROTOCOL_VERSION], "requested": requested_version},
        )
    if not isinstance(meta.get(CAPABILITIES_KEY), dict):
        return request_id, None, error(request_id, -32602, "Invalid per-request metadata")
    client_info = meta.get(CLIENT_INFO_KEY)
    if client_info is not None and (
        not isinstance(client_info, dict)
        or not isinstance(client_info.get("name"), str)
        or not isinstance(client_info.get("version"), str)
    ):
        return request_id, None, error(request_id, -32602, "Invalid clientInfo")
    traceparent = meta.get("traceparent")
    if traceparent is not None:
        match = TRACEPARENT_RE.fullmatch(traceparent) if isinstance(traceparent, str) else None
        if not match or int(match.group(1), 16) == 0 or int(match.group(2), 16) == 0:
            return request_id, None, error(request_id, -32602, "Invalid traceparent")
    if "tracestate" in meta and not _valid_tracestate(meta["tracestate"]):
        return request_id, None, error(request_id, -32602, "Invalid tracestate")
    if "baggage" in meta and not _valid_baggage(meta["baggage"]):
        return request_id, None, error(request_id, -32602, "Invalid baggage")
    return request_id, params, None


def _validate_auth(auth: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(auth, dict):
        return None, "verified auth context is required"
    required_lists = ("roles", "clearances")
    required_strings = ("principal", "tenant", "issuer", "audience")
    if any(not isinstance(auth.get(field), str) or not auth[field] for field in required_strings):
        return None, "verified auth context is incomplete"
    if any(not isinstance(auth.get(field), list) or not auth[field] or not all(isinstance(value, str) for value in auth[field]) for field in required_lists):
        return None, "verified auth attributes are incomplete"
    if auth["issuer"] != EXPECTED_ISSUER or auth["audience"] != EXPECTED_AUDIENCE:
        return None, "issuer or token audience rejected"
    return auth, None


def handle_request(
    message: Any,
    auth_context: Any,
    index: dict[str, Any],
    operator_event_out: dict[str, Any] | None = None,
    *,
    trusted_as_of: date = rag.DEFAULT_AS_OF,
) -> dict[str, Any] | None:
    if is_notification(message):
        return None
    request_id, params, invalid = _validate_request(message)
    if invalid:
        return invalid
    assert params is not None
    traceparent = params["_meta"].get("traceparent")
    method = message.get("method")
    if method == "server/discover":
        return response(
            request_id,
            {"supportedVersions": [PROTOCOL_VERSION], "capabilities": {"tools": {}}, "instructions": "Only search_knowledge is admitted.", "ttlMs": 0, "cacheScope": "private"},
            traceparent,
        )
    auth, auth_issue = _validate_auth(auth_context)
    if auth_issue:
        return error(request_id, AUTHORIZATION_ERROR, auth_issue)
    if method == "tools/list":
        return response(request_id, {"tools": [SEARCH_TOOL], "ttlMs": 0, "cacheScope": "private"}, traceparent)
    if method != "tools/call":
        return error(request_id, -32601, f"Method not found: {method}")
    name = params.get("name")
    if name not in PINNED_TOOLS:
        return error(request_id, -32602, "Tool is not in the pinned inventory")
    if PINNED_TOOLS[name]["side_effect"] != "none":
        return error(request_id, SIDE_EFFECT_APPROVAL_ERROR, "Side-effect approval is required")
    arguments = params.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) - {"question", "top_k"}:
        return error(request_id, -32602, "Invalid search_knowledge arguments")
    question = arguments.get("question")
    if not isinstance(question, str) or not question.strip() or len(question) > 500:
        return error(request_id, -32602, "question must contain 1 to 500 characters")
    top_k = arguments.get("top_k", 3)
    if type(top_k) is not int or not 1 <= top_k <= rag.MAX_RESULTS:
        return error(request_id, -32602, f"top_k must be an integer from 1 through {rag.MAX_RESULTS}")
    result = rag.answer_query(
        index,
        principal=auth["principal"],
        tenant=auth["tenant"],
        roles=auth["roles"],
        clearances=auth["clearances"],
        question=question,
        top_k=top_k,
        as_of=trusted_as_of,
        operator_event_out=operator_event_out,
    )
    text = result["answer"] if result["status"] == "answered" else f"{result['status']}: {result['reason']}"
    return response(
        request_id,
        {"content": [{"type": "text", "text": text}], "structuredContent": result, "isError": result["status"] == "blocked"},
        traceparent,
    )


def serve() -> int:
    index_path = Path(os.environ.get("AITRAINER_RAG_INDEX", RAG_ROOT / "build" / "index.json"))
    try:
        index = rag.load_index(index_path)
        auth = json.loads(os.environ.get("AITRAINER_AUTH_CONTEXT", "null"))
    except (OSError, ValueError, rag.RagError) as exc:
        print(f"bridge startup failed: {exc}", file=sys.stderr)
        return 2
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            value = error(None, -32700, "Parse error")
        else:
            operator_event: dict[str, Any] = {}
            value = handle_request(message, auth, index, operator_event)
            if operator_event:
                # The tool remains externally read-only. The host collects this
                # redacted stderr event into its protected logging plane.
                print("AITRAINER_OPERATOR_EVENT " + json.dumps(operator_event, separators=(",", ":")), file=sys.stderr, flush=True)
        if value is not None:
            print(json.dumps(value, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
