"""Integration tests for stored causal features entering the offline harness.

Synthetic candles and PASS manifests here are software fixtures only.
"""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.causal_feature_producer import produce_causal_feature_snapshots
from aists_brain.feature_artifact_store import persist_feature_artifact
from aists_brain.provenance_input import SCHEMA_VERSION
from aists_brain.research_harness import (
    ResearchHarnessError,
    run_manifest_driven_simulation_from_stored_features,
)


class StoredFeatureHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv_path = self.root / "candles.csv"
        self.manifest_path = self.root / "manifest.json"
        self.features_path = self.root / "stored-features.json"
        self.rows = [
            {"open_time_ms": i * 300000, "close_time_ms": i * 300000 + 299999,
             "open": 100.0 + i, "high": 102.0 + i, "low": 99.0 + i,
             "close": 101.0 + i, "volume": 10.0 + i}
            for i in range(4)
        ]
        with self.csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "open_time_ms", "close_time_ms", "open", "high", "low", "close", "volume"
            ])
            writer.writeheader()
            writer.writerows(self.rows)
        csv_hash = hashlib.sha256(self.csv_path.read_bytes()).hexdigest()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "adjudication_status": "PASS",
            "global_g0_status": "PASS",
            "symbol": "BTCUSDT",
            "market": "spot",
            "interval": "5m",
            "csv_sha256": csv_hash,
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
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        artifact = produce_causal_feature_snapshots(
            self.rows, timeframe="5m", candle_csv_sha256=csv_hash,
            brain_version="brain-test-v1", strategy_version="strategy-test-v1",
        )
        persist_feature_artifact(
            artifact, self.features_path,
            candle_close_times_ms=[row["close_time_ms"] for row in self.rows],
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_pipeline(self):
        return run_manifest_driven_simulation_from_stored_features(
            self.csv_path, self.manifest_path, self.features_path,
            expected_interval="5m", initial_cash_usdt=100.0,
            symbol_filters={"min_qty": 0.001, "step_size": 0.001, "min_notional": 5},
        )

    def test_verified_stored_artifact_flows_into_harness(self):
        result = self.run_pipeline()
        self.assertEqual(result["status"], "SIMULATED_NOT_VALIDATED")
        self.assertEqual(
            result["decision_input"]["stored_artifact_integrity_status"],
            "VERIFIED_RELOADED",
        )
        self.assertEqual(result["decision_input"]["decision_count"], len(self.rows))
        self.assertEqual(result["simulation"]["event_count"], 0)
        self.assertEqual(
            result["accounting_reconciliation"]["status"],
            "PASS_ACCOUNTING_RECONCILIATION",
        )

    def test_blocked_g0_rejects_before_stored_artifact_use(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["global_g0_status"] = "BLOCKED_GLOBAL"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ResearchHarnessError, "historical data gate rejected"):
            self.run_pipeline()

    def test_tampered_stored_artifact_is_rejected(self):
        envelope = json.loads(self.features_path.read_text(encoding="utf-8"))
        envelope["strategy_version"] = "tampered"
        self.features_path.write_text(json.dumps(envelope), encoding="utf-8")
        with self.assertRaisesRegex(ResearchHarnessError, "integrity gate rejected"):
            self.run_pipeline()


if __name__ == "__main__":
    unittest.main()
