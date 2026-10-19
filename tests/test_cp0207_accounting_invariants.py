"""CP-0207 independent accounting-oracle fixtures.
These use Decimal and hand-derived expectations, not production accounting helpers.
They validate arithmetic contracts and separately assert the backtest remains gated.
They do not run a market backtest or claim production accounting is end-to-end validated.
"""
from decimal import Decimal, getcontext
from pathlib import Path
import unittest
getcontext().prec = 40
ROOT = Path(__file__).resolve().parents[1]
BACKTEST = ROOT / "scripts" / "AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"
POLICY = ROOT / "evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json"
TOL = Decimal("1e-8")

def buy(cash, reference_price, fee_bps, slippage_bps):
    fee_rate = Decimal(fee_bps) / Decimal(10000)
    slip_rate = Decimal(slippage_bps) / Decimal(10000)
    fill = reference_price * (Decimal(1) + slip_rate)
    quantity = cash / (fill * (Decimal(1) + fee_rate))
    notional = quantity * fill
    fee = notional * fee_rate
    return {"cash": cash-notional-fee, "qty": quantity, "fill": fill, "notional": notional, "fee": fee, "slippage": (fill-reference_price)*quantity}

def sell(quantity, reference_price, fee_bps, slippage_bps):
    fee_rate = Decimal(fee_bps) / Decimal(10000)
    slip_rate = Decimal(slippage_bps) / Decimal(10000)
    fill = reference_price * (Decimal(1) - slip_rate)
    notional = quantity * fill
    fee = notional * fee_rate
    return {"cash": notional-fee, "fill": fill, "notional": notional, "fee": fee, "slippage": (reference_price-fill)*quantity}

class TestCP0207IndependentAccountingOracle(unittest.TestCase):
    def test_buy_ledger_conserves_cash_with_fee(self):
        initial=Decimal("1000"); b=buy(initial,Decimal("100"),10,5)
        self.assertLessEqual(abs(initial-(b["cash"]+b["qty"]*b["fill"]+b["fee"])),TOL)
        self.assertGreater(b["qty"],0); self.assertGreater(b["fee"],0); self.assertGreater(b["slippage"],0)

    def test_round_trip_cash_matches_independent_net_pnl(self):
        initial=Decimal("1000"); b=buy(initial,Decimal("100"),10,5); s=sell(b["qty"],Decimal("110"),10,5)
        final=b["cash"]+s["cash"]; entry=b["notional"]+b["fee"]; pnl=s["cash"]-entry
        self.assertLessEqual(abs(final-(initial+pnl)),TOL)
        self.assertLessEqual(abs(final-Decimal("1096.704944231181112740333130138")),Decimal("0.01"))

    def test_fees_and_slippage_count_once_per_fill(self):
        b=buy(Decimal("1000"),Decimal("100"),10,5); s=sell(b["qty"],Decimal("110"),10,5)
        fees=b["fee"]+s["fee"]; slips=b["slippage"]+s["slippage"]
        self.assertGreater(fees,b["fee"]); self.assertGreater(slips,b["slippage"])
        self.assertLessEqual(abs(fees-(b["notional"]*Decimal("0.001")+s["notional"]*Decimal("0.001"))),TOL)

    def test_mark_to_market_equity(self):
        cash,qty,mark=Decimal("125"),Decimal("3.25"),Decimal("120")
        self.assertEqual(cash+qty*mark,Decimal("515.00"))

    def test_flat_account_equity_equals_cash(self):
        cash,qty=Decimal("987.654321"),Decimal("0")
        self.assertEqual(cash+qty*Decimal("123.45"),cash)

    def test_flat_segment_pnl_reconciles_to_cash_delta(self):
        start=Decimal("1000"); pnls=[Decimal("12.345"),Decimal("-4.125")]; end=start+sum(pnls,Decimal("0"))
        self.assertLessEqual(abs((end-start)-sum(pnls,Decimal("0"))),TOL)

    def test_gap_exposed_pnl_is_not_added_to_scored_segments(self):
        scored=[Decimal("8.25"),Decimal("-1.50")]; diagnostic_only=Decimal("-35.00")
        total=sum(scored,Decimal("0")); self.assertEqual(total,Decimal("6.75")); self.assertNotEqual(total,total+diagnostic_only)
        p=POLICY.read_text(encoding="utf-8").lower(); self.assertIn("censored_gap_exposed",p); self.assertIn("exclude it from scored metrics",p)

    def test_production_backtest_stays_gated(self):
        s=BACKTEST.read_text(encoding="utf-8"); gate=s.index("load_gap_policy_gate("); row=s.index("load_candidate_gate(")
        manifest=s.index('manifest_path=report_dir/"cp0026_research_candidate_manifest.json"'); loop=s.index("for interval in INTERVALS:",s.index("def main():"))
        self.assertLess(gate,row); self.assertLess(row,manifest); self.assertLess(manifest,loop)
        self.assertIn("current_equity=cash+qty*cl[i]",s); self.assertIn("existing spot exposure is carried through gaps",s.lower())

    def test_indicator_warmup_is_segment_specific(self):
        s=BACKTEST.read_text(encoding="utf-8"); f=s[s.index("def add_features("):s.index("def metrics_from_equity(")]
        self.assertIn('out.groupby("segment_id",sort=False)',f)
        for token in ("min_periods=12","min_periods=26","min_periods=14","rolling(20,min_periods=20)","rolling(10,min_periods=10)"): self.assertIn(token,f)

    def test_tolerance_and_safety_state_are_explicit(self):
        self.assertEqual(TOL,Decimal("0.00000001")); p=POLICY.read_text(encoding="utf-8").lower()
        self.assertIn("live_signing_broadcast_orders",p); self.assertIn('"blocked"',p); self.assertIn('"profitability": "not established"',p)

if __name__=="__main__": unittest.main()
