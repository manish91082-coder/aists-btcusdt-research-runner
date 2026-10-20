import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "audit_binance_archive.py"
SPEC = importlib.util.spec_from_file_location("audit_runner", MODULE_PATH)
audit_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_runner)


class KlineHeaderDetectionTests(unittest.TestCase):
    def test_recognises_documented_header_with_spaces(self):
        row = [
            "Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
            "Quote asset volume", "Number of trades", "Taker buy base asset volume",
            "Taker buy quote asset volume", "Ignore",
        ]
        self.assertTrue(audit_runner.is_kline_header(row))

    def test_recognises_snake_case_header(self):
        row = [
            "open_time", "open", "high", "low", "close", "volume", "close_time",
            "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume", "ignore",
        ]
        self.assertTrue(audit_runner.is_kline_header(row))

    def test_does_not_mistake_a_data_row_for_header(self):
        row = [
            "1792022400000", "100", "101", "99", "100.5", "12",
            "1792022699999", "1200", "7", "5", "500", "0",
        ]
        self.assertFalse(audit_runner.is_kline_header(row))

    def test_rejects_wrong_column_count_as_header(self):
        self.assertFalse(audit_runner.is_kline_header(["open_time", "open", "high"]))


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

    def test_proven_failure_takes_precedence_over_blocker(self):
        self.assertEqual(
            audit_runner.classify_audit_status(
                {"gaps": "FAIL", "official_api_spot_check": "BLOCKED"},
                ["gaps", "official_api_spot_check"],
            ),
            "FAIL",
        )


if __name__ == "__main__":
    unittest.main()
