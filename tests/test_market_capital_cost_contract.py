import unittest

from aists_brain.capital_cost_contract import (
    INITIAL_CAPITAL_INR,
    build_capital_cost_contract,
)


class CapitalCostContractTests(unittest.TestCase):
    def complete_inputs(self):
        return {
            "fx_inr_per_usdt": 100.0,
            "fx_source_ref": "approved-fx-record-1",
            "fx_verified": True,
            "allocation_fraction": 0.2,
            "allocation_source_ref": "approved-allocation-policy-1",
            "allocation_verified": True,
            "fee_bps_per_side": 10.0,
            "fee_source_ref": "verified-fee-schedule-1",
            "fee_verified": True,
            "slippage_bps_per_side": 5.0,
            "slippage_source_ref": "approved-slippage-study-1",
            "slippage_verified": True,
            "symbol_filters": {"min_qty": 0.001, "step_size": 0.001, "min_notional": 5.0},
            "symbol_filters_source_ref": "verified-symbol-filter-snapshot-1",
            "symbol_filters_verified": True,
        }

    def test_unknown_inputs_stay_unknown_and_block_model_readiness(self):
        result = build_capital_cost_contract()
        self.assertEqual(result["initial_capital_inr"], 10_000.0)
        self.assertEqual(INITIAL_CAPITAL_INR, 10_000.0)
        self.assertEqual(result["status"], "BLOCKED_UNVERIFIED_ASSUMPTIONS")
        self.assertIsNone(result["capital_usdt"])
        self.assertIsNone(result["max_allocated_usdt"])
        self.assertIsNone(result["estimated_round_trip_cost_usdt_at_max_allocation"])
        self.assertEqual(result["missing_verified_inputs"], ["fx", "allocation", "fee", "slippage", "symbol_filters"])

    def test_unverified_fx_does_not_convert_inr_capital(self):
        result = build_capital_cost_contract(
            fx_inr_per_usdt=100.0,
            fx_source_ref="unreviewed-source",
            fx_verified=False,
        )
        self.assertIsNone(result["capital_usdt"])
        self.assertFalse(result["fx_verified"])
        self.assertIn("fx", result["missing_verified_inputs"])

    def test_complete_verified_contract_computes_transparent_scenario(self):
        result = build_capital_cost_contract(**self.complete_inputs())
        self.assertEqual(result["status"], "ASSUMPTIONS_VERIFIED_FOR_MODELING_ONLY")
        self.assertAlmostEqual(result["capital_usdt"], 100.0)
        self.assertAlmostEqual(result["max_allocated_usdt"], 20.0)
        self.assertAlmostEqual(result["estimated_round_trip_fee_bps"], 20.0)
        self.assertAlmostEqual(result["estimated_round_trip_slippage_bps"], 10.0)
        self.assertAlmostEqual(result["estimated_round_trip_cost_usdt_at_max_allocation"], 0.06)
        self.assertEqual(result["symbol_filters"]["min_qty"], 0.001)
        self.assertEqual(result["bnb"]["status"], "NOT_EVALUATED_UNVERIFIED_OR_INCOMPLETE")

    def test_verified_boolean_without_source_reference_is_not_verified(self):
        inputs = self.complete_inputs()
        inputs["fee_source_ref"] = None
        result = build_capital_cost_contract(**inputs)
        self.assertIsNone(result["fee_bps_per_side"])
        self.assertIn("fee", result["missing_verified_inputs"])
        self.assertEqual(result["status"], "BLOCKED_UNVERIFIED_ASSUMPTIONS")

    def test_bnb_inputs_are_scenario_only_and_need_verified_source(self):
        inputs = self.complete_inputs()
        inputs.update({
            "bnb_fee_savings_fraction": 0.1,
            "bnb_conversion_overhead_fraction": 0.02,
            "bnb_source_ref": "explicit-bnb-scenario-record",
            "bnb_verified": True,
        })
        result = build_capital_cost_contract(**inputs)
        self.assertEqual(result["bnb"]["status"], "SCENARIO_INPUTS_VERIFIED_NOT_EXCHANGE_CONFIRMED")
        self.assertAlmostEqual(result["bnb"]["effective_fee_bps_per_side_scenario_only"], 9.2)
        self.assertFalse(result["gate_boundary"]["profitability_established"])

    def test_unverified_bnb_scenario_is_not_used(self):
        inputs = self.complete_inputs()
        inputs.update({
            "bnb_fee_savings_fraction": 0.1,
            "bnb_conversion_overhead_fraction": 0.02,
            "bnb_source_ref": "unreviewed-bnb-source",
            "bnb_verified": False,
        })
        result = build_capital_cost_contract(**inputs)
        self.assertIsNone(result["bnb"]["effective_fee_bps_per_side_scenario_only"])
        self.assertIsNone(result["bnb"]["source_ref"])

    def test_rejects_invalid_fraction_and_non_finite_values(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            build_capital_cost_contract(allocation_fraction=1.1)
        with self.assertRaisesRegex(ValueError, "finite numeric"):
            build_capital_cost_contract(fx_inr_per_usdt=float("nan"))

    def test_rejects_incomplete_or_invalid_symbol_filters(self):
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            build_capital_cost_contract(symbol_filters={"min_qty": 0.001})
        inputs = self.complete_inputs()
        inputs["symbol_filters"] = {"min_qty": 0.01, "step_size": 0.001, "min_notional": 5, "max_qty": 0.001}
        with self.assertRaisesRegex(ValueError, "max_qty must be >="):
            build_capital_cost_contract(**inputs)

    def test_model_ready_never_authorizes_market_research_or_live_actions(self):
        result = build_capital_cost_contract(**self.complete_inputs())
        self.assertTrue(result["gate_boundary"]["g0_must_be_independently_cleared_before_real_historical_inputs"])
        self.assertFalse(result["gate_boundary"]["candidate_build_backtest_or_paper_authorized_by_this_contract"])
        self.assertFalse(result["gate_boundary"]["live_signing_public_broadcast_exchange_orders"])
        self.assertFalse(result["gate_boundary"]["automatic_stop_loss_take_profit"])


if __name__ == "__main__":
    unittest.main()
