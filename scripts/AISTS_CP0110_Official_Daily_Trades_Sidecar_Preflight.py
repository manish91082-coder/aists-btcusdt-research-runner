#!/usr/bin/env python3
"""Bounded, read-only availability preflight for seven official Binance Spot daily-trades checksum sidecars."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOST = "data.binance.vision"
TIMEOUT_SECONDS = 20
MAX_SIDECAR_BYTES = 4096
TARGET_DATES = (
    "2017-12-04",
    "2018-02-05",
    "2018-02-07",
    "2018-03-04",
    "2018-03-20",
    "2018-06-20",
    "2018-09-05",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_checksum_body(body: bytes, expected_filename: str) -> dict:
    """Parse a sidecar without assuming its hash token authenticates downloaded archive bytes."""
    try:
        decoded = body.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {
            "utf8_valid": False,
            "text": "",
            "sha256_tokens": [],
            "filename_present": False,
            "parse_valid": False,
        }
    text = decoded.strip()
    tokens = re.findall(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text)
    filename_present = expected_filename in text
    return {
        "utf8_valid": True,
        "text": text,
        "sha256_tokens": [x.lower() for x in tokens],
        "filename_present": filename_present,
        "parse_valid": len(tokens) == 1 and filename_present,
    }


class SameHostHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Permit redirects only when they stay on the allowlisted HTTPS host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
            raise urllib.error.HTTPError(
                newurl, code, "Blocked redirect outside allowlisted HTTPS host", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_target(utc_date: str) -> dict:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", utc_date):
        raise ValueError("Unexpected fixed target date")
    filename = "BTCUSDT-trades-" + utc_date + ".zip"
    url = (
        "https://" + OFFICIAL_HOST + "/data/spot/daily/trades/BTCUSDT/"
        + filename + ".CHECKSUM"
    )
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != OFFICIAL_HOST:
        raise ValueError("Target URL failed the official-host allowlist")
    return {
        "utc_date": utc_date,
        "archive_filename": filename,
        "sidecar_filename": filename + ".CHECKSUM",
        "url": url,
    }


def run_self_tests() -> list[dict]:
    fixture_hash = "a" * 64
    body = (fixture_hash + "  BTCUSDT-trades-2017-12-04.zip\n").encode("utf-8")
    cases = [
        ("valid_sidecar_body", parse_checksum_body(body, "BTCUSDT-trades-2017-12-04.zip")["parse_valid"]),
        ("wrong_expected_filename_rejected", not parse_checksum_body(body, "BTCUSDT-trades-2017-12-05.zip")["parse_valid"]),
        ("missing_hash_rejected", not parse_checksum_body(b"BTCUSDT-trades-2017-12-04.zip\n", "BTCUSDT-trades-2017-12-04.zip")["parse_valid"]),
        ("multiple_hashes_rejected", not parse_checksum_body((fixture_hash + " " + "b" * 64 + " BTCUSDT-trades-2017-12-04.zip").encode(), "BTCUSDT-trades-2017-12-04.zip")["parse_valid"]),
        ("invalid_utf8_rejected", not parse_checksum_body(b"\xff", "BTCUSDT-trades-2017-12-04.zip")["parse_valid"]),
    ]
    return [
        {"check_id": name, "status": "PASS" if passed else "FAIL", "detail": "fixed parser fixture"}
        for name, passed in cases
    ]


def probe_target(target: dict, opener, sidecar_dir: Path) -> dict:
    record = {
        **target,
        "request_attempted": True,
        "request_method": "GET",
        "requested_resource_type": "text_only_checksum_sidecar",
        "official_host_allowlist": OFFICIAL_HOST,
        "http_status": None,
        "final_url": None,
        "response_headers": {},
        "sidecar_bytes": None,
        "sidecar_body_sha256": None,
        "checksum_sha256_token": None,
        "checksum_token_count": 0,
        "filename_present_in_sidecar": False,
        "sidecar_saved": False,
        "archive_zip_downloaded": False,
        "market_data_rest_api_used": False,
        "source_authority_selected": False,
        "case_closed": False,
    }
    request = urllib.request.Request(
        target["url"],
        headers={
            "User-Agent": "AISTS-CP0110-Official-Trade-Sidecar-Preflight/1.0",
            "Accept": "text/plain",
        },
        method="GET",
    )
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            parsed_final = urlparse(final_url)
            status = getattr(response, "status", None)
            body = response.read(MAX_SIDECAR_BYTES + 1)
            headers = response.headers
        record["final_url"] = final_url
        record["http_status"] = status
        record["response_headers"] = {
            key: headers.get(key)
            for key in ("Date", "ETag", "Last-Modified", "Content-Type", "Content-Length")
        }
        record["sidecar_bytes"] = len(body)
        record["sidecar_body_sha256"] = sha_bytes(body)
        record["final_host_allowlist_pass"] = (
            parsed_final.scheme == "https" and parsed_final.hostname == OFFICIAL_HOST
        )
        if not record["final_host_allowlist_pass"]:
            record["status"] = "BLOCKED_REDIRECT_OUTSIDE_OFFICIAL_HOST"
            return record
        if status != 200:
            record["status"] = "HTTP_STATUS_" + str(status)
            return record
        if len(body) > MAX_SIDECAR_BYTES:
            record["status"] = "SIDECAR_BODY_EXCEEDS_LIMIT"
            return record

        parsed = parse_checksum_body(body, target["archive_filename"])
        record["sidecar_utf8_valid"] = parsed["utf8_valid"]
        record["checksum_sha256_token"] = (
            parsed["sha256_tokens"][0] if len(parsed["sha256_tokens"]) == 1 else None
        )
        record["checksum_token_count"] = len(parsed["sha256_tokens"])
        record["filename_present_in_sidecar"] = parsed["filename_present"]
        if not parsed["parse_valid"]:
            record["status"] = "HTTP_200_MALFORMED_CHECKSUM_SIDECAR"
            return record

        sidecar_dir.mkdir(parents=True, exist_ok=True)
        sidecar_path = sidecar_dir / target["sidecar_filename"]
        sidecar_path.write_bytes(body)
        record["sidecar_saved"] = sidecar_path.read_bytes() == body
        record["sidecar_saved_path"] = str(sidecar_path.relative_to(ROOT))
        record["status"] = (
            "AVAILABLE_VALID_CHECKSUM_SIDECAR"
            if record["sidecar_saved"]
            else "SIDECAR_PERSISTENCE_MISMATCH"
        )
        return record
    except urllib.error.HTTPError as exc:
        record["http_status"] = exc.code
        record["status"] = "HTTP_ERROR_" + str(exc.code)
        record["error"] = str(exc.reason)[:300]
        return record
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        record["status"] = "NETWORK_OR_URL_ERROR"
        record["error"] = type(exc).__name__ + ": " + str(exc)[:300]
        return record
    except Exception as exc:
        record["status"] = "UNEXPECTED_PROBE_ERROR"
        record["error"] = type(exc).__name__ + ": " + str(exc)[:300]
        return record


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "utc_date", "archive_filename", "sidecar_filename", "url", "status",
        "http_status", "final_url", "sidecar_bytes", "sidecar_body_sha256",
        "checksum_sha256_token", "checksum_token_count", "filename_present_in_sidecar",
        "sidecar_saved", "sidecar_saved_path", "archive_zip_downloaded",
        "market_data_rest_api_used", "source_authority_selected", "case_closed", "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/cp0110_official_trade_sidecar_preflight")
    args = parser.parse_args()
    output_dir = (ROOT / args.output_dir).resolve()
    if ROOT not in output_dir.parents and output_dir != ROOT:
        raise ValueError("Output directory must remain inside repository root")
    output_dir.mkdir(parents=True, exist_ok=True)
    sidecar_dir = output_dir / "sidecars"

    checks = run_self_tests()
    if any(item["status"] != "PASS" for item in checks):
        raise RuntimeError("Sidecar parser self-tests failed; network probe is blocked")

    opener = urllib.request.build_opener(SameHostHTTPSRedirectHandler())
    targets = [build_target(date) for date in TARGET_DATES]
    results = [probe_target(target, opener, sidecar_dir) for target in targets]
    expected = len(TARGET_DATES)
    valid_count = sum(r["status"] == "AVAILABLE_VALID_CHECKSUM_SIDECAR" for r in results)
    status = (
        "PASS_ALL_7_OFFICIAL_TRADE_SIDECARS_AVAILABLE"
        if valid_count == expected
        else "REVIEW_REQUIRED_TRADE_SIDECAR_AVAILABILITY_GAP"
    )

    checks.extend([
        {
            "check_id": "target_set_fixed_and_exact",
            "status": "PASS" if len(targets) == 7 and tuple(t["utc_date"] for t in targets) == TARGET_DATES else "FAIL",
            "detail": "Seven fixed UTC dates; no caller-provided URLs",
        },
        {
            "check_id": "only_official_checksum_sidecars_requested",
            "status": "PASS" if all(urlparse(t["url"]).hostname == OFFICIAL_HOST and t["url"].endswith(".zip.CHECKSUM") for t in targets) else "FAIL",
            "detail": "HTTPS data.binance.vision checksum URLs only",
        },
        {
            "check_id": "no_trade_archives_or_market_data_rest_api",
            "status": "PASS" if all(not r["archive_zip_downloaded"] and not r["market_data_rest_api_used"] for r in results) else "FAIL",
            "detail": "Metadata-only preflight; archive ZIPs were not requested",
        },
        {
            "check_id": "one_probe_record_per_target",
            "status": "PASS" if len(results) == expected and all(r["request_attempted"] for r in results) else "FAIL",
            "detail": "probe_records=" + str(len(results)) + " expected=" + str(expected),
        },
    ])

    summary = {
        "schema_version": 1,
        "checkpoint": "CP-0110",
        "task": "cp0110_official_trade_sidecar_preflight",
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "symbol": "BTCUSDT",
            "data_product": "official Binance Spot daily trade archives",
            "target_dates_utc": list(TARGET_DATES),
            "targets": expected,
            "valid_checksum_sidecars_available": valid_count,
            "archive_zip_downloaded": False,
            "market_data_rest_api_used": False,
            "exchange_credentials_used": False,
            "raw_klines_modified": False,
            "synthetic_candles_created": False,
            "timestamps_shifted_or_rounded": False,
            "canonical_source_selected": False,
            "source_cases_closed": 0,
            "candidate_build_performed": False,
            "backtest_performed": False,
            "strategy_promoted": False,
            "live_signing_enabled": False,
            "public_broadcast_enabled": False,
            "binance_orders_placed": False,
        },
        "interpretation": (
            "This preflight checks whether the seven official checksum sidecars can be fetched and parsed. "
            "A sidecar token is not independently verified against archive bytes because no archive ZIP was downloaded. "
            "Availability does not establish trade-data completeness, kline equivalence, historical version authority, "
            "canonical source, or case closure."
        ),
        "sources": results,
        "checks": checks,
        "checks_passed": sum(c["status"] == "PASS" for c in checks),
        "checks_total": len(checks),
        "outputs": {},
        "next_bounded_step": (
            "Only if all seven sidecars are available, assess a separately scoped official daily-trades archive reconstruction. "
            "Before downloading any trade ZIP, validate the completeness assumptions for each full UTC day. "
            "Do not use Binance market-data REST endpoints or change frozen kline data."
        ),
    }

    csv_path = output_dir / "CP0110_Official_Daily_Trades_Sidecar_Preflight.csv"
    summary_path = output_dir / "CP0110_Official_Daily_Trades_Sidecar_Preflight_Summary.json"
    report_path = output_dir / "CP0110_Official_Daily_Trades_Sidecar_Preflight_Report_HI.md"
    write_csv(csv_path, results)

    report_lines = [
        "# CP-0110: Official daily-trades checksum-sidecar availability preflight",
        "",
        "Status: " + status,
        "",
        "## Scope",
        "",
        "- Exact target dates (UTC): " + ", ".join(TARGET_DATES),
        "- Valid sidecars found: " + str(valid_count) + "/" + str(expected),
        "- Requests: HTTPS text-only checksum sidecars from data.binance.vision.",
        "- Daily trade ZIPs downloaded: 0.",
        "- Binance market-data REST API calls: 0.",
        "- Raw kline/source bytes changed: no.",
        "- Canonical source selected / source cases closed: no / 0.",
        "",
        "## Per-target results",
        "",
        "| UTC date | Sidecar | HTTP | Status | Sidecar SHA-256 | Archive SHA token |",
        "|---|---|---:|---|---|---|",
    ]
    for row in results:
        report_lines.append(
            "| {date} | {sidecar} | {http} | {status} | {body_hash} | {archive_hash} |".format(
                date=row["utc_date"],
                sidecar=row["sidecar_filename"],
                http=row["http_status"] if row["http_status"] is not None else "none",
                status=row["status"],
                body_hash=row["sidecar_body_sha256"] or "not available",
                archive_hash=row["checksum_sha256_token"] or "not available",
            )
        )
    report_lines.extend([
        "",
        "## Interpretation and limits",
        "",
        "A reachable checksum file reports a SHA-256 token for the named ZIP. Because this task does not download that ZIP, the token is not independently verified against archive bytes. Reachable sidecars do not prove that the underlying trade archive is complete, reconstructs every kline field, or establishes historical kline-source authority.",
        "",
        "The official Binance public-data README describes daily/monthly downloadable files and says each ZIP has a same-folder checksum file. Official repository issue #316 also shows the daily Spot-trades archive path, but its example records a maintenance-related short day on 2018-02-08. That date is not one of these seven target dates; it warns that full-day trade coverage must be independently validated.",
        "",
        "All 11 aggregation blockers remain unresolved. No source is selected and no cases are closed. This probe is not data adjudication, kline reconstruction, a strategy result, or a gate pass.",
        "",
        "## Safety and non-actions",
        "",
        "- No ZIP archive downloaded.",
        "- No Binance market-data REST endpoint called.",
        "- No kline rows or timestamps edited or normalized.",
        "- No synthetic candles, candidate build, backtest, or promotion.",
        "- Live signing, public broadcast, and Binance orders remain blocked.",
        "",
        "## Next bounded step",
        "",
        summary["next_bounded_step"],
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    for out_path in (csv_path, report_path):
        summary["outputs"][out_path.name] = {
            "bytes": out_path.stat().st_size,
            "sha256": sha_bytes(out_path.read_bytes()),
        }
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "checkpoint": "CP-0110",
        "status": status,
        "targets": expected,
        "valid_sidecars_available": valid_count,
        "archive_zip_downloaded": False,
        "market_data_rest_api_used": False,
        "source_cases_closed": 0,
        "output_summary": str(summary_path.relative_to(ROOT)),
    }, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
