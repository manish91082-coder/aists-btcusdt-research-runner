import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0199_ExactKey_SourceConflict_Probe.py"
SPEC = importlib.util.spec_from_file_location("cp0199_conflict", SCRIPT)
PROBE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(PROBE)

class TestCP0199ExactKeyConflictProbe(unittest.TestCase):
    def test_daily_only_key_is_source_conflict_not_canonical_decision(self):
        self.assertEqual(
            PROBE.classify_presence(False, True),
            "DAILY_PRESENT_MONTHLY_MISSING_SOURCE_CONFLICT"
        )
        self.assertEqual(
            PROBE.classify_presence(False, False),
            "ABSENT_FROM_BOTH_CACHED_ARCHIVES"
        )
        self.assertEqual(
            PROBE.classify_presence(True, True, ["a", "b"], ["a", "c"]),
            "BOTH_PRESENT_ROW_TOKEN_CONFLICT"
        )
        self.assertEqual(
            PROBE.classify_presence(True, True, ["a", "b"], ["a", "b"]),
            "BOTH_PRESENT_ROW_TOKENS_MATCH"
        )

    def test_archive_rows_preserve_raw_tokens_and_exact_open_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BTCUSDT-4h-2017-09-06.zip"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("BTCUSDT-4h-2017-09-06.csv",
                                 "1504713600000,1.0,2.0,0.5,1.5,12\n1504728000000,1.5,2.5,1.0,2.0,13\n")
            result = PROBE.read_archive_rows(path)
            target = 1504713600000000
            self.assertEqual(result["zip_crc"], "PASS")
            self.assertEqual(result["off_grid_rows"], 0)
            self.assertEqual(result["duplicate_open_times"], 0)
            self.assertEqual(result["rows"][0]["open_time_us"], target)
            self.assertEqual(result["rows"][0]["raw_tokens"], ["1504713600000", "1.0", "2.0", "0.5", "1.5", "12"])

    def test_probe_is_cache_only_and_keeps_source_authority_open(self):
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
