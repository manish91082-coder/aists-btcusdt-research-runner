import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_validate_btcusdt_history.py"
SPEC = importlib.util.spec_from_file_location("btc_history_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def candle(ts, close_ts=None):
    return [str(ts), "100", "105", "95", "101", "2",
            str(close_ts if close_ts is not None else ts + 299999),
            "202", "3", "1", "101", "0"]


class TestBtcusdtHistoryValidator(unittest.TestCase):
    def test_month_range_inclusive_and_year_rollover(self):
        self.assertEqual(MODULE.month_range("2026-11", "2027-01"),
                         ["2026-11", "2026-12", "2027-01"])

    def test_month_range_rejects_more_than_six_months(self):
        with self.assertRaises(ValueError):
            MODULE.month_range("2025-01", "2025-07")

    def test_headerless_historical_um_archive_is_detected(self):
        start, _ = MODULE.month_bounds_ms("2026-07")
        rows = [candle(start + i * 300000) for i in range(8928)]
        result = MODULE.validate_klines(rows, "2026-07", True, "um_klines")
        self.assertFalse(result["header_present"])
        self.assertEqual(result["rows"], 8928)

    def test_valid_month_grid_rejects_incomplete_month(self):
        # Validation intentionally requires a complete month, not a hand-picked sample.
        with self.assertRaisesRegex(ValueError, "expected 8928 monthly 5m candles"):
            MODULE.validate_klines([candle(1782864000000)], "2026-07", False, "spot_klines")

    def test_off_grid_timestamp_rejected(self):
        ts = MODULE.month_bounds_ms("2026-07")[0] + 1
        with self.assertRaisesRegex(ValueError, "off 5m grid"):
            MODULE.validate_klines([candle(ts)], "2026-07", False, "spot_klines")

    def test_funding_schema_and_finite_rate(self):
        rows = [["calc_time", "funding_rate", "funding_rate_timestamp"],
                ["1782864000000", "0.0001", "1782864000000"]]
        result = MODULE.validate_funding(rows, "2026-07")
        self.assertEqual(result["rows"], 1)
        rows[1][1] = "nan"
        with self.assertRaisesRegex(ValueError, "non-finite"):
            MODULE.validate_funding(rows, "2026-07")


if __name__ == "__main__":
    unittest.main()
