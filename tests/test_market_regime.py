import unittest

from aists_brain.market_regime import classify_market_regime


def context(**overrides):
    result = {
        "schema_version": "aists.market_context.v1",
        "timeframe": "4h",
        "data_status": "READY",
        "trend_state": "BULLISH",
        "latest_close": 110.0,
        "prior_resistance": 109.0,
        "prior_support": 100.0,
        "momentum_10_bar_pct": 3.0,
        "volume_ratio_vs_prior_median": 1.8,
        "atr14_pct": 2.0,
    }
    result.update(overrides)
    return result


class MarketRegimeTests(unittest.TestCase):
    def test_breakout_candidate_is_not_trade_signal(self):
        result = classify_market_regime(context())
        self.assertEqual(result["regime"], "BREAKOUT_UP_CANDIDATE")
        self.assertFalse(result["is_trade_signal"])
        self.assertEqual(result["volume_state"], "HIGH")

    def test_bearish_trend(self):
        result = classify_market_regime(context(
            trend_state="BEARISH", latest_close=95.0, prior_resistance=120.0,
            prior_support=90.0, momentum_10_bar_pct=-2.0,
            volume_ratio_vs_prior_median=1.0,
        ))
        self.assertEqual(result["regime"], "TRENDING_BEARISH")

    def test_range_when_trend_and_momentum_conflict(self):
        result = classify_market_regime(context(
            latest_close=108.0, momentum_10_bar_pct=-0.2
        ))
        self.assertEqual(result["regime"], "RANGE_OR_MIXED")

    def test_insufficient_history_abstains(self):
        result = classify_market_regime(context(data_status="LIMITED_HISTORY"))
        self.assertEqual(result["regime"], "INSUFFICIENT_DATA")
        self.assertEqual(result["confidence"], "UNASSESSED")

    def test_high_volatility_requires_explicit_causal_percentile(self):
        self.assertEqual(classify_market_regime(context())["volatility_state"], "UNASSESSED")
        result = classify_market_regime(context(), high_atr_percentile=92.0)
        self.assertEqual(result["volatility_state"], "HIGH")

    def test_rejects_bad_thresholds(self):
        with self.assertRaisesRegex(ValueError, "volume thresholds"):
            classify_market_regime(context(), low_volume_ratio=2.0, high_volume_ratio=1.5)
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            classify_market_regime(context(), high_atr_percentile=101)

    def test_requires_context_contract(self):
        with self.assertRaisesRegex(ValueError, "context missing required fields"):
            classify_market_regime({"trend_state": "BULLISH"})


if __name__ == "__main__":
    unittest.main()
