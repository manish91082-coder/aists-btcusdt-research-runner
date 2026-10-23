#!/usr/bin/env python3
"""Validate official Binance Spot 1m archives for months with failed Spot 5m checks."""
from __future__ import annotations
import argparse, calendar, csv, hashlib, io, json, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE="https://data.binance.vision"
SYMBOL="BTCUSDT"
MONTHS=["2020-02","2020-03","2020-04","2020-06","2020-11","2020-12",
        "2021-02","2021-03","2021-04","2021-08","2021-09","2023-03"]

def get(url):
    with urlopen(Request(url,headers={"User-Agent":"aists-btcusdt-research-runner/1.0"}),timeout=90) as r:
        if r.status != 200: raise ValueError(f"HTTP {r.status}: {url}")
        return r.read()

def month_bounds(month):
    y,m=map(int,month.split("-"))
    start=int(datetime(y,m,1,tzinfo=timezone.utc).timestamp()*1000)
    days=calendar.monthrange(y,m)[1]
    end=start+days*86400000
    return start,end,days*1440

def validate_1m(payload, month):
    rows=list(csv.reader(io.StringIO(payload.decode("utf-8-sig"))))
    if rows and [x.strip().lower() for x in rows[0][:6]]==["open_time","open","high","low","close","volume"]:
        rows=rows[1:]
    start,end,expected=month_bounds(month)
    previous=None; gaps=[]; bad=0
    for i,row in enumerate(rows,1):
        if len(row)!=12: raise ValueError(f"row {i}: expected 12 columns, got {len(row)}")
        raw=int(row[0]); ts=raw//1000 if raw>=100_000_000_000_000 else raw
        if ts<start or ts>=end or (ts-start)%60000: raise ValueError(f"row {i}: timestamp outside month/off 1m grid: {ts}")
        if previous is not None:
            if ts<=previous: raise ValueError(f"row {i}: duplicate or out-of-order timestamp")
            if ts-previous!=60000: gaps.append({"after_ms":previous,"before_ms":ts,"delta_ms":ts-previous})
        o,h,l,c,v=map(float,row[1:6])
        if min(o,h,l,c)<=0 or v<0 or h<max(o,c,l) or l>min(o,c,h): bad+=1
        close=int(row[6]); close=close//1000 if close>=100_000_000_000_000 else close
        if close<ts or close>ts+60000: bad+=1
        previous=ts
    if not rows: raise ValueError("empty 1m archive")
    return {"rows":len(rows),"expected_rows":expected,"row_count_complete":len(rows)==expected,
            "gap_count":len(gaps),"first_gaps":gaps[:25],"ohlc_close_time_anomalies":bad,
            "first_open_time_ms":int(rows[0][0])//1000 if int(rows[0][0])>=100_000_000_000_000 else int(rows[0][0]),
            "last_open_time_ms":int(rows[-1][0])//1000 if int(rows[-1][0])>=100_000_000_000_000 else int(rows[-1][0])}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="artifacts/btcusdt-spot-1m-gap-audit")
    a=p.parse_args(); out=Path(a.output_dir); raw=out/"raw"; raw.mkdir(parents=True,exist_ok=True)
    checks=[]
    for month in MONTHS:
        url=f"{BASE}/data/spot/monthly/klines/{SYMBOL}/1m/{SYMBOL}-1m-{month}.zip"
        item={"month":month,"dataset":"spot_1m","url":url}
        try:
            archive=get(url); sidecar=get(url+".CHECKSUM")
            expected_hash=sidecar.decode("utf-8").strip().split()[0].lower()
            actual_hash=hashlib.sha256(archive).hexdigest()
            item.update({"archive_sha256":actual_hash,"checksum_expected_sha256":expected_hash,"checksum_matches":actual_hash==expected_hash})
            if actual_hash!=expected_hash: raise ValueError("official SHA-256 sidecar mismatch")
            name=f"{month}_spot_1m.zip"; (raw/name).write_bytes(archive); item["saved_archive"]=name
            with zipfile.ZipFile(io.BytesIO(archive)) as z:
                members=[n for n in z.namelist() if not n.endswith("/")]
                if len(members)!=1: raise ValueError(f"expected one CSV member, got {len(members)}")
                payload=z.read(members[0])
            item["csv_sha256"]=hashlib.sha256(payload).hexdigest()
            item["validation"]=validate_1m(payload,month)
            v=item["validation"]
            item["status"]="PASS" if v["row_count_complete"] and v["gap_count"]==0 and v["ohlc_close_time_anomalies"]==0 else "FAIL"
            if item["status"]=="FAIL": item["error"]="1m archive has missing rows, timestamp gaps or OHLC/close-time anomalies"
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,zipfile.BadZipFile,UnicodeDecodeError) as e:
            item.update({"status":"FAIL","error":f"{type(e).__name__}: {e}"})
        checks.append(item); print(json.dumps(item,ensure_ascii=False),flush=True)
    report={"gate":"BTCUSDT-SPOT-1M-GAP-AUDIT","created_utc":datetime.now(timezone.utc).isoformat(),
            "purpose":"Check official Spot 1m archive integrity for months whose Spot 5m archives failed validation; no 5m reconstruction performed.",
            "months":MONTHS,"checks":checks,
            "summary":{"months_requested":len(MONTHS),"passed":sum(x["status"]=="PASS" for x in checks),
                       "failed":sum(x["status"]!="PASS" for x in checks),
                       "status":"PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL"},
            "limitations":["This is a source-integrity audit only; it does not reconstruct or replace any 5m candle.",
                           "No missing 1m rows are filled or inferred."]}
    path=out/"btc-usdt-spot-1m-gap-audit.json"; path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(path),**report["summary"]},indent=2),flush=True)
    return 0 if report["summary"]["status"]=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
