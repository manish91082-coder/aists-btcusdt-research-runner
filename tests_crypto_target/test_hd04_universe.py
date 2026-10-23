import unittest

from scripts.build_hd04_universe_snapshot import eligible_symbols, digest
from scripts.probe_hd04_coingecko_source import conservative_candidate_symbol


class HD04UniverseTests(unittest.TestCase):
    def test_spot_only_includes_trading_usdt_spot_symbols(self):
        info = {"symbols": [
            {"symbol":"AAAUSDT","status":"TRADING","isSpotTradingAllowed":True,"quoteAsset":"USDT","baseAsset":"AAA"},
            {"symbol":"BBBUSDT","status":"BREAK","isSpotTradingAllowed":True,"quoteAsset":"USDT","baseAsset":"BBB"},
            {"symbol":"CCCUSDC","status":"TRADING","isSpotTradingAllowed":True,"quoteAsset":"USDC","baseAsset":"CCC"},
            {"symbol":"DDDUSDT","status":"TRADING","isSpotTradingAllowed":False,"quoteAsset":"USDT","baseAsset":"DDD"},
        ]}
        result = eligible_symbols(info, "spot")
        self.assertEqual(set(result), {"AAAUSDT"})

    def test_um_only_includes_usdt_perpetual_contracts(self):
        info = {"symbols": [
            {"symbol":"AAAUSDT","status":"TRADING","contractType":"PERPETUAL","quoteAsset":"USDT","marginAsset":"USDT","baseAsset":"AAA"},
            {"symbol":"BBBUSDT","status":"TRADING","contractType":"CURRENT_QUARTER","quoteAsset":"USDT","marginAsset":"USDT","baseAsset":"BBB"},
            {"symbol":"CCCUSDC","status":"TRADING","contractType":"PERPETUAL","quoteAsset":"USDC","marginAsset":"USDC","baseAsset":"CCC"},
            {"symbol":"DDDUSDT","status":"BREAK","contractType":"PERPETUAL","quoteAsset":"USDT","marginAsset":"USDT","baseAsset":"DDD"},
        ]}
        result = eligible_symbols(info, "um_futures")
        self.assertEqual(set(result), {"AAAUSDT"})

    def test_conservative_derivatives_symbol_mapping_preserves_ambiguity(self):
        self.assertEqual(conservative_candidate_symbol("BTCUSDT")["candidate_quote_asset"], "USDT")
        self.assertEqual(conservative_candidate_symbol("ethusdc")["candidate_symbol"], "ETHUSDC")
        self.assertIsNone(conservative_candidate_symbol("BTC/USD"))
        self.assertIsNone(conservative_candidate_symbol(None))

    def test_digest_stable_for_key_order(self):
        self.assertEqual(digest({"a":1,"b":2}), digest({"b":2,"a":1}))


if __name__ == "__main__":
    unittest.main()
