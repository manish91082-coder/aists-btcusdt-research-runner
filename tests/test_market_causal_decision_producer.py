import hashlib
import unittest

from aists_brain.causal_decision_producer import (
    CausalDecisionProducerError,
    produce_causal_strategy_decisions,
)
from aists_brain.decision_lineage import DecisionLineageError, validate_causal_decision_artifact


def candles(count=70, *, trend=1.0):
    rows = []
    interval = 300_000
    price = 100.0
    for index in range(count):
        price += trend
        open_ms = index * interval
        rows.append({
            "open_time_ms": open_ms,
            "close_time_ms": open_ms + interval - 1,
            "open": price - 0.2,
            "high": price + 0.5,
            "low": price - 0.5,
            "close": price,
            "volume": 100.0,
        })
    return rows


def source_hash():
    return hashlib.sha256(b"synthetic-fixture-only-not-market-data").hexdigest()


class CausalDecisionProducerTests(unittest.TestCase):
    def produce(self, rows=None):
        rows = candles() if rows is None else rows
        return produce_causal_strategy_decisions(
            rows, timeframe="5m", candle_csv_sha256=source_hash(),
            brain_version="brain-test-v1", strategy_version="strategy-test-v1",
        )

    def test_artifact_has_causal_lineage_versions_and_safety_contract(self):
        rows = candles()
        artifact = self.produce(rows)
        validated = validate_causal_decision_artifact(
            artifact, candle_csv_sha256=source_hash(),
            candle_close_times_ms=[row["close_time_ms"] for row in rows],
        )
        self.assertEqual(validated["status"], "PASS_CAUSAL_CONTRACT")
        self.assertEqual(artifact["decision_count"], len(rows))
        self.assertEqual(artifact["producer_status"], "ACTIONS_GENERATED_UNVALIDATED")
        self.assertFalse(artifact["safety"]["exchange_order_placement"])
        self.assertFalse(artifact["safety"]["automatic_stop_loss"])
        self.assertFalse(artifact["safety"]["automatic_take_profit"])
        self.assertTrue(all(not d["is_order_instruction"] for d in artifact["decisions"]))

    def test_rising_prices_can_emit_buy_candidate_without_order_instruction(self):
        artifact = self.produce(candles(70, trend=1.0))
        actions = {item["action"] for item in artifact["decisions"]}
        self.assertIn("BUY_CANDIDATE", actions)
        for item in artifact["decisions"]:
            self.assertFalse(item["is_order_instruction"])
            self.assertFalse(item["automatic_stop_loss"])
            self.assertFalse(item["automatic_take_profit"])

    def test_flat_prices_abstain_without_inventing_trade(self):
        rows = []
        interval = 300_000
        for index in range(60):
            open_ms = index * interval
            rows.append({
                "open_time_ms": open_ms, "close_time_ms": open_ms + interval - 1,
                "open": 100.0, "high": 100.5, "low": 99.5,
                "close": 100.0, "volume": 100.0,
            })
        artifact = self.produce(rows)
        self.assertTrue(all(item["action"] == "NO_TRADE" for item in artifact["decisions"]))

    def test_later_candle_change_does_not_change_earlier_snapshot(self):
        original = candles(70)
        changed = candles(71)
        changed[-1]["close"] += 25.0
        changed[-1]["high"] += 25.0
        a = self.produce(original)
        b = self.produce(changed)
        self.assertEqual(a["decisions"][20]["snapshot"], b["decisions"][20]["snapshot"])
        self.assertEqual(a["decisions"][20]["snapshot_sha256"], b["decisions"][20]["snapshot_sha256"])

    def test_future_feature_timestamp_is_rejected_even_after_rehash(self):
        rows = candles()
        artifact = self.produce(rows)
        decision = artifact["decisions"][20]
        decision["snapshot"]["feature_observations"][0]["observed_close_time_ms"] = decision["as_of_ms"] + 1
        from aists_brain.decision_lineage import canonical_sha256
        decision["snapshot_sha256"] = canonical_sha256(decision["snapshot"])
        with self.assertRaises(DecisionLineageError):
            validate_causal_decision_artifact(
                artifact, candle_csv_sha256=source_hash(),
                candle_close_times_ms=[row["close_time_ms"] for row in rows],
            )

    def test_duplicate_decision_ids_rejected_by_lineage_validator(self):
        rows = candles()
        artifact = self.produce(rows)
        artifact["decisions"][1]["decision_id"] = artifact["decisions"][0]["decision_id"]
        from aists_brain.decision_lineage import canonical_sha256
        # Rehashing does not bypass the unique-ID contract.
        artifact["decisions"][1]["snapshot_sha256"] = canonical_sha256(artifact["decisions"][1]["snapshot"])
        with self.assertRaises(DecisionLineageError):
            validate_causal_decision_artifact(
                artifact, candle_csv_sha256=source_hash(),
                candle_close_times_ms=[row["close_time_ms"] for row in rows],
            )

    def test_candle_gap_is_rejected_not_repaired(self):
        rows = candles()
        rows[25]["open_time_ms"] += 300_000
        rows[25]["close_time_ms"] += 300_000
        with self.assertRaises(CausalDecisionProducerError):
            self.produce(rows)

    def test_bad_source_hash_or_strategy_version_rejected(self):
        rows = candles()
        with self.assertRaises(CausalDecisionProducerError):
            produce_causal_strategy_decisions(
                rows, timeframe="5m", candle_csv_sha256="not-a-sha",
                brain_version="b1", strategy_version="s1",
            )
        with self.assertRaises(CausalDecisionProducerError):
            produce_causal_strategy_decisions(
                rows, timeframe="5m", candle_csv_sha256=source_hash(),
                brain_version="b1", strategy_version=" ",
            )


if __name__ == "__main__":
    unittest.main()
