import unittest

from aists_brain.market_context import TIMEFRAMES
from aists_brain.multi_timeframe import build_multi_timeframe_snapshot
from aists_brain.multi_timeframe_selector import select_multi_timeframe_candidate


def inputs(alignment_regimes=None):
    contexts = {tf: {"timeframe": tf, "data_status": "READY"} for tf in TIMEFRAMES}
    labels = alignment_regimes or {}
    regimes = {tf: {"timeframe": tf, "regime": labels.get(tf, "TRENDING_BULLISH")}
               for tf in TIMEFRAMES}
    snapshot = build_multi_timeframe_snapshot(contexts, regimes)
    candidates = {tf: {"status": "NO_ELIGIBLE_STRATEGY", "selected_strategy": None,
                       "selected_action": "NO_TRADE", "is_order_instruction": False}
                  for tf in TIMEFRAMES}
    for tf in ("5m", "15m", "30m"):
        candidates[tf] = {"status": "ONE_ELIGIBLE_CANDIDATE",
                          "selected_strategy": "TREND_FOLLOWING",
                          "selected_action": "LONG_CANDIDATE",
                          "is_order_instruction": False}
    return snapshot, candidates


class MultiTimeframeSelectorTests(unittest.TestCase):
    def test_three_matching_timeframes_make_research_candidate(self):
        snapshot, candidates = inputs()
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["status"], "RESEARCH_CANDIDATE_ONLY")
        self.assertEqual(result["selected_strategy"], "TREND_FOLLOWING")
        self.assertFalse(result["is_order_instruction"])

    def test_incomplete_snapshot_abstains(self):
        snapshot, candidates = inputs()
        snapshot["readiness"] = "NO_TRADE_INCOMPLETE_TIMEFRAME_EVIDENCE"
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["selected_action"], "NO_TRADE")

    def test_bearish_or_mixed_alignment_abstains(self):
        snapshot, candidates = inputs({"1d": "TRENDING_BEARISH"})
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["status"], "ABSTAIN_DIRECTIONAL_CONFLICT")

    def test_too_few_confirmations_abstains(self):
        snapshot, candidates = inputs()
        candidates["15m"]["selected_action"] = "NO_TRADE"
        candidates["30m"]["selected_action"] = "NO_TRADE"
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["status"], "ABSTAIN_WEAK_TIMEFRAME_CONFIRMATION")

    def test_disagreeing_strategy_families_abstain(self):
        snapshot, candidates = inputs()
        candidates["15m"]["selected_strategy"] = "BREAKOUT"
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["status"], "ABSTAIN_STRATEGY_FAMILY_DISAGREEMENT")

    def test_missing_evaluation_abstains(self):
        snapshot, candidates = inputs()
        candidates.pop("1mo")
        result = select_multi_timeframe_candidate(snapshot, candidates)
        self.assertEqual(result["status"], "ABSTAIN_MISSING_CANDIDATE_EVALUATIONS")

    def test_rejects_order_instruction_and_bad_schema(self):
        snapshot, candidates = inputs()
        candidates["5m"]["is_order_instruction"] = True
        with self.assertRaisesRegex(ValueError, "must not be an order instruction"):
            select_multi_timeframe_candidate(snapshot, candidates)
        with self.assertRaisesRegex(ValueError, "schema"):
            select_multi_timeframe_candidate({}, candidates)

    def test_invalid_confirmation_threshold_rejected(self):
        snapshot, candidates = inputs()
        with self.assertRaisesRegex(ValueError, "between 1 and 8"):
            select_multi_timeframe_candidate(snapshot, candidates, min_confirming_timeframes=9)

    def test_unknown_candidate_action_fails_closed(self):
        snapshot, candidates = inputs()
        candidates["5m"]["selected_action"] = "BUY"
        with self.assertRaisesRegex(ValueError, "unsupported candidate action"):
            select_multi_timeframe_candidate(snapshot, candidates)

    def test_unsupported_strategy_family_fails_closed(self):
        snapshot, candidates = inputs()
        candidates["5m"]["selected_strategy"] = "UNVALIDATED_MAGIC"
        with self.assertRaisesRegex(ValueError, "unsupported or missing strategy"):
            select_multi_timeframe_candidate(snapshot, candidates)

    def test_no_trade_cannot_carry_a_selected_strategy(self):
        snapshot, candidates = inputs()
        candidates["5m"]["selected_action"] = "NO_TRADE"
        candidates["5m"]["selected_strategy"] = "TREND_FOLLOWING"
        with self.assertRaisesRegex(ValueError, "NO_TRADE candidate must not select a strategy"):
            select_multi_timeframe_candidate(snapshot, candidates)

    def test_non_boolean_order_flag_fails_closed(self):
        snapshot, candidates = inputs()
        candidates["5m"]["is_order_instruction"] = "false"
        with self.assertRaisesRegex(ValueError, "explicitly remain non-order-instruction"):
            select_multi_timeframe_candidate(snapshot, candidates)

    def test_non_mapping_candidate_fails_closed(self):
        snapshot, candidates = inputs()
        candidates["5m"] = None
        with self.assertRaisesRegex(ValueError, "must be a mapping"):
            select_multi_timeframe_candidate(snapshot, candidates)


if __name__ == "__main__":
    unittest.main()
