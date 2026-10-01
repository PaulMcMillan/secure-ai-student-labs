"""Minimal offline MCP 2026-07-28 stateless STDIO teaching server."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


PROTOCOL_VERSION = "2026-07-28"
PROTOCOL_KEY = "io.modelcontextprotocol/protocolVersion"
CAPABILITIES_KEY = "io.modelcontextprotocol/clientCapabilities"
CLIENT_INFO_KEY = "io.modelcontextprotocol/clientInfo"
SERVER_INFO_KEY = "io.modelcontextprotocol/serverInfo"
SERVER_INFO = {"name": "aitrainer-stateless-policy", "version": "2.0.0"}
TRACEPARENT_RE = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")
TRACESTATE_KEY_RE = re.compile(r"^(?:[a-z0-9][_0-9a-z*/-]{0,255}|[a-z0-9][_0-9a-z*/-]{0,240}@[a-z0-9][_0-9a-z*/-]{0,13})$")
BAGGAGE_TOKEN_RE = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")

POLICIES = {
    "RET-01": {
        "policy_id": "RET-01",
        "title": "Synthetic return window",
        "text": "Training orders may be returned within 30 simulated days.",
        "classification": "public-training",
    },
    "SEC-02": {
        "policy_id": "SEC-02",
        "title": "Synthetic secret handling",
        "text": "Do not place credentials in prompts, source, fixtures, or logs.",
        "classification": "public-training",
    },
}

OUTPUT_PROPERTIES = {
    "policy_id": {"type": "string"},
    "title": {"type": "string"},
    "text": {"type": "string"},
    "classification": {"type": "string", "const": "public-training"},
}

LOOKUP_TOOL = {
    "name": "lookup_policy",
    "title": "Lookup Synthetic Training Policy",
    "description": "Read one static public-training policy by exact ID; no network or side effect.",
    "inputSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"policy_id": {"type": "string", "enum": sorted(POLICIES)}},
        "required": ["policy_id"],
        "additionalProperties": False,
    },
    "outputSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": OUTPUT_PROPERTIES,
        "required": list(OUTPUT_PROPERTIES),
        "additionalProperties": False,
    },
    "annotations": {"readOnlyHint": True, "destructiveHint": False},
}


def valid_request_id(value: Any) -> bool:
    return type(value) in {str, int}


def is_notification(message: Any) -> bool:
    return (
        isinstance(message, dict)
        and message.get("jsonrpc") == "2.0"
        and isinstance(message.get("method"), str)
        and "id" not in message
    )


def valid_tracestate(value: Any) -> bool:
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


def valid_baggage_octets(value: str) -> bool:
    return all(
        code == 0x21
        or 0x23 <= code <= 0x2B
        or 0x2D <= code <= 0x3A
        or 0x3C <= code <= 0x5B
        or 0x5D <= code <= 0x7E
        for code in map(ord, value)
    )


def valid_baggage(value: Any) -> bool:
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
        if not BAGGAGE_TOKEN_RE.fullmatch(key) or not valid_baggage_octets(item_value):
            return False
        for prop in sections[1:]:
            prop_key, separator, prop_value = prop.partition("=")
            if not BAGGAGE_TOKEN_RE.fullmatch(prop_key):
                return False
            if separator and not valid_baggage_octets(prop_value):
                return False
    return True


def response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(result)
    enriched.setdefault("resultType", "complete")
    meta = dict(enriched.get("_meta", {}))
    meta[SERVER_INFO_KEY] = SERVER_INFO
    enriched["_meta"] = meta
    return {"jsonrpc": "2.0", "id": request_id, "result": enriched}


def error(request_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        body["data"] = data
    envelope: dict[str, Any] = {"jsonrpc": "2.0", "error": body}
    if valid_request_id(request_id):
        envelope["id"] = request_id
    return envelope


def validate_envelope(message: Any) -> tuple[Any, str | None]:
    if (
        not isinstance(message, dict)
        or message.get("jsonrpc") != "2.0"
        or not isinstance(message.get("method"), str)
        or "id" not in message
        or not valid_request_id(message.get("id"))
    ):
        return None, "invalid_request"
    request_id = message.get("id")
    params = message.get("params")
    if not isinstance(params, dict) or not isinstance(params.get("_meta"), dict):
        return request_id, "missing_meta"
    meta = params["_meta"]
    requested_version = meta.get(PROTOCOL_KEY)
    if not isinstance(requested_version, str):
        return request_id, "malformed_required_meta"
    if requested_version != PROTOCOL_VERSION:
        return request_id, "unsupported_version"
    if not isinstance(meta.get(CAPABILITIES_KEY), dict):
        return request_id, "malformed_required_meta"
    client_info = meta.get(CLIENT_INFO_KEY)
    if client_info is not None and (
        not isinstance(client_info, dict)
        or not isinstance(client_info.get("name"), str)
        or not isinstance(client_info.get("version"), str)
    ):
        return request_id, "invalid_client_info"
    traceparent = meta.get("traceparent")
    if traceparent is not None:
        match = TRACEPARENT_RE.fullmatch(traceparent) if isinstance(traceparent, str) else None
        if not match or int(match.group(1), 16) == 0 or int(match.group(2), 16) == 0:
            return request_id, "invalid_trace_context"
    if "tracestate" in meta and not valid_tracestate(meta["tracestate"]):
        return request_id, "invalid_trace_context"
    if "baggage" in meta and not valid_baggage(meta["baggage"]):
        return request_id, "invalid_trace_context"
    return request_id, None


def handle_request(message: Any) -> dict[str, Any] | None:
    if is_notification(message):
        return None
    request_id, issue = validate_envelope(message)
    if issue == "invalid_request":
        return error(None, -32600, "Invalid Request")
    if issue == "unsupported_version":
        return error(
            request_id,
            -32022,
            "Unsupported protocol version",
            {"supported": [PROTOCOL_VERSION], "requested": message["params"]["_meta"][PROTOCOL_KEY]},
        )
    if issue in {"missing_meta", "malformed_required_meta", "invalid_client_info", "invalid_trace_context"}:
        return error(request_id, -32602, "Invalid per-request metadata")

    method = message.get("method")
    params = message["params"]
    if method == "server/discover":
        return response(
            request_id,
            {
                "supportedVersions": [PROTOCOL_VERSION],
                "capabilities": {"tools": {}},
                "instructions": "Use only the pinned read-only synthetic policy tool.",
                "ttlMs": 60_000,
                "cacheScope": "public",
            },
        )
    if method == "tools/list":
        return response(
            request_id,
            {"tools": [LOOKUP_TOOL], "ttlMs": 60_000, "cacheScope": "public"},
        )
    if method != "tools/call":
        return error(request_id, -32601, f"Method not found: {method}")

    if params.get("name") != LOOKUP_TOOL["name"]:
        return error(request_id, -32602, "Tool is not in the pinned inventory")
    arguments = params.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {"policy_id"}:
        return response(
            request_id,
            {"content": [{"type": "text", "text": "exactly one policy_id is required"}], "isError": True},
        )
    policy_id = arguments.get("policy_id")
    if policy_id not in POLICIES:
        return response(
            request_id,
            {"content": [{"type": "text", "text": "policy_id is outside the allowed set"}], "isError": True},
        )
    record = POLICIES[policy_id]
    return response(
        request_id,
        {
            "content": [{"type": "text", "text": json.dumps(record, sort_keys=True)}],
            "structuredContent": record,
            "isError": False,
        },
    )


def serve() -> int:
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            result = error(None, -32700, "Parse error")
        else:
            result = handle_request(message)
        if result is not None:
            print(json.dumps(result, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
