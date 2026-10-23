#!/usr/bin/env python3
"""Inventory official Binance monthly BTCUSDT archive URL coverage without downloading archives."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://data.binance.vision"
UA = "aists-btcusdt-research-runner/1.0"
DATASETS = {
    "spot_klines_1m": lambda month: f"{BASE}/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{month}.zip",
    "um_klines_1m": lambda month: f"{BASE}/data/futures/um/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{month}.zip",
    "um_funding": lambda month: f"{BASE}/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{month}.zip",
}


def month_range(start: str, end: str) -> list[str]:
    def parse(value: str) -> tuple[int, int]:
        try:
            y, m = map(int, value.split("-"))
            if len(value) != 7 or not 1 <= m <= 12:
                raise ValueError
            return y, m
        except Exception as exc:
            raise ValueError(f"invalid YYYY-MM month: {value}") from exc
    sy, sm = parse(start)
    ey, em = parse(end)
    a, b = sy * 12 + sm - 1, ey * 12 + em - 1
    if b < a:
        raise ValueError("end month precedes start month")
    if b - a > 119:
        raise ValueError("single coverage inventory is limited to 120 months")
    return [f"{i // 12:04d}-{i % 12 + 1:02d}" for i in range(a, b + 1)]


def head(url: str, timeout: int = 8) -> dict:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {"status": "AVAILABLE" if response.status == 200 else "FAIL",
                    "http_status": response.status,
                    "content_length": int(response.headers.get("Content-Length", "0") or 0)}
    except urllib.error.HTTPError as exc:
        return {"status": "UNAVAILABLE" if exc.code == 404 else "FAIL",
                "http_status": exc.code, "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-month", required=True)
    parser.add_argument("--end-month", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sleep-seconds", type=float, default=0.12)
    args = parser.parse_args()
    months = month_range(args.start_month, args.end_month)
    records = []
    total = len(months) * len(DATASETS)
    tasks = [(month, dataset, url_for(month))
             for month in months for dataset, url_for in DATASETS.items()]

    def probe(item: tuple[str, str, str]) -> dict:
        month, dataset, url = item
        archive = head(url)
        time.sleep(max(0, args.sleep_seconds))
        checksum = head(url + ".CHECKSUM")
        status = ("AVAILABLE" if archive["status"] == "AVAILABLE" and checksum["status"] == "AVAILABLE"
                  else "UNAVAILABLE" if archive["status"] == "UNAVAILABLE"
                  else "FAIL")
        return {"month": month, "dataset": dataset, "url": url,
                "archive": archive, "checksum_sidecar": checksum, "status": status}

    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(probe, item) for item in tasks]
        for index, future in enumerate(as_completed(futures), 1):
            record = future.result()
            records.append(record)
            if index % 25 == 0:
                print(json.dumps({"checks_completed": index, "checks_total": total,
                                  "last": record}, ensure_ascii=False))
    records.sort(key=lambda r: (r["month"], list(DATASETS).index(r["dataset"])))
    counts = {state: sum(r["status"] == state for r in records)
              for state in ("AVAILABLE", "UNAVAILABLE", "FAIL")}
    report = {
        "dataset": "BTCUSDT official Binance monthly archive URL coverage inventory",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "start_month": args.start_month, "end_month": args.end_month,
        "months_requested": months,
        "datasets": list(DATASETS),
        "method": "HEAD requests only; archive bodies are not downloaded and archive contents are not validated",
        "counts": counts, "checks_requested": total, "records": records,
        "limitations": [
            "AVAILABLE means the archive URL and checksum sidecar responded to HEAD, not that archive contents or checksum values were validated.",
            "UNAVAILABLE records an exact HTTP 404 for the archive URL; it is not proof the instrument did not exist.",
            "Some origins or intermediaries may not support HEAD consistently; FAIL must be investigated rather than treated as absence.",
            "Use the full-history collector for content download, SHA-256 comparison and data-quality validation."
        ]
    }
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "btc-usdt-archive-coverage-inventory.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "counts": counts, "checks_requested": total}, indent=2))
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
