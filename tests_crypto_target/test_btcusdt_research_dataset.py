import csv
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "acquire_validate_btcusdt_history.py"
SPEC = importlib.util.spec_from_file_location("acquire_validate_btcusdt_history", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_btcusdt_research_dataset as PREP


def raw_candle(ts, microseconds=False):
    open_ts = ts * 1000 if microseconds else ts
    close_ts = open_ts + (299999000 if microseconds else 299999)
    return [str(open_ts), "100", "105", "95", "101", "2", str(close_ts),
            "202", "3", "1", "101", "0"]


def write_zip(path, rows):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        import io
        buf = io.StringIO()
        csv.writer(buf).writerows(rows)
        zf.writestr("sample.csv", buf.getvalue())


class TestBtcusdtResearchDataset(unittest.TestCase):
    def test_timestamp_microseconds_normalized_to_ms(self):
        self.assertEqual(PREP.normalize_timestamp("1782864000000000"), 1782864000000)
        self.assertEqual(PREP.normalize_timestamp("1782864000000"), 1782864000000)

    def test_legacy_funding_uses_event_timestamp_not_calc_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07_um_funding.zip"
            start, _ = VALIDATOR.month_bounds_ms("2026-07")
            calc = start + 1000
            event = start + 2000
            write_zip(path, [["calc_time", "funding_rate", "funding_rate_timestamp"],
                             [str(calc), "0.0001", str(event)]])
            events, _ = PREP.load_funding(path, "2026-07")
            self.assertEqual(events[0]["funding_time_ms"], str(event))
            self.assertEqual(events[0]["source_time_field"], "funding_rate_timestamp")

    def test_current_funding_schema_preserves_interval_and_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07_um_funding.zip"
            start, _ = VALIDATOR.month_bounds_ms("2026-07")
            write_zip(path, [["calc_time", "funding_interval_hours", "last_funding_rate"],
                             [str(start), "8", "0.0001"]])
            events, _ = PREP.load_funding(path, "2026-07")
            self.assertEqual(events[0]["funding_rate"], "0.0001")
            self.assertEqual(events[0]["funding_interval_hours"], "8")
            self.assertEqual(events[0]["source_time_field"], "calc_time")

    def test_build_fails_closed_on_missing_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, "required source archive missing"):
                PREP.build(Path(tmp), Path(tmp) / "out", ["2026-07"])


if __name__ == "__main__":
    unittest.main()
