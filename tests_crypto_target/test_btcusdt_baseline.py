import importlib.util
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import backtest_btcusdt_baseline as BASE


class TestBtcusdtBaseline(unittest.TestCase):
    def test_flat_benchmark_has_zero_return_and_no_trades(self):
        report, curve = BASE.run_benchmarks(
            [{"timestamp_ms": 1, "open": 100.0, "close": 110.0}],
            1000.0, 10.0, 4.0, 2.0)
        flat = report["benchmarks"]["flat_no_trade"]
        self.assertEqual(flat["final_equity"], 1000.0)
        self.assertEqual(flat["net_return_pct"], 0.0)
        self.assertEqual(flat["trades"], 0)
        self.assertEqual(float(curve[0]["flat_equity"]), 1000.0)

    def test_buy_hold_accounts_for_entry_exit_costs(self):
        rows = [{"timestamp_ms": 1, "open": 100.0, "close": 100.0},
                {"timestamp_ms": 2, "open": 100.0, "close": 110.0}]
        report, _ = BASE.run_benchmarks(rows, 1000.0, 10.0, 4.0, 2.0)
        bh = report["benchmarks"]["spot_buy_and_hold"]
        self.assertLess(bh["final_equity_after_entry_and_exit_costs"], 1100.0)
        self.assertGreater(bh["entry_fee_quote"], 0)
        self.assertGreater(bh["exit_fee_quote"], 0)
        self.assertLess(bh["net_return_pct"], bh["gross_return_pct_before_costs"])

    def test_drawdown_is_negative_for_peak_to_trough(self):
        self.assertAlmostEqual(BASE.max_drawdown([100.0, 120.0, 90.0]), -0.25)

    def test_input_rejects_duplicate_or_unsorted_timestamps(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            BASE.run_benchmarks([
                {"timestamp_ms": 2, "open": 100.0, "close": 100.0},
                {"timestamp_ms": 2, "open": 100.0, "close": 101.0}],
                1000.0, 10.0, 4.0, 2.0)

    def test_input_file_rejects_nonpositive_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("open_time_ms,spot_open,spot_close\n1,0,100\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "finite and positive"):
                BASE.load_spot_rows(path)

    def test_cost_assumptions_must_be_explicitly_valid(self):
        with self.assertRaisesRegex(ValueError, "fee_bps"):
            BASE.run_benchmarks([{"timestamp_ms": 1, "open": 100.0, "close": 100.0}],
                                1000.0, -1.0, 4.0, 2.0)


if __name__ == "__main__":
    unittest.main()
