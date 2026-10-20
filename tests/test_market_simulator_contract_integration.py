"""CP-0276 synthetic-only integration tests for the capital/cost contract.

Fixture values and source references test software wiring only. They are not
external evidence, Binance terms, or BTCUSDT market-performance observations.
"""
import unittest

from aists_brain.capital_cost_contract import build_capital_cost_contract
from aists_brain.cost_aware_simulator import (
    simulate_next_open_with_capital_cost_contract,
)


INTERVAL_MS = 1000
FIXTURE_SCOPE = "SYNTHETIC_SOFTWARE_FIXTURE_ONLY"


def fixture_contract(**overrides):
    inputs = {
        "fx_inr_per_usdt": 100.0,
        "fx_source_ref": "fixture-only-not-real-fx-evidence",
        "fx_verified": True,
        "allocation_fraction": 0.20,
        "allocation_source_ref": "fixture-only-allocation",
        "allocation_verified": True,
        "fee_bps_per_side": 10.0,
        "fee_source_ref": "fixture-only-fee",
        "fee_verified": True,
        "slippage_bps_per_side": 5.0,
        "slippage_source_ref": "fixture-only-slippage",
        "slippage_verified": True,
        "symbol_filters": {
            "min_qty": 0.001,
            "step_size": 0.001,
            "min_notional": 5.0,
        },
        "symbol_filters_source_ref": "fixture-only-symbol-filters",
        "symbol_filters_verified": True,
    }
    inputs.update(overrides)
    return build_capital_cost_contract(**inputs)


def candles():
    prices = [100.0, 100.0, 110.0, 110.0]
    return [
        {
            "open_time_ms": index * INTERVAL_MS,
            "close_time_ms": (index + 1) * INTERVAL_MS - 1,
            "open": price,
            "close": price,
        }
        for index, price in enumerate(prices)
    ]


def decisions():
    return [
        {"decision_id": "fixture-buy", "as_of_ms": 999, "action": "BUY_CANDIDATE"},
        {"decision_id": "fixture-sell", "as_of_ms": 1999, "action": "SELL_CANDIDATE"},
    ]


class CapitalCostSimulatorIntegrationTests(unittest.TestCase):
    def run_fixture(self, contract=None, scope=FIXTURE_SCOPE):
        return simulate_next_open_with_capital_cost_contract(
            candles(),
            decisions(),
            interval_ms=INTERVAL_MS,
            capital_cost_contract=fixture_contract() if contract is None else contract,
            research_input_scope=scope,
        )

    def test_verified_contract_supplies_all_simulator_cost_inputs(self):
        contract = fixture_contract()
        result = self.run_fixture(contract)

        self.assertEqual(contract["capital_usdt"], 100.0)
        self.assertEqual(result["initial_cash_usdt"], contract["capital_usdt"])
        self.assertEqual(result["allocation_fraction"], contract["allocation_fraction"])
        self.assertEqual(result["fee_bps_per_side"], contract["fee_bps_per_side"])
        self.assertEqual(result["slippage_bps_per_side"], contract["slippage_bps_per_side"])
        self.assertEqual(result["exchange_filters"], contract["symbol_filters"])
        self.assertEqual(result["capital_cost_contract_schema"], contract["schema_version"])
        self.assertEqual(result["capital_cost_contract_status"], "ASSUMPTIONS_VERIFIED_FOR_MODELING_ONLY")
        self.assertEqual(result["execution_mode"], "CONTRACT_BOUND_SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(result["event_count"], 2)
        self.assertTrue(all(event["is_order_instruction"] is False for event in result["events"]))
        self.assertFalse(result["safety_boundary"]["real_historical_inputs_permitted"])
        self.assertFalse(result["safety_boundary"]["candidate_build_backtest_or_paper_authorized"])
        self.assertFalse(result["safety_boundary"]["live_signing_public_broadcast_exchange_orders"])
        self.assertFalse(result["safety_boundary"]["automatic_stop_loss_take_profit"])
        self.assertFalse(result["safety_boundary"]["profitability_established"])

    def test_blocked_contract_is_rejected(self):
        contract = fixture_contract(fx_verified=False)
        self.assertEqual(contract["status"], "BLOCKED_UNVERIFIED_ASSUMPTIONS")
        with self.assertRaisesRegex(ValueError, "assumptions are blocked"):
            self.run_fixture(contract)

    def test_missing_source_reference_is_rejected_even_if_status_is_forged(self):
        contract = fixture_contract()
        contract["fee_source_ref"] = None
        with self.assertRaisesRegex(ValueError, "fee_source_ref is missing"):
            self.run_fixture(contract)

    def test_wrong_contract_schema_is_rejected(self):
        contract = fixture_contract()
        contract["schema_version"] = "unknown.schema"
        with self.assertRaisesRegex(ValueError, "unsupported capital_cost_contract schema"):
            self.run_fixture(contract)

    def test_real_historical_scope_is_rejected_while_g0_blocked(self):
        with self.assertRaisesRegex(ValueError, "synthetic software fixtures only"):
            self.run_fixture(scope="HISTORICAL_MARKET_DATA")

    def test_bad_gate_boundary_is_rejected(self):
        contract = fixture_contract()
        contract["gate_boundary"]["candidate_build_backtest_or_paper_authorized_by_this_contract"] = True
        with self.assertRaisesRegex(ValueError, "cannot authorize backtest or paper activity"):
            self.run_fixture(contract)

    def test_non_finite_contract_capital_is_rejected_by_simulator(self):
        contract = fixture_contract()
        contract["capital_usdt"] = float("nan")
        with self.assertRaisesRegex(ValueError, "initial_cash_usdt must be finite numeric"):
            self.run_fixture(contract)


if __name__ == "__main__":
    unittest.main()
