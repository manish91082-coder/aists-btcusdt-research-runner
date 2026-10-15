#!/usr/bin/env python3
"""
AISTS CP-0024: Strict candle-boundary audit + selected Binance daily-archive reconciliation.

The CP-0023 output confirmed 765/765 ZIP checksum matches, but:
- found the same bad close_time row in 5m/15m/30m/1h monthly archives (2020-12-21);
- found off-grid / missing-time events in older intraday archives;
- did not check exact fixed-interval close_time = open_time + duration - 1ms;
- Binance public-data issues report monthly-vs-daily disagreements and a 2023-03-24 BTCUSDT 5m close_time defect.

This notebook:
1. checks expected open-time grid and exact close_time across ALL existing monthly ZIPs;
2. downloads DAILY reference ZIPs only for selected dates disclosed in public Binance repo discussions;
3. validates each downloaded daily ZIP against its official .CHECKSUM sidecar when available;
4. performs exact row-by-row comparison against corresponding rows in the saved monthly archives;
5. writes a separate candidate-overrides CSV using daily rows only as *provisional evidence*, never overwriting raw data.
"""
from __future__ import annotations

import csv, hashlib, json, os, re, time, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Only official downloadable public archive/checksum objects are allowed; no REST API.
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, build_opener

_OFFICIAL_REDIRECT_HOSTS = {
    "data.binance.vision",
    "s3.amazonaws.com",
    "s3-ap-northeast-1.amazonaws.com",
    "s3.ap-northeast-1.amazonaws.com",
    "s3.dualstack.ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.amazonaws.com",
    "data.binance.vision.s3-ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.ap-northeast-1.amazonaws.com",
}

def _official_object_path_ok(url, original_path=None):
    p = urlparse(url)
    if p.scheme != "https" or p.username or p.password or p.query or p.fragment or p.port not in (None, 443):
        return False
    if not (p.path.endswith(".zip") or p.path.endswith(".zip.CHECKSUM")):
        return False
    if p.hostname == "data.binance.vision":
        return p.path.startswith("/data/spot/")
    if p.hostname in _OFFICIAL_REDIRECT_HOSTS and original_path:
        return p.path in {original_path, "/data.binance.vision" + original_path}
    return False

class _OfficialArchiveRedirect(HTTPRedirectHandler):
    def __init__(self, original_path):
        super().__init__()
        self.original_path = original_path

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _official_object_path_ok(newurl, self.original_path):
            raise HTTPError(newurl, code, "Redirect outside exact official archive/checksum allowlist", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def _official_archive_get(url, timeout):
    original = urlparse(url)
    if original.hostname != "data.binance.vision" or not _official_object_path_ok(url):
        raise ValueError("Blocked non-official Binance downloadable archive/checksum URL")
    opener = build_opener(_OfficialArchiveRedirect(original.path))
    with opener.open(Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout) as response:
        final_url = response.geturl()
        if not _official_object_path_ok(final_url, original.path):
            raise ValueError("Final URL failed official host/path validation")
        return response.status, response.read()


SYMBOL = "BTCUSDT"
MONTHLY_BASE = "https://data.binance.vision/data/spot/monthly/klines"
DAILY_BASE = "https://data.binance.vision/data/spot/daily/klines"
INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d", "1mo"]
FIXED_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
TARGET_DATES = [
    "2020-12-21",
    "2021-01-21",
    "2021-04-22",
    "2021-04-23",
    "2021-09-23",
    "2021-09-29",
    "2021-11-01",
    "2022-04-13",
    "2023-03-24",
]
REFERENCE_INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d"]
MAX_WORKERS = 8
TIMEOUT = 30
RETRIES = 2
USER_AGENT = "AISTS-CP0024-Strict-Candle-Reconciliation/1.0"
ROOT = Path("/content/drive/MyDrive/AISTS/market_data/binance_spot/BTCUSDT")
FIELDS = ["open_time","open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore"]
COMPARE_FIELDS = ["open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]

def get_root():
    try:
        import google.colab  # noqa: F401
        from google.colab import drive
        if not Path("/content/drive/MyDrive").exists():
            drive.mount("/content/drive")
        if not Path("/content/drive/MyDrive").exists():
            raise RuntimeError("Google Drive is not mounted at /content/drive/MyDrive")
        return ROOT
    except ImportError:
        fallback = Path(os.environ.get("AISTS_DATA_ROOT", "/content/AISTS/market_data/binance_spot/BTCUSDT"))
        print("Colab not detected; local fallback:", fallback)
        return fallback

def fetch(url):
    return _official_archive_get(url, TIMEOUT)

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_epoch(raw):
    # Spot archives switch to microseconds for data dated 2025-01-01 onward.
    n = int(str(raw).strip())
    return n // 1000 if n >= 100_000_000_000_000 else n

def utc_iso(ms):
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).isoformat()

def open_monthly_archives(root, interval):
    folder = root / "klines" / interval
    if not folder.exists():
        return
    for p in sorted(folder.glob(f"{SYMBOL}-{interval}-????-??.zip")):
        yield p

def read_zip_rows(path):
    """Read rows from ZIP into memory. Used for a single month's file or one daily reference archive."""
    output=[]
    with zipfile.ZipFile(path) as zf:
        bad=zf.testzip()
        if bad:
            raise ValueError(f"ZIP CRC error in member {bad}")
        csvs=[n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csvs:
            raise ValueError("ZIP contains no CSV members")
        import io
        for member in csvs:
            with zf.open(member, "r") as raw:
                for line_no,row in enumerate(csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline="")),1):
                    if row:
                        output.append((member,line_no,row))
    return output

