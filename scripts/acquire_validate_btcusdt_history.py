#!/usr/bin/env python3
"""Download and validate official Binance BTCUSDT monthly Spot/UM 5m and UM funding archives."""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import re
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://data.binance.vision"
SYMBOL = "BTCUSDT"
UA = "aists-btcusdt-research-runner/1.0"
KLINE_FIELDS = 12


def month_range(start: str, end: str) -> list[str]:
    if not re.fullmatch(r"\d{4}-\d{2}", start) or not re.fullmatch(r"\d{4}-\d{2}", end):
        raise ValueError("Months must use YYYY-MM")
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    if not 1 <= sm <= 12 or not 1 <= em <= 12:
        raise ValueError("Month must be between 01 and 12")
    a, b = sy * 12 + sm - 1, ey * 12 + em - 1
    if b < a:
        raise ValueError("end-month must not precede start-month")
    if b - a > 5:
        raise ValueError("A single run is limited to 6 months")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}" for i in range(a, b + 1)]


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read()


def month_bounds_ms(period: str) -> tuple[int, int]:
    year, month = map(int, period.split("-"))
    start = int(datetime(year, month, 1, tzinfo=timezone.utc).timestamp() * 1000)
    days = calendar.monthrange(year, month)[1]
    end = int(datetime(year, month, days, 23, 59, 59, 999000, tzinfo=timezone.utc).timestamp() * 1000)
    return start, end


