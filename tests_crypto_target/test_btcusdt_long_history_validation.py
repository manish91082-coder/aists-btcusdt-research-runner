import csv
import tempfile
import unittest
from pathlib import Path

from scripts.run_btcusdt_long_history_validation import (
    chunks, month_list, validate_combined_candles, validate_combined_funding,
)


class LongHistoryValidationTests(unittest.TestCase):
    def test_requested_period_and_six_month_batch_limit(self):
        months = month_list("2020-01", "2026-09")
        self.assertEqual(len(months), 81)
        batches = chunks(months)
        self.assertTrue(all(1 <= len(batch) <= 6 for batch in batches))
        self.assertEqual(sum(map(len, batches)), len(months))
        self.assertEqual(batches[0], ["2020-01", "2020-02", "2020-03", "2020-04", "2020-05", "2020-06"])

    def test_reversed_range_rejected(self):
        with self.assertRaises(ValueError):
            month_list("2021-01", "2020-12")

    def test_combined_candle_grid_is_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candles.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["open_time_ms"])
                writer.writeheader()
                writer.writerows([{"open_time_ms": 0}, {"open_time_ms": 300000}, {"open_time_ms": 600000}])
            result = validate_combined_candles(path, 3)
            self.assertTrue(result["continuous_5m_grid"])
            self.assertEqual(result["rows"], 3)

    def test_combined_candle_gap_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candles.csv"
            path.write_text("open_time_ms\n0\n600000\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_combined_candles(path, 2)

    def test_combined_funding_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "funding.csv"
            path.write_text("funding_time_ms\n100\n100\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_combined_funding(path)


if __name__ == "__main__":
    unittest.main()
