import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0200_G0_Rulebook_Bound_Gap_Disposition.py"
SPEC = importlib.util.spec_from_file_location("cp0200_g0", SCRIPT)
G0 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(G0)

class TestCP0200G0RulebookDisposition(unittest.TestCase):
    def test_zero_trade_placeholder_remains_unresolved(self):
        status, handling = G0.classify_g0_disposition(
            "NO", "YES", "DAILY_PRESENT_MONTHLY_MISSING_SOURCE_CONFLICT_ZERO_TRADE_PLACEHOLDER"
        )
        self.assertEqual(status, "UNRESOLVED_DAILY_PLACEHOLDER_CONFLICT")
        self.assertIn("DO_NOT_TREAT_AS_VALID_CANDLE", handling)

    def test_missing_from_both_sources_is_not_synthesized(self):
        status, handling = G0.classify_g0_disposition("NO", "NO", "ABSENT_FROM_BOTH_CACHED_ARCHIVES")
        self.assertEqual(status, "UNRESOLVED_MISSING_KEY_BOTH_SOURCES")
        self.assertIn("DO_NOT_SYNTHESIZE_BAR", handling)

    def test_source_conflict_is_not_resolved_by_source_preference(self):
        status, handling = G0.classify_g0_disposition(
            "NO", "YES", "DAILY_PRESENT_MONTHLY_MISSING_SOURCE_CONFLICT"
        )
        self.assertEqual(status, "UNRESOLVED_CROSS_SOURCE_EXACT_KEY_CONFLICT")
        self.assertIn("DO_NOT_SELECT_MONTHLY_OR_DAILY", handling)

    def test_unknown_archive_is_held_out_of_signal_inputs(self):
        status, handling = G0.classify_g0_disposition("UNKNOWN", "UNKNOWN", "UNRESOLVED_ARCHIVE")
        self.assertEqual(status, "UNRESOLVED_ARCHIVE_EVIDENCE_UNAVAILABLE")
        self.assertIn("HOLD_FROM_SIGNAL_POSITION_VALUATION", handling)

    def test_frozen_rulebook_identity_is_pinned_and_no_live_path_exists(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(G0.EXPECTED_RULEBOOK_SHA256, "5ecba19d303d9065f26121f53894b8d4732054155e0d40b87db188e49d8b99e0")
        self.assertEqual(G0.EXPECTED_RULEBOOK_BYTES, 10630)
        for forbidden in ("urllib", "requests.", "urlopen(", "download("):
            self.assertNotIn(forbidden, source)
        self.assertIn('"canonical_source": "NONE"', source)
        self.assertIn('"source_cases_closed": 0', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)

if __name__ == "__main__":
    unittest.main()
