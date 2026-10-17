import unittest

from aists_brain.market_context import TIMEFRAMES, analyze_market_context


def candles_from_closes(closes, *, volume=100.0):
    rows = []
    for i, close in enumerate(closes):
        rows.append({
            "open_time_ms": i * 300_000,
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": volume if i < len(closes) - 1 else volume * 2,
        })
    return rows


class MarketContextTests(unittest.TestCase):
    def test_all_eight_timeframes_are_declared(self):
        self.assertEqual(TIMEFRAMES, ("5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"))

    def test_insufficient_history_does_not_fake_indicators(self):
        result = analyze_market_context(candles_from_closes([100, 101, 102]), "5m")
        self.assertIsNone(result["ema20"])
        self.assertIsNone(result["rsi14"])
        self.assertEqual(result["trend_state"], "INSUFFICIENT_HISTORY")
        self.assertEqual(result["data_status"], "LIMITED_HISTORY")

    def test_uptrend_context_and_prior_zones(self):
        closes = [100 + i for i in range(60)]
        rows = candles_from_closes(closes)
        result = analyze_market_context(rows, "4h")
        self.assertEqual(result["trend_state"], "BULLISH")
        self.assertEqual(result["prior_resistance"], max(r["high"] for r in rows[-21:-1]))
        self.assertEqual(result["prior_support"], min(r["low"] for r in rows[-21:-1]))
        self.assertAlmostEqual(result["volume_ratio_vs_prior_median"], 2.0)
        self.assertEqual(result["data_status"], "READY")

    def test_rejects_non_monotonic_timestamps(self):
        rows = candles_from_closes([100, 101, 102])
        rows[2]["open_time_ms"] = rows[1]["open_time_ms"]
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            analyze_market_context(rows, "5m")

    def test_rejects_invalid_ohlc(self):
        rows = candles_from_closes([100, 101, 102])
        rows[1]["low"] = 500
        with self.assertRaisesRegex(ValueError, "invalid OHLC"):
            analyze_market_context(rows, "5m")

    def test_rejects_zero_or_negative_ohlc_prices(self):
        for field in ("open", "high", "low", "close"):
            for invalid_price in (0.0, -1.0):
                with self.subTest(field=field, invalid_price=invalid_price):
                    rows = candles_from_closes([100, 101, 102])
                    rows[1][field] = invalid_price
                    with self.assertRaisesRegex(ValueError, "OHLC prices must be strictly positive"):
                        analyze_market_context(rows, "5m")

    def test_rejects_unknown_timeframe(self):
        with self.assertRaisesRegex(ValueError, "unsupported timeframe"):
            analyze_market_context(candles_from_closes([100]), "2h")

    def test_does_not_mutate_input(self):
        rows = candles_from_closes([100 + i for i in range(60)])
        before = [dict(row) for row in rows]
        analyze_market_context(rows, "1d")
        self.assertEqual(rows, before)


if __name__ == "__main__":
    unittest.main()
