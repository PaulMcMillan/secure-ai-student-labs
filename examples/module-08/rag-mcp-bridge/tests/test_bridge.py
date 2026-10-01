import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server import EXPECTED_AUDIENCE, EXPECTED_ISSUER, PINNED_TOOLS, SEARCH_TOOL, handle_request, rag  # noqa: E402

INDEX = rag.build_index(ROOT.parents[1] / "rag-reference" / "corpus" / "manifest.json")
AUTH = {"principal": "learner-alpha", "tenant": "northstar", "roles": ["employee"], "clearances": ["internal"], "issuer": EXPECTED_ISSUER, "audience": EXPECTED_AUDIENCE}
TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def request(method="tools/call", name="search_knowledge", arguments=None):
    return {
        "jsonrpc": "2.0", "id": 1, "method": method,
        "params": {"name": name, "arguments": arguments if arguments is not None else {"question": "What is the travel approval threshold?"}, "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}, "io.modelcontextprotocol/clientInfo": {"name": "untrusted-display-name", "version": "1"}, "traceparent": TRACEPARENT}},
    }


class BridgeTests(unittest.TestCase):
    def test_authorized_query_is_cited(self):
        result = handle_request(request(), AUTH, INDEX)["result"]
        self.assertEqual(result["resultType"], "complete")
        self.assertEqual(result["structuredContent"]["status"], "answered")
        self.assertEqual(result["structuredContent"]["citations"][0]["source_id"], "northstar-travel-2026")

    def test_classification_is_filtered_before_ranking(self):
        message = request(arguments={"question": "What must happen before a consequential production action?"})
        operator_event = {}
        result = handle_request(message, AUTH, INDEX, operator_event)["result"]["structuredContent"]
        self.assertEqual(result["status"], "abstained")
        self.assertNotIn("filtered_documents", result["budget"])
        self.assertGreaterEqual(operator_event["policy_filter_counts"]["classification"], 1)

    def test_cross_tenant_query_does_not_retrieve_hidden_source(self):
        message = request(arguments={"question": "What is the Southstar acquisition project codename?"})
        result = handle_request(message, AUTH, INDEX)["result"]["structuredContent"]
        self.assertEqual(result["status"], "abstained")
        self.assertNotIn("southstar-acquisition-private", {row["source_id"] for row in result["retrieved"]})

    def test_wrong_issuer_or_audience_is_rejected(self):
        for field in ("issuer", "audience"):
            auth = copy.deepcopy(AUTH)
            auth[field] = "wrong"
            self.assertEqual(handle_request(request(), auth, INDEX)["error"]["code"], -30001)

    def test_client_info_cannot_replace_auth_context(self):
        self.assertEqual(handle_request(request(), None, INDEX)["error"]["code"], -30001)

    def test_protocol_metadata_is_required_each_request(self):
        message = request(method="tools/list")
        del message["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"]
        self.assertEqual(handle_request(message, AUTH, INDEX)["error"]["code"], -32602)
        self.assertIsNone(handle_request({"jsonrpc": "2.0", "method": "notifications/unknown", "params": {}}, AUTH, INDEX))
        for invalid_id in (None, True, 1.5, {}, []):
            with self.subTest(request_id=invalid_id):
                message = request(method="tools/list")
                message["id"] = invalid_id
                failure = handle_request(message, AUTH, INDEX)
                self.assertEqual(failure["error"]["code"], -32600)
                self.assertNotIn("id", failure)
        invalid_protocol_type = request(method="tools/list")
        invalid_protocol_type["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] = []
        self.assertEqual(handle_request(invalid_protocol_type, AUTH, INDEX)["error"]["code"], -32602)
        unsupported = request(method="tools/list")
        unsupported["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] = "2025-11-25"
        failure = handle_request(unsupported, AUTH, INDEX)["error"]
        self.assertEqual(failure["code"], -32022)
        self.assertEqual(failure["data"], {"supported": ["2026-07-28"], "requested": "2025-11-25"})
        invalid_client_info = request(method="tools/list")
        invalid_client_info["params"]["_meta"]["io.modelcontextprotocol/clientInfo"] = {}
        self.assertEqual(handle_request(invalid_client_info, AUTH, INDEX)["error"]["code"], -32602)
        for invalid_traceparent in (True, "x" * 56, "trace-test", "00-00000000000000000000000000000000-00f067aa0ba902b7-01"):
            with self.subTest(traceparent=invalid_traceparent):
                message = request(method="tools/list")
                message["params"]["_meta"]["traceparent"] = invalid_traceparent
                self.assertEqual(handle_request(message, AUTH, INDEX)["error"]["code"], -32602)
        for field, value in (("tracestate", "bad=value=extra"), ("baggage", {"not": "a string"})):
            with self.subTest(field=field):
                message = request(method="tools/list")
                message["params"]["_meta"][field] = value
                self.assertEqual(handle_request(message, AUTH, INDEX)["error"]["code"], -32602)

    def test_pinned_tool_inventory_rejects_unknown_name(self):
        self.assertEqual(handle_request(request(name="write_policy"), AUTH, INDEX)["error"]["code"], -32602)
        original_effect = PINNED_TOOLS["search_knowledge"]["side_effect"]
        try:
            PINNED_TOOLS["search_knowledge"]["side_effect"] = "write"
            self.assertEqual(handle_request(request(), AUTH, INDEX)["error"]["code"], -30003)
        finally:
            PINNED_TOOLS["search_knowledge"]["side_effect"] = original_effect
        invalid_arguments = [
            {"question": ""},
            {"question": " "},
            {"question": "x" * 501},
            {"question": "travel", "top_k": True},
            {"question": "travel", "top_k": 0},
            {"question": "travel", "top_k": rag.MAX_RESULTS + 1},
        ]
        for arguments in invalid_arguments:
            with self.subTest(arguments=arguments):
                self.assertEqual(handle_request(request(arguments=arguments), AUTH, INDEX)["error"]["code"], -32602)

    def test_tool_list_is_private_and_read_only(self):
        result = handle_request(request(method="tools/list"), AUTH, INDEX)["result"]
        self.assertEqual(result["tools"], [SEARCH_TOOL])
        self.assertEqual(result["cacheScope"], "private")
        self.assertEqual(result["ttlMs"], 0)
        self.assertTrue(result["tools"][0]["annotations"]["readOnlyHint"])
        self.assertEqual(result["tools"][0]["inputSchema"]["properties"]["top_k"]["maximum"], rag.MAX_RESULTS)

    def test_trace_is_propagated_and_telemetry_is_redacted(self):
        operator_event = {}
        result = handle_request(request(), AUTH, INDEX, operator_event)["result"]
        raw = json.dumps(operator_event, sort_keys=True)
        self.assertEqual(result["_meta"]["traceparent"], TRACEPARENT)
        self.assertNotIn("travel approval", raw)
        self.assertNotIn("employee", raw)
        self.assertNotIn("internal", raw)
        self.assertIn("policy_filter_counts", operator_event)


if __name__ == "__main__":
    unittest.main()
