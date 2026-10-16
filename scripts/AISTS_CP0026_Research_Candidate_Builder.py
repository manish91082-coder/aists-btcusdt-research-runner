#!/usr/bin/env python3
"""
AISTS CP-0026: Build a separate, provenance-backed research-candidate dataset.
NO NETWORK DOWNLOADS. Reuses locally stored, checksum-verified monthly and daily ZIPs in Drive.
Original raw ZIPs are never edited or deleted.

Policy:
- For the 40 UTC dates flagged in CP-0025, prefer the corresponding daily public archive,
  provided its local bytes still match the already verified official SHA256 manifest.
- For other dates, use the monthly archive only if its local bytes match the official SHA256 manifest.
- Do not round/change open_time.
- Derive standardized close_time in the *candidate output only* as open_time + interval duration - 1ms.
  Preserve original open/close timestamp tokens and log any normalization.
- Build 1mo candles from the resulting 1d candidate, avoiding gaps in native 1mo archive coverage.
- Do not fill time gaps or delete duplicate rows silently. Record and gate them.
"""
from __future__ import annotations

import argparse, csv, gzip, hashlib, json, os, zipfile
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

SYMBOL = "BTCUSDT"
BASE_INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d"]
FIXED_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
ROOT = Path("/content/drive/MyDrive/AISTS/market_data/binance_spot/BTCUSDT")
CANDIDATE_ROOT = Path(os.environ.get("AISTS_DATA_ROOT", str(ROOT))) / "derived" / "research_candidate_v1" / SYMBOL
OUTPUT_FIELDS = [
    "open_time_ms","open_time_utc","open","high","low","close","volume",
    "close_time_ms","quote_asset_volume","number_of_trades",
    "taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore",
    "source_type","source_interval","source_archive","source_sha256",
    "raw_open_time_token","raw_close_time_token","close_time_normalized",
    "aggregation_bar_count","partial_calendar_month"
]
RAW_FIELDS = [
    "open_time","open","high","low","close","volume","close_time",
    "quote_asset_volume","number_of_trades","taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume","ignore"
]

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
        p = Path(os.environ.get("AISTS_DATA_ROOT", "/content/AISTS/market_data/binance_spot/BTCUSDT"))
        print("Colab not detected; using local fallback:", p)
        return p

def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_epoch(raw):
    # Binance Spot archive timestamps use milliseconds historically and microseconds from 2025.
    n = int(str(raw).strip())
    return n // 1000 if n >= 100_000_000_000_000 else n

def utc_dt(ms):
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc)

def utc_iso(ms):
    return utc_dt(ms).isoformat()

def parse_kline(row):
    if len(row) < 12:
        raise ValueError(f"Expected >=12 fields, got {len(row)}")
    k = {
        "open_time_ms": normalize_epoch(row[0]),
        "open": Decimal(row[1]), "high": Decimal(row[2]), "low": Decimal(row[3]),
        "close": Decimal(row[4]), "volume": Decimal(row[5]),
        "raw_close_time_ms": normalize_epoch(row[6]),
        "quote_asset_volume": Decimal(row[7]), "number_of_trades": int(row[8]),
        "taker_buy_base_asset_volume": Decimal(row[9]),
        "taker_buy_quote_asset_volume": Decimal(row[10]), "ignore": row[11],
        "raw_open_time_token": row[0], "raw_close_time_token": row[6],
    }
    for key, value in k.items():
        if isinstance(value, Decimal) and not value.is_finite():
            raise ValueError(f"{key} is not finite")
    return k

def expected_close(open_ms, interval):
    if interval in FIXED_MS:
        return open_ms + FIXED_MS[interval] - 1
    if interval == "1mo":
        dt = utc_dt(open_ms)
        nxt = datetime(dt.year+1,1,1,tzinfo=timezone.utc) if dt.month == 12 else datetime(dt.year,dt.month+1,1,tzinfo=timezone.utc)
        return int(nxt.timestamp()*1000)-1
    raise ValueError(f"Unknown interval {interval}")

def is_on_grid(open_ms, interval):
    if interval in FIXED_MS:
        return open_ms % FIXED_MS[interval] == 0
    if interval == "1mo":
        dt = utc_dt(open_ms)
        return dt.day == 1 and dt.hour == dt.minute == dt.second == dt.microsecond == 0
    return False

