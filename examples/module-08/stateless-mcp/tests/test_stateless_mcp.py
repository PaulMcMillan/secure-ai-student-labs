import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from client import meta, run_exchange, summarize  # noqa: E402
from dossier_check import evaluate  # noqa: E402
from server import LOOKUP_TOOL, PROTOCOL_VERSION, SERVER_INFO_KEY, handle_request  # noqa: E402


def request(method, request_id=1, **params):
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {**params, "_meta": meta()}}


class ServerTests(unittest.TestCase):
    def test_discover_is_stateless_and_advertises_pinned_version(self):
        result = handle_request(request("server/discover"))["result"]
        self.assertEqual(result["supportedVersions"], [PROTOCOL_VERSION])
        self.assertEqual(result["capabilities"], {"tools": {}})
        self.assertNotIn("serverInfo", result)
        self.assertIn(SERVER_INFO_KEY, result["_meta"])

    def test_every_success_is_complete(self):
        for message in (request("server/discover"), request("tools/list"), request("tools/call", name="lookup_policy", arguments={"policy_id": "RET-01"})):
            self.assertEqual(handle_request(message)["result"]["resultType"], "complete")

    def test_missing_per_request_meta_is_rejected(self):
        result = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        self.assertEqual(result["error"]["code"], -32602)
        self.assertIsNone(handle_request({"jsonrpc": "2.0", "method": "notifications/unknown", "params": {}}))
        for invalid_id in (None, True, 1.5, {}, []):
            with self.subTest(request_id=invalid_id):
                invalid = handle_request(request("tools/list", request_id=invalid_id))
                self.assertEqual(invalid["error"]["code"], -32600)
                self.assertNotIn("id", invalid)
        invalid_protocol_type = request("tools/list")
        invalid_protocol_type["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] = []
        self.assertEqual(handle_request(invalid_protocol_type)["error"]["code"], -32602)
        invalid_client_info = request("tools/list")
        invalid_client_info["params"]["_meta"]["io.modelcontextprotocol/clientInfo"] = {}
        self.assertEqual(handle_request(invalid_client_info)["error"]["code"], -32602)
        for field, value in (
            ("traceparent", "trace-test"),
            ("tracestate", "bad=value=extra"),
            ("baggage", {"not": "a string"}),
        ):
            with self.subTest(field=field):
                invalid_trace = request("tools/list")
                invalid_trace["params"]["_meta"][field] = value
                self.assertEqual(handle_request(invalid_trace)["error"]["code"], -32602)

    def test_wrong_version_is_rejected_without_fallback(self):
        message = request("tools/list")
        message["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] = "2025-11-25"
        failure = handle_request(message)["error"]
        self.assertEqual(failure["code"], -32022)
        self.assertEqual(failure["data"], {"supported": [PROTOCOL_VERSION], "requested": "2025-11-25"})

    def test_missing_capabilities_is_rejected(self):
        message = request("tools/list")
        del message["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"]
        self.assertEqual(handle_request(message)["error"]["code"], -32602)

    def test_tool_list_is_deterministic_bounded_and_cacheable(self):
        result = handle_request(request("tools/list"))["result"]
        self.assertEqual(result["tools"], [LOOKUP_TOOL])
        self.assertEqual(result["cacheScope"], "public")
        self.assertGreater(result["ttlMs"], 0)
        self.assertFalse(LOOKUP_TOOL["inputSchema"]["additionalProperties"])

    def test_unknown_tool_is_rejected_by_pinned_inventory(self):
        result = handle_request(request("tools/call", name="delete_all", arguments={}))
        self.assertEqual(result["error"]["code"], -32602)

    def test_stdio_exchange_has_no_session_or_credentials(self):
        responses, stderr = run_exchange()
        summary = summarize(responses, stderr)
        self.assertEqual(summary["response_count"], 3)
        self.assertEqual(summary["tool_names"], ["lookup_policy"])
        self.assertFalse(summary["session_used"])
        self.assertFalse(summary["credentials_used"])
        self.assertTrue(summary["stderr_empty"])


class DossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads((ROOT / "risk-dossier.json").read_text(encoding="utf-8"))

    def changed(self):
        return copy.deepcopy(self.dossier)

    def test_complete_dossier_is_valid(self):
        self.assertTrue(evaluate(self.changed())["valid"])

    def test_protocol_must_be_current_and_pinned(self):
        dossier = self.changed()
        dossier["protocol_version"] = "2025-11-25"
        self.assertIn("protocol_not_pinned", evaluate(dossier)["issues"])

    def test_each_required_control_must_be_explained(self):
        dossier = self.changed()
        del dossier["controls"]["issuer_and_token_audience_validation"]
        self.assertIn("missing_issuer_and_token_audience_validation", evaluate(dossier)["issues"])

    def test_pinned_tool_inventory_is_required(self):
        dossier = self.changed()
        dossier["pinned_tools"] = []
        self.assertIn("pinned_tool_inventory_invalid", evaluate(dossier)["issues"])


if __name__ == "__main__":
    unittest.main()