def parse_row(row):
    if len(row) < 12:
        raise ValueError(f"expected 12 fields, got {len(row)}")
    values = {
        "open_time": normalize_epoch(row[0]),
        "close_time": normalize_epoch(row[6]),
        "open": Decimal(row[1]), "high": Decimal(row[2]), "low": Decimal(row[3]),
        "close": Decimal(row[4]), "volume": Decimal(row[5]),
        "quote_asset_volume": Decimal(row[7]), "number_of_trades": int(row[8]),
        "taker_buy_base_asset_volume": Decimal(row[9]),
        "taker_buy_quote_asset_volume": Decimal(row[10]), "ignore": row[11],
    }
    for k,v in values.items():
        if isinstance(v, Decimal) and not v.is_finite():
            raise ValueError(f"{k} is not finite")
    return values

def expected_bar_end(open_ms, interval):
    if interval in FIXED_MS:
        return open_ms + FIXED_MS[interval] - 1
    if interval == "1mo":
        dt=datetime.fromtimestamp(open_ms/1000, tz=timezone.utc)
        if dt.month == 12:
            nxt=datetime(dt.year+1,1,1,tzinfo=timezone.utc)
        else:
            nxt=datetime(dt.year,dt.month+1,1,tzinfo=timezone.utc)
        return int(nxt.timestamp()*1000)-1
    return None

def expected_open_grid(open_ms, interval):
    if interval in FIXED_MS:
        return open_ms % FIXED_MS[interval] == 0
    if interval == "1mo":
        dt=datetime.fromtimestamp(open_ms/1000, tz=timezone.utc)
        return dt.day == 1 and dt.hour == dt.minute == dt.second == dt.microsecond == 0
    return True

