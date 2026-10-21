import hashlib, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import audit_binance_monthly_archive as audit


class MonthlyArchiveTests(unittest.TestCase):
    def test_checksum_digest(self):
        digest = hashlib.sha256(b"sample").hexdigest()
        self.assertEqual(
            audit.checksum_digest(f"{digest}  BTCUSDT-5m-2026-09.zip\n".encode()),
            digest,
        )

    def test_bad_checksum_rejected(self):
        with self.assertRaises(ValueError):
            audit.checksum_digest(b"not-a-checksum")

    def test_september_2026_expected_5m_rows(self):
        start, end, days = audit.month_bounds("2026-09")
        self.assertEqual(days, 30)
        self.assertEqual((end - start) // audit.INTERVAL_MS["5m"], 8640)

    def test_one_valid_candle_passes_quality_checks(self):
        start, _, _ = audit.month_bounds("2026-09")
        row = (
            f"{start},100,101,99,100.5,10,{start + 299999},1000,5,4,400,0\n"
        ).encode()
        report = audit.validate_csv(row, "usdm", "2026-09", "5m", False)
        self.assertEqual(report["row_count"], 1)
        self.assertTrue(all(v == "PASS" for v in report["checks"].values()))

    def test_non_positive_prices_fail_quality_gate(self):
        start, _, _ = audit.month_bounds("2026-09")
        rows = [
            f"{start},-100,-99,-101,-100.5,10,{start + 299999},1000,5,4,400,0",
            f"{start + 300000},1,2,0,1,10,{start + 599999},1000,5,4,400,0",
        ]
        for row in rows:
            with self.subTest(row=row):
                report = audit.validate_csv((row + "\\n").encode(), "usdm", "2026-09", "5m", False)
                self.assertEqual(report["checks"]["ohlc_invariants"], "PASS")
                self.assertEqual(report["checks"]["positive_prices"], "FAIL")

    def test_full_month_coverage_detects_missing_rows(self):
        start, _, _ = audit.month_bounds("2026-09")
        rows = []
        for i in (0, 2):
            t = start + i * audit.INTERVAL_MS["5m"]
            rows.append(
                f"{t},100,101,99,100.5,10,{t + 299999},1000,5,4,400,0"
            )
        report = audit.validate_csv(
            ("\n".join(rows) + "\n").encode(), "usdm", "2026-09", "5m", True
        )
        self.assertEqual(report["row_count"], 2)
        self.assertEqual(report["checks"]["gaps"], "FAIL")
        self.assertEqual(report["checks"]["full_month_coverage"], "FAIL")

    def test_invalid_month_rejected(self):
        with self.assertRaises(ValueError):
            audit.month_bounds("2026-13")


if __name__ == "__main__":
    unittest.main()
