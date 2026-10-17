import copy
import unittest

from aists_brain.paper_portfolio import (
    append_paper_fill, create_ledger, mark_to_market, verify_ledger,
)


class PaperPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.ledger = create_ledger(initial_cash_usdt=100, provenance_status="BLOCKED",
                                    fee_assumption_note="10 bps assumed, not verified")

    def test_buy_sell_cash_inventory_and_realized_pnl(self):
        ledger = append_paper_fill(self.ledger, timestamp_ms=1000, side="BUY",
                                   quantity_btc=0.001, price_usdt=20000, fee_usdt=0.02,
                                   decision_id="d1", reason="paper test only")
        self.assertAlmostEqual(ledger["cash_usdt"], 79.98)
        self.assertAlmostEqual(ledger["btc_quantity"], 0.001)
        ledger = append_paper_fill(ledger, timestamp_ms=2000, side="SELL",
                                   quantity_btc=0.001, price_usdt=21000, fee_usdt=0.021,
                                   decision_id="d2", reason="paper test exit")
        self.assertAlmostEqual(ledger["cash_usdt"], 100.959)
        self.assertAlmostEqual(ledger["realized_pnl_usdt"], 0.979)
        self.assertEqual(ledger["btc_quantity"], 0)
        self.assertEqual(ledger["sequence"], 2)

    def test_input_is_not_mutated_and_hash_chain_verifies(self):
        original = copy.deepcopy(self.ledger)
        ledger = append_paper_fill(self.ledger, timestamp_ms=1000, side="BUY",
                                   quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                                   decision_id="d1", reason="paper")
        self.assertEqual(self.ledger, original)
        self.assertEqual(verify_ledger(ledger)["status"], "PASS_HASH_CHAIN")

    def test_mark_to_market_uses_supplied_price(self):
        ledger = append_paper_fill(self.ledger, timestamp_ms=1000, side="BUY",
                                   quantity_btc=0.001, price_usdt=20000, fee_usdt=0.01,
                                   decision_id="d1", reason="paper")
        mtm = mark_to_market(ledger, mark_price_usdt=22000)
        self.assertAlmostEqual(mtm["btc_market_value_usdt"], 22)
        self.assertAlmostEqual(mtm["equity_usdt"], 101.99)
        self.assertFalse(mtm["is_verified_market_valuation"])

    def test_rejects_over_spend_and_shorting(self):
        with self.assertRaisesRegex(ValueError, "exceeds available cash"):
            append_paper_fill(self.ledger, timestamp_ms=1000, side="BUY",
                              quantity_btc=1, price_usdt=20000, fee_usdt=0,
                              decision_id="overspend", reason="test")
        with self.assertRaisesRegex(ValueError, "shorting is disabled"):
            append_paper_fill(self.ledger, timestamp_ms=1000, side="SELL",
                              quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                              decision_id="short", reason="test")

    def test_rejects_duplicate_ids_bad_time_and_tampering(self):
        ledger = append_paper_fill(self.ledger, timestamp_ms=1000, side="BUY",
                                   quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                                   decision_id="d1", reason="paper")
        with self.assertRaisesRegex(ValueError, "duplicate decision_id"):
            append_paper_fill(ledger, timestamp_ms=1001, side="BUY",
                              quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                              decision_id="d1", reason="duplicate")
        with self.assertRaisesRegex(ValueError, "non-decreasing"):
            append_paper_fill(ledger, timestamp_ms=999, side="BUY",
                              quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                              decision_id="d2", reason="bad time")
        tampered = copy.deepcopy(ledger)
        tampered["events"][0]["price_usdt"] = 21000
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_ledger(tampered)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            create_ledger(initial_cash_usdt=0)
        with self.assertRaises(ValueError):
            append_paper_fill(self.ledger, timestamp_ms=True, side="BUY",
                              quantity_btc=0.001, price_usdt=20000, fee_usdt=0,
                              decision_id="d1", reason="bad timestamp")
        with self.assertRaises(ValueError):
            mark_to_market(self.ledger, mark_price_usdt=float("nan"))


if __name__ == "__main__":
    unittest.main()