def strict_monthly_audit(root):
    results=[]
    rows_with_close=[]
    rows_with_grid=[]
    rows_bad_ohlc=[]
    archives_bad=[]
    for interval in INTERVALS:
        paths=list(open_monthly_archives(root, interval) or [])
        count=0
        prev=None
        dup=outorder=0
        for path in paths:
            try:
                raw_rows=read_zip_rows(path)
            except Exception as e:
                archives_bad.append({"interval":interval,"filename":path.name,"error":f"{type(e).__name__}: {e}"})
                continue
            for member,line_no,row in raw_rows:
                try:
                    k=parse_row(row)
                except Exception as e:
                    rows_bad_ohlc.append({"interval":interval,"filename":path.name,"line_number":line_no,
                                          "type":"PARSE_ERROR","error":f"{type(e).__name__}: {e}","raw_row":row})
                    continue
                t=k["open_time"]; ctime=k["close_time"]
                if prev is not None:
                    if t==prev: dup+=1
                    elif t<prev: outorder+=1
                prev=t
                count+=1
                reasons=[]
                if k["low"] > min(k["open"],k["close"]): reasons.append("LOW_ABOVE_OPEN_OR_CLOSE")
                if k["high"] < max(k["open"],k["close"]): reasons.append("HIGH_BELOW_OPEN_OR_CLOSE")
                if k["low"] > k["high"]: reasons.append("LOW_ABOVE_HIGH")
                if k["volume"] < 0: reasons.append("NEGATIVE_VOLUME")
                if reasons:
                    rows_bad_ohlc.append({"interval":interval,"filename":path.name,"inner_csv":member,
                                          "line_number":line_no,"open_time_utc":utc_iso(t),
                                          "type":"OHLC_ANOMALY","reasons":reasons})
                if not expected_open_grid(t, interval):
                    rows_with_grid.append({"interval":interval,"filename":path.name,"inner_csv":member,
                                           "line_number":line_no,"open_time_utc":utc_iso(t),
                                           "open_time_raw":row[0],"type":"OFF_GRID_OPEN_TIME"})
                expected_end=expected_bar_end(t,interval)
                if expected_end is not None and ctime != expected_end:
                    rows_with_close.append({
                        "interval":interval,"filename":path.name,"inner_csv":member,"line_number":line_no,
                        "open_time_utc":utc_iso(t),"open_time_raw":row[0],
                        "actual_close_time_utc":utc_iso(ctime),"actual_close_time_raw":row[6],
                        "expected_close_time_utc":utc_iso(expected_end),"expected_close_time_ms":expected_end,
                        "difference_ms":ctime-expected_end,"type":"CLOSE_TIME_NOT_EQUAL_EXPECTED"
                    })
        results.append({"interval":interval,"archive_count":len(paths),"rows_scanned":count,
                        "duplicate_open_times":dup,"out_of_order_open_times":outorder})
        print(json.dumps({**results[-1],
                          "close_time_anomaly_count":sum(r["interval"]==interval for r in rows_with_close),
                          "off_grid_open_time_count":sum(r["interval"]==interval for r in rows_with_grid),
                          "ohlc_anomaly_count":sum(r["interval"]==interval for r in rows_bad_ohlc)}))
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    write_dict_csv(reports/"strict_close_time_anomalies.csv",rows_with_close)
    write_dict_csv(reports/"off_grid_open_time_rows.csv",rows_with_grid)
    write_dict_csv(reports/"strict_ohlc_anomalies.csv",rows_bad_ohlc)
    (reports/"strict_monthly_audit_summary.json").write_text(json.dumps({
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "results":results,
        "close_time_anomaly_count":len(rows_with_close),
        "off_grid_open_time_count":len(rows_with_grid),
        "ohlc_or_parse_anomaly_count":len(rows_bad_ohlc),
        "bad_archive_count":len(archives_bad),
        "bad_archives":archives_bad,
        "note":"This checks the exact expected close boundary and UTC open-time grid. An anomaly is an investigation flag, not permission to rewrite raw data."
    },indent=2,ensure_ascii=False),encoding="utf-8")
    print("STRICT AUDIT SUMMARY:", json.dumps({
        "close_time_anomaly_count":len(rows_with_close),
        "off_grid_open_time_count":len(rows_with_grid),
        "ohlc_or_parse_anomaly_count":len(rows_bad_ohlc),
        "bad_archive_count":len(archives_bad)
    },indent=2))
    return rows_with_close, rows_with_grid, rows_bad_ohlc, archives_bad

def write_dict_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("status,no_rows\nPASS,0\n",encoding="utf-8")
        return
    keys=sorted(set().union(*(r.keys() for r in rows)))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})

def daily_path(root, interval, day):
    return root/"reference_daily"/interval/f"{SYMBOL}-{interval}-{day}.zip"

