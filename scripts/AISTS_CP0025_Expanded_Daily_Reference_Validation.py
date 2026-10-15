#!/usr/bin/env python3
"""
AISTS CP-0025: Expand checksum-verified daily references to every date flagged by CP-0024.
Does not edit/delete monthly raw ZIPs or auto-apply corrections. No API keys, no orders.
"""
from __future__ import annotations
import csv, hashlib, json, os, re, time, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.parse import urlparse

SYMBOL = "BTCUSDT"
MONTHLY_BASE = "https://data.binance.vision/data/spot/monthly/klines"
DAILY_BASE = "https://data.binance.vision/data/spot/daily/klines"
INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d", "1mo"]
REFERENCE_INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d"]
FIXED_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
KNOWN_RESEARCH_DATES = [
    "2020-12-21", "2021-01-21", "2021-04-22", "2021-04-23",
    "2021-09-23", "2021-09-29", "2021-11-01", "2022-04-13", "2023-03-24"
]
ROOT = Path("/content/drive/MyDrive/AISTS/market_data/binance_spot/BTCUSDT")
TIMEOUT = 30
RETRIES = 2
MAX_WORKERS = 8
USER_AGENT = "AISTS-CP0025-Expanded-Daily-Reference-Validation/1.0"
FIELDS = ["open_time","open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore"]
COMPARE_FIELDS = ["open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def get_root():
    try:
        import google.colab  # noqa: F401
        from google.colab import drive
        if not Path("/content/drive/MyDrive").exists():
            drive.mount("/content/drive")
        if not Path("/content/drive/MyDrive").exists():
            raise RuntimeError("Google Drive not mounted at /content/drive/MyDrive")
        return ROOT
    except ImportError:
        fallback=Path(os.environ.get("AISTS_DATA_ROOT","/content/AISTS/market_data/binance_spot/BTCUSDT"))
        print("Colab not detected; local fallback:",fallback)
        return fallback

# Restrict public-data redirects to HTTPS and the same exact object path.
ALLOWED_DATA_HOSTS = {
    "data.binance.vision",
    "s3.amazonaws.com",
    "s3-ap-northeast-1.amazonaws.com",
    "s3.ap-northeast-1.amazonaws.com",
    "s3.dualstack.ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.amazonaws.com",
    "data.binance.vision.s3-ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.ap-northeast-1.amazonaws.com",
}

def _same_object_path(target_path, original_path):
    return target_path == original_path or target_path.endswith(original_path)

class RestrictedOfficialDataRedirect(HTTPRedirectHandler):
    def __init__(self, original_path):
        super().__init__()
        self.original_path = original_path

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_DATA_HOSTS:
            raise HTTPError(newurl, code, "Redirect host/scheme is outside official data allowlist", headers, fp)
        if not _same_object_path(parsed.path, self.original_path):
            raise HTTPError(newurl, code, "Redirect changed the requested public archive object path", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url):
    original = urlparse(url)
    if original.scheme != "https" or original.hostname != "data.binance.vision" or not original.path.startswith("/data/spot/"):
        raise ValueError("Blocked non-official Binance Public Data URL")
    req=Request(url,headers={"User-Agent":USER_AGENT})
    opener = build_opener(RestrictedOfficialDataRedirect(original.path))
    with opener.open(req,timeout=TIMEOUT) as r:
        final = urlparse(r.geturl())
        if final.scheme != "https" or final.hostname not in ALLOWED_DATA_HOSTS or not _same_object_path(final.path, original.path):
            raise ValueError("Final URL failed official-host/same-object-path validation")
        return r.status,r.read()

def normalize_epoch(raw):
    n=int(str(raw).strip())
    return n//1000 if n>=100_000_000_000_000 else n

def utc_dt(ms):
    return datetime.fromtimestamp(ms/1000,tz=timezone.utc)

def utc_iso(ms):
    return utc_dt(ms).isoformat()

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def write_rows(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("status,no_rows\nPASS,0\n",encoding="utf-8")
        return
    keys=sorted(set().union(*(r.keys() for r in rows)))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})

def parse_row(row):
    if len(row)<12:
        raise ValueError(f"Expected at least 12 fields, got {len(row)}")
    d={
        "open_time":normalize_epoch(row[0]), "close_time":normalize_epoch(row[6]),
        "open":Decimal(row[1]),"high":Decimal(row[2]),"low":Decimal(row[3]),
        "close":Decimal(row[4]),"volume":Decimal(row[5]),
        "quote_asset_volume":Decimal(row[7]),"number_of_trades":int(row[8]),
        "taker_buy_base_asset_volume":Decimal(row[9]),
        "taker_buy_quote_asset_volume":Decimal(row[10]),"ignore":row[11]
    }
    for k,v in d.items():
        if isinstance(v,Decimal) and not v.is_finite():
            raise ValueError(f"{k} is not finite")
    return d

