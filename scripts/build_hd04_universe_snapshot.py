#!/usr/bin/env python3
"""Build a timestamped Binance Spot/USDT-M Futures universe and coverage snapshot.

Public endpoints only; no API key. Snapshot is point-in-time and is not a
historical survivorship-bias-free universe by itself.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPOT_HOSTS = ["https://data-api.binance.vision", "https://api-gcp.binance.com", "https://api.binance.com", "https://api1.binance.com", "https://api2.binance.com", "https://api3.binance.com", "https://api4.binance.com"]
UM_HOSTS = ["https://fapi.binance.com", "https://fapi1.binance.com", "https://fapi2.binance.com", "https://fapi3.binance.com", "https://fapi4.binance.com"]
UA = "aists-btcusdt-research-runner/1.0"


def fetch_json(url: str, attempts: int = 1):
    last = None
    from urllib.parse import urlsplit, urlunsplit
    parts = urlsplit(url)
    spot_hosts = {h.split("//", 1)[1] for h in SPOT_HOSTS}
    host_group = SPOT_HOSTS if parts.netloc in spot_hosts else UM_HOSTS
    candidates = []
    for host in host_group:
        candidate = urlunsplit((parts.scheme, host.split("//", 1)[1], parts.path, parts.query, parts.fragment))
        if candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        for i in range(attempts):
            try:
                req = Request(candidate, headers={"User-Agent": UA})
                with urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                last = exc
                if i + 1 < attempts:
                    time.sleep(2 ** i)
    raise RuntimeError(f"GET failed across official Binance market-data hosts: {url}: {last}")

def digest(payload) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def eligible_symbols(info, market):
    symbols = {}
    for s in info.get("symbols", []):
        if s.get("status") != "TRADING":
            continue
        if market == "spot":
            if not s.get("isSpotTradingAllowed", False) or s.get("quoteAsset") != "USDT":
                continue
        else:
            if s.get("contractType") != "PERPETUAL" or s.get("quoteAsset") != "USDT" or s.get("marginAsset") != "USDT":
                continue
        symbols[s["symbol"]] = {
            "symbol": s["symbol"], "status": s.get("status"),
            "baseAsset": s.get("baseAsset"), "quoteAsset": s.get("quoteAsset"),
            "marginAsset": s.get("marginAsset"), "contractType": s.get("contractType"),
            "onboardDate": s.get("onboardDate"), "deliveryDate": s.get("deliveryDate"),
            "filters": s.get("filters", []),
            "permissions": s.get("permissions"),
            "permissionSets": s.get("permissionSets"),
        }
    return symbols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/hd04")
    ap.add_argument("--top-n", type=int, default=10)
    args = ap.parse_args()
    if not 1 <= args.top_n <= 100:
        ap.error("--top-n must be between 1 and 100")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    report = {
        "schema_version": 1, "gate": "HD-04", "snapshot_started_utc": started,
        "primary_goal_usdt": 1061120.54,
        "note": "Point-in-time eligible universe and quote-volume ranking; not a historical universe or profitability evidence.",
        "sources": {}, "markets": {}, "funding_history_checks": [],
        "fee_assumptions": {
            "spot": {"status": "NOT_ASSUMED", "source": "https://www.binance.com/en/fee/trading"},
            "um_futures": {"status": "NOT_ASSUMED", "source": "https://www.binance.com/en/fee/futureFee"},
            "note": "Public fee pages are linked for verification. Account-specific tier/discount is unknown; backtest must parameterize maker/taker fees and run sensitivity instead of hardcoding an assumed user tier."
        }
    }
    endpoints = {
        "spot": {
            "info": f"{SPOT_HOSTS[0]}/api/v3/exchangeInfo",
            "ticker": f"{SPOT_HOSTS[0]}/api/v3/ticker/24hr",
            "market": "spot",
        },
        "um_futures": {
            "info": f"{UM_HOSTS[0]}/fapi/v1/exchangeInfo",
            "ticker": f"{UM_HOSTS[0]}/fapi/v1/ticker/24hr",
            "market": "um_futures",
        },
    }
    for name, cfg in endpoints.items():
        info = fetch_json(cfg["info"])
        tickers = fetch_json(cfg["ticker"])
        eligible = eligible_symbols(info, cfg["market"])
        ticker_map = {x["symbol"]: x for x in tickers if x.get("symbol") in eligible}
        rows = []
        for symbol, meta in eligible.items():
            ticker = ticker_map.get(symbol)
            if not ticker:
                continue
            try:
                quote_volume = float(ticker["quoteVolume"])
                last_price = float(ticker["lastPrice"])
                if quote_volume < 0 or last_price < 0:
                    continue
            except (ValueError, TypeError, KeyError):
                continue
            rows.append({
                **meta, "quoteVolume24h": quote_volume,
                "lastPriceSnapshot": last_price,
                "priceChangePercent24h": float(ticker.get("priceChangePercent", 0)),
                "volume24h": float(ticker.get("volume", 0)),
            })
        rows.sort(key=lambda x: (-x["quoteVolume24h"], x["symbol"]))
        snapshot = {
            "exchangeInfo_source": cfg["info"], "ticker_source": cfg["ticker"],
            "exchangeInfo_sha256_canonical_json": digest(info),
            "ticker_sha256_canonical_json": digest(tickers),
            "exchangeInfo_serverTime": info.get("serverTime"),
            "eligible_symbol_count": len(eligible),
            "eligible_symbols_missing_ticker_count": len(set(eligible) - set(ticker_map)),
            "ranking_metric": "24h quoteVolume in USDT as returned by public ticker endpoint",
            "ranking_cutoff_utc": datetime.now(timezone.utc).isoformat(),
            "top_n": rows[:args.top_n],
            "coverage_symbols": sorted(eligible.keys()),
        }
        report["sources"][name] = {
            "exchange_info_url": cfg["info"], "ticker_url": cfg["ticker"],
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "exchange_info_sha256_canonical_json": snapshot["exchangeInfo_sha256_canonical_json"],
            "ticker_sha256_canonical_json": snapshot["ticker_sha256_canonical_json"],
        }
        report["markets"][name] = snapshot
    # Check historical funding endpoint availability for each Futures top-N symbol.
    futures_top = report["markets"]["um_futures"]["top_n"]
    for item in futures_top:
        symbol = item["symbol"]
        url = f"{UM_HOSTS[0]}/fapi/v1/fundingRate?symbol={symbol}&limit=2"
        check = {"symbol": symbol, "source_url": url}
        try:
            data = fetch_json(url)
            check["request_passed"] = isinstance(data, list)
            check["returned_records"] = len(data) if isinstance(data, list) else None
            check["records"] = data[:2] if isinstance(data, list) else None
            check["historical_funding_endpoint_available"] = isinstance(data, list) and len(data) > 0
        except Exception as exc:
            check["request_passed"] = False
            check["historical_funding_endpoint_available"] = False
            check["error"] = f"{type(exc).__name__}: {exc}"
        report["funding_history_checks"].append(check)
    report["snapshot_finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = {
        "spot_eligible_symbols": report["markets"]["spot"]["eligible_symbol_count"],
        "um_perpetual_eligible_symbols": report["markets"]["um_futures"]["eligible_symbol_count"],
        "spot_top_n": [x["symbol"] for x in report["markets"]["spot"]["top_n"]],
        "um_top_n": [x["symbol"] for x in futures_top],
        "funding_endpoint_symbols_with_records": sum(x.get("historical_funding_endpoint_available", False) for x in report["funding_history_checks"]),
        "funding_endpoint_symbols_checked": len(report["funding_history_checks"]),
        "spot_ticker_missing_for_eligible": report["markets"]["spot"]["eligible_symbols_missing_ticker_count"],
        "um_ticker_missing_for_eligible": report["markets"]["um_futures"]["eligible_symbols_missing_ticker_count"],
    }
    path = out / "hd04-universe-snapshot.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"gate":"HD-04","report":str(path),"summary":report["summary"],"sources":report["sources"]}, indent=2))
    # A source snapshot can pass as a reproducible point-in-time capture even if
    # some funding requests fail; those are explicitly surfaced as coverage debt.
    complete = (
        len(report["markets"]["spot"]["top_n"]) == args.top_n
        and len(futures_top) == args.top_n
        and report["summary"]["spot_ticker_missing_for_eligible"] == 0
        and report["summary"]["um_ticker_missing_for_eligible"] == 0
    )
    return 0 if complete else 1

if __name__ == "__main__":
    raise SystemExit(main())
