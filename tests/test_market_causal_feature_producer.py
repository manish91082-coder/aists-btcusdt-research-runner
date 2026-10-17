"""Tests for the causal feature producer; synthetic rows are software fixtures only."""
import unittest

from aists_brain.causal_feature_producer import (
    FeatureProducerError, produce_causal_feature_snapshots,
)
from aists_brain.decision_lineage import validate_causal_decision_artifact


def candles():
    return [
        {"open_time_ms": i * 300000, "close_time_ms": i * 300000 + 299999,
         "open": 100.0 + i, "high": 102.0 + i, "low": 99.0 + i,
         "close": 101.0 + i, "volume": 10.0 + i}
        for i in range(4)
    ]


def produce(rows):
    return produce_causal_feature_snapshots(
        rows, timeframe="5m", candle_csv_sha256="a" * 64,
        brain_version="brain-test-v1", strategy_version="strategy-test-v1",
    )


class CausalFeatureProducerTests(unittest.TestCase):
    def test_produces_hash_bound_snapshots_and_never_emits_trade_action(self):
        artifact = produce(candles())
        self.assertEqual(artifact["producer_status"], "FEATURES_ONLY_NO_TRADE")
        self.assertEqual(artifact["decision_count"], 4)
        self.assertTrue(all(d["action"] == "NO_TRADE" for d in artifact["decisions"]))
        validated = validate_causal_decision_artifact(
            artifact, candle_csv_sha256="a" * 64,
            candle_close_times_ms=[c["close_time_ms"] for c in candles()],
        )
        self.assertEqual(validated["status"], "PASS_CAUSAL_CONTRACT")

    def test_later_candle_change_does_not_change_earlier_snapshot(self):
        original = candles()
        changed = candles()
        changed[-1]["close"] += 50
        changed[-1]["high"] += 50
        first = produce(original)["decisions"][0]
        first_after = produce(changed)["decisions"][0]
        self.assertEqual(first["snapshot"], first_after["snapshot"])
        self.assertEqual(first["snapshot_sha256"], first_after["snapshot_sha256"])

    def test_each_snapshot_features_end_at_its_own_cutoff(self):
        artifact = produce(candles())
        for decision in artifact["decisions"]:
            self.assertTrue(decision["snapshot"]["feature_observations"])
            self.assertTrue(all(
                f["observed_close_time_ms"] <= decision["as_of_ms"]
                for f in decision["snapshot"]["feature_observations"]
            ))

    def test_gaps_are_rejected_without_repair(self):
        rows = candles()
        rows[2]["open_time_ms"] += 300000
        rows[2]["close_time_ms"] += 300000
        with self.assertRaisesRegex(FeatureProducerError, "has a gap"):
            produce(rows)

    def test_invalid_ohlc_is_rejected(self):
        rows = candles()
        rows[0]["low"] = 1000
        with self.assertRaisesRegex(ValueError, "invalid OHLC range"):
            produce(rows)

    def test_invalid_hash_or_versions_are_rejected(self):
        with self.assertRaisesRegex(FeatureProducerError, "lowercase SHA-256"):
            produce_causal_feature_snapshots(
                candles(), timeframe="5m", candle_csv_sha256="X" * 64,
                brain_version="v1", strategy_version="s1",
            )
        with self.assertRaisesRegex(FeatureProducerError, "brain_version"):
            produce_causal_feature_snapshots(
                candles(), timeframe="5m", candle_csv_sha256="a" * 64,
                brain_version=" ", strategy_version="s1",
            )

    def test_wrong_interval_duration_is_rejected(self):
        rows = candles()
        rows[0]["close_time_ms"] -= 1
        with self.assertRaisesRegex(FeatureProducerError, "close_time_ms invalid"):
            produce(rows)


if __name__ == "__main__":
    unittest.main()
