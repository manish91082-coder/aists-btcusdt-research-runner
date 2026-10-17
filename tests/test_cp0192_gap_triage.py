import csv
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0192_Cache_Only_Cross_Interval_Gap_Triage.py"
SPEC = importlib.util.spec_from_file_location("cp0192_triage", SCRIPT)
TRIAGE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(TRIAGE)

class TestCP0192CacheOnlyTriage(unittest.TestCase):
    def test_gap_rows_expand_to_exact_missing_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gaps.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=[
                    "previous_open_time_utc", "next_open_time_utc",
                    "delta_us", "missing_intervals_estimate", "gap_class"
                ])
                writer.writeheader()
                writer.writerow({
                    "previous_open_time_utc": "2018-02-08T00:00:00+00:00",
                    "next_open_time_utc": "2018-02-09T08:00:00+00:00",
                    "delta_us": 115200000000, "missing_intervals_estimate": 7,
                    "gap_class": "MULTIPLE_OF_4H"
                })
            slots = TRIAGE.read_gap_slots(path)
            self.assertEqual(len(slots), 7)
            self.assertEqual(slots[0]["expected_open_time_utc"], "2018-02-08T04:00:00+00:00")
            self.assertEqual(slots[-1]["expected_open_time_utc"], "2018-02-09T04:00:00+00:00")

    def test_rejects_inconsistent_gap_estimate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gaps.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=[
                    "previous_open_time_utc", "next_open_time_utc",
                    "delta_us", "missing_intervals_estimate", "gap_class"
                ])
                writer.writeheader()
                writer.writerow({
                    "previous_open_time_utc": "2018-02-08T00:00:00+00:00",
                    "next_open_time_utc": "2018-02-09T08:00:00+00:00",
                    "delta_us": 115200000000, "missing_intervals_estimate": 6,
                    "gap_class": "MULTIPLE_OF_4H"
                })
            with self.assertRaises(ValueError):
                TRIAGE.read_gap_slots(path)

    def test_cache_path_is_exact_and_interval_scoped(self):
        root = Path("/cache/monthly")
        self.assertEqual(
            TRIAGE.expected_archive_path(root, "5m", "2018-02"),
            root / "5m" / "2018-02" / "BTCUSDT-5m-2018-02.zip"
        )
        self.assertEqual(
            TRIAGE.expected_archive_path(root, "1h", "2018-02"),
            root / "1h" / "2018-02" / "BTCUSDT-1h-2018-02.zip"
        )

    def test_archive_inspection_records_hash_crc_and_timestamp_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "BTCUSDT-5m-2017-08.zip"
            csv_name = "BTCUSDT-5m-2017-08.csv"
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(csv_name, "1502942400000,1,1,1,1,1\n1502942700000,1,1,1,1,1\n")
            record, opens = TRIAGE.inspect_cached_archive(archive_path, "5m", "2017-08")
            self.assertEqual(record["cache_status"], "PRESENT")
            self.assertEqual(record["zip_crc"], "PASS")
            self.assertEqual(record["timestamp_unit"], "milliseconds")
            self.assertEqual(record["timestamp_unit_status"], "PASS")
            self.assertEqual(record["rows"], 2)
            self.assertEqual(len(record["sha256"]), 64)
            self.assertEqual(len(opens), 2)

    def test_wrong_timestamp_unit_is_not_used_as_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "BTCUSDT-5m-2017-08.zip"
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("BTCUSDT-5m-2017-08.csv", "1735689600000000,1,1,1,1,1\n")
            record, opens = TRIAGE.inspect_cached_archive(archive_path, "5m", "2017-08")
            self.assertEqual(record["zip_crc"], "PASS")
            self.assertEqual(record["timestamp_unit_status"], "FAIL")
            self.assertEqual(len(opens), 1)

    def test_triage_source_has_no_network_or_mutation_path(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests.", "urlopen(", "download(", "os.remove", "unlink(", "replace("):
            self.assertNotIn(forbidden, source)
        self.assertIn('"network_used": False', source)
        self.assertIn('"archive_downloads": 0', source)
        self.assertIn('"canonical_source": "NONE"', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)

if __name__ == "__main__":
    unittest.main()