def download_daily_one(root, interval, day):
    path=daily_path(root,interval,day)
    path.parent.mkdir(parents=True,exist_ok=True)
    filename=path.name
    url=f"{DAILY_BASE}/{SYMBOL}/{interval}/{filename}"
    checksum_url=url+".CHECKSUM"
    rec={"date":day,"interval":interval,"filename":filename,"url":url,
         "path":str(path),"download_status":None,"zip_sha256":None,
         "checksum_status":None,"official_sha256":None,"detail":None}
    try:
        if path.exists():
            with zipfile.ZipFile(path) as zf:
                bad=zf.testzip()
                if bad: raise ValueError(f"existing ZIP CRC error {bad}")
            zip_bytes=None
        else:
            last_error=None
            for attempt in range(RETRIES+1):
                try:
                    _,zip_bytes=fetch(url); break
                except HTTPError as e:
                    if e.code==404:
                        rec.update(download_status="NOT_AVAILABLE_404",detail="Daily archive HTTP 404")
                        return rec
                    last_error=f"HTTP {e.code}: {e.reason}"
                except (URLError,TimeoutError,OSError) as e:
                    last_error=f"{type(e).__name__}: {e}"
                if attempt<RETRIES: time.sleep(1+attempt)
            else:
                rec.update(download_status="DOWNLOAD_ERROR",detail=last_error)
                return rec
            tmp=path.with_suffix(".zip.part"); tmp.write_bytes(zip_bytes)
            with zipfile.ZipFile(tmp) as zf:
                bad=zf.testzip()
                if bad:
                    tmp.unlink(missing_ok=True)
                    rec.update(download_status="ZIP_CRC_ERROR",detail=f"ZIP CRC error in {bad}")
                    return rec
            tmp.replace(path)
        rec["zip_sha256"]=sha256_file(path)
        rec["download_status"]="EXISTS_VALID" if zip_bytes is None else "DOWNLOADED_VALID"
    except Exception as e:
        rec.update(download_status="LOCAL_OR_ZIP_ERROR",detail=f"{type(e).__name__}: {e}")
        return rec
    # Verify official sidecar. Store it if available.
    try:
        _,check_bytes=fetch(checksum_url)
        text=check_bytes.decode("utf-8",errors="replace").strip()
        m=re.search(r"(?i)\b([0-9a-f]{64})\b",text)
        if not m:
            rec.update(checksum_status="SIDECAR_INVALID",detail=(rec.get("detail","")+"; checksum sidecar lacks SHA256").strip("; "))
        else:
            official=m.group(1).lower(); rec["official_sha256"]=official
            rec["checksum_status"]="MATCH" if official==rec["zip_sha256"].lower() else "MISMATCH"
            if rec["checksum_status"]=="MISMATCH":
                rec["detail"]="Downloaded daily ZIP differs from official checksum"
        check_path=path.with_suffix(path.suffix+".CHECKSUM")
        check_path.write_bytes(check_bytes)
    except HTTPError as e:
        rec["checksum_status"]="SIDECAR_NOT_FOUND" if e.code==404 else "SIDECAR_HTTP_ERROR"
        rec["detail"]=f"Checksum sidecar HTTP {e.code}"
    except Exception as e:
        rec["checksum_status"]="SIDECAR_FETCH_ERROR"
        rec["detail"]=f"{type(e).__name__}: {e}"
    return rec

