#!/usr/bin/env python3
"""Validate one official Binance monthly kline archive; no API calls or trading."""
import argparse, calendar, csv, hashlib, io, json, re, sys, urllib.request, zipfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASES={"spot":"https://data.binance.vision/data/spot/monthly/klines","usdm":"https://data.binance.vision/data/futures/um/monthly/klines"}
INTERVAL_MS={"5m":300000,"15m":900000,"1h":3600000,"4h":14400000,"8h":28800000,"1d":86400000}
COLS=12

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"binance-monthly-archive-audit/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        if r.status!=200: raise RuntimeError(f"HTTP {r.status}: {url}")
        return r.read()

def checksum_digest(raw):
    m=re.fullmatch(rb"\s*([0-9a-fA-F]{64})(?:\s+[^\r\n]+)?\s*",raw)
    if not m: raise ValueError("Unrecognised official .CHECKSUM format")
    return m.group(1).decode().lower()

def month_bounds(month):
    if not re.fullmatch(r"\d{4}-\d{2}",month): raise ValueError("month must be YYYY-MM")
    y,m=map(int,month.split("-"))
    if not 1<=m<=12: raise ValueError("month must be YYYY-MM")
    start=int(datetime(y,m,1,tzinfo=timezone.utc).timestamp()*1000)
    days=calendar.monthrange(y,m)[1]
    end=int(datetime(y+(m==12),(m%12)+1,1,tzinfo=timezone.utc).timestamp()*1000)
    return start,end,days

def is_header(row):
    if len(row)!=COLS: return False
    norm=[re.sub(r"[^a-z0-9]","",x.lower().strip()) for x in row]
    choices=[{"opentime"},{"open"},{"high"},{"low"},{"close"},{"volume"},{"closetime"},{"quoteassetvolume","quotevolume"},{"numberoftrades","count"},{"takerbuybaseassetvolume","takerbuyvolume"},{"takerbuyquoteassetvolume","takerbuyquotevolume"},{"ignore"}]
    return all(v in c for v,c in zip(norm,choices))