def finite_float(value: str, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite {field}: {value}")
    return result


def validate_klines(rows: list[list[str]], period: str, header: bool, venue: str) -> dict:
    if not rows:
        raise ValueError("empty kline CSV")
    expected_header = ["open_time", "open", "high", "low", "close", "volume"]
    actual_header = [x.strip().lower() for x in rows[0][:6]] == expected_header
    # Binance archive schema changed over time: some UM kline months include
    # a header while older monthly files start directly with candle data.
    # Detect the actual file shape instead of trusting a date-wide assumption.
    if actual_header:
        rows = rows[1:]
    elif header:
        try:
            int(rows[0][0])
        except (ValueError, IndexError) as exc:
            raise ValueError(f"unexpected kline header/data row: {rows[0][:6]}") from exc
    if not rows:
        raise ValueError("no data rows after header")
    start_ms, end_ms = month_bounds_ms(period)
    expected = (end_ms - start_ms + 1) // 300000
    seen, previous = set(), None
    for i, row in enumerate(rows, 1):
        if len(row) != KLINE_FIELDS:
            raise ValueError(f"row {i}: expected 12 columns, got {len(row)}")
        raw_ts = int(row[0])
        # Binance Spot archives use microseconds for recent history; UM archives use milliseconds.
        ts = raw_ts // 1000 if raw_ts >= 100_000_000_000_000 else raw_ts
        if ts < start_ms or ts > end_ms or (ts - start_ms) % 300000:
            raise ValueError(f"row {i}: timestamp outside month or off 5m grid: raw={raw_ts}, normalized_ms={ts}")
        if ts in seen:
            raise ValueError(f"row {i}: duplicate timestamp {ts}")
        if previous is not None and ts - previous != 300000:
            raise ValueError(f"row {i}: gap or ordering error, delta={ts-previous}ms")
        seen.add(ts)
        previous = ts
        o, h, low, c, vol = [finite_float(row[j], f"column {j}") for j in range(1, 6)]
        if min(o, h, low, c) <= 0 or vol < 0:
            raise ValueError(f"row {i}: invalid price or negative volume")
        if h < max(o, c, low) or low > min(o, c, h):
            raise ValueError(f"row {i}: inconsistent OHLC")
        raw_close_ts = int(row[6])
        close_ts = raw_close_ts // 1000 if raw_close_ts >= 100_000_000_000_000 else raw_close_ts
        if close_ts < ts or close_ts > ts + 300000:
            raise ValueError(f"row {i}: invalid close time")
        finite_float(row[7], "quote volume")
        int(row[8])
        finite_float(row[9], "taker buy base volume")
        finite_float(row[10], "taker buy quote volume")
    if len(rows) != expected:
        raise ValueError(f"expected {expected} monthly 5m candles, found {len(rows)}")
    normalize_ms = lambda value: int(value) // 1000 if int(value) >= 100_000_000_000_000 else int(value)
    return {"rows": len(rows), "first_open_time_ms": normalize_ms(rows[0][0]),
            "last_open_time_ms": normalize_ms(rows[-1][0]), "continuous_5m_grid": True,
            "numeric_ohlcv_and_ohlc_relations_valid": True, "venue": venue, "header_present": actual_header}


def validate_funding(rows: list[list[str]], period: str) -> dict:
    if not rows:
        raise ValueError("empty funding CSV")
    header = [x.strip().lower() for x in rows[0]]
    # Binance has published both legacy and newer funding archive schemas.
    legacy = header[:3] == ["calc_time", "funding_rate", "funding_rate_timestamp"]
    current = header[:3] == ["calc_time", "funding_interval_hours", "last_funding_rate"]
    if not (legacy or current):
        raise ValueError(f"unexpected funding header: {rows[0][:3]}")
    data = rows[1:]
    if not data:
        raise ValueError("no funding data rows")
    start_ms, end_ms = month_bounds_ms(period)
    previous = None
    for i, row in enumerate(data, 1):
        if len(row) < 3:
            raise ValueError(f"funding row {i}: expected at least 3 columns")
        raw_ts = int(row[0])
        ts = raw_ts // 1000 if raw_ts >= 100_000_000_000_000 else raw_ts
        if not start_ms <= ts <= end_ms:
            raise ValueError(f"funding row {i}: timestamp outside month")
        if previous is not None and ts <= previous:
            raise ValueError(f"funding row {i}: duplicate or nonascending timestamp")
        rate_index = 1 if legacy else 2
        rate = finite_float(row[rate_index], "funding rate")
        if abs(rate) > 1:
            raise ValueError(f"funding row {i}: implausible funding rate {rate}")
        if legacy:
            int(row[2])
        else:
            interval_hours = finite_float(row[1], "funding interval hours")
            if interval_hours <= 0 or interval_hours > 24:
                raise ValueError(f"funding row {i}: invalid funding interval hours {interval_hours}")
        previous = ts
    normalize_ms = lambda value: int(value) // 1000 if int(value) >= 100_000_000_000_000 else int(value)
    return {"rows": len(data), "first_calc_time_ms": normalize_ms(data[0][0]),
            "last_calc_time_ms": normalize_ms(data[-1][0]), "timestamps_unique_ascending": True,
            "numeric_rates_finite": True}


def check_one(out_dir: Path, period: str, dataset: str, url: str, header: bool) -> dict:
    item = {"period": period, "dataset": dataset, "url": url,
            "checked_utc": datetime.now(timezone.utc).isoformat()}
    try:
        archive = fetch(url)
        checksum_text = fetch(url + ".CHECKSUM").decode("utf-8-sig").strip()
        expected_hash = checksum_text.split()[0].lower()
        actual_hash = hashlib.sha256(archive).hexdigest()
        item.update({"archive_bytes": len(archive), "archive_sha256": actual_hash,
                     "checksum_expected_sha256": expected_hash,
                     "checksum_matches": actual_hash == expected_hash,
                     "checksum_sidecar_url": url + ".CHECKSUM"})
        if not item["checksum_matches"]:
            raise ValueError("official SHA-256 sidecar mismatch")
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            members = [n for n in zf.namelist() if not n.endswith("/")]
            if len(members) != 1:
                raise ValueError(f"expected one CSV member, found {len(members)}")
            member = members[0]
            payload = zf.read(member)
        decoded = payload.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(decoded)))
        if dataset.endswith("funding"):
            validation = validate_funding(rows, period)
        else:
            validation = validate_klines(rows, period, header, dataset)
        safe_name = f"{period}_{dataset}.zip"
        (out_dir / safe_name).write_bytes(archive)
        item.update({"status": "PASS", "member_name": member, "saved_archive": safe_name,
                     "csv_content_sha256": hashlib.sha256(payload).hexdigest(),
                     "validation": validation})
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile) as exc:
        item.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
    return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-month", default="2026-07")
    parser.add_argument("--end-month", default="2026-09")
    parser.add_argument("--output-dir", default="artifacts/hd04-history")
    args = parser.parse_args()
    periods = month_range(args.start_month, args.end_month)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checks = []
    for period in periods:
        for dataset, url, header in [
            ("spot_klines", f"{BASE}/data/spot/monthly/klines/{SYMBOL}/5m/{SYMBOL}-5m-{period}.zip", False),
            ("um_klines", f"{BASE}/data/futures/um/monthly/klines/{SYMBOL}/5m/{SYMBOL}-5m-{period}.zip", True),
            ("um_funding", f"{BASE}/data/futures/um/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{period}.zip", True),
        ]:
            checks.append(check_one(out_dir, period, dataset, url, header))
            time.sleep(0.15)
    passed = sum(c["status"] == "PASS" for c in checks)
    report = {
        "gate": "BTCUSDT-MULTIMONTH-HISTORY-INTEGRITY",
        "symbol": SYMBOL, "interval": "5m", "months_requested": periods,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Official Binance public monthly archives; each archive checked against its adjacent .CHECKSUM file.",
        "limitations": ["This is a BTCUSDT historical sample, not full-universe discovery.",
                        "Checksum and integrity validation do not establish strategy profitability.",
                        "Funding rows are validated for schema, timestamps and finite rates; no fixed row count is assumed."],
        "summary": {"months": len(periods), "files_expected": len(checks),
                    "files_passed": passed, "files_failed": len(checks)-passed,
                    "overall": "PASS" if passed == len(checks) else "FAIL"},
        "checks": checks,
    }
    report_path = out_dir / "btc-usdt-multimonth-integrity-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), **report["summary"],
                      "failed": [{"period": c["period"], "dataset": c["dataset"], "error": c.get("error")}
                                 for c in checks if c["status"] != "PASS"]}, indent=2))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
