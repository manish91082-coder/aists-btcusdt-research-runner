import csv
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "AISTS_CP0040_Quarantine_Gate.py"
SPEC = importlib.util.spec_from_file_location("cp0040_quarantine_gate", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(GATE)

FROZEN_MANIFEST = ROOT / "evidence" / "source_adjudication" / "CP0040_Run_38882377148" / "CP0040_ExactKey_Quarantine_Manifest.csv"
FROZEN_SHA256 = "d29a20e604ddfc3f2ba29ab07296b76f2ccc0b894f1cd8fb1a0b8ab001037819"


class TestCP0040ExactKeyQuarantineGate(unittest.TestCase):
    def test_frozen_manifest_hash_and_population_are_required(self):
        keys, summary = GATE.load_quarantine_manifest(
            FROZEN_MANIFEST, expected_sha256=FROZEN_SHA256
        )
        self.assertEqual(summary["status"], "PASS_MANIFEST_VALIDATED")
        self.assertEqual(summary["manifest_rows"], 969)
        self.assertEqual(summary["unique_case_ids"], 969)
        self.assertEqual(hashlib.sha256(FROZEN_MANIFEST.read_bytes()).hexdigest(), FROZEN_SHA256)
        self.assertGreater(len(keys), 0)

    def test_frozen_manifest_tamper_fails_closed(self):
        with self.assertRaisesRegex(GATE.QuarantineManifestError, "SHA-256 mismatch"):
            GATE.load_quarantine_manifest(FROZEN_MANIFEST, expected_sha256="0" * 64)

    def test_exact_interval_and_timestamp_identity(self):
        key = GATE.exact_key("4h", "1504699200000")
        rows = [
            {"open_time_ms": "1504699200000", "payload": "same-key"},
            {"open_time_ms": "1504699200001", "payload": "one-ms-different"},
        ]
        kept, excluded = GATE.quarantine_rows(rows, "4h", {key})
        self.assertEqual([r["payload"] for r in excluded], ["same-key"])
        self.assertEqual([r["payload"] for r in kept], ["one-ms-different"])
        kept_other_interval, excluded_other_interval = GATE.quarantine_rows(
            [rows[0]], "1h", {key}
        )
        self.assertEqual(len(kept_other_interval), 1)
        self.assertEqual(excluded_other_interval, [])

    def test_fractional_timestamp_is_rejected_without_rounding(self):
        for token in ("1504699200000.0", "1504699200000.5", "-1", ""):
            with self.subTest(token=token):
                with self.assertRaises(GATE.QuarantineManifestError):
                    GATE.exact_key("4h", token)

    def test_invalid_interval_is_rejected(self):
        with self.assertRaisesRegex(GATE.QuarantineManifestError, "unsupported interval"):
            GATE.exact_key("4H", "1504699200000")

    def test_duplicate_case_id_fails_closed(self):
        csv_text = (
            "case_id,case_class,interval,open_time_ms,disposition,canonical_source,case_closed\n"
            "CASE-1,TEST,4h,1000,UNRESOLVED,NONE,false\n"
            "CASE-1,TEST,4h,2000,UNRESOLVED,NONE,false\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(GATE.QuarantineManifestError, "duplicate case_id"):
                GATE.load_quarantine_manifest(path)

    def test_closed_case_or_selected_source_fails_closed(self):
        for canonical, closed in (("NONE", "true"), ("BINANCE", "false")):
            csv_text = (
                "case_id,case_class,interval,open_time_ms,disposition,canonical_source,case_closed\n"
                f"CASE-1,TEST,4h,1000,UNRESOLVED,{canonical},{closed}\n"
            )
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / "manifest.csv"
                path.write_text(csv_text, encoding="utf-8")
                with self.assertRaises(GATE.QuarantineManifestError):
                    GATE.load_quarantine_manifest(path)


if __name__ == "__main__":
    unittest.main()
