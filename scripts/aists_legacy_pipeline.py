#!/usr/bin/env python3
"""Reproducible CP-0025 -> CP-0026 -> CP-0027 execution on GitHub Actions.

Official monthly ZIPs are revalidated against freshly retrieved .CHECKSUM sidecars.
CP-0025 discovers/reconciles flagged dates and downloads their official daily references.
CP-0026 constructs provisional candidates without editing raw ZIPs.
CP-0027 is executed from its vendored source, unmodified.
No Binance REST market-data API, exchange credentials, signing, or live orders.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

INTERVALS=("5m","15m","30m","1h","4h","1d","1mo")
FIRST=(2017,8); LAST=(2026,9)
KNOWN_MONTHLY_1MO_UNAVAILABLE={"2024-03","2026-03","2026-07","2026-08","2026-09"}
REPO=Path(__file__).resolve().parents[1]
SCRIPTS=REPO/"scripts"


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def months():
    y,m=FIRST
    while (y,m)<=LAST:
        yield y,m
        if m==12: y,m=y+1,1
        else: m+=1


def import_module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import reviewed module: {path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def zip_inventory(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload),"r") as z:
            bad=z.testzip()
            regular=[i for i in z.infolist() if not i.is_dir()]
            csvs=[i.filename for i in regular if i.filename.lower().endswith(".csv")]
            return {
                "zip_crc":"PASS" if bad is None else "FAIL",
                "zip_bad_member":bad or "",
                "member_count":len(regular),
                "csv_member_count":len(csvs),
                "member_names":json.dumps([i.filename for i in regular],ensure_ascii=False),
                "status":"PASS" if bad is None and len(regular)>=1 and len(csvs)>=1 else "REVIEW_REQUIRED",
                "error":"" if bad is None and csvs else (f"ZIP CRC: {bad}" if bad else "No CSV member"),
            }
    except Exception as exc:
        return {"zip_crc":"FAIL","zip_bad_member":"","member_count":0,"csv_member_count":0,
                "member_names":"[]","status":"REVIEW_REQUIRED","error":f"{type(exc).__name__}: {exc}"}


def self_tests(core):
    tests=[]
    def add(name, ok, detail=""):
        tests.append({"test":name,"status":"PASS" if ok else "FAIL","detail":detail})
    rel="/monthly/klines/BTCUSDT/4h/BTCUSDT-4h-2020-01.zip"
    good="https://data.binance.vision/data/spot"+rel
    add("official_archive_url_exact_host_path",core.official_url(good,rel))
    add("reject_rest_api_host",not core.official_url("https://api.binance.com/api/v3/klines","/api/v3/klines"))
    add("reject_lookalike_host",not core.official_url("https://data.binance.vision.evil.example/data/spot"+rel,rel))
    add("reject_http",not core.official_url(good.replace("https:","http:"),rel))
    add("target_archive_count",sum(1 for _ in INTERVALS for _ in months())==770)
    add("known_monthly_missing_allowlist",KNOWN_MONTHLY_1MO_UNAVAILABLE=={"2024-03","2026-03","2026-07","2026-08","2026-09"})
    parsed,bound,_=core.parse_checksum(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa BTCUSDT-4h-2020-01.zip","BTCUSDT-4h-2020-01.zip")
    add("official_checksum_hash_filename_binding",parsed=="a"*64 and bound)
    sample=io.BytesIO()
    with zipfile.ZipFile(sample,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("BTCUSDT-4h-2020-01.csv","1,1,1,1,1,0,1439,0,0,0,0,0\n")
    inv=zip_inventory(sample.getvalue())
    add("synthetic_zip_crc_and_csv_inventory",inv["zip_crc"]=="PASS" and inv["csv_member_count"]==1)
    add("network_target_is_official_archive_only", 'url="https://data.binance.vision/data/spot"+rel' in Path(__file__).read_text(encoding="utf-8") and 'sumurl=url+".CHECKSUM"' in Path(__file__).read_text(encoding="utf-8"))
    add("legacy_sources_present",all((SCRIPTS/f"AISTS_CP00{n}_{label}.py").exists() for n,label in [
        ("25","Expanded_Daily_Reference_Validation"),("26","Research_Candidate_Builder"),("27","MultiTimeframe_Baseline_Backtest")
    ]))
    return {"total":len(tests),"passed":sum(t["status"]=="PASS" for t in tests),"tests":tests}


def acquire_one(core, interval, year, month, cache_root, data_root):
    name=f"BTCUSDT-{interval}-{year:04d}-{month:02d}.zip"
    rel=f"/monthly/klines/BTCUSDT/{interval}/{name}"
    relsum=rel+".CHECKSUM"
    url="https://data.binance.vision/data/spot"+rel
    checksum_url=url+".CHECKSUM"
    row={
        "interval":interval,"month":f"{year:04d}-{month:02d}","filename":name,
        "zip_url":url,"checksum_url":checksum_url,"checksum_http":"",
        "checksum_sha256":"","official_sha256":"","local_sha256":"",
        "checksum_name_bound":False,"cache_used":False,"zip_http":"",
        "zip_bytes":0,"zip_sha256_match":False,"zip_crc":"NOT_RUN",
        "member_count":0,"csv_member_count":0,"content_qa":"PENDING_CP0025",
        "status":"REVIEW_REQUIRED","error":"",
    }
    # Always read the official sidecar first, including for cached bytes.
    side=core.get_bytes(checksum_url,relsum)
    row["checksum_http"]=side.get("status","ERROR")
    if not side.get("ok"):
        row["error"]="CHECKSUM fetch failed: "+str(side.get("error",side.get("status")))
        if interval=="1mo" and row["month"] in KNOWN_MONTHLY_1MO_UNAVAILABLE and "404" in row["error"]:
            row["status"]="KNOWN_UNAVAILABLE_404"
        return row
    row["checksum_sha256"]=sha256_bytes(side["body"])
    expected,bound,side_text=core.parse_checksum(side["body"],name)
    row["official_sha256"]=expected or ""
    row["checksum_name_bound"]=bool(bound)
    if not expected or not bound:
        row["error"]="Invalid CHECKSUM format or filename binding."
        return row

    # Prefer the old cache name if byte-identical. If stale, keep it untouched and use a versioned verified cache file.
    folder=cache_root/interval/f"{year:04d}-{month:02d}"
    folder.mkdir(parents=True,exist_ok=True)
    original_cache=folder/name
    versioned_cache=folder/f"{name}.{expected[:16]}.verified"
    body=None
    chosen_cache=None
    for candidate in (original_cache,versioned_cache):
        if candidate.is_file():
            try:
                if sha256_file(candidate)==expected:
                    body=candidate.read_bytes(); chosen_cache=candidate
                    row["cache_used"]=True; row["zip_http"]="CACHE_SHA256_MATCH_FRESH_SIDECAR"
                    break
            except OSError:
                pass
    if body is None:
        got=core.get_bytes(url,rel)
        row["zip_http"]=got.get("status","ERROR")
        if not got.get("ok"):
            row["error"]="ZIP fetch failed: "+str(got.get("error",got.get("status")))
            if interval=="1mo" and row["month"] in KNOWN_MONTHLY_1MO_UNAVAILABLE and "404" in row["error"]:
                row["status"]="KNOWN_UNAVAILABLE_404"
            return row
        body=got["body"]
    row["zip_bytes"]=len(body)
    actual=sha256_bytes(body)
    row["local_sha256"]=actual
    row["zip_sha256_match"]=actual==expected
    if actual!=expected:
        row["error"]="ZIP SHA-256 differs from freshly fetched official CHECKSUM."
        row["status"]="CHECKSUM_MISMATCH"
        return row

    inv=zip_inventory(body)
    row.update({k:v for k,v in inv.items() if k in ("zip_crc","member_count","csv_member_count")})
    if inv["status"]!="PASS":
        # Keep checksum-valid raw bytes in a quarantine area, not in the candidate input directory.
        quarantine=data_root/"quarantine"/"monthly_zip_crc_or_structure_review"
        quarantine.mkdir(parents=True,exist_ok=True)
        target=quarantine/name
        if not target.exists(): target.write_bytes(body)
        row["error"]=inv["error"] or "ZIP CRC/CSV inventory requires review"
        row["status"]="CHECKSUM_MATCH_ARCHIVE_REVIEW_QUARANTINED"
        return row

    # Save a verified cache copy only after official SHA-256 and ZIP CRC/CSV inventory pass.
    if chosen_cache is None:
        target_cache=original_cache if not original_cache.exists() else versioned_cache
        if not target_cache.exists():
            tmp=target_cache.with_name(target_cache.name+".part")
            tmp.write_bytes(body)
            if sha256_file(tmp)!=expected:
                tmp.unlink(missing_ok=True)
                row["error"]="Post-write cache hash mismatch."
                return row
            tmp.replace(target_cache)
    # Place byte-identical, verified source copy in the isolated workspace for the frozen CP scripts.
    dest_dir=data_root/"klines"/interval
    dest_dir.mkdir(parents=True,exist_ok=True)
    dest=dest_dir/name
    if dest.exists():
        if sha256_file(dest)!=expected:
            row["error"]="Existing workspace archive conflicts with fresh official checksum; not overwritten."
            row["status"]="LOCAL_SOURCE_CONFLICT"
            return row
    else:
        tmp=dest.with_name(dest.name+".part")
        tmp.write_bytes(body)
        if sha256_file(tmp)!=expected:
            tmp.unlink(missing_ok=True)
            row["error"]="Post-write source-copy hash mismatch."
            return row
        tmp.replace(dest)
    row["status"]="MATCH"
    row["content_qa"]="PENDING_CP0025"
    row["error"]=""
    return row


def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("status,no_rows\nPASS,0\n",encoding="utf-8")
        return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)


def run_stage(script, env, log_dir, timeout=6600):
    label=script.stem
    started=time.monotonic()
    proc=subprocess.run([sys.executable,str(script)],cwd=str(REPO),env=env,text=True,
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    (log_dir/f"{label}.stdout.log").write_text(proc.stdout[-300000:],encoding="utf-8")
    (log_dir/f"{label}.stderr.log").write_text(proc.stderr[-150000:],encoding="utf-8")
    return {"stage":label,"exit_code":proc.returncode,"elapsed_seconds":round(time.monotonic()-started,2),
            "stdout_tail":proc.stdout[-12000:],"stderr_tail":proc.stderr[-5000:]}


def copy_if_exists(src, zipobj, arcname, inventory):
    if src.is_file():
        size=src.stat().st_size
        digest=sha256_file(src)
        zipobj.write(src,arcname=arcname,compress_type=zipfile.ZIP_DEFLATED)
        inventory.append({"path":arcname,"bytes":size,"sha256":digest})
        return True
    return False


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="results/legacy_pipeline")
    ap.add_argument("--cache-dir",default=".cache/aists/binance-monthly-archives")
    ap.add_argument("--data-root",default=".aists_workspace/market_data/binance_spot/BTCUSDT")
    args=ap.parse_args()
    out=(REPO/args.output_dir).resolve()
    cache=(REPO/args.cache_dir).resolve()
    data_root=(REPO/args.data_root).resolve()
    reports=data_root/"reports"; reports.mkdir(parents=True,exist_ok=True)
    logs=out/"logs"; logs.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc)
    core=import_module(SCRIPTS/"historical_reference_replay.py","aists_historical_core")
    tests=self_tests(core)
    (out/"self_tests.json").write_text(json.dumps(tests,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if tests["passed"]!=tests["total"]:
        summary={"checkpoint":"AISTS-GH-LEGACY-001","status":"BLOCKED_SELF_TEST_FAILURE","self_tests":tests,
                 "started_at_utc":started.isoformat(),"finished_at_utc":now_utc(),"raw_source_mutation":False}
        (out/"legacy_pipeline_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(summary,indent=2,ensure_ascii=False));return 2

    months_list=list(months())
    tasks=[(interval,y,m) for interval in INTERVALS for y,m in months_list]
    records=[]
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures={pool.submit(acquire_one,core,iv,y,m,cache,data_root):(iv,y,m) for iv,y,m in tasks}
        for fut in as_completed(futures):
            iv,y,m=futures[fut]
            try: rec=fut.result()
            except Exception as exc:
                rec={"interval":iv,"month":f"{y:04d}-{m:02d}","filename":f"BTCUSDT-{iv}-{y:04d}-{m:02d}.zip",
                     "zip_url":"","checksum_url":"","status":"ACQUISITION_EXCEPTION","error":f"{type(exc).__name__}: {exc}",
                     "zip_sha256_match":False,"cache_used":False}
            records.append(rec)
    records.sort(key=lambda r:(r.get("interval",""),r.get("month","")))
    write_csv(out/"monthly_archive_acquisition_manifest.csv",records)
    write_csv(reports/"official_checksum_verification.csv",[
        {"interval":r.get("interval"),"filename":r.get("filename"),
         "path":str(data_root/"klines"/str(r.get("interval"))/str(r.get("filename"))),
         "local_sha256":r.get("local_sha256",""),"official_sha256":r.get("official_sha256",""),
         "status":"MATCH" if r.get("status")=="MATCH" and r.get("local_sha256")==r.get("official_sha256") else r.get("status"),
         "zip_crc":r.get("zip_crc","NOT_RUN"),"member_count":r.get("member_count",0),
         "csv_member_count":r.get("csv_member_count",0),"checksum_sidecar_sha256":r.get("checksum_sha256",""),
         "content_qa_status":"PENDING_CP0025","error":r.get("error","")}
        for r in records
    ])

    known_unavailable=[r for r in records if r.get("status")=="KNOWN_UNAVAILABLE_404"]
    unknown_failures=[r for r in records if r.get("status")!="MATCH" and r.get("status")!="KNOWN_UNAVAILABLE_404"]
    coverage={"expected_objects":len(tasks),"match_archives":sum(r.get("status")=="MATCH" for r in records),
              "known_unavailable_1mo_404":len(known_unavailable),"other_review_or_error":len(unknown_failures),
              "known_missing_months":sorted(r["month"] for r in known_unavailable)}
    (out/"monthly_archive_acquisition_summary.json").write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    # Mark content evidence after CP-0025 scans the verified raw ZIPs. Do not promote any source.
    env=os.environ.copy(); env["AISTS_DATA_ROOT"]=str(data_root)
    env["PYTHONUNBUFFERED"]="1"
    stages=[]
    cp25=SCRIPTS/"AISTS_CP0025_Expanded_Daily_Reference_Validation.py"
    cp26=SCRIPTS/"AISTS_CP0026_Research_Candidate_Builder.py"
    cp27=SCRIPTS/"AISTS_CP0027_MultiTimeframe_Baseline_Backtest.py"

    try:
        s25=run_stage(cp25,env,logs,timeout=6600); stages.append(s25)
        if s25["exit_code"]==0:
            # Reconcile raw-source content rows with acquisition-manifest hashes.
            dates_file=reports/"cp0025_reference_dates.json"
            if dates_file.exists():
                flagged=json.loads(dates_file.read_text(encoding="utf-8")).get("dates",[])
                (out/"cp0025_flagged_dates_summary.json").write_text(json.dumps({"count":len(flagged),"dates":flagged},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            s26=run_stage(cp26,env,logs,timeout=6600); stages.append(s26)
            if s26["exit_code"]==0:
                s27=run_stage(cp27,env,logs,timeout=6600); stages.append(s27)
    except subprocess.TimeoutExpired as exc:
        stages.append({"stage":"SUBPROCESS_TIMEOUT","exit_code":124,"elapsed_seconds":None,
                       "stderr_tail":f"Stage exceeded timeout: {exc}"})

    # Add post-CP0025 content-level flags to the monthly acquisition manifest.
    if reports.joinpath("cp0025_flagged_monthly_rows.csv").exists():
        try:
            flagged_rows=list(csv.DictReader(reports.joinpath("cp0025_flagged_monthly_rows.csv").open(newline="",encoding="utf-8")))
            by_interval={}
            for row in flagged_rows: by_interval[row.get("interval","")]=by_interval.get(row.get("interval",""),0)+1
            (out/"monthly_content_flag_counts.json").write_text(json.dumps({"flagged_rows_by_interval":by_interval,"flagged_source_rows":len(flagged_rows)},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        except Exception as exc:
            (out/"monthly_content_flag_counts.json").write_text(json.dumps({"status":"READ_ERROR","error":repr(exc)},indent=2)+"\n",encoding="utf-8")

    # Collect key metrics while keeping raw archives and full candidate files out of artifacts.
    cp25_summary={}
    p=reports/"cp0025_reconciliation_summary.json"
    if p.exists():
        try: cp25_summary=json.loads(p.read_text(encoding="utf-8"))
        except Exception: pass
    cp26_summary={}
    p=reports/"cp0026_research_candidate_manifest.json"
    if p.exists():
        try: cp26_summary=json.loads(p.read_text(encoding="utf-8"))
        except Exception: pass
    cp27_summary={}
    p=reports/"cp0027_backtest_summary.json"
    if p.exists():
        try: cp27_summary=json.loads(p.read_text(encoding="utf-8"))
        except Exception: pass
    cp27_results=[]
    p=data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"baseline_results.csv"
    if p.exists():
        try:
            with p.open(newline="",encoding="utf-8") as f: cp27_results=list(csv.DictReader(f))
        except Exception: pass
    selected=[]
    for row in cp27_results:
        if row.get("strategy") in ("EMA_12_26","RSI14_30_55","DONCHIAN20_10","BUY_AND_HOLD","CASH") and row.get("period") in ("TRAIN","VALIDATION","OOS"):
            selected.append({k:row.get(k) for k in ("interval","period","strategy","total_return_pct","max_drawdown_pct","cagr_pct","closed_trades","fees_paid","estimated_slippage_cost","status") if k in row})
    write_csv(out/"cp0027_key_metrics.csv",selected)

    bundle=out/"AISTS_CP0025_CP0026_CP0027_Legacy_Pipeline_Evidence.zip"
    bundle_inventory=[]
    include=[
        (reports/"official_checksum_verification.csv","source/official_checksum_verification.csv"),
        (out/"monthly_archive_acquisition_manifest.csv","source/monthly_archive_acquisition_manifest.csv"),
        (out/"monthly_archive_acquisition_summary.json","source/monthly_archive_acquisition_summary.json"),
        (out/"monthly_content_flag_counts.json","source/monthly_content_flag_counts.json"),
        (reports/"cp0025_reference_dates.json","cp0025/cp0025_reference_dates.json"),
        (reports/"cp0025_flagged_monthly_rows.csv","cp0025/cp0025_flagged_monthly_rows.csv"),
        (reports/"cp0025_daily_reference_manifest.csv","cp0025/cp0025_daily_reference_manifest.csv"),
        (reports/"cp0025_daily_reference_manifest.json","cp0025/cp0025_daily_reference_manifest.json"),
        (reports/"cp0025_daily_reference_summary.json","cp0025/cp0025_daily_reference_summary.json"),
        (reports/"cp0025_value_mismatches.csv","cp0025/cp0025_value_mismatches.csv"),
        (reports/"cp0025_daily_monthly_row_disposition.csv","cp0025/cp0025_daily_monthly_row_disposition.csv"),
        (reports/"cp0025_reference_read_errors.csv","cp0025/cp0025_reference_read_errors.csv"),
        (reports/"cp0025_reconciliation_summary.json","cp0025/cp0025_reconciliation_summary.json"),
        (reports/"cp0026_research_candidate_manifest.json","cp0026/cp0026_research_candidate_manifest.json"),
        (reports/"cp0026_day_source_disposition.csv","cp0026/cp0026_day_source_disposition.csv"),
        (reports/"cp0026_candidate_quality_issues.csv","cp0026/cp0026_candidate_quality_issues.csv"),
        (reports/"cp0027_backtest_summary.json","cp0027/cp0027_backtest_summary.json"),
        (data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"baseline_results.csv","cp0027/baseline_results.csv"),
        (data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"data_quality.csv","cp0027/data_quality.csv"),
        (data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"oos_slippage_sensitivity.csv","cp0027/oos_slippage_sensitivity.csv"),
        (data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"assumptions.json","cp0027/assumptions.json"),
        (data_root/"derived"/"research_candidate_v1"/"BTCUSDT"/"backtest_cp0027"/"oos_trades_5bps.csv.gz","cp0027/oos_trades_5bps.csv.gz"),
    ]
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for src,arc in include: copy_if_exists(src,z,arc,bundle_inventory)
        for src in sorted(logs.glob("*.log")): copy_if_exists(src,z,"logs/"+src.name,bundle_inventory)
        copy_if_exists(out/"cp0027_key_metrics.csv",z,"cp0027/cp0027_key_metrics.csv",bundle_inventory)
    with zipfile.ZipFile(bundle,"r") as z:
        bad=z.testzip()
        zip_crc="PASS" if bad is None else "FAIL"
        members=z.namelist()
    bundle_sha=sha256_file(bundle)

    end=datetime.now(timezone.utc)
    monthly_summary={
        "expected_archives":len(tasks),
        "checksum_and_zip_inventory_pass":sum(r.get("status")=="MATCH" for r in records),
        "known_unavailable_1mo_404":len(known_unavailable),
        "other_source_review_or_error":len(unknown_failures),
        "cache_hits":sum(bool(r.get("cache_used")) for r in records),
        "bytes_reused_or_downloaded":sum(int(r.get("zip_bytes",0) or 0) for r in records),
    }
    status=("PIPELINE_COMPLETED" if len(stages)>=3 and all(s.get("exit_code")==0 for s in stages)
            else "PIPELINE_PARTIAL_OR_BLOCKED")
    summary={
        "checkpoint":"AISTS-GH-LEGACY-001",
        "status":status,
        "started_at_utc":started.isoformat(),"finished_at_utc":end.isoformat(),
        "elapsed_seconds":round((end-started).total_seconds(),2),
        "requested_task":"CP-0025 -> CP-0026 -> CP-0027 original pipeline",
        "source_policy":"Only official downloadable Spot monthly ZIPs and sibling .CHECKSUM objects; original CP-0025 adds official daily ZIP+CHECKSUM references for flagged dates. No Binance REST market-data endpoints.",
        "monthly_source_acquisition":monthly_summary,
        "cp0025_reconciliation_summary":cp25_summary,
        "cp0026_candidate_gate":cp26_summary.get("gate"),
        "cp0026_interval_results":cp26_summary.get("results"),
        "cp0027_execution_status":cp27_summary.get("execution_status"),
        "cp0027_initial_capital_assumption_usdt":cp27_summary.get("initial_equity_usdt"),
        "capital_caveat":"Vendored CP-0027 script is preserved unchanged and reports 10,000 USDT initial equity. This does not represent the user's ₹10,000 INR planning baseline; use percentage metrics for this legacy replay and separately recalibrate amount-based outputs.",
        "cp0027_key_metrics":selected,
        "stages":[{"stage":s.get("stage"),"exit_code":s.get("exit_code"),"elapsed_seconds":s.get("elapsed_seconds")} for s in stages],
        "monthly_missing_expected_1mo_files":sorted(r.get("month") for r in known_unavailable),
        "all_strategy_and_trading_gates":"NO_PROMOTION; RESEARCH_ONLY",
        "exchange_rest_api_used":False,"exchange_credentials_used":False,"live_orders_or_signing":False,
        "raw_source_archives_modified":False,"raw_source_corrections_applied":False,
        "canonical_sources_selected":False,"source_cases_closed":0,"strategy_promoted":False,
        "candidate_files_in_evidence_bundle":False,
        "evidence_bundle":{"path":str(bundle),"bytes":bundle.stat().st_size,"sha256":bundle_sha,"zip_crc":zip_crc,"members":len(members),"payload_files":len(bundle_inventory)},
        "self_tests":tests,
    }
    (out/"legacy_pipeline_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    (out/"evidence_file_hash_manifest.json").write_text(json.dumps(bundle_inventory,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True))
    return 0 if status=="PIPELINE_COMPLETED" else 1


if __name__=="__main__":
    raise SystemExit(main())
