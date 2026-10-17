"""Causal decision lineage contract tests; no market-performance claims."""
import copy
import unittest

from aists_brain.decision_lineage import (
    DECISION_SCHEMA, DecisionLineageError, canonical_sha256,
    validate_causal_decision_artifact,
)


CSV_HASH = "a" * 64
SOURCE_HASH = "b" * 64


def make_artifact():
    snapshot = {
        "as_of_ms": 299999,
        "brain_version": "brain-v1",
        "strategy_version": "strategy-v1",
        "feature_observations": [{
            "feature_name": "ema_spread",
            "timeframe": "5m",
            "observed_close_time_ms": 299999,
            "source_sha256": SOURCE_HASH,
            "value": 0.125,
        }],
    }
    return {
        "schema_version": DECISION_SCHEMA,
        "status": "PASS",
        "source_csv_sha256": CSV_HASH,
        "brain_version": "brain-v1",
        "strategy_version": "strategy-v1",
        "decisions": [{
            "decision_id": "d1",
            "as_of_ms": 299999,
            "action": "BUY_CANDIDATE",
            "snapshot": snapshot,
            "snapshot_sha256": canonical_sha256(snapshot),
        }],
    }


class DecisionLineageTests(unittest.TestCase):
    def validate(self, artifact):
        return validate_causal_decision_artifact(
            artifact, candle_csv_sha256=CSV_HASH, candle_close_times_ms=[299999, 599999],
        )

    def test_valid_hash_bound_causal_snapshot_passes(self):
        result = self.validate(make_artifact())
        self.assertEqual(result["status"], "PASS_CAUSAL_CONTRACT")
        self.assertEqual(result["decision_count"], 1)
        self.assertEqual(result["decisions"][0]["action"], "BUY_CANDIDATE")

    def test_future_feature_timestamp_is_rejected_even_with_recomputed_hash(self):
        artifact = make_artifact()
        snapshot = artifact["decisions"][0]["snapshot"]
        snapshot["feature_observations"][0]["observed_close_time_ms"] = 600000
        artifact["decisions"][0]["snapshot_sha256"] = canonical_sha256(snapshot)
        with self.assertRaisesRegex(DecisionLineageError, "future feature data"):
            self.validate(artifact)

    def test_snapshot_tampering_is_detected(self):
        artifact = make_artifact()
        artifact["decisions"][0]["snapshot"]["feature_observations"][0]["value"] = 999
        with self.assertRaisesRegex(DecisionLineageError, "snapshot hash mismatch"):
            self.validate(artifact)

    def test_wrong_candle_csv_binding_is_rejected(self):
        artifact = make_artifact()
        artifact["source_csv_sha256"] = "c" * 64
        with self.assertRaisesRegex(DecisionLineageError, "not bound"):
            self.validate(artifact)

    def test_brain_and_strategy_version_must_match_snapshot(self):
        artifact = make_artifact()
        artifact["decisions"][0]["snapshot"]["strategy_version"] = "other"
        artifact["decisions"][0]["snapshot_sha256"] = canonical_sha256(artifact["decisions"][0]["snapshot"])
        with self.assertRaisesRegex(DecisionLineageError, "strategy version mismatch"):
            self.validate(artifact)

    def test_invalid_feature_source_hash_and_nonfinite_value_rejected(self):
        artifact = make_artifact()
        feature = artifact["decisions"][0]["snapshot"]["feature_observations"][0]
        feature["source_sha256"] = "not-a-hash"
        artifact["decisions"][0]["snapshot_sha256"] = canonical_sha256(artifact["decisions"][0]["snapshot"])
        with self.assertRaisesRegex(DecisionLineageError, "source hash invalid"):
            self.validate(artifact)
        artifact = make_artifact()
        artifact["decisions"][0]["snapshot"]["feature_observations"][0]["value"] = float("nan")
        with self.assertRaisesRegex(DecisionLineageError, "finite JSON-compatible"):
            self.validate(artifact)

    def test_decision_must_reference_known_candle_close(self):
        artifact = make_artifact()
        artifact["decisions"][0]["as_of_ms"] = 123
        with self.assertRaisesRegex(DecisionLineageError, "supplied candle close"):
            self.validate(artifact)


if __name__ == "__main__":
    unittest.main()