def read_zip_rows(path: Path):
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure in {bad}")
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise ValueError("ZIP contains no CSV")
        import io
        for member in names:
            with zf.open(member, "r") as raw:
                for line_no, row in enumerate(csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline="")),1):
                    if row:
                        yield member, line_no, row

def load_dict_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Required manifest not found: {path}")
    with path.open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def load_candidate_gate(manifest_path: Path, blockers_path: Path, summary_path: Path):
    """Fail closed unless a validated row manifest exists and every non-row blocker is resolved."""
    for path in (manifest_path, blockers_path, summary_path):
        if not path.is_file():
            raise RuntimeError(f"G0_BLOCKED_MISSING_QUARANTINE_GATE_FILE: {path}")
    summary=json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("status") not in {"PASS_ROW_LEVEL_MANIFEST_NONROW_BLOCKERS_REMAIN","PASS_CANDIDATE_ELIGIBILITY_READY"}:
        raise RuntimeError(f"G0_BLOCKED_UNRECOGNIZED_MANIFEST_STATUS: {summary.get('status')!r}")
    actual_manifest_sha=sha256_file(manifest_path)
    expected_manifest_sha=summary.get("row_level_manifest",{}).get("sha256")
    if actual_manifest_sha != expected_manifest_sha:
        raise RuntimeError(f"G0_BLOCKED_MANIFEST_SHA256_MISMATCH: actual={actual_manifest_sha}; expected={expected_manifest_sha}")
    manifest=load_dict_csv(manifest_path)
    expected_rows=summary.get("row_level_manifest",{}).get("rows")
    if len(manifest) != expected_rows or len(manifest) != 969:
        raise RuntimeError(f"G0_BLOCKED_MANIFEST_ROW_COUNT: actual={len(manifest)}; expected={expected_rows}")
    required={"case_id","case_class","interval","open_time_ms","disposition","canonical_source","case_closed"}
    if not manifest or not required.issubset(manifest[0]):
        raise RuntimeError("G0_BLOCKED_MANIFEST_SCHEMA_INVALID")
    keys=set()
    cases_by_key={}
    classes=Counter()
    for row in manifest:
        iv=str(row["interval"]).strip()
        ts=str(row["open_time_ms"]).strip()
        if iv not in BASE_INTERVALS + ["1mo"] or not ts.isdigit():
            raise RuntimeError(f"G0_BLOCKED_INVALID_EXACT_KEY: {row.get('case_id')}")
        key=(iv,ts)
        keys.add(key)
        cases_by_key.setdefault(key,[]).append(str(row["case_id"]))
        classes[str(row["case_class"])]+=1
        if str(row["canonical_source"]).upper() != "NONE" or str(row["case_closed"]).lower() != "false":
            raise RuntimeError(f"G0_BLOCKED_SOURCE_AUTHORITY_OR_CLOSED_CASE: {row.get('case_id')}")
    if len(keys) != len(manifest):
        raise RuntimeError(f"G0_BLOCKED_DUPLICATE_EXACT_KEYS: unique={len(keys)} rows={len(manifest)}")
    if dict(classes) != summary.get("row_level_manifest",{}).get("case_class_counts"):
        raise RuntimeError("G0_BLOCKED_MANIFEST_CLASS_COUNTS_MISMATCH")
    blockers=load_dict_csv(blockers_path)
    blocker_summary=summary.get("nonrow_blockers",{})
    if len(blockers) != blocker_summary.get("rows"):
        raise RuntimeError("G0_BLOCKED_NONROW_BLOCKER_COUNT_MISMATCH")
    if len(blockers) > 0 or blocker_summary.get("candidate_eligibility_blocked") is True:
        raise RuntimeError(f"G0_BLOCKED_NONROW_BLOCKERS_REMAIN: {len(blockers)} unresolved non-row cases")
    if summary.get("status") != "PASS_CANDIDATE_ELIGIBILITY_READY":
        raise RuntimeError(f"G0_BLOCKED_MANIFEST_NOT_APPROVED_FOR_CANDIDATE_BUILD: {summary.get('status')}")
    return keys, cases_by_key, summary

