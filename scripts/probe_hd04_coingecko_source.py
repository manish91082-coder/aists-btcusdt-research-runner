#!/usr/bin/env python3
"""Probe CoinGecko exchange endpoints as independent corroboration, not exchange authority."""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://api.coingecko.com/api/v3"
UA = "aists-btcusdt-research-runner/1.0"


def fetch_json(path: str):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    key = os.environ.get("COINGECKO_DEMO_API_KEY", "").strip()
    if key:
        headers["x-cg-demo-api-key"] = key
    req = Request(BASE + path, headers=headers)
    with urlopen(req, timeout=25) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def summarize_exchange(payload: dict, name: str, url: str, sha256: str) -> dict:
    tickers = payload.get("tickers", [])
    pairs = [{
        "base": t.get("base"), "target": t.get("target"),
        "market": t.get("market", {}).get("identifier") if isinstance(t.get("market"), dict) else None,
        "last": t.get("last"),
        "converted_volume_usd": t.get("converted_volume", {}).get("usd")
            if isinstance(t.get("converted_volume"), dict) else None,
        "trust_score": t.get("trust_score"),
    } for t in tickers]
    return {
        "name": name, "url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": sha256, "exchange_name": payload.get("name"),
        "reported_volume_btc": payload.get("trade_volume_24h_btc"),
        "tickers_returned": len(tickers), "tickers": pairs[:100],
        "coverage_note": "Exchange endpoint output is independent corroboration only; not a complete Binance exchangeInfo universe or official per-symbol USDT quoteVolume ranking."
    }


def summarize_derivatives_list(payload, url: str, sha256: str) -> dict:
    if not isinstance(payload, list):
        raise ValueError(f"Expected list from /derivatives, got {type(payload).__name__}")
    matches = []
    for item in payload:
        market = str(item.get("market", ""))
        if "binance" not in market.lower() or "futures" not in market.lower():
            continue
        matches.append({
            "market": market, "symbol": item.get("symbol"), "index_id": item.get("index_id"),
            "price": item.get("price"), "contract_type": item.get("contract_type"),
            "funding_rate": item.get("funding_rate"), "open_interest": item.get("open_interest"),
            "volume_24h": item.get("volume_24h"), "last_traded_at": item.get("last_traded_at"),
            "expired": item.get("expired"), "url": item.get("url"),
        })
    return {
        "name": "all_derivatives_filtered_to_binance_futures",
        "url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": sha256, "total_derivative_tickers_returned": len(payload),
        "binance_futures_matches": len(matches), "tickers": matches,
        "coverage_note": "Filtered from CoinGecko global derivatives ticker list; aggregator coverage is not authoritative Binance contract metadata."
    }


def main() -> int:
    out = Path("artifacts/hd04")
    out.mkdir(parents=True, exist_ok=True)
    exchange_checks = [
        ("binance_spot_exchange", "/exchanges/binance"),
        ("binance_futures_exchange", "/derivatives/exchanges/binance_futures"),
    ]
    results, errors = [], []
    for name, path in exchange_checks:
        try:
            payload, sha = fetch_json(path)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object, got {type(payload).__name__}")
            results.append(summarize_exchange(payload, name, BASE + path, sha))
        except Exception as exc:
            errors.append({"name": name, "url": BASE + path,
                           "error": f"{type(exc).__name__}: {exc}",
                           "retrieved_utc": datetime.now(timezone.utc).isoformat()})
    path = "/derivatives"
    try:
        payload, sha = fetch_json(path)
        results.append(summarize_derivatives_list(payload, BASE + path, sha))
    except Exception as exc:
        errors.append({"name": "all_derivatives_filtered_to_binance_futures", "url": BASE + path,
                       "error": f"{type(exc).__name__}: {exc}",
                       "retrieved_utc": datetime.now(timezone.utc).isoformat()})
    spot = next((x for x in results if x["name"] == "binance_spot_exchange"), {})
    deriv = next((x for x in results if x["name"] == "all_derivatives_filtered_to_binance_futures"), {})
    report = {
        "gate": "HD-04-independent-exchange-source-probe", "source": "CoinGecko API",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "authentication_configured": bool(os.environ.get("COINGECKO_DEMO_API_KEY", "").strip()),
        "documentation": [
            "https://docs.coingecko.com/reference/exchanges-id",
            "https://docs.coingecko.com/reference/derivatives-exchange-id",
            "https://docs.coingecko.com/reference/derivatives-tickers",
        ],
        "results": results, "errors": errors,
        "summary": {
            "endpoints_checked": 3, "endpoints_succeeded": len(results), "endpoints_failed": len(errors),
            "spot_tickers_returned": spot.get("tickers_returned"),
            "binance_futures_ticker_matches": deriv.get("binance_futures_matches"),
            "status": "PASS_CORROBORATION_PROBE" if results else "BLOCKED_SOURCE_ACCESS",
        },
        "limitations": [
            "This probe does not replace Binance exchangeInfo, exact contract status, complete symbol coverage, or official quote-volume rankings.",
            "CoinGecko's reported exchange volume is denominated in BTC on documented exchange endpoints; it is not interchangeable with Binance per-symbol USDT quoteVolume.",
            "CoinGecko derivatives results are aggregator coverage and may not enumerate every Binance Futures contract."
        ],
    }
    target = out / "hd04-coingecko-source-probe.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    preview = []
    for item in results:
        sample = item.get("tickers", [])[:5]
        preview.append({k: v for k, v in item.items() if k != "tickers"} | {"tickers_sample": sample})
    print(json.dumps({"report": str(target), "summary": report["summary"], "errors": errors, "results": preview}, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
