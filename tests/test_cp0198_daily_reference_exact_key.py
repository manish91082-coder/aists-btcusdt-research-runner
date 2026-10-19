import csv
import hashlib
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0198_DailyReference_4H_ExactKey_Audit.py"
SPEC = importlib.util.spec_from_file_location("cp0198_daily_reference", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(AUDIT)

class TestCP0198DailyReferenceExactKey(unittest.TestCase):
    def test_timestamp_units_normalize_to_microseconds(self):
        self.assertEqual(AUDIT.normalize_timestamp_to_us(1504713600000), (1504713600000000, "milliseconds"))
        self.assertEqual(AUDIT.normalize_timestamp_to_us(1735689600000000), (1735689600000000, "microseconds"))
        with self.assertRaises(ValueError):
            AUDIT.normalize_timestamp_to_us(12345)

    def test_gap_csv_expands_exact_missing_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gaps.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=[
                    "previous_open_time_utc", "next_open_time_utc",
                    "delta_us", "missing_intervals_estimate", "gap_class"
                ])
                writer.writeheader()
                writer.writerow({
                    "previous_open_time_utc": "2017-09-06T12:00:00+00:00",
                    "next_open_time_utc": "2017-09-06T20:00:00+00:00",
                    "delta_us": 28800000000, "missing_intervals_estimate": 1,
                    "gap_class": "MULTIPLE_OF_4H"
                })
            slots = AUDIT.read_gap_slots(path)
            self.assertEqual(len(slots), 1)
            self.assertEqual(slots[0]["expected_open_time_utc"], "2017-09-06T16:00:00+00:00")

    def test_daily_archive_requires_frozen_sha_bytes_crc_and_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BTCUSDT-4h-2017-09-06.zip"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("BTCUSDT-4h-2017-09-06.csv",
                                 "1504713600000,1,1,1,1,1\n1504728000000,1,1,1,1,1\n")
            sha = AUDIT.sha256_file(path)
            row = {
                "date": "2017-09-06", "sha256_local": sha, "official_sha256": sha,
                "sidecar_sha256": "b" * 64, "bytes": str(path.stat().st_size), "zip_crc": "PASS"
            }
            rec, opens = AUDIT.inspect_daily_archive(path, row)
            self.assertEqual(rec["inventory_sha_status"], "MATCH")
            self.assertEqual(rec["inventory_bytes_status"], "MATCH")
            self.assertEqual(rec["zip_crc"], "PASS")
            self.assertEqual(rec["open_grid_status"], "PASS")
            self.assertEqual(len(opens), 2)

    def test_wrong_inventory_hash_blocks_exact_key_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BTCUSDT-4h-2017-09-06.zip"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("BTCUSDT-4h-2017-09-06.csv", "1504713600000,1,1,1,1,1\n")
            row = {
                "date": "2017-09-06", "sha256_local": "a" * 64, "official_sha256": "a" * 64,
                "sidecar_sha256": "b" * 64, "bytes": str(path.stat().st_size), "zip_crc": "PASS"
            }
            rec, opens = AUDIT.inspect_daily_archive(path, row)
            self.assertEqual(rec["inventory_sha_status"], "MISMATCH")
            self.assertEqual(opens, None)

    def test_exact_key_audit_is_cache_only_and_never_promotes_source(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests.", "urlopen(", "download("):
            self.assertNotIn(forbidden, source)
        self.assertIn('"network_used": False', source)
        self.assertIn('"archive_downloads": 0', source)
        self.assertIn('"canonical_source": "NONE"', source)
        self.assertIn('"source_cases_closed": 0', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)

if __name__ == "__main__":
    unittest.main()
