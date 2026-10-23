#!/usr/bin/env python3
"""Bounded historical archive coverage check for top CoinGecko Binance-Futures USDT candidates.

Candidate labels are not Binance listing authority. Missing archives are coverage observations,
not proof that a symbol was never listed or is inactive.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://data.binance.vision/data"
UA = "aists-btcusdt-research-runner/1.0"
INPUT = Path("artifacts/hd04/hd04-coingecko-source-probe.json")
OUTPUT = Path("artifacts/hd04/hd04-candidate-archive-coverage.json")
MONTH = "2026-09"
INTERVAL = "5m"
LIMIT = 10


def select_usdt_candidates(report: dict, limit: int = LIMIT) -> list[dict]:
    """Select unique conservative USDT candidates by reported volume, deterministic ties."""
    derivative_result = next(
        (item for item in report.get("results", [])
         if item.get("name") == "all_derivatives_filtered_to_binance_futures"), {}
    )
    selected = {}
    for ticker in derivative_result.get("tickers", []):
        symbol = ticker.get("candidate_symbol")
        volume = ticker.get("volume_24h")
        if ticker.get("candidate_quote_asset") != "USDT" or not isinstance(symbol, str):
            continue
        if not re.fullmatch(r"[A-Z0-9]+USDT", symbol):
            continue
        try:
            numeric_volume = float(volume)
        except (TypeError, ValueError):
            numeric_volume = -1.0
        if symbol not in selected or numeric_volume > selected[symbol]["reported_volume_24h"]:
            selected[symbol] = {
                "candidate_symbol": symbol,
                "raw_symbol": ticker.get("raw_symbol"),
                "market_label": ticker.get("market"),
                "reported_volume_24h": numeric_volume,
                "volume_source": "CoinGecko /derivatives aggregator field; units/source semantics not independently normalized",
            }
    ordered = sorted(selected.values(), key=lambda x: (-x["reported_volume_24h"], x["candidate_symbol"]))
    return ordered[:max(0, limit)]


def request_bytes(url: str) -> dict:
    req = Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urlopen(req, timeout=15) as response:
            body = response.read()
            return {"status": "HTTP_OK", "http_status": response.status, "body": body}
    except HTTPError as exc:
        return {"status": "NOT_AVAILABLE_OR_NOT_LISTED" if exc.code == 404 else "HTTP_ERROR",
                "http_status": exc.code, "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError, OSError) as exc:
        return {"status": "SOURCE_OR_NETWORK_ERROR", "error": f"{type(exc).__name__}: {exc}"}


def check_archive(symbol: str, market: str) -> dict:
    if market == "spot":
        rel = f"spot/monthly/klines/{symbol}/{INTERVAL}/{symbol}-{INTERVAL}-{MONTH}.zip"
    else:
        rel = f"futures/um/monthly/klines/{symbol}/{INTERVAL}/{symbol}-{INTERVAL}-{MONTH}.zip"
    url = f"{BASE}/{rel}"
    zip_result = request_bytes(url)
    record = {"market": market, "symbol_candidate": symbol, "month": MONTH, "interval": INTERVAL,
              "archive_url": url, "archive_status": zip_result["status"]}
    if "http_status" in zip_result:
        record["archive_http_status"] = zip_result["http_status"]
    if "error" in zip_result:
        record["archive_error"] = zip_result["error"]
    if zip_result["status"] != "HTTP_OK":
        return record
    body = zip_result["body"]
    record["archive_size_bytes"] = len(body)
    record["archive_sha256"] = hashlib.sha256(body).hexdigest()
    if not body.startswith(b"PK"):
        record.update({"archive_status": "INVALID_ZIP_SIGNATURE", "checksum_status": "NOT_CHECKED"})
        return record
    checksum_url = url + ".CHECKSUM"
    checksum_result = request_bytes(checksum_url)
    record["checksum_url"] = checksum_url
    record["checksum_status"] = checksum_result["status"]
    if checksum_result["status"] != "HTTP_OK":
        if "http_status" in checksum_result:
            record["checksum_http_status"] = checksum_result["http_status"]
        if "error" in checksum_result:
            record["checksum_error"] = checksum_result["error"]
        return record
    sidecar = checksum_result["body"].decode("utf-8", errors="replace").strip()
    expected = sidecar.split()[0].lower() if sidecar.split() else ""
    record["official_checksum_sha256"] = expected
    record["checksum_status"] = "MATCH" if re.fullmatch(r"[0-9a-f]{64}", expected) and expected == record["archive_sha256"] else "MISMATCH_OR_UNPARSEABLE"
    record["checksum_sidecar_text"] = sidecar[:300]
    return record


def main() -> int:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing prior CoinGecko report: {INPUT}")
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    candidates = select_usdt_candidates(source)
    checks = []
    for candidate in candidates:
        for market in ("spot", "um_futures"):
            checks.append({**candidate, **check_archive(candidate["candidate_symbol"], market)})
            time.sleep(0.15)
    report = {
        "gate": "HD-04-bounded-candidate-archive-coverage",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source_report": str(INPUT),
        "source_note": "CoinGecko aggregator candidates only; this is not a verified Binance listing universe.",
        "archive_scope": {"month": MONTH, "interval": INTERVAL, "markets": ["spot", "um_futures"],
                          "candidate_limit": LIMIT},
        "candidate_count": len(candidates),
        "selected_candidates": candidates,
        "checks": checks,
        "summary": {
            "archive_objects_checked": len(checks),
            "archive_http_ok": sum(x.get("archive_status") == "HTTP_OK" for x in checks),
            "checksum_matches": sum(x.get("checksum_status") == "MATCH" for x in checks),
            "unavailable_or_not_listed_404": sum(x.get("archive_status") == "NOT_AVAILABLE_OR_NOT_LISTED" and x.get("archive_http_status") == 404 for x in checks),
            "network_or_other_errors": sum(x.get("archive_status") in ("HTTP_ERROR", "SOURCE_OR_NETWORK_ERROR") for x in checks),
        },
        "interpretation": [
            "A 404 means this exact monthly archive URL was unavailable at probe time; it does not prove the symbol was never listed or is inactive.",
            "An archive with matching official checksum establishes object integrity only; CSV schema and candle continuity are not validated by this probe.",
            "Spot and USD-M Futures coverage are reported separately; a derivatives candidate need not be Spot-listed.",
            "The selected sample is capped at ten unique USDT candidates ranked by the aggregator-reported volume field, whose units are preserved as source-reported."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), **report["summary"],
                      "candidates": [x["candidate_symbol"] for x in candidates]}, indent=2))
    return 0 if candidates else 1


if __name__ == "__main__":
    raise SystemExit(main())
