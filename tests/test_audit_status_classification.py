import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "audit_binance_archive.py"
SPEC = importlib.util.spec_from_file_location("audit_runner", MODULE_PATH)
audit_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_runner)


class AuditStatusClassificationTests(unittest.TestCase):
    def test_api_mismatch_is_failure(self):
        self.assertEqual(
            audit_runner.classify_api_sample_results([
                {"status": "PASS"}, {"status": "FAIL"}, {"status": "BLOCKED"}
            ]),
            "FAIL",
        )

    def test_api_transport_error_is_blocked(self):
        self.assertEqual(
            audit_runner.classify_api_sample_results([
                {"status": "BLOCKED", "error": "temporary network error"}
            ]),
            "BLOCKED",
        )

    def test_all_api_samples_pass(self):
        self.assertEqual(
            audit_runner.classify_api_sample_results([
                {"status": "PASS"}, {"status": "PASS"}
            ]),
            "PASS",
        )

    def test_required_blocker_keeps_audit_blocked(self):
        self.assertEqual(
            audit_runner.classify_audit_status(
                {"checksum": "PASS", "official_api_spot_check": "BLOCKED"},
                ["checksum", "official_api_spot_check"],
            ),
            "BLOCKED",
        )

    def test_data_quality_failure_is_failure(self):
        self.assertEqual(
            audit_runner.classify_audit_status(
                {"checksum": "PASS", "gaps": "FAIL"},
                ["checksum", "gaps"],
            ),
            "FAIL",
        )

    def test_all_required_checks_must_pass(self):
        self.assertEqual(
            audit_runner.classify_audit_status(
                {"checksum": "PASS", "gaps": "PASS"},
                ["checksum", "gaps"],
            ),
            "PASS",
        )


if __name__ == "__main__":
    unittest.main()
