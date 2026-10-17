"""CP-0210 contract-level segment/censor accounting oracle.

Pure in-memory Decimal fixtures and static source guards only. No market data,
candidate build, market backtest, production policy application, or G0 bypass.
"""
from decimal import Decimal, getcontext
import json
from pathlib import Path
import unittest

getcontext().prec = 40
ROOT = Path(__file__).resolve().parents[1]
D = Decimal
TOL = D("1e-8")
CONTRACT = ROOT / "docs/CP0210_Segment_Censor_Accounting_Contract.md"
POLICY = ROOT / "evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json"
BACKTEST = ROOT / "scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"
GAP_GATE = ROOT / "scripts/AISTS_CP0203_GapPolicy_Gate.py"


def eligible_segment_oracle(start_cash, trade_pnls):
    """Independent flat-to-flat segment arithmetic; caller supplies closed eligible P&Ls."""
    total = sum(trade_pnls, D("0"))
    return {"start_cash": start_cash, "scored_pnl": total, "end_cash": start_cash + total}


def censored_episode_oracle(eligible_pnls, censored_episode_diagnostic_pnl):
    """Censored P&L is retained separately and never enters the scored total."""
    scored = sum(eligible_pnls, D("0"))
    return {
        "scored_pnl": scored,
        "eligible_episode_count": len(eligible_pnls),
        "censored_episode_count": 1,
        "excluded_diagnostic_pnl": censored_episode_diagnostic_pnl,
        "full_window_status": "BLOCKED_GAP_VALUATION_UNSCORABLE",
        "fabricated_exit_count": 0,
    }


class TestCP0210SegmentCensorContract(unittest.TestCase):
    def test_flat_segment_cash_delta_matches_eligible_closed_trades(self):
        start = D("1000")
        pnls = [D("12.345"), D("-4.125"), D("0.80")]
        result = eligible_segment_oracle(start, pnls)
        self.assertLessEqual(abs((result["end_cash"] - result["start_cash"]) - result["scored_pnl"]), TOL)
        self.assertEqual(result["scored_pnl"], D("9.020"))

    def test_censored_episode_is_excluded_not_zeroed_or_realized(self):
        result = censored_episode_oracle([D("8.25"), D("-1.50")], D("-35.00"))
        self.assertEqual(result["scored_pnl"], D("6.75"))
        self.assertEqual(result["excluded_diagnostic_pnl"], D("-35.00"))
        self.assertEqual(result["censored_episode_count"], 1)
        self.assertEqual(result["fabricated_exit_count"], 0)
        self.assertEqual(result["full_window_status"], "BLOCKED_GAP_VALUATION_UNSCORABLE")
        self.assertNotEqual(result["scored_pnl"], result["scored_pnl"] + result["excluded_diagnostic_pnl"])

    def test_policy_and_contract_preserve_exact_gap_population_and_status(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        keys = policy["expected_missing_slots"]
        self.assertEqual(len(keys), 17)
        self.assertEqual(len({x["open_time_ms"] for x in keys}), 17)
        self.assertEqual(sum(x["classification"].startswith("EXISTING_ROW_CASE_OVERLAP") for x in keys), 1)
        self.assertEqual(sum(x["classification"] == "GAP_WINDOW_ONLY" for x in keys), 16)
        self.assertEqual(policy["status"], "FROZEN_FOR_SENSITIVITY_ONLY_NOT_G0_CLEARANCE")
        contract = CONTRACT.read_text(encoding="utf-8")
        for token in ("CENSORED_GAP_EXPOSED", "BLOCKED_GAP_VALUATION_UNSCORABLE",
                      "COUNTERFACTUAL_BOUNDARY_CLOSEOUT", "do not create a sell fill",
                      "flat cash", "Decimal", "NOT G0 CLEARANCE"):
            self.assertIn(token.lower(), contract.lower())

    def test_production_application_and_g0_clearance_remain_blocked(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertFalse(policy["explicit_non_effects"]["backtest_authorized"])
        self.assertFalse(policy["explicit_non_effects"]["quarantine_applied_to_candidate_builder"])
        self.assertEqual(policy["scope"]["canonical_source"], "NONE")
        self.assertEqual(policy["scope"]["g0"], "BLOCKED_GLOBAL")
        gate = GAP_GATE.read_text(encoding="utf-8")
        self.assertIn("G0_BLOCKED_GAP_POLICY_UNRESOLVED", gate)
        source = BACKTEST.read_text(encoding="utf-8")
        main = source[source.index("def main():"):]
        self.assertLess(main.index("load_gap_policy_gate("), main.index("load_candidate_gate("))
        self.assertIn("if not contiguous[i]:", source)

    def test_scoring_contract_explicitly_separates_diagnostic_and_scored_pnl(self):
        contract = CONTRACT.read_text(encoding="utf-8").lower()
        for token in ("excluded diagnostic pnl", "eligible fully closed episodes",
                      "do not sum segment equity curves across gaps",
                      "post-gap sensitivity segments are replayed independently from flat cash",
                      "indicator warm-up", "source cases closed"):
            self.assertIn(token, contract)
        result = censored_episode_oracle([D("2.00")], D("17.00"))
        self.assertEqual(result["scored_pnl"], D("2.00"))
        self.assertEqual(result["excluded_diagnostic_pnl"], D("17.00"))

if __name__ == "__main__":
    unittest.main()
