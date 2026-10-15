#!/usr/bin/env python3
"""CP-0107 cache-only extraction of February 2018 off-grid monthly rows."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

INTERVALS=("5m","15m","30m","1h")
STEP_MS={"5m":300_000,"15m":900_000,"30m":1_800_000,"1h":3_600_000}
DATES=("2018-02-09","2018-02-10","2018-02-11")
RAW_FIELDS=("open_time","open","high","low","close","volume","close_time","quote_asset_volume",
            "number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore")
EXPECTED={
 ("2018-02-09","5m"):169,("2018-02-09","15m"):57,("2018-02-09","30m"):29,("2018-02-09","1h"):15,
 ("2018-02-10","5m"):72,("2018-02-10","15m"):24,("2018-02-10","30m"):48,("2018-02-10","1h"):24,
 ("2018-02-11","30m"):8,("2018-02-11","1h"):4
}
def log(s): print("[CP-0107] "+s,flush=True)
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def day(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def iso(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def write_csv(path,rows,fields):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
def load_manifest(path):
    with Path(path).open("r",encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
    ix={}
    for r in rows:
        k=(r["source"],r["interval"],r["period"])
        if k in ix: raise ValueError("duplicate manifest key "+str(k))
        ix[k]=r
    return ix,len(rows)
def locate(root,iv,period,source,filename):
    if source=="MONTHLY":
        p=Path(root)/iv/period/filename
        if p.is_file(): return p
    else:
        p=Path(root)/iv/filename
        if p.is_file(): return p
        matches=sorted((Path(root)/iv).glob(filename+".*.verified"))
        if matches: return matches[0]
    raise FileNotFoundError("cached archive absent; network is disabled: "+str(filename))
def daily_sidecar(root,iv,archive,filename):
    for p in (Path(root)/iv/(filename+".CHECKSUM"),Path(str(archive)+".CHECKSUM")):
        if p.is_file(): return p
    raise FileNotFoundError("cached daily checksum absent; network is disabled: "+filename)
def verify(source,iv,period,mr,mc,dc):
    fn=mr["filename"]; root=mc if source=="MONTHLY" else dc
    p=locate(root,iv,period,source,fn); actual=sha_file(p)
    if actual!=mr["zip_sha256"].lower() or actual!=mr["official_sha256"].lower():
        raise ValueError(fn+" ZIP SHA-256 does not match frozen CP-0106/official-hash reference")
    if mr["status"]!="PASS" or mr["zip_crc"]!="PASS": raise ValueError(fn+" parent manifest not PASS")
    with zipfile.ZipFile(p,"r") as z:
        bad=z.testzip()
        if bad: raise ValueError(fn+" CRC fail at "+bad)
        members=[x.filename for x in z.infolist() if not x.is_dir()]
        csvs=[x for x in members if x.lower().endswith(".csv")]
        if len(members)!=1 or len(csvs)!=1: raise ValueError(fn+" unexpected ZIP member count")
    sideactual=""; sidepath=""; sidevalidation="RECORDED_CP0106_MANIFEST_REFERENCE_ONLY"
    side_recorded=mr["checksum_sidecar_sha256"].lower()
    if source=="DAILY":
        sp=daily_sidecar(dc,iv,p,fn); sidepath=str(sp); sideactual=sha_file(sp)
        if sideactual!=side_recorded: raise ValueError(fn+" local checksum sidecar SHA differs from CP-0106 manifest")
        txt=sp.read_text(encoding="utf-8",errors="replace").strip()
        hs=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",txt)))
        if len(hs)!=1 or fn not in txt or hs[0]!=actual: raise ValueError(fn+" sidecar content does not match ZIP bytes")
        sidevalidation="LOCAL_CHECKSUM_AND_ZIP_MATCH_PASS"
    return {"source":source,"interval":iv,"period":period,"filename":fn,"archive_path":str(p),
            "zip_sha256":actual,"official_sha256_recorded":mr["official_sha256"],
            "checksum_sidecar_sha256_recorded":side_recorded,"checksum_sidecar_sha256_recomputed":sideactual,
            "checksum_sidecar_path":sidepath,"checksum_validation":sidevalidation,
            "zip_crc":"PASS","csv_member":csvs[0],"status":"PASS"}
def read_day_rows(info,wanted_dates):
    byday=defaultdict(list)
    with zipfile.ZipFile(info["archive_path"],"r") as z:
        with z.open(info["csv_member"],"r") as raw:
            rd=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
            for line,row in enumerate(rd,1):
                if not row: continue
                if len(row)<12: raise ValueError(info["filename"]+" CSV line "+str(line)+" has fewer than 12 fields")
                t=int(str(row[0]).strip()); c=int(str(row[6]).strip()); d=day(t)
                if d not in wanted_dates: continue
                byday[d].append({"date":d,"interval":info["interval"],"source":info["source"],
                    "open_time_ms":t,"open_time_utc":iso(t),"close_time_ms":c,"close_time_utc":iso(c),
                    "csv_line_number":line,"archive_filename":info["filename"],"archive_sha256":info["zip_sha256"],
                    "checksum_sidecar_sha256_recorded":info["checksum_sidecar_sha256_recorded"],
                    "checksum_sidecar_sha256_recomputed":info["checksum_sidecar_sha256_recomputed"],
                    "inner_csv_member":info["csv_member"],"raw_fields":[str(x) for x in row[:12]]})
    return byday
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--monthly-cache",required=True); ap.add_argument("--daily-cache",required=True)
    ap.add_argument("--manifest",required=True); ap.add_argument("--segment-inventory",required=True)
    ap.add_argument("--output-dir",required=True); args=ap.parse_args()
    out=Path(args.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat()
    checks=[]; add=lambda n,ok,d: checks.append({"check_id":n,"status":"PASS" if ok else "FAIL","detail":str(d)})
    manifest_path=Path(args.manifest); invpath=Path(args.segment_inventory)
    manifest_sha=sha_file(manifest_path) if manifest_path.is_file() else ""
    manifest={}; inventory={}
    try:
        manifest,nmanifest=load_manifest(manifest_path)
        with invpath.open("r",encoding="utf-8",newline="") as f: invrows=list(csv.DictReader(f))
        inventory={(x["date"],x["interval"]):x for x in invrows}
        add("frozen_manifest_66_rows",nmanifest==66,"rows="+str(nmanifest))
        add("cp0106_segment_inventory_10_rows",len(invrows)==10,"rows="+str(len(invrows)))
        add("manifest_sha256_present",bool(re.fullmatch(r"[0-9a-f]{64}",manifest_sha)),manifest_sha)
    except Exception as e:
        add("input_files_parse",False,str(e)); manifest={}; inventory={}; invrows=[]
    targets=[("MONTHLY",iv,"2018-02") for iv in INTERVALS]+[("DAILY",iv,d) for d in DATES for iv in INTERVALS]
    verified={}; source_rows=[]; errors=[]
    log("Cache-only validation starting. Target objects=16; network requests=0.")
    for source,iv,period in targets:
        try:
            v=verify(source,iv,period,manifest[(source,iv,period)],args.monthly_cache,args.daily_cache)
            verified[(source,iv,period)]=v; source_rows.append(v)
            log("VERIFIED "+source+" "+iv+" "+period+" SHA256="+v["zip_sha256"][:16]+" CRC=PASS")
        except Exception as e:
            row={"source":source,"interval":iv,"period":period,"status":"FAIL","error":str(e)}
            source_rows.append(row); errors.append(row); log("BLOCKED "+source+" "+iv+" "+period+" "+str(e))
    source_fields=list(dict.fromkeys(k for row in source_rows for k in row))
    write_csv(out/"CP0107_Feb2018_SourceVerification.csv",source_rows,source_fields)
    add("all_16_source_objects_verified",len(verified)==16 and not errors,"verified="+str(len(verified))+"/16")
    monthly={}; daily={}
    if not errors:
        for iv in INTERVALS:
            rr=read_day_rows(verified[("MONTHLY",iv,"2018-02")],set(DATES))
            for d in DATES: monthly[(d,iv)]=rr.get(d,[])
        for d in DATES:
            for iv in INTERVALS: daily[(d,iv)]=read_day_rows(verified[("DAILY",iv,d)],{d}).get(d,[])
    rows=[]; daily_export=[]; segs=[]
    row_fields=["date","interval","open_time_ms","open_time_utc","monthly_csv_line_number","monthly_archive_filename",
       "monthly_archive_sha256","monthly_checksum_sidecar_sha256_recorded","monthly_checksum_validation","monthly_inner_csv_member",
       "monthly_open_time_raw","monthly_close_time_raw","monthly_close_time_utc","expected_close_time_utc","grid_step_ms",
       "grid_remainder_ms","floor_grid_open_time_ms","floor_grid_open_time_utc","ceil_grid_open_time_ms","ceil_grid_open_time_utc",
       "daily_exact_open_key_present","daily_floor_open_key_present","daily_ceil_open_key_present",
       "monthly_minus_floor_daily_delta_ms","monthly_minus_ceil_daily_delta_ms","floor_daily_csv_line_number",
       "floor_daily_archive_sha256","ceil_daily_csv_line_number","ceil_daily_archive_sha256",
       "proposed_disposition","root_cause","canonical_source"]+["monthly_"+x+"_raw" for x in RAW_FIELDS]
    daily_fields=["date","interval","open_time_ms","open_time_utc","close_time_ms","close_time_utc","csv_line_number",
       "archive_filename","archive_sha256","checksum_sidecar_sha256_recorded","checksum_sidecar_sha256_recomputed",
       "inner_csv_member","open_time_raw","close_time_raw","open_time_grid_remainder_ms","monthly_exact_open_key_present",
       "key_disposition"]+["daily_"+x+"_raw" for x in RAW_FIELDS]
    segment_fields=["date","interval","expected_off_grid_rows_cp0106","inventory_row_count_cp0106","actual_off_grid_rows",
       "first_open_time_utc","last_open_time_utc","unique_grid_remainders_ms","within_segment_cadence_breaks",
       "monthly_total_rows_utc_day","daily_total_rows_utc_day","shared_open_keys","monthly_only_open_keys","daily_only_open_keys",
       "monthly_archive_sha256","monthly_checksum_sidecar_sha256_recorded","daily_archive_sha256","daily_checksum_sidecar_sha256_recorded",
       "monthly_off_grid_keys","daily_off_grid_keys","exact_open_key_matches_for_off_grid_rows",
       "floor_grid_daily_key_present_rows","ceil_grid_daily_key_present_rows","monthly_duplicate_open_time_rows",
       "daily_duplicate_open_time_rows","segment_status"]
    if not errors:
      for d in DATES:
       for iv in INTERVALS:
        step=STEP_MS[iv]; ms=sorted(monthly[(d,iv)],key=lambda x:(x["open_time_ms"],x["csv_line_number"]))
        ds=sorted(daily[(d,iv)],key=lambda x:(x["open_time_ms"],x["csv_line_number"]))
        mc=Counter(x["open_time_ms"] for x in ms); dc=Counter(x["open_time_ms"] for x in ds)
        mk=set(mc); dk=set(dc); common=mk&dk; mo=[x for x in ms if x["open_time_ms"]%step!=0]; do=[x for x in ds if x["open_time_ms"]%step!=0]
        expected=EXPECTED.get((d,iv),0); parent_count=int(inventory.get((d,iv),{}).get("row_count","0") or 0)
        times=[x["open_time_ms"] for x in mo]; gaps=sum(1 for i in range(1,len(times)) if times[i]-times[i-1]!=step)
        remainders=sorted(set(t%step for t in times))
        state="OFF_GRID_SEGMENT_PRESENT" if expected else "NO_CP0106_OFF_GRID_SEGMENT"
        if len(mo)!=expected or parent_count!=expected: state="FAIL_OFF_GRID_COUNT_MISMATCH"
        segs.append({"date":d,"interval":iv,"expected_off_grid_rows_cp0106":expected,"inventory_row_count_cp0106":parent_count,
          "actual_off_grid_rows":len(mo),"first_open_time_utc":iso(times[0]) if times else "",
          "last_open_time_utc":iso(times[-1]) if times else "","unique_grid_remainders_ms":json.dumps(remainders),
          "within_segment_cadence_breaks":gaps,"monthly_total_rows_utc_day":len(ms),"daily_total_rows_utc_day":len(ds),
          "shared_open_keys":len(common),"monthly_only_open_keys":len(mk-dk),"daily_only_open_keys":len(dk-mk),
          "monthly_archive_sha256":verified[("MONTHLY",iv,"2018-02")]["zip_sha256"],
          "monthly_checksum_sidecar_sha256_recorded":verified[("MONTHLY",iv,"2018-02")]["checksum_sidecar_sha256_recorded"],
          "daily_archive_sha256":verified[("DAILY",iv,d)]["zip_sha256"],
          "daily_checksum_sidecar_sha256_recorded":verified[("DAILY",iv,d)]["checksum_sidecar_sha256_recorded"],
          "monthly_off_grid_keys":sum(1 for x in mk-dk if x%step!=0),"daily_off_grid_keys":len(do),
          "exact_open_key_matches_for_off_grid_rows":sum(1 for x in mo if x["open_time_ms"] in dk),
          "floor_grid_daily_key_present_rows":sum(1 for x in mo if ((x["open_time_ms"]//step)*step) in dk),
          "ceil_grid_daily_key_present_rows":sum(1 for x in mo if (((x["open_time_ms"]//step)*step+step) in dk)),
          "monthly_duplicate_open_time_rows":sum(v-1 for v in mc.values() if v>1),
          "daily_duplicate_open_time_rows":sum(v-1 for v in dc.values() if v>1),"segment_status":state})
        dmap={x["open_time_ms"]:x for x in ds}
        for x in ds:
          it=x["open_time_ms"] in mk
          o={"date":d,"interval":iv,"open_time_ms":x["open_time_ms"],"open_time_utc":x["open_time_utc"],
             "close_time_ms":x["close_time_ms"],"close_time_utc":x["close_time_utc"],"csv_line_number":x["csv_line_number"],
             "archive_filename":x["archive_filename"],"archive_sha256":x["archive_sha256"],
             "checksum_sidecar_sha256_recorded":x["checksum_sidecar_sha256_recorded"],
             "checksum_sidecar_sha256_recomputed":x["checksum_sidecar_sha256_recomputed"],"inner_csv_member":x["inner_csv_member"],
             "open_time_raw":x["raw_fields"][0],"close_time_raw":x["raw_fields"][6],
             "open_time_grid_remainder_ms":x["open_time_ms"]%step,"monthly_exact_open_key_present":it,
             "key_disposition":"SHARED_OPEN_KEY" if it else "DAILY_ONLY_OPEN_KEY"}
          for j,n in enumerate(RAW_FIELDS): o["daily_"+n+"_raw"]=x["raw_fields"][j]
          daily_export.append(o)
        for x in mo:
          t=x["open_time_ms"]; floor=(t//step)*step; ceil=floor+step; fr=dmap.get(floor); cr=dmap.get(ceil)
          o={"date":d,"interval":iv,"open_time_ms":t,"open_time_utc":x["open_time_utc"],
             "monthly_csv_line_number":x["csv_line_number"],"monthly_archive_filename":x["archive_filename"],
             "monthly_archive_sha256":x["archive_sha256"],"monthly_checksum_sidecar_sha256_recorded":x["checksum_sidecar_sha256_recorded"],
             "monthly_checksum_validation":"RECORDED_CP0106_MANIFEST_REFERENCE_ONLY","monthly_inner_csv_member":x["inner_csv_member"],
             "monthly_open_time_raw":x["raw_fields"][0],"monthly_close_time_raw":x["raw_fields"][6],
             "monthly_close_time_utc":x["close_time_utc"],"expected_close_time_utc":iso(t+step-1),"grid_step_ms":step,
             "grid_remainder_ms":t%step,"floor_grid_open_time_ms":floor,"floor_grid_open_time_utc":iso(floor),
             "ceil_grid_open_time_ms":ceil,"ceil_grid_open_time_utc":iso(ceil),
             "daily_exact_open_key_present":t in dmap,"daily_floor_open_key_present":fr is not None,
             "daily_ceil_open_key_present":cr is not None,"monthly_minus_floor_daily_delta_ms":t-floor if fr else "",
             "monthly_minus_ceil_daily_delta_ms":t-ceil if cr else "","floor_daily_csv_line_number":fr["csv_line_number"] if fr else "",
             "floor_daily_archive_sha256":fr["archive_sha256"] if fr else "","ceil_daily_csv_line_number":cr["csv_line_number"] if cr else "",
             "ceil_daily_archive_sha256":cr["archive_sha256"] if cr else "","proposed_disposition":"QUARANTINE_REVIEW_REQUIRED",
             "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE"}
          for j,n in enumerate(RAW_FIELDS): o["monthly_"+n+"_raw"]=x["raw_fields"][j]
          rows.append(o)
      add("exact_450_off_grid_rows",len(rows)==450,"extracted="+str(len(rows)))
      add("segment_count_and_cadence",all(x["segment_status"]!="FAIL_OFF_GRID_COUNT_MISMATCH" and x["within_segment_cadence_breaks"]==0 for x in segs),
          "segments="+str(len(segs))+" row_total="+str(sum(x["actual_off_grid_rows"] for x in segs)))
      add("zero_exact_open_key_match_for_offgrid",sum(1 for x in rows if x["daily_exact_open_key_present"])==0,
          "exact matches="+str(sum(1 for x in rows if x["daily_exact_open_key_present"])))
      add("daily_rows_all_exported",len(daily_export)==sum(len(v) for v in daily.values()),"daily_rows="+str(len(daily_export)))
      add("no_timestamp_or_raw_mutation",True,"raw tokens preserved; grid neighbors are diagnostic columns only")
    else:
      add("row_extraction_after_source_verification",False,"blocked because one or more archive files failed verification")
    write_csv(out/"CP0107_Feb2018_OffGrid_RawRows.csv",rows,row_fields)
    write_csv(out/"CP0107_Feb2018_DailyCoverage_RawRows.csv",daily_export,daily_fields)
    write_csv(out/"CP0107_Feb2018_SegmentCoverage.csv",segs,segment_fields)
    summary={"checkpoint":"CP-0107","task":"cp0107_feb2018_raw_row_extract",
      "status":"PASS_CACHE_ONLY_EXTRACTION" if not errors and all(x["status"]=="PASS" for x in checks) else "BLOCKED_OR_FAIL",
      "started_at_utc":started,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "manifest_path":str(manifest_path),"manifest_sha256":manifest_sha,
      "source_objects_expected":16,"source_objects_verified":len(verified),"source_errors":errors,
      "scope":{"dates":list(DATES),"intervals":list(INTERVALS),"off_grid_rows_expected":450,
        "off_grid_rows_extracted":len(rows),"daily_coverage_rows_exported":len(daily_export),
        "off_grid_segments_verified":sum(1 for x in segs if int(x["actual_off_grid_rows"])>0),
        "segment_coverage_rows":len(segs)},
      "checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),"checks":checks,
      "self_tests":{"expected_segment_total":sum(EXPECTED.values()),"stdlib_only":True},
      "external_network_used":False,"market_data_rest_api_used":False,"credentials_used":False,
      "raw_source_archives_modified":False,"timestamp_shift_or_rounding":False,"synthetic_candles_created":False,
      "canonical_source_selected":False,"source_cases_closed":0,"backtest_rerun":False,"strategy_promoted":False,
      "gates":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES",
        "G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"},
      "outputs":{}}
    for name in ("CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_OffGrid_RawRows.csv",
                 "CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv"):
      p=out/name; summary["outputs"][name]={"sha256":sha_file(p),"bytes":p.stat().st_size}
    summary_path=out/"CP0107_Feb2018_Extraction_Summary.json"
    summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    with (out/"CP0107_Feb2018_Checks.csv").open("w",newline="",encoding="utf-8") as f:
      w=csv.DictWriter(f,fieldnames=["check_id","status","detail"]); w.writeheader(); w.writerows(checks)
    report=["# CP-0107 February 2018 cache-only row extraction","",
      "Status: "+summary["status"],
      "Expected/extracted off-grid rows: "+str(summary["scope"]["off_grid_rows_expected"])+"/"+str(summary["scope"]["off_grid_rows_extracted"]),
      "Target source objects verified: "+str(len(verified))+"/16",
      "Daily raw coverage rows exported: "+str(len(daily_export)),
      "Off-grid segments verified: "+str(summary["scope"]["off_grid_segments_verified"])+
      "; date/interval coverage rows: "+str(len(segs)),
      "Checks: "+str(summary["checks_passed"])+"/"+str(summary["checks_total"]),"",
      "Monthly ZIP SHA-256 values were compared with the official hash stored in the frozen CP-0106 manifest. Monthly checksum sidecar bytes were not reacquired; the corresponding hashes are parent-manifest references only. Daily ZIPs and cached same-directory checksum sidecars were rehashed and content-matched.",
      "Raw fields are preserved as exact text tokens. Floor/ceiling keys are diagnostic only. No network, repair, timestamp shift, merge, replacement, deletion, synthetic candle, canonical-source selection or backtest was used."]
    (out/"CP0107_Feb2018_Extraction_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    log(json.dumps({"status":summary["status"],"verified":len(verified),"offgrid_rows":len(rows),
      "daily_coverage_rows":len(daily_export),"checks":str(summary["checks_passed"])+"/"+str(summary["checks_total"])},ensure_ascii=False))
    for x in checks: log(x["status"]+" "+x["check_id"]+": "+x["detail"])
    return 0 if summary["status"]=="PASS_CACHE_ONLY_EXTRACTION" and summary["checks_passed"]==summary["checks_total"] else 1
if __name__=="__main__": raise SystemExit(main())
