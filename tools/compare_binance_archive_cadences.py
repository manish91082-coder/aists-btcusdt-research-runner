#!/usr/bin/env python3
"""Cross-check one official Binance daily kline archive against its monthly archive.

This is a diagnostic consistency check, not an independent-source check and not a
replacement for the official REST API check. It never places orders.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, urllib.error, urllib.request, zipfile
from datetime import date, datetime, timezone
from pathlib import Path

BASES = {
    "spot": "https://data.binance.vision/data/spot",
    "usdm": "https://data.binance.vision/data/futures/um",
}
INTERVALS = {"1m":60000,"3m":180000,"5m":300000,"15m":900000,"30m":1800000,"1h":3600000,"2h":7200000,"4h":14400000,"6h":21600000,"8h":28800000,"12h":43200000,"1d":86400000,"3d":259200000,"1w":604800000}

def fetch(url: str) -> bytes:
    req=urllib.request.Request(url, headers={"User-Agent":"binance-archive-cadence-crosscheck/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 200: raise RuntimeError(f"HTTP {r.status}: {url}")
        return r.read()

def digest(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def checksum_expected(b: bytes) -> str:
    text=b.decode("utf-8", errors="replace").strip()
    m=re.match(r"^\s*([0-9a-fA-F]{64})(?:\s+.*)?$",text)
    if not m: raise ValueError(f"Unrecognised .CHECKSUM format: {text[:120]!r}")
    return m.group(1).lower()

def archive_rows(zbytes: bytes, market: str, day: date, interval: str):
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1: raise ValueError(f"Expected exactly one CSV, got {names!r}")
        raw=z.read(names[0])
    unit="us" if market=="spot" and day>=date(2025,1,1) else "ms"
    start=int(datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc).timestamp()*1000)
    end=start+86400000
    parsed={}
    for line,row in enumerate(csv.reader(io.StringIO(raw.decode("utf-8-sig"))),1):
        if not row: continue
        if len(row)!=12:
            if line==1: continue
            raise ValueError(f"Unexpected {len(row)}-column row at line {line}")
        try: ot=int(row[0])//1000 if unit=="us" else int(row[0])
        except ValueError:
            if line==1 and any(x.lower().replace("_","") in {"opentime","open time"} for x in row[:1]): continue
            raise
        if start <= ot < end:
            if ot in parsed: raise ValueError(f"Duplicate open timestamp {ot}")
            parsed[ot]=tuple(row[1:6]) + (row[7],row[8],row[9],row[10])
    return parsed

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--market",choices=tuple(BASES),required=True)
    p.add_argument("--symbol",default="BTCUSDT")
    p.add_argument("--interval",choices=tuple(INTERVALS),default="5m")
    p.add_argument("--date",required=True)
    p.add_argument("--out",default="cadence_crosscheck")
    a=p.parse_args()
    day=date.fromisoformat(a.date)
    if day.isoformat()!=a.date: p.error("--date must be canonical YYYY-MM-DD")
    sym=a.symbol.upper()
    if not re.fullmatch(r"[A-Z0-9]+",sym): p.error("Invalid symbol")
    base=BASES[a.market]; month=day.strftime("%Y-%m")
    daily=f"{base}/daily/klines/{sym}/{a.interval}/{sym}-{a.interval}-{day.isoformat()}.zip"
    monthly=f"{base}/monthly/klines/{sym}/{a.interval}/{sym}-{a.interval}-{month}.zip"
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    report={"market":a.market.upper(),"symbol":sym,"interval":a.interval,"date_utc":a.date,
            "diagnostic":"official daily-vs-monthly archive consistency; same publisher, not independent source",
            "daily_url":daily,"monthly_url":monthly,"status":"BLOCKED","checks":{},"errors":[]}
    try:
        all_rows={}
        for cadence,url in (("daily",daily),("monthly",monthly)):
            blob=fetch(url); checksum=fetch(url+".CHECKSUM")
            actual=digest(blob); expected=checksum_expected(checksum)
            (out/f"{cadence}.zip").write_bytes(blob); (out/f"{cadence}.zip.CHECKSUM").write_bytes(checksum)
            report[cadence]={"bytes":len(blob),"sha256":actual,"official_checksum_sha256":expected,
                             "checksum_match":actual==expected}
            if actual!=expected: raise ValueError(f"{cadence} archive checksum mismatch")
            all_rows[cadence]=archive_rows(blob,a.market,day,a.interval)
            report["checks"][cadence+"_checksum"]="PASS"
        d,m=all_rows["daily"],all_rows["monthly"]
        missing_daily=sorted(set(m)-set(d)); missing_monthly=sorted(set(d)-set(m))
        mismatches=[t for t in sorted(set(d)&set(m)) if d[t]!=m[t]]
        report["daily_rows_in_target_day"]=len(d); report["monthly_rows_in_target_day"]=len(m)
        report["daily_only_open_count"]=len(missing_monthly); report["monthly_only_open_count"]=len(missing_daily)
        report["value_mismatch_count"]=len(mismatches)
        report["first_mismatch_open_ms"]=mismatches[0] if mismatches else None
        interval_ms=INTERVALS[a.interval]
        expected_count=86400000//interval_ms if interval_ms<=86400000 and 86400000%interval_ms==0 else None
        report["expected_rows_for_utc_day"]=expected_count
        coverage_ok=(expected_count is None) or (len(d)==expected_count and len(m)==expected_count)
        report["checks"]["daily_utc_day_coverage"]="PASS" if coverage_ok else "FAIL"
        equal=bool(d) and d==m
        report["checks"]["daily_monthly_rows_identical"]="PASS" if equal else "FAIL"
        report["status"]="PASS" if equal and coverage_ok else "FAIL"
    except (urllib.error.URLError,TimeoutError,OSError,zipfile.BadZipFile,RuntimeError,ValueError) as e:
        report["errors"].append(f"{type(e).__name__}: {e}")
        report["status"]="BLOCKED" if isinstance(e,(urllib.error.URLError,TimeoutError)) or "HTTP " in str(e) else "FAIL"
    report["retrieved_at_utc"]=datetime.now(timezone.utc).isoformat()
    path=out/f"{a.market}-{sym}-{a.interval}-{a.date}.crosscheck.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print(f"Report written to: {path}")
    return 0 if report["status"]=="PASS" else 2

if __name__=="__main__": raise SystemExit(main())
