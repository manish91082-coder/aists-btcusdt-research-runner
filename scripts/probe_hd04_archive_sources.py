#!/usr/bin/env python3
"""Probe Binance's official static archives for historical Spot, UM klines and funding data."""
from __future__ import annotations
import csv, hashlib, io, json, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://data.binance.vision"
UA = "aists-btcusdt-research-runner/1.0"
PERIOD = "2026-09"
SYMBOL = "BTCUSDT"


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read()


def check_archive(name: str, url: str) -> dict:
    item = {"name": name, "url": url, "checked_utc": datetime.now(timezone.utc).isoformat()}
    try:
        raw = fetch(url)
        checksum_raw = fetch(url + ".CHECKSUM").decode("utf-8").strip()
        expected = checksum_raw.split()[0].lower()
        actual = hashlib.sha256(raw).hexdigest()
        item.update({"available": True, "bytes": len(raw), "sha256": actual,
                     "checksum_sidecar": url + ".CHECKSUM", "checksum_expected": expected,
                     "checksum_matches": actual == expected})
        if not item["checksum_matches"]:
            item["error"] = "SHA-256 mismatch"
            return item
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if len(names) != 1:
                item["error"] = f"Expected one data file in ZIP, found {len(names)}"
                return item
            payload = zf.read(names[0]).decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(payload)))
        item["member_name"] = names[0]
        item["row_count"] = len(rows)
        item["first_row"] = rows[0] if rows else None
        item["last_row"] = rows[-1] if rows else None
        item["nonempty"] = bool(rows)
        item["content_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    except Exception as exc:
        item.update({"available": False, "error": f"{type(exc).__name__}: {exc}"})
    return item


def main():
    out = Path("artifacts/hd04")
    out.mkdir(parents=True, exist_ok=True)
    urls = [
        ("spot_5m_klines", f"{BASE}/data/spot/monthly/klines/{SYMBOL}/5m/{SYMBOL}-5m-{PERIOD}.zip"),
        ("um_5m_klines", f"{BASE}/data/futures/um/monthly/klines/{SYMBOL}/5m/{SYMBOL}-5m-{PERIOD}.zip"),
        ("um_funding_rate", f"{BASE}/data/futures/um/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{PERIOD}.zip"),
    ]
    checks = [check_archive(name, url) for name, url in urls]
    report = {
        "gate": "HD-04-archive-source-probe", "symbol": SYMBOL, "period": PERIOD,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source_repository": "https://github.com/binance/binance-public-data",
        "source_notes": "Official static archive probe. Passing files establish archive access and checksum integrity only, not a full market universe or profitability.",
        "checks": checks,
        "summary": {
            "files_checked": len(checks),
            "files_available_and_checksum_matched": sum(x.get("available") and x.get("checksum_matches") and x.get("nonempty") for x in checks),
            "failed_files": [x["name"] for x in checks if not (x.get("available") and x.get("checksum_matches") and x.get("nonempty"))],
        }
    }
    path = out / "hd04-archive-source-probe.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(path), "summary": report["summary"], "checks": checks}, indent=2))
    return 0 if report["summary"]["files_available_and_checksum_matched"] == len(checks) else 1

if __name__ == "__main__":
    raise SystemExit(main())
