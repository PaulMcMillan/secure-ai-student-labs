import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("secure_ai_check", ROOT / "secure_ai_check.py")
checker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(checker)


class SecureAIEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hardened_path = ROOT / "profiles" / "hardened-synthetic.json"
        cls.hardened = json.loads(cls.hardened_path.read_text(encoding="utf-8"))

    def validate_data(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return checker.validate(path)

    def evidence(self, data, identifier):
        return next(item for item in data["platform_evidence"] if item["id"] == identifier)

    def test_hardened_synthetic_packet_passes(self):
        report = checker.validate(self.hardened_path)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(7, report["modalities"])
        self.assertEqual(8, report["platform_evidence"])
        self.assertFalse(report["host_probed"])
        self.assertFalse(report["performance_claims_satisfy_security_controls"])

    def test_declared_assertions_are_not_accepted_as_evidence(self):
        report = checker.validate(ROOT / "profiles" / "declared-baseline.json")
        self.assertFalse(report["valid"])
        self.assertTrue(any("missing platform evidence" in error for error in report["errors"]))

    def test_wrong_json_shapes_fail_closed_without_tracebacks(self):
        malformed_evidence = copy.deepcopy(self.hardened)
        malformed_evidence["platform_evidence"][0]["evidence_class"] = []
        malformed_evidence["platform_evidence"][0]["status"] = {}
        malformed_packets = (
            ([], "root must be an object"),
            (
                {
                    "safety": None,
                    "modality_controls": None,
                    "platform_evidence": None,
                    "control_spine": None,
                },
                "must be an array",
            ),
            (malformed_evidence, "unknown evidence_class"),
        )
        for packet, expected_error in malformed_packets:
            with self.subTest(packet=packet):
                report = self.validate_data(packet)
                self.assertFalse(report["valid"])
                self.assertTrue(
                    any(expected_error in error for error in report["errors"]),
                    report["errors"],
                )
                self.assertFalse(report["external_actions"])
                self.assertFalse(report["host_probed"])

    def test_gpu_benchmark_cannot_be_reclassified_as_security_control(self):
        data = copy.deepcopy(self.hardened)
        self.evidence(data, "gpu_capability")["counts_as_ai_security_control"] = True
        report = self.validate_data(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("GPU API/benchmark" in error for error in report["errors"]))

    def test_ima_count_is_not_a_pass_threshold(self):
        data = copy.deepcopy(self.hardened)
        self.evidence(data, "ima")["measurement_count_interpretation"] = "higher-is-more-secure"
        report = self.validate_data(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("pass threshold" in error for error in report["errors"]))

    def test_each_data_device_requires_encryption_evidence(self):
        data = copy.deepcopy(self.hardened)
        self.evidence(data, "disk_encryption")["covered_devices"][1]["encrypted"] = False
        report = self.validate_data(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("data-bearing device" in error for error in report["errors"]))

    def test_installed_lkrg_is_not_the_same_as_loaded_lkrg(self):
        data = copy.deepcopy(self.hardened)
        self.evidence(data, "lkrg")["loaded_at_observation"] = False
        report = self.validate_data(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("both installed and loaded" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
