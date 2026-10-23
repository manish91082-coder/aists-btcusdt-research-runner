import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts.probe_btcusdt_archive_coverage import head, month_range


class TestBtcusdtArchiveCoverageInventory(unittest.TestCase):
    def test_month_range_across_year_boundary(self):
        self.assertEqual(month_range("2019-11", "2020-02"),
                         ["2019-11", "2019-12", "2020-01", "2020-02"])

    def test_month_range_rejects_reverse_range(self):
        with self.assertRaisesRegex(ValueError, "end month precedes"):
            month_range("2020-02", "2020-01")

    def test_month_range_limits_to_120_months(self):
        with self.assertRaisesRegex(ValueError, "limited to 120 months"):
            month_range("2010-01", "2020-01")

    def test_head_records_available_with_content_length(self):
        class Response:
            status = 200
            headers = {"Content-Length": "1234"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
        with patch("scripts.probe_btcusdt_archive_coverage.urllib.request.urlopen", return_value=Response()):
            result = head("https://example.invalid/file.zip")
        self.assertEqual(result["status"], "AVAILABLE")
        self.assertEqual(result["content_length"], 1234)

    def test_head_404_is_unavailable_not_fail(self):
        err = HTTPError("https://example.invalid/file.zip", 404, "Not Found", {}, None)
        with patch("scripts.probe_btcusdt_archive_coverage.urllib.request.urlopen", side_effect=err):
            result = head("https://example.invalid/file.zip")
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertEqual(result["http_status"], 404)


if __name__ == "__main__":
    unittest.main()
