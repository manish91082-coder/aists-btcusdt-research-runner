#!/usr/bin/env python3
"""Read-only official checksum and exact 4h candle-gap audit for 110 cached monthly archives."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, urllib.error, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TASK = "cp0165_4h_monthly_checksum_gap_audit"
INTERVAL_MS = 4 * 60 * 60 * 1000
EXPECTED_MONTHS = 110
FIRST_MONTH = (2017, 8)
LAST_MONTH = (2026, 9)
OFFICIAL_HOSTS = {
    "data.binance.vision", "s3.amazonaws.com", "s3-ap-northeast-1.amazonaws.com",
    "s3.ap-northeast-1.amazonaws.com", "s3.dualstack.ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.amazonaws.com", "data.binance.vision.s3-ap-northeast-1.amazonaws.com",
    "data.binance.vision.s3.ap-northeast-1.amazonaws.com",
}
def utc_now():
    return datetime.now(timezone.utc).isoformat()
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()
def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
def read_csv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
def expected_periods():
    y,m=FIRST_MONTH
    while (y,m)<=LAST_MONTH:
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m==13: y,m=y+1,1
def parse_checksum(text, filename):
    hashes=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",text)))
    name_match=filename in text
    return hashes, name_match
def fetch_sidecar(url, filename):
    original=urlparse(url)
    if original.scheme!="https" or original.hostname!="data.binance.vision" or not original.path.endswith(".zip.CHECKSUM") or original.query or original.fragment:
        return {"fetch_status":"BLOCKED_URL_VALIDATION","error":"URL did not pass official HTTPS sidecar allowlist"}
    req=urllib.request.Request(url,headers={"User-Agent":"AISTS-CP0165-4H-Checksum-Audit/1.0","Accept":"text/plain"})
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            final=urlparse(response.geturl())
            body=response.read(4097)
            status=getattr(response,"status",None)
        if final.scheme!="https" or final.hostname not in OFFICIAL_HOSTS or final.path not in {original.path,"/data.binance.vision"+original.path}:
            return {"fetch_status":"BLOCKED_REDIRECT_VALIDATION","error":"Redirect outside allowlisted official checksum object"}
        if status!=200 or not body or len(body)>4096:
            return {"fetch_status":"SIDECAR_HTTP_OR_SIZE_ERROR","error":f"http={status}; bytes={len(body)}"}
        text=body.decode("utf-8",errors="strict").strip()
        hashes,name_match=parse_checksum(text,filename)
        return {"fetch_status":"FETCHED","sidecar_sha256":sha256_bytes(body),"sidecar_hashes":";".join(hashes),
                "sidecar_filename_match":name_match,"sidecar_bytes":len(body),"error":""}
    except (urllib.error.URLError,TimeoutError,UnicodeError,ValueError) as exc:
        return {"fetch_status":"SIDECAR_UNAVAILABLE","error":f"{type(exc).__name__}: {exc}"}
def timestamp_to_iso(ms):
    return datetime.fromtimestamp(ms/1000,timezone.utc).isoformat()
def read_open_times(zip_path):
    values=[]
    with zipfile.ZipFile(zip_path,"r") as zf:
        bad=zf.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failure at member {bad}")
        members=[n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(members)!=1:
            raise ValueError(f"expected one CSV member, found {len(members)}")
        with zf.open(members[0],"r") as raw:
            import io
            reader=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
            for line_no,row in enumerate(reader,1):
                if not row: continue
                try: value=int(row[0])
                except (ValueError,IndexError):
                    if line_no==1: continue
                    raise ValueError(f"non-integer open_time at line {line_no}")
                values.append(value)
    return values
def blocked_outputs(out, started, reason, inventory_rows=0):
    summary={"schema_version":1,"checkpoint":"CP-0165","task":TASK,"status":"BLOCKED_4H_AUDIT_INPUT_INVALID",
             "started_at_utc":started,"finished_at_utc":utc_now(),"blocking_reason":reason,
             "expected_months":EXPECTED_MONTHS,"archive_inventory_rows":inventory_rows,
             "checks_passed":0,"checks_total":1,"checks":[{"check_id":"frozen_inventory_and_scope","status":"FAIL","detail":reason}],
             "checksum_matches":0,"checksum_unavailable_or_mismatched":0,"gap_events":0,"estimated_missing_intervals":0,
             "network_used":False,"official_sidecar_requests":0,"monthly_zip_downloads":0,"daily_archive_downloads":0,
             "market_data_rest_api_used":False,"canonical_source":"NONE","source_cases_closed":0,"g0":"BLOCKED_GLOBAL",
             "backtest_run":False,"candidate_build":False,"strategy_promoted":False,"live_signing_broadcast_orders":"BLOCKED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Report_HI.md").write_text("# CP-0165: 4h archive checksum/gap audit\n\n- Status: BLOCKED_4H_AUDIT_INPUT_INVALID\n- Reason: "+reason+"\n- No archive downloads, candidate build, backtest, source-authority change, or live action was performed.\n",encoding="utf-8")
    write_csv(out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Details.csv",[],["period","filename","cache_status","local_sha256","zip_crc","sidecar_status","sidecar_sha256","sidecar_hashes","sidecar_filename_match","checksum_status","error"])
    write_csv(out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Gaps.csv",[],["previous_open_time_utc","next_open_time_utc","delta_ms","missing_intervals_estimate","gap_class"])
    return summary
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive-inventory",default="evidence/source_adjudication/CP0040_Reconstruction_Run_38895499283/CP0040_Baseline_Reconstruction_Archive_Inventory.csv")
    ap.add_argument("--monthly-cache",default=".cache/aists/binance-monthly-archives")
    ap.add_argument("--output-dir",default="results/cp0165_4h_archive_audit")
    args=ap.parse_args()
    started=utc_now()
    inventory_path=ROOT/args.archive_inventory
    cache=(ROOT/args.monthly_cache).resolve()
    out=(ROOT/args.output_dir).resolve()
    if not inventory_path.is_file():
        return 1 if blocked_outputs(out,started,"Frozen baseline archive inventory is missing.").get("status")=="PASS" else 0
    all_rows=read_csv(inventory_path)
    rows=[r for r in all_rows if r.get("source")=="monthly_cache" and r.get("interval")=="4h"]
    periods=list(expected_periods())
    period_counts={p:sum(1 for r in rows if str(r.get("filename","")).endswith(f"4h-{p}.zip")) for p in periods}
    if len(rows)!=EXPECTED_MONTHS or len(set(r.get("filename","") for r in rows))!=EXPECTED_MONTHS or periods!=[p for p,c in period_counts.items() if c==1]:
        return 0 if blocked_outputs(out,started,f"Expected exactly one frozen monthly 4h archive for each of 110 months; found rows={len(rows)} unique_files={len(set(r.get('filename','') for r in rows))}.",len(rows)) else 1
    if not cache.is_dir():
        return 0 if blocked_outputs(out,started,"Restored monthly archive cache is absent; ZIP downloads are prohibited.",len(rows)) else 1
    by_period={str(r["date"]):r for r in rows if r.get("date")}
    # Inventory date fields are not authoritative for scope; filenames define period keys.
    by_period={str(r["filename"]).rsplit("-",1)[-1].removesuffix(".zip"):r for r in rows}
    def inspect(row):
        filename=row["filename"]
        period=filename.removeprefix("BTCUSDT-4h-").removesuffix(".zip")
        matches=[p for p in cache.rglob(filename) if p.is_file()]
        rec={"period":period,"filename":filename,"cache_status":"","local_sha256":"","zip_crc":"",
             "sidecar_status":"","sidecar_sha256":"","sidecar_hashes":"","sidecar_filename_match":False,
             "checksum_status":"","error":"","cache_match_count":len(matches)}
        if len(matches)!=1:
            rec.update({"cache_status":"MISSING" if not matches else "DUPLICATE","checksum_status":"NOT_CHECKED",
                        "sidecar_status":"NOT_REQUESTED","error":f"cache matches={len(matches)}"})
            return rec, []
        path=matches[0]
        rec["cache_path"]=str(path.relative_to(ROOT))
        try:
            rec["local_sha256"]=sha256_file(path)
            with zipfile.ZipFile(path,"r") as zf:
                bad=zf.testzip()
            rec["zip_crc"]="PASS" if bad is None else "FAIL"
            if bad is not None: raise ValueError(f"ZIP CRC failure at member {bad}")
            times=read_open_times(path)
        except Exception as exc:
            rec.update({"cache_status":"INVALID","checksum_status":"NOT_CHECKED","sidecar_status":"NOT_REQUESTED",
                        "error":f"{type(exc).__name__}: {exc}"})
            return rec, []
        rec["cache_status"]="PRESENT"
        url=f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/4h/{filename}.CHECKSUM"
        side=fetch_sidecar(url,filename)
        rec.update({"sidecar_status":side.get("fetch_status","UNKNOWN"),"sidecar_sha256":side.get("sidecar_sha256",""),
                    "sidecar_hashes":side.get("sidecar_hashes",""),"sidecar_filename_match":side.get("sidecar_filename_match",False)})
        if side.get("error"): rec["error"]=side["error"]
        hashes=side.get("sidecar_hashes","").split(";") if side.get("sidecar_hashes") else []
        if side.get("fetch_status")=="FETCHED" and len(hashes)==1 and hashes[0]==rec["local_sha256"].lower() and side.get("sidecar_filename_match"):
            rec["checksum_status"]="MATCH"
        elif side.get("fetch_status")=="FETCHED":
            rec["checksum_status"]="MISMATCH_OR_AMBIGUOUS"
        else:
            rec["checksum_status"]="UNAVAILABLE"
        return rec,times
    results=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(inspect,row) for row in rows]
        for future in as_completed(futures):
            results.append(future.result())
    details=[x[0] for x in results]
    details.sort(key=lambda x:x["period"])
    # Audit raw ZIP candle timestamps; never fill, shift, or discard any candle.
    all_times=[]
    for rec,times in results:
        if rec["cache_status"]=="PRESENT" and rec["zip_crc"]=="PASS":
            all_times.extend(times)
    all_times.sort()
    gaps=[]
    duplicates=0
    off_grid=0
    for i,t in enumerate(all_times):
        if t % INTERVAL_MS: off_grid += 1
        if i and t==all_times[i-1]: duplicates += 1
        if i and t>all_times[i-1]:
            delta=t-all_times[i-1]
            if delta>INTERVAL_MS:
                gaps.append({"previous_open_time_utc":timestamp_to_iso(all_times[i-1]),
                             "next_open_time_utc":timestamp_to_iso(t),"delta_ms":delta,
                             "missing_intervals_estimate":max(0,delta//INTERVAL_MS-1),
                             "gap_class":"MULTIPLE_OF_4H" if delta%INTERVAL_MS==0 else "IRREGULAR_DELTA"})
    matches=sum(r["checksum_status"]=="MATCH" for r in details)
    unavailable=sum(r["checksum_status"]!="MATCH" for r in details)
    checks=[
        {"check_id":"frozen_inventory_has_110_unique_4h_months","status":"PASS" if len(rows)==110 and len(details)==110 else "FAIL","detail":f"inventory_rows={len(rows)} details={len(details)}"},
        {"check_id":"all_cached_archives_have_single_csv_crc_pass","status":"PASS" if all(r["cache_status"]=="PRESENT" and r["zip_crc"]=="PASS" for r in details) else "FAIL","detail":f"valid={sum(r['cache_status']=='PRESENT' and r['zip_crc']=='PASS' for r in details)}/110"},
        {"check_id":"all_110_official_sidecar_hashes_match","status":"PASS" if matches==110 else "FAIL","detail":f"matches={matches}; unavailable_or_mismatched={unavailable}"},
        {"check_id":"raw_candle_timestamps_audited","status":"PASS" if bool(all_times) else "FAIL","detail":f"rows={len(all_times)} duplicates={duplicates} off_grid={off_grid} gap_events={len(gaps)}"},
    ]
    status="PASS_ALL_110_OFFICIAL_CHECKSUMS_MATCH" if all(c["status"]=="PASS" for c in checks) and matches==110 else "REVIEW_REQUIRED_4H_ARCHIVE_PROVENANCE_INCOMPLETE"
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Details.csv",details,
              ["period","filename","cache_path","cache_match_count","cache_status","local_sha256","zip_crc","sidecar_status","sidecar_sha256","sidecar_hashes","sidecar_filename_match","checksum_status","error"])
    write_csv(out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Gaps.csv",gaps,
              ["previous_open_time_utc","next_open_time_utc","delta_ms","missing_intervals_estimate","gap_class"])
    summary={"schema_version":1,"checkpoint":"CP-0165","task":TASK,"status":status,"started_at_utc":started,"finished_at_utc":utc_now(),
             "expected_months":110,"archive_inventory_rows":len(rows),"months_with_single_cache_match":sum(r["cache_match_count"]==1 for r in details),
             "checksum_matches":matches,"checksum_unavailable_or_mismatched":unavailable,"official_sidecar_requests":sum(r["sidecar_status"] not in ("NOT_REQUESTED",) for r in details),
             "monthly_zip_downloads":0,"daily_archive_downloads":0,"market_data_rest_api_used":False,"network_used":True,
             "cached_zip_bytes_modified":False,"raw_source_archives_modified":False,"source_selected":False,"canonical_source":"NONE",
             "source_cases_closed":0,"g0":"BLOCKED_GLOBAL","backtest_run":False,"candidate_build":False,"strategy_promoted":False,
             "live_signing_broadcast_orders":"BLOCKED","raw_4h_rows_audited":len(all_times),"duplicate_open_times":duplicates,
             "off_grid_open_times":off_grid,"gap_events":len(gaps),"estimated_missing_intervals":sum(g["missing_intervals_estimate"] for g in gaps),
             "checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),"checks":checks}
    (out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    report=["# CP-0165: 4h monthly archive checksum and exact gap audit","",f"- Status: {status}",
            f"- Scope: {len(rows)} expected monthly 4h archives (2017-08 through 2026-09).",
            f"- Official checksum matches: {matches}/110; unavailable or mismatched: {unavailable}.",
            f"- Raw ZIP candle rows inspected: {len(all_times)}; duplicate opens: {duplicates}; off-grid opens: {off_grid}.",
            f"- Exact gap events: {len(gaps)}; estimated missing 4h intervals: {summary['estimated_missing_intervals']}.",
            "- The audit fetches only official .CHECKSUM sidecars; it does not download ZIPs or use Binance REST APIs.",
            "- G0 remains BLOCKED_GLOBAL; canonical source remains NONE; this audit does not authorize candidate builds/backtests or establish profitability.",
            "- Gap rows describe raw cached archives; no candles are interpolated, shifted, or deleted.","",
            "## Checks",""]
    report.extend([f"- {c['status']}: {c['check_id']} ({c['detail']})" for c in checks])
    (out/"CP0165_4H_Monthly_Checksum_Gap_Audit_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"checksum_matches":matches,"unavailable_or_mismatched":unavailable,
                      "raw_4h_rows_audited":len(all_times),"gap_events":len(gaps),"estimated_missing_intervals":summary["estimated_missing_intervals"]},sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
