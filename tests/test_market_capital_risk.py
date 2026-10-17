import unittest

from aists_brain.capital_risk import build_capital_plan


class CapitalRiskTests(unittest.TestCase):
    def test_inr_capital_conversion_and_position_cap(self):
        result = build_capital_plan(
            capital_inr=10000, inr_per_usdt=100, allocation_pct=25,
            position_pct=10, fee_bps_per_side=10, slippage_bps_per_side=5,
        )
        self.assertEqual(result["capital_usdt_estimate"], 100)
        self.assertEqual(result["allocation_budget_usdt"], 25)
        self.assertEqual(result["position_notional_usdt"], 10)
        self.assertEqual(result["unallocated_capital_usdt"], 90)
        self.assertFalse(result["controls"]["is_order_instruction"])

    def test_cost_estimate_is_explicit_round_trip(self):
        result = build_capital_plan(
            capital_inr=10000, inr_per_usdt=100, position_pct=10,
            fee_bps_per_side=10, slippage_bps_per_side=5,
        )
        self.assertAlmostEqual(result["estimated_costs_usdt"]["round_trip_total"], 0.03)
        self.assertAlmostEqual(result["estimated_costs_usdt"]["break_even_price_move_bps_approx"], 30)
        self.assertFalse(result["cost_assumptions"]["fee_tier_verified"])

    def test_bnb_discount_is_only_a_supplied_assumption(self):
        result = build_capital_plan(
            capital_inr=10000, inr_per_usdt=100, position_pct=10,
            fee_bps_per_side=10, slippage_bps_per_side=0,
            bnb_fee_discount_pct=25,
        )
        self.assertAlmostEqual(result["estimated_costs_usdt"]["entry_fee"], 0.0075)
        self.assertFalse(result["cost_assumptions"]["bnb_discount_eligibility_verified"])

    def test_invalid_financial_inputs_rejected(self):
        for kwargs in (
            {"capital_inr": 0, "inr_per_usdt": 100},
            {"capital_inr": 10000, "inr_per_usdt": 0},
            {"capital_inr": 10000, "inr_per_usdt": 100, "allocation_pct": 101},
            {"capital_inr": 10000, "inr_per_usdt": 100, "position_pct": 0},
            {"capital_inr": 10000, "inr_per_usdt": 100, "fee_bps_per_side": -1},
            {"capital_inr": 10000, "inr_per_usdt": 100, "bnb_fee_discount_pct": 101},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_capital_plan(**kwargs)

    def test_no_automatic_sl_tp_or_live_orders(self):
        result = build_capital_plan(capital_inr=10000, inr_per_usdt=100)
        self.assertFalse(result["controls"]["automatic_stop_loss"])
        self.assertFalse(result["controls"]["automatic_take_profit"])
        self.assertFalse(result["controls"]["live_signing_enabled"])
        self.assertFalse(result["controls"]["public_broadcast_enabled"])
        self.assertFalse(result["controls"]["binance_orders_placed"])


if __name__ == "__main__":
    unittest.main()
