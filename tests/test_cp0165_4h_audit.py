import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0165_4H_Monthly_Checksum_Gap_Audit.py"
SPEC = importlib.util.spec_from_file_location("cp0165_audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(AUDIT)

class TestCP0165AuditHelpers(unittest.TestCase):
    def test_expected_month_scope_is_exactly_110(self):
        months = list(AUDIT.expected_periods())
        self.assertEqual(len(months), 110)
        self.assertEqual(months[0], "2017-08")
        self.assertEqual(months[-1], "2026-09")
        self.assertEqual(len(set(months)), 110)

    def test_checksum_parser_requires_hash_and_archive_name(self):
        digest = "a" * 64
        hashes, named = AUDIT.parse_checksum(f"{digest}  BTCUSDT-4h-2017-08.zip", "BTCUSDT-4h-2017-08.zip")
        self.assertEqual(hashes, [digest])
        self.assertTrue(named)

    def test_checksum_parser_does_not_invent_missing_hash(self):
        hashes, named = AUDIT.parse_checksum("missing hash for BTCUSDT-4h-2017-08.zip", "BTCUSDT-4h-2017-08.zip")
        self.assertEqual(hashes, [])
        self.assertTrue(named)


    def test_runner_and_workflow_wiring_are_bounded(self):
        root = Path(__file__).resolve().parents[1]
        runner = (root / "scripts" / "aists_runner.py").read_text(encoding="utf-8")
        workflow = (root / ".github" / "workflows" / "python-runner.yml").read_text(encoding="utf-8")
        self.assertIn('"cp0165_4h_monthly_checksum_gap_audit"', runner)
        self.assertIn('"cp0118_monthly_parent_child_internal_rollup_audit","cp0165_4h_monthly_checksum_gap_audit"):', runner)
        self.assertIn('"cp0165_4h_monthly_checksum_gap_audit":"AISTS_CP0165_4H_Monthly_Checksum_Gap_Audit.py"', runner)
        self.assertIn('elif task=="cp0165_4h_monthly_checksum_gap_audit":', runner)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("- cp0165_4h_monthly_checksum_gap_audit", workflow)
        self.assertIn("publish_cp0165_4h_monthly_checksum_gap_audit:", workflow)
        self.assertIn('s.get("canonical_source")!="NONE"', workflow)
        self.assertIn('s.get("g0")!="BLOCKED_GLOBAL"', workflow)
        self.assertIn('s.get("monthly_zip_downloads")!=0', workflow)

if __name__ == "__main__":
    unittest.main()
