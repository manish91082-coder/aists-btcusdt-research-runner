import unittest

from aists_brain.strategy_action_engine import (
    ENGINE_VERSION,
    StrategyActionError,
    generate_research_action,
)


def context(**overrides):
    base = {
        "data_status": "READY",
        "trend_state": "BULLISH",
        "momentum_10_bar_pct": 2.0,
        "rsi14": 45.0,
        "latest_close": 110.0,
        "prior_resistance": 105.0,
        "prior_support": 90.0,
    }
    base.update(overrides)
    return base


def regime(**overrides):
    base = {"regime": "TRENDING_BULLISH", "volume_state": "NORMAL"}
    base.update(overrides)
    return base


class StrategyActionEngineTests(unittest.TestCase):
    def test_eligible_trend_candidate_maps_to_buy_candidate(self):
        result = generate_research_action(context(), regime(), position_open=False)
        self.assertEqual(result["schema_version"], ENGINE_VERSION)
        self.assertEqual(result["action"], "BUY_CANDIDATE")
        self.assertEqual(result["selected_strategy"], "TREND_FOLLOWING")
        self.assertEqual(result["fill_timing"], "NEXT_CONTIGUOUS_BAR_OPEN")
        self.assertFalse(result["is_order_instruction"])

    def test_ineligible_or_conflicting_context_abstains(self):
        result = generate_research_action(
            context(trend_state="MIXED", momentum_10_bar_pct=0.0),
            regime(regime="RANGE_OR_MIXED", volume_state="LOW"),
            position_open=False,
        )
        self.assertEqual(result["action"], "NO_TRADE")
        self.assertIsNone(result["selected_strategy"])

    def test_open_trend_position_exits_when_bullish_confirmation_fails(self):
        result = generate_research_action(
            context(trend_state="MIXED"),
            regime(regime="RANGE_OR_MIXED"),
            position_open=True,
            position_strategy="TREND_FOLLOWING",
        )
        self.assertEqual(result["action"], "SELL_CANDIDATE")
        self.assertIn("no longer confirmed", result["reason"])

    def test_breakout_exit_uses_prior_support_reference(self):
        result = generate_research_action(
            context(latest_close=88.0, prior_support=90.0),
            regime(regime="TRENDING_BULLISH"),
            position_open=True,
            position_strategy="BREAKOUT",
        )
        self.assertEqual(result["action"], "SELL_CANDIDATE")
        self.assertIn("prior-lookback support", result["reason"])

    def test_mean_reversion_exit_at_rsi_55(self):
        result = generate_research_action(
            context(rsi14=55.0, trend_state="MIXED"),
            regime(regime="RANGE_OR_MIXED"),
            position_open=True,
            position_strategy="MEAN_REVERSION",
        )
        self.assertEqual(result["action"], "SELL_CANDIDATE")

    def test_incomplete_data_abstains_instead_of_forcing_exit(self):
        result = generate_research_action(
            context(data_status="LIMITED_HISTORY"),
            regime(regime="INSUFFICIENT_DATA", volume_state="UNKNOWN"),
            position_open=True,
            position_strategy="TREND_FOLLOWING",
        )
        self.assertEqual(result["action"], "NO_TRADE")
        self.assertEqual(result["fill_timing"], "NONE")

    def test_position_contract_and_safety_flags(self):
        with self.assertRaises(StrategyActionError):
            generate_research_action(context(), regime(), position_open=True)
        with self.assertRaises(StrategyActionError):
            generate_research_action(context(), regime(), position_open=False, position_strategy="BREAKOUT")
        result = generate_research_action(context(), regime(), position_open=False)
        self.assertFalse(result["automatic_stop_loss"])
        self.assertFalse(result["automatic_take_profit"])
        self.assertFalse(result["is_order_instruction"])

    def test_unsupported_position_strategy_rejected(self):
        with self.assertRaises(StrategyActionError):
            generate_research_action(
                context(), regime(), position_open=True, position_strategy="MAGIC"
            )


if __name__ == "__main__":
    unittest.main()
