"""Adversarial tests for source-candle feature recomputation.

Synthetic candles are software fixtures only, never market-performance evidence.
"""
import copy
import unittest

from aists_brain.causal_feature_producer import produce_causal_feature_snapshots
from aists_brain.decision_lineage import canonical_sha256
from aists_brain.source_feature_verifier import (
    SourceFeatureVerificationError,
    verify_features_against_source_candles,
)


def fixture_candles(count=55):
    rows = []
    interval = 300_000
    for index in range(count):
        open_ms = index * interval
        close = 100.0 + index * 0.3 + (index % 4) * 0.1
        rows.append({
            "open_time_ms": open_ms, "close_time_ms": open_ms + interval - 1,
            "open": close - 0.1, "high": close + 0.4, "low": close - 0.5,
            "close": close, "volume": 10.0 + index,
        })
    return rows


def artifact_for(rows):
    return produce_causal_feature_snapshots(
        rows, timeframe="5m", candle_csv_sha256="a" * 64,
        brain_version="test-brain-v1", strategy_version="test-strategy-v1",
    )


class SourceFeatureVerifierTests(unittest.TestCase):
    def test_actual_source_prefix_and_features_pass(self):
        rows = fixture_candles()
        result = verify_features_against_source_candles(artifact_for(rows), candles=rows)
        self.assertEqual(result["status"], "PASS_SOURCE_FEATURE_RECOMPUTATION")
        self.assertEqual(result["decision_count"], len(rows))

    def test_tampered_feature_value_rejected_even_with_recomputed_snapshot_hash(self):
        rows = fixture_candles()
        artifact = copy.deepcopy(artifact_for(rows))
        decision = artifact["decisions"][30]
        decision["snapshot"]["feature_observations"][0]["value"] += 0.25
        decision["snapshot_sha256"] = canonical_sha256(decision["snapshot"])
        with self.assertRaisesRegex(SourceFeatureVerificationError, "feature value mismatch"):
            verify_features_against_source_candles(artifact, candles=rows)

    def test_tampered_prefix_and_feature_hash_rejected_even_with_recomputed_snapshot_hash(self):
        rows = fixture_candles()
        artifact = copy.deepcopy(artifact_for(rows))
        decision = artifact["decisions"][30]
        fake_hash = "f" * 64
        decision["snapshot"]["input_prefix_sha256"] = fake_hash
        for feature in decision["snapshot"]["feature_observations"]:
            feature["source_sha256"] = fake_hash
        decision["snapshot_sha256"] = canonical_sha256(decision["snapshot"])
        with self.assertRaisesRegex(SourceFeatureVerificationError, "input prefix hash"):
            verify_features_against_source_candles(artifact, candles=rows)


if __name__ == "__main__":
    unittest.main()
