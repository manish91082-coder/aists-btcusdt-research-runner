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

    def test_frozen_inventory_comparison_detects_hash_and_size_drift(self):
        digest = "a" * 64
        row = {"sha256_local": digest, "bytes": "123"}
        self.assertEqual(
            AUDIT.compare_frozen_inventory(row, digest, 123),
            (digest, "123", "MATCH", "MATCH"),
        )
        self.assertEqual(
            AUDIT.compare_frozen_inventory(row, "b" * 64, 123),
            (digest, "123", "MISMATCH", "MATCH"),
        )
        self.assertEqual(
            AUDIT.compare_frozen_inventory(row, digest, 124),
            (digest, "123", "MATCH", "MISMATCH"),
        )
        self.assertEqual(
            AUDIT.compare_frozen_inventory({"sha256_local": "", "bytes": ""}, digest, 123),
            ("", "", "UNAVAILABLE", "UNAVAILABLE"),
        )

    def test_checksum_parser_requires_hash_and_archive_name(self):
        digest = "a" * 64
        hashes, named = AUDIT.parse_checksum(f"{digest}  BTCUSDT-4h-2017-08.zip", "BTCUSDT-4h-2017-08.zip")
        self.assertEqual(hashes, [digest])
        self.assertTrue(named)

    def test_checksum_parser_does_not_invent_missing_hash(self):
        hashes, named = AUDIT.parse_checksum("missing hash for BTCUSDT-4h-2017-08.zip", "BTCUSDT-4h-2017-08.zip")
        self.assertEqual(hashes, [])
        self.assertTrue(named)

    def test_checksum_parser_does_not_pair_hash_from_another_line(self):
        digest = "a" * 64
        text = f"{digest}  BTCUSDT-4h-2017-07.zip\nBTCUSDT-4h-2017-08.zip"
        hashes, named = AUDIT.parse_checksum(text, "BTCUSDT-4h-2017-08.zip")
        self.assertEqual(hashes, [])
        self.assertTrue(named)

    def test_redirect_handler_blocks_untrusted_target_before_following(self):
        handler = AUDIT.OfficialChecksumRedirectHandler()
        req = AUDIT.urllib.request.Request(
            "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2017-08.zip.CHECKSUM"
        )
        with self.assertRaises(AUDIT.urllib.error.HTTPError):
            handler.redirect_request(
                req, None, 302, "Found", {}, "https://example.invalid/steal"
            )

    def test_redirect_handler_allows_only_official_https_object_path(self):
        handler = AUDIT.OfficialChecksumRedirectHandler()
        req = AUDIT.urllib.request.Request(
            "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2017-08.zip.CHECKSUM"
        )
        result = handler.redirect_request(
            req, None, 302, "Found", {},
            "https://s3.amazonaws.com" + req.full_url.removeprefix("https://data.binance.vision")
        )
        self.assertIsNotNone(result)

    def test_redirect_handler_allows_signed_query_only_on_official_s3(self):
        handler = AUDIT.OfficialChecksumRedirectHandler()
        req = AUDIT.urllib.request.Request(
            "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2017-08.zip.CHECKSUM"
        )
        result = handler.redirect_request(
            req, None, 302, "Found", {},
            "https://s3.amazonaws.com" + req.full_url.removeprefix("https://data.binance.vision")
            + "?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=example"
        )
        self.assertIsNotNone(result)

    def test_redirect_handler_blocks_query_on_binance_host(self):
        handler = AUDIT.OfficialChecksumRedirectHandler()
        req = AUDIT.urllib.request.Request(
            "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2017-08.zip.CHECKSUM"
        )
        with self.assertRaises(AUDIT.urllib.error.HTTPError):
            handler.redirect_request(
                req, None, 302, "Found", {},
                req.full_url + "?unexpected=1"
            )

    def test_checksum_parser_rejects_hash_for_different_archive(self):
        digest = "b" * 64
        hashes, named = AUDIT.parse_checksum(
            f"{digest}  BTCUSDT-4h-2017-07.zip", "BTCUSDT-4h-2017-08.zip"
        )
        self.assertEqual(hashes, [])
        self.assertFalse(named)


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
        self.assertIn('"publish_cp0165_4h_monthly_checksum_gap_audit")', runner)
        self.assertIn("publisher_scoped=(scoped_count==16)", runner)
        self.assertIn("scoped_count in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)", runner)
        self.assertIn('s.get("canonical_source")!="NONE"', workflow)
        self.assertIn('s.get("g0")!="BLOCKED_GLOBAL"', workflow)
        self.assertIn('if s.get("status")!="BLOCKED_4H_AUDIT_INPUT_INVALID" and rows!=110:', workflow)
        self.assertIn('rows<0', workflow)
        self.assertIn('s.get("monthly_zip_downloads")!=0', workflow)

    def test_read_only_execution_workflow_is_bounded(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "cp0165-4h-audit-execution.yml").read_text(encoding="utf-8")
        self.assertIn("branches: [cp-0165-4h-archive-audit]", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("actions: read", workflow)
        self.assertIn("actions/cache/restore@v4", workflow)
        self.assertIn("scripts/AISTS_CP0165_4H_Monthly_Checksum_Gap_Audit.py", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("git push", workflow)
        self.assertNotIn("curl ", workflow)

    def test_missing_inventory_writes_blocked_evidence_without_failing_runner(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(AUDIT, "ROOT", root), patch("sys.argv", [
                "audit", "--archive-inventory", "missing.csv",
                "--monthly-cache", "cache", "--output-dir", "out"
            ]):
                rc = AUDIT.main()
            summary = __import__("json").loads(
                (root / "out" / "CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json").read_text()
            )
            self.assertEqual(rc, 0)
            self.assertEqual(summary["status"], "BLOCKED_4H_AUDIT_INPUT_INVALID")
            self.assertFalse(summary["network_used"])
            import csv
            with (root / "out" / "CP0165_4H_Monthly_Checksum_Gap_Audit_Details.csv").open(encoding="utf-8", newline="") as f:
                details_header = next(csv.reader(f))
            self.assertEqual(details_header, [
                "period", "filename", "cache_path", "cache_match_count", "cache_status",
                "local_sha256", "inventory_sha256", "inventory_bytes",
                "baseline_sha256_status", "baseline_bytes_status", "zip_crc",
                "sidecar_status", "sidecar_sha256", "sidecar_hashes",
                "sidecar_filename_match", "checksum_status", "error",
            ])

    def test_invalid_inventory_writes_blocked_evidence_without_failing_runner(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "inventory.csv"
            inventory.write_text("source,interval,filename\nmonthly_cache,4h,BTCUSDT-4h-2017-08.zip\n")
            with patch.object(AUDIT, "ROOT", root), patch("sys.argv", [
                "audit", "--archive-inventory", "inventory.csv",
                "--monthly-cache", "cache", "--output-dir", "out"
            ]):
                rc = AUDIT.main()
            summary = __import__("json").loads(
                (root / "out" / "CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json").read_text()
            )
            self.assertEqual(rc, 0)
            self.assertEqual(summary["status"], "BLOCKED_4H_AUDIT_INPUT_INVALID")
            self.assertFalse(summary["network_used"])

    def test_missing_cache_writes_blocked_evidence_without_failing_runner(self):
        import csv
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = root / "inventory.csv"
            with inventory.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["source", "interval", "filename"])
                writer.writeheader()
                for month in AUDIT.expected_periods():
                    writer.writerow({
                        "source": "monthly_cache", "interval": "4h",
                        "filename": f"BTCUSDT-4h-{month}.zip"
                    })
            with patch.object(AUDIT, "ROOT", root), patch("sys.argv", [
                "audit", "--archive-inventory", "inventory.csv",
                "--monthly-cache", "missing-cache", "--output-dir", "out"
            ]):
                rc = AUDIT.main()
            summary = __import__("json").loads(
                (root / "out" / "CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json").read_text()
            )
            self.assertEqual(rc, 0)
            self.assertEqual(summary["status"], "BLOCKED_4H_AUDIT_INPUT_INVALID")
            self.assertEqual(summary["archive_inventory_rows"], 110)
            self.assertFalse(summary["network_used"])

if __name__ == "__main__":
    unittest.main()
