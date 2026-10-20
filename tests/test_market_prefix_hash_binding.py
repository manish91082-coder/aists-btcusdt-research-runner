"""Independent regression checks for causal prefix hashes and feature derivation.

Synthetic candles here are software fixtures only, never profitability evidence.
"""
import hashlib
import json
import unittest

from aists_brain.causal_decision_producer import produce_causal_strategy_decisions
from aists_brain.causal_feature_producer import produce_causal_feature_snapshots
from aists_brain.market_context import analyze_market_context


INTERVAL_MS = 300_000


def fixture_candles(count=55):
    rows = []
    for index in range(count):
        open_ms = index * INTERVAL_MS
        close = 100.0 + index * 0.3 + (index % 4) * 0.1
        rows.append({
            "open_time_ms": open_ms,
            "close_time_ms": open_ms + INTERVAL_MS - 1,
            "open": close - 0.1,
            "high": close + 0.4,
            "low": close - 0.5,
            "close": close,
            "volume": 10.0 + index,
        })
    return rows


def normalized_prefix(rows):
    normalized = []
    for row in rows:
        normalized.append({
            "open_time_ms": row["open_time_ms"],
            "close_time_ms": row["close_time_ms"],
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row["volume"]),
        })
    return normalized


def canonical_hash(value):
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class CausalPrefixHashBindingTests(unittest.TestCase):
    def _assert_prefix_binding(self, artifact, rows):
        for index, decision in enumerate(artifact["decisions"]):
            prefix = normalized_prefix(rows[:index + 1])
            expected_hash = canonical_hash(prefix)
            snapshot = decision["snapshot"]
            self.assertEqual(snapshot["input_prefix_sha256"], expected_hash)
            self.assertTrue(snapshot["feature_observations"])
            for feature in snapshot["feature_observations"]:
                self.assertEqual(feature["source_sha256"], expected_hash)
            expected_context = analyze_market_context(prefix, "5m")
            for feature in snapshot["feature_observations"]:
                self.assertEqual(feature["value"], float(expected_context[feature["feature_name"]]))

    def test_feature_only_producer_hashes_exact_normalized_prefix_and_derives_values_from_it(self):
        rows = fixture_candles()
        artifact = produce_causal_feature_snapshots(
            rows, timeframe="5m", candle_csv_sha256="a" * 64,
            brain_version="test-brain-v1", strategy_version="test-strategy-v1",
        )
        self._assert_prefix_binding(artifact, rows)

    def test_strategy_decision_producer_hashes_exact_normalized_prefix_and_derives_values_from_it(self):
        rows = fixture_candles()
        artifact = produce_causal_strategy_decisions(
            rows, timeframe="5m", candle_csv_sha256="b" * 64,
            brain_version="test-brain-v1", strategy_version="test-strategy-v1",
        )
        self._assert_prefix_binding(artifact, rows)


if __name__ == "__main__":
    unittest.main()
