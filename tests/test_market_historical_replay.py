import unittest

from aists_brain.market_context import TIMEFRAMES
from aists_brain.multi_timeframe import build_multi_timeframe_snapshot
from aists_brain.historical_replay import replay_decisions


def make_record(as_of_ms, bullish=True):
    contexts = {tf: {"timeframe": tf, "data_status": "READY"} for tf in TIMEFRAMES}
    label = "TRENDING_BULLISH" if bullish else "TRENDING_BEARISH"
    regimes = {tf: {"timeframe": tf, "regime": label} for tf in TIMEFRAMES}
    snapshot = build_multi_timeframe_snapshot(contexts, regimes, as_of_ms=as_of_ms)
    candidates = {tf: {"status": "NO_ELIGIBLE_STRATEGY", "selected_strategy": None,
                       "selected_action": "NO_TRADE", "is_order_instruction": False} for tf in TIMEFRAMES}
    if bullish:
        for tf in ("5m", "15m", "30m"):
            candidates[tf] = {"status": "ONE_ELIGIBLE_CANDIDATE", "selected_strategy": "TREND_FOLLOWING",
                              "selected_action": "LONG_CANDIDATE", "is_order_instruction": False}
    return {"as_of_ms": as_of_ms, "snapshot": snapshot, "candidates_by_timeframe": candidates}


MANIFEST = {"sources": [{"path": "fixture.csv", "sha256": "a" * 64}]}


class HistoricalReplayTests(unittest.TestCase):
    def test_provenance_gate_is_mandatory(self):
        with self.assertRaisesRegex(RuntimeError, "provenance_gate"):
            replay_decisions([make_record(100)], provenance_gate="BLOCKED", source_manifest=MANIFEST)

    def test_manifest_requires_sha256(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            replay_decisions([make_record(100)], provenance_gate="PASS", source_manifest={"sources": [{"path": "x", "sha256": "bad"}]})

    def test_replays_decisions_without_pnl_claim(self):
        result = replay_decisions([make_record(100), make_record(200, False)], provenance_gate="PASS", source_manifest=MANIFEST)
        self.assertEqual(result["status"], "REPLAYED_NO_PNL")
        self.assertEqual(result["record_count"], 2)
        self.assertEqual(result["decision_counts"]["research_candidate_only"], 1)
        self.assertEqual(result["decision_counts"]["no_trade_or_abstain"], 1)
        self.assertIn("no P&L", " ".join(result["limitations"]))

    def test_duplicate_or_out_of_order_time_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            replay_decisions([make_record(100), make_record(100)], provenance_gate="PASS", source_manifest=MANIFEST)

    def test_snapshot_cannot_be_from_future(self):
        record = make_record(100)
        record["snapshot"]["as_of_ms"] = 101
        with self.assertRaisesRegex(ValueError, "exceeds replay as-of"):
            replay_decisions([record], provenance_gate="PASS", source_manifest=MANIFEST)

    def test_empty_records_is_explicit_empty_replay(self):
        result = replay_decisions([], provenance_gate="PASS", source_manifest=MANIFEST)
        self.assertEqual(result["record_count"], 0)
        self.assertEqual(result["status"], "REPLAYED_NO_PNL")


if __name__ == "__main__":
    unittest.main()
