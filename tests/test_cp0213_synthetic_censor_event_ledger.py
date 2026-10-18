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



def validate_exact_population(candidate_keys, expected_keys):
    """Fail closed on missing, duplicate, altered, or extra exact keys."""
    if len(candidate_keys) != len(set(candidate_keys)):
        raise ValueError("duplicate exact key")
    if set(candidate_keys) != set(expected_keys) or len(candidate_keys) != len(expected_keys):
        raise ValueError("exact-key population mismatch")
    return True


def unscorable_full_window_result():
    """Do not publish numeric risk metrics where the path is unobservable."""
    return {
        "status": "BLOCKED_GAP_VALUATION_UNSCORABLE",
        "scored_return": None,
        "scored_equity": None,
        "scored_max_drawdown": None,
    }


def independent_event_ledger():
    """Small independent Decimal event ledger including a mark and fee accounting."""
    cash = D("1000")
    qty = D("0")
    fee_rate = D("0.001")
    events = []

    buy_gross = D("200") * D("2")
    buy_fee = buy_gross * fee_rate
    cash -= buy_gross + buy_fee
    qty += D("2")
    events.append({"event": "BUY_FILL", "cash": cash, "qty": qty, "fee": buy_fee})

    mark_price = D("210")
    equity_at_mark = cash + qty * mark_price
    events.append({"event": "BAR_CLOSE_MARK", "cash": cash, "qty": qty,
                   "mark_price": mark_price, "equity": equity_at_mark})

    sell_gross = qty * D("190")
    sell_fee = sell_gross * fee_rate
    cash += sell_gross - sell_fee
    qty -= D("2")
    events.append({"event": "SELL_FILL", "cash": cash, "qty": qty, "fee": sell_fee})

    return {
        "events": events,
        "final_cash": cash,
        "final_qty": qty,
        "total_fees": buy_fee + sell_fee,
        "realized_net_pnl": cash - D("1000"),
    }

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

    def test_event_level_decimal_ledger_reconciles_cash_quantity_fees_and_equity(self):
        result = independent_event_ledger()
        events = result["events"]
        self.assertEqual([e["event"] for e in events], ["BUY_FILL", "BAR_CLOSE_MARK", "SELL_FILL"])
        self.assertEqual(events[0]["cash"], D("599.600"))
        self.assertEqual(events[0]["qty"], D("2"))
        self.assertEqual(events[1]["equity"], D("1019.600"))
        self.assertEqual(events[2]["cash"], D("979.220"))
        self.assertEqual(result["final_qty"], D("0"))
        self.assertEqual(result["total_fees"], D("0.780"))
        self.assertEqual(result["realized_net_pnl"], D("-20.780"))
        # Independent conservation identity: start cash + net P&L = ending cash.
        self.assertLessEqual(abs(D("1000") + result["realized_net_pnl"] - result["final_cash"]), TOL)

    def test_full_window_risk_metrics_are_null_when_unscorable(self):
        result = unscorable_full_window_result()
        self.assertEqual(result["status"], "BLOCKED_GAP_VALUATION_UNSCORABLE")
        self.assertIsNone(result["scored_return"])
        self.assertIsNone(result["scored_equity"])
        self.assertIsNone(result["scored_max_drawdown"])

    def test_exact_population_validator_rejects_missing_duplicate_and_extra_keys(self):
        expected = ["k1", "k2", "k3"]
        self.assertTrue(validate_exact_population(["k3", "k1", "k2"], expected))
        for candidate in (["k1", "k2"], ["k1", "k2", "k2"], ["k1", "k2", "k4"]):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    validate_exact_population(candidate, expected)

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
