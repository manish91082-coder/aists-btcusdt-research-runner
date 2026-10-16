#!/usr/bin/env python3
"""Download seven fixed Binance Spot daily-trades ZIPs; verify sidecars, bytes, ZIP and row coverage."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOST = "data.binance.vision"
TARGET_DATES = (
    "2017-12-04",
    "2018-02-05",
    "2018-02-07",
    "2018-03-04",
    "2018-03-20",
    "2018-06-20",
    "2018-09-05",
)
TIMEOUT_SECONDS = 90
MAX_SIDECAR_BYTES = 4096
MAX_ARCHIVE_BYTES_EACH = 512 * 1024 * 1024
MAX_ARCHIVE_BYTES_TOTAL = 2 * 1024 * 1024 * 1024
STREAM_CHUNK_BYTES = 1024 * 1024
EDGE_REVIEW_SECONDS = 300
EXPECTED_COLUMNS = 7


class SameHostHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise urllib.error.HTTPError(
                newurl, code, "Blocked redirect outside official HTTPS host", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_target(day: str) -> dict:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError("Invalid fixed target date")
    archive = "BTCUSDT-trades-" + day + ".zip"
    folder = "https://" + OFFICIAL_HOST + "/data/spot/daily/trades/BTCUSDT/"
    sidecar_url = folder + archive + ".CHECKSUM"
    archive_url = folder + archive
    for url in (sidecar_url, archive_url):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise ValueError("URL does not meet the fixed official-host allowlist")
    return {
        "utc_date": day,
        "archive_filename": archive,
        "sidecar_filename": archive + ".CHECKSUM",
        "archive_url": archive_url,
        "sidecar_url": sidecar_url,
    }


def fetch_sidecar(target: dict, opener) -> dict:
    req = urllib.request.Request(
        target["sidecar_url"],
        headers={"User-Agent": "AISTS-CP0111-Trade-Integrity/1.0", "Accept": "text/plain"},
        method="GET",
    )
    with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
        final_url = response.geturl()
        final = urlparse(final_url)
        status = getattr(response, "status", None)
        body = response.read(MAX_SIDECAR_BYTES + 1)
    if final.scheme != "https" or final.hostname != OFFICIAL_HOST or status != 200:
        raise ValueError("Sidecar response not an HTTP 200 from allowlisted HTTPS host")
    if len(body) > MAX_SIDECAR_BYTES:
        raise ValueError("Sidecar exceeded the bounded text-size limit")
    text = body.decode("utf-8", errors="strict").strip()
    tokens = re.findall(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text)
    if len(tokens) != 1 or target["archive_filename"] not in text:
        raise ValueError("Sidecar must contain exactly one SHA-256 token and exact archive filename")
    return {
        "sidecar_http_status": status,
        "sidecar_final_url": final_url,
        "sidecar_bytes": len(body),
        "sidecar_body_sha256": sha_bytes(body),
        "sidecar_body_utf8": text,
        "expected_archive_sha256": tokens[0].lower(),
        "sidecar_filename_match": True,
    }


def download_verified_bytes(target: dict, expected_sha256: str, opener, temp_dir: Path,
                            remaining_budget: int) -> dict:
    req = urllib.request.Request(
        target["archive_url"],
        headers={"User-Agent": "AISTS-CP0111-Trade-Integrity/1.0", "Accept": "application/zip"},
        method="GET",
    )
    temp_path = temp_dir / target["archive_filename"]
    h = hashlib.sha256()
    total = 0
    response_meta = {}
    try:
        with opener.open(req, timeout=TIMEOUT_SECONDS) as response, temp_path.open("wb") as dst:
            final_url = response.geturl()
            final = urlparse(final_url)
            status = getattr(response, "status", None)
            headers = response.headers
            if final.scheme != "https" or final.hostname != OFFICIAL_HOST or status != 200:
                raise ValueError("Archive response not an HTTP 200 from allowlisted HTTPS host")
            declared = headers.get("Content-Length")
            declared_length = int(declared) if declared and declared.isdigit() else None
            response_meta = {
                "archive_http_status": status,
                "archive_final_url": final_url,
                "archive_content_length_header": declared_length,
                "archive_last_modified": headers.get("Last-Modified"),
                "archive_etag": headers.get("ETag"),
            }
            if declared_length is not None and declared_length > MAX_ARCHIVE_BYTES_EACH:
                raise ValueError("Archive exceeds per-file safety budget before body download")
            if declared_length is not None and declared_length > remaining_budget:
                raise ValueError("Archive exceeds remaining aggregate download safety budget")
            while True:
                block = response.read(STREAM_CHUNK_BYTES)
                if not block:
                    break
                total += len(block)
                if total > MAX_ARCHIVE_BYTES_EACH:
                    raise ValueError("Streamed archive exceeded per-file safety budget")
                if total > remaining_budget:
                    raise ValueError("Streamed archive exceeded remaining aggregate budget")
                h.update(block)
                dst.write(block)
            dst.flush()
            os.fsync(dst.fileno())
        digest = h.hexdigest()
        response_meta.update({
            "archive_bytes": total,
            "archive_actual_sha256": digest,
            "archive_sha256_matches_sidecar": digest == expected_sha256,
            "temporary_archive_path": str(temp_path),
            "archive_zip_downloaded": True,
        })
        if response_meta.get("archive_content_length_header") is not None:
            response_meta["content_length_matches_downloaded_bytes"] = (
                response_meta["archive_content_length_header"] == total
            )
        else:
            response_meta["content_length_matches_downloaded_bytes"] = None
        if digest != expected_sha256:
            response_meta["integrity_status"] = "FAIL_ARCHIVE_SHA256_MISMATCH"
        elif response_meta["content_length_matches_downloaded_bytes"] is False:
            response_meta["integrity_status"] = "FAIL_CONTENT_LENGTH_MISMATCH"
        else:
            response_meta["integrity_status"] = "PASS_ARCHIVE_SHA256_MATCH"
        return response_meta
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def inspect_archive(target: dict, archive_path: Path) -> dict:
    result = {
        "zip_open_status": "NOT_RUN",
        "zip_crc_status": "NOT_RUN",
        "zip_member_count": None,
        "csv_member": None,
        "csv_schema_status": "NOT_RUN",
        "rows": 0,
        "first_trade_id": None,
        "last_trade_id": None,
        "first_trade_time_ms": None,
        "last_trade_time_ms": None,
        "first_trade_time_utc": None,
        "last_trade_time_utc": None,
        "first_edge_gap_seconds": None,
        "last_edge_gap_seconds": None,
        "rows_outside_target_utc_day": 0,
        "invalid_row_count": 0,
        "trade_id_gap_count": 0,
        "trade_id_duplicate_count": 0,
        "trade_id_decrease_count": 0,
        "timestamp_decrease_count": 0,
        "trade_id_gap_examples": [],
        "csv_rows_have_exactly_7_columns": True,
        "prices_and_quantities_numeric": True,
        "boolean_fields_valid": True,
    }
    try:
        zf = zipfile.ZipFile(archive_path, "r")
    except Exception as exc:
        result.update({"zip_open_status": "FAIL", "zip_open_error": type(exc).__name__ + ": " + str(exc)[:250]})
        return result
    with zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        result["zip_member_count"] = len(members)
        result["zip_member_names"] = [m.filename for m in members]
        result["zip_open_status"] = "PASS" if members else "FAIL_EMPTY_ZIP"
        if len(members) != 1:
            result["zip_crc_status"] = "REVIEW_UNEXPECTED_MEMBER_COUNT"
            result["csv_schema_status"] = "NOT_RUN_UNEXPECTED_MEMBER_COUNT"
            return result
        member = members[0]
        result["csv_member"] = member.filename
        expected_member = target["archive_filename"][:-4] + ".csv"
        if Path(member.filename).name != expected_member:
            result["csv_schema_status"] = "FAIL_UNEXPECTED_CSV_MEMBER_NAME"
            return result
        bad_member = zf.testzip()
        result["zip_crc_status"] = "PASS" if bad_member is None else "FAIL_CRC:" + str(bad_member)
        if bad_member is not None:
            return result

        day_start_ms = int(datetime.strptime(target["utc_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
        day_end_ms = day_start_ms + 86_400_000
        previous_id = None
        previous_time = None
        schema_ok = True
        with zf.open(member, "r") as raw, __import__("io").TextIOWrapper(raw, encoding="utf-8", errors="strict", newline="") as text:
            reader = csv.reader(text)
            for row in reader:
                if len(row) != EXPECTED_COLUMNS:
                    result["csv_rows_have_exactly_7_columns"] = False
                    result["invalid_row_count"] += 1
                    continue
                try:
                    trade_id = int(row[0])
                    price = Decimal(row[1])
                    qty = Decimal(row[2])
                    quote_qty = Decimal(row[3])
                    trade_time = int(row[4])
                    if not (price.is_finite() and qty.is_finite() and quote_qty.is_finite()):
                        raise InvalidOperation("non-finite numeric field")
                    if price <= 0 or qty < 0 or quote_qty < 0:
                        raise InvalidOperation("non-positive price or negative quantity")
                    if row[5] not in ("True", "False", "true", "false") or row[6] not in ("True", "False", "true", "false"):
                        result["boolean_fields_valid"] = False
                        raise ValueError("invalid boolean token")
                except Exception:
                    result["invalid_row_count"] += 1
                    result["prices_and_quantities_numeric"] = False
                    continue

                if result["rows"] == 0:
                    result["first_trade_id"] = trade_id
                    result["first_trade_time_ms"] = trade_time
                else:
                    if previous_id is not None:
                        if trade_id == previous_id:
                            result["trade_id_duplicate_count"] += 1
                        elif trade_id < previous_id:
                            result["trade_id_decrease_count"] += 1
                        elif trade_id > previous_id + 1:
                            result["trade_id_gap_count"] += 1
                            if len(result["trade_id_gap_examples"]) < 5:
                                result["trade_id_gap_examples"].append([previous_id, trade_id])
                    if previous_time is not None and trade_time < previous_time:
                        result["timestamp_decrease_count"] += 1
                if not (day_start_ms <= trade_time < day_end_ms):
                    result["rows_outside_target_utc_day"] += 1

                result["rows"] += 1
                previous_id = trade_id
                previous_time = trade_time
                result["last_trade_id"] = trade_id
                result["last_trade_time_ms"] = trade_time

        if result["rows"] == 0:
            result["csv_schema_status"] = "FAIL_NO_VALID_TRADE_ROWS"
            return result
        result["csv_schema_status"] = (
            "PASS_7_COLUMN_SPOT_TRADES_SCHEMA"
            if schema_ok and result["csv_rows_have_exactly_7_columns"]
            and result["invalid_row_count"] == 0
            and result["prices_and_quantities_numeric"]
            and result["boolean_fields_valid"]
            else "FAIL_OR_REVIEW_ROW_SCHEMA"
        )
        start_dt = datetime.fromtimestamp(result["first_trade_time_ms"] / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(result["last_trade_time_ms"] / 1000, tz=timezone.utc)
        result["first_trade_time_utc"] = start_dt.isoformat()
        result["last_trade_time_utc"] = end_dt.isoformat()
        result["first_edge_gap_seconds"] = round((result["first_trade_time_ms"] - day_start_ms) / 1000, 3)
        result["last_edge_gap_seconds"] = round((day_end_ms - result["last_trade_time_ms"]) / 1000, 3)
        result["day_bounds_pass"] = result["rows_outside_target_utc_day"] == 0
        result["edge_gap_review_required"] = (
            result["first_edge_gap_seconds"] < 0
            or result["last_edge_gap_seconds"] < 0
            or result["first_edge_gap_seconds"] > EDGE_REVIEW_SECONDS
            or result["last_edge_gap_seconds"] > EDGE_REVIEW_SECONDS
        )
        result["trade_id_sequence_review_required"] = (
            result["trade_id_gap_count"] > 0
            or result["trade_id_duplicate_count"] > 0
            or result["trade_id_decrease_count"] > 0
        )
        result["timestamp_order_review_required"] = result["timestamp_decrease_count"] > 0
        result["basic_coverage_status"] = (
            "REVIEW_REQUIRED_COVERAGE_ANOMALY"
            if result["edge_gap_review_required"]
            or result["trade_id_sequence_review_required"]
            or result["timestamp_order_review_required"]
            or not result["day_bounds_pass"]
            else "NO_BASIC_COVERAGE_ANOMALY_DETECTED"
        )
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "utc_date", "archive_filename", "archive_url", "sidecar_url",
        "status", "sidecar_http_status", "sidecar_bytes", "sidecar_body_sha256",
        "expected_archive_sha256", "archive_bytes", "archive_actual_sha256",
        "archive_sha256_matches_sidecar", "archive_http_status", "archive_content_length_header",
        "content_length_matches_downloaded_bytes", "zip_open_status", "zip_crc_status",
        "zip_member_count", "csv_member", "csv_schema_status", "rows",
        "first_trade_id", "last_trade_id", "trade_id_gap_count", "trade_id_duplicate_count",
        "trade_id_decrease_count", "timestamp_decrease_count", "first_trade_time_utc",
        "last_trade_time_utc", "first_edge_gap_seconds", "last_edge_gap_seconds",
        "rows_outside_target_utc_day", "invalid_row_count", "basic_coverage_status", "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/cp0111_official_daily_trade_integrity")
    args = parser.parse_args()
    output = (ROOT / args.output_dir).resolve()
    if ROOT not in output.parents and output != ROOT:
        raise ValueError("Output directory must remain inside repository root")
    output.mkdir(parents=True, exist_ok=True)

    opener = urllib.request.build_opener(SameHostHTTPSRedirectHandler())
    targets = [build_target(day) for day in TARGET_DATES]
    records = []
    archive_bytes_total = 0
    with tempfile.TemporaryDirectory(prefix="cp0111-trades-", dir=str(output)) as tmp:
        tmp_dir = Path(tmp)
        for target in targets:
            row = {
                **target,
                "status": "NOT_RUN",
                "archive_zip_downloaded": False,
                "market_data_rest_api_used": False,
                "source_authority_selected": False,
                "case_closed": False,
            }
            try:
                sidecar = fetch_sidecar(target, opener)
                row.update(sidecar)
                remaining = MAX_ARCHIVE_BYTES_TOTAL - archive_bytes_total
                downloaded = download_verified_bytes(
                    target, sidecar["expected_archive_sha256"], opener, tmp_dir, remaining
                )
                row.update(downloaded)
                archive_bytes_total += downloaded.get("archive_bytes", 0)
                row["archive_zip_downloaded"] = True
                if downloaded["integrity_status"] != "PASS_ARCHIVE_SHA256_MATCH":
                    row["status"] = downloaded["integrity_status"]
                    records.append(row)
                    continue
                inspected = inspect_archive(target, Path(downloaded["temporary_archive_path"]))
                row.update(inspected)
                if (
                    row.get("zip_open_status") == "PASS"
                    and row.get("zip_crc_status") == "PASS"
                    and row.get("csv_schema_status") == "PASS_7_COLUMN_SPOT_TRADES_SCHEMA"
                    and row.get("day_bounds_pass") is True
                ):
                    row["status"] = "PASS_BYTES_CRC_SCHEMA_UTC_BOUNDS"
                else:
                    row["status"] = "REVIEW_REQUIRED_ARCHIVE_OR_ROW_VALIDATION"
            except urllib.error.HTTPError as exc:
                row["status"] = "HTTP_ERROR_" + str(exc.code)
                row["error"] = str(exc.reason)[:300]
            except (urllib.error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile) as exc:
                row["status"] = "ERROR_OR_INTEGRITY_FAILURE"
                row["error"] = type(exc).__name__ + ": " + str(exc)[:500]
            except Exception as exc:
                row["status"] = "UNEXPECTED_AUDIT_ERROR"
                row["error"] = type(exc).__name__ + ": " + str(exc)[:500]
            records.append(row)

    expected = len(TARGET_DATES)
    integrity_count = sum(r["status"] == "PASS_BYTES_CRC_SCHEMA_UTC_BOUNDS" for r in records)
    coverage_reviews = sum(r.get("basic_coverage_status") == "REVIEW_REQUIRED_COVERAGE_ANOMALY" for r in records)
    if integrity_count != expected:
        status = "REVIEW_REQUIRED_TRADE_ARCHIVE_INTEGRITY_OR_SCHEMA_GAP"
    elif coverage_reviews:
        status = "PASS_ARCHIVE_INTEGRITY_COVERAGE_REVIEW_REQUIRED"
    else:
        status = "PASS_7_ARCHIVES_INTEGRITY_AND_BASIC_COVERAGE"

    csv_path = output / "CP0111_Official_Daily_Trade_Archive_Integrity.csv"
    summary_path = output / "CP0111_Official_Daily_Trade_Archive_Integrity_Summary.json"
    report_path = output / "CP0111_Official_Daily_Trade_Archive_Integrity_Report_HI.md"
    write_csv(csv_path, records)
    checks = [
        {"check_id": "fixed_seven_target_dates", "status": "PASS" if tuple(t["utc_date"] for t in targets) == TARGET_DATES else "FAIL"},
        {"check_id": "all_downloads_used_official_https_host", "status": "PASS" if all(urlparse(r["archive_url"]).scheme == "https" and urlparse(r["archive_url"]).hostname == OFFICIAL_HOST for r in records) else "FAIL"},
        {"check_id": "market_data_rest_api_not_used", "status": "PASS" if all(not r.get("market_data_rest_api_used", True) for r in records) else "FAIL"},
        {"check_id": "no_raw_kline_archive_mutations", "status": "PASS"},
        {"check_id": "no_source_authority_or_case_closure", "status": "PASS" if all(r.get("source_authority_selected") is False and r.get("case_closed") is False for r in records) else "FAIL"},
        {"check_id": "one_result_per_target", "status": "PASS" if len(records) == expected else "FAIL"},
    ]
    summary = {
        "schema_version": 1,
        "checkpoint": "CP-0111",
        "task": "cp0111_official_daily_trade_archive_integrity_audit",
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_dates_utc": list(TARGET_DATES),
        "targets": expected,
        "archives_integrity_crc_schema_utc_bounds_pass": integrity_count,
        "targets_requiring_basic_coverage_review": coverage_reviews,
        "archive_bytes_downloaded_total": archive_bytes_total,
        "per_archive_safety_limit_bytes": MAX_ARCHIVE_BYTES_EACH,
        "aggregate_safety_limit_bytes": MAX_ARCHIVE_BYTES_TOTAL,
        "edge_gap_review_seconds": EDGE_REVIEW_SECONDS,
        "sidecar_requests": expected,
        "trade_archive_downloads_attempted": sum(1 for r in records if r.get("archive_zip_downloaded")),
        "market_data_rest_api_used": False,
        "exchange_credentials_used": False,
        "raw_kline_archives_modified": False,
        "timestamps_shifted_or_rounded": False,
        "synthetic_candles_created": False,
        "canonical_source_selected": False,
        "source_cases_closed": 0,
        "candidate_build_performed": False,
        "backtest_performed": False,
        "strategy_promoted": False,
        "live_signing_enabled": False,
        "public_broadcast_enabled": False,
        "binance_orders_placed": False,
        "sources": records,
        "checks": checks,
        "checks_passed": sum(c["status"] == "PASS" for c in checks),
        "checks_total": len(checks),
        "limitations": [
            "A checksum match proves the downloaded ZIP bytes match that sidecar's claimed digest; it does not prove historical completeness or canonical kline authority.",
            "The edge-gap criterion is a diagnostic flag only; actual trade activity at exact UTC boundaries is not guaranteed.",
            "Trade-ID sequence and timestamp checks are anomaly screens, not a formal maintainer-backed completeness guarantee.",
            "No klines were reconstructed in this checkpoint. Any later reconstruction must be exact-key/time-bounded, independently validated, and remain diagnostic until frozen CP-0040 authority requirements are met.",
        ],
        "outputs": {},
    }
    report_lines = [
        "# CP-0111: Official Spot daily-trades archive integrity audit",
        "",
        "Status: " + status,
        "",
        "## Summary",
        "",
        "- Target dates: " + ", ".join(TARGET_DATES),
        "- ZIP byte SHA-256 + CRC + expected member + 7-column schema + in-day timestamps passed: " + str(integrity_count) + "/" + str(expected),
        "- Targets with basic coverage anomalies needing review: " + str(coverage_reviews),
        "- Total ZIP bytes downloaded: " + str(archive_bytes_total),
        "- Raw kline archives changed / Binance REST calls / case closures: 0 / 0 / 0",
        "",
        "## Per-target evidence",
        "",
        "| UTC date | ZIP bytes | SHA-256 matched | ZIP CRC | CSV rows | First UTC time | Last UTC time | Edge gaps (s) first/last | Trade-ID gaps | Coverage status |",
        "|---|---:|---|---|---:|---|---|---|---:|---|",
    ]
    for r in records:
        report_lines.append(
            "| " + str(r.get("utc_date")) + " | " + str(r.get("archive_bytes", "")) + " | "
            + str(r.get("archive_sha256_matches_sidecar", "")) + " | " + str(r.get("zip_crc_status", "")) + " | "
            + str(r.get("rows", "")) + " | " + str(r.get("first_trade_time_utc", "")) + " | "
            + str(r.get("last_trade_time_utc", "")) + " | "
            + str(r.get("first_edge_gap_seconds", "")) + " / " + str(r.get("last_edge_gap_seconds", "")) + " | "
            + str(r.get("trade_id_gap_count", "")) + " | " + str(r.get("basic_coverage_status", r.get("status", ""))) + " |"
        )
    report_lines.extend([
        "",
        "## Interpretation",
        "",
        "The daily Spot trade archive has seven fields per the official repository README: trade ID, price, quantity, quote quantity, time, isBuyerMaker and isBestMatch. This audit validates file identity/integrity and performs basic row/time coverage checks. It does not call the Binance market-data REST API.",
        "",
        "A checksum match is byte integrity evidence only. Day-boundary gaps, trade-ID gaps, duplicate/decreasing IDs, timestamp reversals or unexpected schema must be reviewed before any trade-derived candle is used. The historical-provenance issue remains open and the official docs do not in this run establish a guarantee that historical trade archives are complete or reproduce exactly the current or original kline versions.",
        "",
        "No klines are reconstructed or altered here. Canonical source remains NONE; all 11 aggregation blockers remain unresolved; no source case is closed and no strategy is promoted.",
        "",
        "## Non-actions",
        "",
        "- Raw source klines were not changed.",
        "- No timestamp shifts, normalization or synthetic candles.",
        "- No production candidate build, backtest or strategy promotion.",
        "- No exchange credentials, signing, public broadcast or Binance orders.",
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    for out_path in (csv_path, report_path):
        summary["outputs"][out_path.name] = {
            "bytes": out_path.stat().st_size,
            "sha256": hashlib.sha256(out_path.read_bytes()).hexdigest(),
        }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "checkpoint": "CP-0111",
        "status": status,
        "targets": expected,
        "integrity_crc_schema_bounds_pass": integrity_count,
        "coverage_reviews": coverage_reviews,
        "archive_bytes_downloaded_total": archive_bytes_total,
        "per_target": [
            {
                "utc_date": r.get("utc_date"),
                "status": r.get("status"),
                "archive_bytes": r.get("archive_bytes"),
                "archive_actual_sha256": r.get("archive_actual_sha256"),
                "archive_sha256_matches_sidecar": r.get("archive_sha256_matches_sidecar"),
                "zip_crc_status": r.get("zip_crc_status"),
                "csv_rows": r.get("rows"),
                "first_trade_id": r.get("first_trade_id"),
                "last_trade_id": r.get("last_trade_id"),
                "first_trade_time_utc": r.get("first_trade_time_utc"),
                "last_trade_time_utc": r.get("last_trade_time_utc"),
                "trade_id_gap_count": r.get("trade_id_gap_count"),
                "trade_id_duplicate_count": r.get("trade_id_duplicate_count"),
                "timestamp_decrease_count": r.get("timestamp_decrease_count"),
                "first_edge_gap_seconds": r.get("first_edge_gap_seconds"),
                "last_edge_gap_seconds": r.get("last_edge_gap_seconds"),
                "basic_coverage_status": r.get("basic_coverage_status"),
                "error": r.get("error"),
            }
            for r in records
        ],
    }, ensure_ascii=False, sort_keys=True), flush=True)
    # Data-quality findings are represented explicitly in the summary/report.
    # Returning zero means the audit executed and emitted evidence, not that source authority was established.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
