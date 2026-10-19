"""Synthetic-only end-to-end wiring checks for the causal decision pipeline.

Fixtures in this module are software test data, never BTCUSDT market evidence.
"""
import hashlib
import unittest

from aists_brain.causal_decision_producer import produce_causal_strategy_decisions
from aists_brain.cost_aware_simulator import simulate_next_open
from aists_brain.accounting_reconciliation import reconcile_simulation_with_ledger
from aists_brain.paper_portfolio import append_paper_fill, create_ledger, verify_ledger


INTERVAL_MS = 300_000


def synthetic_candles(count=96):
    """Create deterministic, gap-free synthetic OHLCV fixtures only."""
    rows = []
    price = 100.0
    for index in range(count):
        # Piecewise trends plus bounded oscillation exercise regime/action code
        # without pretending to represent actual market history.
        phase = (index // 12) % 4
        drift = (0.8 if phase == 0 else -0.65 if phase == 1 else
                 0.45 if phase == 2 else -0.35)
        close = max(10.0, price + drift + ((index % 5) - 2) * 0.07)
        open_price = price
        high = max(open_price, close) + 0.25
        low = min(open_price, close) - 0.25
        rows.append({
            "open_time_ms": index * INTERVAL_MS,
            "close_time_ms": (index + 1) * INTERVAL_MS - 1,
            "open": round(open_price, 6),
            "high": round(high, 6),
            "low": round(low, 6),
            "close": round(close, 6),
            "volume": float(10 + (index % 7)),
        })
        price = close
    return rows


class SyntheticDecisionPipelineIntegrationTests(unittest.TestCase):
    def test_causal_producer_to_simulator_to_accounting_reconciles(self):
        candles = synthetic_candles()
        source_hash = hashlib.sha256(b"synthetic-software-fixture-only").hexdigest()
        artifact = produce_causal_strategy_decisions(
            candles,
            timeframe="5m",
            candle_csv_sha256=source_hash,
            brain_version="cp0274-test-brain-v1",
            strategy_version="cp0274-test-strategy-v1",
        )

        self.assertEqual(artifact["status"], "PASS")
        self.assertEqual(artifact["producer_status"], "ACTIONS_GENERATED_UNVALIDATED")
        self.assertEqual(artifact["decision_count"], len(candles))
        self.assertEqual(artifact["mode"], "OFFLINE_RESEARCH_ONLY")
        self.assertFalse(artifact["safety"]["live_signing"])
        self.assertFalse(artifact["safety"]["public_broadcast"])
        self.assertFalse(artifact["safety"]["exchange_order_placement"])
        self.assertFalse(artifact["safety"]["automatic_stop_loss"])
        self.assertFalse(artifact["safety"]["automatic_take_profit"])

        decisions = artifact["decisions"]
        allowed = {"BUY_CANDIDATE", "SELL_CANDIDATE", "NO_TRADE"}
        self.assertTrue(all(item["action"] in allowed for item in decisions))
        self.assertTrue(all(item["is_order_instruction"] is False for item in decisions))
        self.assertTrue(all(item["snapshot"]["as_of_ms"] == item["as_of_ms"] for item in decisions))
        self.assertTrue(all(item["snapshot_sha256"] for item in decisions))

        simulation = simulate_next_open(
            candles,
            decisions,
            interval_ms=INTERVAL_MS,
            initial_cash_usdt=100.0,
            allocation_fraction=0.25,
            fee_bps_per_side=10.0,
            slippage_bps_per_side=5.0,
            symbol_filters={"min_qty": 0.001, "step_size": 0.001, "min_notional": 5.0},
        )
        self.assertEqual(simulation["mode"], "OFFLINE_RESEARCH_ONLY")
        self.assertEqual(simulation["status"], "SIMULATED_NOT_VALIDATED")
        self.assertTrue(all(event["is_order_instruction"] is False for event in simulation["events"]))

        ledger = create_ledger(
            initial_cash_usdt=100.0,
            provenance_status="SYNTHETIC_FIXTURE_ONLY_NOT_G0_EVIDENCE",
            fee_assumption_note="test-only fee/slippage assumptions",
        )
        for event in simulation["events"]:
            ledger = append_paper_fill(
                ledger,
                timestamp_ms=event["fill_open_time_ms"],
                side=event["side"],
                quantity_btc=event["quantity_btc"],
                price_usdt=event["fill_price_usdt"],
                fee_usdt=event["fee_usdt"],
                decision_id=event["decision_id"],
                reason="CP-0274 synthetic integration fixture",
            )
        reconciliation = reconcile_simulation_with_ledger(simulation, ledger)
        self.assertEqual(reconciliation["status"], "PASS_ACCOUNTING_RECONCILIATION")
        self.assertEqual(reconciliation["event_count"], simulation["event_count"])
        self.assertEqual(verify_ledger(ledger)["status"], "PASS_HASH_CHAIN")

    def test_producer_refuses_gapped_synthetic_fixture_without_repair(self):
        candles = synthetic_candles(4)
        candles[2]["open_time_ms"] += INTERVAL_MS
        candles[2]["close_time_ms"] += INTERVAL_MS
        with self.assertRaisesRegex(ValueError, "gap detected"):
            produce_causal_strategy_decisions(
                candles,
                timeframe="5m",
                candle_csv_sha256=hashlib.sha256(b"fixture").hexdigest(),
                brain_version="cp0274-test-brain-v1",
                strategy_version="cp0274-test-strategy-v1",
            )


if __name__ == "__main__":
    unittest.main()
