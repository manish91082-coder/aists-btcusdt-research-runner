import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0267_NotVerified_Gate.py"
SPEC = importlib.util.spec_from_file_location("cp0267_gate", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

class TestCP0267NotVerifiedGate(unittest.TestCase):
    def setUp(self):
        self.good = ("BTCUSDT", "BINANCE_SPOT", "4h", "1000")
        self.bad = ("BTCUSDT", "BINANCE_SPOT", "4h", "2000")
        self.manifest = {self.good: "VERIFIED_PRIMARY_CURRENT_SNAPSHOT",
                         self.bad: "NOT_VERIFIED_MISMATCH"}
        self.rows = [
            {"symbol": self.good[0], "market": self.good[1], "interval": self.good[2], "open_time_ms": self.good[3]},
            {"symbol": self.bad[0], "market": self.bad[1], "interval": self.bad[2], "open_time_ms": self.bad[3]},
        ]

    def test_partition_excludes_not_verified_exact_key(self):
        kept, excluded = GATE.partition_rows(self.rows, self.manifest)
        self.assertEqual([r["open_time_ms"] for r in kept], ["1000"])
        self.assertEqual([r["open_time_ms"] for r in excluded], ["2000"])
        self.assertEqual(excluded[0]["exclusion_status"], "NOT_VERIFIED_MISMATCH")

    def test_unverified_key_cannot_reach_scoring(self):
        with self.assertRaisesRegex(GATE.NotVerifiedGateError, "UNVERIFIED_KEY_REACHED_SCORING"):
            GATE.require_scored_rows(self.rows, self.manifest)

    def test_missing_manifest_key_fails_closed(self):
        with self.assertRaisesRegex(GATE.NotVerifiedGateError, "KEY_NOT_IN_MANIFEST"):
            GATE.partition_rows([self.rows[0]], {})

    def test_frozen_ledger_population_and_policy_load(self):
        root = Path(__file__).resolve().parents[1]
        evidence = root / "evidence" / "source_adjudication" / "CP0040_Run_38882377148"
        policy = GATE.load_scoped_policy(
            evidence / "CP0040_ExactKey_Quarantine_Manifest.csv",
            evidence / "CP0040_NonRow_Blockers.csv",
        )
        self.assertEqual(policy["exact_rows"], 969)
        self.assertEqual(policy["nonrow_rows"], 27)
        self.assertEqual(policy["gap_keys"], 17)
        self.assertEqual(policy["status"], "NOT_VERIFIED_EXCLUSION_POLICY_LOADED")

    def test_all_three_blocker_families_are_excluded_by_exact_key_or_date(self):
        root = Path(__file__).resolve().parents[1]
        evidence = root / "evidence" / "source_adjudication" / "CP0040_Run_38882377148"
        policy = GATE.load_scoped_policy(
            evidence / "CP0040_ExactKey_Quarantine_Manifest.csv",
            evidence / "CP0040_NonRow_Blockers.csv",
        )
        self.assertTrue(GATE.exclusion_reasons(policy, "4h", "1504713600000"))
        self.assertTrue(GATE.exclusion_reasons(policy, "5m", "1512378000000", "2017-12-04T09:00:00Z"))
        self.assertTrue(GATE.exclusion_reasons(policy, "15m", "1512378000000", "2017-12-04T09:00:00Z"))
        self.assertFalse(GATE.exclusion_reasons(policy, "1d", "1609459200000", "2021-01-01T00:00:00Z"))

    def test_manifest_hash_and_schema_are_required(self):
        data = ("symbol,market,interval,open_time_ms,status,reason\n"
                "BTCUSDT,BINANCE_SPOT,4h,1000,NOT_VERIFIED_GAP,missing key\n")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "manifest.csv"
            p.write_text(data, encoding="utf-8")
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            loaded = GATE.load_manifest(p, sha)
            self.assertEqual(loaded[self.good], "NOT_VERIFIED_GAP")
            with self.assertRaisesRegex(GATE.NotVerifiedGateError, "MANIFEST_SHA_MISMATCH"):
                GATE.load_manifest(p, "0" * 64)

if __name__ == "__main__":
    unittest.main()
