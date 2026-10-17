import unittest

from aists_brain.causal_volatility import causal_atr_percentile, causal_atr_percentile_series
from aists_brain.multi_timeframe import build_multi_timeframe_snapshot
from aists_brain.market_context import TIMEFRAMES


def context(tf, status="READY"):
    return {"timeframe": tf, "data_status": status, "trend_state": "BULLISH"}


def regime(tf, label="TRENDING_BULLISH"):
    return {"timeframe": tf, "regime": label, "is_trade_signal": False}


class MultiTimeframeTests(unittest.TestCase):
    def full_inputs(self):
        return ({tf: context(tf) for tf in TIMEFRAMES},
                {tf: regime(tf) for tf in TIMEFRAMES})

    def test_complete_snapshot_has_all_eight_and_is_not_signal(self):
        contexts, regimes = self.full_inputs()
        result = build_multi_timeframe_snapshot(contexts, regimes, as_of_ms=123)
        self.assertEqual(result["readiness"], "READY")
        self.assertEqual(len(result["frames"]), 8)
        self.assertEqual(result["alignment"], "BULLISH_BIAS")
        self.assertFalse(result["is_trade_signal"])

    def test_missing_frame_forces_abstention_without_fill(self):
        contexts, regimes = self.full_inputs()
        contexts.pop("1w")
        result = build_multi_timeframe_snapshot(contexts, regimes)
        self.assertEqual(result["missing_timeframes"], ["1w"])
        self.assertEqual(result["frames"]["1w"]["status"], "MISSING")
        self.assertEqual(result["readiness"], "NO_TRADE_INCOMPLETE_TIMEFRAME_EVIDENCE")

    def test_limited_frame_forces_abstention(self):
        contexts, regimes = self.full_inputs()
        contexts["4h"] = context("4h", "LIMITED_HISTORY")
        result = build_multi_timeframe_snapshot(contexts, regimes)
        self.assertEqual(result["limited_timeframes"], ["4h"])
        self.assertNotEqual(result["readiness"], "READY")

    def test_opposing_regimes_are_reported_as_conflict(self):
        contexts, regimes = self.full_inputs()
        regimes["1d"] = regime("1d", "TRENDING_BEARISH")
        result = build_multi_timeframe_snapshot(contexts, regimes)
        self.assertEqual(result["alignment"], "MIXED_CONFLICT")
        self.assertTrue(result["conflicts"])

    def test_unknown_or_mismatched_timeframe_rejected(self):
        contexts, regimes = self.full_inputs()
        contexts["2h"] = context("2h")
        with self.assertRaisesRegex(ValueError, "unsupported timeframe"):
            build_multi_timeframe_snapshot(contexts, regimes)
        contexts, regimes = self.full_inputs()
        contexts["4h"] = context("1d")
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_multi_timeframe_snapshot(contexts, regimes)

    def test_inputs_are_not_mutated(self):
        contexts, regimes = self.full_inputs()
        before = contexts["5m"].copy()
        build_multi_timeframe_snapshot(contexts, regimes)
        self.assertEqual(contexts["5m"], before)


class CausalVolatilityTests(unittest.TestCase):
    def test_percentile_uses_only_prior_values(self):
        self.assertEqual(causal_atr_percentile(4.0, [1, 2, 3]), 100.0)
        self.assertEqual(causal_atr_percentile(2.0, [1, 2, 3]), 66.66666666666666)

    def test_insufficient_history_returns_none(self):
        self.assertIsNone(causal_atr_percentile(1.0, [0.5, 0.8], min_observations=3, lookback=5))

    def test_series_is_causal_and_early_values_unavailable(self):
        values = [1, 2, 3, 4, 5]
        result = causal_atr_percentile_series(values, min_observations=2, lookback=3)
        self.assertEqual(result[:2], [None, None])
        self.assertEqual(result[2], 100.0)
        self.assertEqual(result[3], 100.0)

    def test_rejects_invalid_values_and_lookback(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            causal_atr_percentile(-1, [1])
        with self.assertRaisesRegex(ValueError, "lookback"):
            causal_atr_percentile(1, [], min_observations=3, lookback=2)


if __name__ == "__main__":
    unittest.main()
