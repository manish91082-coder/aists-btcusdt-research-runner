"""Tests for create-only causal feature artifact storage; synthetic data are test fixtures only."""
import json
import tempfile
import unittest
from pathlib import Path

from aists_brain.causal_feature_producer import produce_causal_feature_snapshots
from aists_brain.feature_artifact_store import (
    FeatureArtifactStoreError,
    load_feature_artifact,
    persist_feature_artifact,
)


def fixture_candles():
    return [
        {"open_time_ms": i * 300000, "close_time_ms": i * 300000 + 299999,
         "open": 100.0 + i, "high": 102.0 + i, "low": 99.0 + i,
         "close": 101.0 + i, "volume": 10.0 + i}
        for i in range(4)
    ]


def fixture_artifact():
    return produce_causal_feature_snapshots(
        fixture_candles(), timeframe="5m", candle_csv_sha256="a" * 64,
        brain_version="brain-test-v1", strategy_version="strategy-test-v1",
    )


def close_times():
    return [c["close_time_ms"] for c in fixture_candles()]


class FeatureArtifactStoreTests(unittest.TestCase):
    def test_persist_reload_round_trip_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "features.json"
            result = persist_feature_artifact(
                fixture_artifact(), target, candle_close_times_ms=close_times()
            )
            loaded = load_feature_artifact(target, candle_close_times_ms=close_times())
            self.assertEqual(result["status"], "PERSISTED_AND_RELOADED")
            self.assertEqual(loaded["status"], "VERIFIED_RELOADED")
            self.assertEqual(loaded["artifact"], fixture_artifact())
            self.assertEqual(result["payload_sha256"], loaded["payload_sha256"])
            self.assertEqual(result["file_sha256"], loaded["file_sha256"])

    def test_refuses_to_overwrite_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "features.json"
            target.write_text("keep-me", encoding="utf-8")
            with self.assertRaisesRegex(FeatureArtifactStoreError, "refusing to overwrite"):
                persist_feature_artifact(
                    fixture_artifact(), target, candle_close_times_ms=close_times()
                )
            self.assertEqual(target.read_text(encoding="utf-8"), "keep-me")

    def test_tampered_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "features.json"
            persist_feature_artifact(
                fixture_artifact(), target, candle_close_times_ms=close_times()
            )
            envelope = json.loads(target.read_text(encoding="utf-8"))
            envelope["brain_version"] = "tampered"
            target.write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaisesRegex(FeatureArtifactStoreError, "payload hash mismatch"):
                load_feature_artifact(target, candle_close_times_ms=close_times())

    def test_wrong_candle_close_list_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "features.json"
            with self.assertRaises(FeatureArtifactStoreError):
                persist_feature_artifact(
                    fixture_artifact(), target, candle_close_times_ms=[123]
                )
            self.assertFalse(target.exists())

    def test_artifact_with_preexisting_store_metadata_is_rejected(self):
        artifact = fixture_artifact()
        artifact["artifact_store"] = {}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FeatureArtifactStoreError, "already contains"):
                persist_feature_artifact(
                    artifact, Path(tmp) / "features.json",
                    candle_close_times_ms=close_times(),
                )


if __name__ == "__main__":
    unittest.main()
