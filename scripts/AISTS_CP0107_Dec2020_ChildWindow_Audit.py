#!/usr/bin/env python3
"""Cache-only exact 5m child-key audit for nine December 2020 roll-up review cases."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,shutil,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

DAY="2020-12-21"
START=1608553800000
END=1608562800000
STEP=300000
TARGETS=[
 ("MONTHLY","5m","2020-12","BTCUSDT-5m-2020-12.zip"),
 ("DAILY","5m","2020-12-21","BTCUSDT-5m-2020-12-21.zip")
]
def log(message): print("[CP-0107-DEC-CHILD] "+message,flush=True)
def sha_file(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def utc_day(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def utc_iso(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def read_csv(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_csv(path,rows,fields=None):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if fields is None: fields=list(rows[0].keys()) if rows else ["status"]
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
  w.writeheader();w.writerows(rows)
def verify_sidecar(path,filename,zipsha,manifestsha):
 actual=sha_file(path)
 if actual!=manifestsha: raise ValueError(filename+" sidecar SHA mismatch against frozen manifest")
 txt=path.read_text(encoding="utf-8",errors="replace").strip()
 tokens=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",txt)))
 if len(tokens)!=1 or filename not in txt or tokens[0]!=zipsha: raise ValueError(filename+" sidecar content does not match ZIP")
 return actual
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--monthly-cache",required=True)
 ap.add_argument("--daily-cache",required=True)
 ap.add_argument("--manifest",required=True)
 ap.add_argument("--rollup-csv",required=True)
 ap.add_argument("--source-dir",required=True)
 ap.add_argument("--output-dir",required=True)
 a=ap.parse_args()
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 source_dir=Path(a.source_dir)
 base_names=("CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv",
  "CP0107_Feb2018_DailyCoverage_RawRows.csv","CP0107_Feb2018_SegmentCoverage.csv",
  "CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md","CP0107_Feb2018_Checks.csv")
 for name in base_names:
  source_file=source_dir/name
  if not source_file.is_file(): raise FileNotFoundError("verified CP-0107 base evidence absent: "+str(source_file))
  shutil.copy2(source_file,out/name)
 base=json.loads((out/"CP0107_Feb2018_Extraction_Summary.json").read_text(encoding="utf-8"))
 if base.get("status")!="PASS_CACHE_ONLY_EXTRACTION" or base.get("scope",{}).get("off_grid_rows_extracted")!=450:
  raise ValueError("base February evidence failed its saved status/count gate")
 manifest=read_csv(a.manifest)
 midx={(x["source"],x["interval"],x["period"]):x for x in manifest}
 rollups=[x for x in read_csv(a.rollup_csv) if x.get("status")=="REVIEW_REQUIRED"]
 if len(rollups)!=9: raise ValueError("expected 9 roll-up review rows, got "+str(len(rollups)))
 archives=[]; rows_by_source={}; keys_by_source={}; row_by_key={}
 raw_fields=("open_time","open","high","low","close","volume","close_time","quote_asset_volume",
             "number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore")
 for src,iv,period,filename in TARGETS:
  mr=midx[(src,iv,period)]
  root=Path(a.monthly_cache)/"5m"/"2020-12" if src=="MONTHLY" else Path(a.daily_cache)/"5m"
  path=root/filename
  if not path.is_file(): raise FileNotFoundError("existing cache ZIP absent; network disabled: "+str(path))
  actual=sha_file(path)
  if actual!=mr["zip_sha256"] or actual!=mr["official_sha256"]: raise ValueError(filename+" SHA-256 mismatch with official frozen-manifest value")
  records=[]
  with zipfile.ZipFile(path,"r") as z:
   bad=z.testzip()
   if bad: raise ValueError(filename+" ZIP CRC failure at "+bad)
   members=[m.filename for m in z.infolist() if not m.is_dir()]
   csvs=[m for m in members if m.lower().endswith(".csv")]
   if len(members)!=1 or len(csvs)!=1: raise ValueError(filename+" unexpected archive member set")
   member=csvs[0]
   with z.open(member,"r") as raw:
    rd=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
    for line,row in enumerate(rd,1):
     if not row: continue
     if len(row)<12: raise ValueError(filename+" CSV line has fewer than 12 columns")
     op=int(row[0]);cl=int(row[6])
     if utc_day(op)!=DAY or not (START<=op<END): continue
     rec={"source":src,"interval":"5m","open_time_ms":op,"open_time_utc":utc_iso(op),
      "csv_line_number":line,"archive_filename":filename,"archive_sha256":actual,"inner_csv_member":member,
      "close_time_ms":cl,"close_time_utc":utc_iso(cl),"grid_remainder_ms":op%STEP}
     for idx,fname in enumerate(raw_fields): rec["raw_"+fname]=str(row[idx])
     records.append(rec)
  side_actual="";sidepath="";side_status="RECORDED_PARENT_MANIFEST_REFERENCE_ONLY"
  if src=="DAILY":
   side=Path(a.daily_cache)/"5m"/(filename+".CHECKSUM")
   if not side.is_file(): raise FileNotFoundError("cached official daily checksum absent; network disabled: "+str(side))
   side_actual=verify_sidecar(side,filename,actual,mr["checksum_sidecar_sha256"])
   sidepath=str(side);side_status="LOCAL_SIDECAR_AND_ZIP_MATCH_PASS"
  archives.append({"source":src,"interval":"5m","period":period,"filename":filename,
    "archive_path":str(path),"zip_sha256":actual,"official_sha256_recorded":mr["official_sha256"],
    "checksum_sidecar_sha256_recorded":mr["checksum_sidecar_sha256"],
    "checksum_sidecar_sha256_recomputed":side_actual,"checksum_sidecar_path":sidepath,
    "checksum_status":side_status,"inner_csv_member":member,"zip_crc":"PASS","archive_status":"PASS",
    "window_rows":len(records)})
  rows_by_source[src]=records
  bykey={}
  for rec in records:
   if rec["open_time_ms"] in bykey: raise ValueError("duplicate exact open key in "+filename)
   bykey[rec["open_time_ms"]]=rec
  row_by_key[src]=bykey;keys_by_source[src]=set(bykey)
  log("VERIFIED "+src+" "+filename+" SHA256="+actual[:16]+" CRC=PASS rows_in_window="+str(len(records))+" checksum="+side_status)
 raw_output=[x for src in ("MONTHLY","DAILY") for x in rows_by_source[src]]
 raw_columns=["source","interval","open_time_ms","open_time_utc","csv_line_number","archive_filename",
  "archive_sha256","inner_csv_member","close_time_ms","close_time_utc","grid_remainder_ms"]+["raw_"+x for x in raw_fields]
 write_csv(out/"CP0107_Dec2020_5m_ActualRows_Window.csv",raw_output,raw_columns)
 coverage=[]
 for src in ("MONTHLY","DAILY"):
  rows=rows_by_source[src];bykey=row_by_key[src]
  for expected in range(START,END,STEP):
   actual=bykey.get(expected)
   nearest=min(rows,key=lambda x:abs(x["open_time_ms"]-expected)) if rows else None
   coverage.append({"source":src,"expected_open_time_ms":expected,"expected_open_time_utc":utc_iso(expected),
    "exact_key_present":str(actual is not None),"actual_archive_open_time_utc":actual["open_time_utc"] if actual else "",
    "actual_archive_csv_line":actual["csv_line_number"] if actual else "",
    "nearest_open_time_diagnostic_only":nearest["open_time_utc"] if nearest else "",
    "nearest_delta_ms_diagnostic_only":nearest["open_time_ms"]-expected if nearest else "",
    "nearest_is_counterpart":"False","archive_filename":next(x["filename"] for x in archives if x["source"]==src),
    "archive_sha256":next(x["zip_sha256"] for x in archives if x["source"]==src),
    "classification":"EXACT_CHILD_KEY_PRESENT" if actual else "EXACT_CHILD_KEY_ABSENT_IN_VERIFIED_ARCHIVE"})
 write_csv(out/"CP0107_Dec2020_5m_ChildCoverage.csv",coverage)
 roll_cov=[]
 for r in rollups:
  src=r["source"];iv=r["parent_interval"]
  start=int(datetime.fromisoformat(r["parent_open_time_utc"].replace("Z","+00:00")).timestamp()*1000)
  duration={"15m":900000,"30m":1800000,"1h":3600000}[iv]
  expected=list(range(start,start+duration,STEP))
  keys=keys_by_source[src]
  present=[t for t in expected if t in keys]
  missing=[t for t in expected if t not in keys]
  old_missing=json.loads(r["missing_child_open_times_utc"])
  old_as_ms=[int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000) for s in old_missing]
  now_found=[t for t in old_as_ms if t in keys]
  still_missing=[t for t in old_as_ms if t not in keys]
  new_missing=[t for t in missing if t not in old_as_ms]
  rec={"source":src,"parent_interval":iv,"parent_open_time_utc":utc_iso(start),
   "expected_child_5m_bars":len(expected),"available_exact_child_5m_bars":len(present),
   "all_missing_child_open_times_utc":json.dumps([utc_iso(t) for t in missing]),
   "previous_window_missing_child_keys":json.dumps([utc_iso(t) for t in old_as_ms]),
   "previously_flagged_keys_now_present_in_full_archive":json.dumps([utc_iso(t) for t in now_found]),
   "previously_flagged_keys_still_absent":json.dumps([utc_iso(t) for t in still_missing]),
   "additional_missing_keys_found_by_full_archive_scan":json.dumps([utc_iso(t) for t in new_missing]),
   "previous_parent_row_present":r["parent_row_present"],
   "source_5m_archive_filename":next(x["filename"] for x in archives if x["source"]==src),
   "source_5m_archive_sha256":next(x["zip_sha256"] for x in archives if x["source"]==src),
   "rollup_child_audit_status":"CHILD_SET_COMPLETE_NEEDS_PARENT_COMPARISON" if not missing else "CHILD_KEYS_MISSING_IN_VERIFIED_ARCHIVE",
   "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE","aggregate_created":"False"}
  roll_cov.append(rec)
 write_csv(out/"CP0107_Dec2020_ReviewRollup_ChildCoverage.csv",roll_cov)
 write_csv(out/"CP0107_Dec2020_5m_SourceVerification.csv",archives)
 statuses=Counter(x["rollup_child_audit_status"] for x in roll_cov)
 checks=[
  {"check":"two_archives_match_official_sha_and_crc","status":"PASS" if len(archives)==2 and all(x["archive_status"]=="PASS" for x in archives) else "FAIL","detail":"Verified full cached monthly/daily 5m ZIP bytes."},
  {"check":"daily_sidecar_rehashed_and_content_matched","status":"PASS" if next(x for x in archives if x["source"]=="DAILY")["checksum_status"]=="LOCAL_SIDECAR_AND_ZIP_MATCH_PASS" else "FAIL","detail":"Daily .CHECKSUM re-hash and content comparison."},
  {"check":"exact_grid_coverage_rows","status":"PASS" if len(coverage)==60 else "FAIL","detail":str(len(coverage))},
  {"check":"nine_rollups_rechecked_against_full_archives","status":"PASS" if len(roll_cov)==9 else "FAIL","detail":str(len(roll_cov))},
  {"check":"no_synthetic_rows_or_aggregates","status":"PASS","detail":"Only original 5m source rows and expected-key coverage are emitted."}
 ]
 if any(x["status"]!="PASS" for x in checks): raise SystemExit("Focused December child audit validation failed: "+json.dumps(checks))
 outputs={}
 for name in ("CP0107_Dec2020_5m_ActualRows_Window.csv","CP0107_Dec2020_5m_ChildCoverage.csv",
              "CP0107_Dec2020_ReviewRollup_ChildCoverage.csv","CP0107_Dec2020_5m_SourceVerification.csv"):
  path=out/name;outputs[name]={"sha256":sha_file(path),"bytes":path.stat().st_size}
 summary={"checkpoint":"CP-0107","task":"cp0107_dec2020_child_window_audit",
  "status":"PASS_CACHE_ONLY_DEC2020_CHILD_AUDIT","generated_at_utc":datetime.now(timezone.utc).isoformat(),
  "source_archives_verified":2,"source_archive_sha256":{x["source"]:x["zip_sha256"] for x in archives},
  "source_rows_in_1230_to_1500_utc_window":{src:len(rows_by_source[src]) for src in rows_by_source},
  "expected_grid_keys_per_source":30,"expected_grid_keys_total":len(coverage),
  "exact_keys_present":{src:sum(1 for x in coverage if x["source"]==src and x["exact_key_present"]=="True") for src in ("MONTHLY","DAILY")},
  "exact_keys_absent":{src:sum(1 for x in coverage if x["source"]==src and x["exact_key_present"]=="False") for src in ("MONTHLY","DAILY")},
  "review_rollups_checked":9,"rollup_child_status_counts":dict(statuses),
  "rollup_child_coverage":[{"source":x["source"],"interval":x["parent_interval"],"parent_open_time_utc":x["parent_open_time_utc"],
    "expected":x["expected_child_5m_bars"],"available":x["available_exact_child_5m_bars"],
    "missing":json.loads(x["all_missing_child_open_times_utc"]),"status":x["rollup_child_audit_status"],
    "previously_flagged_keys_now_present":json.loads(x["previously_flagged_keys_now_present_in_full_archive"]),
    "previously_flagged_keys_still_absent":json.loads(x["previously_flagged_keys_still_absent"])} for x in roll_cov],
  "checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),"checks":checks,"outputs":outputs,
  "external_network_used":False,"market_data_rest_api_used":False,"raw_archives_modified":False,
  "timestamp_shift_or_rounding":False,"synthetic_candles_created":False,"aggregate_candles_created":False,
  "source_cases_closed":0,"canonical_source_selected":False,"root_cause":"OPEN_NOT_ESTABLISHED",
  "backtest_rerun":False,"strategy_promoted":False,
  "gates":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"}}
 (out/"CP0107_Dec2020_ChildWindow_Audit_Summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 report=["# CP-0107: December 2020 full-cache 5m child-key audit","",
  "Status: "+summary["status"]+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+" PASS.",
  "Two cached official 5m ZIPs were checked against CP-0106 official SHA-256 references and ZIP CRC. The daily .CHECKSUM bytes were also re-hashed and content-matched.",
  "Window: 2020-12-21 12:30 through 14:55 UTC inclusive; 30 expected exact keys per source.",
  "The nine missing-child roll-up cases were re-evaluated against the full cached monthly/daily source ZIP, not only the earlier 59-row contextual extract.",
  "Absence means the exact open-time key was not found in verified archive bytes; it does not explain why or establish which source is canonical.",
  "No download, source repair, timestamp shift, synthetic candle/aggregate, backtest or strategy promotion."]
 (out/"CP0107_Dec2020_ChildWindow_Audit_Report_HI.md").write_text("\n".join(report)+"\n",encoding="utf-8")
 log(json.dumps({"status":summary["status"],"checks":str(summary["checks_passed"])+"/"+str(summary["checks_total"]),
  "window_rows":summary["source_rows_in_1230_to_1500_utc_window"],"exact_keys_present":summary["exact_keys_present"],
  "exact_keys_absent":summary["exact_keys_absent"],"rollup_statuses":dict(statuses)},ensure_ascii=False))
 return 0
if __name__=="__main__": raise SystemExit(main())