def validate_csv(raw,market,month,interval,full):
    start,end,days=month_bounds(month); unit="us" if market=="spot" and month>="2025-01" else "ms"
    rows=[]; malformed=0; header=False; first=True
    with io.TextIOWrapper(io.BytesIO(raw),encoding="utf-8",newline="") as f:
        for n,row in enumerate(csv.reader(f),1):
            if not row or all(not x.strip() for x in row): continue
            if first:
                first=False; header=is_header(row)
                if header: continue
            if len(row)!=COLS: malformed+=1; continue
            try:
                factor=1000 if unit=="us" else 1
                t=int(row[0])//factor; ct=int(row[6])//factor
                o,h,l,c=map(Decimal,row[1:5]); v,q=Decimal(row[5]),Decimal(row[7])
                trades=int(row[8]); tb,tq=Decimal(row[9]),Decimal(row[10])
                if not all(x.is_finite() for x in (o,h,l,c,v,q,tb,tq)): raise ValueError()
                rows.append((t,ct,o,h,l,c,v,q,trades,tb,tq))
            except (ValueError,InvalidOperation,OverflowError): malformed+=1
    checks={"row_schema":"PASS" if rows and not malformed else "FAIL"}
    if not rows: return {"checks":checks,"row_count":0,"malformed_rows":malformed,"csv_header_present":header,"timestamp_unit":unit}
    ts=[r[0] for r in rows]; step=INTERVAL_MS[interval]
    gaps=[(a,b) for a,b in zip(ts,ts[1:]) if b-a>step]
    checks.update({
      "month_membership":"PASS" if all(start<=t<end for t in ts) else "FAIL",
      "duplicates":"PASS" if len(ts)==len(set(ts)) else "FAIL",
      "ordering":"PASS" if ts==sorted(ts) else "FAIL",
      "gaps":"PASS" if not gaps else "FAIL",
      "timestamp_alignment":"PASS" if all((t-start)%step==0 for t in ts) else "FAIL",
      "close_time_semantics":"PASS" if all(r[1]==r[0]+step-1 for r in rows) else "FAIL",
      "ohlc_invariants":"PASS" if all(r[4]<=r[2]<=r[3] and r[4]<=r[5]<=r[3] and r[4]<=r[3] for r in rows) else "FAIL",
      "nonnegative_volume_counts":"PASS" if all(min(r[6],r[7],r[9],r[10])>=0 and r[8]>=0 for r in rows) else "FAIL"})
    expected=(end-start)//step
    observed=set(ts)\n    missing=[t for t in range(start,end,step) if t not in observed] if full else []
    if full: checks["full_month_coverage"]="PASS" if len(rows)==expected and not missing else "FAIL"
    return {"checks":checks,"row_count":len(rows),"malformed_rows":malformed,"csv_header_present":header,"timestamp_unit":unit,
      "expected_rows_if_full_month":expected,"first_open_time_utc":datetime.fromtimestamp(min(ts)/1000,timezone.utc).isoformat(),
      "last_open_time_utc":datetime.fromtimestamp(max(ts)/1000,timezone.utc).isoformat(),"duplicate_rows":len(ts)-len(set(ts)),
      "gap_count":len(gaps),"gap_examples":[{"after":a,"before":b} for a,b in gaps[:20]],"missing_expected_rows_if_full_month":len(missing)}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--market",choices=BASES,required=True); p.add_argument("--symbol",default="BTCUSDT")
    p.add_argument("--interval",choices=INTERVAL_MS,default="5m"); p.add_argument("--month",required=True); p.add_argument("--require-full-month",action="store_true"); p.add_argument("--out",default="monthly-output")
    a=p.parse_args()
    try: month_bounds(a.month)
    except ValueError as e: p.error(str(e))
    if not re.fullmatch(r"[A-Za-z0-9]+",a.symbol): p.error("invalid symbol")
    symbol=a.symbol.upper(); name=f"{symbol}-{a.interval}-{a.month}.zip"; url=f"{BASES[a.market]}/{symbol}/{a.interval}/{name}"
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    report={"audit_id":f"{a.market}-{symbol}-{a.interval}-{a.month}","retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"market":a.market.upper(),"symbol":symbol,"interval":a.interval,"month_utc":a.month,"source_url":url,"checksum_url":url+".CHECKSUM","status":"BLOCKED","checks":{},"policy":"Historical archive validation; REST API is not called.","limitations":["Publisher checksum proves byte agreement with publisher digest, not independent economic truth.","No candles are inferred before an asset/product listing.","Workflow artifacts are temporary staging, not durable data storage."]}
    try:
        blob=fetch(url); report["checks"]["archive_download"]="PASS"; report["source_bytes"]=len(blob); report["source_sha256"]=hashlib.sha256(blob).hexdigest(); (out/name).write_bytes(blob)
        check=fetch(url+".CHECKSUM"); digest=checksum_digest(check); (out/(name+".CHECKSUM")).write_bytes(check); report["official_sha256"]=digest
        report["checks"]["official_checksum_match"]="PASS" if digest==report["source_sha256"] else "FAIL"
        if digest!=report["source_sha256"]: raise ValueError("archive SHA-256 differs from official checksum")
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            csvs=[n for n in z.namelist() if n.lower().endswith(".csv")]
            if len(csvs)!=1: raise ValueError(f"expected exactly one CSV, found {csvs!r}")
            raw=z.read(csvs[0]); report["checks"]["zip_integrity"]="PASS"; (out/Path(csvs[0]).name).write_bytes(raw)
        report.update(validate_csv(raw,a.market,a.month,a.interval,a.require_full_month))
        report["status"]="PASS" if all(v=="PASS" for v in report["checks"].values()) else "FAIL"
    except Exception as e:
        report["errors"]=[f"{type(e).__name__}: {e}"]
        if "differs from official checksum" in str(e) or "expected exactly one CSV" in str(e): report["status"]="FAIL"
        else: report["status"]="BLOCKED"
        report["checks"].setdefault("archive_download","BLOCKED")
    (out/f"{a.market}-{symbol}-{a.interval}-{a.month}.report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"audit_id":report["audit_id"],"status":report["status"],"checks":report["checks"],"errors":report.get("errors",[])},indent=2))
    return 0 if report["status"]=="PASS" else 2 if report["status"]=="BLOCKED" else 1
if __name__=="__main__": sys.exit(main())