def download_daily_references(root):
    tasks=[(iv,day) for day in TARGET_DATES for iv in REFERENCE_INTERVALS]
    print(f"Daily references required: {len(tasks)} archive requests for {len(TARGET_DATES)} dates x {len(REFERENCE_INTERVALS)} intervals.")
    records=[]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fs={pool.submit(download_daily_one,root,iv,day):(iv,day) for iv,day in tasks}
        for i,f in enumerate(as_completed(fs),1):
            try: rec=f.result()
            except Exception as e:
                iv,day=fs[f]
                rec={"date":day,"interval":iv,"filename":f"{SYMBOL}-{iv}-{day}.zip","download_status":"INTERNAL_ERROR","checksum_status":None,"detail":repr(e)}
            records.append(rec)
            if i%10==0 or i==len(tasks):
                counts={}
                for r in records:
                    key=f"{r.get('download_status')}|{r.get('checksum_status')}"
                    counts[key]=counts.get(key,0)+1
                print(f"[{i}/{len(tasks)}] {counts}")
    records.sort(key=lambda r:(r["date"],r["interval"]))
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    write_dict_csv(reports/"daily_reference_download_manifest.csv",records)
    (reports/"daily_reference_download_manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
    counts={}
    for r in records:
        key=f"{r.get('download_status')}|{r.get('checksum_status')}"
        counts[key]=counts.get(key,0)+1
    summary={"generated_at_utc":datetime.now(timezone.utc).isoformat(),"archive_count_requested":len(tasks),
             "status_counts":counts,
             "download_errors":sum(r.get("download_status") not in ("DOWNLOADED_VALID","EXISTS_VALID") for r in records),
             "checksum_nonmatch_or_unavailable":sum(r.get("checksum_status")!="MATCH" for r in records),
             "note":"Daily archives are saved separately under reference_daily and never replace the raw monthly files."}
    (reports/"daily_reference_download_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("DAILY REFERENCE SUMMARY:",json.dumps(summary,indent=2))
    return records,summary

def load_monthly_rows_for_date(root, interval, day):
    year,month=map(int,day[:7].split("-"))
    path=root/"klines"/interval/f"{SYMBOL}-{interval}-{year:04d}-{month:02d}.zip"
    if not path.exists():
        return {}, {"status":"MONTHLY_ARCHIVE_MISSING","path":str(path)}
    out={}
    try:
        for member,line,row in read_zip_rows(path):
            try:k=parse_row(row)
            except Exception:continue
            if utc_iso(k["open_time"])[:10]==day:
                out[k["open_time"]]=(member,line,row,k)
        return out,{"status":"AVAILABLE","path":str(path)}
    except Exception as e:
        return {},{"status":"MONTHLY_ARCHIVE_READ_ERROR","path":str(path),"detail":repr(e)}

def compare_daily_to_monthly(root, daily_records):
    comparisons=[]
    override_candidates=[]
    blocked_reference=[]
    for ref in daily_records:
        day=ref["date"]; interval=ref["interval"]
        if ref.get("download_status") not in ("DOWNLOADED_VALID","EXISTS_VALID"):
            comparisons.append({"date":day,"interval":interval,"status":"DAILY_REFERENCE_UNAVAILABLE",
                                "detail":ref.get("detail"),"daily_download_status":ref.get("download_status")})
            continue
        if ref.get("checksum_status") != "MATCH":
            blocked_reference.append({"date":day,"interval":interval,"filename":ref.get("filename"),
                                      "checksum_status":ref.get("checksum_status"),"detail":ref.get("detail")})
        path=Path(ref["path"])
        try:
            daily_rows={}
            for member,line,row in read_zip_rows(path):
                try:k=parse_row(row)
                except Exception as e:
                    comparisons.append({"date":day,"interval":interval,"status":"DAILY_ROW_PARSE_ERROR",
                                        "line_number":line,"detail":repr(e)})
                    continue
                daily_rows[k["open_time"]]=(member,line,row,k)
        except Exception as e:
            comparisons.append({"date":day,"interval":interval,"status":"DAILY_ARCHIVE_READ_ERROR","detail":repr(e)})
            continue
        monthly_rows,monthly_state=load_monthly_rows_for_date(root,interval,day)
        if monthly_state["status"]!="AVAILABLE":
            comparisons.append({"date":day,"interval":interval,"status":monthly_state["status"],"detail":monthly_state})
            continue
        all_times=sorted(set(daily_rows)|set(monthly_rows))
        for t in all_times:
            d=daily_rows.get(t); m=monthly_rows.get(t)
            if d is None:
                comparisons.append({"date":day,"interval":interval,"open_time_utc":utc_iso(t),
                                    "status":"MONTHLY_ONLY_ROW","daily_reference":ref["filename"]})
                continue
            if m is None:
                comparisons.append({"date":day,"interval":interval,"open_time_utc":utc_iso(t),
                                    "status":"DAILY_ONLY_ROW","daily_reference":ref["filename"]})
                # Row may be considered a candidate only when checksum matched.
                if ref.get("checksum_status")=="MATCH":
                    dk=d[3]
                    override_candidates.append({**{"date":day,"interval":interval,"open_time_ms":t,
                        "open_time_utc":utc_iso(t),"candidate_reason":"DAILY_ROW_MISSING_FROM_MONTHLY",
                        "reference_archive":ref["filename"],"reference_sha256":ref.get("zip_sha256")},
                        **{k:str(dk[k]) for k in ["open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]}})
                continue
            dm=d[3]; mm=m[3]
            diffs=[]
            for field in COMPARE_FIELDS:
                if dm[field] != mm[field]:
                    diffs.append({"field":field,"daily":str(dm[field]),"monthly":str(mm[field])})
            if diffs:
                comparisons.append({"date":day,"interval":interval,"open_time_ms":t,"open_time_utc":utc_iso(t),
                                    "status":"VALUE_MISMATCH","different_fields":diffs,
                                    "monthly_archive":Path(monthly_state["path"]).name,
                                    "daily_archive":ref["filename"],
                                    "daily_checksum_status":ref.get("checksum_status")})
                if ref.get("checksum_status")=="MATCH":
                    override_candidates.append({**{"date":day,"interval":interval,"open_time_ms":t,
                        "open_time_utc":utc_iso(t),"candidate_reason":"DAILY_MONTHLY_VALUE_MISMATCH",
                        "reference_archive":ref["filename"],"reference_sha256":ref.get("zip_sha256")},
                        **{k:str(dm[k]) for k in ["open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]}})
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    write_dict_csv(reports/"daily_vs_monthly_row_comparison.csv",comparisons)
    write_dict_csv(reports/"candidate_daily_reference_overrides.csv",override_candidates)
    summary={
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "daily_archives_processed":sum(r.get("download_status") in ("DOWNLOADED_VALID","EXISTS_VALID") for r in daily_records),
        "compared_or_flagged_rows":len(comparisons),
        "status_counts":{},
        "candidate_override_count":len(override_candidates),
        "references_not_checksum_verified":len(blocked_reference),
        "candidate_overrides_are_automatic_authority":False,
        "note":"Override candidates are evidence only. They must not be applied to raw history until review determines the approved canonical source."
    }
    for c in comparisons:
        summary["status_counts"][c["status"]]=summary["status_counts"].get(c["status"],0)+1
    (reports/"daily_vs_monthly_comparison_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print("DAILY VS MONTHLY SUMMARY:",json.dumps(summary,indent=2))
    if blocked_reference:
        write_dict_csv(reports/"daily_references_checksum_not_matched_or_available.csv",blocked_reference)
    return comparisons,override_candidates,summary

def create_bundle(root):
    reports=root/"reports"
    bundle=reports/"AISTS_CP0024_Strict_Reconciliation_Bundle.zip"
    names=[
        "strict_monthly_audit_summary.json","strict_close_time_anomalies.csv",
        "off_grid_open_time_rows.csv","strict_ohlc_anomalies.csv",
        "daily_reference_download_manifest.csv","daily_reference_download_manifest.json",
        "daily_reference_download_summary.json","daily_vs_monthly_row_comparison.csv",
        "candidate_daily_reference_overrides.csv","daily_vs_monthly_comparison_summary.json",
    ]
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            p=reports/name
            if p.exists():zf.write(p,arcname=name)
    print("AUDIT BUNDLE:",bundle)
    print("This bundle contains reports only; the daily reference archives and original historical data remain in Drive.")

def main():
    root=get_root()
    if not root.exists():raise FileNotFoundError(f"Expected Drive data folder not found: {root}")
    print("AISTS CP-0024 | strict boundary check + daily-reference reconciliation")
    print("Drive root:",root)
    print("Raw monthly ZIP archives will never be modified.")
    strict_monthly_audit(root)
    daily_records,daily_summary=download_daily_references(root)
    compare_daily_to_monthly(root,daily_records)
    create_bundle(root)
    print("\nNEXT: Upload reports/AISTS_CP0024_Strict_Reconciliation_Bundle.zip here.")
    print("Backtests remain blocked for the affected windows until all mismatch and close-time findings are dispositioned.")

if __name__ == "__main__":
    main()