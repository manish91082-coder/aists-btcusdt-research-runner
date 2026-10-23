import calendar
import csv
import io
import unittest
import zipfile
from datetime import datetime, timezone

from scripts.collect_btcusdt_full_history import months_between, validate_archive


def kline_row(ts_ms):
    return [str(ts_ms), "100", "101", "99", "100.5", "2", str(ts_ms + 59999),
            "201", "5", "1", "100.5", "0"]


def zipped_csv(rows):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sample.csv", "\n".join(",".join(row) for row in rows) + "\n")
    return buffer.getvalue()


class FullHistoryCollectorTests(unittest.TestCase):
    def test_month_range_across_year_boundary(self):
        self.assertEqual(months_between("2025-11", "2026-02"),
                         ["2025-11", "2025-12", "2026-01", "2026-02"])

    def test_month_range_rejects_reverse(self):
        with self.assertRaises(ValueError):
            months_between("2026-02", "2026-01")

    def test_kline_archive_checks_exact_month_grid(self):
        month = "2026-02"
        start = int(datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp() * 1000)
        rows = [kline_row(start + i * 60_000) for i in range(calendar.monthrange(2026, 2)[1] * 1440)]
        report = validate_archive(zipped_csv(rows), month, "spot_klines_1m")
        self.assertEqual(report["rows"], 40320)
        self.assertTrue(report["continuous_1m_grid"])

    def test_kline_archive_rejects_missing_minute(self):
        month = "2026-02"
        start = int(datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp() * 1000)
        count = calendar.monthrange(2026, 2)[1] * 1440
        rows = [kline_row(start + i * 60_000) for i in range(count) if i != 12]
        with self.assertRaisesRegex(ValueError, "duplicate, gap, or ordering"):
            validate_archive(zipped_csv(rows), month, "um_klines_1m")

    def test_kline_archive_rejects_invalid_ohlc(self):
        month = "2026-02"
        start = int(datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp() * 1000)
        count = calendar.monthrange(2026, 2)[1] * 1440
        rows = [kline_row(start + i * 60_000) for i in range(count)]
        rows[0][2] = "98"
        with self.assertRaisesRegex(ValueError, "inconsistent OHLC"):
            validate_archive(zipped_csv(rows), month, "spot_klines_1m")

    def test_funding_schema_validates_events(self):
        payload = zipped_csv([
            ["calc_time", "funding_interval_hours", "last_funding_rate"],
            ["1770000000000", "8", "0.0001"],
            ["1770028800000", "8", "-0.0002"],
        ])
        report = validate_archive(payload, "2026-02", "um_funding")
        self.assertEqual(report["schema"], "current")
        self.assertEqual(report["rows"], 2)


if __name__ == "__main__":
    unittest.main()