def expected_end(open_ms,interval):
    if interval in FIXED_MS:
        return open_ms+FIXED_MS[interval]-1
    if interval=="1mo":
        dt=utc_dt(open_ms)
        nxt=datetime(dt.year+1,1,1,tzinfo=timezone.utc) if dt.month==12 else datetime(dt.year,dt.month+1,1,tzinfo=timezone.utc)
        return int(nxt.timestamp()*1000)-1
    return None

def on_grid(open_ms,interval):
    if interval in FIXED_MS:
        return open_ms%FIXED_MS[interval]==0
    if interval=="1mo":
        dt=utc_dt(open_ms)
        return dt.day==1 and dt.hour==dt.minute==dt.second==dt.microsecond==0
    return True

def archive_paths(root,interval):
    folder=root/"klines"/interval
    if not folder.exists():
        return []
    return sorted(folder.glob(f"{SYMBOL}-{interval}-????-??.zip"))

def csv_rows_from_zip(path):
    with zipfile.ZipFile(path) as zf:
        bad=zf.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure in member {bad}")
        names=[n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise ValueError("No CSV member")
        import io
        for member in names:
            with zf.open(member,"r") as raw:
                reader=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
                for line_no,row in enumerate(reader,1):
                    if row:
                        yield member,line_no,row

def date_from_row(row):
    return utc_dt(normalize_epoch(row[0])).date().isoformat()

def discover_flagged_dates(root):
    """Scan local monthly archives and CP-0024 reports; add explicit research dates."""
    dates=set(KNOWN_RESEARCH_DATES)
    evidence=[]
    # Existing CP-0024 row reports capture discrepancies even if the raw candle passes simple invariants.
    for name, date_col in [
        ("strict_close_time_anomalies.csv","open_time_utc"),
        ("off_grid_open_time_rows.csv","open_time_utc"),
        ("daily_vs_monthly_row_comparison.csv","date"),
        ("forensic_gap_events.csv","next_open_time_utc"),
    ]:
        p=root/"reports"/name
        if not p.exists():
            continue
        try:
            with p.open(newline="",encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    value=row.get(date_col,"")
                    if not value: continue
                    d=value[:10]
                    if re.match(r"^\d{4}-\d{2}-\d{2}$",d):
                        dates.add(d)
        except Exception as e:
            evidence.append({"report":name,"error":f"{type(e).__name__}: {e}"})

    scan_summary=[]
    for interval in INTERVALS:
        paths=archive_paths(root,interval)
        for path in paths:
            try:
                for member,line,row in csv_rows_from_zip(path):
                    try:
                        k=parse_row(row)
                    except Exception as e:
                        try: d=date_from_row(row)
                        except Exception: d=None
                        if d: dates.add(d)
                        evidence.append({"interval":interval,"file":path.name,"line":line,"type":"PARSE_ERROR","date":d,"detail":repr(e)})
                        continue
                    d=utc_dt(k["open_time"]).date().isoformat()
                    bad_open=not on_grid(k["open_time"],interval)
                    exp=expected_end(k["open_time"],interval)
                    bad_close=exp is not None and k["close_time"]!=exp
                    bad_ohlc=(k["low"]>min(k["open"],k["close"]) or k["high"]<max(k["open"],k["close"]) or k["low"]>k["high"] or k["volume"]<0)
                    if bad_open or bad_close or bad_ohlc:
                        dates.add(d)
                        evidence.append({"interval":interval,"file":path.name,"line":line,"date":d,
                                         "open_time_utc":utc_iso(k["open_time"]),
                                         "off_grid_open":bad_open,"close_time_mismatch":bad_close,
                                         "ohlc_anomaly":bad_ohlc,
                                         "actual_close_time_utc":utc_iso(k["close_time"]),
                                         "expected_close_time_utc":utc_iso(exp) if exp is not None else None})
            except Exception as e:
                evidence.append({"interval":interval,"file":path.name,"type":"ARCHIVE_READ_ERROR","detail":repr(e)})
        scan_summary.append({"interval":interval,"monthly_archive_count":len(paths)})
    dates=sorted(dates)
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    (reports/"cp0025_reference_dates.json").write_text(json.dumps({
        "generated_at_utc":now_utc(),"date_count":len(dates),"dates":dates,
        "known_research_dates":KNOWN_RESEARCH_DATES,
        "monthly_archive_counts":scan_summary,
        "evidence_flag_row_count":len(evidence),
        "note":"Date list is generated from CP-0024 evidence and a fresh scan of local monthly ZIPs. It is a review set, not proof that all daily archives are the canonical data."
    },indent=2,ensure_ascii=False),encoding="utf-8")
    write_rows(reports/"cp0025_flagged_monthly_rows.csv",evidence)
    print(f"Discovered {len(dates)} dates requiring daily-reference review.")
    print("Flagged date set:",", ".join(dates))
    return dates

def daily_archive_path(root,interval,day):
    return root/"reference_daily"/interval/f"{SYMBOL}-{interval}-{day}.zip"

def get_or_download_daily(root,interval,day):
    path=daily_archive_path(root,interval,day)
    path.parent.mkdir(parents=True,exist_ok=True)
    url=f"{DAILY_BASE}/{SYMBOL}/{interval}/{path.name}"
    checksum_url=url+".CHECKSUM"
    rec={"date":day,"interval":interval,"filename":path.name,"url":url,
         "path":str(path),"download_status":None,"zip_sha256":None,
         "checksum_status":None,"official_sha256":None,"detail":None}
    try:
        if path.exists():
            try:
                with zipfile.ZipFile(path) as zf:
                    bad=zf.testzip()
                    if bad: raise ValueError(f"CRC error {bad}")
                rec["download_status"]="EXISTS_VALID"
            except Exception as e:
                # Preserve an invalid pre-existing evidence file. Never silently delete it.
                rec.update(download_status="EXISTING_ARCHIVE_INVALID",
                           detail=f"Existing daily reference archive preserved; validation error: {type(e).__name__}: {e}")
                return rec
        if not path.exists():
            last_error=None
            payload=None
            for attempt in range(RETRIES+1):
                try:
                    _,payload=fetch(url)
                    break
                except HTTPError as e:
                    if e.code==404:
                        rec.update(download_status="NOT_AVAILABLE_404",detail="Official daily archive returned 404")
                        return rec
                    last_error=f"HTTPError {e.code}: {e.reason}"
                except (URLError,TimeoutError,OSError) as e:
                    last_error=f"{type(e).__name__}: {e}"
                if attempt<RETRIES: time.sleep(1+attempt)
            if payload is None:
                rec.update(download_status="DOWNLOAD_ERROR",detail=last_error)
                return rec
            tmp=path.with_suffix(".zip.part")
            tmp.write_bytes(payload)
            with zipfile.ZipFile(tmp) as zf:
                bad=zf.testzip()
                if bad:
                    tmp.unlink(missing_ok=True)
                    rec.update(download_status="ZIP_CRC_ERROR",detail=f"CRC error in {bad}")
                    return rec
            tmp.replace(path)
            rec["download_status"]="DOWNLOADED_VALID"
        rec["zip_sha256"]=sha256_file(path)
    except Exception as e:
        rec.update(download_status="LOCAL_ARCHIVE_ERROR",detail=f"{type(e).__name__}: {e}")
        return rec

    # Always re-fetch the current official sidecar; don't treat prior result text as proof.
    last_error=None
    for attempt in range(RETRIES+1):
        try:
            _,check=fetch(checksum_url)
            text=check.decode("utf-8",errors="replace").strip()
            m=re.search(r"(?i)\b([0-9a-f]{64})\b",text)
            if not m:
                rec.update(checksum_status="SIDECAR_INVALID",detail=(rec.get("detail") or ""))
            else:
                rec["official_sha256"]=m.group(1).lower()
                rec["checksum_status"]="MATCH" if rec["official_sha256"]==rec["zip_sha256"].lower() else "MISMATCH"
            cp=path.with_suffix(path.suffix+".CHECKSUM")
            cp.write_bytes(check)
            return rec
        except HTTPError as e:
            if e.code==404:
                rec.update(checksum_status="SIDECAR_NOT_FOUND",detail="Official checksum sidecar returned 404")
                return rec
            last_error=f"HTTPError {e.code}: {e.reason}"
        except (URLError,TimeoutError,OSError) as e:
            last_error=f"{type(e).__name__}: {e}"
        if attempt<RETRIES: time.sleep(1+attempt)
    rec.update(checksum_status="SIDECAR_FETCH_ERROR",detail=last_error)
    return rec

def download_references(root,dates):
    tasks=[(iv,d) for d in dates for iv in REFERENCE_INTERVALS]
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    print(f"Daily reference checks: {len(tasks)} interval-date archives ({len(dates)} dates × {len(REFERENCE_INTERVALS)} intervals).")
    records=[]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures={pool.submit(get_or_download_daily,root,iv,d):(iv,d) for iv,d in tasks}
        for i,f in enumerate(as_completed(futures),1):
            try: rec=f.result()
            except Exception as e:
                iv,d=futures[f]
                rec={"date":d,"interval":iv,"filename":f"{SYMBOL}-{iv}-{d}.zip","download_status":"INTERNAL_ERROR","checksum_status":None,"detail":repr(e)}
            records.append(rec)
            if i%25==0 or i==len(tasks):
                status_counts={}
                for r in records:
                    key=f"{r.get('download_status')}|{r.get('checksum_status')}"
                    status_counts[key]=status_counts.get(key,0)+1
                print(f"[{i}/{len(tasks)}] {status_counts}")
    records.sort(key=lambda r:(r.get("date",""),r.get("interval","")))
    write_rows(reports/"cp0025_daily_reference_manifest.csv",records)
    (reports/"cp0025_daily_reference_manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
    counts={}
    for r in records:
        key=f"{r.get('download_status')}|{r.get('checksum_status')}"
        counts[key]=counts.get(key,0)+1
    summary={"generated_at_utc":now_utc(),"expected_requests":len(tasks),"date_count":len(dates),
             "status_counts":counts,"checksum_match_count":sum(r.get("checksum_status")=="MATCH" for r in records),
             "checksum_not_match_or_unavailable_count":sum(r.get("checksum_status")!="MATCH" for r in records),
             "download_error_count":sum(r.get("download_status") not in ("DOWNLOADED_VALID","EXISTS_VALID","NOT_AVAILABLE_404") for r in records),
             "note":"Daily archive checksum match is byte-integrity evidence; it does not by itself establish which archive representation is the authoritative historical candle."}
    (reports/"cp0025_daily_reference_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print("REFERENCE DOWNLOAD SUMMARY:",json.dumps(summary,indent=2))
    return records,summary

def load_rows_by_open(path,interval,day):
    result={}
    errors=[]
    try:
        for member,line,row in csv_rows_from_zip(path):
            try:
                k=parse_row(row)
                if utc_dt(k["open_time"]).date().isoformat()==day:
                    result[k["open_time"]]={"fields":k,"member":member,"line":line,"raw":row}
            except Exception as e:
                errors.append({"file":path.name,"line":line,"error":repr(e),"raw_row":row})
    except Exception as e:
        errors.append({"file":path.name,"error":repr(e)})
    return result,errors

def compare_date_interval(root,interval,day,daily_rec):
    monthly=root/"klines"/interval/f"{SYMBOL}-{interval}-{day[:4]}-{day[5:7]}.zip"
    daily=Path(daily_rec["path"])
    if not monthly.exists():
        return [],[{"date":day,"interval":interval,"status":"MONTHLY_ARCHIVE_MISSING","monthly_path":str(monthly)}],[]
    if daily_rec.get("download_status") not in ("DOWNLOADED_VALID","EXISTS_VALID"):
        return [],[{"date":day,"interval":interval,"status":"DAILY_REFERENCE_UNAVAILABLE","detail":daily_rec.get("detail"),"download_status":daily_rec.get("download_status")}],[]
    monthly_rows,monthly_errors=load_rows_by_open(monthly,interval,day)
    daily_rows,daily_errors=load_rows_by_open(daily,interval,day)
    diffs=[]; exact_summary=[]
    all_times=sorted(set(monthly_rows)|set(daily_rows))
    checksum_ok=daily_rec.get("checksum_status")=="MATCH"
    for t in all_times:
        m=monthly_rows.get(t); d=daily_rows.get(t)
        if m is None:
            exact_summary.append({"date":day,"interval":interval,"open_time_utc":utc_iso(t),"status":"DAILY_ONLY_ROW",
                                  "daily_file":daily.name,"daily_checksum_status":daily_rec.get("checksum_status")})
            continue
        if d is None:
            exact_summary.append({"date":day,"interval":interval,"open_time_utc":utc_iso(t),"status":"MONTHLY_ONLY_ROW",
                                  "monthly_file":monthly.name,"open_time_raw":m["raw"][0]})
            continue
        mk=m["fields"]; dk=d["fields"]; changed=[]
        for field in COMPARE_FIELDS:
            if mk[field]!=dk[field]:
                changed.append({"field":field,"monthly":str(mk[field]),"daily":str(dk[field])})
        if changed:
            row={"date":day,"interval":interval,"open_time_ms":t,"open_time_utc":utc_iso(t),
                 "status":"VALUE_MISMATCH","monthly_file":monthly.name,"daily_file":daily.name,
                 "daily_checksum_status":daily_rec.get("checksum_status"),"different_fields":changed}
            diffs.append(row)
            if checksum_ok:
                exact_summary.append({**row,"candidate_reference":"CHECKSUM_VERIFIED_DAILY_CANDIDATE_ONLY"})
        else:
            exact_summary.append({"date":day,"interval":interval,"open_time_ms":t,"open_time_utc":utc_iso(t),"status":"MATCH"})
    if monthly_errors:
        exact_summary.extend({"date":day,"interval":interval,"status":"MONTHLY_ROW_PARSE_ERROR",**e} for e in monthly_errors)
    if daily_errors:
        exact_summary.extend({"date":day,"interval":interval,"status":"DAILY_ROW_PARSE_ERROR",**e} for e in daily_errors)
    return diffs,exact_summary,monthly_errors+daily_errors

def reconcile_all(root,daily_records):
    bykey={(r.get("interval"),r.get("date")):r for r in daily_records}
    all_diffs=[]; all_rows=[]; read_errors=[]
    for rec in daily_records:
        interval=rec.get("interval"); day=rec.get("date")
        if interval not in REFERENCE_INTERVALS or not day: continue
        diffs,rows,errs=compare_date_interval(root,interval,day,rec)
        all_diffs.extend(diffs); all_rows.extend(rows); read_errors.extend(errs)
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    write_rows(reports/"cp0025_value_mismatches.csv",all_diffs)
    write_rows(reports/"cp0025_daily_monthly_row_disposition.csv",all_rows)
    write_rows(reports/"cp0025_reference_read_errors.csv",read_errors)
    counts={}
    for r in all_rows:
        status=r.get("status","UNKNOWN")
        counts[status]=counts.get(status,0)+1
    summary={
        "generated_at_utc":now_utc(),
        "daily_archives_processed":len(daily_records),
        "value_mismatch_rows":len(all_diffs),
        "daily_monthly_status_counts":counts,
        "daily_checksum_verified_mismatch_rows":sum(r.get("daily_checksum_status")=="MATCH" for r in all_diffs),
        "read_error_count":len(read_errors),
        "automatic_corrections_applied":0,
        "gate":"INVESTIGATE_BEFORE_BACKTEST" if all_diffs or read_errors or any(s in counts for s in ["MONTHLY_ONLY_ROW","DAILY_ONLY_ROW"]) else "READY_FOR_SEPARATE_FINAL_AUDIT",
        "note":"No raw ZIP data was changed. Exact-open-time joins cannot automatically resolve shifted/off-grid timestamp segments. All unmatched rows and mismatches remain review candidates."
    }
    (reports/"cp0025_reconciliation_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print("RECONCILIATION SUMMARY:",json.dumps(summary,indent=2))
    return summary

def make_bundle(root):
    reports=root/"reports"
    names=[
        "cp0025_reference_dates.json","cp0025_flagged_monthly_rows.csv",
        "cp0025_daily_reference_manifest.csv","cp0025_daily_reference_manifest.json",
        "cp0025_daily_reference_summary.json","cp0025_value_mismatches.csv",
        "cp0025_daily_monthly_row_disposition.csv","cp0025_reference_read_errors.csv",
        "cp0025_reconciliation_summary.json"
    ]
    bundle=reports/"AISTS_CP0025_Expanded_Reference_Bundle.zip"
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for n in names:
            p=reports/n
            if p.exists(): zf.write(p,arcname=n)
    print("REPORT BUNDLE:",bundle)
    print("Upload this compact bundle here. Raw market data stays in Drive.")

def main():
    root=get_root()
    if not root.exists(): raise FileNotFoundError(f"Data folder missing: {root}")
    print("AISTS CP-0025 | Expanded daily-reference validation")
    print("Root:",root)
    print("Raw monthly ZIPs will not be edited or deleted.")
    dates=discover_flagged_dates(root)
    daily_records,daily_summary=download_references(root,dates)
    reconcile_all(root,daily_records)
    make_bundle(root)
    print("Backtest gate remains blocked until mismatch and unmatched-row dispositions are reviewed.")

if __name__=="__main__":
    main()