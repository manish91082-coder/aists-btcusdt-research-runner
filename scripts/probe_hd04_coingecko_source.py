#!/usr/bin/env python3
"""Probe CoinGecko exchange endpoints as independent corroboration, not exchange authority."""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://api.coingecko.com/api/v3"
UA = "aists-btcusdt-research-runner/1.0"


def fetch_json(path: str) -> dict:
    headers = {"User-Agent": UA, "Accept": "application/json"}
    key = os.environ.get("COINGECKO_DEMO_API_KEY", "").strip()
    if key:
        headers["x-cg-demo-api-key"] = key
    req = Request(BASE + path, headers=headers)
    with urlopen(req, timeout=25) as response:
        raw = response.read()
    return {"payload": json.loads(raw.decode("utf-8")), "sha256": hashlib.sha256(raw).hexdigest()}


def summarize(payload: dict, name: str, url: str, sha256: str) -> dict:
    tickers = payload.get("tickers", [])
    pairs = []
    for t in tickers:
        pairs.append({
            "base": t.get("base"), "target": t.get("target"),
            "market": t.get("market", {}).get("identifier") if isinstance(t.get("market"), dict) else None,
            "last": t.get("last"), "converted_volume_usd": t.get("converted_volume", {}).get("usd")
                if isinstance(t.get("converted_volume"), dict) else None,
            "trust_score": t.get("trust_score"),
        })
    return {
        "name": name, "url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": sha256, "exchange_name": payload.get("name"),
        "exchange_id": payload.get("id"), "reported_volume_btc": payload.get("trade_volume_24h_btc"),
        "tickers_returned": len(tickers), "tickers": pairs[:100],
        "coverage_note": "CoinGecko exchange-level reported tickers/volume are independent corroboration only; not a complete Binance exchangeInfo universe or official exchange quoteVolume ranking."
    }


def main() -> int:
    out = Path("artifacts/hd04")
    out.mkdir(parents=True, exist_ok=True)
    checks = [
        ("binance_spot_exchange", "/exchanges/binance"),
        ("binance_futures_exchange", "/derivatives/exchanges/binance_futures"),
    ]
    results, errors = [], []
    for name, path in checks:
        try:
            response = fetch_json(path)
            results.append(summarize(response["payload"], name, BASE + path, response["sha256"]))
        except Exception as exc:
            errors.append({"name": name, "url": BASE + path,
                           "error": f"{type(exc).__name__}: {exc}",
                           "retrieved_utc": datetime.now(timezone.utc).isoformat()})
    report = {
        "gate": "HD-04-independent-exchange-source-probe",
        "source": "CoinGecko API",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "authentication_configured": bool(os.environ.get("COINGECKO_DEMO_API_KEY", "").strip()),
        "documentation": [
            "https://docs.coingecko.com/reference/exchanges-id",
            "https://docs.coingecko.com/reference/derivatives-exchange-id",
        ],
        "results": results, "errors": errors,
        "summary": {"endpoints_checked": len(checks), "endpoints_succeeded": len(results),
                    "endpoints_failed": len(errors),
                    "status": "PASS_CORROBORATION_PROBE" if results else "BLOCKED_SOURCE_ACCESS"},
        "limitations": [
            "This probe does not replace Binance exchangeInfo, exact contract status, complete symbol coverage, or official quote-volume rankings.",
            "CoinGecko's reported exchange volume is denominated in BTC on documented exchange endpoints; it is not interchangeable with Binance per-symbol USDT quoteVolume.",
            "A limited ticker sample must not be treated as a full exchange universe."
        ],
    }
    target = out / "hd04-coingecko-source-probe.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "summary": report["summary"], "errors": errors,
                      "results": [{k: v for k, v in x.items() if k != "tickers"} | {"tickers_sample": x["tickers"][:5]} for x in results]}, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
