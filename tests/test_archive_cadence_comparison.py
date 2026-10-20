import io
import unittest
import zipfile
from datetime import date, datetime, timezone

from tools.compare_binance_archive_cadences import archive_rows, INTERVALS


def make_zip(rows):
    raw="\n".join(",".join(map(str,row)) for row in rows)+"\n"
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("BTCUSDT-5m.csv",raw)
    return out.getvalue()


def kline(open_ms, close_ms, close="101.0"):
    # Standard 12-field Binance kline record.
    return [open_ms,"100.0","102.0","99.0",close,"12.0",close_ms,"1200.0","42","6.0","600.0","0"]


class ArchiveCadenceComparisonTests(unittest.TestCase):
    def test_spot_microseconds_normalize_to_milliseconds(self):
        day=date(2026,10,15)
        start=int(datetime(2026,10,15,tzinfo=timezone.utc).timestamp()*1000)
        row=kline(start*1000,(start+INTERVALS["5m"]-1)*1000)
        parsed=archive_rows(make_zip([row]),"spot",day,"5m")
        self.assertIn(start,parsed)
        self.assertEqual(len(parsed),1)

    def test_futures_millisecond_timestamps_are_preserved(self):
        day=date(2026,10,15)
        start=int(datetime(2026,10,15,tzinfo=timezone.utc).timestamp()*1000)
        parsed=archive_rows(make_zip([kline(start,start+INTERVALS["5m"]-1)]),"usdm",day,"5m")
        self.assertIn(start,parsed)

    def test_duplicate_open_time_is_rejected(self):
        day=date(2026,10,15)
        start=int(datetime(2026,10,15,tzinfo=timezone.utc).timestamp()*1000)
        with self.assertRaisesRegex(ValueError,"Duplicate open timestamp"):
            archive_rows(make_zip([kline(start,start+299999),kline(start,start+299999)]),"usdm",day,"5m")

    def test_utc_day_expected_count_for_five_minute_interval(self):
        self.assertEqual(86400000//INTERVALS["5m"],288)


if __name__ == "__main__":
    unittest.main()
