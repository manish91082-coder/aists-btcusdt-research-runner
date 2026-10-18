"""CP-0213 synthetic censor-event ledger oracle.

Independent in-memory fixture only. This does not exercise or authorize the
production Policy B scorer; no market data, candidate build, or backtest.
"""
from decimal import Decimal, getcontext
from pathlib import Path
import json
import unittest

getcontext().prec = 40
D = Decimal
TOL = D("1e-8")
ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json"
CONTRACT = ROOT / "docs/CP0210_Segment_Censor_Accounting_Contract.md"
BACKTEST = ROOT / "scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"
GATE = ROOT / "scripts/AISTS_CP0203_GapPolicy_Gate.py"


def buy(cash, price, quantity, fee_rate):
    gross = price * quantity
    fee = gross * fee_rate
    return cash - gross - fee, quantity, fee


def sell(cash, quantity, price, fee_rate):
    gross = quantity * price
    fee = gross * fee_rate
    return cash + gross - fee, fee


def independent_censor_fixture():
    """A single held episode crosses a gap; later close remains diagnostic only."""
    initial_cash = D("1000")
    fee_rate = D("0.001")
    buy_price, quantity, later_sale_price = D("100"), D("5"), D("90")
    cash_after_buy, held_qty, buy_fee = buy(initial_cash, buy_price, quantity, fee_rate)

    # CENSOR_GAP is a state/accounting classification, never a fill.
    censor = {
        "event": "CENSOR_GAP_EXPOSED",
        "synthetic_candle_count": 0,
        "fill_count": 0,
        "exit_price": None,
        "position_qty_at_censor": held_qty,
    }

    # Keep the historical episode in a diagnostic-only ledger. This later sale
    # is an observed event in the synthetic fixture, not an invented boundary fill.
    diagnostic_cash, sell_fee = sell(cash_after_buy, held_qty, later_sale_price, fee_rate)
    diagnostic_pnl = diagnostic_cash - initial_cash
    scored_pnl = D("0")  # no eligible fully closed scored episode in this fixture

    # Separate post-gap sensitivity replay starts independently, not with held_qty.
    post_gap = {
        "cash": initial_cash,
        "quantity": D("0"),
        "pending_signal": None,
        "indicator_state": {},
        "warmup_observations": 0,
    }
    return {
        "initial_cash": initial_cash,
        "cash_after_buy": cash_after_buy,
        "held_qty": held_qty,
        "buy_fee": buy_fee,
        "sell_fee": sell_fee,
        "censor": censor,
        "diagnostic_cash": diagnostic_cash,
        "diagnostic_pnl": diagnostic_pnl,
        "scored_pnl": scored_pnl,
        "post_gap": post_gap,
        "full_window_status": "BLOCKED_GAP_VALUATION_UNSCORABLE",
    }


def group_adjacent_missing_slots(open_times_ms, step_ms=14_400_000):
    """Group adjacent missing 4h keys without dropping or rewriting exact keys."""
    ordered = sorted(set(open_times_ms))
    if len(ordered) != len(open_times_ms):
        raise ValueError("duplicate exact missing key")
    groups = []
    for key in ordered:
        if not groups or key != groups[-1][-1] + step_ms:
            groups.append([key])
        else:
            groups[-1].append(key)
    return groups


class TestCP0213SyntheticCensorEventLedger(unittest.TestCase):
    def test_gap_censor_has_no_fabricated_boundary_fill(self):
        result = independent_censor_fixture()
        self.assertEqual(result["censor"]["event"], "CENSOR_GAP_EXPOSED")
        self.assertEqual(result["censor"]["synthetic_candle_count"], 0)
        self.assertEqual(result["censor"]["fill_count"], 0)
        self.assertIsNone(result["censor"]["exit_price"])
        self.assertEqual(result["censor"]["position_qty_at_censor"], D("5"))

    def test_later_sale_is_diagnostic_not_scored(self):
        result = independent_censor_fixture()
        self.assertEqual(result["diagnostic_cash"], D("949.050"))
        self.assertEqual(result["diagnostic_pnl"], D("-50.950"))
        self.assertEqual(result["scored_pnl"], D("0"))
        self.assertNotEqual(result["diagnostic_pnl"], result["scored_pnl"])
        self.assertEqual(result["full_window_status"], "BLOCKED_GAP_VALUATION_UNSCORABLE")
        # Event-level cash/quantity/fee arithmetic reconciles independently.
        expected_cash = D("1000") - D("500") - D("0.500") + D("450") - D("0.450")
        self.assertLessEqual(abs(result["diagnostic_cash"] - expected_cash), TOL)
        self.assertEqual(result["held_qty"], D("5"))
        self.assertEqual(result["buy_fee"] + result["sell_fee"], D("0.950"))

    def test_post_gap_replay_has_no_inherited_state_and_requires_warmup(self):
        state = independent_censor_fixture()["post_gap"]
        self.assertEqual(state["cash"], D("1000"))
        self.assertEqual(state["quantity"], D("0"))
        self.assertIsNone(state["pending_signal"])
        self.assertEqual(state["indicator_state"], {})
        self.assertEqual(state["warmup_observations"], 0)

    def test_adjacent_missing_keys_group_without_losing_exact_identity(self):
        step = 14_400_000
        keys = [0, step, 3 * step, 4 * step, 7 * step]
        groups = group_adjacent_missing_slots(keys, step)
        self.assertEqual(groups, [[0, step], [3 * step, 4 * step], [7 * step]])
        self.assertEqual(sorted(k for group in groups for k in group), sorted(keys))
        with self.assertRaises(ValueError):
            group_adjacent_missing_slots([0, 0], step)

    def test_frozen_population_identity_and_fail_closed_guards_remain(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        keys = policy["expected_missing_slots"]
        self.assertEqual(len(keys), 17)
        self.assertEqual(len({item["open_time_ms"] for item in keys}), 17)
        self.assertEqual(sum(item["classification"].startswith("EXISTING_ROW_CASE_OVERLAP") for item in keys), 1)
        self.assertEqual(sum(item["classification"] == "GAP_WINDOW_ONLY" for item in keys), 16)
        self.assertEqual(policy["status"], "FROZEN_FOR_SENSITIVITY_ONLY_NOT_G0_CLEARANCE")
        self.assertFalse(policy["explicit_non_effects"]["backtest_authorized"])
        self.assertFalse(policy["explicit_non_effects"]["quarantine_applied_to_candidate_builder"])
        self.assertEqual(policy["scope"]["canonical_source"], "NONE")
        self.assertEqual(policy["scope"]["g0"], "BLOCKED_GLOBAL")
        gate = GATE.read_text(encoding="utf-8")
        self.assertIn("G0_BLOCKED_GAP_POLICY_UNRESOLVED", gate)
        source = BACKTEST.read_text(encoding="utf-8")
        main = source[source.index("def main():"):]
        self.assertLess(main.index("load_gap_policy_gate("), main.index("load_candidate_gate("))
        contract = CONTRACT.read_text(encoding="utf-8").lower()
        self.assertIn("blocked_gap_valuation_unscorable", contract)
        self.assertIn("post-gap sensitivity segments are replayed independently from flat cash", contract)


if __name__ == "__main__":
    unittest.main()
