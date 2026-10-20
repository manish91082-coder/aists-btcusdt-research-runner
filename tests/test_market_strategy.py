import unittest

from aists_brain.strategy_candidates import evaluate_strategy_candidates


def market(**overrides):
    result = {
        "data_status": "READY",
        "trend_state": "BULLISH",
        "momentum_10_bar_pct": 2.0,
        "rsi14": 55.0,
    }
    result.update(overrides)
    return result


def regime(**overrides):
    result = {"regime": "TRENDING_BULLISH", "volume_state": "NORMAL"}
    result.update(overrides)
    return result


class StrategyCandidateTests(unittest.TestCase):
    def test_selects_bullish_trend_candidate(self):
        result = evaluate_strategy_candidates(market(), regime())
        self.assertEqual(result["selected_strategy"], "TREND_FOLLOWING")
        self.assertEqual(result["selected_action"], "LONG_CANDIDATE")
        self.assertFalse(result["is_order_instruction"])

    def test_selects_breakout_candidate_with_volume(self):
        result = evaluate_strategy_candidates(
            market(), regime(regime="BREAKOUT_UP_CANDIDATE", volume_state="HIGH")
        )
        self.assertEqual(result["selected_strategy"], "BREAKOUT")

    def test_mean_reversion_only_in_range_context(self):
        result = evaluate_strategy_candidates(
            market(trend_state="MIXED", momentum_10_bar_pct=-0.2, rsi14=25),
            regime(regime="RANGE_OR_MIXED"),
        )
        self.assertEqual(result["selected_strategy"], "MEAN_REVERSION")

    def test_low_volume_breakout_is_rejected(self):
        result = evaluate_strategy_candidates(
            market(), regime(regime="BREAKOUT_UP_CANDIDATE", volume_state="LOW")
        )
        self.assertEqual(result["selected_action"], "NO_TRADE")
        self.assertEqual(result["status"], "NO_ELIGIBLE_STRATEGY")

    def test_insufficient_data_abstains(self):
        result = evaluate_strategy_candidates(
            market(data_status="LIMITED_HISTORY"), regime()
        )
        self.assertEqual(result["status"], "ABSTAIN_INSUFFICIENT_DATA")
        self.assertEqual(result["selected_action"], "NO_TRADE")

    def test_missing_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, "market context missing"):
            evaluate_strategy_candidates({}, regime())
        with self.assertRaisesRegex(ValueError, "regime context missing"):
            evaluate_strategy_candidates(market(), {})


if __name__ == "__main__":
    unittest.main()
