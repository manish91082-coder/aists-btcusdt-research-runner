import hashlib, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import audit_binance_monthly_archive as audit

class MonthlyArchiveTests(unittest.TestCase):
    def test_checksum_digest(self):
        digest=hashlib.sha256(b"sample").hexdigest()
        self.assertEqual(audit.checksum_digest(f"{digest}  BTCUSDT-5m-2026-09.zip\n".encode()),digest)
    def test_bad_checksum_rejected(self):
        with self.assertRaises(ValueError): audit.checksum_digest(b"not-a-checksum")
    def test_september_2026_expected_5m_rows(self):
        start,end,days=audit.month_bounds("2026-09")
        self.assertEqual(days,30)
        self.assertEqual((end-start)//audit.INTERVAL_MS["5m"],8640)
    def test_one_valid_candle_passes_quality_checks(self):
        start, _, _ = audit.month_bounds("2026-09")
        row = f"{start},100,101,99,100.5,10,{start+299999},1000,5,4,400,0\\n".encode()
        report = audit.validate_csv(row, "usdm", "2026-09", "5m", False)
        self.assertEqual(report["row_count"], 1)
        self.assertTrue(all(v == "PASS" for v in report["checks"].values()))

    def test_invalid_month_rejected(self):
        with self.assertRaises(ValueError): audit.month_bounds("2026-13")

if __name__=="__main__": unittest.main()
