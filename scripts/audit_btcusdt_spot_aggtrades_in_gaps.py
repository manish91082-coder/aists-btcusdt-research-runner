#!/usr/bin/env python3
"""Cross-check known Spot kline gaps against official Spot daily aggTrades archives.

Diagnostic only. Never reconstructs, fills, or drops candles.
"""
from __future__ import annotations
import argparse, calendar, csv, hashlib, io, json, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://data.binance.vision"
SYMBOL = "BTCUSDT"
MONTHS = ["2020-02","2020-03","2020-04","2020-06","2020-11","2020-12",
          "2021-02","2021-03","2021-04","2021-08","2021-09","2023-03"]
# Exact missing intervals previously measured in the official Spot 1m archive.
GAPS = {
 "2020-02":[("2020-02-09T02:00:00Z","2020-02-09T03:00:00Z"),("2020-02-19T11:36:00Z","2020-02-19T17:30:00Z")],
 "2020-03":[("2020-03-04T09:22:00Z","2020-03-04T11:30:00Z")],
 "2020-04":[("2020-04-25T02:00:00Z","2020-04-25T04:30:00Z")],
 "2020-06":[("2020-06-28T02:00:00Z","2020-06-28T05:30:00Z")],
 "2020-11":[("2020-11-30T06:00:00Z","2020-11-30T07:00:00Z")],
 "2020-12":[("2020-12-21T14:10:00Z","2020-12-21T18:00:00Z"),("2020-12-25T02:00:00Z","2020-12-25T03:00:00Z")],
 "2021-02":[("2021-02-11T03:41:00Z","2021-02-11T05:00:00Z")],
 "2021-03":[("2021-03-06T02:00:00Z","2021-03-06T03:30:00Z")],
 "2021-04":[("2021-04-20T02:00:00Z","2021-04-20T04:30:00Z"),("2021-04-25T04:01:00Z","2021-04-25T08:45:00Z")],
 "2021-08":[("2021-08-13T02:00:00Z","2021-08-13T06:30:00Z")],
 "2021-09":[("2021-09-29T07:00:00Z","2021-09-29T09:00:00Z")],
 "2023-03":[("2023-03-24T12:40:00Z","2023-03-24T14:00:00Z")],
}
def ms(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)
def get(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent":"aists-btcusdt-research-runner/1.0"}), timeout=120) as r:
        if r.status != 200: raise ValueError(f"HTTP {r.status}: {url}")
        return r.read()
def inspect(month: str) -> dict:
    """Audit only daily archives overlapping known windows, rather than huge monthly files."""
    windows = GAPS[month]
    by_day = {}
    for a, b in windows:
        day = datetime.fromtimestamp(ms(a)/1000, timezone.utc).date()
        end_day = datetime.fromtimestamp((ms(b)-1)/1000, timezone.utc).date()
        while day <= end_day:
            by_day.setdefault(day.isoformat(), [])
            day = day.fromordinal(day.toordinal()+1)
    per_gap = [{"start_utc":a,"end_utc":b,"trade_rows":0,
                "first_trade_utc":None,"last_trade_utc":None} for a,b in windows]
    checks = []
    for day in sorted(by_day):
        url=f"{BASE}/data/spot/daily/aggTrades/{SYMBOL}/{SYMBOL}-aggTrades-{day}.zip"
        body=get(url)
        sidecar=get(url+".CHECKSUM").decode("utf-8").strip().split()[0].lower()
        digest=hashlib.sha256(body).hexdigest()
        if digest != sidecar:
            raise ValueError(f"aggTrades checksum mismatch for {day}")
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            members=[n for n in z.namelist() if not n.endswith("/")]
            if len(members)!=1:
                raise ValueError(f"expected one CSV member for {day}, got {len(members)}")
            rows=csv.reader(io.StringIO(z.read(members[0]).decode("utf-8-sig")))
            for row in rows:
                if len(row)<6: continue
                try: t=int(row[5])
                except (ValueError,TypeError): continue
                for g,(a,b) in zip(per_gap,windows):
                    lo,hi=ms(a),ms(b)
                    if lo <= t < hi:
                        stamp=datetime.fromtimestamp(t/1000,timezone.utc).isoformat()
                        g["trade_rows"]+=1
                        if g["first_trade_utc"] is None or stamp < g["first_trade_utc"]:
                            g["first_trade_utc"]=stamp
                        if g["last_trade_utc"] is None or stamp > g["last_trade_utc"]:
                            g["last_trade_utc"]=stamp
        checks.append({"date_utc":day,"url":url,"sha256":digest,"checksum_matches":True})
    return {"month":month,"status":"PASS","daily_archives_checked":checks,
            "gaps":per_gap,
            "interpretation_limit":"A positive trade count proves trades occurred inside the interval. Zero counts require checking archive coverage and boundary semantics; they do not by themselves authorize candle reconstruction."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="artifacts/btcusdt-spot-aggtrade-gap-audit")
    args=p.parse_args(); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    results=[]
    for month in MONTHS:
        try: item=inspect(month)
        except Exception as e: item={"month":month,"status":"ERROR","error":f"{type(e).__name__}: {e}"}
        results.append(item); print(json.dumps(item,ensure_ascii=False),flush=True)
    report={"gate":"OFFICIAL-SPOT-AGGTRADES-GAP-CROSSCHECK","created_utc":datetime.now(timezone.utc).isoformat(),
            "source":"Binance public daily Spot aggTrades archives and official CHECKSUM sidecars",
            "months":MONTHS,"results":results,
            "summary":{"months_requested":len(MONTHS),"completed":sum(x["status"]=="PASS" for x in results),"errors":sum(x["status"]=="ERROR" for x in results)},
            "limitations":["Independent trade-level cross-check only; no candle reconstruction.","Checksum confirms archive bytes against sidecar, not completeness of market events.","Zero observed trades are not sufficient evidence to relax kline continuity checks."]}
    path=out/"btc-usdt-spot-aggtrade-gap-audit.json"; path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(path),**report["summary"]},indent=2),flush=True)
    return 0 if report["summary"]["completed"]==len(MONTHS) else 1
if __name__=="__main__": raise SystemExit(main())
