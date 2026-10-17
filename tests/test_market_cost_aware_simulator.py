import unittest

from aists_brain.cost_aware_simulator import simulate_next_open


def bars(prices, interval_ms=1000, opens=None):
    opens = opens or [i * interval_ms for i in range(len(prices))]
    return [
        {
            "open_time_ms": open_ms,
            "close_time_ms": open_ms + interval_ms - 1,
            "open": prices[i],
            "close": prices[i],
        }
        for i, open_ms in enumerate(opens)
    ]


class CostAwareSimulatorTests(unittest.TestCase):
    def test_next_open_fill_models_fees_and_slippage(self):
        candles = bars([100, 110, 120, 130])
        result = simulate_next_open(
            candles,
            [
                {"decision_id": "buy-1", "as_of_ms": 999, "action": "BUY_CANDIDATE"},
                {"decision_id": "sell-1", "as_of_ms": 1999, "action": "SELL_CANDIDATE"},
            ],
            interval_ms=1000,
            initial_cash_usdt=1000,
            allocation_fraction=0.5,
            fee_bps_per_side=10,
            slippage_bps_per_side=5,
        )
        self.assertEqual(result["status"], "SIMULATED_NOT_VALIDATED")
        self.assertEqual(result["event_count"], 2)
        self.assertEqual(result["closed_round_trip_count"], 1)
        self.assertEqual(result["events"][0]["fill_open_time_ms"], 1000)
        self.assertEqual(result["events"][1]["fill_open_time_ms"], 2000)
        self.assertGreater(result["events"][1]["fill_price_usdt"], 0)
        self.assertAlmostEqual(result["events"][0]["fill_price_usdt"], 110 * 1.0005)
        self.assertAlmostEqual(result["events"][1]["fill_price_usdt"], 120 * 0.9995)
        self.assertFalse(result["events"][0]["is_order_instruction"])
        self.assertFalse(result["events"][1]["is_order_instruction"])

    def test_gap_does_not_get_filled_by_later_bar(self):
        candles = bars([100, 130], opens=[0, 2000])
        result = simulate_next_open(
            candles,
            [{"decision_id": "buy-gap", "as_of_ms": 999, "action": "BUY_CANDIDATE"}],
            interval_ms=1000,
            initial_cash_usdt=1000,
        )
        self.assertEqual(result["event_count"], 0)
        self.assertEqual(result["skipped_decisions"][0]["reason"], "NO_NEXT_CONTIGUOUS_BAR")

    def test_no_trade_and_no_automatic_stop_or_take_profit(self):
        result = simulate_next_open(
            bars([100, 80, 120]),
            [{"decision_id": "hold", "as_of_ms": 999, "action": "NO_TRADE"}],
            interval_ms=1000,
            initial_cash_usdt=1000,
        )
        self.assertEqual(result["event_count"], 0)
        self.assertEqual(result["closed_round_trip_count"], 0)
        self.assertTrue(any("no automatic stop-loss/take-profit" in item for item in result["limitations"]))

    def test_buy_without_exit_remains_open_and_marks_exit_costs(self):
        result = simulate_next_open(
            bars([100, 110, 120]),
            [{"decision_id": "buy", "as_of_ms": 999, "action": "BUY_CANDIDATE"}],
            interval_ms=1000,
            initial_cash_usdt=1000,
            allocation_fraction=0.25,
            fee_bps_per_side=10,
            slippage_bps_per_side=5,
        )
        self.assertEqual(result["event_count"], 1)
        self.assertEqual(result["closed_round_trip_count"], 0)
        self.assertGreater(result["btc_quantity"], 0)
        self.assertIn("estimated_exit_costs", result.keys().__str__())

    def test_rejects_decision_that_does_not_reference_candle_close(self):
        with self.assertRaisesRegex(ValueError, "reference a supplied candle close"):
            simulate_next_open(
                bars([100, 110]),
                [{"decision_id": "bad", "as_of_ms": 1000, "action": "BUY_CANDIDATE"}],
                interval_ms=1000,
                initial_cash_usdt=1000,
            )

    def test_rejects_duplicate_decision_ids_and_invalid_costs(self):
        candles = bars([100, 110, 120])
        duplicate = [
            {"decision_id": "same", "as_of_ms": 999, "action": "NO_TRADE"},
            {"decision_id": "same", "as_of_ms": 1999, "action": "NO_TRADE"},
        ]
        with self.assertRaisesRegex(ValueError, "unique"):
            simulate_next_open(candles, duplicate, interval_ms=1000, initial_cash_usdt=1000)
        with self.assertRaisesRegex(ValueError, "allocation_fraction"):
            simulate_next_open(candles, [], interval_ms=1000, initial_cash_usdt=1000, allocation_fraction=1.1)

    def test_rejects_nonmonotonic_candles(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            simulate_next_open(
                bars([100, 110], opens=[1000, 0]),
                [],
                interval_ms=1000,
                initial_cash_usdt=1000,
            )


if __name__ == "__main__":
    unittest.main()
