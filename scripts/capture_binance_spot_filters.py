#!/usr/bin/env python3
"""Capture current public Binance Spot BTCUSDT exchange filters as evidence.

This is operational metadata only. It does not fetch klines/trades or place orders.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://data-api.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT"
OUT = Path("evidence/operational_filters")
TIMEOUT_SECONDS = 20


def main() -> None:
    request_started = datetime.now(timezone.utc)
    req = urllib.request.Request(URL, headers={"User-Agent": "AISTS-operational-filter-evidence/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read()
        http_status = response.status
        response_headers = dict(response.headers.items())
    captured_at = datetime.now(timezone.utc)

    payload = json.loads(raw.decode("utf-8"))
    symbols = payload.get("symbols")
    if not isinstance(symbols, list) or len(symbols) != 1 or symbols[0].get("symbol") != "BTCUSDT":
        raise SystemExit("FAIL_CLOSED: response did not contain exactly the requested BTCUSDT symbol")
    symbol = symbols[0]
    if not isinstance(symbol.get("filters"), list) or not symbol["filters"]:
        raise SystemExit("FAIL_CLOSED: BTCUSDT filters absent or empty")

    raw_sha256 = hashlib.sha256(raw).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = captured_at.strftime("%Y%m%dT%H%M%SZ")
    raw_path = OUT / f"BTCUSDT_Spot_exchangeInfo_{stamp}.raw.json"
    manifest_path = OUT / f"BTCUSDT_Spot_exchangeInfo_{stamp}.manifest.json"
    raw_path.write_bytes(raw)
    manifest = {
        "evidence_type": "current_operational_exchange_filters_not_historical_provenance",
        "symbol": "BTCUSDT",
        "source_url": URL,
        "request_started_utc": request_started.isoformat(),
        "captured_at_utc": captured_at.isoformat(),
        "http_status": http_status,
        "binance_server_time_ms": payload.get("serverTime"),
        "response_content_type": response_headers.get("Content-Type"),
        "raw_file": raw_path.name,
        "raw_sha256": raw_sha256,
        "symbol_status": symbol.get("status"),
        "base_asset": symbol.get("baseAsset"),
        "quote_asset": symbol.get("quoteAsset"),
        "filters": symbol["filters"],
        "limitations": [
            "Snapshot records current operational metadata only; it is not a historical filter reconstruction.",
            "It does not establish the user's account fee tier, BNB discount eligibility, INR-to-USDT conversion, or capital allocation.",
            "It does not resolve G0 source provenance or authorize candidate evaluation."
        ]
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": "PASS_CURRENT_METADATA_CAPTURED",
        "symbol": "BTCUSDT",
        "captured_at_utc": captured_at.isoformat(),
        "raw_file": str(raw_path),
        "manifest_file": str(manifest_path),
        "raw_sha256": raw_sha256,
        "filter_types": [f.get("filterType") for f in symbol["filters"]]
    }, indent=2))


if __name__ == "__main__":
    main()
