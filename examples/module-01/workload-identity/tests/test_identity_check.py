import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("identity_check", ROOT / "identity_check.py")
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


class WorkloadIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = checker.load(ROOT / "identity-contract.json")
        cls.hardened = checker.evaluate(
            cls.contract, checker.load(ROOT / "profiles" / "hardened.json")
        )
        cls.unsafe = checker.evaluate(
            cls.contract, checker.load(ROOT / "profiles" / "unsafe.json")
        )

    def test_hardened_profile_passes(self):
        self.assertTrue(self.hardened["valid"], self.hardened["failed_controls"])
        self.assertEqual(9, self.hardened["passed_controls"])

    def test_unsafe_profile_fails(self):
        self.assertFalse(self.unsafe["valid"])
        self.assertEqual(0, self.unsafe["passed_controls"])

    def test_identity_is_dedicated_and_short_lived(self):
        self.assertTrue(self.hardened["controls"]["dedicated_workload_identity"])
        self.assertTrue(self.hardened["controls"]["short_lived_verifiable_identity"])

    def test_peers_verify_each_other(self):
        self.assertTrue(self.hardened["controls"]["mutual_peer_verification"])

    def test_node_workload_and_location_are_attested(self):
        self.assertTrue(self.hardened["controls"]["attested_execution_location"])

    def test_resources_are_least_privilege(self):
        self.assertTrue(self.hardened["controls"]["least_privilege_resources"])

    def test_secrets_are_vault_references_only(self):
        self.assertTrue(self.hardened["controls"]["vault_only_secrets"])

    def test_network_is_segmented_and_default_deny(self):
        self.assertTrue(self.hardened["controls"]["segmented_default_deny_network"])

    def test_execution_and_approval_are_bounded(self):
        self.assertTrue(self.hardened["controls"]["sandboxed_execution"])
        self.assertTrue(self.hardened["controls"]["consequential_human_approval"])

    def test_checker_performs_no_external_actions(self):
        for field in [
            "model_called",
            "network_used",
            "credentials_read",
            "certificates_issued",
            "external_actions",
        ]:
            self.assertFalse(self.hardened[field])

    def test_malformed_profile_types_are_rejected(self):
        mutations = [
            ("workload_identity", "credential_lifetime_minutes", True),
            ("authorization", "actions", "read"),
            ("secrets", "vault_references", "vault://not-a-list"),
            ("runtime_attestation", "allowed_execution_environments", "prod-ai-inference"),
            ("network", "authorized_egress", {"host": "benefits-policy-read.internal"}),
            ("human_approval", "required_for", "destructive"),
            ("execution", "sandboxed", 1),
        ]
        source = checker.load(ROOT / "profiles" / "hardened.json")
        for section, field, malformed_value in mutations:
            with self.subTest(field=f"{section}.{field}"):
                profile = copy.deepcopy(source)
                profile[section][field] = malformed_value
                report = checker.evaluate(self.contract, profile)
                self.assertFalse(report["valid"])
                self.assertIn(f"{section}.{field}", report["schema_errors"])


if __name__ == "__main__":
    unittest.main()
