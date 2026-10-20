import copy
import tempfile
import unittest
from pathlib import Path

from aists_brain.paper_portfolio import (
    append_ledger_jsonl,
    append_paper_fill,
    build_decision_context,
    create_ledger,
    load_ledger_jsonl,
    verify_ledger,
)


CANDIDATE = {
    "status": "RESEARCH_CANDIDATE_ONLY",
    "selected_action": "LONG_CANDIDATE",
    "selected_strategy": "TREND_FOLLOWING",
    "confirming_timeframes": ["5m", "15m", "30m"],
    "is_order_instruction": False,
}


class PaperPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.ledger = create_ledger(
            initial_cash_usdt=100,
            provenance_status="BLOCKED",
            fee_assumption_note="10 bps assumed, not verified",
        )
        self.context = build_decision_context(
            CANDIDATE,
            brain_version="cp0129-test",
            snapshot_sha256="a" * 64,
            as_of_ms=1000,
        )

    def add_buy(self, ledger, decision_id="d1", timestamp_ms=1001):
        return append_paper_fill(
            ledger,
            timestamp_ms=timestamp_ms,
            side="BUY",
            quantity_btc=0.001,
            price_usdt=20000,
            fee_usdt=0.02,
            decision_id=decision_id,
            reason="hypothetical paper fill only",
            decision_context=self.context,
        )

    def test_decision_context_binds_candidate_and_snapshot(self):
        context = self.context
        self.assertEqual(context["brain_version"], "cp0129-test")
        self.assertEqual(context["snapshot_sha256"], "a" * 64)
        self.assertEqual(context["as_of_ms"], 1000)
        with self.assertRaisesRegex(ValueError, "requires a RESEARCH_CANDIDATE_ONLY"):
            build_decision_context(
                {"status": "NO_TRADE", "selected_action": "NO_TRADE"},
                brain_version="v1",
                snapshot_sha256="a" * 64,
                as_of_ms=1000,
            )
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            build_decision_context(
                CANDIDATE, brain_version="v1", snapshot_sha256="bad", as_of_ms=1000
            )

    def test_fill_contains_decision_binding_and_verifies(self):
        ledger = self.add_buy(self.ledger)
        event = ledger["events"][0]
        self.assertEqual(event["decision_context"], self.context)
        self.assertEqual(verify_ledger(ledger)["status"], "PASS_HASH_CHAIN")

    def test_jsonl_persists_reloads_and_is_idempotent(self):
        ledger = self.add_buy(self.ledger)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper-ledger.jsonl"
            first = append_ledger_jsonl(path, ledger)
            self.assertEqual(first["new_events_appended"], 1)
            self.assertEqual(first["status"], "PASS_DURABLE_JSONL_HASH_CHAIN")
            loaded = load_ledger_jsonl(path)
            self.assertEqual(loaded, ledger)
            second = append_ledger_jsonl(path, ledger)
            self.assertEqual(second["new_events_appended"], 0)
            self.assertEqual(load_ledger_jsonl(path), ledger)

    def test_appends_only_new_suffix_and_rejects_rollback(self):
        first = self.add_buy(self.ledger)
        second = append_paper_fill(
            first, timestamp_ms=2000, side="SELL", quantity_btc=0.001,
            price_usdt=21000, fee_usdt=0.021, decision_id="d2",
            reason="hypothetical paper exit only",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper-ledger.jsonl"
            append_ledger_jsonl(path, first)
            result = append_ledger_jsonl(path, second)
            self.assertEqual(result["new_events_appended"], 1)
            self.assertEqual(load_ledger_jsonl(path), second)
            with self.assertRaisesRegex(ValueError, "rollback"):
                append_ledger_jsonl(path, first)

    def test_tampering_and_truncated_lines_are_rejected(self):
        ledger = self.add_buy(self.ledger)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper-ledger.jsonl"
            append_ledger_jsonl(path, ledger)
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace('"price_usdt":20000.0', '"price_usdt":20001.0'), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_ledger_jsonl(path)
            path.write_text(original + '{"record_type":"event"', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "truncated"):
                load_ledger_jsonl(path)

    def test_input_ledger_is_not_mutated(self):
        original = copy.deepcopy(self.ledger)
        self.add_buy(self.ledger)
        self.assertEqual(self.ledger, original)


if __name__ == "__main__":
    unittest.main()
