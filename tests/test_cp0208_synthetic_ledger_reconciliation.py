"""CP-0208 synthetic event-tape reconciliation.

Runs only the simulator function against four in-memory candles. It never calls
main(), reads candidate market data, or bypasses the G0 gate for a market run.
The reference ledger uses Decimal and independently calculated fill/accounting
equations, then compares each simulator ledger event within 1e-8 USDT.
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
TIMES = [0, 14_400_000, 28_800_000, 43_200_000]
OPENS = [100.0, 100.0, 110.0, 105.0]
CLOSES = [100.0, 102.0, 111.0, 108.0]


def reference_ledger():
    cash = D("10000"); qty = D("0"); fees = D("0"); slippage = D("0"); realized = D("0")
    fee_rate = D("10") / D("10000"); slip_rate = D("5") / D("10000")
    events = []

    def record(event, i, fill=None, equity=None):
        events.append({"event": event, "open_time_ms": TIMES[i], "cash": cash,
                       "quantity": qty, "fill_price": fill,
                       "equity": cash + qty * D(str(CLOSES[i])) if equity is None else equity,
                       "fees_paid": fees, "estimated_slippage_cost": slippage,
                       "net_realized_pnl": realized})

    # Bar 0 closes with a buy signal; bar 1 opens the first position.
    record("BAR_CLOSE_MARK", 0, equity=cash)
    ref = D("100"); fill = ref * (D("1") + slip_rate)
    qty = cash / (fill * (D("1") + fee_rate))
    notional = qty * fill; fee = notional * fee_rate
    cash = max(D("0"), cash-notional-fee); fees += fee; slippage += (fill-ref)*qty
    entry_cost = notional + fee
    record("BUY_FILL", 1, fill=fill, equity=cash+qty*fill)
    record("BAR_CLOSE_MARK", 1)

    # Bar 1's exit signal fills at bar 2 open.
    ref = D("110"); fill = ref * (D("1")-slip_rate)
    notional = qty * fill; fee = notional * fee_rate; net = notional-fee
    fees += fee; slippage += (ref-fill)*qty; realized += net-entry_cost
    cash += net; qty = D("0")
    record("SELL_FILL", 2, fill=fill, equity=cash)
    record("BAR_CLOSE_MARK", 2, equity=cash)

    # Bar 2's entry signal fills at bar 3 open; final close liquidation follows.
    ref = D("105"); fill = ref * (D("1")+slip_rate)
    qty = cash / (fill * (D("1")+fee_rate))
    notional = qty * fill; fee = notional * fee_rate
    cash = max(D("0"), cash-notional-fee); fees += fee; slippage += (fill-ref)*qty
    entry_cost = notional + fee
    record("BUY_FILL", 3, fill=fill, equity=cash+qty*fill)
    record("BAR_CLOSE_MARK", 3, equity=cash+qty*D("108"))

    ref = D("108"); fill = ref * (D("1")-slip_rate)
    notional = qty * fill; fee = notional * fee_rate; net = notional-fee
    fees += fee; slippage += (ref-fill)*qty; realized += net-entry_cost
    cash += net; qty = D("0")
    record("WINDOW_END_LIQUIDATION", 3, fill=fill, equity=cash)
    return events


class TestCP0208SyntheticLedgerReconciliation(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "open_time_ms": TIMES, "open": OPENS,
            "high": [101.0, 103.0, 112.0, 109.0],
            "low": [99.0, 99.0, 109.0, 104.0],
            "close": CLOSES, "volume": [1.0]*4,
            "ema_fast": [2.0, 1.0, 2.0, 2.0],
            "ema_slow": [1.0, 2.0, 1.0, 1.0],
            "rsi14": [50.0]*4, "prior_high20": [float("nan")]*4,
            "prior_low10": [float("nan")]*4,
            # This fixture begins inside a contiguous segment; the signal at row 0 is valid.
            "contiguous": [True, True, True, True],
        })

    def test_every_ledger_event_matches_independent_decimal_oracle(self):
        result = simulate_strategy(self.frame, "4h", 0, 4, "EMA_12_26", 10.0, 5.0, trade_log=True, ledger_log=True)
        expected = reference_ledger()
        actual = result["ledger_log"]
        self.assertEqual(len(actual), len(expected))
        for got, want in zip(actual, expected):
            self.assertEqual(got["event"], want["event"])
            self.assertEqual(got["open_time_ms"], want["open_time_ms"])
            for field in ("cash", "quantity", "equity", "fees_paid", "estimated_slippage_cost", "net_realized_pnl"):
                self.assertLessEqual(abs(D(str(got[field]))-want[field]), TOL, f"{got['event']} {field}")
            if want["fill_price"] is None:
                self.assertIsNone(got["fill_price"])
            else:
                self.assertLessEqual(abs(D(str(got["fill_price"]))-want["fill_price"]), TOL)

    def test_aggregate_result_reconciles_to_independent_ledger(self):
        result = simulate_strategy(self.frame, "4h", 0, 4, "EMA_12_26", 10.0, 5.0, trade_log=True, ledger_log=True)
        expected = reference_ledger()[-1]
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["buy_fills"], 2)
        self.assertEqual(result["sell_fills"], 2)
        self.assertEqual(result["closed_trades"], 2)
        self.assertLessEqual(abs(D(str(result["final_equity"]))-expected["equity"]), TOL)
        self.assertLessEqual(abs(D(str(result["net_realized_pnl"]))-expected["net_realized_pnl"]), TOL)
        self.assertLessEqual(abs(D(str(result["fees_paid"]))-expected["fees_paid"]), TOL)
        self.assertLessEqual(abs(D(str(result["estimated_slippage_cost"]))-expected["estimated_slippage_cost"]), TOL)
        self.assertEqual([t["exit_type"] for t in result["trade_log"]], ["strategy_signal", "window_end_liquidation"])

    def test_ledger_trace_is_opt_in(self):
        result = simulate_strategy(self.frame, "4h", 0, 4, "EMA_12_26", 10.0, 5.0)
        self.assertEqual(result["ledger_log"], [])

if __name__ == "__main__":
    unittest.main()
