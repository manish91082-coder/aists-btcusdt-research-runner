"""CP-0209: synthetic gap-boundary verification.

All candles are in-memory fixtures. These tests never call main(), load market
archives, build candidates, or run a market-data backtest. The simulator's
carry-through-gap behavior is explicitly treated as diagnostic-only; this
checkpoint does not apply Policy B to production scoring.
"""
import json
from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from AISTS_CP0027_MultiTimeframe_Baseline_Backtest import simulate_strategy

POLICY_PATH = ROOT / "evidence/source_adjudication/CP0206_Gap_Window_Quarantine_Policy.json"
TIMES = [0, 14_400_000, 43_200_000, 57_600_000]


def make_frame(contiguous, fast, slow):
    opens = [100.0, 101.0, 102.0, 103.0]
    closes = [100.0, 101.0, 102.0, 103.0]
    return pd.DataFrame({
        "open_time_ms": TIMES, "open": opens,
        "high": [p + 1 for p in opens], "low": [p - 1 for p in opens],
        "close": closes, "volume": [1.0] * 4,
        "ema_fast": fast, "ema_slow": slow,
        "rsi14": [50.0] * 4,
        "prior_high20": [float("nan")] * 4,
        "prior_low10": [float("nan")] * 4,
        "contiguous": contiguous,
    })


class TestCP0209GapBoundaryVerification(unittest.TestCase):
    def test_boundary_row_cannot_create_signal_filled_after_gap(self):
        # Row 2 is the first observed row after a missing 4h slot. Deliberately
        # supply finite bullish values there to prove the simulator rejects
        # the boundary row itself as a signal origin.
        frame = make_frame(
            [False, True, False, True],
            [2.0, 1.0, 9.0, 1.0],
            [1.0, 2.0, 2.0, 2.0],
        )
        result = simulate_strategy(frame, "4h", 0, 4, "EMA_12_26", 10.0, 5.0,
                                   trade_log=True, ledger_log=True)
        self.assertEqual(result["buy_fills"], 0)
        self.assertEqual(result["sell_fills"], 0)
        self.assertEqual(result["trade_log"], [])
        self.assertFalse(any(e["event"] == "BUY_FILL" for e in result["ledger_log"]))

    def test_gap_exposed_position_is_not_misrepresented_as_policy_b_scoring(self):
        # Start inside an already-contiguous segment so a position can exist
        # before the gap. The production simulator still carries it through
        # the gap and liquidates at window end: this is diagnostic behavior,
        # NOT Policy B censoring and therefore not eligible for risk acceptance.
        frame = make_frame(
            [True, True, False, True],
            [2.0, 2.0, 1.0, 1.0],
            [1.0, 1.0, 2.0, 2.0],
        )
        result = simulate_strategy(frame, "4h", 0, 4, "EMA_12_26", 10.0, 5.0,
                                   trade_log=True, ledger_log=True)
        self.assertEqual(result["buy_fills"], 1)
        self.assertEqual(result["sell_fills"], 1)
        self.assertEqual(result["trade_log"][-1]["exit_type"], "window_end_liquidation")

        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "FROZEN_FOR_SENSITIVITY_ONLY_NOT_G0_CLEARANCE")
        rules = policy["policy_b"]["rules"]
        self.assertTrue(any("CENSORED_GAP_EXPOSED" in rule and "exclude it from scored metrics" in rule
                            for rule in rules))
        self.assertFalse(policy["explicit_non_effects"]["backtest_authorized"])
        self.assertFalse(policy["explicit_non_effects"]["quarantine_applied_to_candidate_builder"])

    def test_gap_boundary_source_guard_remains_fail_closed(self):
        source = (ROOT / "scripts/AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py").read_text(encoding="utf-8")
        main_body = source[source.index("def main():"):]
        self.assertIn("load_gap_policy_gate", main_body)
        self.assertIn("load_candidate_gate", main_body)
        self.assertLess(main_body.index("load_gap_policy_gate"), main_body.index("load_candidate_gate"))


if __name__ == "__main__":
    unittest.main()
