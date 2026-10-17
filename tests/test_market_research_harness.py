"""Integration tests for manifest-driven offline research harness."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.research_harness import (
    DECISION_SCHEMA, ResearchHarnessError, run_manifest_driven_simulation,
)
from aists_brain.provenance_input import SCHEMA_VERSION


class ResearchHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv_path = self.root / "candles.csv"
        self.manifest_path = self.root / "manifest.json"
        self.decisions_path = self.root / "decisions.json"
        self.rows = [
            {"open_time_ms": 0, "close_time_ms": 299999, "open": 100, "high": 103,
             "low": 99, "close": 102, "volume": 4},
            {"open_time_ms": 300000, "close_time_ms": 599999, "open": 102, "high": 104,
             "low": 101, "close": 103, "volume": 5},
            {"open_time_ms": 600000, "close_time_ms": 899999, "open": 103, "high": 106,
             "low": 102, "close": 105, "volume": 6},
        ]
        self.write_rows()
        self.write_manifest()
        self.write_decisions()

    def tearDown(self):
        self.tmp.cleanup()

    def write_rows(self):
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume"
            ])
            writer.writeheader()
            writer.writerows(self.rows)

    def write_manifest(self, **overrides):
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "adjudication_status": "PASS",
            "global_g0_status": "PASS",
            "symbol": "BTCUSDT",
            "market": "spot",
            "interval": "5m",
            "csv_sha256": hashlib.sha256(self.csv_path.read_bytes()).hexdigest(),
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

    def write_decisions(self, **overrides):
        artifact = {
            "schema_version": DECISION_SCHEMA,
            "status": "PASS",
            "source_csv_sha256": hashlib.sha256(self.csv_path.read_bytes()).hexdigest(),
            "brain_version": "test-brain-v1",
            "decisions": [
                {"decision_id": "d1", "as_of_ms": 299999, "action": "BUY_CANDIDATE"},
                {"decision_id": "d2", "as_of_ms": 599999, "action": "SELL_CANDIDATE"},
            ],
        }
        artifact.update(overrides)
        self.decisions_path.write_text(json.dumps(artifact), encoding="utf-8")

    def run_harness(self):
        return run_manifest_driven_simulation(
            self.csv_path, self.manifest_path, self.decisions_path,
            expected_interval="5m", initial_cash_usdt=100.0,
            allocation_fraction=0.25, fee_bps_per_side=10, slippage_bps_per_side=5,
        )

    def test_valid_bound_inputs_run_offline_simulation(self):
        result = self.run_harness()
        self.assertEqual(result["status"], "SIMULATED_NOT_VALIDATED")
        self.assertEqual(result["data_input"]["row_count"], 3)
        self.assertEqual(result["decision_input"]["brain_version"], "test-brain-v1")
        self.assertEqual(result["simulation"]["closed_round_trip_count"], 1)
        self.assertFalse(result["simulation"]["events"][0]["is_order_instruction"])

    def test_global_g0_blocked_refuses_run(self):
        self.write_manifest(global_g0_status="BLOCKED_GLOBAL")
        with self.assertRaisesRegex(ResearchHarnessError, "historical data gate rejected"):
            self.run_harness()

    def test_decisions_bound_to_different_csv_refused(self):
        self.write_decisions(source_csv_sha256="d" * 64)
        with self.assertRaisesRegex(ResearchHarnessError, "not bound"):
            self.run_harness()

    def test_non_pass_decision_artifact_refused(self):
        self.write_decisions(status="BLOCKED")
        with self.assertRaisesRegex(ResearchHarnessError, "status is not PASS"):
            self.run_harness()

    def test_missing_brain_version_refused(self):
        self.write_decisions(brain_version="")
        with self.assertRaisesRegex(ResearchHarnessError, "brain_version"):
            self.run_harness()

    def test_decision_outside_candle_history_refused(self):
        self.write_decisions(decisions=[
            {"decision_id": "bad", "as_of_ms": 123456, "action": "BUY_CANDIDATE"}
        ])
        with self.assertRaisesRegex(ResearchHarnessError, "reference a supplied candle"):
            self.run_harness()

    def test_wrong_interval_refused(self):
        with self.assertRaisesRegex(ResearchHarnessError, "historical data gate rejected"):
            run_manifest_driven_simulation(
                self.csv_path, self.manifest_path, self.decisions_path,
                expected_interval="4h", initial_cash_usdt=100.0,
            )


if __name__ == "__main__":
    unittest.main()
