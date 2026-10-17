import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKTEST = ROOT / "scripts" / "AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"


class TestCP0204BacktestGapGate(unittest.TestCase):
    def test_gap_gate_runs_before_manifest_or_output_creation(self):
        source = BACKTEST.read_text(encoding="utf-8")
        gate = source.index("load_gap_policy_gate(")
        manifest = source.index('manifest_path=report_dir/"cp0026_research_candidate_manifest.json"')
        output_creation = source.index("result_dir.mkdir")
        candidate_load = source.index("load_candidate(root,interval,manifest)")
        self.assertLess(gate, manifest)
        self.assertLess(gate, output_creation)
        self.assertLess(gate, candidate_load)

    def test_gap_valuation_behavior_is_explicitly_identified_as_unresolved(self):
        source = BACKTEST.read_text(encoding="utf-8")
        self.assertIn("existing spot exposure is carried through gaps and marked at the next observed prices.", source.lower())
        self.assertIn("current_equity=cash+qty*cl[i]", source)
        self.assertIn("if i+1>=end_idx or not contiguous[i+1]:", source)
        self.assertIn("load_gap_policy_gate(", source)

    def test_gate_precedes_any_performance_computation(self):
        source = BACKTEST.read_text(encoding="utf-8")
        gate = source.index("load_gap_policy_gate(")
        metrics = source.index("def metrics_from_equity")
        main = source.index("def main():")
        self.assertLess(metrics, main)
        self.assertLess(gate, source.index("for interval in INTERVALS:", main))

    def test_backtest_remains_offline_and_no_order_path_is_added(self):
        source = BACKTEST.read_text(encoding="utf-8")
        for forbidden in ("api.binance.com/api/", "create_order(", "new_order(", "signed_request("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
