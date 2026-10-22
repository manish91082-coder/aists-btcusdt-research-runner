#!/usr/bin/env python3
"""Download and validate Binance public September 2026 BTCUSDT 5m kline archives.

No API key is used. Original ZIPs and a machine-readable integrity report are
written beneath the requested output directory. Any failed validation exits 1.
"""
from __future__ import annotations

import argparse
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
from typing import Any

YEAR, MONTH = 2026, 9
SYMBOL, INTERVAL = "BTCUSDT", "5m"
INTERVAL_MS = 5 * 60 * 1000
EXPECTED_ROWS = 30 * 24 * 60 // 5
EXPECTED_FIRST_MS = int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp() * 1000)
EXPECTED_LAST_MS = EXPECTED_FIRST_MS + (EXPECTED_ROWS - 1) * INTERVAL_MS
COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trade_count", "taker_buy_base_volume",
    "taker_buy_quote_volume", "ignore",
]
NUMERIC_NONNEGATIVE = ["open", "high", "low", "close", "volume", "quote_volume",
                       "taker_buy_base_volume", "taker_buy_quote_volume"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get(url: str, attempts: int = 3) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "aists-btcusdt-research-runner/1.0"}
    )
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                return response.read()
        except Exception as exc:  # record and retry transient public archive failures
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Download failed after {attempts} attempts: {url}: {last}")


def timestamp_ms(value: str) -> int:
    n = int(value)
    # Binance archives have historically used milliseconds; tolerate microseconds
    # only when unambiguous, then normalize to milliseconds for validation.
    if n >= 100_000_000_000_000:
        return n // 1000
    return n