def partition_candidate_rows(rows, interval, quarantine_keys):
    """Partition candidate-shaped rows by exact key; never rounds timestamps or mutates rows."""
    kept, quarantined = [], []
    for row in rows:
        token=str(row.get("open_time_ms",""))
        if not token.isdigit():
            raise ValueError(f"candidate open_time_ms must be an exact integer token: {token!r}")
        (quarantined if (interval,token) in quarantine_keys else kept).append(row)
    return kept, quarantined

def run_gate_self_test(manifest_path: Path, blockers_path: Path, summary_path: Path):
    checks=[]
    def check(name, ok, detail):
        checks.append({"test":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
        if not ok: raise AssertionError(f"{name}: {detail}")
    try:
        load_candidate_gate(manifest_path,blockers_path,summary_path)
        blocked=False; message="gate unexpectedly allowed candidate build"
    except RuntimeError as exc:
        blocked="G0_BLOCKED_NONROW_BLOCKERS_REMAIN" in str(exc)
        message=str(exc)
    check("current_27_nonrow_blockers_fail_closed",blocked,message)
    keys={("5m","1518170294789")}
    fixture=[{"open_time_ms":"1518170294789","raw_open_time_token":"1518170294789"},
             {"open_time_ms":"1518170294790","raw_open_time_token":"1518170294790"}]
    kept,quarantined=partition_candidate_rows(fixture,"5m",keys)
    check("exact_key_quarantined",len(quarantined)==1 and quarantined[0] is fixture[0],len(quarantined))
    check("one_ms_difference_retained",len(kept)==1 and kept[0] is fixture[1],len(kept))
    check("raw_timestamp_tokens_unchanged",fixture[0]["raw_open_time_token"]=="1518170294789" and fixture[1]["raw_open_time_token"]=="1518170294790","fixture values preserved")
    other,other_q=partition_candidate_rows([fixture[0]],"15m",keys)
    check("other_interval_not_matched",len(other)==1 and not other_q,len(other))
    return {"status":"PASS","tests_passed":len(checks),"tests_total":len(checks),"tests":checks,
            "scope":"actual manifest preflight plus synthetic partition fixtures; no market data, candidate build, or backtest"}

def verify_monthly_manifest(root):
    path = root / "reports" / "official_checksum_verification.csv"
    records = load_dict_csv(path)
    bykey = {(r.get("interval"),r.get("filename")):r for r in records}
    required = []
    for interval in BASE_INTERVALS + ["1mo"]:
        folder = root / "klines" / interval
        for p in sorted(folder.glob(f"{SYMBOL}-{interval}-????-??.zip")) if folder.exists() else []:
            r = bykey.get((interval,p.name))
            if not r or r.get("status") != "MATCH":
                raise RuntimeError(f"Monthly archive lacks a MATCH in official_checksum_verification.csv: {interval}/{p.name}")
            actual = sha256_file(p)
            if actual.lower() != (r.get("local_sha256") or "").lower() or actual.lower() != (r.get("official_sha256") or "").lower():
                raise RuntimeError(f"Monthly ZIP changed since official checksum check: {p.name}")
            required.append({"interval":interval,"filename":p.name,"sha256":actual,"path":str(p)})
    print(f"Monthly archive checksum revalidation: PASS for {len(required)} local ZIPs.")
    return bykey, required

def load_daily_manifest(root):
    path = root / "reports" / "cp0025_daily_reference_manifest.csv"
    records = load_dict_csv(path)
    bykey = {}
    for r in records:
        key=(r.get("interval"),r.get("date"))
        if key in bykey:
            raise RuntimeError(f"Duplicate daily reference manifest row: {key}")
        bykey[key]=r
    return bykey, records

def verify_daily_reference(root, interval, day, manifest):
    r=manifest.get((interval,day))
    if not r:
        raise RuntimeError(f"No CP-0025 daily reference manifest row for {interval} {day}")
    if r.get("checksum_status") != "MATCH":
        raise RuntimeError(f"Daily reference was not checksum verified: {interval} {day}: {r.get('checksum_status')}")
    path=root/"reference_daily"/interval/r["filename"]
    if not path.exists():
        raise FileNotFoundError(f"Daily reference ZIP not found: {path}")
    actual=sha256_file(path)
    if actual.lower() != (r.get("zip_sha256") or "").lower() or actual.lower() != (r.get("official_sha256") or "").lower():
        raise RuntimeError(f"Daily reference ZIP changed since CP-0025 checksum validation: {path.name}")
    return path, actual

def candidate_row(k, interval, source_type, source_interval, archive, source_sha):
    op = k["open_time_ms"]
    cls = expected_close(op, interval)
    raw_close = k.get("raw_close_time_ms")
    return {
        "open_time_ms": op,
        "open_time_utc": utc_iso(op),
        "open": str(k["open"]), "high": str(k["high"]), "low": str(k["low"]),
        "close": str(k["close"]), "volume": str(k["volume"]),
        "close_time_ms": cls,
        "quote_asset_volume": str(k["quote_asset_volume"]),
        "number_of_trades": int(k["number_of_trades"]),
        "taker_buy_base_asset_volume": str(k["taker_buy_base_asset_volume"]),
        "taker_buy_quote_asset_volume": str(k["taker_buy_quote_asset_volume"]),
        "ignore": str(k.get("ignore","0")),
        "source_type": source_type, "source_interval": source_interval,
        "source_archive": archive, "source_sha256": source_sha,
        "raw_open_time_token": str(k.get("raw_open_time_token","")),
        "raw_close_time_token": str(k.get("raw_close_time_token","")),
        "close_time_normalized": bool(raw_close is not None and raw_close != cls),
        "aggregation_bar_count": "",
        "partial_calendar_month": ""
    }

def audit_and_write_interval(root, interval, flagged_dates, daily_manifest, monthly_checksums, out_path, quarantine_keys, quarantine_cases):
    interval_dir = root / "klines" / interval
    paths = sorted(interval_dir.glob(f"{SYMBOL}-{interval}-????-??.zip"))
    month_paths = {}
    for p in paths:
        # name format BTCUSDT-interval-YYYY-MM.zip
        ym=p.name.rsplit("-",2)
        year_month=(int(ym[-2]),int(ym[-1].removesuffix(".zip")))
        month_paths[year_month]=p
    days_by_month={}
    for day in flagged_dates:
        y,m=map(int,day[:7].split("-"))
        days_by_month.setdefault((y,m),[]).append(day)
    month_keys=sorted(set(month_paths)|set(days_by_month))
    disposition=[]
    issues=[]
    quarantined=[]
    summary={
        "interval":interval,"monthly_archives":len(paths),"months_processed":len(month_keys),
        "monthly_rows_kept":0,"monthly_rows_suppressed_for_flagged_dates":0,
        "daily_reference_rows_selected":0,"parse_errors":0,"checksum_verified":True,
        "candidate_rows":0,"quarantined_rows":0,"close_time_normalized_rows":0,"off_grid_open_rows":0,
        "ohlc_anomaly_rows":0,"duplicate_open_times":0,"out_of_order_open_times":0,
        "gap_events":0,"estimated_missing_intervals":0,"first_open_time_utc":None,"last_open_time_utc":None,
    }
    previous=None
    with gzip.open(out_path,"wt",newline="",encoding="utf-8",compresslevel=6) as gz:
        writer=csv.DictWriter(gz,fieldnames=OUTPUT_FIELDS,extrasaction="ignore")
        writer.writeheader()
        for ym in month_keys:
            monthly_rows=[]
            archive=month_paths.get(ym)
            if archive:
                checksum=monthly_checksums.get((interval,archive.name))
                if not checksum or checksum.get("status")!="MATCH":
                    raise RuntimeError(f"Missing monthly SHA256 evidence for {archive.name}")
                actual=sha256_file(archive)
                if actual.lower() != checksum["local_sha256"].lower() or actual.lower() != checksum["official_sha256"].lower():
                    raise RuntimeError(f"Monthly archive checksum mismatch at build time: {archive.name}")
                for member,line,row in read_zip_rows(archive):
                    try:
                        k=parse_kline(row)
                        day=utc_dt(k["open_time_ms"]).date().isoformat()
                        if day in flagged_dates:
                            summary["monthly_rows_suppressed_for_flagged_dates"] += 1
                            continue
                        monthly_rows.append(candidate_row(k,interval,"monthly_archive",interval,archive.name,actual))
                    except Exception as e:
                        summary["parse_errors"] += 1
                        issues.append({"interval":interval,"file":archive.name,"line":line,"type":"MONTHLY_PARSE_ERROR","detail":f"{type(e).__name__}: {e}"})
            daily_rows=[]
            for day in sorted(days_by_month.get(ym,[])):
                daily_path, daily_sha=verify_daily_reference(root,interval,day,daily_manifest)
                day_count=0
                for member,line,row in read_zip_rows(daily_path):
                    try:
                        k=parse_kline(row)
                        actual_day=utc_dt(k["open_time_ms"]).date().isoformat()
                        if actual_day != day:
                            issues.append({"interval":interval,"file":daily_path.name,"line":line,"type":"DAILY_ROW_DATE_MISMATCH",
                                           "expected_date":day,"actual_date":actual_day})
                            continue
                        daily_rows.append(candidate_row(k,interval,"daily_reference_override",interval,daily_path.name,daily_sha))
                        day_count+=1
                    except Exception as e:
                        summary["parse_errors"] += 1
                        issues.append({"interval":interval,"file":daily_path.name,"line":line,"type":"DAILY_PARSE_ERROR","detail":f"{type(e).__name__}: {e}"})
                summary["daily_reference_rows_selected"] += day_count
                monthly_suppressed_for_day = 0  # exact per-day count is separately derived from tracked events
                disposition.append({
                    "interval":interval,"date":day,"selected_source":"daily_reference",
                    "daily_archive":daily_path.name,"daily_sha256":daily_sha,
                    "daily_rows_selected":day_count,"reason":"CP-0025 flagged date; daily archive passed official SHA256 revalidation",
                    "raw_monthly_archives_modified":False
                })
            chunk=monthly_rows+daily_rows
            chunk.sort(key=lambda r:int(r["open_time_ms"]))
            # Audit/write: no auto-dedup; preserve defects in candidate and block if found.
            for r in chunk:
                t=int(r["open_time_ms"])
                qkey=(interval,str(t))
                if qkey in quarantine_keys:
                    qr=dict(r)
                    qr["quarantine_case_ids"]=";".join(quarantine_cases.get(qkey,[]))
                    qr["quarantine_reason"]="CP-0040 exact interval + open_time_ms key"
                    quarantined.append(qr)
                    summary["quarantined_rows"]+=1
                    continue
                if not is_on_grid(t,interval):
                    summary["off_grid_open_rows"]+=1
                    issues.append({"interval":interval,"open_time_utc":r["open_time_utc"],"type":"CANDIDATE_OFF_GRID_OPEN","source_type":r["source_type"],"source_archive":r["source_archive"]})
                if int(r["close_time_ms"]) != expected_close(t,interval):
                    issues.append({"interval":interval,"open_time_utc":r["open_time_utc"],"type":"CANDIDATE_CLOSE_TIME_FAILURE"})
                if r["close_time_normalized"]:
                    summary["close_time_normalized_rows"]+=1
                try:
                    o,h,l,c,v=[Decimal(r[k]) for k in ("open","high","low","close","volume")]
                    if l>min(o,c) or h<max(o,c) or l>h or v<0:
                        summary["ohlc_anomaly_rows"]+=1
                        issues.append({"interval":interval,"open_time_utc":r["open_time_utc"],"type":"CANDIDATE_OHLC_ANOMALY","source_type":r["source_type"]})
                except Exception as e:
                    summary["parse_errors"]+=1
                    issues.append({"interval":interval,"open_time_utc":r.get("open_time_utc"),"type":"CANDIDATE_NUMERIC_ERROR","detail":repr(e)})
                if previous is not None:
                    delta=t-previous
                    if delta==0:
                        summary["duplicate_open_times"]+=1
                        issues.append({"interval":interval,"open_time_utc":r["open_time_utc"],"type":"CANDIDATE_DUPLICATE_OPEN"})
                    elif delta<0:
                        summary["out_of_order_open_times"]+=1
                        issues.append({"interval":interval,"open_time_utc":r["open_time_utc"],"type":"CANDIDATE_OUT_OF_ORDER"})
                    elif delta>FIXED_MS[interval]:
                        summary["gap_events"]+=1
                        if delta%FIXED_MS[interval]==0:
                            summary["estimated_missing_intervals"]+=max(0,delta//FIXED_MS[interval]-1)
                            missing=delta//FIXED_MS[interval]-1
                        else:
                            summary["estimated_missing_intervals"]+=1
                            missing=None
                        if summary["gap_events"]<=10000:
                            issues.append({"interval":interval,"previous_open_time_utc":utc_iso(previous),"open_time_utc":r["open_time_utc"],
                                           "type":"CANDIDATE_TIME_GAP","delta_ms":delta,"estimated_missing_intervals":missing})
                previous=t
                summary["candidate_rows"]+=1
                if summary["first_open_time_utc"] is None:
                    summary["first_open_time_utc"]=r["open_time_utc"]
                summary["last_open_time_utc"]=r["open_time_utc"]
                summary["monthly_rows_kept"] += int(r["source_type"]=="monthly_archive")
                writer.writerow(r)
    summary["status"] = "PASS_STRUCTURAL_GAPS_RECORDED" if (
        summary["parse_errors"]==0 and summary["off_grid_open_rows"]==0 and
        summary["ohlc_anomaly_rows"]==0 and summary["duplicate_open_times"]==0 and
        summary["out_of_order_open_times"]==0
    ) else "BLOCKED_STRUCTURAL_ERRORS"
    summary["gap_policy"]="Gaps recorded, never interpolated or silently filled."
    summary["close_time_policy"]="Candidate output close_time is normalized to open_time + interval duration - 1ms. Original raw close-time token is retained."
    return summary, disposition, issues, quarantined

def create_monthly_from_daily(root, daily_candidate_path, monthly_out):
    """Create complete candidate 1mo candles from the candidate 1d series."""
    grouped={}
    with gzip.open(daily_candidate_path,"rt",newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t=int(row["open_time_ms"]); dt=utc_dt(t); key=(dt.year,dt.month)
            grouped.setdefault(key,[]).append(row)
    src_sha=sha256_file(daily_candidate_path)
    rows_written=0
    summary={"interval":"1mo","source_type":"derived_from_candidate_1d","source_file":daily_candidate_path.name,
             "source_sha256":src_sha,"candidate_rows":0,"off_grid_open_rows":0,"ohlc_anomaly_rows":0,
             "duplicate_open_times":0,"first_open_time_utc":None,"last_open_time_utc":None}
    previous=None
    with gzip.open(monthly_out,"wt",newline="",encoding="utf-8",compresslevel=6) as gz:
        w=csv.DictWriter(gz,fieldnames=OUTPUT_FIELDS,extrasaction="ignore");w.writeheader()
        for (year,month),bars in sorted(grouped.items()):
            bars.sort(key=lambda r:int(r["open_time_ms"]))
            first,last=bars[0],bars[-1]
            start_ms=int(datetime(year,month,1,tzinfo=timezone.utc).timestamp()*1000)
            nxt=datetime(year+1,1,1,tzinfo=timezone.utc) if month==12 else datetime(year,month+1,1,tzinfo=timezone.utc)
            end_ms=int(nxt.timestamp()*1000)-1
            high=max(Decimal(b["high"]) for b in bars)
            low=min(Decimal(b["low"]) for b in bars)
            volume=sum((Decimal(b["volume"]) for b in bars),Decimal("0"))
            quote=sum((Decimal(b["quote_asset_volume"]) for b in bars),Decimal("0"))
            trades=sum(int(b["number_of_trades"]) for b in bars)
            taker_base=sum((Decimal(b["taker_buy_base_asset_volume"]) for b in bars),Decimal("0"))
            taker_quote=sum((Decimal(b["taker_buy_quote_asset_volume"]) for b in bars),Decimal("0"))
            r={
                "open_time_ms":start_ms,"open_time_utc":utc_iso(start_ms),"open":first["open"],
                "high":str(high),"low":str(low),"close":last["close"],"volume":str(volume),
                "close_time_ms":end_ms,"quote_asset_volume":str(quote),"number_of_trades":trades,
                "taker_buy_base_asset_volume":str(taker_base),"taker_buy_quote_asset_volume":str(taker_quote),
                "ignore":"0","source_type":"derived_from_candidate_1d","source_interval":"1d",
                "source_archive":daily_candidate_path.name,"source_sha256":src_sha,
                "raw_open_time_token":"","raw_close_time_token":"","close_time_normalized":False,
                "aggregation_bar_count":len(bars),
                "partial_calendar_month":len(bars) != (nxt - datetime(year,month,1,tzinfo=timezone.utc)).days
            }
            if not is_on_grid(start_ms,"1mo"): summary["off_grid_open_rows"]+=1
            if previous is not None and start_ms==previous: summary["duplicate_open_times"]+=1
            previous=start_ms
            summary["candidate_rows"]+=1
            if summary["first_open_time_utc"] is None: summary["first_open_time_utc"]=r["open_time_utc"]
            summary["last_open_time_utc"]=r["open_time_utc"]
            w.writerow(r)
    summary["status"]="PASS_STRUCTURAL" if not any(summary[k] for k in ["off_grid_open_rows","ohlc_anomaly_rows","duplicate_open_times"]) else "BLOCKED_STRUCTURAL_ERRORS"
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--gate-self-test",action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--blockers")
    ap.add_argument("--gate-summary")
    ap.add_argument("--gate-test-output")
    args=ap.parse_args()
    if args.gate_self_test:
        if not (args.manifest and args.blockers and args.gate_summary):
            ap.error("--gate-self-test requires --manifest, --blockers, and --gate-summary")
        result=run_gate_self_test(Path(args.manifest),Path(args.blockers),Path(args.gate_summary))
        print(json.dumps(result,indent=2,ensure_ascii=False))
        if args.gate_test_output:
            test_out=Path(args.gate_test_output); test_out.parent.mkdir(parents=True,exist_ok=True)
            test_out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\\n",encoding="utf-8")
        return
    root=get_root()
    if not root.exists(): raise FileNotFoundError(f"Expected Drive data root not found: {root}")
    gate_dir=root/"reports"
    manifest_path=Path(args.manifest) if args.manifest else gate_dir/"CP0040_ExactKey_Quarantine_Manifest.csv"
    blockers_path=Path(args.blockers) if args.blockers else gate_dir/"CP0040_NonRow_Blockers.csv"
    gate_summary_path=Path(args.gate_summary) if args.gate_summary else gate_dir/"CP0040_ExactKey_Quarantine_Manifest_Summary.json"
    quarantine_keys,quarantine_cases,gate_summary=load_candidate_gate(manifest_path,blockers_path,gate_summary_path)
    print("CP-0040 quarantine gate PASS; exact keys loaded:",len(quarantine_keys))
    dates_path=root/"reports"/"cp0025_reference_dates.json"
    if not dates_path.exists(): raise FileNotFoundError(f"Run CP-0025 first; not found: {dates_path}")
    flagged=json.loads(dates_path.read_text(encoding="utf-8"))["dates"]
    flagged_dates=set(flagged)
    monthly_checksums,monthly_archive_manifest=verify_monthly_manifest(root)
    daily_manifest,daily_manifest_rows=load_daily_manifest(root)
    # Validate coverage for every flagged date and each base interval before modifying the derived candidate.
    missing=[]
    for day in sorted(flagged_dates):
        for interval in BASE_INTERVALS:
            if (interval,day) not in daily_manifest:
                missing.append({"date":day,"interval":interval,"reason":"no daily reference manifest entry"})
    if missing:
        raise RuntimeError(f"Flagged-day reference coverage incomplete ({len(missing)}); see notebook error and do not build candidate.")
    outdir=CANDIDATE_ROOT/"intervals"
    outdir.mkdir(parents=True,exist_ok=True)
    reports=root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    summaries=[]; all_dispositions=[]; all_issues=[]; all_quarantined=[]
    print("AISTS CP-0026 | build provisional research candidate")
    print("No downloads. No raw ZIP edits. Uses current Drive files + existing checksum evidence.")
    print(f"Flagged UTC dates: {len(flagged_dates)}; day-level source policy: official-checksum-verified daily archive for flagged days.")
    print("Other dates: checksum-reverified monthly archive. Open times are never rounded.")
    for interval in BASE_INTERVALS:
        out=outdir/f"{SYMBOL}-{interval}-research-candidate.csv.gz"
        summary,dispositions,issues,quarantined=audit_and_write_interval(root,interval,flagged_dates,daily_manifest,monthly_checksums,out,quarantine_keys,quarantine_cases)
        summary["file"]=str(out)
        summary["sha256"]=sha256_file(out)
        summaries.append(summary);all_dispositions.extend(dispositions);all_issues.extend(issues);all_quarantined.extend(quarantined)
        print(json.dumps(summary,ensure_ascii=False))
    monthly_out=outdir/f"{SYMBOL}-1mo-research-candidate.csv.gz"
    daily_path=outdir/f"{SYMBOL}-1d-research-candidate.csv.gz"
    monthly_summary=create_monthly_from_daily(root,daily_path,monthly_out)
    monthly_summary["file"]=str(monthly_out);monthly_summary["sha256"]=sha256_file(monthly_out)
    summaries.append(monthly_summary)
    write_csv_path=reports/"cp0026_day_source_disposition.csv"
    write_rows(write_csv_path,all_dispositions)
    write_rows(reports/"cp0026_candidate_quality_issues.csv",all_issues)
    write_rows(reports/"cp0026_quarantined_candidate_rows.csv",all_quarantined)
    source_counts={}
    for s in summaries:
        source_counts[s["interval"]]={k:s.get(k) for k in ["candidate_rows","monthly_rows_kept","monthly_rows_suppressed_for_flagged_dates","daily_reference_rows_selected","close_time_normalized_rows","quarantined_rows","off_grid_open_rows","ohlc_anomaly_rows","duplicate_open_times","out_of_order_open_times","gap_events","estimated_missing_intervals","status","first_open_time_utc","last_open_time_utc","sha256"]}
    blocking=[s for s in summaries if str(s.get("status","")).startswith("BLOCKED")]
    report={
        "project":"AISTS CP-0026",
        "generated_at_utc":now_utc(),"symbol":SYMBOL,"market":"spot",
        "drive_root":str(root),"candidate_root":str(CANDIDATE_ROOT),
        "flagged_date_count":len(flagged_dates),"flagged_dates":sorted(flagged_dates),
        "cp0040_quarantine_gate":{"status":"PASS","manifest_sha256":gate_summary["row_level_manifest"]["sha256"],"manifest_keys":len(quarantine_keys),"selected_source_rows_quarantined":len(all_quarantined),"quarantine_audit":"cp0026_quarantined_candidate_rows.csv"},
        "source_policy":{
            "flagged_dates":"Select daily public archive only when its local SHA256 matches CP-0025's official SHA256 evidence.",
            "unflagged_dates":"Select monthly archive only when its local SHA256 matches the published official SHA256 sidecar recorded in CP-0023.",
            "raw_archives":"Immutable; no edits/deletions.",
            "close_time":"Normalize on the derived candidate only to the deterministic interval boundary. Keep raw close-time token and boolean provenance.",
            "open_time":"Never round; any off-grid candidate open blocks structural PASS.",
            "gaps":"Record but never fill. Need interpreted gap policy before use in performance claims.",
            "monthly":"Derived from the constructed candidate 1d series to provide complete 1mo coverage and one clear source lineage."
        },
        "monthly_raw_archives_checksum_verified":len(monthly_archive_manifest),
        "daily_reference_archive_manifest_rows":len(daily_manifest_rows),
        "results":source_counts,
        "blocking_interval_count":len(blocking),
        "gate":"BLOCKED_STRUCTURAL_ERRORS" if blocking else "PROVISIONAL_CANDIDATE_BUILT_GAPS_RECORDED",
        "interpretation":"Provisional research artifact, not proof of strategy profitability or a declaration that daily archives are globally authoritative. It applies a transparent source-selection policy only to known flagged dates.",
        "important":"Do not enable live trading based on this artifact. Review per-interval gap counts and candidate_quality_issues.csv before interpreting a backtest."
    }
    (reports/"cp0026_research_candidate_manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    bundle=reports/"AISTS_CP0026_Research_Candidate_Report_Bundle.zip"
    bundle_names=["cp0026_research_candidate_manifest.json","cp0026_day_source_disposition.csv","cp0026_candidate_quality_issues.csv",
                  "cp0025_daily_reference_summary.json","cp0025_reconciliation_summary.json","cp0026_quarantined_candidate_rows.csv"]
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for name in bundle_names:
            p=reports/name
            if p.exists(): zf.write(p,arcname=name)
    print("\nFINAL CANDIDATE GATE:",report["gate"])
    print("Candidate interval files are saved in Drive:",outdir)
    print("Report bundle:",bundle)
    print("Upload the report bundle here. Do NOT upload the large candidate datasets.")
    print("Raw ZIP archives remain untouched.")

def write_rows(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("status,no_rows\nPASS,0\n",encoding="utf-8");return
    keys=sorted(set().union(*(r.keys() for r in rows)))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore");w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})

if __name__=="__main__":
    main()