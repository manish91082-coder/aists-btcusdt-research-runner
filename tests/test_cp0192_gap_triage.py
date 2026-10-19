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

    def test_boundary_evidence_counts_missing_child_intervals(self):
        interval_us = TRIAGE.INTERVAL_US["5m"]
        window_us = TRIAGE.INTERVAL_US["4h"]
        start_us = 1518062400000000
        opens = {
            start_us - interval_us,
            start_us + window_us + interval_us,
        }
        result = TRIAGE.boundary_evidence(opens, start_us, interval_us, window_us)
        self.assertEqual(result["missing_intervals_between_boundaries"], 49)
        self.assertEqual(result["boundary_gap_class"], "MULTIPLE_OF_INTERVAL")
        self.assertTrue(result["previous_open_time_utc"])
        self.assertTrue(result["next_open_time_utc"])

    def test_cache_path_is_exact_and_interval_scoped(self):
        root = Path("/cache/monthly")
        self.assertEqual(
            TRIAGE.expected_archive_path(root, "5m", "2018-02"),
            root / "5m" / "2018-02" / "BTCUSDT-5m-2018-02.zip"
        )
        self.assertEqual(
            TRIAGE.expected_archive_path(root, "15m", "2018-02"),
            root / "15m" / "2018-02" / "BTCUSDT-15m-2018-02.zip"
        )
        self.assertEqual(
            TRIAGE.expected_archive_path(root, "30m", "2018-02"),
            root / "30m" / "2018-02" / "BTCUSDT-30m-2018-02.zip"
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

    def test_off_grid_open_time_invalidates_archive_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "BTCUSDT-5m-2017-08.zip"
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("BTCUSDT-5m-2017-08.csv", "1502942400000,1,1,1,1,1\n1502942700001,1,1,1,1,1\n")
            record, opens = TRIAGE.inspect_cached_archive(archive_path, "5m", "2017-08")
            self.assertEqual(record["zip_crc"], "PASS")
            self.assertEqual(record["open_grid_status"], "FAIL")
            self.assertEqual(record["off_grid_rows"], 1)
            self.assertEqual(record["duplicate_open_times"], 0)

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

    def test_expected_child_interval_counts_cover_exact_4h_window(self):
        self.assertEqual(TRIAGE.CHILD_INTERVALS, ("5m", "15m", "30m", "1h"))
        self.assertEqual(TRIAGE.EXPECTED_CHILD_INTERVALS, {"5m": 48, "15m": 16, "30m": 8, "1h": 4})
        for interval in TRIAGE.CHILD_INTERVALS:
            self.assertEqual(TRIAGE.EXPECTED_CHILD_INTERVALS[interval] * TRIAGE.INTERVAL_US[interval], TRIAGE.INTERVAL_US["4h"])

    def test_triage_source_has_no_network_or_mutation_path(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests.", "urlopen(", "download(", "os.remove", "unlink("):
            self.assertNotIn(forbidden, source)
        self.assertIn('"network_used": False', source)
        self.assertIn('"archive_downloads": 0', source)
        self.assertIn('"canonical_source": "NONE"', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)
        self.assertIn('record["open_grid_status"] == "PASS"', source)
        self.assertIn("slots_with_zero_child_opens_in_valid_archives", source)
        self.assertIn("slots_with_unavailable_or_invalid_child_archives", source)
        self.assertNotIn("slots_with_no_child_opens_inside_missing_4h_windows", source)

if __name__ == "__main__":
    unittest.main()
