import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_btcusdt_spot_aggtrades_in_gaps.py"
SPEC = importlib.util.spec_from_file_location("aggtrade_gap_audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class TestAggTradesGapAudit(unittest.TestCase):
    def test_half_open_interval_includes_start_excludes_end(self):
        start, end = 1_000, 2_000
        self.assertTrue(AUDIT.in_half_open_interval(start, start, end))
        self.assertTrue(AUDIT.in_half_open_interval(end - 1, start, end))
        self.assertFalse(AUDIT.in_half_open_interval(end, start, end))
        self.assertFalse(AUDIT.in_half_open_interval(start - 1, start, end))

    def test_all_configured_gaps_have_positive_duration(self):
        total = 0
        for month, windows in AUDIT.GAPS.items():
            self.assertIn(month, AUDIT.MONTHS)
            for start_text, end_text in windows:
                start, end = AUDIT.ms(start_text), AUDIT.ms(end_text)
                self.assertLess(start, end, f"{month}: {start_text} -> {end_text}")
                total += 1
        self.assertEqual(total, 15)

    def test_gap_boundaries_are_utc_and_millisecond_aligned(self):
        for windows in AUDIT.GAPS.values():
            for start_text, end_text in windows:
                for value in (start_text, end_text):
                    timestamp = AUDIT.ms(value)
                    rendered = AUDIT.datetime.fromtimestamp(
                        timestamp / 1000, AUDIT.timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%SZ")
                    self.assertEqual(rendered, value)


if __name__ == "__main__":
    unittest.main()
