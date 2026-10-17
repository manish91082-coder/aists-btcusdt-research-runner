"""Tests for independent simulator-to-paper-ledger accounting reconciliation."""
import copy
import unittest

from aists_brain.accounting_reconciliation import (
    ReconciliationError, reconcile_simulation_with_ledger,
)
from aists_brain.cost_aware_simulator import simulate_next_open
from aists_brain.paper_portfolio import create_ledger, append_paper_fill


class AccountingReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.candles = [
            {"open_time_ms": 0, "close_time_ms": 299999, "open": 100.0, "close": 102.0},
            {"open_time_ms": 300000, "close_time_ms": 599999, "open": 103.0, "close": 104.0},
            {"open_time_ms": 600000, "close_time_ms": 899999, "open": 105.0, "close": 106.0},
        ]
        self.decisions = [
            {"decision_id": "buy-1", "as_of_ms": 299999, "action": "BUY_CANDIDATE"},
            {"decision_id": "sell-1", "as_of_ms": 599999, "action": "SELL_CANDIDATE"},
        ]
        self.sim = simulate_next_open(
            self.candles, self.decisions, interval_ms=300000,
            initial_cash_usdt=1000.0, allocation_fraction=0.25,
            fee_bps_per_side=10.0, slippage_bps_per_side=5.0,
        )
        self.ledger = create_ledger(initial_cash_usdt=1000.0)
        for event in self.sim["events"]:
            self.ledger = append_paper_fill(
                self.ledger,
                timestamp_ms=event["fill_open_time_ms"],
                side=event["side"],
                quantity_btc=event["quantity_btc"],
                price_usdt=event["fill_price_usdt"],
                fee_usdt=event["fee_usdt"],
                decision_id=event["decision_id"],
                reason="reconciliation test fixture",
            )

    def test_matching_events_and_ledger_reconcile(self):
        result = reconcile_simulation_with_ledger(self.sim, self.ledger)
        self.assertEqual(result["status"], "PASS_ACCOUNTING_RECONCILIATION")
        self.assertEqual(result["event_count"], 2)
        self.assertEqual(result["buy_count"], 1)
        self.assertEqual(result["sell_count"], 1)
        self.assertAlmostEqual(result["independently_recomputed_cash_usdt"], self.ledger["cash_usdt"])

    def test_cash_tampering_is_detected(self):
        altered = copy.deepcopy(self.sim)
        altered["cash_usdt"] += 1.0
        with self.assertRaisesRegex(ReconciliationError, "cash recomputation"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_event_order_or_id_mismatch_is_detected(self):
        altered = copy.deepcopy(self.ledger)
        altered["events"][0]["decision_id"] = "wrong-id"
        with self.assertRaises(ValueError):
            reconcile_simulation_with_ledger(self.sim, altered)

    def test_ledger_fee_mismatch_is_detected(self):
        altered = copy.deepcopy(self.ledger)
        altered["cumulative_fees_usdt"] += 0.01
        with self.assertRaisesRegex(ReconciliationError, "cumulative fees"):
            reconcile_simulation_with_ledger(self.sim, altered)

    def test_action_side_mismatch_is_rejected(self):
        altered = copy.deepcopy(self.sim)
        altered["events"][0]["side"] = "SELL"
        with self.assertRaisesRegex(ReconciliationError, "action/side mismatch"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_order_instruction_flag_is_rejected(self):
        altered = copy.deepcopy(self.sim)
        altered["events"][0]["is_order_instruction"] = True
        with self.assertRaisesRegex(ReconciliationError, "must not be an order instruction"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_event_slippage_assumption_mismatch_is_rejected(self):
        altered = copy.deepcopy(self.sim)
        altered["events"][0]["slippage_bps_per_side"] = 0.0
        with self.assertRaisesRegex(ReconciliationError, "event slippage assumption mismatch"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_matching_but_incorrect_event_and_ledger_fee_is_detected(self):
        altered_sim = copy.deepcopy(self.sim)
        altered_sim["events"][0]["fee_usdt"] += 0.01
        altered_ledger = create_ledger(initial_cash_usdt=1000.0)
        for event in altered_sim["events"]:
            altered_ledger = append_paper_fill(
                altered_ledger,
                timestamp_ms=event["fill_open_time_ms"],
                side=event["side"],
                quantity_btc=event["quantity_btc"],
                price_usdt=event["fill_price_usdt"],
                fee_usdt=event["fee_usdt"],
                decision_id=event["decision_id"],
                reason="tampered fee regression fixture",
            )
        with self.assertRaisesRegex(ReconciliationError, "fee arithmetic mismatch"):
            reconcile_simulation_with_ledger(altered_sim, altered_ledger)

    def test_mark_to_market_mismatch_is_detected(self):
        altered = copy.deepcopy(self.sim)
        altered["equity_usdt_after_estimated_exit_costs"] += 5.0
        with self.assertRaisesRegex(ReconciliationError, "mark-to-market"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_net_pnl_summary_mismatch_is_detected(self):
        altered = copy.deepcopy(self.sim)
        altered["net_pnl_usdt_after_modeled_costs"] += 1.0
        with self.assertRaisesRegex(ReconciliationError, "net PnL summary"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_net_return_summary_mismatch_is_detected(self):
        altered = copy.deepcopy(self.sim)
        altered["net_return_pct_after_modeled_costs"] += 1.0
        with self.assertRaisesRegex(ReconciliationError, "net return summary"):
            reconcile_simulation_with_ledger(altered, self.ledger)

    def test_event_count_mismatch_is_detected(self):
        altered = copy.deepcopy(self.sim)
        altered["events"] = altered["events"][:1]
        with self.assertRaisesRegex(ReconciliationError, "event count mismatch"):
            reconcile_simulation_with_ledger(altered, self.ledger)


if __name__ == "__main__":
    unittest.main()