def validate_csv(blob: bytes, product: str) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"Expected exactly one CSV in ZIP; found {names}")
        raw = archive.read(names[0])
    text = io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8-sig", newline="")
    reader = csv.reader(text)
    rows = list(reader)
    if rows and rows[0] and rows[0][0].strip().lower() in {"open_time", "open time"}:
        rows = rows[1:]
    errors: list[str] = []
    if any(len(row) != 12 for row in rows):
        bad = sum(len(row) != 12 for row in rows)
        errors.append(f"{bad} row(s) do not have 12 kline fields")
    parsed: list[tuple[int, list[str]]] = []
    for i, row in enumerate(rows, start=1):
        if len(row) != 12:
            continue
        try:
            parsed.append((timestamp_ms(row[0]), row))
        except Exception:
            errors.append(f"row {i}: invalid open_time")
    times = [x[0] for x in parsed]
    if times != sorted(times):
        errors.append("open_time values are not sorted")
    duplicates = len(times) - len(set(times))
    if duplicates:
        errors.append(f"{duplicates} duplicate open_time value(s)")
    off_grid = sum(t % INTERVAL_MS != 0 for t in times)
    if off_grid:
        errors.append(f"{off_grid} open_time value(s) are off the 5m UTC grid")
    missing = sorted(set(range(EXPECTED_FIRST_MS, EXPECTED_LAST_MS + 1, INTERVAL_MS)) - set(times))
    unexpected = sorted(set(times) - set(range(EXPECTED_FIRST_MS, EXPECTED_LAST_MS + 1, INTERVAL_MS)))
    if missing:
        errors.append(f"{len(missing)} expected interval(s) missing")
    if unexpected:
        errors.append(f"{len(unexpected)} timestamp(s) outside September 2026")
    bad_numeric = 0
    bad_ohlc = 0
    bad_close_time = 0
    for _, row in parsed:
        try:
            values = {k: float(row[COLUMNS.index(k)]) for k in NUMERIC_NONNEGATIVE}
            if any(not math.isfinite(v) or v < 0 for v in values.values()):
                bad_numeric += 1
            o, h, lo, c = (float(row[i]) for i in (1, 2, 3, 4))
            if not all(math.isfinite(v) for v in (o, h, lo, c)) or lo > min(o, c) or h < max(o, c) or lo > h:
                bad_ohlc += 1
            close_ms = timestamp_ms(row[6])
            if close_ms < timestamp_ms(row[0]) or close_ms > timestamp_ms(row[0]) + INTERVAL_MS:
                bad_close_time += 1
            trade_count = int(row[8])
            if trade_count < 0:
                bad_numeric += 1
        except Exception:
            bad_numeric += 1
    if bad_numeric:
        errors.append(f"{bad_numeric} row-level numeric/trade-count issue(s)")
    if bad_ohlc:
        errors.append(f"{bad_ohlc} row(s) fail OHLC consistency")
    if bad_close_time:
        errors.append(f"{bad_close_time} row(s) fail close_time bounds")
    return {
        "product": product, "symbol": SYMBOL, "interval": INTERVAL,
        "expected_rows": EXPECTED_ROWS, "actual_rows": len(rows),
        "first_open_time_ms": min(times) if times else None,
        "last_open_time_ms": max(times) if times else None,
        "first_open_time_utc": datetime.fromtimestamp(min(times)/1000, timezone.utc).isoformat() if times else None,
        "last_open_time_utc": datetime.fromtimestamp(max(times)/1000, timezone.utc).isoformat() if times else None,
        "duplicate_count": duplicates, "off_grid_count": off_grid,
        "missing_interval_count": len(missing), "unexpected_timestamp_count": len(unexpected),
        "numeric_issue_count": bad_numeric, "ohlc_issue_count": bad_ohlc,
        "close_time_issue_count": bad_close_time,
        "sample_missing_open_time_ms": missing[:10],
        "errors": errors, "passed": not errors and len(rows) == EXPECTED_ROWS,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/hd03")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    report: dict[str, Any] = {
        "schema_version": 1, "gate": "HD-03", "period": "2026-09",
        "symbol": SYMBOL, "interval": INTERVAL, "expected_rows": EXPECTED_ROWS,
        "expected_first_open_time_utc": datetime.fromtimestamp(EXPECTED_FIRST_MS/1000, timezone.utc).isoformat(),
        "expected_last_open_time_utc": datetime.fromtimestamp(EXPECTED_LAST_MS/1000, timezone.utc).isoformat(),
        "retrieval_started_utc": started, "sources": [], "overall_passed": False,
    }
    base = "https://data.binance.vision/data"
    for product, path in [
        ("spot", f"spot/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YEAR}-{MONTH:02d}.zip"),
        ("um_futures", f"futures/um/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YEAR}-{MONTH:02d}.zip"),
    ]:
        url = f"{base}/{path}"
        item: dict[str, Any] = {"product": product, "source_url": url}
        try:
            blob = get(url)
            archive_path = output / f"{product}-{SYMBOL}-{INTERVAL}-{YEAR}-{MONTH:02d}.zip"
            archive_path.write_bytes(blob)
            item["retrieved_bytes"] = len(blob)
            item["local_archive"] = archive_path.name
            item["sha256"] = sha256(archive_path)
            item["retrieved_utc"] = datetime.now(timezone.utc).isoformat()
            try:
                sidecar_url = url + ".CHECKSUM"
                sidecar = get(sidecar_url, attempts=1).decode("utf-8", errors="replace").strip()
                item["source_checksum_url"] = sidecar_url
                item["source_checksum_text"] = sidecar
                item["source_checksum_available"] = True
                expected = sidecar.split()[0].lower()
                if len(expected) == 64 and all(ch in "0123456789abcdef" for ch in expected):
                    item["source_checksum_matches"] = expected == item["sha256"]
                    if not item["source_checksum_matches"]:
                        item.setdefault("errors", []).append("Binance sidecar SHA-256 does not match downloaded ZIP")
                else:
                    item["source_checksum_matches"] = None
                    item.setdefault("warnings", []).append("Checksum sidecar format not recognized; local SHA-256 retained")
            except Exception as exc:
                item["source_checksum_available"] = False
                item["source_checksum_note"] = f"No readable sidecar; independently computed local SHA-256 retained ({exc})"
            item["validation"] = validate_csv(blob, product)
            item["passed"] = item["validation"]["passed"] and item.get("source_checksum_matches") is not False and not item.get("errors")
        except Exception as exc:
            item["passed"] = False
            item.setdefault("errors", []).append(f"{type(exc).__name__}: {exc}")
        report["sources"].append(item)
    report["retrieval_finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["overall_passed"] = len(report["sources"]) == 2 and all(x.get("passed") is True for x in report["sources"])
    report_path = output / "hd03-integrity-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": report["gate"], "period": report["period"],
        "overall_passed": report["overall_passed"],
        "sources": [{"product": x["product"], "passed": x.get("passed"),
                     "rows": x.get("validation", {}).get("actual_rows"),
                     "sha256": x.get("sha256"), "errors": x.get("errors", []) + x.get("validation", {}).get("errors", [])}
                    for x in report["sources"]],
        "report": str(report_path),
    }, indent=2))
    return 0 if report["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
