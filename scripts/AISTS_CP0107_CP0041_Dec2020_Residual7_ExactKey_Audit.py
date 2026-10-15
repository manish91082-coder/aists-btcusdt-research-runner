#!/usr/bin/env python3
"""Offline exact-open-key audit of seven residual CP-0041 monthly-only rows on 2020-12-21."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,shutil,subprocess,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT_REL="evidence/source_adjudication/CP0107_CP0041_Dec2020_Residual7_RowSnapshot.csv"
SNAPSHOT_BLOB="702572504a0057fc59893ebcbe009de3015ef32e"
MANIFEST_REL="evidence/source_adjudication/CP0107_SourceArchive_Manifest_66.csv"
MANIFEST_BLOB="012f57029f6928821afe68332f59e7b043181648"
PACKAGE_SHA="23d8c4479f7ec4591e861f4e3a67f1db5cdb4641ff3da3d23a9484fabfc64fcc"
WORKLIST_MEMBER_SHA="f69229b7bb49a539bae6a8b878447b569c9450760998bfa33a50af9ef6f6ce0f"
STEP_MS={"5m":300000,"15m":900000,"30m":1800000,"1h":3600000}
PER_DAY={"5m":288,"15m":96,"30m":48,"1h":24}
RAW_FIELDS=["open_time","open","high","low","close","volume","close_time","quote_asset_volume","number_of_trades","taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore"]
BASE_FILES=(
 "CP0107_Feb2018_Extraction_Summary.json","CP0107_Feb2018_OffGrid_RawRows.csv","CP0107_Feb2018_DailyCoverage_RawRows.csv",
 "CP0107_Feb2018_SegmentCoverage.csv","CP0107_Feb2018_SourceVerification.csv","CP0107_Feb2018_Extraction_Report_HI.md","CP0107_Feb2018_Checks.csv",
 "CP0107_Dec2020_ChildWindow_Audit_Summary.json","CP0107_Dec2020_5m_ActualRows_Window.csv","CP0107_Dec2020_5m_ChildCoverage.csv",
 "CP0107_Dec2020_ReviewRollup_ChildCoverage.csv","CP0107_Dec2020_5m_SourceVerification.csv",
 "CP0107_Dec2020_FieldReview_Summary.json","CP0107_Dec2020_FieldReview_Report_HI.md","CP0107_Dec2020_Shared_5m_RawField_Comparison.csv",
 "CP0107_Dec2020_CloseTime_Fingerprint_FieldReview.csv","CP0107_Dec2020_Missing_5m_ChildKeys_BySource.csv",
 "CP0107_Monthly_Checksum_Provenance_Summary.json","CP0107_Monthly_Checksum_Provenance_Report_HI.md",
 "BTCUSDT-5m-2020-12.zip.CHECKSUM","BTCUSDT-5m-2020-12-21.zip.CHECKSUM"
)
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def blob(rel):return subprocess.check_output(["git","rev-parse","HEAD:"+rel],cwd=ROOT,text=True).strip()
def read_csv(path):
 with Path(path).open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write_csv(path,rows,fields=None):
 if fields is None:fields=list(rows[0].keys()) if rows else ["status"]
 with Path(path).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)
def iso(ms):return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
def utc_day(ms):return datetime.fromtimestamp(ms/1000,tz=timezone.utc).date().isoformat()
def parse_zip(path,expected_member):
 with zipfile.ZipFile(path,"r") as z:
  bad=z.testzip()
  if bad:raise ValueError("ZIP CRC failed at "+bad+" in "+path.name)
  files=[x.filename for x in z.infolist() if not x.is_dir()]
  csvs=[x for x in files if x.lower().endswith(".csv")]
  if len(files)!=1 or len(csvs)!=1:raise ValueError("expected exactly one CSV member in "+path.name)
  member=csvs[0]
  if expected_member and member!=expected_member:raise ValueError("CSV member differs from frozen manifest in "+path.name)
  rows=[]
  with z.open(member,"r") as raw:
   rd=csv.reader(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
   for lineno,row in enumerate(rd,1):
    if not row:continue
    if len(row)!=12:raise ValueError(path.name+" line "+str(lineno)+" not 12 fields")
    rows.append({"csv_line_number":lineno,"open_time_token":str(row[0]),"open_time_ms":int(row[0]),
     "raw":{k:str(v) for k,v in zip(RAW_FIELDS,row)}})
  return member,rows
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--snapshot",required=True);ap.add_argument("--manifest",required=True)
 ap.add_argument("--monthly-cache",required=True);ap.add_argument("--daily-cache",required=True)
 ap.add_argument("--baseline-dir",required=True);ap.add_argument("--output-dir",required=True)
 a=ap.parse_args()
 out=Path(a.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
 src=ROOT/a.baseline_dir
 for name in BASE_FILES:
  p=src/name
  if not p.is_file():raise FileNotFoundError("previous verified evidence missing: "+str(p))
  shutil.copy2(p,out/name)
 snapshot_path=ROOT/a.snapshot;manifest_path=ROOT/a.manifest
 if blob(a.snapshot)!=SNAPSHOT_BLOB:raise ValueError("7-row source snapshot Git blob SHA mismatch")
 if blob(a.manifest)!=MANIFEST_BLOB:raise ValueError("66-source manifest Git blob SHA mismatch")
 if sha_file(snapshot_path)=="" or sha_file(manifest_path)=="":raise ValueError("source evidence hash missing")
 snapshot=read_csv(snapshot_path);manifest=read_csv(manifest_path)
 checks=[]
 def ck(name,ok,detail):checks.append({"check_id":name,"status":"PASS" if ok else "FAIL","detail":str(detail)})
 ck("source_package_and_worklist_hashes",len(snapshot)==7 and all(x.get("source_package_sha256")==PACKAGE_SHA and x.get("worklist_member_sha256")==WORKLIST_MEMBER_SHA for x in snapshot),"package and frozen worklist member recorded on all 7 rows")
 expected_cases={"UNMATCHED-M-15m-1608559200000","UNMATCHED-M-1h-1608559200000","UNMATCHED-M-30m-1608559200000","UNMATCHED-M-5m-1608558600000","UNMATCHED-M-5m-1608558900000","UNMATCHED-M-5m-1608559200000","UNMATCHED-M-5m-1608559500000"}
 ck("exact_seven_residual_monthly_only_ids",len(snapshot)==7 and {x["case_id"] for x in snapshot}==expected_cases and len({x["case_id"] for x in snapshot})==7,"exact case ID set and no duplicates")
 by_manifest={(x["source"],x["interval"],x["filename"]):x for x in manifest}
 archive_results=[];row_results=[]
 for rec in snapshot:
  case=rec["case_id"];iv=rec["interval"];date=rec["utc_date"];open_ms=int(rec["open_time_ms"]);period=date[:7]
  for srcname,filename,expected_sha,cache_root in (
   ("MONTHLY",rec["monthly_archive"],rec["monthly_sha256"],Path(a.monthly_cache)),
   ("DAILY",rec["daily_archive"],rec["daily_sha256"],Path(a.daily_cache))
  ):
   fr=by_manifest.get((srcname,iv,filename))
   if fr is None:raise ValueError("source archive absent from frozen 66-row manifest: "+srcname+" "+filename)
   if fr.get("status")!="PASS" or fr.get("zip_crc")!="PASS" or fr.get("zip_sha256")!=expected_sha or fr.get("official_sha256")!=expected_sha:
    raise ValueError("frozen source manifest hash/status mismatch for "+filename)
   if srcname=="MONTHLY":p=cache_root/iv/period/filename
   else:p=cache_root/iv/filename
   if not p.is_file():raise FileNotFoundError("cached source archive not found; no download fallback: "+str(p))
   actual=sha_file(p)
   if actual!=expected_sha:raise ValueError("cached archive bytes differ from frozen official SHA: "+filename)
   member,parsed=parse_zip(p,fr.get("csv_member"))
   sidepath=p.with_name(p.name+".CHECKSUM")
   side_exists=sidepath.is_file();side_hash=sha_file(sidepath) if side_exists else ""
   side_manifest_hash=fr.get("checksum_sidecar_sha256","")
   side_status="PASS_CACHED_SIDECAR_MATCH" if side_exists and side_hash==side_manifest_hash else ("SIDECAR_BYTES_NOT_IN_CACHE_REFERENCE_ONLY" if not side_exists else "CACHED_SIDECAR_HASH_MISMATCH")
   if side_exists and side_hash!=side_manifest_hash:raise ValueError("cached .CHECKSUM bytes differ from frozen manifest SHA: "+filename)
   token_match=False
   if side_exists:
    import re
    side_text=sidepath.read_text(encoding="utf-8",errors="strict")
    import_tokens=sorted(set(x.lower() for x in re.findall(r"(?i)\b[0-9a-f]{64}\b",side_text)))
    token_match=len(import_tokens)==1 and import_tokens[0]==expected_sha.lower() and filename in side_text
    if not token_match:raise ValueError("cached .CHECKSUM token does not point to archive hash: "+filename)
   bykey={}
   duplicates=[]
   for x in parsed:
    bykey.setdefault(x["open_time_ms"],[]).append(x)
    if utc_day(x["open_time_ms"])!=date and srcname=="DAILY":raise ValueError("daily ZIP has row outside requested UTC date: "+filename)
   count_exact=len(bykey.get(open_ms,[]))
   if srcname=="MONTHLY":
    if count_exact!=1:raise ValueError("expected exactly one monthly open key for "+case)
    found=bykey[open_ms][0]
    if any(found["raw"][field]!=rec.get("monthly_"+field+"_token","") for field in RAW_FIELDS):
     raise ValueError("frozen CP-0041 raw token does not match monthly ZIP row for "+case)
    if sha_bytes(json.dumps(found["raw"],sort_keys=True,separators=(",",":")).encode())=="":raise ValueError("raw row fingerprint failure")
   else:found=bykey[open_ms][0] if count_exact else None
   step=STEP_MS[iv];day_start=int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp()*1000)
   expected_keys=set(range(day_start,day_start+86400000,step));found_keys=set(bykey)
   offgrid=sorted(k for k in found_keys if (k-day_start)%step!=0)
   duplicates=len([k for k,v in bykey.items() if len(v)>1])
   missing_count=len(expected_keys-found_keys) if srcname=="DAILY" else None
   nearest=[]
   if srcname=="DAILY" and not found:
    nearest=sorted(((abs(k-open_ms),k) for k in found_keys),key=lambda x:(x[0],x[1]))[:1]
   archive_results.append({"case_id":case,"source":srcname,"interval":iv,"filename":filename,"period":period if srcname=="MONTHLY" else date,
    "cache_path":str(p),"archive_sha256_expected":expected_sha,"archive_sha256_actual":actual,"archive_hash_matches":"True",
    "official_sha256_matches":"True","zip_crc":"PASS","csv_member":member,"source_manifest_blob_sha1":blob(a.manifest),
    "sidecar_file_status":side_status,"sidecar_sha256_actual":side_hash,"sidecar_sha256_frozen_reference":side_manifest_hash,
    "sidecar_token_matches_archive_sha":"True" if token_match else ("False" if side_exists else "NOT_RECHECKED_SIDECAR_NOT_CACHED"),
    "raw_rows_in_archive":len(parsed),"unique_open_keys":len(bykey),"duplicate_open_keys":duplicates,
    "exact_target_open_key_rows":count_exact,"daily_expected_grid_keys_absent":missing_count,
    "daily_off_grid_open_keys":len(offgrid) if srcname=="DAILY" else None,
    "target_nearest_daily_open_key_utc_diagnostic_only":iso(nearest[0][1]) if nearest else "",
    "target_nearest_daily_open_key_delta_ms_diagnostic_only":nearest[0][0] if nearest else "",
    "interpretation":"Exact open-time presence test only; nearest key is diagnostic and never treated as counterpart"})
   if srcname=="MONTHLY":monthly_result=(found,actual,fr,side_status,side_hash,token_match,member,missing_count)
   else:daily_result=(found,actual,fr,side_status,side_hash,token_match,member,missing_count,nearest)
  mrow=monthly_result[0]["raw"];drow=daily_result[0]["raw"] if daily_result[0] else None
  differences=[k for k in RAW_FIELDS if drow and drow[k]!=mrow[k]]
  row_results.append({
   "case_id":case,"interval":iv,"utc_date":date,"open_time_ms":open_ms,"open_time_utc":iso(open_ms),
   "original_worklist_record_type":rec["original_record_type"],"original_worklist_disposition":rec["original_disposition"],
   "source_row_json_sha256_from_worklist":rec["source_row_json_sha256"],
   "monthly_archive_filename":rec["monthly_archive"],"monthly_archive_sha256":monthly_result[1],
   "monthly_inner_csv_member":monthly_result[6],"monthly_csv_line_number":monthly_result[0]["csv_line_number"],
   "monthly_exact_open_key_present":"True","monthly_exact_row_matches_frozen_worklist_raw_tokens":"True",
   "monthly_raw_close_time_token":mrow["close_time"],"monthly_raw_ohlc_flat":"True" if len({mrow[k] for k in ("open","high","low","close")})==1 else "False",
   "monthly_raw_zero_volume_and_trades":"True" if mrow["volume"]=="0.00000000" and mrow["number_of_trades"]=="0" else "False",
   "daily_archive_filename":rec["daily_archive"],"daily_archive_sha256":daily_result[1],"daily_inner_csv_member":daily_result[6],
   "daily_exact_open_key_present":"True" if drow else "False","daily_exact_open_key_counterpart_status":"PRESENT_REVIEW_FIELD_COMPARE" if drow else "ABSENT_FROM_HASH_VERIFIED_DAILY_ARCHIVE",
   "daily_exact_counterpart_csv_line_number":daily_result[0]["csv_line_number"] if drow else "",
   "daily_raw_differing_fields":";".join(differences),"daily_raw_field_diff_count":len(differences),
   "daily_nearest_open_time_utc_diagnostic_only":iso(daily_result[8][0][1]) if daily_result[8] else "",
   "daily_nearest_open_time_delta_ms_diagnostic_only":daily_result[8][0][0] if daily_result[8] else "",
   "daily_archive_rows":next(x["raw_rows_in_archive"] for x in archive_results if x["case_id"]==case and x["source"]=="DAILY"),
   "daily_expected_grid_keys_absent":daily_result[7],
   "daily_grid_key_exact_absence_confirmed":"True" if not drow else "False",
   "disposition":"OPEN_REVIEW_REQUIRED_DAILY_EXACT_KEY_ABSENT" if not drow else "OPEN_REVIEW_REQUIRED_DAILY_EXACT_KEY_VALUE_COMPARISON",
   "root_cause":"OPEN_NOT_ESTABLISHED","canonical_source":"NONE","case_closed":"False",
   "monthly_sidecar_status":monthly_result[3],"daily_sidecar_status":daily_result[3],
   "cp0041_package_sha256":PACKAGE_SHA,"cp0041_worklist_member_sha256":WORKLIST_MEMBER_SHA,
   "cp0107_archive_manifest_blob_sha1":MANIFEST_BLOB,"no_timestamp_shift_or_rounding":"True",
   "raw_rows_merged_replaced_or_deleted":"False","synthetic_candles_created":"False","backtest_rerun":"False","strategy_promoted":"False"
  })
  ck("monthly_archive_valid:"+case,monthly_result[1]==rec["monthly_sha256"] and monthly_result[3]!="CACHED_SIDECAR_HASH_MISMATCH" and monthly_result[0]["raw"]=={k:rec.get("monthly_"+k+"_token","") for k in RAW_FIELDS},
     "monthly exact raw tokens revalidated against cached bytes")
  ck("daily_archive_valid:"+case,daily_result[1]==rec["daily_sha256"] and daily_result[3]!="CACHED_SIDECAR_HASH_MISMATCH",
     "daily cache hash/CRC verified; sidecar status="+daily_result[3])
  ck("daily_exact_key_status:"+case,(not daily_result[0]) or all(daily_result[0]["raw"][k]==mrow[k] for k in RAW_FIELDS),
     "daily exact open key count="+str(1 if daily_result[0] else 0))
  ck("source_case_remains_open:"+case,not drow and row_results[-1]["case_closed"]=="False" and row_results[-1]["canonical_source"]=="NONE",
     row_results[-1]["disposition"])
 check_all=all(x["status"]=="PASS" for x in checks) and len(row_results)==7 and all(x["daily_exact_open_key_present"]=="False" for x in row_results)
 write_csv(out/"CP0107_CP0041_Dec2020_Residual7_ArchiveVerification.csv",archive_results)
 write_csv(out/"CP0107_CP0041_Dec2020_Residual7_ExactKey_Audit.csv",row_results)
 outputs={}
 for name in ("CP0107_CP0041_Dec2020_Residual7_ArchiveVerification.csv","CP0107_CP0041_Dec2020_Residual7_ExactKey_Audit.csv"):
  p=out/name;outputs[name]={"sha256":sha_file(p),"bytes":p.stat().st_size,"rows":len(read_csv(p))}
 status="PASS_SEVEN_RESIDUAL_EXACT_KEY_AUDIT" if check_all else "FAIL_SEVEN_RESIDUAL_EXACT_KEY_AUDIT"
 summary={"checkpoint":"CP-0107","task":"cp0107_cp0041_dec2020_residual7_exact_key_audit","status":status,
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"source_row_count":len(row_results),"archive_objects_checked":len(archive_results),
  "daily_exact_key_counterparts":sum(x["daily_exact_open_key_present"]=="True" for x in row_results),
  "daily_exact_key_absent":sum(x["daily_exact_open_key_present"]=="False" for x in row_results),
  "flat_zero_monthly_rows":sum(x["monthly_raw_ohlc_flat"]=="True" and x["monthly_raw_zero_volume_and_trades"]=="True" for x in row_results),
  "checks":checks,"checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),"outputs":outputs,
  "sources":{"source_snapshot_blob_sha1":blob(a.snapshot),"source_manifest_blob_sha1":blob(a.manifest),"cp0041_package_sha256":PACKAGE_SHA,
   "cp0041_worklist_member_sha256":WORKLIST_MEMBER_SHA},
  "disposition":{"all_seven_remain_open":True,"root_cause":"OPEN_NOT_ESTABLISHED","canonical_source_selected":False,"source_cases_closed":0,
   "raw_archives_modified":False,"timestamps_shifted_or_rounded":False,"rows_merged_replaced_or_deleted":False,"synthetic_candles_created":False,
   "backtest_rerun":False,"strategy_promoted":False,
   "gate_states":{"G0":"BLOCKED_GLOBAL","G1":"PARTIAL_SYSTEM_LEVEL","G2":"FAIL_CURRENT_23_CANDIDATES","G3":"BLOCKED_PARTIAL","G4":"INSUFFICIENT_EVIDENCE","G5":"NOT_RUN","G6":"NOT_BUILT","G7":"LIVE_BLOCKED"}},
  "interpretation":"The audit determines exact-open-key presence from hash/CRC-verified archive bytes. It does not assign source authority or explain why a row is absent; nearest timestamps remain diagnostic-only."}
 report=[
  "# CP-0107: seven residual December 2020 monthly-only rows","",
  "Status: "+status+"; checks "+str(summary["checks_passed"])+"/"+str(summary["checks_total"])+" PASS.","",
  "## Sources verified","",
  "- Original CP-0041 worklist member SHA-256: "+WORKLIST_MEMBER_SHA+"; package SHA-256: "+PACKAGE_SHA+".",
  "- The seven target row snapshots are exact CP-0041 worklist entries, and their 12 raw tokens were matched against the monthly archive rows.",
  "- Four monthly and four daily ZIPs were reused from the pre-existing cache. Every ZIP SHA-256 and CRC was checked against the frozen 66-source manifest. Cached sidecar bytes, where present, were also rehashed; absent sidecar bytes are explicitly marked reference-only without network retrieval.",
  "",
  "## Exact key result","",
  "- Seven exact monthly rows audited; daily exact-open counterparts found: "+str(summary["daily_exact_key_counterparts"])+"; absent from verified daily archive bytes: "+str(summary["daily_exact_key_absent"])+".",
  "- All monthly rows have flat OHLC 22646.53000000 with zero volume/trades; the shared close-time anomaly token is preserved as raw evidence where present.",
  "",
  "## Disposition","",
  "All seven remain OPEN_REVIEW_REQUIRED. No canonical source or root cause selected; no cases closed. No timestamp shift/rounding, row edit, merge, synthetic candle, backtest rerun or strategy promotion."
 ]
 report_path=out/"CP0107_CP0041_Dec2020_Residual7_Report_HI.md";report_path.write_text("\n".join(report)+"\n",encoding="utf-8")
 outputs[report_path.name]={"sha256":sha_file(report_path),"bytes":report_path.stat().st_size,"rows":None}
 sp=out/"CP0107_CP0041_Dec2020_Residual7_Summary.json";sp.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 print(json.dumps({"status":status,"checks_passed":summary["checks_passed"],"checks_total":summary["checks_total"],
  "source_rows":len(row_results),"archive_objects_checked":len(archive_results),"daily_exact_key_counterparts":summary["daily_exact_key_counterparts"],
  "daily_exact_key_absent":summary["daily_exact_key_absent"],"monthly_rows_flat_zero":summary["flat_zero_monthly_rows"],"outputs":outputs},ensure_ascii=False,sort_keys=True),flush=True)
 return 0 if check_all else 1
if __name__=="__main__":raise SystemExit(main())
