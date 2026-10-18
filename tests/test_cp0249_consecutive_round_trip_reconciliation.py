"""CP-0249: consecutive round-trip accounting reconciliation.

Deterministic synthetic fixture only. Exercises the production simulator on three
sequential long-only round trips, with the last position liquidated at window end.
No historical market data, strategy evaluation, or G0 bypass is involved.
"""
from decimal import Decimal, getcontext
from pathlib import Path
import sys
import unittest
import pandas as pd

getcontext().prec = 40
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from AISTS_CP0027_MultiTimeframe_Baseline_Backtest import simulate_strategy

D = Decimal
TOL = D("1e-8")
TIMES = [i * 14_400_000 for i in range(6)]
OPENS = [100.0, 100.0, 110.0, 105.0, 115.0, 120.0]
CLOSES = [100.0, 102.0, 111.0, 108.0, 116.0, 125.0]
FAST = [2.0, 1.0, 2.0, 1.0, 2.0, 1.0]
SLOW = [1.0, 2.0, 1.0, 2.0, 1.0, 2.0]


def independent_totals():
    """Hand-specified signal/fill sequence; Decimal equations independent of simulator."""
    cash = D("10000")
    qty = D("0")
    fees = D("0")
    slippage = D("0")
    realized = D("0")
    fee_rate = D("10") / D("10000")
    slip_rate = D("5") / D("10000")
    closed = 0

    # Three buy/sell cycles: signal at bars 0..4 fills at the next open.
    for signal_bar, side in ((0, "BUY"), (1, "SELL"), (2, "BUY"),
                             (3, "SELL"), (4, "BUY")):
        ref = D(str(OPENS[signal_bar + 1]))
        if side == "BUY":
            fill = ref * (D("1") + slip_rate)
            qty = cash / (fill * (D("1") + fee_rate))
            notional = qty * fill
            fee = notional * fee_rate
            cash -= notional + fee
            fees += fee
            slippage += (fill - ref) * qty
            entry_cost = notional + fee
        else:
            fill = ref * (D("1") - slip_rate)
            notional = qty * fill
            fee = notional * fee_rate
            proceeds = notional - fee
            fees += fee
            slippage += (ref - fill) * qty
            realized += proceeds - entry_cost
            cash += proceeds
            qty = D("0")
            closed += 1

    # Final position is closed at the final candle close, including costs.
    ref = D(str(CLOSES[-1]))
    fill = ref * (D("1") - slip_rate)
    notional = qty * fill
    fee = notional * fee_rate
    proceeds = notional - fee
    fees += fee
    slippage += (ref - fill) * qty
    realized += proceeds - entry_cost
    cash += proceeds
    qty = D("0")
    closed += 1
    return {"final_equity": cash, "net_realized_pnl": realized,
            "fees_paid": fees, "estimated_slippage_cost": slippage,
            "closed_trades": closed}


class TestCP0249ConsecutiveRoundTripReconciliation(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "open_time_ms": TIMES, "open": OPENS,
            "high": [101.0, 103.0, 112.0, 109.0, 117.0, 126.0],
            "low": [99.0, 99.0, 109.0, 104.0, 114.0, 119.0],
            "close": CLOSES, "volume": [1.0] * 6,
            "ema_fast": FAST, "ema_slow": SLOW,
            "rsi14": [50.0] * 6,
            "prior_high20": [float("nan")] * 6,
            "prior_low10": [float("nan")] * 6,
            "contiguous": [True] * 6,
        })

    def test_higher_fees_or_slippage_never_improve_final_equity(self):
        results = {}
        for fee_bps in (10.0, 15.0, 20.0):
            for slippage_bps in (5.0, 10.0, 20.0):
                result = simulate_strategy(
                    self.frame, "4h", 0, 6, "EMA_12_26",
                    fee_bps, slippage_bps,
                )
                self.assertEqual(result["status"], "OK")
                results[(fee_bps, slippage_bps)] = D(str(result["final_equity"]))

        for fee_bps in (10.0, 15.0):
            for slippage_bps in (5.0, 10.0, 20.0):
                self.assertLessEqual(
                    results[(fee_bps + 5.0, slippage_bps)],
                    results[(fee_bps, slippage_bps)],
                    f"higher fee improved equity at slippage={slippage_bps}",
                )
        for fee_bps in (10.0, 15.0, 20.0):
            self.assertLessEqual(
                results[(fee_bps, 10.0)], results[(fee_bps, 5.0)],
                f"higher slippage improved equity at fee={fee_bps}",
            )
            self.assertLessEqual(
                results[(fee_bps, 20.0)], results[(fee_bps, 10.0)],
                f"higher slippage improved equity at fee={fee_bps}",
            )

    def test_three_consecutive_round_trips_match_independent_decimal_totals(self):
        got = simulate_strategy(
            self.frame, "4h", 0, 6, "EMA_12_26", 10.0, 5.0,
            trade_log=True, ledger_log=True,
        )
        want = independent_totals()
        self.assertEqual(got["status"], "OK")
        self.assertEqual(got["buy_fills"], 3)
        self.assertEqual(got["sell_fills"], 3)
        self.assertEqual(got["closed_trades"], 3)
        for key in ("final_equity", "net_realized_pnl", "fees_paid",
                    "estimated_slippage_cost"):
            self.assertLessEqual(abs(D(str(got[key])) - want[key]), TOL, key)
        self.assertEqual(
            [t["exit_type"] for t in got["trade_log"]],
            ["strategy_signal", "strategy_signal", "window_end_liquidation"],
        )


if __name__ == "__main__":
    unittest.main()
