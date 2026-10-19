import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0197_Feb2018_DailyReference_Evidence_Linkage.py"
SPEC = importlib.util.spec_from_file_location("cp0197_linkage", SCRIPT)
LINKAGE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(LINKAGE)

class TestCP0197EvidenceLinkage(unittest.TestCase):
    def test_epoch_units_normalize_without_timestamp_shift(self):
        self.assertEqual(LINKAGE.normalize_ms_to_us(1518170400000), 1518170400000000)
        self.assertEqual(LINKAGE.normalize_ms_to_us(1735689600000000), 1735689600000000)
        with self.assertRaises(ValueError):
            LINKAGE.normalize_ms_to_us(12345)

    def test_linkage_is_existing_evidence_only(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("urllib", "requests.", "urlopen(", "download("):
            self.assertNotIn(forbidden, source)
        self.assertIn("prior_evidence_hash_checks", source)
        self.assertIn("canonical_source", source)
        self.assertIn('"source_cases_closed": 0', source)
        self.assertIn('"network_used": False', source)
        self.assertIn('"downloads": 0', source)
        self.assertIn('"live_signing_broadcast_orders": "BLOCKED"', source)

    def test_february_slots_are_classified_without_canonical_promotion(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("UNRESOLVED_NO_PRIOR_DAILY_REFERENCE_FOR_DATE", source)
        self.assertIn("DAILY_REFERENCE_DOES_NOT_COVER_TARGET_WINDOW", source)
        self.assertIn("OUTSIDE_CP0107_DAILY_EVIDENCE_SCOPE", source)
        self.assertIn('"canonical_source": "NONE"', source)

if __name__ == "__main__":
    unittest.main()
