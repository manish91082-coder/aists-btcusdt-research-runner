#!/usr/bin/env python3
"""Bounded read-only Bybit/OKX public API reachability and schema probe."""
from __future__ import annotations
import hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

START = 1788220800000  # 2026-09-01T00:00:00Z
END = 1788224400000    # 2026-09-01T01:00:00Z
UA = "aists-btcusdt-research-runner/1.0"

def fetch(name, base, path, params, provider):
    url = base + path + "?" + urlencode(params)
    item = {"name": name, "url": url, "checked_utc": datetime.now(timezone.utc).isoformat()}
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            item["http_status"] = response.status
        payload = json.loads(raw.decode("utf-8"))
        item["response_sha256"] = hashlib.sha256(raw).hexdigest()
        if provider == "bybit":
            if payload.get("retCode") != 0:
                raise ValueError("Bybit API error: " + str(payload.get("retMsg")))
            result = payload.get("result", {})
            rows = result.get("list", []) if isinstance(result, dict) else []
        else:
            if payload.get("code") != "0":
                raise ValueError("OKX API error: " + str(payload.get("msg")))
            rows = payload.get("data", [])
        if not isinstance(rows, list):
            raise ValueError("Expected list data")
        if not rows:
            raise ValueError("API returned an empty data list")
        item.update({"rows": len(rows), "sample": rows[:2]})
        if "kline" in name or "candles" in name:
            timestamps = []
            anomalies = []
            for index, row in enumerate(rows):
                try:
                    ts = int(row[0])
                    values = [float(row[i]) for i in range(1, 6)]
                    opn, high, low, close, volume = values
                    if not all(math.isfinite(value) for value in values):
                        anomalies.append("row " + str(index) + ": non-finite OHLCV")
                    if min(opn, high, low, close) <= 0 or high < max(opn, low, close) or low > min(opn, close):
                        anomalies.append("row " + str(index) + ": invalid OHLC relationship")
                    if volume < 0:
                        anomalies.append("row " + str(index) + ": negative volume")
                    if ts % 300000:
                        anomalies.append("row " + str(index) + ": timestamp off 5-minute grid")
                    if not START <= ts < END:
                        anomalies.append("row " + str(index) + ": timestamp outside requested window")
                    timestamps.append(ts)
                except (ValueError, TypeError, IndexError) as exc:
                    anomalies.append("row " + str(index) + ": malformed candle " + type(exc).__name__)
            ordered = sorted(timestamps)
            unique = sorted(set(ordered))
            duplicates = len(ordered) - len(unique)
            gaps = sum(1 for left, right in zip(unique, unique[1:]) if right - left != 300000)
            if len(unique) != 12:
                anomalies.append("expected 12 candles in the fixed one-hour window; found " + str(len(unique)))
            item.update({"timestamps_ms_sorted": ordered, "duplicate_timestamps": duplicates,
                         "non_5m_steps": gaps, "candle_anomalies": anomalies[:30]})
            if anomalies or duplicates or gaps or not ordered:
                raise ValueError("Candle validation failed: anomalies=" + str(len(anomalies)) +
                                 ", duplicates=" + str(duplicates) + ", gaps=" + str(gaps))
            item["window_rows"] = len(ordered)
        item["status"] = "PASS"
    except Exception as exc:
        item.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
    return item

def main():
    b, o = "https://api.bybit.com", "https://www.okx.com"
    checks = []
    for category in ("spot", "linear"):
        checks.append(fetch(f"bybit_{category}_5m_kline", b, "/v5/market/kline",
            {"category":category,"symbol":"BTCUSDT","interval":"5","start":str(START),"end":str(END),"limit":"100"},"bybit"))
        checks.append(fetch(f"bybit_{category}_instrument", b, "/v5/market/instruments-info",
            {"category":category,"symbol":"BTCUSDT","limit":"10"},"bybit"))
    checks.append(fetch("bybit_linear_funding", b, "/v5/market/funding/history",
        {"category":"linear","symbol":"BTCUSDT","startTime":str(START),"endTime":str(END),"limit":"100"},"bybit"))
    for inst, label, kind in (("BTC-USDT","spot","SPOT"),("BTC-USDT-SWAP","swap","SWAP")):
        checks.append(fetch(f"okx_{label}_5m_candles", o, "/api/v5/market/history-candles",
            {"instId":inst,"bar":"5m","after":str(END),"before":str(START),"limit":"100"},"okx"))
        checks.append(fetch(f"okx_{label}_instrument", o, "/api/v5/public/instruments",
            {"instType":kind,"instId":inst},"okx"))
    checks.append(fetch("okx_swap_funding", o, "/api/v5/public/funding-rate-history",
        {"instId":"BTC-USDT-SWAP","after":str(END),"before":str(START),"limit":"100"},"okx"))
    out = Path("artifacts/hd04")
    out.mkdir(parents=True, exist_ok=True)
    report = {"gate":"HD-04-alternate-source-probe","retrieved_utc":datetime.now(timezone.utc).isoformat(),
      "window_utc":{"start":"2026-09-01T00:00:00Z","end":"2026-09-01T01:00:00Z"},
      "checks":checks,"summary":{"total":len(checks),"passed":sum(x["status"]=="PASS" for x in checks),
      "failed":sum(x["status"]!="PASS" for x in checks)},
      "limitations":["Probe tests a small BTC sample only; it does not establish full exchange universe or Binance listing authority.",
      "Exchange naming, retention, volume units and funding conventions differ.","No credentials or trading endpoints are used."]}
    target = out / "hd04-alternate-sources.json"
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(target),"summary":report["summary"],
      "checks":[{"name":x["name"],"status":x["status"],"rows":x.get("rows"),"error":x.get("error")} for x in checks]},indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
