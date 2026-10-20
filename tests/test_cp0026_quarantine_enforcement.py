import csv
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BUILDER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "AISTS_CP0026_Research_Candidate_Builder.py"
SPEC = importlib.util.spec_from_file_location("aists_cp0026_candidate_builder", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class CP0026QuarantineEnforcementTests(unittest.TestCase):
    def test_exact_interval_and_timestamp_key_is_quarantined(self):
        keys = {("5m", "1518170294789")}
        rows = [
            {"open_time_ms": "1518170294789", "raw_open_time_token": "1518170294789", "close": "100"},
            {"open_time_ms": "1518170294790", "raw_open_time_token": "1518170294790", "close": "101"},
        ]
        kept, quarantined = BUILDER.partition_candidate_rows(rows, "5m", keys)
        self.assertEqual(quarantined, [rows[0]])
        self.assertEqual(kept, [rows[1]])
        self.assertEqual(rows[0]["raw_open_time_token"], "1518170294789")
        self.assertEqual(rows[0]["close"], "100")

    def test_same_timestamp_on_another_interval_is_not_matched(self):
        rows = [{"open_time_ms": "1518170294789"}]
        kept, quarantined = BUILDER.partition_candidate_rows(
            rows, "15m", {("5m", "1518170294789")}
        )
        self.assertEqual(kept, rows)
        self.assertEqual(quarantined, [])

    def test_non_integer_timestamp_fails_closed(self):
        for token in ("1518170294789.0", "1518170294789.5", "", "-1"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    BUILDER.partition_candidate_rows(
                        [{"open_time_ms": token}], "5m", {("5m", "1518170294789")}
                    )

    def test_manifest_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.csv"
            blockers = root / "blockers.csv"
            summary = root / "summary.json"
            manifest.write_text(
                "case_id,case_class,interval,open_time_ms,disposition,canonical_source,case_closed\n"
                "ROW-1,EXACT_KEY,5m,1518170294789,QUARANTINE,NONE,false\n",
                encoding="utf-8",
            )
            blockers.write_text("case_id,record_type,disposition\n", encoding="utf-8")
            summary.write_text(json.dumps({
                "status": "PASS_CANDIDATE_ELIGIBILITY_READY",
                "row_level_manifest": {
                    "sha256": "0" * 64,
                    "rows": 1,
                    "case_class_counts": {"EXACT_KEY": 1},
                },
                "nonrow_blockers": {"rows": 0, "candidate_eligibility_blocked": False},
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MANIFEST_SHA256_MISMATCH"):
                BUILDER.load_candidate_gate(manifest, blockers, summary)

    def test_unresolved_nonrow_blockers_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.csv"
            blockers = root / "blockers.csv"
            summary = root / "summary.json"
            manifest_text = (
                "case_id,case_class,interval,open_time_ms,disposition,canonical_source,case_closed\n"
                "ROW-1,EXACT_KEY,5m,1518170294789,QUARANTINE,NONE,false\n"
            )
            manifest.write_text(manifest_text, encoding="utf-8")
            blockers.write_text(
                "case_id,record_type,disposition\nAGG-1,AGG,UNRESOLVED\n",
                encoding="utf-8",
            )
            digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            summary.write_text(json.dumps({
                "status": "PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN",
                "row_level_manifest": {
                    "sha256": digest,
                    "rows": 1,
                    "case_class_counts": {"EXACT_KEY": 1},
                },
                "nonrow_blockers": {"rows": 1, "candidate_eligibility_blocked": True},
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "NONROW_BLOCKERS_REMAIN"):
                BUILDER.load_candidate_gate(manifest, blockers, summary)


    def _write_daily_fixture(self, path):
        fields = [
            "open_time_ms", "open", "high", "low", "close", "volume",
            "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume",
        ]
        rows = []
        for year, month, day, price in ((2020, 1, 1, "10"), (2020, 2, 1, "20")):
            dt = BUILDER.datetime(year, month, day, tzinfo=BUILDER.timezone.utc)
            rows.append({
                "open_time_ms": str(int(dt.timestamp() * 1000)),
                "open": price, "high": str(int(price) + 2), "low": str(int(price) - 2),
                "close": str(int(price) + 1), "volume": "3", "quote_asset_volume": "30",
                "number_of_trades": "4", "taker_buy_base_asset_volume": "1",
                "taker_buy_quote_asset_volume": "10",
            })
        with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return rows

    def test_derived_monthly_exact_key_is_quarantined_and_audited(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            daily = root / "BTCUSDT-1d-research-candidate.csv.gz"
            monthly = root / "BTCUSDT-1mo-research-candidate.csv.gz"
            self._write_daily_fixture(daily)
            jan = str(int(BUILDER.datetime(2020, 1, 1, tzinfo=BUILDER.timezone.utc).timestamp() * 1000))
            quarantined = []
            summary = BUILDER.create_monthly_from_daily(
                root, daily, monthly, {("1mo", jan)}, {("1mo", jan): ["ROW-MONTH"]}, quarantined
            )
            with gzip.open(monthly, "rt", newline="", encoding="utf-8") as stream:
                output = list(csv.DictReader(stream))
            self.assertEqual([row["open_time_utc"] for row in output], ["2020-02-01T00:00:00Z"])
            self.assertEqual(summary["quarantined_exact_key_rows"], 1)
            self.assertEqual(summary["status"], "BLOCKED_QUARANTINED_DERIVED_INPUTS")
            self.assertEqual(quarantined[0]["quarantine_case_ids"], "ROW-MONTH")
            self.assertEqual(quarantined[0]["derived_row_written"], False)

    def test_derived_monthly_is_quarantined_when_a_daily_source_key_is_quarantined(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            daily = root / "BTCUSDT-1d-research-candidate.csv.gz"
            monthly = root / "BTCUSDT-1mo-research-candidate.csv.gz"
            self._write_daily_fixture(daily)
            jan15 = str(int(BUILDER.datetime(2020, 1, 15, tzinfo=BUILDER.timezone.utc).timestamp() * 1000))
            quarantined = []
            summary = BUILDER.create_monthly_from_daily(
                root, daily, monthly, {("1d", jan15)}, {("1d", jan15): ["ROW-DAILY"]}, quarantined
            )
            with gzip.open(monthly, "rt", newline="", encoding="utf-8") as stream:
                output = list(csv.DictReader(stream))
            self.assertEqual([row["open_time_utc"] for row in output], ["2020-02-01T00:00:00Z"])
            self.assertEqual(summary["quarantined_source_input_rows"], 1)
            self.assertEqual(summary["status"], "BLOCKED_QUARANTINED_DERIVED_INPUTS")
            self.assertIn(jan15, quarantined[0]["source_quarantine_open_time_ms"])
            self.assertEqual(quarantined[0]["quarantine_case_ids"], "ROW-DAILY")


if __name__ == "__main__":
    unittest.main()
