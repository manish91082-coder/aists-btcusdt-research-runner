import importlib.util
import io
import unittest
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0171_Daily_Archive_Acquisition.py"
SPEC = importlib.util.spec_from_file_location("cp0171", SCRIPT)
cp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cp)

class TestCP0171(unittest.TestCase):
    def test_frozen_scope_is_108_objects(self):
        self.assertEqual(len(tuple(cp.target_days())) * len(cp.INTERVALS), 108)

    def test_official_url_allowlist(self):
        path = "/data/spot/daily/klines/BTCUSDT/4h/BTCUSDT-4h-2026-10-01.zip"
        self.assertTrue(cp.official_url("https://data.binance.vision" + path, path))
        self.assertFalse(cp.official_url("http://data.binance.vision" + path, path))
        self.assertFalse(cp.official_url("https://data.binance.vision.attacker.invalid" + path, path))
        self.assertFalse(cp.official_url("https://api.binance.com/api/v3/klines", path))

    def test_filename_bound_checksum(self):
        name = "BTCUSDT-4h-2026-10-01.zip"
        self.assertEqual(cp.parse_checksum("a"*64 + "  " + name, name), "a"*64)
        self.assertIsNone(cp.parse_checksum("a"*64 + "  unrelated.zip", name))
        self.assertIsNone(cp.parse_checksum("a"*64 + "  " + name + "\n" + "b"*64 + "  " + name, name))

    def test_synthetic_daily_archive_quality(self):
        day = date(2026, 10, 1)
        start = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp() * 1000)
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as z:
            rows = []
            for i in range(6):
                op = start + i * cp.STEP_MS["4h"]
                close = op + cp.STEP_MS["4h"] - 1
                rows.append(",".join(map(str, [op, "1", "2", "0.5", "1.5", "10", close, "15", "7", "4", "6", "0"])))
            z.writestr("BTCUSDT-4h-2026-10-01.csv", "\n".join(rows) + "\n")
        qa = cp.inspect_zip(payload.getvalue(), "4h", day)
        self.assertEqual(qa["zip_crc"], "PASS")
        self.assertEqual(qa["row_count"], 6)
        self.assertEqual(qa["off_grid_open_times"], 0)
        self.assertEqual(qa["wrong_utc_date_rows"], 0)
        self.assertEqual(qa["row_count_status"], "EXPECTED_COUNT")

    def test_timestamp_unit_guard(self):
        self.assertEqual(cp.ts_ms("1790812800000"), 1790812800000)
        with self.assertRaises(ValueError):
            cp.ts_ms("12345")

if __name__ == "__main__":
    unittest.main()
