#!/usr/bin/env python3
"""Download and audit one official Binance daily kline archive.

Stdlib-only; intended for a network-enabled, zero-cost Python runtime such as Colab.
This is a research-data validator, not trading code. It never places orders.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

SPOT_BASE = "https://data.binance.vision/data/spot/daily/klines"
UM_BASE = "https://data.binance.vision/data/futures/um/daily/klines"
SPOT_API = "https://api.binance.com/api/v3/klines"
UM_API = "https://fapi.binance.com/fapi/v1/klines"
INTERVAL_MS = {
    "1m": 60_000, "3m": 180_000, "5m": 300_000, "15m": 900_000,
    "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000,
    "4h": 14_400_000, "6h": 21_600_000, "8h": 28_800_000,
    "12h": 43_200_000, "1d": 86_400_000, "3d": 259_200_000,
    "1w": 604_800_000,
}
# Binance archive kline CSV layout documented by the official public-data repository.
EXPECTED_COLUMNS = 12


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "binance-public-data-audit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def parse_official_checksum(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace").strip()
    # Official .CHECKSUM files typically begin with the hex digest, optionally followed by filename.
    match = re.match(r"^\s*([0-9a-fA-F]{64})(?:\s+.*)?$", text)
    if not match:
        raise ValueError(f"Unrecognised official checksum file format: {text[:160]!r}")
    return match.group(1).lower()


def timestamp_ms(raw_value: str, unit: str) -> int:
    value = int(raw_value)
    if unit == "us":
        if value % 1000:
            # Preserve sub-millisecond raw value, but normalize to milliseconds for API comparison.
            return value // 1000
        return value // 1000
    if unit == "ms":
        return value
    raise ValueError(f"Unsupported timestamp unit: {unit}")


def is_kline_header(row: list[str]) -> bool:
    """Recognize documented verbose and abbreviated 12-column Binance kline headers."""
    if len(row) != EXPECTED_COLUMNS:
        return False
    normalise = lambda value: re.sub(r"[^a-z0-9]", "", value.strip().lower())
    observed = [normalise(value) for value in row]
    # Binance archives use both verbose field names (e.g. quote_asset_volume)
    # and abbreviated names (e.g. quote_volume, count, taker_buy_volume).
    accepted = [
        {"opentime"}, {"open"}, {"high"}, {"low"}, {"close"}, {"volume"},
        {"closetime"}, {"quoteassetvolume", "quotevolume"},
        {"numberoftrades", "count"},
        {"takerbuybaseassetvolume", "takerbuyvolume"},
        {"takerbuyquoteassetvolume", "takerbuyquotevolume"}, {"ignore"},
    ]
    return all(value in names for value, names in zip(observed, accepted))


def classify_api_sample_results(sample_results: list[dict]) -> str:
    """Distinguish a real API/data mismatch from a temporary inability to verify."""
    statuses = {item.get("status") for item in sample_results}
    if "FAIL" in statuses:
        return "FAIL"
    if "BLOCKED" in statuses:
        return "BLOCKED"
    return "PASS"


def classify_audit_status(checks: dict[str, str], required_checks: list[str]) -> str:
    """A proven required-check failure outranks blockers; otherwise preserve blocked status."""
    statuses = [checks.get(key) for key in required_checks]
    if any(status == "FAIL" or status == "FAIL_OR_BLOCKED" for status in statuses):
        return "FAIL"
    if any(status == "BLOCKED" for status in statuses):
        return "BLOCKED"
    if all(status == "PASS" for status in statuses):
        return "PASS"
    return "FAIL"


def api_candle(base: str, symbol: str, interval: str, open_time_ms: int) -> list:
    query = urllib.parse.urlencode({
        "symbol": symbol, "interval": interval, "startTime": open_time_ms, "limit": 1
    })
    payload = json.loads(fetch(f"{base}?{query}").decode("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"API returned no candle for open time {open_time_ms}: {payload!r}")
    return payload[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=("spot", "usdm"), required=True)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="5m", choices=tuple(INTERVAL_MS))
    parser.add_argument("--date", required=True, help="UTC archive date YYYY-MM-DD")
    parser.add_argument("--out", default="binance_audit_output")
    parser.add_argument("--api-samples", type=int, default=3, choices=(0, 1, 2, 3))
    args = parser.parse_args()

    try:
        archive_date = date.fromisoformat(args.date)
        if archive_date.isoformat() != args.date:
            raise ValueError("Date must be canonical YYYY-MM-DD.")
    except ValueError as exc:
        parser.error(str(exc))

    symbol = args.symbol.upper()
    if not re.fullmatch(r"[A-Z0-9]+", symbol):
        parser.error("Symbol must contain only ASCII letters and digits.")
    base = SPOT_BASE if args.market == "spot" else UM_BASE
    api_base = SPOT_API if args.market == "spot" else UM_API
    filename = f"{symbol}-{args.interval}-{args.date}.zip"
    url = f"{base}/{symbol}/{args.interval}/{filename}"
    checksum_url = url + ".CHECKSUM"
    # Official documented convention: Spot archive timestamps switched to microseconds on 2025-01-01;
    # USDⓈ-M Futures archive timestamps remain milliseconds. Record the chosen rule in the report.
    if args.market == "spot" and archive_date >= date(2025, 1, 1):
        ts_unit, ts_rule = "us", "official Spot archive convention from 2025-01-01"
    else:
        ts_unit, ts_rule = "ms", "official archive convention for this market/period"

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "audit_id": f"{args.market}-{symbol}-{args.interval}-{args.date}",
        "retrieved_at_utc": utc_now(),
        "market": args.market.upper(),
        "symbol": symbol,
        "interval": args.interval,
        "archive_date_utc": args.date,
        "source_url": url,
        "official_checksum_url": checksum_url,
        "timestamp_unit": ts_unit,
        "timestamp_unit_rule": ts_rule,
        "status": "BLOCKED",
        "checks": {},
        "csv_header_present": None,
        "errors": [],
        "limitations": [
            "Checksum validates bytes against the publisher's checksum, not economic correctness or completeness.",
            "API spot-check is bounded and does not establish complete archive correctness.",
            "Daily archive may be absent or unpublished; an HTTP/DNS failure is BLOCKED, not a data-quality FAIL."
        ],
    }

    try:
        archive_bytes = fetch(url)
        report["checks"]["archive_download"] = "PASS"
        report["source_file_bytes"] = len(archive_bytes)
        report["source_sha256"] = hashlib.sha256(archive_bytes).hexdigest()
        archive_path = out_dir / filename
        archive_path.write_bytes(archive_bytes)

        checksum_bytes = fetch(checksum_url)
        official_hash = parse_official_checksum(checksum_bytes)
        (out_dir / (filename + ".CHECKSUM")).write_bytes(checksum_bytes)
        report["official_checksum_sha256"] = official_hash
        report["checks"]["official_checksum_match"] = (
            "PASS" if report["source_sha256"] == official_hash else "FAIL"
        )
        if report["checks"]["official_checksum_match"] != "PASS":
            raise RuntimeError("Downloaded archive SHA-256 does not match official checksum.")

        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            csv_names = [n for n in names if n.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise RuntimeError(f"Expected exactly one CSV in ZIP; found {csv_names!r}")
            csv_name = csv_names[0]
            csv_bytes = zf.read(csv_name)
        report["checks"]["zip_integrity"] = "PASS"
        report["archive_member"] = csv_name
        (out_dir / Path(csv_name).name).write_bytes(csv_bytes)

        rows = []
        malformed = 0
        first_nonempty_record = True
        with io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8", newline="") as stream:
            for line_no, row in enumerate(csv.reader(stream), start=1):
                if not row or all(not x.strip() for x in row):
                    continue
                if first_nonempty_record:
                    first_nonempty_record = False
                    report["csv_header_present"] = is_kline_header(row)
                    if report["csv_header_present"]:
                        continue
                if len(row) != EXPECTED_COLUMNS:
                    malformed += 1
                    continue
                try:
                    # Validate numeric fields used in OHLCV and trade count.
                    open_raw, high_raw, low_raw, close_raw = map(Decimal, row[1:5])
                    volume = Decimal(row[5])
                    quote_volume = Decimal(row[7])
                    trades = int(row[8])
                    taker_base = Decimal(row[9])
                    taker_quote = Decimal(row[10])
                    open_ms = timestamp_ms(row[0], ts_unit)
                    close_ms = timestamp_ms(row[6], ts_unit)
                    if not all(x.is_finite() for x in (open_raw, high_raw, low_raw, close_raw,
                                                       volume, quote_volume, taker_base, taker_quote)):
                        raise ValueError("non-finite numeric value")
                    rows.append({
                        "line": line_no, "raw_open_time": row[0], "open_ms": open_ms,
                        "close_ms": close_ms, "open": open_raw, "high": high_raw,
                        "low": low_raw, "close": close_raw, "volume": volume,
                        "quote_volume": quote_volume, "trades": trades,
                        "taker_base": taker_base, "taker_quote": taker_quote, "raw": row
                    })
                except (ValueError, InvalidOperation, OverflowError):
                    malformed += 1

        report["row_count"] = len(rows)
        report["malformed_rows"] = malformed
        if not rows:
            raise RuntimeError("No valid 12-column kline rows were parsed.")
        if malformed:
            report["checks"]["row_schema"] = "FAIL"
        else:
            report["checks"]["row_schema"] = "PASS"

        opens = [r["open_ms"] for r in rows]
        duplicates = len(opens) - len(set(opens))
        out_of_order = sum(1 for a, b in zip(opens, opens[1:]) if b < a)
        interval_ms = INTERVAL_MS[args.interval]
        gaps = []
        for a, b in zip(opens, opens[1:]):
            if b > a + interval_ms:
                gaps.append({"after_open_ms": a, "before_open_ms": b,
                             "missing_interval_count": max(0, (b - a) // interval_ms - 1)})

        # For intervals that tile a UTC day, validate the day boundaries as well as
        # gaps between observed rows. Otherwise a missing first/last candle would be invisible.
        expected_opens = None
        boundary_missing = []
        if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0:
            day_start = int(datetime.combine(archive_date, datetime.min.time(), tzinfo=timezone.utc).timestamp() * 1000)
            expected_opens = list(range(day_start, day_start + 86_400_000, interval_ms))
            observed = set(opens)
            boundary_missing = [t for t in expected_opens if t not in observed]
        report["expected_candle_count_for_utc_day"] = len(expected_opens) if expected_opens is not None else None
        report["missing_expected_open_count_for_utc_day"] = len(boundary_missing)
        report["missing_expected_open_examples_utc"] = [
            datetime.fromtimestamp(t / 1000, timezone.utc).isoformat() for t in boundary_missing[:25]
        ]
        report["checks"]["utc_day_coverage"] = (
            "PASS" if expected_opens is not None and not boundary_missing else
            "FAIL" if expected_opens is not None else "NOT_APPLICABLE"
        )

        day_start_ms = int(datetime.combine(
            archive_date, datetime.min.time(), tzinfo=timezone.utc
        ).timestamp() * 1000)
        outside_archive_day = sum(
            1 for r in rows
            if not (day_start_ms <= r["open_ms"] < day_start_ms + 86_400_000)
        )
        misaligned_opens = 0
        wrong_close_times = 0
        if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0:
            misaligned_opens = sum(
                1 for r in rows if (r["open_ms"] - day_start_ms) % interval_ms != 0
            )
            # Kline close timestamps are inclusive: open + interval - 1 ms after
            # normalization of both millisecond and microsecond archive timestamps.
            wrong_close_times = sum(
                1 for r in rows if r["close_ms"] != r["open_ms"] + interval_ms - 1
            )
        report["rows_outside_archive_utc_day"] = outside_archive_day
        report["misaligned_open_timestamps"] = misaligned_opens if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0 else None
        report["unexpected_close_timestamps"] = wrong_close_times if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0 else None
        report["checks"]["archive_date_membership"] = "PASS" if outside_archive_day == 0 else "FAIL"
        report["checks"]["open_time_alignment"] = (
            "PASS" if misaligned_opens == 0 else "FAIL"
        ) if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0 else "NOT_APPLICABLE"
        report["checks"]["close_time_semantics"] = (
            "PASS" if wrong_close_times == 0 else "FAIL"
        ) if interval_ms <= 86_400_000 and 86_400_000 % interval_ms == 0 else "NOT_APPLICABLE"

        bad_ohlc = sum(1 for r in rows if not (
            r["low"] <= r["open"] <= r["high"] and
            r["low"] <= r["close"] <= r["high"] and r["low"] <= r["high"]
        ))
        negative_values = sum(1 for r in rows if (
            r["volume"] < 0 or r["quote_volume"] < 0 or r["trades"] < 0 or
            r["taker_base"] < 0 or r["taker_quote"] < 0
        ))
        report.update({
            "first_event_time_utc": datetime.fromtimestamp(min(opens) / 1000, timezone.utc).isoformat(),
            "last_event_time_utc": datetime.fromtimestamp(max(opens) / 1000, timezone.utc).isoformat(),
            "duplicate_rows": duplicates,
            "out_of_order_rows": out_of_order,
            "missing_interval_count": sum(g["missing_interval_count"] for g in gaps),
            "gap_examples": gaps[:25],
            "bad_ohlc_rows": bad_ohlc,
            "negative_volume_or_count_rows": negative_values,
            "first_raw_open_time": rows[0]["raw_open_time"],
            "last_raw_open_time": rows[-1]["raw_open_time"],
        })
        report["checks"]["duplicates"] = "PASS" if duplicates == 0 else "FAIL"
        report["checks"]["ordering"] = "PASS" if out_of_order == 0 else "FAIL"
        report["checks"]["gaps"] = "PASS" if not gaps else "FAIL"
        report["checks"]["ohlc_invariants"] = "PASS" if bad_ohlc == 0 else "FAIL"
        report["checks"]["nonnegative_volume_counts"] = "PASS" if negative_values == 0 else "FAIL"

        sample_results = []
        if args.api_samples:
            positions = sorted(set([0, len(rows) // 2, len(rows) - 1]))[:args.api_samples]
            for pos in positions:
                r = rows[pos]
                try:
                    candle = api_candle(api_base, symbol, args.interval, r["open_ms"])
                    # API times are milliseconds; compare timestamp and OHLCV fields using Decimal.
                    checks = {
                        "open_time": int(candle[0]) == r["open_ms"],
                        "open": Decimal(str(candle[1])) == r["open"],
                        "high": Decimal(str(candle[2])) == r["high"],
                        "low": Decimal(str(candle[3])) == r["low"],
                        "close": Decimal(str(candle[4])) == r["close"],
                        "volume": Decimal(str(candle[5])) == r["volume"],
                    }
                    passed = all(checks.values())
                    sample_results.append({"row_index": pos, "checks": checks, "status": "PASS" if passed else "FAIL"})
                except Exception as exc:
                    api_ok = False
                    sample_results.append({"row_index": pos, "status": "BLOCKED", "error": str(exc)})
            report["api_sample_results"] = sample_results
            report["checks"]["official_api_spot_check"] = classify_api_sample_results(sample_results)
        else:
            report["checks"]["official_api_spot_check"] = "NOT_RUN"

        required_checks = [
            "archive_download", "official_checksum_match", "zip_integrity", "row_schema",
            "duplicates", "ordering", "gaps", "utc_day_coverage", "archive_date_membership",
            "open_time_alignment", "close_time_semantics", "ohlc_invariants",
            "nonnegative_volume_counts", "official_api_spot_check"
        ]
        report["status"] = classify_audit_status(report["checks"], required_checks)
    except (urllib.error.URLError, TimeoutError, OSError, zipfile.BadZipFile, RuntimeError, ValueError) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["status"] = "BLOCKED" if isinstance(exc, (urllib.error.URLError, TimeoutError)) or "HTTP " in str(exc) else "FAIL"

    report["completed_at_utc"] = utc_now()
    report_path = out_dir / f"{report['audit_id']}.report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    print(f"\nReport written to: {report_path}")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
