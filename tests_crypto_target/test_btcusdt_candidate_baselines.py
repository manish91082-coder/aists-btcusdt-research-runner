import unittest

from scripts.backtest_btcusdt_candidate_baselines import desired_positions, run, simulate


class CandidateBaselineTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"timestamp_ms": i * 300000, "open": 100.0 + i * 0.1,
             "close": 100.05 + i * 0.1}
            for i in range(80)
        ]

    def test_candidate_names_and_report_are_deterministic(self):
        report, curves = run(self.rows, 1000.0, 10.0, 2.0, 5.0)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["benchmark_only"])
        self.assertEqual(set(curves), {"trend_sma_12_48", "mean_reversion_z48"})
        for name in curves:
            self.assertEqual(len(curves[name]), len(self.rows))
            self.assertTrue(report[name]["final_equity_after_final_liquidation"] >= 0)
            self.assertTrue(report[name]["total_fees_quote"] >= 0)

    def test_signals_only_use_available_prefix(self):
        closes = [100.0 + i for i in range(80)]
        original = desired_positions(closes)
        changed_future = closes[:60] + [c * 10 for c in closes[60:]]
        changed = desired_positions(changed_future)
        # Decisions formed through candle 59 must not depend on later candles.
        for name in original:
            self.assertEqual(original[name][:60], changed[name][:60])

    def test_zero_costs_do_not_charge_fees(self):
        report, _ = run(self.rows, 1000.0, 0.0, 0.0, 0.0)
        for name in ("trend_sma_12_48", "mean_reversion_z48"):
            self.assertEqual(report[name]["total_fees_quote"], 0.0)

    def test_invalid_prices_rejected(self):
        bad = [dict(row) for row in self.rows]
        bad[4]["close"] = float("nan")
        with self.assertRaises(ValueError):
            run(bad, 1000.0, 10.0, 2.0, 5.0)


if __name__ == "__main__":
    unittest.main()
