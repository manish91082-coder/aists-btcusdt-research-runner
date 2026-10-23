#!/usr/bin/env python3
"""Resumable BTCUSDT archive collector for official Binance monthly data.

Downloads the canonical 1m Spot and USDⓈ-M Futures klines plus Futures funding
archives where available. Larger candle intervals should be derived from the
validated 1m base to avoid duplicate storage. Each ZIP is retained with a
SHA-256 manifest; missing archives are recorded, never synthesized.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://data.binance.vision"
SYMBOL = "BTCUSDT"
UA = "aists-btcusdt-research-runner/1.0"


def months_between(start: str, end: str) -> list[str]:
    def parse(s: str) -> tuple[int, int]:
        try:
            y, m = map(int, s.split("-"))
            if len(s) != 7 or not 1 <= m <= 12:
                raise ValueError
            return y, m
        except Exception as exc:
            raise ValueError(f"invalid YYYY-MM month: {s}") from exc
    sy, sm = parse(start)
    ey, em = parse(end)
    a, b = sy * 12 + sm - 1, ey * 12 + em - 1
    if b < a:
        raise ValueError("end month precedes start month")
    if b - a > 119:
        raise ValueError("single invocation is limited to 120 months; run in resumable decade-sized batches")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}" for i in range(a, b + 1)]


def request_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read()


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
            if target.exists() and target.stat().st_size:
                payload = target.read_bytes()
                reused = True
            else:
                payload = request_bytes(url)
                reused = False
            digest = hashlib.sha256(payload).hexdigest()
            # Archive must be a readable ZIP containing exactly one non-directory member.
            with zipfile.ZipFile(target if reused else __import__("io").BytesIO(payload)) as zf:
                members = [n for n in zf.namelist() if not n.endswith("/")]
                if len(members) != 1:
                    raise ValueError(f"expected one data member, got {len(members)}")
                bad = zf.testzip()
                if bad:
                    raise ValueError(f"ZIP CRC failure: {bad}")
            checksum_text = request_bytes(url + ".CHECKSUM").decode("utf-8-sig").strip()
            expected = checksum_text.split()[0].lower()
            if digest != expected:
                raise ValueError("official SHA-256 sidecar mismatch")
            if not reused:
                target.write_bytes(payload)
            record.update({"status": "PASS", "bytes": len(payload), "sha256": digest,
                           "official_checksum": expected, "reused_existing": reused,
                           "member": members[0]})
        except urllib.error.HTTPError as exc:
            record.update({"status": "UNAVAILABLE" if exc.code == 404 else "FAIL",
                           "error": f"HTTP {exc.code}"})
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
            record.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
        records.append(record)
        if idx % 25 == 0:
            print(json.dumps({"processed": idx, "total": len(jobs), "last": record}, ensure_ascii=False))
        time.sleep(max(0, args.sleep_seconds))
    summary = {
        "dataset": "BTCUSDT official monthly archive collection",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": SYMBOL,
        "canonical_candle_interval": "1m",
        "larger_intervals": "derive from validated 1m data; do not duplicate raw archive storage",
        "periods_requested": periods,
        "source": "Binance public data archive and adjacent .CHECKSUM SHA-256 sidecars",
        "counts": {key: sum(1 for r in records if r["status"] == key)
                   for key in ("PASS", "UNAVAILABLE", "FAIL")},
        "archives": records,
        "limitations": [
            "A 404 means that specific monthly archive was not published at that URL; it does not prove the instrument did not exist.",
            "ZIP integrity and checksum verification do not replace full candle-schema, timestamp-grid, OHLCV, and gap validation.",
            "This collector stores local runner files during a workflow; durable long-term retention requires a persistent storage target.",
            "No data is invented for unavailable periods. Spot and Futures have different history start dates."
        ]
    }
    manifest = root / "btc-usdt-archive-collection-manifest.json"
    manifest.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "counts": summary["counts"],
                      "archives_requested": len(records)}, indent=2))
    return 1 if summary["counts"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
