import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0201_Gap_Quarantine_Overlap_Crosswalk.py"
SPEC = importlib.util.spec_from_file_location("cp0201_crosswalk", SCRIPT)
CROSSWALK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CROSSWALK)

class TestCP0201GapQuarantineCrosswalk(unittest.TestCase):
    def test_exact_key_normalization_is_interval_scoped(self):
        self.assertEqual(CROSSWALK.normalized_key("4h", "1504713600000"), ("4h", "1504713600000"))
        self.assertNotEqual(
            CROSSWALK.normalized_key("4h", "1504713600000"),
            CROSSWALK.normalized_key("1h", "1504713600000")
        )

    def test_existing_daily_only_case_is_linked_not_duplicated(self):
        disposition, action = CROSSWALK.classify_gap_key([
            {"ledger": "cp0040_quarantine", "case_id": "UNMATCHED-D-4h-1504713600000"}
        ])
        self.assertEqual(disposition, "OVERLAPS_EXISTING_ROW_LEVEL_CASE_DO_NOT_DUPLICATE")
        self.assertIn("do not create a duplicate", action)

    def test_absent_key_remains_gap_policy_item_not_synthetic_row(self):
        disposition, action = CROSSWALK.classify_gap_key([])
        self.assertEqual(disposition, "GAP_WINDOW_ONLY_NO_ROW_CASE_IN_INSPECTED_LEDGERS")
        self.assertIn("do not synthesize a bar", action)

    def test_crosswalk_is_append_only_recommendation_not_builder_mutation(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests.", "urlopen(", "download("):
            self.assertNotIn(forbidden, source)
        self.assertIn('"duplicate_cases_created": 0', source)
        self.assertIn('"quarantine_applied_to_candidate_builder": False', source)
        self.assertIn('"canonical_source": "NONE"', source)
        self.assertIn('"source_cases_closed": 0', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)

if __name__ == "__main__":
    unittest.main()
