#!/usr/bin/env python3
"""Resumable collector for checksum-verified official BTCUSDT monthly archives."""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://data.binance.vision"
SYMBOL = "BTCUSDT"
UA = "aists-btcusdt-research-runner/1.0"
COLUMNS = 12


def months_between(start: str, end: str) -> list[str]:
    def parse(value: str) -> tuple[int, int]:
        try:
            year, month = map(int, value.split("-"))
            if len(value) != 7 or not 1 <= month <= 12:
                raise ValueError
            return year, month
        except Exception as exc:
            raise ValueError(f"invalid YYYY-MM month: {value}") from exc
    sy, sm = parse(start)
    ey, em = parse(end)
    a, b = sy * 12 + sm - 1, ey * 12 + em - 1
    if b < a:
        raise ValueError("end month precedes start month")
    if b - a > 119:
        raise ValueError("single invocation is limited to 120 months")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}" for i in range(a, b + 1)]


def request_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read()


def timestamp_ms(value: str) -> int:
    raw = int(value)
    return raw // 1000 if raw >= 100_000_000_000_000 else raw


def validate_archive(payload: bytes, month: str, dataset: str) -> dict:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        if len(members) != 1:
            raise ValueError(f"expected one data member, got {len(members)}")
        member = members[0]
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        raw = archive.read(member)
    rows = csv.reader(io.StringIO(raw.decode("utf-8-sig")))
    first, count, previous = None, 0, None
    year, mon = map(int, month.split("-"))
    start = int(datetime(year, mon, 1, tzinfo=timezone.utc).timestamp() * 1000)
    days = calendar.monthrange(year, mon)[1]
    end = start + days * 86_400_000
    expected_rows = days * 1440
    if dataset.endswith("klines_1m"):
        for line_no, row in enumerate(rows, 1):
            if not row:
                continue
            # Binance Spot archives commonly omit headers; newer UM archives may include one.
            if line_no == 1 and row[0].strip().lower() in {"open_time", "open time", "open_time_ms"}:
                if len(row) != COLUMNS:
                    raise ValueError(f"row {line_no}: unexpected kline header width {len(row)}")
                continue
            if len(row) != COLUMNS:
                raise ValueError(f"row {line_no}: expected 12 columns, got {len(row)}")
            ts = timestamp_ms(row[0])
            if not start <= ts < end or (ts - start) % 60_000:
                raise ValueError(f"row {line_no}: timestamp outside month or off 1m grid")
            if previous is not None and ts - previous != 60_000:
                raise ValueError(f"row {line_no}: duplicate, gap, or ordering issue")
            values = [float(row[i]) for i in range(1, 6)]
            if not all(math.isfinite(x) for x in values) or min(values[:4]) <= 0 or values[4] < 0:
                raise ValueError(f"row {line_no}: invalid OHLCV numeric value")
            op, high, low, close, volume = values
            if high < max(op, close, low) or low > min(op, close, high):
                raise ValueError(f"row {line_no}: inconsistent OHLC")
            close_ts = timestamp_ms(row[6])
            if close_ts < ts or close_ts > ts + 60_000:
                raise ValueError(f"row {line_no}: invalid close timestamp")
            float(row[7])
            int(row[8])
            float(row[9])
            float(row[10])
            previous = ts
            first = ts if first is None else first
            count += 1
        if count != expected_rows:
            raise ValueError(f"expected {expected_rows} monthly 1m candles, found {count}")
        return {"member": member, "rows": count, "expected_rows": expected_rows,
                "first_open_time_ms": first, "last_open_time_ms": previous,
                "continuous_1m_grid": True, "ohlcv_valid": True}
    # Funding archives have had more than one published schema.
    all_rows = list(rows)
    if not all_rows:
        raise ValueError("empty funding archive")
    header = [v.strip().lower() for v in all_rows[0]]
    legacy = header[:3] == ["calc_time", "funding_rate", "funding_rate_timestamp"]
    current = header[:3] == ["calc_time", "funding_interval_hours", "last_funding_rate"]
    if not (legacy or current):
        raise ValueError(f"unexpected funding schema: {header[:3]}")
    previous = None
    for line_no, row in enumerate(all_rows[1:], 2):
        ts = timestamp_ms(row[0])
        if not start <= ts < end:
            raise ValueError(f"funding row {line_no}: timestamp outside month")
        if previous is not None and ts <= previous:
            raise ValueError(f"funding row {line_no}: duplicate or unsorted timestamp")
        rate = float(row[1] if legacy else row[2])
        if not math.isfinite(rate) or abs(rate) > 1:
            raise ValueError(f"funding row {line_no}: invalid funding rate")
        if legacy:
            int(row[2])
        else:
            interval = float(row[1])
            if not math.isfinite(interval) or not 0 < interval <= 24:
                raise ValueError(f"funding row {line_no}: invalid interval")
        previous = ts
        count += 1
    if count == 0:
        raise ValueError("funding archive has no event rows")
    return {"member": member, "rows": count, "schema": "legacy" if legacy else "current",
            "first_calc_time_ms": timestamp_ms(all_rows[1][0]),
            "last_calc_time_ms": previous, "timestamps_unique_ascending": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-month", required=True)
    parser.add_argument("--end-month", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include-funding", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.12)
    args = parser.parse_args()
    periods = months_between(args.start_month, args.end_month)
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    records = []
    jobs = []
    for month in periods:
        jobs.append((month, "spot_klines_1m", f"{BASE}/data/spot/monthly/klines/{SYMBOL}/1m/{SYMBOL}-1m-{month}.zip"))
        jobs.append((month, "um_klines_1m", f"{BASE}/data/futures/um/monthly/klines/{SYMBOL}/1m/{SYMBOL}-1m-{month}.zip"))
        if args.include_funding:
            jobs.append((month, "um_funding", f"{BASE}/data/futures/um/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{month}.zip"))
    for idx, (month, dataset, url) in enumerate(jobs, 1):
        filename = f"{month}_{dataset}.zip"
        target = root / filename
        record = {"month": month, "dataset": dataset, "url": url, "file": filename}
        try:
            payload = target.read_bytes() if target.exists() and target.stat().st_size else request_bytes(url)
            reused = target.exists() and target.stat().st_size > 0
            digest = hashlib.sha256(payload).hexdigest()
            checksum_text = request_bytes(url + ".CHECKSUM").decode("utf-8-sig").strip()
            expected = checksum_text.split()[0].lower()
            if digest != expected:
                raise ValueError("official SHA-256 sidecar mismatch")
            validation = validate_archive(payload, month, dataset)
            if not reused:
                target.write_bytes(payload)
            record.update({"status": "PASS", "bytes": len(payload), "sha256": digest,
                           "official_checksum": expected, "reused_existing": reused,
                           "validation": validation})
        except urllib.error.HTTPError as exc:
            record.update({"status": "UNAVAILABLE" if exc.code == 404 else "FAIL",
                           "error": f"HTTP {exc.code}"})
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile,
                RuntimeError, UnicodeDecodeError, csv.Error) as exc:
            record.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
        records.append(record)
        if idx % 25 == 0:
            print(json.dumps({"processed": idx, "total": len(jobs), "last": record}, ensure_ascii=False))
        time.sleep(max(0, args.sleep_seconds))
    summary = {
        "dataset": "BTCUSDT official monthly archive collection",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": SYMBOL, "canonical_candle_interval": "1m",
        "larger_intervals": "derive from validated 1m data; avoid duplicating raw candle archives",
        "periods_requested": periods,
        "source": "Binance public archive plus official adjacent .CHECKSUM sidecars",
        "counts": {key: sum(1 for r in records if r["status"] == key)
                   for key in ("PASS", "UNAVAILABLE", "FAIL")},
        "archives": records,
        "limitations": [
            "HTTP 404 means this archive URL was unavailable, not proof the instrument did not exist.",
            "Each candle archive must pass row count, 1m grid, timestamp, numeric OHLCV, OHLC relation and close-time checks.",
            "Funding schemas are validated but event-time economics must still be reviewed before backtesting.",
            "Workflow artifacts expire; long-term durable storage must be configured separately.",
            "No missing data is synthesized; Spot and Futures coverage can begin at different dates."
        ]
    }
    manifest = root / "btc-usdt-archive-collection-manifest.json"
    manifest.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "counts": summary["counts"],
                      "archives_requested": len(records)}, indent=2))
    return 1 if summary["counts"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
