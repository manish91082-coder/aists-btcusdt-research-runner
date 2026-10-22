import csv
import io
import zipfile
import unittest
from datetime import datetime, timezone

from scripts.acquire_validate_hd03 import (
    EXPECTED_FIRST_MS, EXPECTED_ROWS, INTERVAL_MS, validate_csv,
)


def make_archive(duplicate_first_two=False):
    csv_buffer = io.StringIO(newline="")
    writer = csv.writer(csv_buffer)
    for i in range(EXPECTED_ROWS):
        open_ms = EXPECTED_FIRST_MS + i * INTERVAL_MS
        if duplicate_first_two and i == 1:
            open_ms = EXPECTED_FIRST_MS
        writer.writerow([
            open_ms, "100", "105", "95", "101", "10",
            open_ms + INTERVAL_MS - 1, "1000", "5", "4", "400", "0",
        ])
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("BTCUSDT-5m-2026-09.csv", csv_buffer.getvalue())
    return payload.getvalue()


class HD03ValidationTests(unittest.TestCase):
    def test_complete_synthetic_month_passes(self):
        report = validate_csv(make_archive(), "spot")
        self.assertTrue(report["passed"], report["errors"])
        self.assertEqual(report["actual_rows"], 8640)
        self.assertEqual(report["duplicate_count"], 0)
        self.assertEqual(report["missing_interval_count"], 0)
        self.assertEqual(report["ohlc_issue_count"], 0)

    def test_duplicate_and_missing_interval_fail(self):
        report = validate_csv(make_archive(duplicate_first_two=True), "spot")
        self.assertFalse(report["passed"])
        self.assertEqual(report["duplicate_count"], 1)
        self.assertEqual(report["missing_interval_count"], 1)
        self.assertTrue(any("duplicate" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
