import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from client import run_exchange, summarize  # noqa: E402
from dossier_check import evaluate  # noqa: E402
from server import LOOKUP_TOOL, PROTOCOL_VERSION, TrainingServer  # noqa: E402


def initialize(server, version=PROTOCOL_VERSION):
    return server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": version,
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        }
    )


def ready_server():
    server = TrainingServer()
    initialize(server)
    server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return server


class ServerTests(unittest.TestCase):
    def test_initialize_advertises_only_tools(self):
        result = initialize(TrainingServer())["result"]
        self.assertEqual(result["protocolVersion"], PROTOCOL_VERSION)
        self.assertEqual(result["capabilities"], {"tools": {}})

    def test_version_mismatch_selects_supported_version(self):
        result = initialize(TrainingServer(), "older-version")["result"]
        self.assertEqual(result["protocolVersion"], PROTOCOL_VERSION)

    def test_operation_before_initialized_notification_is_rejected(self):
        server = TrainingServer()
        initialize(server)
        result = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(result["error"]["code"], -32002)

    def test_tool_list_has_bounded_schema(self):
        result = ready_server().handle(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        tool = result["result"]["tools"][0]
        self.assertEqual(tool, LOOKUP_TOOL)
        self.assertFalse(tool["inputSchema"]["additionalProperties"])
        self.assertIn("outputSchema", tool)

    def test_known_policy_returns_structured_public_training_data(self):
        result = ready_server().handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "lookup_policy", "arguments": {"policy_id": "RET-01"}},
            }
        )["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(result["structuredContent"]["classification"], "public-training")

    def test_unknown_tool_is_protocol_error(self):
        result = ready_server().handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "delete_all", "arguments": {}},
            }
        )
        self.assertEqual(result["error"]["code"], -32602)

    def test_invalid_arguments_are_tool_error(self):
        result = ready_server().handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "lookup_policy",
                    "arguments": {"policy_id": "UNKNOWN", "extra": True},
                },
            }
        )["result"]
        self.assertTrue(result["isError"])

    def test_stdio_exchange_has_expected_summary(self):
        responses, stderr = run_exchange()
        summary = summarize(responses, stderr)
        self.assertEqual(summary["response_count"], 3)
        self.assertEqual(summary["tool_names"], ["lookup_policy"])
        self.assertFalse(summary["credentials_used"])
        self.assertFalse(summary["network_used"])
        self.assertTrue(summary["stderr_empty"])


class DossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = json.loads((ROOT / "risk-dossier.json").read_text(encoding="utf-8"))

    def changed(self):
        return copy.deepcopy(self.dossier)

    def test_complete_dossier_is_valid(self):
        self.assertTrue(evaluate(self.changed())["valid"])

    def test_required_identity_boundary_is_enforced(self):
        dossier = self.changed()
        dossier["identity_boundary"] = ""
        self.assertIn("missing_identity_boundary", evaluate(dossier)["issues"])

    def test_write_tool_requires_prompt(self):
        dossier = self.changed()
        dossier["tools"][0]["side_effect"] = "irreversible_write"
        dossier["tools"][0]["approval"] = "auto"
        self.assertIn("write_tool_needs_prompt", evaluate(dossier)["issues"])

    def test_secrets_in_source_are_rejected(self):
        dossier = self.changed()
        dossier["secrets_in_source"] = True
        self.assertIn("secrets_not_excluded", evaluate(dossier)["issues"])


if __name__ == "__main__":
    unittest.main()
