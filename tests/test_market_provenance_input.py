"""Tests for fail-closed, hash-bound historical candle input loading."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.provenance_input import (
    ProvenanceGateError, SCHEMA_VERSION, load_provenance_cleared_candles,
)


class ProvenanceInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv_path = self.root / "candles.csv"
        self.manifest_path = self.root / "manifest.json"
        self.rows = [
            {"open_time_ms": 0, "close_time_ms": 299999, "open": 100, "high": 103,
             "low": 99, "close": 102, "volume": 4},
            {"open_time_ms": 300000, "close_time_ms": 599999, "open": 102, "high": 104,
             "low": 101, "close": 103, "volume": 5},
        ]
        self.write_rows(self.rows)
        self.write_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def write_rows(self, rows):
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume"
            ])
            writer.writeheader()
            writer.writerows(rows)

    def write_manifest(self, **overrides):
        raw = self.csv_path.read_bytes()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "adjudication_status": "PASS",
            "global_g0_status": "PASS",
            "symbol": "BTCUSDT",
            "market": "spot",
            "interval": "5m",
            "csv_sha256": hashlib.sha256(raw).hexdigest(),
            "source_manifest_sha256": "a" * 64,
            "adjudication_report_sha256": "b" * 64,
            "source_archive_sha256": ["c" * 64],
            "expected_row_count": len(self.rows),
            "first_open_time_ms": self.rows[0]["open_time_ms"],
            "last_open_time_ms": self.rows[-1]["open_time_ms"],
            "coverage_pct": 100.0,
            "all_missing_intervals_accounted": True,
            "all_gap_events_accounted": True,
            "completed_candles_only": True,
        }
        manifest.update(overrides)
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_valid_manifest_loads_without_repair(self):
        result = load_provenance_cleared_candles(self.csv_path, self.manifest_path)
        self.assertEqual(result["status"], "LOADED_WITH_EXTERNAL_PASS_CLAIM")
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(result["candles"][1]["close"], 103.0)

    def test_global_gate_blocked_fails_closed(self):
        self.write_manifest(global_g0_status="BLOCKED_GLOBAL")
        with self.assertRaisesRegex(ProvenanceGateError, "global G0"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_candidate_pass_without_global_pass_fails(self):
        self.write_manifest(adjudication_status="PASS", global_g0_status="BLOCKED_GLOBAL")
        with self.assertRaises(ProvenanceGateError):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_csv_tampering_fails_hash(self):
        self.csv_path.write_text(self.csv_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ProvenanceGateError, "SHA-256"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_wrong_interval_fails(self):
        with self.assertRaisesRegex(ProvenanceGateError, "interval mismatch"):
            load_provenance_cleared_candles(
                self.csv_path, self.manifest_path, expected_interval="4h"
            )

    def test_coverage_below_rulebook_threshold_fails(self):
        self.write_manifest(coverage_pct=99.49)
        with self.assertRaisesRegex(ProvenanceGateError, "coverage_pct"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_unaccounted_gap_fails(self):
        self.write_manifest(all_gap_events_accounted=False)
        with self.assertRaisesRegex(ProvenanceGateError, "gap events"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_bad_ohlc_fails(self):
        bad = [dict(row) for row in self.rows]
        bad[0]["high"] = 98
        self.write_rows(bad)
        self.write_manifest()
        with self.assertRaisesRegex(ProvenanceGateError, "invalid OHLC"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_hash_correct_but_bad_ohlc_fails(self):
        bad = [dict(row) for row in self.rows]
        bad[0]["high"] = 98
        self.write_rows(bad)
        self.write_manifest()
        with self.assertRaisesRegex(ProvenanceGateError, "invalid OHLC"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_row_count_mismatch_fails(self):
        self.write_manifest(expected_row_count=999)
        with self.assertRaisesRegex(ProvenanceGateError, "row count"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)

    def test_source_hashes_must_be_valid(self):
        self.write_manifest(source_archive_sha256=["not-a-sha"])
        with self.assertRaisesRegex(ProvenanceGateError, "source archive hash"):
            load_provenance_cleared_candles(self.csv_path, self.manifest_path)


if __name__ == "__main__":
    unittest.main()
